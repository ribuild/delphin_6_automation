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
import time
#from delphin_6_automation.database_interactions import mongo_setup
#from delphin_6_automation.database_interactions.auth import auth_dict
#from delphin_6_automation.backend import simulation_worker

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":

    # Setup connection
    #mongo_setup.global_init(auth_dict)
    logger = ribuild_logger(__name__)

    #simulation_worker.docker_worker('hpc', '.')

    #mongo_setup.global_end_ssh(auth_dict)

    while True:
        logger.info('This is a info test')
        logger.debug('This is a debug test')
        time.sleep(5)
