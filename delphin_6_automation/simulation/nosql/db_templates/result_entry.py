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
# RESULT CLASS


class Result(mongoengine.Document):

    added_date = mongoengine.DateTimeField(default=datetime.now)
    delphin_id = mongoengine.ObjectIdField(required=True)
    delphin_db = mongoengine.DictField(required=True)
    process_db = mongoengine.DictField()
    process_id = mongoengine.ObjectIdField()

    log = mongoengine.DictField(required=True)
    results = mongoengine.DictField(required=True)
    geometry_file = mongoengine.DictField(required=True)
    geometry_file_hash = mongoengine.IntField(required=True)
    simulation_started = mongoengine.DateTimeField(required=True)

    meta = collections.raw_result_db


class ProcessedResult(mongoengine.Document):

    added_date = mongoengine.DateTimeField(default=datetime.now)
    delphin_id = mongoengine.ObjectIdField(required=True)
    delphin_db = mongoengine.DictField(required=True)
    raw_db = mongoengine.DictField(required=True)
    raw_id = mongoengine.ObjectIdField(required=True)

    meta = collections.processed_result_db
