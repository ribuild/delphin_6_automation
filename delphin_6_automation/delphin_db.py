__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import xml.etree.ElementTree as ET
import xmltodict
import json


# RiBuild Modules:
import delphin_6_automation.nosql.db_templates.delphin_entry as de
import delphin_6_automation.nosql.database_collections as collections

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN FUNCTIONS AND CLASSES


def mongo_document_to_dp6():
    """Converts a json file to Delphin 6 project file"""


def dp6_to_json(dp6_path):
    """Converts a Delphin 6 project file to a json file"""

    delphin_dict = dp6_to_dict(dp6_path)

    return dict_to_json(delphin_dict)


def dp6_to_dict(path):
    """Converts a Delphin 6 project file to a python dict"""

    xml_string = ET.tostring(ET.parse(path).getroot())
    xml_dict = xmltodict.parse(xml_string)

    return dict(xml_dict['ns0:DelphinProject'])


def dict_to_json(delphin_dict):
    """Converts a dict of a Delphin 6 project file to a json file"""

    json_file = json.dumps(delphin_dict)

    return json_file


def do6_to_mongo_db():
    """Converts a Delphin 6 output to a json file"""


def upload_to_database(delphin_file,  queue_priority):
    """Uploads a Delphin file to a database"""

    entry = de.Delphin()
    entry.materials = collections.material_db
    entry.weather = collections.weather_db
    entry.queue_priority = queue_priority

    delphin_dict = dp6_to_dict(delphin_file)
    entry.dp6_file = delphin_dict

    if len(delphin_dict['ns0:Discretization']) > 2:
        entry.dimensions = 3
    elif len(delphin_dict['ns0:Discretization']) > 1:
        entry.dimensions = 2
    else:
        entry.dimensions = 1

    entry.save()


