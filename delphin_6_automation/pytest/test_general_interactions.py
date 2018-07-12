__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
from delphin_6_automation.database_interactions import general_interactions
# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_list_weather_stations(add_three_years_weather):

    weather_list = general_interactions.list_weather_stations()

    assert weather_list
    assert isinstance(weather_list, dict)
