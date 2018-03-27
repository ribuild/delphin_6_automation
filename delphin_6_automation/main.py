__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import sys


source_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, source_folder)

# RiBuild Modules:
from delphin_6_automation.ribuild_logger import logger
from delphin_6_automation.backend import main

# -------------------------------------------------------------------------------------------------------------------- #
# BACKEND

if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception('Error in main')
