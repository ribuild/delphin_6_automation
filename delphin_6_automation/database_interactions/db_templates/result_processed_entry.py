__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

from datetime import datetime

# Modules:
import mongoengine

# RiBuild Modules:
import delphin_6_automation.database_interactions.database_collections as collections


#from delphin_6_automation.nosql.db_templates.delphin_entry import Delphin

# -------------------------------------------------------------------------------------------------------------------- #
# RESULT CLASS


class ProcessedResult(mongoengine.Document):

    added_date = mongoengine.DateTimeField(default=datetime.now)
    delphin = mongoengine.GenericReferenceField(required=True)
    results_raw = mongoengine.GenericReferenceField(required=True)

    meta = collections.processed_result_db
