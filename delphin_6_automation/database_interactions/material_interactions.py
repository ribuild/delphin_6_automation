__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
from collections import OrderedDict
import typing

# RiBuild Modules:
import delphin_6_automation.database_interactions.db_templates.delphin_entry as delphin_db
import delphin_6_automation.database_interactions.db_templates.material_entry as material_db
from delphin_6_automation.file_parsing import material_parser
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# DATABASE INTERACTIONS


def find_material_ids(project_materials: list) -> list:
    """
    Find ids of given material entries based on material name and material unique id.

    :param project_materials: List tuples with material file names and unique material ids
    :return: list with material entries
    """

    material_entries = []
    for material_pair in project_materials:
        material_entry = material_db.Material.objects(material_name=material_pair[0],
                                                      material_id=material_pair[1]).first()

        if material_entry:
            material_entries.append(material_entry)
        else:
            raise FileNotFoundError(f'Material: {material_pair[0]} with material ID: {material_pair[1]} '
                                    f'does not exist in database.\n'
                                    f'Please upload material files before uploading Delphin Projects\n')

    return material_entries


def list_project_materials(delphin_document: delphin_db.Delphin) -> list:
    """
    Returns a list with the materials in a project entry.

    :param delphin_document: Delphin entry
    :return: List tuples with material file names and unique material ids
    """

    materials = dict(delphin_document.dp6_file)['DelphinProject']['Materials']['MaterialReference']

    material_list = [(material['#text'].split('/')[-1].split('_')[0],
                      int(material['#text'].split('/')[-1].split('_')[-1][:-3]))
                     for material in materials]

    logger.debug(f'Found the following materials {material_list} related to the '
                 f'Delphin project with ID: {delphin_document.id}')

    return material_list


def upload_materials_from_folder(user_path_input: str) -> typing.List[str]:
    """Upload the Delphin material files located in a given folder"""

    material_dict_lst = []

    logger.debug(f'Uploads material files from {user_path_input}')

    if user_path_input.endswith(".m6"):
        upload_material_file(user_path_input)

    else:
        for root, dirs, files in os.walk(user_path_input):
            for file, _ in zip(files, root):
                if file.endswith(".m6"):
                    upload_material_file(file)

    return material_dict_lst


def upload_material_file(material_path: str) -> delphin_db.Delphin.id:
    """
    Uploads a Delphin file to a database.rst.

    :param material_path: Path to a Delphin 6 material project file
    :return: Database entry id
    """

    entry = material_db.Material()
    entry.material_data = material_parser.material_file_to_dict(material_path)
    entry.material_name = os.path.split(material_path)[-1].split('_')[0]
    entry.material_id = int(os.path.split(material_path)[-1].split('_')[1][:-3])
    entry.save()

    logger.debug(f'Material: {os.path.split(material_path)[-1].split("_")[0]} upload to database with ID: {entry.id}')

    return entry.id


def change_material_location(delphin_object: delphin_db.Delphin) -> str:
    """
    Changes the location of the material database location for the Delphin Project file.

    :param delphin_object: ID of entry
    :return: ID of entry
    """

    delphin_dict = dict(delphin_object.dp6_file)
    delphin_dict['DelphinProject']['DirectoryPlaceholders']['Placeholder']['#text'] = "${Project Directory}/materials"
    delphin_object.update(set__dp6_file=delphin_dict)

    return delphin_object.id


def download_materials(delphin_object: delphin_db.Delphin, path: str) -> None:
    """
    Downloads the materials of a Delphin Project

    :param delphin_object: Delphin entry ID
    :param path: Path to save to
    :return: None
    """

    materials_list = delphin_object.materials
    change_material_location(delphin_object)

    if not os.path.isdir(path):
        os.mkdir(path)

    for material in materials_list:
        material_parser.dict_to_m6(material, path)

    logger.debug(f'Materials for Delphin project with ID: {delphin_object.id} downloaded to {path}')


def get_material_info(material_id: int) -> dict:
    """Get the material info for a material in the database given a Delphin Material ID"""

    material = material_db.Material.objects(material_id=material_id).first()

    material_dict = OrderedDict((('@name', f'{material.material_name} [{material.material_id}]'),
                                 ('@color', str(material.material_data['IDENTIFICATION-COLOUR'])),
                                 ('@hatchCode', str(material.material_data['IDENTIFICATION-HATCHING'])),
                                 ('#text', '${Material Database}/' +
                                  os.path.split(material.material_data['INFO-FILE'])[-1])
                                 )
                                )
    return material_dict
