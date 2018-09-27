__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import mongoengine
from datetime import datetime

# RiBuild Modules
import delphin_6_automation.database_interactions.database_collections as collections
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


class Sample(mongoengine.Document):

    # Meta Data
    added_date = mongoengine.DateTimeField(default=datetime.now)

    # References
    samples = mongoengine.DictField(required=True)
    delphin_docs = mongoengine.ListField(field=mongoengine.ReferenceField(document_type=delphin_entry.Delphin))
    iteration = mongoengine.IntField(required=True)
    mean = mongoengine.DictField()
    standard_deviation = mongoengine.DictField()

    meta = collections.sample_db


class SampleRaw(mongoengine.Document):

    # Meta Data
    added_date = mongoengine.DateTimeField(default=datetime.now)

    # References
    samples_raw = mongoengine.ListField(required=True)
    sequence_number = mongoengine.IntField(required=True)

    meta = collections.sample_raw_db


class Strategy(mongoengine.Document):

    # Meta Data
    added_date = mongoengine.DateTimeField(default=datetime.now)
    current_iteration = mongoengine.IntField(default=0)
    used_samples_per_set = mongoengine.IntField(default=0)
    meta = collections.strategy_db

    # References
    samples = mongoengine.ListField(field=mongoengine.ReferenceField(document_type=Sample))
    samples_raw = mongoengine.ListField(field=mongoengine.ReferenceField(document_type=SampleRaw))
    standard_error = mongoengine.DictField()
    strategy = mongoengine.DictField(required=True)
    time_prediction_model = mongoengine.BinaryField()
