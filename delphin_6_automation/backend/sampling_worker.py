import delphin_6_automation.database_interactions.sampling_interactions

__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import sys
import os

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.sampling import sampling
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions import sampling_interactions

# Logger
logger = ribuild_logger(__name__)


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def main():
    print_header()
    menu()


def print_header():
    print('---------------------------------------------------')
    print('|                                                  |')
    print('|           RiBuild EU Research Project            |')
    print('|           for Hygrothermal Simulations           |')
    print('|                                                  |')
    print('|                 WORK IN PROGRESS                 |')
    print('|               Sampling Environment               |')
    print('|                                                  |')
    print('---------------------------------------------------')


def menu():
    print('')
    print('------------------- SAMPLING MENU ---------------------')
    print('')
    print("Available Actions:")
    print("[a] Start Sampling")
    print("[b] Create Sampling Strategy")
    print("[c] View Current Samples")
    print("[x] Exit")

    choice = input("> ").strip().lower()

    if choice == 'a':
        logger.info('starting sampling')
        sampling_strategy_id = input("Define sampling strategy ID >")
        logger.info(sampling_strategy_id)

        print('\nStarting sampling\n')
        sampling_worker(sampling_strategy_id)

    elif choice == 'b':
        strategy = sampling.create_sampling_strategy(os.path.dirname(__file__))
        strategy_id = sampling_interactions.upload_sampling_strategy(strategy)
        print(f'Created sampling and uploaded it with ID: {strategy_id}')
        logger.info(f'Created sampling and uploaded it with ID: {strategy_id}')

    elif choice == 'c':
        print('Not implemented')
        pass

    elif choice == 'x':
        print("Goodbye")


def sampling_worker(strategy_id):
    # Initialize
    strategy_doc = sampling_interactions.get_sampling_strategy(strategy_id)
    sample_iteration = 0
    convergence = False
    new_samples_per_set = strategy_doc.strategy['settings']['initial samples per set']
    used_samples_per_set = 0
    previous_samples = 0
    samples_per_set = sum([len(strategy_doc.strategy['design'][design_])
                          for design_ in strategy_doc.strategy['design'].keys()]) * \
                      sum([len(strategy_doc.strategy['scenario'][scenario_])
                          for scenario_ in strategy_doc.strategy['scenario'].keys()])

    # Run loop
    while not convergence:
        print(f'\nRunning sampling iteration #{sample_iteration}')
        print(f'New Samples per set: {new_samples_per_set}')
        print(f'Used samples per set: {used_samples_per_set}')
        print(f'Previous samples: {previous_samples}')
        logger.info(f'Running sampling iteration #{sample_iteration}')
        logger.info(f'New Samples per set: {new_samples_per_set}')
        logger.info(f'Used samples per set: {used_samples_per_set}')
        logger.info(f'Previous samples: {previous_samples}')

        new_samples = sampling.create_samples(strategy_doc, used_samples_per_set)
        sampling_id = sampling_interactions.upload_samples(new_samples, sample_iteration)
        delphin_ids = sampling.create_delphin_projects(strategy_doc.strategy, new_samples)
        sampling_interactions.add_delphin_to_sampling(sampling_id, delphin_ids)
        simulation_interactions.wait_until_simulated(delphin_ids)
        current_error = sampling.calculate_error(strategy_doc.strategy)
        sampling_interactions.upload_standard_error(strategy_doc, sampling_id, current_error)
        convergence = sampling.check_convergence(strategy_doc.strategy, current_error)

        print(f'Standard Error at iteration {sample_iteration} is: {current_error}')
        logger.info(f'Standard Error at iteration {sample_iteration} is: {current_error}')

        # Update parameters for next iteration
        used_samples_per_set = used_samples_per_set + new_samples_per_set
        # TODO - length of scenarios * designs?
        previous_samples = used_samples_per_set * samples_per_set
        sample_iteration += 1

        if used_samples_per_set >= strategy_doc.strategy['settings']['max_samples']:
            print(f'Maximum number of samples reached. Simulated {used_samples_per_set} samples per set')
            logger.info(f'Maximum number of samples reached. Simulated {used_samples_per_set} samples per set')
            print('\nExits. Bye')
            sys.exit()

    print(f'Convergence reached at iteration #{sample_iteration}')
    logger.info(f'Convergence reached at iteration #{sample_iteration}')
    print('\nExits. Bye')
    sys.exit()
