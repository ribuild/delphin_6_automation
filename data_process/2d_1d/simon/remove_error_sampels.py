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
from delphin_6_automation.database_interactions import simulation_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)

samples = sample_entry.Sample.objects(iteration=3)

print(samples.count())

for sample in samples:

    print(f'In sample with ID: {sample.id}')
    delphin_projects = sample.delphin_docs

    for entry in delphin_projects:
        if delphin_entry.Delphin.objects(id=entry.id):
            print(f'Deleting project with ID: {entry.id}')
            #entry.delete()
        else:
            print(f'ID: {entry.id} does not exists')


mongo_setup.global_end_ssh(server)
