__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:


# RiBuild Modules:
from delphin_6_automation.nosql.db_templates import delphin_entry as delphin_db

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
