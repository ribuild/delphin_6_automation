__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os

# RiBuild Modules
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry

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
