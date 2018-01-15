__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import mongoengine
from datetime import datetime

# RiBuild Modules:
import delphin_6_automation.simulation.nosql.database_collections as collections

# -------------------------------------------------------------------------------------------------------------------- #
# WEATHER CLASS


class Weather(mongoengine.Document):

    temperature = mongoengine.ListField(required=True)
    relative_humidity = mongoengine.ListField(required=True)
    vertical_rain = mongoengine.ListField(required=True)
    wind_direction = mongoengine.ListField(required=True)
    wind_speed = mongoengine.ListField(required=True)
    long_wave_radiation = mongoengine.ListField(required=True)
    diffuse_radiation = mongoengine.ListField(required=True)
    direct_radiation = mongoengine.ListField(required=True)

    location = mongoengine.GeoPointField(required=True)
    source = mongoengine.StringField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)

    meta = collections.weather_db
