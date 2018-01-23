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
import delphin_6_automation.nosql.db_templates.delphin_entry as delphin_db
import delphin_6_automation.nosql.db_templates.result_processed_entry as processed_db

# -------------------------------------------------------------------------------------------------------------------- #
# RESULT CLASS


class Result(mongoengine.Document):

    added_date = mongoengine.DateTimeField(default=datetime.now)
    delphin = mongoengine.ReferenceField(document_type=delphin_db.Delphin)
    results_processed = mongoengine.ReferenceField(document_type=processed_db.ProcessedResult, required=True)

    log = mongoengine.DictField(required=True)
    results = mongoengine.DictField(required=True)
    geometry_file = mongoengine.DictField(required=True)
    geometry_file_hash = mongoengine.IntField(required=True)
    simulation_started = mongoengine.DateTimeField(required=True)

    meta = collections.raw_result_db
