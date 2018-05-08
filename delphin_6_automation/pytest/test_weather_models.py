__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import numpy as np
import matplotlib.pyplot as plt

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


def test_solar_radiation():
    folder = os.path.join(os.path.dirname(__file__), 'test_files')

    diff_rad = np.array(weather_parser.ccd_to_list(folder + '/diffuse_radiation.ccd'))
    dir_rad = np.array(weather_parser.ccd_to_list(folder + '/direct_radiation.ccd'))
    radiation = diff_rad + dir_rad
    hour_of_the_year = np.array([int(i) for i in range(8760)] * 3)
    short_wave = weather_modeling.short_wave_radiation(radiation, -2.083, 57.167, hour_of_the_year, 0, 230)

    plt.figure()
    plt.plot(np.linspace(0, len(radiation), len(radiation)), short_wave)
    plt.show()

    print(short_wave)