__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

import os
import bson
import shutil

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import result_raw_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_2d_1d as auth_dict
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def download_raw_result(result_id: str, download_path: str) -> bool:
    """
    Downloads a result entry from the database.rst.

    :param result_id: Database entry id
    :param download_path: Path where the result should be written
    :return: True
    """

    result_obj = result_raw_entry.Result.objects(id=result_id).first()
    download_path = os.path.join(download_path, str(result_id))

    if not os.path.exists(download_path):
        os.mkdir(download_path)

    # delphin_parser.write_log_files(result_obj, download_path)
    download_result_files(result_obj, download_path)

    return True


def download_result_files(result_obj: result_raw_entry.Result, download_path: str) -> bool:
    """
    Writes out all the result files from a result database entry.

    :param result_obj: Raw result entry
    :param download_path: Where to write the files
    :return: True
    """

    result_dict: dict = bson.BSON.decode(result_obj.results.read())
    result_path = download_path + '/results'

    if not os.path.exists(result_path):
        os.mkdir(result_path)
    else:
        shutil.rmtree(result_path)
        os.mkdir(result_path)

    delphin_parser.dict_to_g6a(dict(result_obj.geometry_file), result_path)

    valid_results = ['heat loss', 'relative humidity interior surface',
                     'relative humidity mould', 'temperature interior surface', 'temperature mould']
    for result_name in result_dict.keys():
        if result_name in valid_results:
            delphin_parser.dict_to_d6o(result_dict[result_name], os.path.join(result_path, result_name),
                                       result_obj.simulation_started, result_obj.geometry_file['name'],
                                       result_obj.geometry_file_hash)

    return True


folder = r'C:\Users\ocni\Desktop\simulation_years_data'

server = mongo_setup.global_init(auth_dict)

print('Starts Downloading\n')
print(f'There are currently {delphin_entry.Delphin.objects(simulated__exists=True).filter(sample_data__design_option__dim="1D").count()} simulated projects in the database')
print(f'Downloading Projects\n')
print(f'-------------------------------------------------------------\n')

index = 0
for project in delphin_entry.Delphin.objects(simulated__exists=True).filter(sample_data__design_option__dim='1D').only('id'):

    project_id = str(project.id)
    project_folder = os.path.join(folder, str(project_id))

    if not os.path.exists(project_folder):
        print(f'Downloads Project with ID: {project_id}')
        result_id = str(delphin_entry.Delphin.objects(id=project_id).first().results_raw.id)
        os.mkdir(project_folder)
        general_interactions.download_sample_data(project_id, project_folder)
        download_raw_result(result_id, project_folder)

        index += 1
        if index % 1000 == 0:
            print(f'\n{index} projects have been downloaded\n')

    else:
        print(f'Skipping Project with ID: {project_id}. Already downloaded.')

mongo_setup.global_end_ssh(server)
