__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:


# RiBuild Modules:
from delphin_6_automation.nosql.db_templates.delphin_entry import Delphin

# -------------------------------------------------------------------------------------------------------------------- #
# DATABASE INTERACTIONS


def gather_material_list(delphin_id: str)->list:
    """
    Gathers the material file names of Delphin file in the database
    :param delphin_id: database id
    :return: list of material file names
    """

    delphin_document = Delphin.objects(id=delphin_id).first()

    material_list = []
    for material_dict in delphin_document['dp6_file']['DelphinProject']['Materials']['MaterialReference']:
        material_list.append(material_dict['#text'].split('/')[-1])

    return material_list
