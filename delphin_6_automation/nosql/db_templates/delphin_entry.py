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
# DELPHIN CLASS


class Delphin(mongoengine.Document):

    added_date = mongoengine.DateTimeField(default=datetime.now)
    simulated = mongoengine.DateTimeField()
    simulating = mongoengine.BooleanField(default=False)
    queue_priority = mongoengine.IntField(default=1)
    dimensions = mongoengine.IntField(required=True)

    # References
    result_db = mongoengine.DictField()
    result_id = mongoengine.ObjectIdField()
    dp6_file = mongoengine.DictField(required=True)
    materials = mongoengine.DictField(required=True)
    weather = mongoengine.DictField(required=True)

    meta = collections.delphin_db['db_alias']
