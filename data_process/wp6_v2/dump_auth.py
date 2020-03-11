__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
import os
import json
from delphin_6_automation.database_interactions.auth import auth_dict

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":

    folder = os.path.dirname(__file__)
    with open(os.path.join(folder, "db_ait.json"), 'w') as file:
        json.dump(auth_dict, file)
