__author__ = "Christian Kongsgaard"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
from collections import OrderedDict

# RiBuild Modules:
import delphin_6_automation.database_interactions.db_templates.delphin_entry as delphin_db
import delphin_6_automation.database_interactions.db_templates.material_entry as material_db
from delphin_6_automation.file_parsing import material_parser


# -------------------------------------------------------------------------------------------------------------------- #
# DATABASE INTERACTIONS


def find_material_ids(project_materials: list) -> list:
    """
    Find ids of given material entries based on material name and material unique id.

    :param project_materials: List tuples with material file names and unique material ids
    :type project_materials: list
    :return: list with material entries
    :rtype: list
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

    return material_list


def convert_and_upload_file(user_path_input):

    material_dict_lst = []

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

    return entry.id


def change_material_location(delphin_object: delphin_db.Delphin) -> str:
    """
    Changes the location of the material database location for the Delphin Project file.

    :param delphin_object: ID of entry
    :type delphin_object: delphin_db.Delphin
    :return: ID of entry
    :rtype: str
    """

    delphin_dict = dict(delphin_object.dp6_file)
    delphin_dict['DelphinProject']['DirectoryPlaceholders']['Placeholder']['#text'] = "${Project Directory}/materials"
    delphin_object.update(set__dp6_file=delphin_dict)

    return delphin_object.id


def download_materials(delphin_object: delphin_db.Delphin, path: str) -> bool:
    """
    Downloads the materials of a Delphin Project

    :param delphin_object: Delphin entry ID
    :type delphin_object: delphin_db.Delphin
    :param path: Path to save to
    :type path: str
    :return: True
    :rtype: bool
    """

    materials_list = delphin_object.materials
    change_material_location(delphin_object)

    if not os.path.isdir(path):
        os.mkdir(path)

    for material in materials_list:
        material_parser.dict_to_m6(material, path)

    return True


def get_material_info(material_id: int) -> dict:
    material = material_db.Material.objects(material_id=material_id).first()

    material_dict = OrderedDict((('@name', f'{material.material_name} [{material.material_id}]'),
                                 ('@color', str(material.material_data['IDENTIFICATION-COLOUR'])),
                                 ('@hatchCode', str(material.material_data['IDENTIFICATION-HATCHING'])),
                                 ('#text', '${Material Database}/' +
                                  str(material.material_data['INFO-FILE'].split('/')[-1]))
                                 )
                                )
    return material_dict
