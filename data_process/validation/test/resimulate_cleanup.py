__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions.auth import validation as auth_dict
from delphin_6_automation.database_interactions import mongo_setup
# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


server = mongo_setup.global_init(auth_dict)


for project in delphin_entry.Delphin.objects(simulated__exists=True).only('id'):
    project_id = str(project.id)
    doc = delphin_entry.Delphin.objects(id=project_id).first()

    doc.update(unset__simulated=1)
    doc.update(unset__simulation_time=1)
    doc.update(unset__results_raw=1)
    doc.update(unset__result_processed=1)

mongo_setup.global_end_ssh(server)
