__author__ = ''

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import platform
from pathlib import Path
import subprocess
from datetime import datetime

# RiBuild Modules:
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import general_interactions
import delphin_6_automation.database_interactions.mongo_setup as mongo_setup
import delphin_6_automation.database_interactions.db_templates.result_raw_entry as result_db
from delphin_6_automation.database_interactions.auth import dtu_byg


# -------------------------------------------------------------------------------------------------------------------- #
# RIBUILD SIMULATION WORKER, DELPHIN SOLVER,


def worker(id_):
    """
    Simulation worker. Supposed to be used with main simulation loop.
    :param id_: Database entry ID from simulation queue
    :return: True on success otherwise False
    """

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
    time_0 = datetime.now()
    general_interactions.download_full_project_from_database(str(id_), delphin_path)
    solve_delphin(delphin_path + '/' + id_ + '.d6p', delphin_exe=exe_path, verbosity_level=0)
    id_result = delphin_interactions.upload_results_to_database(delphin_path + '/' + id_)
    delta_time = datetime.now() - time_0

    # Check if uploaded:
    test_doc = result_db.Result.objects(id=id_result).first()

    simulation_interactions.set_simulated(id_)

    if test_doc:
        simulation_interactions.clean_simulation_folder(delphin_path)
        print(f'Finished solving {id_}. Simulation duration: {delta_time}\n')
        return True
    else:
        raise FileNotFoundError('Could not find result entry')


def solve_delphin(file, delphin_exe=r'C:/Program Files/IBK/Delphin 6.0/DelphinSolver.exe', verbosity_level=1):
    """Solves a delphin file"""

    print(f'Solves {file}')

    verbosity = "verbosity-level=" + str(verbosity_level)
    command_string = '"' + str(delphin_exe) + '" --close-on-exit --' + verbosity + ' "' + file + '"'

    return subprocess.run(command_string, shell=True)


def github_updates():
    # Check for github update to code
    pass


def simulation_worker():
    try:
        while True:
            id_ = simulation_interactions.find_next_sim_in_queue()
            if id_:
                worker(id_)
            else:
                pass
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    # Setup connection
    mongo_setup.global_init(dtu_byg)

    simulation_worker()
