__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import mongoengine
import datetime

# RiBuild Modules
import delphin_6_automation.database_interactions.database_collections as collections
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


class Log(mongoengine.Document):

    # Meta Data
    added_data = mongoengine.DateTimeField(default=datetime.datetime.now())

    # References
    delphin = mongoengine.ReferenceField(document_type=delphin_entry.Delphin)

    # Data