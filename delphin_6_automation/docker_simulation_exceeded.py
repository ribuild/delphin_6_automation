__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import sys
import json

source_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, source_folder)

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.backend import simulation_worker

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":

    logger = ribuild_logger()
    # Setup connection
    auth_path = '/run/secrets/db_ait'
    with open(auth_path, 'r') as file:
        auth_dict = json.load(file)

    server = mongo_setup.global_init(auth_dict)

    try:

        folder = '/app/data'

        simulation_worker.exceeded_worker('hpc', folder)

    except Exception as err:
        logger.exception('Error in main')

    finally:
        mongo_setup.global_end_ssh(server)
