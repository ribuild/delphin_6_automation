__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"

#----------------------------------------------------------------------------------------------------------------------#
#Functions and Classes
import asyncio.subprocess as subprocess
from datetime import datetime
import xml.etree.ElementTree as ET

def solve_delphin(file, delphin_exe = r'C:/Program Files/IBK/Delphin 6.0/DelphinSolverUI.exe', verbosity_level=1):
    """Solves a delphin file"""

    verbosity = "verbosity-level = "+str(verbosity_level)
    retcode = subprocess.Process([delphin_exe, verbosity, file])
    return retcode


def json_to_dp6():
    """Converts a json file to delphin6 project file"""

def dp6_to_json():
    """Converts a delphin6 project file to a json file"""

def do6_to_json():
    """Converts a delphin6 output to a json file"""


class Delphin6File():

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

    def attributes(self):

        return None

    def project_info(self, created=None):
        lastEdited = datetime.strftime('%c', datetime.now())

        if not created:
            created = lastEdited

        self.project_info = {'created': created, 'lastEdited': lastEdited}

    def directory_placeholders(self):
        return None

    def init(self, duration, longitude, latitude, climate_data_path, balance_equation_module='BEHeatMoisture'):
        self.init = {'SimulationParameter': {'BalanceEquationModule': balance_equation_module, 'Interval': {'IBK:Parameter': }}}

    def materials(self):
        return None

    def discretization(self):
        return None

    def conditions(self):
        return None

    def outputs(self):
        return None

    def assignments(self):
        return None
