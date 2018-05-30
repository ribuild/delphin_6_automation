__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import mongoengine
from _datetime import datetime

# RiBuild Modules
from delphin_6_automation.database_interactions import database_collections
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild User


class User(mongoengine.Document):

    email = mongoengine.EmailField(required=True)
    password = mongoengine.StringField(required=False)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    name = mongoengine.StringField(required=True)
    simulations = mongoengine.ListField(mongoengine.ReferenceField(document_type=delphin_entry.Delphin))

    meta = database_collections.user_db