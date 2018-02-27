__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import sys

source_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, source_folder)

# RiBuild Modules:
from delphin_6_automation.backend import *

# -------------------------------------------------------------------------------------------------------------------- #
# BACKEND

if __name__ == "__main__":
    main()
