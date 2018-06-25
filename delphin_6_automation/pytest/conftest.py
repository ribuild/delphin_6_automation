__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest
from mongoengine.connection import get_connection
import os

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions import user_interactions
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions import delphin_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.fixture(scope='session')
def setup_database():
    auth_dict = {"ip": "192.38.64.134",
                 "port": 27017,
                 "alias": "local",
                 "name": "test",
                 "ssh": False}

    mongo_setup.global_init(auth_dict)

    yield

    db = get_connection('local')
    db.drop_database('test')
    mongo_setup.global_end_ssh(auth_dict)


@pytest.fixture(scope='function')
def empty_database(setup_database):

    db = get_connection('local')
    db.drop_database('test')

    yield


@pytest.fixture()
def test_folder():

    return os.path.dirname(os.path.realpath(__file__)) + '/test_files'


@pytest.fixture()
def delphin_file_path(test_folder):

    delphin_file = test_folder + '/delphin/delphin_project_1d.d6p'

    return delphin_file


@pytest.fixture()
def add_single_user(setup_database):

    user_interactions.create_account('User Test', 'test@test.com')

    yield


@pytest.fixture()
def add_two_materials(test_folder, setup_database):

    material_files = ['AltbauziegelDresdenZP_504.m6', 'LimeCementMortarHighCementRatio_717.m6', ]

    for file in material_files:
        material_interactions.upload_material_file(test_folder + '/materials/' + file)

    yield


@pytest.fixture()
def add_three_years_weather(setup_database, test_folder):

    weather_ids = weather_interactions.upload_weather_to_db(test_folder + '/weather/Aberdeen_3_years.WAC')

    return weather_ids


@pytest.fixture()
def db_one_project(empty_database, delphin_file_path, add_single_user, add_two_materials, add_three_years_weather):

    priority = 'high'
    climate_class = 'a'
    location_name = 'Aberdeen'
    years = [2020, 2020, 2021]

    sim_id = general_interactions.add_to_simulation_queue(delphin_file_path, priority)
    weather_interactions.assign_indoor_climate_to_project(sim_id, climate_class)
    weather_interactions.assign_weather_by_name_and_years(sim_id, location_name, years)
    delphin_interactions.change_entry_simulation_length(sim_id, len(years), 'a')

    yield
