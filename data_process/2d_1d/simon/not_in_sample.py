__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_2d_1d as auth_dict
from delphin_6_automation.database_interactions import general_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)

projects = delphin_entry.Delphin.objects()
sample = sample_entry.Sample.objects().first()
#sample_projects = set(list(sample.delphin_docs))

simulated_projects = delphin_entry.Delphin.objects(simulated__exists=True)

print(f'There are currently {len(simulated_projects)} simulated projects in the database')

"""
for proj in projects:
    if proj not in sample_projects:
        print(f'Project with ID: {proj.id} is not part of a sample!')
        #proj.delete()
"""

mongo_setup.global_end_ssh(server)
