__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import time
import sys
import json

# Insert Python Path
source_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, source_folder)

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions import mongo_setup

# Logger
logger = ribuild_logger(__name__)

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
        simulation_interactions.check_simulating_projects()

    except Exception as err:
        logger.exception('Error in main')

    finally:
        mongo_setup.global_end_ssh(server)
        time.sleep(3600)

