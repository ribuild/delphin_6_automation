__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup, sampling_interactions, simulation_interactions
from delphin_6_automation.database_interactions.auth import auth_dict

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

if __name__ == "__main__":

    server = mongo_setup.global_init(auth_dict)

    print('Starting')
    strategy_doc = sample_entry.Strategy.objects().first()
    strategy_id = strategy_doc.id

    print(f'Current Iteration is: {strategy_doc.current_iteration}')
    sample_doc = sample_entry.Sample.objects(iteration=strategy_doc.current_iteration).first()
    sample_id = sample_doc.id

    print(f'Getting Delphin IDs for sample: {sample_id}')
    #delphin_ids = sample_doc.delphin_docs.get("id")

    print('Updating queue')

    delphin = sample_doc.delphin_docs

    for doc in delphin:
        doc.update(set__queue_priority=1)

    mongo_setup.global_end_ssh(server)
