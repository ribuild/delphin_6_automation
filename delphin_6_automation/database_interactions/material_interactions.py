__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:


# RiBuild Modules:
from delphin_6_automation.nosql.db_templates import delphin_entry as delphin_db
from delphin_6_automation.nosql.db_templates import material_entry as material_db
from delphin_6_automation.file_parsing.delphin_material_file import material_file_to_dict

# -------------------------------------------------------------------------------------------------------------------- #
# DATABASE INTERACTIONS


def dict_to_m6(material: dict, path: str) -> bool:
    """
    Takes an material dict and converts it into a .m6 file.

    :param material: material dict
    :param path: Path to where .m6 should be placed.
    :return: True
    """

    # TODO - Create function
    return True


def list_project_materials(sim_id: str) -> list:
    """
    Returns a list with the materials in a project entry.

    :param sim_id: Delphin entry ID
    :return: List with material file names
    """

    materials = delphin_db.Delphin.objects(id=sim_id).first().dp6_file.DelphinProject.Materials

    material_list = [material.split('/')[-1]
                     for material in materials]

    return material_list


def assign_materials_to_project():
    """
    Assign materials to a Delphin entry.

    :return:
    """

    # TODO - Create function
    return None



def convert_and_upload_file(user_path_input):

    material_dict_lst = []

    if user_path_input.endswith(".m6"):
        upload_material_file(user_path_input)

    else:
        for root, dirs, files in os.walk(user_path_input):
            for file, root in zip(files, root):
                if file.endswith(".m6"):
                    upload_material_file(file)

    return material_dict_lst


def upload_material_file(user_input: str) -> delphin_db.Delphin.id:
    """
    Uploads a Delphin file to a database.

    :param delphin_file: Path to a Delphin 6 project file
    :param queue_priority: Queue priority for the simulation
    :return: Database entry id
    """


    entry = material_db.Material()
    entry.material_data = material_file_to_dict(user_input)

    entry.save()

    return entry.id