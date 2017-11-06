__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import asyncio.subprocess as subprocess
import xml.etree.ElementTree as ET
import xmltodict

# RiBuild Modules:

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN FUNCTIONS AND CLASSES


def solve_delphin(file, delphin_exe=r'C:/Program Files/IBK/Delphin 6.0/DelphinSolverUI.exe', verbosity_level=1):
    """Solves a delphin file"""

    verbosity = "verbosity-level = "+str(verbosity_level)
    retcode = subprocess.Process([delphin_exe, verbosity, file])
    return retcode


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

    json = None

    return json


def do6_to_json():
    """Converts a delphin6 output to a json file"""


def test():
    return None