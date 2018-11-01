__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import shutil
import datetime
import pytest

# RiBuild Modules
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import simulation_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_list_weather_stations(add_three_years_weather):

    weather_list = general_interactions.list_weather_stations()

    assert weather_list
    assert isinstance(weather_list, dict)


def test_download_full_project_from_database(db_one_project, tmpdir):

    folder = tmpdir.mkdir('test')

    delphin_doc = delphin_entry.Delphin.objects().first()

    general_interactions.download_full_project_from_database(delphin_doc.id, folder)

    weather = ['indoor_relative_humidity.ccd', 'indoor_temperature.ccd', 'long_wave_radiation.ccd',
               'relative_humidity.ccd', 'short_wave_radiation.ccd', 'temperature.ccd',
               'wind_driven_rain.ccd', 'wind_speed.ccd']
    materials = ['AltbauziegelDresdenZP_504.m6', 'LimeCementMortarHighCementRatio_717.m6']

    assert os.path.exists(os.path.join(folder, f'{delphin_doc.id}.d6p'))
    assert os.path.exists(os.path.join(folder, 'weather'))
    assert all([weather_ in os.listdir(os.path.join(folder, 'weather'))
               for weather_ in weather])
    assert os.path.exists(os.path.join(folder, 'materials'))
    assert all([material in os.listdir(os.path.join(folder, 'materials'))
               for material in materials])


def test_download_results_1(add_results, tmpdir, test_folder):

    folder = tmpdir.mkdir('test')
    source_folder = tmpdir.mkdir('source')
    general_interactions.download_raw_result(add_results, folder)
    shutil.unpack_archive(test_folder + '/raw_results/delphin_results.zip', source_folder)

    source_g6a = open(os.path.join(source_folder,
                                   'delphin_results/results/5a5479095d9460327c6970f0_2823182570.g6a'), 'r').readlines()
    test_g6a = open(os.path.join(folder,
                                 f'{add_results}/results/5a5479095d9460327c6970f0_2823182570.g6a'), 'r').readlines()
    assert test_g6a == source_g6a

    source_d6o = open(os.path.join(source_folder,
                                   'delphin_results/results/Surface relative humidity - left side, outdoor.d6o'),
                      'r').readlines()
    del source_d6o[3]
    test_d6o = open(os.path.join(folder,
                                 f'{add_results}/results/Surface relative humidity - left side, outdoor.d6o'),
                    'r').readlines()
    del test_d6o[3]
    assert test_d6o == source_d6o


@pytest.mark.parametrize('sim_time',
                         [0, 1, 2])
def test_get_average_computation_time(db_one_project, sim_time):

    delphin_id = delphin_entry.Delphin.objects().first().id
    if sim_time == 1:
        delta_time = datetime.timedelta(minutes=3)
        simulation_interactions.set_simulation_time(delphin_id, delta_time)
    elif sim_time == 2:
        simulation_interactions.set_simulation_time_estimate(delphin_id, 5)

    computation_time = general_interactions.compute_simulation_time(delphin_id)

    assert computation_time
    assert isinstance(computation_time, int)

    if sim_time == 1:
        assert computation_time == 3
    elif sim_time == 2:
        assert computation_time == 5
    else:
        assert computation_time == 120
