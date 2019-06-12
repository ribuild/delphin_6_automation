__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions.auth import auth_dict

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)

samples = sample_entry.Sample.objects().only('delphin_docs')

for sample in samples:
    print(sample)
    delphin_ids = [delp.id for delp in sample.delphin_docs]

    simulated = [False] * len(delphin_ids)
    print(f'Checking if Delphin projects have been simulated')

    for index, id_ in enumerate(delphin_ids):
        entry = delphin_entry.Delphin.objects(id=id_).only('simulated').first()

        if entry.simulated:
            simulated[index] = True

    print(f'Waiting until all projects are simulated. {sum(simulated)}/{len(simulated)} is simulated')
    print('')

mongo_setup.global_end_ssh(server)
