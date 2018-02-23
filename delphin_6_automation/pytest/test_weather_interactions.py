__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:

# RiBuild Modules:
import delphin_6_automation.database_interactions.mongo_setup as mongo_setup
from delphin_6_automation.database_interactions.auth import dtu_byg

# -------------------------------------------------------------------------------------------------------------------- #
# TEST

mongo_setup.global_init(dtu_byg)


def test_assign_indoor_climate_1():
    pass


def test_assign_weather_1():
    pass

