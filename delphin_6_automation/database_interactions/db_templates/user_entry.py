__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import mongoengine
from _datetime import datetime

# RiBuild Modules
import delphin_6_automation.database_interactions.database_collections as collections

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild User


class User(mongoengine.Document):

    email = mongoengine.EmailField(required=True)
    password = mongoengine.StringField(required=False)
    added_date = mongoengine.DateTimeField(default=datetime.now)
    name = mongoengine.StringField(required=True)

    meta = collections.user_db