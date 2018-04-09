__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os

# RiBuild Modules
from delphin_6_automation.delphin_setup import weather_modeling
from delphin_6_automation.file_parsing import weather_parser

# -------------------------------------------------------------------------------------------------------------------- #
# TEST WEATHER MODELS


def test_rain_model():
    folder = os.path.join(os.path.dirname(__file__), 'test_files')

    rain = weather_parser.ccd_to_list(folder + '/vertical_rain.ccd')
    wind_speed = weather_parser.ccd_to_list(folder + '/wind_speed.ccd')
    wind_direction = weather_parser.ccd_to_list(folder + '/wind_direction.ccd')
    wall_location = {'height': 5, 'width': 5}
    wdr = weather_modeling.driving_rain(rain, wind_direction, wind_speed, wall_location, 90, 0)

    assert rain == wdr
