__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import sys

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.sampling import sampling
from delphin_6_automation.database_interactions import simulation_interactions

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
    print("[b] Create Sampling Scheme")
    print("[c] View Current Samples")
    print("[x] Exit")

    choice = input("> ").strip().lower()

    if choice == 'a':
        logger.info('starting sampling')
        sampling_scheme_path = input("Define path to sampling scheme >")
        logger.info(sampling_scheme_path)

        print('Starting sampling\n')
        sampling_worker(sampling_scheme_path)

    elif choice == 'b':
        sampling_scheme_path = input("Define path to where the sampling scheme should be saved >")
        sampling.create_sampling_scheme(sampling_scheme_path)
        logger.info(f'Created sampling at: {sampling_scheme_path}')

    elif choice == 'c':
        print('Not implemented')
        pass

    elif choice == 'x':
        print("Goodbye")


def sampling_worker(path):
    scheme = sampling.load_scheme(path)
    sample_iteration = 0
    current_error = 0
    convergence = False

    while not convergence:
        print(f'Running sampling iteration #{sample_iteration}')
        logger.info(f'Running sampling iteration #{sample_iteration}')

        samples = sampling.load_existing_samples()
        new_samples = sampling.create_samples(scheme, samples)
        sampling_document = sampling.upload_samples(new_samples, sample_iteration)
        delphin_docs = sampling.create_delphin_projects(scheme, new_samples)
        sampling.add_delphin_to_sampling(sampling_document, delphin_docs)
        simulation_interactions.wait_until_simulated(delphin_docs)
        current_error = sampling.calculate_error(delphin_docs)
        sampling.upload_standard_error(sampling_document, current_error)

        print(f'Standard Error at iteration {sample_iteration} is: {current_error}')
        logger.info(f'Standard Error at iteration {sample_iteration} is: {current_error}')

        convergence = sampling.check_convergence(scheme, current_error)
        sample_iteration += 1

    print(f'Convergence reached at iteration #{sample_iteration}')
    logger.info(f'Convergence reached at iteration #{sample_iteration}')
    print('Exits. Bye')
    sys.exit()
