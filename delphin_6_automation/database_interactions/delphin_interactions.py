__author__ = ""
__license__ = "MIT"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import shutil
import xmltodict
from collections import OrderedDict

# RiBuild Modules:
import delphin_6_automation.database_interactions.db_templates.result_raw_entry as result_db
import delphin_6_automation.database_interactions.db_templates.delphin_entry as delphin_db
import delphin_6_automation.database_interactions.db_templates.material_entry as material_db
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import weather_interactions
import delphin_6_automation.delphin_setup.delphin_permutations as permutations
from delphin_6_automation.file_parsing import delphin_parser


# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN FUNCTIONS AND CLASSES


def upload_delphin_to_database(delphin_file: str,  queue_priority: int) -> delphin_db.Delphin.id:
    """
    Uploads a Delphin file to a database.rst.

    :param delphin_file: Path to a Delphin 6 project file
    :param queue_priority: Queue priority for the simulation
    :return: Database entry id
    """

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file)
    entry_id = upload_delphin_dict_to_database(delphin_dict, queue_priority)

    return entry_id


def upload_delphin_dict_to_database(delphin_dict: dict, queue_priority: int) -> delphin_db.Delphin.id:
    """
    Uploads a Delphin file to a database.rst.

    :param delphin_dict: Dict with a Delphin 6 project
    :param queue_priority: Queue priority for the simulation
    :return: Database entry id
    """

    entry = delphin_db.Delphin()
    entry.queue_priority = queue_priority
    entry.dp6_file = delphin_dict
    entry.materials = material_interactions.find_material_ids(material_interactions.list_project_materials(entry))

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
    Converts a database.rst entry to Delphin 6 project file.

    :param document_id: Database entry id.
    :param path: Path to where the files should be written.
    :return: True
    """

    delphin_document = delphin_db.Delphin.objects(id=document_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    xmltodict.unparse(delphin_dict, output=open(path + '/' + document_id + '.d6p', 'w'), pretty=True)

    return True


def upload_results_to_database(path_: str, delete_files: bool =True) -> str:
    """
    Uploads the results from a Delphin simulation.

    :param path_: folder path containing the result files
    :param delete_files: if True the result folder will be deleted. Default is True
    :return: Result entry id
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
    delphin_entry.update(set__results_raw=entry)

    if delete_files:
        shutil.rmtree(path_)

    return entry.id


def download_result_files(result_obj: result_db.Result, download_path: str) -> bool:
    """
    Writes out all the result files from a result database.rst entry.

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


def permutate_entry_layer_width(original_id, layer_material, widths, queue_priority):

    delphin_document = delphin_db.Delphin.objects(id=original_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    modified_ids = []

    for width in widths:
        modified_dict = permutations.change_layer_width(delphin_dict, layer_material, width)
        modified_ids.append(str(upload_delphin_dict_to_database(modified_dict, queue_priority)))

    return modified_ids


def permutate_entry_layer_material(original_id, original_material, new_materials, queue_priority):

    delphin_document = delphin_db.Delphin.objects(id=original_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    modified_ids = []

    for new_material in new_materials:

        if isinstance(new_material, str):
            material = material_db.Material.objects(material_name=new_material).first()

            material_dict = OrderedDict((('@name', f'{material.material_name} [{material.material_id}]'),
                                         ('@color', str(material.material_data['IDENTIFICATION-COLOUR'])),
                                         ('@hatchCode', str(material.material_data['IDENTIFICATION-HATCHING'])),
                                         ('#text', '${Material Database}/' +
                                          str(material.material_data['INFO-FILE'].split('/')[-1]))
                                         )
                                        )
            modified_dict = permutations.change_layer_material(delphin_dict, original_material, material_dict)
            modified_ids.append(upload_delphin_dict_to_database(modified_dict, queue_priority))

        elif isinstance(new_material, int):
            material = material_db.Material.objects(material_id=new_material).first()

            material_dict = OrderedDict((('@name', f'{material.material_name} [{material.material_id}]'),
                                         ('@color', str(material.material_data['IDENTIFICATION-COLOUR'])),
                                         ('@hatchCode', str(material.material_data['IDENTIFICATION-HATCHING'])),
                                         ('#text', '${Material Database}/' +
                                          str(material.material_data['INFO-FILE'].split('/')[-1]))
                                         )
                                        )
            modified_dict = permutations.change_layer_material(delphin_dict, original_material, material_dict)
            modified_ids.append(upload_delphin_dict_to_database(modified_dict, queue_priority))

    return modified_ids


def permutate_entry_orientation(original_id, orientation_list, queue_priority):

    delphin_document = delphin_db.Delphin.objects(id=original_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    modified_ids = []

    for orientation in orientation_list:
        modified_dict = permutations.change_orientation(delphin_dict, orientation)
        modified_ids.append(str(upload_delphin_dict_to_database(modified_dict, queue_priority)))

    return modified_ids


def permutate_entry_weather(original_id, weather_stations, queue_priority):
    delphin_document = delphin_db.Delphin.objects(id=original_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    modified_ids = []

    for station in weather_stations['stations']:
        print(station)
        print(weather_stations['years'])
        for index in range(len(weather_stations['years'])):
            print(weather_stations['years'][index])
            modified_id = str(upload_delphin_dict_to_database(delphin_dict, queue_priority))
            weather_interactions.assign_weather_by_name_and_years(
                modified_id, station, weather_stations['years'][index])
            modified_ids.append(modified_id)

    return modified_ids


def permutate_entry_boundary_coefficient(original_id, boundary_condition, coefficient_name,
                                      coefficient_list, queue_priority):

    delphin_document = delphin_db.Delphin.objects(id=original_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    modified_ids = []

    for coefficient in coefficient_list:
        modified_dict = permutations.change_boundary_coefficient(delphin_dict, boundary_condition,
                                                                 coefficient_name, coefficient)
        modified_ids.append(str(upload_delphin_dict_to_database(modified_dict, queue_priority)))

    return modified_ids


def permutate_entry_simulation_length(original_id, length_list, unit_list, queue_priority):
    delphin_document = delphin_db.Delphin.objects(id=original_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    modified_ids = []

    for unit in unit_list:
        for length in length_list:
            modified_dict = permutations.change_simulation_length(delphin_dict, length, unit)
            modified_ids.append(str(upload_delphin_dict_to_database(modified_dict, queue_priority)))

    return modified_ids


def change_entry_simulation_length(sim_id, length, unit):

    delphin_document = delphin_db.Delphin.objects(id=sim_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    permutations.change_simulation_length(delphin_dict, length, unit)

    delphin_document.update(set__dp6_file=delphin_dict)

    return delphin_document.id
