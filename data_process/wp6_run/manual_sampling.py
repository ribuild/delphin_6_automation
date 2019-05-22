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
    (sample_iteration, convergence,
     new_samples_per_set, used_samples_per_set) = sampling.initialize_sampling(strategy_doc)
    existing_sample = sampling.sample_exists(strategy_doc)

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

    mongo_setup.global_end_ssh(server)
