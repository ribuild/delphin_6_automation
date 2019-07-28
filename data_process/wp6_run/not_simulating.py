__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions import simulation_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

if __name__ == "__main__":
    server = mongo_setup.global_init(auth_dict)

    entries = delphin_entry.Delphin.objects(simulating__ne=None)

    print(f'There is {entries.count()} simulating projects in the database')

    for entry in entries:
        simulation_interactions.set_simulating(entry.id, False)

    print(f'There is now {entries.count()} simulating projects in the database')
    mongo_setup.global_end_ssh(server)
