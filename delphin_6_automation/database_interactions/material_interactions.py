__author__ = "Christian Kongsgaard"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os

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
        material_entries.append(material_db.Material.objects(material_name=material_pair[0],
                                                             material_id=material_pair[1]).first())
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


def download_materials(delphin_id: str, path: str) -> bool:
    """
    Downloads the materials of a Delphin Project

    :param delphin_id: Delphin entry ID
    :type delphin_id: str
    :param path: Path to save to
    :type path: str
    :return: True
    :rtype: bool
    """

    materials_list = delphin_db.Delphin.objects(id=delphin_id).first().materials

    for material in materials_list:
        material_parser.dict_to_m6(material, path)

    return True
