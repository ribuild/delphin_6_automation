__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import asyncio.subprocess as subprocess
from datetime import datetime
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


class Delphin6File:

    def __init__(self):
        self.xmlns_ns = None
        self.xmlns_xsi = None
        self.file_version = None
        self.schema_location = None
        self.project_info = None
        self.directory_placeholders = None
        self.init = None
        self.materials = None
        self.discretization = None
        self.conditions = None
        self.outputs = None
        self.assignments = None

    def create_attributes(self):
        return None

    def create_project_info(self, created=None):
        last_edited = datetime.strftime(datetime.now(), '%c')

        if not created:
            created = last_edited

        self.project_info = {'created': created, 'lastEdited': last_edited}

    def create_directory_placeholders(self, climate_database=None, material_database=None):
        if not climate_database:
            climate_database = r'C:/Program Files/IBK/Delphin 6.0/resources/DB_climate'

        if not material_database:
            material_database = r'C:/Program Files/IBK/Delphin 6.0/resources/DB_materials'

        directory_placeholders_dict = {'climate': {'name': 'Climate Database',
                                                   'path': climate_database},
                                       'material': {'name': 'Material Database',
                                                    'path': material_database}
                                       }

        self.directory_placeholders = directory_placeholders_dict
        return None

    def create_init(self, duration, longitude, latitude, climate_data_path, balance_equation_module='BEHeatMoisture'):
        self.init = {'SimulationParameter': {'BalanceEquationModule': balance_equation_module, 'Interval': {'IBK:Parameter': ''}}}

    def create_materials(self):
        return None

    def create_discretization(self):
        return None

    def create_conditions(self):
        return None

    def create_outputs(self):
        return None

    def create_assignments(self):
        return None

    def create_dicts(self):
        self.create_project_info()
        self.create_directory_placeholders()
        self.create_init()
        self.create_materials()
        self.create_discretization()
        self.create_conditions()
        self.create_outputs()
        self.create_assignments()

    def create_xml(self):
        self.create_dicts()

        delphin_root = ET.Element('ns0:DelphinProject')

        info_subtree = ET.SubElement(delphin_root, 'ProjectInfo')

        dir_place_subtree = ET.SubElement(delphin_root, 'DirectoryPlaceholders')

        init_subtree = ET.SubElement(delphin_root, 'Init')

        material_subtree = ET.SubElement(delphin_root, 'Materials')

        discretization_subtree = ET.SubElement(delphin_root, 'Discretization')

        conditions_subtree = ET.SubElement(delphin_root, 'Conditions')

        outputs_subtree = ET.SubElement(delphin_root, 'Outputs')

        assignments_subtree = ET.SubElement(delphin_root, 'Assignments')

        delphin_tree = ET.ElementTree(delphin_root)

        return delphin_tree

    def write_xml(self, path):
        xml_file = self.create_xml()

        xml_file.write(path, xml_declaration=True)
