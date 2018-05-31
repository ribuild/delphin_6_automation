__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.backend import backend

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_delphin_checker():
    folder = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    delphin_file = folder + '/delphin/delphin_project_1d.d6p'

    backend.check_delphin_file(delphin_file)
