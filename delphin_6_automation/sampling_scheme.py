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
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.backend.sampling_worker import main
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":
    # Setup connection
    mongo_setup.global_init(auth_dict)
    logger = ribuild_logger(__name__)

    try:
        main()

    except Exception as err:
        logger.exception('Error in main')
