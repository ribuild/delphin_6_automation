__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import sys

source_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, source_folder)

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.backend import simulation_worker
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions import general_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":

    # Setup connection
    mongo_setup.global_init(auth_dict)
    logger = ribuild_logger(__name__)

    folder = '/app/data'
    id_ = simulation_interactions.find_next_sim_in_queue()
    simulation_folder = os.path.join(folder, id_)

    if not os.path.isdir(simulation_folder):
        os.mkdir(simulation_folder)
    else:
        simulation_interactions.clean_simulation_folder(simulation_folder)
        os.mkdir(simulation_folder)

    # Download, solve, upload
    logger.info(f'Downloads project with ID: {id_}')

    general_interactions.download_full_project_from_database(id_, simulation_folder)
    estimated_time = simulation_worker.get_average_computation_time(id_)
    submit_file = simulation_worker.create_submit_file(id_, simulation_folder, estimated_time)
    logger.info('Done')

    #simulation_worker.docker_worker('hpc')

    mongo_setup.global_end_ssh(auth_dict)
