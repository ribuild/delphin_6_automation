__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import asyncio.subprocess as subprocess

# RiBuild Modules:

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN FUNCTIONS AND CLASSES


def solve_delphin(file, delphin_exe=r'C:/Program Files/IBK/Delphin 6.0/DelphinSolverUI.exe', verbosity_level=1):
    """Solves a delphin file"""

    verbosity = "verbosity-level = "+str(verbosity_level)
    retcode = subprocess.Process([delphin_exe, verbosity, file])
    return retcode