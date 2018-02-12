__author__ = ""
__license__ = "MIT"
__version__ = "0.0.1"

# delphin_6_automation simulation.simulation_process
# Folder intended for everything related to the simulation itself on the computer pools.


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

import os
import shutil

import delphin_6_automation.nosql.db_templates.result_raw_entry as result_db
# Modules:
import xmltodict

# RiBuild Modules:
import delphin_6_automation.database_interactions.db_templates.delphin_entry as delphin_db
import delphin_6_automation.database_interactions.material_interactions as material_interact
from delphin_6_automation.file_parsing import delphin_parser


# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN FUNCTIONS AND CLASSES


def upload_delphin_to_database(delphin_file: str,  queue_priority: int) -> delphin_db.Delphin.id:
    """
    Uploads a Delphin file to a database.

    :param delphin_file: Path to a Delphin 6 project file
    :param queue_priority: Queue priority for the simulation
    :return: Database entry id
    """

    entry = delphin_db.Delphin()
    entry.queue_priority = queue_priority

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file)
    entry.dp6_file = delphin_dict
    entry.materials = material_interact.find_material_ids(material_interact.list_project_materials(entry))

    if len(delphin_dict['DelphinProject']['Discretization']) > 2:
        entry.dimensions = 3
    elif len(delphin_dict['DelphinProject']['Discretization']) > 1:
        entry.dimensions = 2
    else:
        entry.dimensions = 1

    entry.save()

    return entry.id


def download_delphin_entry(document_id: str, path: str) -> bool:
    """
    Converts a database entry to Delphin 6 project file.

    :param document_id: Database entry id.
    :param path: Path to where the files should be written.
    :return: True
    """

    delphin_document = delphin_db.Delphin.objects(id=document_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    xmltodict.unparse(delphin_dict, output=open(path + '/' + document_id + '.d6p', 'w'), pretty=True)

    return True


def upload_results_to_database(path_: str, delete_files: bool =True) -> bool:
    """
    Uploads the results from a Delphin simulation.

    :param path_: folder path containing the result files
    :param delete_files: if True the result folder will be deleted. Default is True
    :return: True on success
    """

    id_ = os.path.split(path_)[1]
    delphin_entry = delphin_db.Delphin.objects(id=id_).first()
    result_dict = {}
    result_path = path_ + '/results'
    log_path = path_ + '/log'
    geometry_dict = {}
    meta_dict = {}

    for result_file in os.listdir(result_path):
        if result_file.endswith('.d6o'):
            result_dict[result_file.split('.')[0]], meta_dict = delphin_parser.d6o_to_dict(result_path, result_file)

        elif result_file.endswith('.g6a'):
            geometry_dict = delphin_parser.g6a_to_dict(result_path, result_file)

    entry = result_db.Result()

    entry.delphin = delphin_entry
    entry.log['integrator_cvode_stats'] = delphin_parser.cvode_stats_to_dict(log_path)
    entry.log['les_direct_stats'] = delphin_parser.les_stats_to_dict(log_path)
    entry.log['progress'] = delphin_parser.progress_to_dict(log_path)
    entry.geometry_file = geometry_dict
    entry.results = result_dict
    entry.simulation_started = meta_dict['created']
    entry.geometry_file_hash = meta_dict['geo_file_hash']
    entry.save()

    # Add results reference to Delphin entry
    delphin_entry.update(push__results_raw=entry)

    if delete_files:
        shutil.rmtree(path_)

    return entry.id


def download_result_files(result_obj: result_db.Result, download_path: str) -> bool:
    """
    Writes out all the result files from a result database entry.

    :param result_obj: Database entry
    :param download_path: Where to write the files
    :return: True
    """

    result_dict = result_obj.to_mongo()

    result_path = download_path + '/results'

    if not os.path.exists(result_path):
        os.mkdir(result_path)
    else:
        shutil.rmtree(result_path)
        os.mkdir(result_path)

    delphin_parser.dict_to_g6a(dict(result_obj.geometry_file), result_path)

    for result_name in result_dict['results'].keys():
        delphin_parser.dict_to_d6o(result_dict, result_name, result_path)

    return True
