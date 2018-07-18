__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import bson

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import weather_entry
from delphin_6_automation.database_interactions import weather_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_download_weather_1(db_one_project, test_folder, tmpdir):
    folder = tmpdir.mkdir('test')
    source_folder = test_folder + '/weather'

    # Setup
    delphin_doc = delphin_entry.Delphin.objects().first()
    weather_interactions.download_weather(delphin_doc, folder)

    def get_weather_files(path):
        files = []
        for file in ['short_wave_radiation.ccd', 'indoor_relative_humidity.ccd',
                     'indoor_temperature.ccd', 'long_wave_radiation.ccd', 'relative_humidity.ccd',
                     'temperature.ccd', 'wind_driven_rain.ccd', 'wind_speed.ccd']:
            file_obj = open(os.path.join(path, file), 'r')
            files.append(file_obj.readlines())
        return files

    # Get files
    test_files = get_weather_files(folder)
    source_files = get_weather_files(source_folder)

    # Assert
    assert test_files == source_files


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
