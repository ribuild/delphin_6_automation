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

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":

    server = mongo_setup.global_init(auth_dict)

    strategy_doc = sample_entry.Strategy.objects().first()
    strategy_id = strategy_doc.id
    (sample_iteration, convergence,
     new_samples_per_set, used_samples_per_set) = sampling.initialize_sampling(strategy_doc)
    existing_sample = sampling.sample_exists(strategy_doc)

    logger.info(f'Running sampling iteration #{sample_iteration}')
    logger.info(f'New Samples per set: {new_samples_per_set}')
    logger.info(f'Used samples per set: {used_samples_per_set}')

    if not existing_sample:
        logger.info('Creating new samples')
        new_samples = sampling.create_samples(strategy_doc, used_samples_per_set)
        sample_id = sampling_interactions.upload_samples(new_samples, sample_iteration)
        delphin_ids = sampling.create_delphin_projects(strategy_doc.strategy, new_samples)
        sampling_interactions.add_delphin_to_sampling(sample_id, delphin_ids)
        sampling_interactions.update_time_estimation_model(strategy_id)
        sampling_interactions.predict_simulation_time(delphin_ids, strategy_id)
        sampling_interactions.update_queue_priorities(sample_id)
        sampling_interactions.add_sample_to_strategy(strategy_id, sample_id)

    else:
        logger.info('Found existing sample')
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

    mongo_setup.global_end_ssh(server)
