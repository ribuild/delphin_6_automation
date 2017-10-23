__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"

#----------------------------------------------------------------------------------------------------------------------#
#Functions and Classes
import asyncio.subprocess as subprocess

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

def test()
    return None