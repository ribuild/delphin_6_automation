__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import os.path
import shutil
import json
import bson.json_util

# RiBuild Modules:
import delphin_6_automation.database_interactions.delphin_interactions as delphin_interact
import delphin_6_automation.nosql.mongo_setup as mongo_setup
from delphin_6_automation.nosql.auth import dtu_byg
import delphin_6_automation.nosql.db_templates.delphin_entry as delphin_db
import delphin_6_automation.nosql.db_templates.result_raw_entry as result_db
import delphin_6_automation.nosql.db_templates.weather_entry as weather_db
import delphin_6_automation.pytest.pytest_helper_functions as helper
import delphin_6_automation.file_parsing.delphin_weather_file as weather_parser

# -------------------------------------------------------------------------------------------------------------------- #
# TEST

mongo_setup.global_init(dtu_byg)


def test_upload_project_1():
    delphin_file = os.path.dirname(os.path.realpath(__file__)) + '/test_files/5a5479095d9460327c6970f0.d6p'
    id_ = delphin_interact.upload_to_database(delphin_file, 10)

    test_doc = delphin_db.Delphin.objects(id=id_).first()
    test_dict = test_doc.to_mongo()
    test_dict.pop('_id')
    test_dict.pop('added_date')

    source_dict = delphin_db.Delphin.objects(id='5a5479095d9460327c6970f0').first().to_mongo()
    source_dict.pop('_id')
    source_dict.pop('added_date')

    assert test_dict == source_dict
    test_doc.delete()


def test_upload_results_1():
    test_path, source_path = helper.setup_test_folders()
    result_zip = os.path.dirname(os.path.realpath(__file__)) + '/test_files/5a5479095d9460327c6970f0.zip'
    result_folder = test_path
    shutil.unpack_archive(result_zip, result_folder)
    id_ = delphin_interact.results_to_mongo_db(result_folder + '/5a5479095d9460327c6970f0')

    test_doc = result_db.Result.objects(id=id_).first()
    test_dict = test_doc.to_mongo()
    test_dict.pop('_id')
    test_dict.pop('added_date')

    source_dict = result_db.Result.objects(id='5a54a8a35d946027d804103c').first().to_mongo()
    source_dict.pop('_id')
    source_dict.pop('added_date')

    assert test_dict == source_dict
    test_doc.delete()
    helper.clean_up_test_folders()


def test_upload_materials_1():
    # TODO
    pass


def test_upload_weather_1():
    # Local Files
    folder = os.path.dirname(os.path.abspath(__file__)) + '/test_files'
    weather_file = 'Aberdeen_-2.083_57.167_2020_2050_A1B.WAC'

    # Upload
    weather_ids = weather_parser.wac_to_db(folder + '/' + weather_file)

    # Convert uploaded entry to back to dict
    weather_dict = dict(weather_db.Weather.objects(id=weather_ids[15]).first().to_mongo())
    with open(folder + '/Aberdeen_db_entry.txt') as outfile:
        loaded_entry = bson.json_util.loads(json.load(outfile))

    # Clean up mess
    loaded_entry.pop('added_date')
    loaded_entry.pop('_id')
    loaded_entry.pop('dates')
    weather_dict.pop('added_date')
    weather_dict.pop('_id')
    weather_dict.pop('dates')

    # Assert
    assert weather_dict == loaded_entry


def test_upload_indoor_climate_1():
    weather_id = '5a65ec9b5d946021a84937df'
    weather_parser.add_indoor_climate_to_weather_db(weather_id)
