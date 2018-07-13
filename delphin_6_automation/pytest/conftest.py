__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest
from mongoengine.connection import get_connection
import os
import shutil
import sys
import numpy as np

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions import user_interactions
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import sampling_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.sampling import sampling


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.fixture(scope='session')
def setup_database():
    if sys.platform == 'win32':
        auth_dict = {"ip": "192.38.64.134",
                     "port": 27017,
                     "alias": "local",
                     "name": "test",
                     "ssh": False}
    else:
        auth_dict = {"ip": "127.0.0.1",
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
    years = [2020, 2021, 2022]

    sim_id = general_interactions.add_to_simulation_queue(delphin_file_path, priority)
    weather_interactions.assign_indoor_climate_to_project(sim_id, climate_class)
    weather_interactions.assign_weather_by_name_and_years(sim_id, location_name, years)
    delphin_interactions.change_entry_simulation_length(sim_id, len(years), 'a')

    yield


@pytest.fixture()
def add_results(db_one_project, tmpdir, test_folder):
    temp_folder = tmpdir.mkdir('upload')
    delphin_doc = delphin_entry.Delphin.objects().first()

    # Upload results
    result_zip = test_folder + '/raw_results/delphin_results.zip'
    shutil.unpack_archive(result_zip, temp_folder)
    os.rename(os.path.join(temp_folder, 'delphin_results'), os.path.join(temp_folder, str(delphin_doc.id)))
    result_id = delphin_interactions.upload_results_to_database(os.path.join(temp_folder, str(delphin_doc.id)))

    return result_id


@pytest.fixture()
def add_sampling_strategy(empty_database, add_three_years_weather, tmpdir):
    test_dir = tmpdir.mkdir('test')
    strategy = sampling.create_sampling_strategy(test_dir)
    sampling_interactions.upload_sampling_strategy(strategy)


@pytest.fixture()
def add_raw_sample(setup_database):
    sampling_interactions.upload_raw_samples(sampling.sobol(m=2 ** 12, dimension=3), 0)


@pytest.fixture()
def strategy_with_raw_dummy_samples(add_sampling_strategy):
    strategy_entry = sample_entry.Strategy.objects().first()
    raw_id = sampling_interactions.upload_raw_samples(np.random.rand(2 ** 12,
                                                                     len(strategy_entry.strategy[
                                                                             'distributions'].keys())),
                                                      0)

    sampling_interactions.add_raw_samples_to_strategy(strategy_entry, raw_id)


@pytest.fixture()
def dummy_sample():
    return {str(i): {} for i in range(10)}


@pytest.fixture()
def mock_sobol(monkeypatch):
    strategy = sample_entry.Strategy.objects().first()

    def mockreturn(m, dimension, sets):
        return np.random.rand(2 ** 12, len(strategy.strategy['distributions'].keys()))

    monkeypatch.setattr(sampling, 'sobol', mockreturn)


@pytest.fixture()
def add_dummy_sample(setup_database, dummy_sample):

    sample_id = sampling_interactions.upload_samples(dummy_sample, 0)
    sample_doc = sample_entry.Sample.objects(id=sample_id).first()