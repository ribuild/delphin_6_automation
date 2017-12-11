__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:


# RiBuild Modules:
from delphin_6_automation.nosql.db_templates.delphin_entry import delphin_db
from delphin_6_automation.nosql.db_templates.result_entry import result_db

# -------------------------------------------------------------------------------------------------------------------- #
# DATABASE INTERACTIONS


def gather_material_list(delphin_id: str)->list:
    """
    Gathers the material file names of Delphin file in the database
    :param delphin_id: database id
    :return: list of material file names
    """

    delphin_document = delphin_db.objects(id=delphin_id).first()

    material_list = []
    for material_dict in delphin_document['dp6_file']['DelphinProject']['Materials']['MaterialReference']:
        material_list.append(material_dict['#text'].split('/')[-1])

    return material_list


def download_raw_result(result_id, download_path):
    result_obj = result_db.objects(id=result_id).first()

    delphin_interact.write_log_files(result_obj, download_path)
    delphin_interact.write_result_files(result_obj, download_path)
    delphin_interact.write_geometry_files(result_obj, download_path)

    return True


def download_result(result_id, download_path):
    return None