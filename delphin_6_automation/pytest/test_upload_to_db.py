__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import json
import os
import os.path
import shutil
import bson.json_util

# RiBuild Modules:
import delphin_6_automation.database_interactions.db_templates.delphin_entry as delphin_db
import delphin_6_automation.database_interactions.db_templates.material_entry as material_db
import delphin_6_automation.database_interactions.db_templates.result_raw_entry as result_db
import delphin_6_automation.database_interactions.db_templates.weather_entry as weather_db
try:
    from delphin_6_automation.database_interactions.auth import dtu_byg as authorisation
except ModuleNotFoundError:
    import delphin_6_automation.database_interactions.auth_travis as authorisation

import delphin_6_automation.database_interactions.delphin_interactions as delphin_interact
import delphin_6_automation.database_interactions.material_interactions as material_interact
import delphin_6_automation.database_interactions.mongo_setup as mongo_setup
import delphin_6_automation.database_interactions.weather_interactions as weather_interact
import delphin_6_automation.file_parsing.weather_parser as weather_parser
import delphin_6_automation.pytest.pytest_helper_functions as helper

# -------------------------------------------------------------------------------------------------------------------- #
# TEST

mongo_setup.global_init(authorisation)


def test_upload_weather_1():
    # Local Files
    folder = os.path.dirname(os.path.abspath(__file__)) + '/test_files'
    weather_file = 'Aberdeen_-2.083_57.167_2020_2050_A1B.WAC'

    # Upload
    weather_ids = weather_parser.wac_to_db(folder + '/' + weather_file)

    # Convert uploaded entry back to dict
    weather_dict = dict(weather_db.Weather.objects(id=weather_ids[15]).first().to_mongo())
    with open(folder + '/Aberdeen_db_entry.txt') as outfile:
        source_entry = bson.json_util.loads(json.load(outfile))

    # Clean up mess
    source_entry.pop('added_date')
    source_entry.pop('_id')
    source_entry.pop('dates')
    weather_dict.pop('added_date')
    weather_dict.pop('_id')
    weather_dict.pop('dates')

    for weather_id in weather_ids:
        weather_db.Weather.objects(id=weather_id).first().delete()

    # Assert
    assert weather_dict == source_entry


def test_upload_materials_1():
    # Local Files
    folder = os.path.dirname(os.path.abspath(__file__)) + '/test_files'
    material_file = 'AltbauziegelDresdenZO_503.m6'

    # Upload
    material_id = material_interact.upload_material_file(folder + '/' + material_file)

    # Convert uploaded entry back to dict
    material_doc = material_db.Material.objects(id=material_id).first()
    material_dict = dict(material_doc.to_mongo())
    with open(folder + '/AltbauZiegel_entry.txt') as outfile:
        source_entry = bson.json_util.loads(json.load(outfile))

    # Clean up mess
    source_entry.pop('added_date')
    source_entry.pop('_id')
    source_entry['material_data'].pop('INFO-MATERIAL_NAME')
    source_entry['material_data'].pop('INFO-LAST_MODIFIED')
    source_entry['material_data'].pop('INFO-FILE')

    material_dict.pop('added_date')
    material_dict.pop('_id')
    material_dict['material_data'].pop('INFO-MATERIAL_NAME')
    material_dict['material_data'].pop('INFO-LAST_MODIFIED')
    material_dict['material_data'].pop('INFO-FILE')

    # Assert
    #material_doc.delete()
    for key in material_dict.keys():
        assert material_dict[key] == source_entry[key]


def test_upload_project_1():
    """Test upload of delphin project without any weather"""

    material_ids = helper.upload_needed_materials('upload_project_1')
    folder = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    delphin_file = folder + '/delphin_project.d6p'
    id_ = delphin_interact.upload_delphin_to_database(delphin_file, 10)

    test_doc = delphin_db.Delphin.objects(id=id_).first()
    test_dict = test_doc.to_mongo()
    test_dict.pop('_id')
    test_dict.pop('added_date')
    materials = test_dict.pop('materials')

    with open(folder + '/delphin_project_entry.txt') as outfile:
        source_entry = bson.json_util.loads(json.load(outfile))

    source_entry.pop('_id')
    source_entry.pop('added_date')
    source_entry.pop('materials')

    # Clean up
    test_doc.delete()
    for id_ in material_ids:
        material_db.Material.objects(id=id_).first().delete()

    assert test_dict == source_entry
    assert materials == material_ids


def test_upload_project_2():
    """Test upload of delphin project with weather"""

    material_ids = helper.upload_needed_materials('upload_project_2')
    weather_ids = helper.upload_needed_weather('upload_project_2')

    folder = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    delphin_file = folder + '/delphin_project.d6p'
    id_ = delphin_interact.upload_delphin_to_database(delphin_file, 10)

    test_doc = delphin_db.Delphin.objects(id=id_).first()
    weather_interact.assign_weather_to_project(id_, weather_ids)
    test_doc.reload()
    test_dict = test_doc.to_mongo()
    test_dict.pop('_id')
    test_dict.pop('added_date')
    materials = test_dict.pop('materials')
    weather = test_dict.pop('weather')

    with open(folder + '/delphin_project_with_weather_entry.txt') as outfile:
        source_entry = bson.json_util.loads(json.load(outfile))

    source_entry.pop('_id')
    source_entry.pop('added_date')
    source_entry.pop('materials')
    source_entry.pop('weather')

    # Clean up
    test_doc.delete()
    for material_id in material_ids:
        material_db.Material.objects(id=material_id).first().delete()
    for weather_id in weather_ids:
        weather_db.Weather.objects(id=weather_id).first().delete()

    assert test_dict == source_entry
    assert materials == material_ids
    assert weather == weather_ids


def test_upload_results_1():
    # Create test folders
    result_folder, source_path = helper.setup_test_folders()

    # Upload Delphin Project, so it can be linked to
    material_ids = helper.upload_needed_materials('upload_project_1')
    folder = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    delphin_file = folder + '/delphin_project.d6p'
    delphin_id = delphin_interact.upload_delphin_to_database(delphin_file, 10)

    # Upload results
    result_zip = folder + '/delphin_results.zip'
    shutil.unpack_archive(result_zip, result_folder)
    os.rename(result_folder + '/delphin_results', result_folder + '/' + str(delphin_id))
    result_id = delphin_interact.upload_results_to_database(result_folder + '/' + str(delphin_id))

    # Prepare test
    test_doc = result_db.Result.objects(id=result_id).first()
    test_dict = test_doc.to_mongo()
    test_dict.pop('_id')
    test_dict.pop('added_date')
    test_dict.pop('delphin')
    test_dict.pop('simulation_started')

    with open(folder + '/delphin_result_entry.txt') as outfile:
        source_entry = bson.json_util.loads(json.load(outfile))

    source_entry.pop('_id')
    source_entry.pop('added_date')
    source_entry.pop('delphin')
    source_entry.pop('simulation_started')

    # Clean up
    test_doc.delete()
    delphin_db.Delphin.objects(id=delphin_id).first().delete()
    for material_id in material_ids:
        material_db.Material.objects(id=material_id).first().delete()
    helper.clean_up_test_folders()

    # Assert
    assert test_dict == source_entry
