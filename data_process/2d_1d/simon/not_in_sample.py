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

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)

sample = sample_entry.Sample.objects()

sample_projects = [delphin.id
                   for s in sample
                   for delphin in s.delphin_docs]


print(f'There is {len(sample_projects)} connected to a sample')

projects = delphin_entry.Delphin.objects()

print(f'There are currently {len(projects)} projects in the database')

print('Starting')
for proj in projects:
    if proj.id not in sample_projects:
        #print(f'Project with ID: {proj.id} is not part of a sample!')
        proj.delete()


mongo_setup.global_end_ssh(server)
