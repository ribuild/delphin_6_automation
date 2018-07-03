__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import mongoengine
from datetime import datetime

# RiBuild Modules:
import delphin_6_automation.database_interactions.database_collections as collections


# -------------------------------------------------------------------------------------------------------------------- #
# RESULT CLASS


class ProcessedResult(mongoengine.Document):

    # Meta
    meta = collections.processed_result_db
    added_date = mongoengine.DateTimeField(default=datetime.now)
    delphin = mongoengine.GenericReferenceField(required=True)
    results_raw = mongoengine.GenericReferenceField(required=True)

    # Results
    mould = mongoengine.FileField(required=True, db_alias=meta['db_alias'],
                                  collection_name=meta['collection'])
    heat_loss = mongoengine.FileField(required=True, db_alias=meta['db_alias'],
                                      collection_name=meta['collection'])
    algae = mongoengine.FileField(required=True, db_alias=meta['db_alias'],
                                  collection_name=meta['collection'])

    u_value = mongoengine.FloatField(required=True)
    thresholds = mongoengine.DictField(required=True)
