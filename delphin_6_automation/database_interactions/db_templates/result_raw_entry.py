__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

from datetime import datetime

# Modules:
import mongoengine

# RiBuild Modules:
import delphin_6_automation.database_interactions.database_collections as collections


# -------------------------------------------------------------------------------------------------------------------- #
# RESULT CLASS

class Result(mongoengine.Document):
    meta = collections.raw_result_db

    added_date = mongoengine.DateTimeField(default=datetime.now)
    delphin = mongoengine.GenericReferenceField(required=True)
    result_processed = mongoengine.GenericReferenceField()

    log = mongoengine.FileField(db_alias=meta['db_alias'], collection_name=meta['collection'])
    results = mongoengine.FileField(required=True, db_alias=meta['db_alias'], collection_name=meta['collection'])
    geometry_file = mongoengine.DictField(required=True)
    geometry_file_hash = mongoengine.IntField(required=True)
    simulation_started = mongoengine.DateTimeField(required=True)
