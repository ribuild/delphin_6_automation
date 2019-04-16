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

folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\test\Hans'

for project in delphin_entry.Delphin.objects(simulated__exists=True).only('id')[:2]:
    project_id = str(project.id)
    project_folder = os.path.join(folder, str(project_id))

    os.mkdir(project_folder)

    general_interactions.download_full_project_from_database(project_id, project_folder)
    general_interactions.download_sample_data(project_id, project_folder)

mongo_setup.global_end_ssh(server)
