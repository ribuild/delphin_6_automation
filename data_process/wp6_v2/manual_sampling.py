from delphin_6_automation.backend.sampling_worker import create_new_samples
from delphin_6_automation.sampling import sampling

__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup, sampling_interactions, simulation_interactions
from delphin_6_automation.database_interactions.auth import auth_dict
import sys
# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":

    server = mongo_setup.global_init(auth_dict)
    strategy_id = sample_entry.Strategy.objects().first().id
    strategy_doc = sampling_interactions.get_sampling_strategy(strategy_id)
    (sample_iteration, convergence,
     new_samples_per_set, used_samples_per_set) = sampling.initialize_sampling(strategy_doc)

    # Run loop
    iterations = 75
    logger.info(f"Running until {iterations} sample iterations")
    while sample_iteration < iterations:
        logger.info(f'Running sampling iteration #{sample_iteration}')
        logger.info(f'New Samples per set: {new_samples_per_set}')
        logger.info(f'Used samples per set: {used_samples_per_set}')

        #strategy_doc.reload()
        existing_sample = sampling.sample_exists(strategy_doc)

        if not existing_sample:
            delphin_ids, sample_id = create_new_samples(strategy_doc, used_samples_per_set, sample_iteration)

        else:
            logger.info('Found existing sample')
            sample_id = existing_sample.id

        # Update parameters for next iteration
        used_samples_per_set = used_samples_per_set + new_samples_per_set
        sample_iteration += 1
        sampling_interactions.upload_sample_iteration_parameters(strategy_doc,
                                                                 sample_iteration,
                                                                 used_samples_per_set)

    logger.info(f'Convergence reached at iteration #{sample_iteration}\n')
    logger.info('Exits. Bye')
    sys.exit()

    mongo_setup.global_end_ssh(server)
