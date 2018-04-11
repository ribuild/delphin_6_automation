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
from delphin_6_automation.logging import ribuild_logger

# Logger
logger = ribuild_logger.ribuild_logger(__name__)

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


def check_delphin_file(delphin_dict: dict):
    """
    Checks if a Delphin project file is valid for simulation.

    :return:
    :rtype:
    """

    error = False

    # 1D or 2D?
    if len(delphin_dict['DelphinProject']['Discretization']) > 2:
        logger.warning('Delphin Project File is 3 dimensional. Permutations are not guaranteed to work!')
    elif len(delphin_dict['DelphinProject']['Discretization']) > 1:
        logger.warning('Delphin Project File is 2 dimensional. Permutations are not guaranteed to work!')
    else:
        logger.info('Delphin Project File is 1 dimensional.')

    # Is materials correct?
    material_error = False

    for material in delphin_dict['DelphinProject']['Materials']['MaterialReference']:
        material_id = material['@name'][-5:]
        if not material_id.startswith('[') and material_id.endswith(']'):
            logger.error(f'Material name should end with: [XXX], where XXX is the Delphin Material ID. '
                         f'Material ended with: {material_id}')
            material_error = True

        try:
            material_int = int(material_id[1:-1])
        except ValueError:
            logger.error(f'Material name should end with: [XXX], where XXX is the Delphin Material ID. '
                         f'Delphin Material ID {material_id} was not an integer, but a: {type(material_id[1:-1])}')
            material_error = True

    if not material_error:
        logger.info('Material check passed')
    else:
        error = True
        logger.error('Material check did not pass')

    # Is interface correct?
    interface_error = False

    interfaces = delphin_dict['DelphinProject']['Conditions']['Interfaces']['Interface']

    if interfaces[0]['@name'].lower() != 'indoor surface' and str(interfaces[0]['@name'].lower()) != 'interior surface':
        logger.warning(f'Interior surface should be named: indoor surface or interior surface. '
                       f'Named given was: {interfaces[0]["@name"].lower()}')

    if interfaces[0]['@type'] != 'Detailed':
        logger.error(f'Interior interface should be: Detailed. Interface type given was: {interfaces[0]["@type"]}')
        interface_error = True

    interior_boundaries = ['IndoorHeatConduction', 'IndoorVaporDiffusion']
    for bc_ref in interfaces[0]['BCReference']:
        try:
            index = interior_boundaries.index(bc_ref.split(':')[-1])
            interior_boundaries.pop(index)
        except ValueError:
            logger.error(f'Boundary condition not part of: {interior_boundaries}. '
                         f'Boundary condition given was: {bc_ref.split(":")[-1]}')
            interface_error = True

    if str(interfaces[1]['@name'].lower()) != 'outdoor surface' and str(interfaces[0]['@name'].lower()) != 'exterior surface':
        logger.warning(f'Exterior surface should be named: outdoor surface or exterior surface. '
                       f'Named given was: {interfaces[1]["@name"].lower()}')

    if interfaces[1]['@type'] != 'Detailed':
        logger.error(f'Exterior interface should be: Detailed. Interface type given was: {interfaces[1]["@type"]}')
        interface_error = True

    exterior_boundaries = ['OutdoorHeatConduction', 'OutdoorVaporDiffusion', 'OutdoorShortWaveRadiation',
                           'OutdoorLongWaveRadiation', 'OutdoorWindDrivenRain']
    for bc_ref in interfaces[1]['BCReference']:
        try:
            index = exterior_boundaries.index(bc_ref.split(':')[-1])
            exterior_boundaries.pop(index)
        except ValueError:
            logger.error(f'Boundary condition not part of: {exterior_boundaries}. '
                         f'Boundary condition given was: {bc_ref.split(":")[-1]}')
            interface_error = True

    if not interface_error:
        logger.info('Interface check passed')
    else:
        error = True
        logger.error('Interface check did not pass')

    # Is climate conditions correct?
    climate_error = False

    for climate_condition in delphin_dict['DelphinProject']['Conditions']['ClimateConditions']['ClimateCondition']:
        if climate_condition['@kind'] != 'TabulatedData':
            logger.error(f'Climate condition kind should be TabulatedData. '
                         f'Given kind was: {climate_condition["@kind"]}')
            climate_error = True

        if climate_condition['IBK:Flag'][1]['#text'] != 'false':
            logger.error(f'Climate condition should not use ExtendData. '
                         f'Given value was: {climate_condition[2]["#text"]}')
            climate_error = True

    if not climate_error:
        logger.info('Climate condition check passed')
    else:
        error = True
        logger.error('Climate condition check did not pass')

    # Is boundary conditions correct?
    boundary_error = False

    for boundary_condition in delphin_dict['DelphinProject']['Conditions']['BoundaryConditions']['BoundaryCondition']:
        if boundary_condition['@type'] == 'HeatConduction':
            if boundary_condition['@kind'] != 'Exchange':
                logger.error(f'Heat conduction should be of the boundary condition kind: Exchange. '
                             f'Given kind was: {boundary_condition["@kind"]}')
                boundary_error = True

        elif boundary_condition['@type'] == 'VaporDiffusion':
            if boundary_condition['@kind'] != 'Exchange':
                logger.error(f'Vapor diffusion should be of the boundary condition kind: Exchange. '
                             f'Given kind was: {boundary_condition["@kind"]}')
                boundary_error = True

        elif boundary_condition['@type'] == 'WindDrivenRain':
            if boundary_condition['@kind'] != 'ImposedFlux':
                logger.error(f'Wind driven rain should be of the boundary condition kind: ImposedFlux. '
                             f'Given kind was: {boundary_condition["@kind"]}')
                boundary_error = True

        elif boundary_condition['@type'] == 'ShortWaveRadiation':
            if boundary_condition['@kind'] != 'StandardRadiationModel':
                logger.error(f'Short wave radiation should be of the boundary condition kind: StandardRadiationModel. '
                             f'Given kind was: {boundary_condition["@kind"]}')
                boundary_error = True

        elif boundary_condition['@type'] == 'LongWaveRadiation':
            if boundary_condition['@kind'] != 'LongWaveComponents':
                logger.error(f'Long wave radiation should be of the boundary condition kind: LongWaveComponents. '
                             f'Given kind was: {boundary_condition["@kind"]}')
                boundary_error = True

    if not boundary_error:
        logger.info('Boundary condition check passed')
    else:
        error = True
        logger.error('Boundary condition check did not pass')

    # Is outputs correct?
    # TODO - To be determined

    return error
