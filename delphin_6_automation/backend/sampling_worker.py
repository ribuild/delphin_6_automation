__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import sys
import os
import matplotlib.pyplot as plt
import numpy as np

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

    try:
        while True:
            menu()
    except KeyboardInterrupt:
        sys.exit()


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
    print("[c] View Current Progress")
    print("[x] Exit")

    choice = input("> ").strip().lower()

    if choice == 'a':
        logger.debug('starting sampling')
        sampling_strategy_id = input("Define sampling strategy ID > ")
        logger.debug(sampling_strategy_id)

        logger.info('\nStarting sampling\n')
        sampling_worker(sampling_strategy_id)

    elif choice == 'b':
        strategy = sampling.create_sampling_strategy(os.path.dirname(__file__))
        strategy_id = sampling_interactions.upload_sampling_strategy(strategy)
        logger.info(f'Created sampling and uploaded it with ID: {strategy_id}')

    elif choice == 'c':
        sampling_strategy_id = input("Define sampling strategy ID > ")
        sampling_overview(sampling_strategy_id)

    elif choice == 'x':
        logger.info("Goodbye")


def sampling_worker(strategy_id):
    strategy_doc = sampling_interactions.get_sampling_strategy(strategy_id)
    (sample_iteration, convergence,
     new_samples_per_set, used_samples_per_set) = sampling.initialize_sampling(strategy_doc)

    # Run loop
    while not convergence:
        logger.info(f'Running sampling iteration #{sample_iteration}')
        logger.info(f'New Samples per set: {new_samples_per_set}')
        logger.info(f'Used samples per set: {used_samples_per_set}')

        strategy_doc.reload()
        existing_sample = sampling.sample_exists(strategy_doc)

        if not existing_sample:
            logger.info('Creating new samples')
            new_samples = sampling.create_samples(strategy_doc, used_samples_per_set)
            sample_id = sampling_interactions.upload_samples(new_samples, sample_iteration)
            delphin_ids = sampling.create_delphin_projects(strategy_doc.strategy, new_samples)
            sampling_interactions.add_delphin_to_sampling(sample_id, delphin_ids)
            sampling_interactions.add_sample_to_strategy(strategy_id, sample_id)

        else:
            logger.debug('Found existing sample')
            delphin_ids = sampling_interactions.get_delphin_for_sample(existing_sample)
            sample_id = existing_sample.id

        simulation_interactions.wait_until_simulated(delphin_ids)
        sampling.calculate_sample_output(strategy_doc.strategy, sample_id)
        current_error = sampling.calculate_error(strategy_doc)
        sampling_interactions.upload_standard_error(strategy_doc, current_error)
        convergence = sampling.check_convergence(strategy_doc)

        logger.debug(f'Standard Error at iteration {sample_iteration} is: {current_error}\n')

        # Update parameters for next iteration
        used_samples_per_set = used_samples_per_set + new_samples_per_set
        sample_iteration += 1
        sampling_interactions.upload_sample_iteration_parameters(strategy_doc, sample_iteration, used_samples_per_set)

        if used_samples_per_set >= strategy_doc.strategy['settings']['max samples']:
            logger.info(f'Maximum number of samples reached. Simulated {used_samples_per_set} samples per set\n')
            logger.info('Exits. Bye')
            sys.exit()

    logger.info(f'Convergence reached at iteration #{sample_iteration}\n')
    logger.info('Exits. Bye')
    sys.exit()


def sampling_overview(strategy_id):

    strategy_doc = sampling_interactions.get_sampling_strategy(strategy_id)

    def create_figure(damage_model: str):
        plt.figure()

        for design in strategy_doc.standard_error.keys():
            data = strategy_doc.standard_error[design][damage_model]
            x = np.arange(0, len(data))
            if len(data) == 1:
                plt.scatter(x, data, label=design)
            else:
                plt.plot(x, data, label=design)
            plt.xlim(x[0]-1, x[-1]+1)

        plt.legend()
        plt.title(f'Sampling Convergence:\n{damage_model.capitalize()}')
        plt.xlabel('Iterations')
        plt.ylabel('Standard Error')

    create_figure('mould')
    create_figure('heat_loss')

    plt.show()
