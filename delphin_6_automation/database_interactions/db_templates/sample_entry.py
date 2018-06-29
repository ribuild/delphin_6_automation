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


class Sample(mongoengine.Document):

    # Meta Data
    added_date = mongoengine.DateTimeField(default=datetime.now)

    # References

    meta = collections.sample_db
