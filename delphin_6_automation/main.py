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
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.backend import main

# -------------------------------------------------------------------------------------------------------------------- #
# BACKEND

if __name__ == "__main__":
    local_logger = ribuild_logger(__name__)

    try:
        main()

    except Exception:
        print('Exited with error!')
        local_logger.exception('Error in main')
