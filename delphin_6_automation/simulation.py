__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
# Modules:
import os
import sys


source_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, source_folder)

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import notifiers_logger
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import dtu_byg
from delphin_6_automation.simulation_worker import main

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":
    # Setup connection
    mongo_setup.global_init(dtu_byg)
    notifier_logger = notifiers_logger(__name__)

    try:
        main()

    except Exception:
        print('Exited with error!')
        notifier_logger.error('Error in main')