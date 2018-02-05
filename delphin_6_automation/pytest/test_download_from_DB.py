__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import filecmp
import os
import shutil

# RiBuild Modules:
import delphin_6_automation.database_interactions.delphin_interactions as delphin_interact
import delphin_6_automation.database_interactions.general_interactions as general_interact
import delphin_6_automation.nosql.mongo_setup as mongo_setup
import delphin_6_automation.pytest.pytest_helper_functions as helper
from delphin_6_automation.nosql.auth import dtu_byg

# -------------------------------------------------------------------------------------------------------------------- #
# TEST

mongo_setup.global_init(dtu_byg)


def test_download_project_1():
    id_ = "5a5479095d9460327c6970f0"
    test_path, source_path = helper.setup_test_folders()
    test_file_path = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    delphin_interact.download_from_database(id_, test_path)
    shutil.copy(test_file_path + '/' + id_ + '.d6p', source_path + '/' + id_ + '.d6p')
    assert filecmp.cmp(source_path + '/' + str(id_) + '.d6p', test_path + '/' + str(id_) + '.d6p')
    helper.clean_up_test_folders()


def test_download_results_1():
    test_path, source_path = helper.setup_test_folders()
    id_ = '5a54a8a35d946027d804103c'
    general_interact.download_raw_result(id_, test_path)

    source_zip = os.path.dirname(os.path.realpath(__file__)) + '/test_files/5a5479095d9460327c6970f0.zip'
    shutil.unpack_archive(source_zip, source_path)

    for file in os.listdir(test_path + '/log'):
        print(filecmp.cmp(source_path + '/5a5479095d9460327c6970f0/log/' + file, test_path + '/log/' + file))

    for file in os.listdir(test_path + '/results'):
        assert filecmp.cmp(source_path + '/5a5479095d9460327c6970f0/results/' + file, test_path + '/results/' + file)


def test_download_materials_1():
    # TODO
    pass


def test_download_weather_1():
    test_path, source_path = helper.setup_test_folders()


    pass


test_download_weather_1()