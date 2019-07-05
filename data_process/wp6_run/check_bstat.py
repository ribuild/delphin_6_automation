__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import time
import sys


# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions import simulation_interactions

# Logger
logger = ribuild_logger(__name__)

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":
    #auth_path = '/run/secrets'
    auth_path = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\test\checks'
    # Setup connection

    try:
        file = os.path.join(auth_path, 'ocni.json')
        count = simulation_interactions.check_simulations(file)
        print(f'{count} in bstat')

    except Exception as err:
        logger.exception('Error in main')
