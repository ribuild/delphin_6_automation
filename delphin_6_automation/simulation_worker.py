__author__ = ''

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import platform
from pathlib import Path
import subprocess

# RiBuild Modules:
import delphin_6_automation.database_interactions.delphin_interactions as delphin_interact
import delphin_6_automation.database_interactions.mongo_setup as mongo_setup
import delphin_6_automation.database_interactions.db_templates.result_raw_entry as result_db

# -------------------------------------------------------------------------------------------------------------------- #
# RIBUILD SIMULATION WORKER, DELPHIN SOLVER,


def worker(id_, database):
    """
    Simulation worker. Supposed to be used with main simulation loop.
    :param id_: Database entry ID from simulation queue
    :param database: Database to download from.
    :return: True on success otherwise False
    """

    # Setup connection
    mongo_setup.global_init(database)

    # Find paths
    system = platform.system()
    if system == 'Windows':
        delphin_path = r'C:/ribuild'
        exe_path = r'C:/Program Files/IBK/Delphin 6.0/DelphinSolver.exe'
    elif system == 'Linux':
        home = str(Path.home())
        delphin_path = home + '/ribuild'
        exe_path = ''
    else:
        raise NameError('OS not supported')

    if not os.path.isdir(delphin_path):
        os.mkdir(delphin_path)

    # Download, solve, upload
    delphin_interact.download_delphin_entry(id_, delphin_path)
    solve_delphin(delphin_path + id_ + '.d6p', delphin_exe=exe_path, verbosity_level=0)
    id_result = delphin_interact.upload_results_to_database(delphin_path + '/' + id_)

    # Check if uploaded:
    test_doc = result_db.Result.objects(id=id_result).first()

    # TODO - Flag for simulation ended

    if test_doc:
        return True
    else:
        raise FileNotFoundError('Could not find result entry')


def solve_delphin(file, delphin_exe=r'C:/Program Files/IBK/Delphin 6.0/DelphinSolver.exe', verbosity_level=1):
    """Solves a delphin file"""

    verbosity = "verbosity-level=" + str(verbosity_level)
    command_string = '"' + str(delphin_exe) + '" --close-on-exit --' + verbosity + ' "' + file + '"'

    return subprocess.run(command_string, shell=True)


def find_next_in_queue():
    # Find next simulation
    # Flag for simulation started
    # return id to worker
    pass


def github_updates():
    # Check for github update to code
    pass


def simulation_worker():
    try:
        while True:
            id = find_next_in_queue()
            worker(id, database=ribuild)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    simulation_worker()
