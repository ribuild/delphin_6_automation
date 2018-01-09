__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import filecmp
import os
import shutil

# RiBuild Modules:
import delphin_6_automation.simulation.database_interactions.delphin_interactions as delphin_interact
import delphin_6_automation.simulation.nosql.mongo_setup as mongo_setup
import delphin_6_automation.pytest.pytest_helper_functions as helper
from delphin_6_automation.simulation.nosql.auth import dtu_byg

# -------------------------------------------------------------------------------------------------------------------- #
# TEST

mongo_setup.global_init(dtu_byg)


def test_download_1():
    id_ = "5a5479095d9460327c6970f0"
    test_path, source_path = helper.setup_test_folders()
    test_file_path = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    delphin_interact.download_from_database(id_, test_path)
    shutil.copy(test_file_path + '/' + id_ + '.d6p', source_path + '/' + id_ + '.d6p')
    assert filecmp.cmp(source_path + '/' + str(id_) + '.d6p', test_path + '/' + str(id_) + '.d6p')
    helper.clean_up_test_folders()
