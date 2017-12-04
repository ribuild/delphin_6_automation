__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
#import asyncio.subprocess as subprocess
import subprocess

# RiBuild Modules:

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN FUNCTIONS AND CLASSES


def solve_delphin(file, delphin_exe=r'C:/Program Files/IBK/Delphin 6.0/DelphinSolver.exe', verbosity_level=1):
    """Solves a delphin file"""

    verbosity = "verbosity-level=" + str(verbosity_level)
    command_string = '"' + str(delphin_exe) + '" --close-on-exit --' + verbosity + ' "' + file + '"'
    #print(command_string)
    retcode = subprocess.run(command_string, shell=True)

    return retcode