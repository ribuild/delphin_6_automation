__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import mongoengine
from datetime import datetime

# RiBuild Modules:


# -------------------------------------------------------------------------------------------------------------------- #
# MATERIAL CLASS


class Material(mongoengine.Document):

    meta = {'db_alias': 'core',
            'collection': 'materials'
            }
