__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import shutil

# RiBuild Modules:
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.file_parsing import weather_parser


# -------------------------------------------------------------------------------------------------------------------- #
# TEST HELPER FUNCTIONS


def setup_test_folders():
    default_path = os.path.dirname(os.path.realpath(__file__))

    test_dir = default_path + '/test_dir'
    test_dir_source = default_path + '/test_dir/source'
    test_dir_test = default_path + '/test_dir/test'

    if not os.path.isdir(test_dir):
        os.mkdir(test_dir)
    if not os.path.isdir(test_dir_source):
        os.mkdir(test_dir_source)
    if not os.path.isdir(test_dir_test):
        os.mkdir(test_dir_test)

    return test_dir_test, test_dir_source


def unzip_with_test_folder_setup(zip_file):
    test_dir_test, test_dir_source = setup_test_folders()

    default_path = os.path.dirname(os.path.realpath(__file__))
    files_dir = default_path + '/test_files'
    shutil.unpack_archive(files_dir + '/' + zip_file, test_dir_source)

    return test_dir_test, test_dir_source


def clean_up_test_folders():
    test_dir = os.path.dirname(os.path.realpath(__file__)) + '/test_dir'
    shutil.rmtree(test_dir)


def upload_needed_materials(test_case: str) -> list:
    folder = os.path.dirname(os.path.realpath(__file__)) + '/test_files/helper_files'

    if test_case in ['upload_project_1', 'upload_project_2']:
        # Needed files
        material_files = ['WietersdorfPeggauerMineralischeKalkzementLeichtputz_630.m6', 'BrickWienerberger_512.m6',
                          'RemmersiQTherm_438.m6', 'RemmersiQFix_437.m6', 'IQTop_726.m6', 'RestorationRender_210.m6']

    else:
        material_files = []

    # Upload
    material_ids = []
    for material_file in material_files:
        material_ids.append(material_interactions.upload_material_file(folder + '/' + material_file))

    return material_ids


def upload_needed_weather(test_case: str):
    # Local Files
    folder = os.path.dirname(os.path.abspath(__file__)) + '/test_files/helper_files'

    if test_case == 'upload_project_2':
        weather_file = 'Aberdeen_3_years.WAC'

    else:
        return None

    # Upload
    return weather_parser.wac_to_db(folder + '/' + weather_file)


def upload_needed_project(test_case: str) -> tuple:

    if test_case == 'download_project_1':
        folder = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
        delphin_file = folder + '/delphin_project.d6p'

        material_ids = upload_needed_materials('upload_project_2')
        weather_ids = upload_needed_weather('upload_project_2')
        delphin_id = delphin_interactions.upload_delphin_to_database(delphin_file, 10)

        weather_interactions.assign_weather_to_project(delphin_id, weather_ids)
        weather_interactions.assign_indoor_climate_to_project(delphin_id, 'a')

        return delphin_id, weather_ids, material_ids

    elif test_case == 'download_material_project_1':
        folder = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
        delphin_file = folder + '/delphin_project.d6p'

        material_ids = upload_needed_materials('upload_project_2')
        delphin_id = delphin_interactions.upload_delphin_to_database(delphin_file, 10)

        return delphin_id, material_ids


def upload_needed_results(test_case: str) -> tuple:

    if test_case == 'download_results_1':
        # Create test folders
        result_folder, source_path = setup_test_folders()

        # Upload Delphin Project, so it can be linked to
        material_ids = upload_needed_materials('upload_project_1')
        folder = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
        delphin_file = folder + '/delphin_project.d6p'
        delphin_id = delphin_interactions.upload_delphin_to_database(delphin_file, 10)

        # Upload results
        result_zip = folder + '/delphin_results.zip'
        shutil.unpack_archive(result_zip, result_folder)
        os.rename(result_folder + '/delphin_results', result_folder + '/' + str(delphin_id))
        result_id = delphin_interactions.upload_results_to_database(result_folder + '/' + str(delphin_id))

        return result_id, delphin_id, material_ids


