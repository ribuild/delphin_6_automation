__author__ = "Christian Kongsgaard"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

from datetime import datetime

# Modules:
import mongoengine

# RiBuild Modules:
import delphin_6_automation.database_interactions.database_collections as collections


# -------------------------------------------------------------------------------------------------------------------- #
# MATERIAL CLASS


class Material(mongoengine.Document):

    material_name = mongoengine.StringField(required=True)
    material_id = mongoengine.IntField(required=True)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    material_data = mongoengine.DictField(required=True)

    meta = collections.material_db
