__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import mongoengine
from datetime import datetime

# RiBuild Modules
import delphin_6_automation.database_interactions.database_collections as collections

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


class TimeModel(mongoengine.Document):

    # Meta Data
    added_date = mongoengine.DateTimeField(default=datetime.now)
    meta = collections.time_model_db

    # Model Data
    model = mongoengine.BinaryField(required=True)
    test_score = mongoengine.FloatField(required=True)
    model_parameters = mongoengine.ListField(required=True)
    model_features = mongoengine.ListField(required=True)

    # References
    sample_strategy = mongoengine.GenericReferenceField(required=True)
