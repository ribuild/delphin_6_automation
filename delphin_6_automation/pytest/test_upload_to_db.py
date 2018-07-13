__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import os.path
import shutil
import bson.json_util
import datetime
import pytest

# RiBuild Modules:
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import material_entry
from delphin_6_automation.database_interactions.db_templates import result_raw_entry
from delphin_6_automation.database_interactions.db_templates import weather_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions import sampling_interactions
from delphin_6_automation.file_parsing import delphin_parser
from delphin_6_automation.sampling import sampling


# -------------------------------------------------------------------------------------------------------------------- #
# TEST


def test_upload_weather_1(test_folder, empty_database):
    # Local Files
    weather_file = 'Aberdeen_-2.083_57.167_2020_2050_A1B.WAC'

    # Upload
    weather_interactions.upload_weather_to_db(test_folder + '/weather/' + weather_file)

    assert len(weather_entry.Weather.objects()) == 31

    for weather in weather_entry.Weather.objects():
        assert isinstance(weather.year, int)
        assert isinstance(weather.location, list)
        assert weather.location[0] == -2.083
        assert weather.location[1] == 57.167
        assert weather.location_name == 'Aberdeen'

        weather_data: dict = bson.BSON.decode(weather.weather_data.read())
        for quantity in ['temperature', 'relative_humidity', 'vertical_rain', 'wind_direction',
                         'wind_speed', 'long_wave_radiation', 'diffuse_radiation', 'direct_radiation']:
            assert quantity in weather_data


def test_upload_materials_1(test_folder, empty_database):
    # Local Files
    material_file = 'AltbauziegelDresdenZP_504.m6'

    # Upload
    material_interactions.upload_material_file(test_folder + '/materials/' + material_file)

    assert len(material_entry.Material.objects()) == 1

    material = material_entry.Material.objects().first()
    assert material.material_name == 'AltbauziegelDresdenZP'
    assert material.material_id == 504
    assert isinstance(material.material_data, dict)


def test_upload_project_1(delphin_file_path, empty_database, add_two_materials):
    """Test upload of delphin project without any weather"""

    delphin_interactions.upload_delphin_to_database(delphin_file_path, 10)

    assert len(delphin_entry.Delphin.objects()) == 1
    test_doc = delphin_entry.Delphin.objects().first()

    assert not test_doc.simulating
    assert test_doc.dimensions == 1
    assert isinstance(test_doc.dp6_file, dict)
    assert isinstance(test_doc.materials, list)
    assert not test_doc.weather
    assert not test_doc.indoor_climate
    assert not test_doc.results_raw
    assert not test_doc.simulated
    assert not test_doc.simulation_time


def test_upload_project_2(delphin_file_path, empty_database, add_two_materials, add_three_years_weather):
    """Test upload of delphin project with weather"""

    id_ = delphin_interactions.upload_delphin_to_database(delphin_file_path, 10)
    weather_interactions.assign_weather_to_project(id_, add_three_years_weather)

    assert len(delphin_entry.Delphin.objects()) == 1
    test_doc = delphin_entry.Delphin.objects().first()

    assert not test_doc.simulating
    assert test_doc.dimensions == 1
    assert isinstance(test_doc.dp6_file, dict)
    assert isinstance(test_doc.materials, list)
    assert len(test_doc.weather) == 3
    assert not test_doc.indoor_climate
    assert not test_doc.results_raw
    assert not test_doc.simulated
    assert not test_doc.simulation_time


def test_upload_results_1(db_one_project, test_folder, tmpdir):
    temp_folder = tmpdir.mkdir('test')
    delphin_doc = delphin_entry.Delphin.objects().first()

    # Upload results
    result_zip = test_folder + '/raw_results/delphin_results.zip'
    shutil.unpack_archive(result_zip, temp_folder)
    os.rename(os.path.join(temp_folder, 'delphin_results'), os.path.join(temp_folder, str(delphin_doc.id)))
    result_id = delphin_interactions.upload_results_to_database(os.path.join(temp_folder, str(delphin_doc.id)))

    # Prepare test
    assert result_raw_entry.Result.objects()

    result_doc = result_raw_entry.Result.objects(id=result_id).first()
    delphin_doc.reload()

    # Assert
    assert result_doc.delphin == delphin_doc
    assert delphin_doc.results_raw == result_doc
    assert result_doc.log
    assert result_doc.results
    assert isinstance(result_doc.geometry_file, dict)
    assert result_doc.geometry_file_hash


def test_delphin_file_checker_1(delphin_file_path):
    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    assert not delphin_interactions.check_delphin_file(delphin_dict)


def test_cvode_stats(test_folder, tmpdir):
    temp_folder = tmpdir.mkdir('test')
    result_zip = test_folder + '/raw_results/delphin_results.zip'
    shutil.unpack_archive(result_zip, temp_folder)
    integrator_dict = delphin_parser.cvode_stats_to_dict(os.path.join(temp_folder,
                                                                      'delphin_results/log'))

    assert isinstance(integrator_dict, dict)


def test_upload_sampling_strategy(add_three_years_weather, tmpdir):
    test_dir = tmpdir.mkdir('test')
    strategy = sampling.create_sampling_strategy(test_dir)
    strategy_id = sampling_interactions.upload_sampling_strategy(strategy)

    strategy_doc = sample_entry.Strategy.objects().first()

    # Checks
    assert isinstance(strategy_doc.added_date, datetime.datetime)
    assert not strategy_doc.samples
    assert not strategy_doc.standard_error
    assert strategy_doc.strategy

    # Strategy Check
    assert isinstance(strategy_doc.strategy, dict)
    assert all(element in list(strategy_doc.strategy.keys())
               for element in ['design', 'scenario', 'distributions', 'settings'])

    # Strategy Scenario Check
    assert strategy_doc.strategy['scenario']
    assert isinstance(strategy_doc.strategy['scenario'], dict)

    # Strategy Distributions Check
    assert strategy_doc.strategy['distributions']
    assert isinstance(strategy_doc.strategy['distributions'], dict)
    for distribution in strategy_doc.strategy['distributions'].keys():
        assert all(element in list(strategy_doc.strategy['distributions'][distribution].keys())
                   for element in ['type', 'range'])
        assert strategy_doc.strategy['distributions'][distribution]['type']
        assert strategy_doc.strategy['distributions'][distribution]['range']

    # Strategy Settings Check
    assert strategy_doc.strategy['settings']
    setting_elements = ['initial samples per set', 'add samples per run',
                        'max samples', 'sequence', 'standard error threshold']
    assert all(element in list(strategy_doc.strategy['settings'].keys())
               for element in setting_elements)
    for setting in strategy_doc.strategy['settings'].keys():
        assert strategy_doc.strategy['settings'][setting]


def test_upload_raw_samples(empty_database):
    raw_id = sampling_interactions.upload_raw_samples(sampling.sobol(m=2 ** 12, dimension=3), 1)
    raw_entry = sample_entry.SampleRaw.objects(id=raw_id).first()

    assert raw_entry
    assert isinstance(raw_entry.added_date, datetime.datetime)
    assert isinstance(raw_entry.samples_raw, list)
    assert raw_entry.sequence_number == 1


def test_add_raw_samples_to_strategy(add_sampling_strategy, add_raw_sample):
    raw_entry = sample_entry.SampleRaw.objects().first()
    strategy_entry = sample_entry.Strategy.objects().first()

    sampling_interactions.add_raw_samples_to_strategy(strategy_entry, raw_entry.id)
    strategy_entry.reload()

    assert isinstance(strategy_entry.samples_raw, list)
    assert strategy_entry.samples_raw[0] == raw_entry


def test_upload_processed_results(add_results, tmpdir, test_folder):
    folder = tmpdir.mkdir('test')
    weather_folder = folder.mkdir('weather')
    result_zip = test_folder + '/raw_results/delphin_results1.zip'
    shutil.unpack_archive(result_zip, folder)
    shutil.copy(f'{test_folder}/weather/temperature.ccd', f'{weather_folder}/temperature.ccd')
    shutil.copy(f'{test_folder}/weather/indoor_temperature.ccd', f'{weather_folder}/indoor_temperature.ccd')
    result_doc = result_raw_entry.Result.objects().first()
    delphin_doc = delphin_entry.Delphin.objects().first()

    result_folder = os.path.join(folder, 'delphin_id/results')
    result_id = delphin_interactions.upload_processed_results(result_folder, delphin_doc, result_doc)


@pytest.mark.parametrize('iteration',
                         [0, 1, 2])
def test_upload_samples(setup_database, dummy_sample, iteration):

    sample_id = sampling_interactions.upload_samples(dummy_sample, iteration)
    sample_doc = sample_entry.Sample.objects(id=sample_id).first()

    assert sample_doc
    assert isinstance(sample_doc.added_date, datetime.datetime)

    assert sample_doc.samples
    assert isinstance(sample_doc.samples, dict)
    assert sample_doc.iteration == iteration
    assert not sample_doc.delphin_docs
    assert not sample_doc.standard_error
