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


class Temperature(mongoengine.Document):

    temperature = mongoengine.ListField(required=True)
    dates = mongoengine.ListField(required=True)

    # Meta Data
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    unit = mongoengine.StringField(required=True)

    meta = collections.temperature_db


class RelativeHumidity(mongoengine.Document):
    relative_humidity = mongoengine.ListField(required=True)
    dates = mongoengine.ListField(required=True)

    # Meta Data
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    unit = mongoengine.StringField(required=True)

    meta = collections.relative_humidity_db


class VerticalRain(mongoengine.Document):
    vertical_rain = mongoengine.ListField(required=True)
    dates = mongoengine.ListField(required=True)

    # Meta Data
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    unit = mongoengine.StringField(required=True)

    meta = collections.vertical_rain_db


class WindDirection(mongoengine.Document):
    wind_direction = mongoengine.ListField(required=True)
    dates = mongoengine.ListField(required=True)

    # Meta Data
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    unit = mongoengine.StringField(required=True)

    meta = collections.wind_direction_db


class WindSpeed(mongoengine.Document):
    wind_speed = mongoengine.ListField(required=True)
    dates = mongoengine.ListField(required=True)

    # Meta Data
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    unit = mongoengine.StringField(required=True)

    meta = collections.wind_speed_db


class LongWaveRadiation(mongoengine.Document):
    long_wave_radiation = mongoengine.ListField(required=True)
    dates = mongoengine.ListField(required=True)

    # Meta Data
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    unit = mongoengine.StringField(required=True)

    meta = collections.long_wave_radiation_db


class DiffuseRadiation(mongoengine.Document):
    diffuse_radiation = mongoengine.ListField(required=True)
    dates = mongoengine.ListField(required=True)

    # Meta Data
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    unit = mongoengine.StringField(required=True)

    meta = collections.diffuse_radiation_db


class DirectRadiation(mongoengine.Document):
    direct_radiation = mongoengine.ListField(required=True)
    dates = mongoengine.ListField(required=True)

    # Meta Data
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    unit = mongoengine.StringField(required=True)

    meta = collections.direct_radiation_db


class Weather(mongoengine.Document):

    # Weather Data
    temperature = mongoengine.ReferenceField(document_type=Temperature, required=True)
    relative_humidity = mongoengine.ReferenceField(document_type=RelativeHumidity, required=True)
    vertical_rain = mongoengine.ReferenceField(document_type=VerticalRain, required=True)
    wind_direction = mongoengine.ReferenceField(document_type=WindDirection, required=True)
    wind_speed = mongoengine.ReferenceField(document_type=WindSpeed, required=True)
    long_wave_radiation = mongoengine.ReferenceField(document_type=LongWaveRadiation, required=True)
    diffuse_radiation = mongoengine.ReferenceField(document_type=DiffuseRadiation, required=True)
    direct_radiation = mongoengine.ReferenceField(document_type=DirectRadiation, required=True)
    dates = mongoengine.ListField(required=True)

    # Meta Data
    location = mongoengine.GeoPointField(required=True)
    altitude = mongoengine.FloatField(required=True)
    source = mongoengine.DictField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    units = mongoengine.DictField(required=True)

    meta = collections.weather_db
