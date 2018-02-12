__author__ = "Christian Kongsgaard"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import platform
from pathlib import Path

# RiBuild Modules:
import delphin_6_automation.database_interactions.delphin_interactions as delphin_interact
import delphin_6_automation.simulation_package.delphin_solver as solver
import delphin_6_automation.nosql.mongo_setup as mongo_setup
import delphin_6_automation.nosql.db_templates.result_raw_entry as result_db

# -------------------------------------------------------------------------------------------------------------------- #
# RIBUILD SIMULATION WORKER

# TODO - Test worker.


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
    delphin_interact.download_from_database(id_, delphin_path)
    solver.solve_delphin(delphin_path + id_ + '.d6p', delphin_exe=exe_path, verbosity_level=0)
    id_result = delphin_interact.results_to_mongo_db(delphin_path + '/' + id_)

    # Check if uploaded:
    test_doc = result_db.Result.objects(id=id_result).first()

    if test_doc:
        return True
    else:
        raise FileNotFoundError('Could not find result entry')




