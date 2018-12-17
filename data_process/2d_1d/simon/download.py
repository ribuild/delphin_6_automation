__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import getpass
import os
import pathlib

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_2d_1d as auth_dict
from delphin_6_automation.database_interactions import general_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


user = getpass.getuser()

folder = os.path.join('C:\\', 'Users', user, 'Desktop', '2D-1D', 'Simulated')

if not os.path.exists(folder):
    pathlib.Path(folder).mkdir(parents=True)

server = mongo_setup.global_init(auth_dict)
simulated_projects = delphin_entry.Delphin.objects(simulated__exists=True)

print(f'There are currently {len(simulated_projects)} simulated projects in the database')
print(f'Downloading Projects')
"""
for project in simulated_projects[:10]:
    project_folder = os.path.join(folder, str(project.id))

    if not os.path.exists(project_folder):
        print(f'\nDownloads Project with ID: {project.id}')

        os.mkdir(project_folder)
        general_interactions.download_full_project_from_database(project.id, project_folder)
        general_interactions.download_sample_data(project.id, project_folder)

        result_id = str(project.results_raw.id)
        general_interactions.download_raw_result(result_id, project_folder)

    else:
        print(f'Skipping Project with ID: {project.id}. Already downloaded.')
"""
mongo_setup.global_end_ssh(server)
