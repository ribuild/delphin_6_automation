__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import mongoengine
import delphin_6_automation.database_interactions.database_collections as collections

# RiBuild Modules:


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

class Normalized(mongoengine.Document):
    # Meta Data
    meta = collections.normalized_db

    delphin = mongoengine.GenericReferenceField()
    loc = mongoengine.PointField()

    orientation = mongoengine.IntField()
    wall_width = mongoengine.FloatField()
    wall_material = mongoengine.StringField()
    ext_plaster = mongoengine.BooleanField()
    int_plaster = mongoengine.BooleanField()
    country = mongoengine.StringField()
    city = mongoengine.StringField()
    heat_loss = mongoengine.FloatField()
    mould = mongoengine.FloatField()
    u_value = mongoengine.FloatField()
    algae = mongoengine.FloatField()
    environment_impact = mongoengine.FloatField()
    insulation_system = mongoengine.StringField()
    insulation_thickness = mongoengine.IntField()
    avg_surface_temp = mongoengine.FloatField()
    min_surface_temp = mongoengine.FloatField()
    lambda_value = mongoengine.FloatField()
    rain = mongoengine.FloatField()
