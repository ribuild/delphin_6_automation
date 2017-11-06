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

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN FUNCTIONS AND CLASSES


def json_to_dp6():
    """Converts a json file to delphin6 project file"""


def dp6_to_json(dp6_path):
    """Converts a delphin6 project file to a json file"""

    delphin_dict = dp6_to_dict(dp6_path)

    return dict_to_json(delphin_dict)

def dp6_to_dict(path):
    """Converts a delphin6 project file to a python dict"""

    xml_string = ET.tostring(ET.parse(path).getroot())
    xml_dict = xmltodict.parse(xml_string)

    return dict(xml_dict['ns0:DelphinProject'])


def dict_to_json(delphin_dict):
    """Converts a dict of a delphin6 project file to a json file"""

    json_file = json.dumps(delphin_dict)

    return json_file


def do6_to_json():
    """Converts a delphin6 output to a json file"""


def json_to_database(json, database):
    """Uploads a json file to a database"""

