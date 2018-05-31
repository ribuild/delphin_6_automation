__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

from datetime import datetime

# Modules:
import mongoengine

# RiBuild Modules:
import delphin_6_automation.database_interactions.database_collections as collections


# -------------------------------------------------------------------------------------------------------------------- #
# WEATHER CLASS


class Weather(mongoengine.Document):
    meta = collections.weather_db

    # Weather Data
    weather_data = mongoengine.FileField(required=True, db_alias=meta['db_alias'],
                                         collection_name=meta['collection'])
    # weather_data = {'temperature': [], 'vertical_rain': [], 'wind_direction': [], 'wind_speed': [],
    # 'long_wave_radiation': [], 'diffuse_radiation': [], 'direct_radiation': []}

    # Meta Data
    dates = mongoengine.DictField(mongoengine.DateTimeField, required=True)
    year = mongoengine.IntField(required=True)
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    location_name = mongoengine.StringField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    units = mongoengine.DictField(required=True)
