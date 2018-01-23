__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import mongoengine
from datetime import datetime

# RiBuild Modules:
import delphin_6_automation.nosql.database_collections as collections
import delphin_6_automation.nosql.db_templates.delphin_entry as delphin_db
import delphin_6_automation.nosql.db_templates.result_raw_entry as raw_db

# -------------------------------------------------------------------------------------------------------------------- #
# RESULT CLASS


class ProcessedResult(mongoengine.Document):

    added_date = mongoengine.DateTimeField(default=datetime.now)
    delphin = mongoengine.ReferenceField(document_type=delphin_db.Delphin, required=True)
    results_raw = mongoengine.ReferenceField(document_type=raw_db.Result, required=True)

    meta = collections.processed_result_db
