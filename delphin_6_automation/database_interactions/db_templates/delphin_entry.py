__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import mongoengine
from datetime import datetime

# RiBuild Modules:
import delphin_6_automation.database_interactions.database_collections as collections
import delphin_6_automation.database_interactions.db_templates.result_processed_entry as processed_db
import delphin_6_automation.database_interactions.db_templates.material_entry as material_db
import delphin_6_automation.database_interactions.db_templates.result_raw_entry as raw_db
import delphin_6_automation.database_interactions.db_templates.weather_entry as weather_db

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN CLASS


class Delphin(mongoengine.Document):

    # Meta Data
    added_date = mongoengine.DateTimeField(default=datetime.now)
    simulated = mongoengine.DateTimeField()
    simulating = mongoengine.BooleanField(default=False)
    simulation_time = mongoengine.FloatField()
    exceeded_time_limit = mongoengine.BooleanField()
    queue_priority = mongoengine.IntField(default=1)
    sample_data = mongoengine.DictField()
    restart_data = mongoengine.DictField()

    # References
    dimensions = mongoengine.IntField(required=True)
    results_raw = mongoengine.ReferenceField(document_type=raw_db.Result)
    result_processed = mongoengine.ReferenceField(document_type=processed_db.ProcessedResult)
    dp6_file = mongoengine.DictField(required=True)
    materials = mongoengine.ListField(mongoengine.ReferenceField(document_type=material_db.Material))
    weather = mongoengine.ListField(mongoengine.ReferenceField(document_type=weather_db.Weather))
    indoor_climate = mongoengine.StringField()

    meta = collections.delphin_db
