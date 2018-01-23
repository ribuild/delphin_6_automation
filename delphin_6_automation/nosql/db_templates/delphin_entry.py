__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import mongoengine
from datetime import datetime


# RiBuild Modules:
import delphin_6_automation.nosql.database_collections as collections
import delphin_6_automation.nosql.db_templates.result_raw_entry as result_db

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN CLASS


class Delphin(mongoengine.Document):

    added_date = mongoengine.DateTimeField(default=datetime.now)
    simulated = mongoengine.DateTimeField()
    simulating = mongoengine.BooleanField(default=False)
    queue_priority = mongoengine.IntField(default=1)
    dimensions = mongoengine.IntField(required=True)

    # References
    results_raw = mongoengine.ReferenceField(document_type=result_db.Result)
    result_processed = mongoengine.ReferenceField(document_type=result_db.ProcessedResult)
    dp6_file = mongoengine.DictField(required=True)
    materials = mongoengine.DictField(required=True)
    weather = mongoengine.DictField(required=True)

    meta = collections.delphin_db
