__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import codecs
import shutil

# RiBuild Modules:
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import general_interactions
import delphin_6_automation.database_interactions.db_templates.material_entry as material_db
import delphin_6_automation.database_interactions.db_templates.delphin_entry as delphin_db
import delphin_6_automation.database_interactions.mongo_setup as mongo_setup
import delphin_6_automation.pytest.pytest_helper_functions as helper
from delphin_6_automation.database_interactions.auth import dtu_byg

# -------------------------------------------------------------------------------------------------------------------- #
# TEST

mongo_setup.global_init(dtu_byg)

# TODO - update download tests


def test_download_results_1():
    # TODO - Update

    result_id, delphin_id, material_id = helper.upload_needed_results('download_results_1')

    default_path = os.path.dirname(os.path.realpath(__file__))
    test_path, source_path = default_path + '/test_dir/test', default_path + '/test_dir/source'

    general_interactions.download_raw_result(result_id, test_path)
    shutil.unpack_archive(default_path + '/test_files/delphin_results.zip', source_path)

    #source_progress = open(source_path + '/delphin_results/log/progress.txt', 'r').readlines()
    #test_progress = open(test_path + '/log/progress.txt', 'r').readlines()

    #source_cvode = open(source_path + '/delphin_results/log/integrator_cvode_stats.tsv', 'r').readlines()
    #test_cvode = open(test_path + '/log/integrator_cvode_stats.tsv', 'r').readlines()

    #source_les = open(source_path + '/delphin_results/log/LES_direct_stats.tsv', 'r').readlines()
    #test_les = open(test_path + '/log/LES_direct_stats.tsv', 'r').readlines()

    source_g6a = open(source_path + '/delphin_results/results/5a5479095d9460327c6970f0_2823182570.g6a', 'r').readlines()
    test_g6a = open(test_path + '/results/5a5479095d9460327c6970f0_2823182570.g6a', 'r').readlines()
    assert test_g6a == source_g6a

"""

def test_download_materials_1():
    # TODO - Create
    test_folder, _ = helper.setup_test_folders()
    delphin_id, material_ids = helper.upload_needed_project('download_material_project_1')
    material_interactions.download_materials(str(delphin_id), test_folder)
    source_folder = os.path.dirname(os.path.realpath(__file__)) + '/test_files/helper_files'

    def get_material_files(path):
        files = []
        for file in ['BrickWienerberger_512.m6',]:
            #'IQTop_726.m6', 'RemmersiQFix_437.m6',
            #         'RemmersiQTherm_438.m6', 'RestorationRender_210.m6',
            #         'WietersdorfPeggauerMineralischeKalkzementLeichtputz_630.m6']:
            file_path = path + '/' + file
            files.append(codecs.open(file_path, "r", "utf-8").readlines())
        return files

    # Get files
    test_files = get_material_files(test_folder)
    source_files = get_material_files(source_folder)

    # Clean up
    delphin_db.Delphin.objects(id=delphin_id).first().delete()
    for material_id in material_ids:
        material_db.Material.objects(id=material_id).first().delete()
    #helper.clean_up_test_folders()

    # Assert
    assert test_files == source_files

def test_download_weather_1():
    # Setup
    test_folder, _ = helper.setup_test_folders()
    source_folder = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    delphin_id, weather_ids, material_ids = helper.upload_needed_project('download_project_1')
    weather_interactions.download_weather(str(delphin_id), test_folder)

    def get_weather_files(path):
        files = []
        for file in ['diffuse_radiation.ccd', 'direct_radiation.ccd', 'indoor_relative_humidity.ccd',
                     'indoor_temperature.ccd', 'long_wave_radiation.ccd', 'relative_humidity.ccd',
                     'temperature.ccd', 'vertical_rain.ccd', 'wind_direction.ccd', 'wind_speed.ccd']:
            file_obj = open(path + '/' + file, 'r')
            files.append(file_obj.readlines())
        return files

    # Get files
    test_files = get_weather_files(test_folder)
    source_files = get_weather_files(source_folder)

    # Clean up
    delphin_db.Delphin.objects(id=delphin_id).first().delete()
    for material_id in material_ids:
        material_db.Material.objects(id=material_id).first().delete()
    for weather_id in weather_ids:
        weather_db.Weather.objects(id=weather_id).first().delete()
    helper.clean_up_test_folders()

    # Assert
    assert test_files == source_files


def test_download_project_1():
    # TODO - Update
    pass
    id_ = "5a5479095d9460327c6970f0"
    test_path, source_path = helper.setup_test_folders()
    test_file_path = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    delphin_interact.download_from_database(id_, test_path)
    shutil.copy(test_file_path + '/' + id_ + '.d6p', source_path + '/' + id_ + '.d6p')
    assert filecmp.cmp(source_path + '/' + str(id_) + '.d6p', test_path + '/' + str(id_) + '.d6p')
    helper.clean_up_test_folders()


def test_download_results_1():
    # TODO - Update
    pass
    test_path, source_path = helper.setup_test_folders()
    id_ = '5a54a8a35d946027d804103c'
    general_interact.download_raw_result(id_, test_path)

    source_zip = os.path.dirname(os.path.realpath(__file__)) + '/test_files/5a5479095d9460327c6970f0.zip'
    shutil.unpack_archive(source_zip, source_path)

    for file in os.listdir(test_path + '/log'):
        print(filecmp.cmp(source_path + '/5a5479095d9460327c6970f0/log/' + file, test_path + '/log/' + file))

    for file in os.listdir(test_path + '/results'):
        assert filecmp.cmp(source_path + '/5a5479095d9460327c6970f0/results/' + file, test_path + '/results/' + file)
"""