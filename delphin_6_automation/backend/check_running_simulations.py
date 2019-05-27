__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import json
import os
import time
import sys

# Insert Python Path
source_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, source_folder)

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions import simulation_interactions

# Logger
logger = ribuild_logger(__name__)

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":
    logger = ribuild_logger()


    auth = {}
    auth_path = '/run/secrets'
    for file in os.listdir(auth_path):
        name = file.split('_')[1]

        with open(auth_path, 'r') as f:
            auth[name] = json.load(f)

    # Setup connection
    server = mongo_setup.global_init(auth_dict)

    try:
        for key in auth.keys():
            simulation_interactions.check_simulations(auth[key])

    except Exception as err:
        logger.exception('Error in main')

    finally:
        mongo_setup.global_end_ssh(server)
        time.sleep(120)
