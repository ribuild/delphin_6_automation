__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import mongoengine
from datetime import datetime

# RiBuild Modules:
import delphin_6_automation.nosql.database_collections as collections

# -------------------------------------------------------------------------------------------------------------------- #
# WEATHER CLASS


class Weather(mongoengine.Document):

    # Weather Data
    temperature = mongoengine.ListField(required=True)
    relative_humidity = mongoengine.ListField(required=True)
    vertical_rain = mongoengine.ListField(required=True)
    wind_direction = mongoengine.ListField(required=True)
    wind_speed = mongoengine.ListField(required=True)
    long_wave_radiation = mongoengine.ListField(required=True)
    diffuse_radiation = mongoengine.ListField(required=True)
    direct_radiation = mongoengine.ListField(required=True)
    dates = mongoengine.ListField(required=True)

    # Indoor Data
    indoor_temperature_a = mongoengine.ListField()
    indoor_relative_humidity_a = mongoengine.ListField()
    indoor_temperature_b = mongoengine.ListField()
    indoor_relative_humidity_b = mongoengine.ListField()

    # Meta Data
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    units = mongoengine.DictField(required=True)

    meta = collections.weather_db
