__author__ = 'Christian Kongsgaard, Thomas Perkov'
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import platform
from pathlib import Path
import subprocess
from datetime import datetime

# RiBuild Modules:
from delphin_6_automation.logging.ribuild_logger import ribuild_logger, notifiers_logger
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import general_interactions
import delphin_6_automation.database_interactions.mongo_setup as mongo_setup
import delphin_6_automation.database_interactions.db_templates.result_raw_entry as result_db
from delphin_6_automation.database_interactions.auth import dtu_byg


# -------------------------------------------------------------------------------------------------------------------- #
# RIBUILD SIMULATION WORKER, DELPHIN SOLVER,

logger = ribuild_logger(__name__)


def local_worker(id_):
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
        logger.error('OS not supported')
        raise NameError('OS not supported')

    if not os.path.isdir(delphin_path):
        os.mkdir(delphin_path)

    # Download, solve, upload
    time_0 = datetime.now()

    print(f'\nDownloads project with ID: {id_}')
    logger.info(f'Downloads project with ID: {id_}')

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
        logger.info(f'Finished solving {id_}. Simulation duration: {delta_time}')
        return True
    else:
        logger.error('Could not find result entry')
        raise FileNotFoundError('Could not find result entry')


def solve_delphin(file, delphin_exe=r'C:/Program Files/IBK/Delphin 6.0/DelphinSolver.exe', verbosity_level=1):
    """Solves a delphin file"""

    print(f'Solves {file}')
    logger.info(f'Solves {file}')

    verbosity = "verbosity-level=" + str(verbosity_level)
    command_string = '"' + str(delphin_exe) + '" --close-on-exit --' + verbosity + ' "' + file + '"'
    process = subprocess.run(command_string, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

    output = process.stdout.decode()
    if output:
        logger.info(output)

    return True


def github_updates():
    if general_interactions.get_github_version() != general_interactions.get_git_revision_hash():
        print('New version of Delphin 6 Automation is available on Github!!')
        return False
    else:
        return True


def get_average_computation_time(sim_id):
    # TODO - Get the average time for this type of construction (2D or 1D)
    pass


def create_submit_file(sim_id, simulation_folder):
    delphin_path = '~/Delphin-6.0/bin/DelphinSolver'
    computation_time = get_average_computation_time(sim_id)
    cpus = 24
    ram_per_cpu = '10MB'
    submit_file = f'submit_{sim_id}.sh'

    file = open(f"{simulation_folder}/{submit_file}", 'w')
    file.write("#!/bin/bash\n")
    file.write("#BSUB -J DelphinJob\n")
    file.write("#BSUB -o DelphinJob_%J.out\n")
    file.write("#BSUB -e DelphinJob_%J.err\n")
    file.write("#BSUB -q hpc\n")
    file.write(f"#BSUB -W {computation_time}\n")
    file.write(f'#BSUB -R "rusage[mem={ram_per_cpu}] span[hosts=1]"\n')
    file.write(f"#BSUB -n {cpus}\n")
    file.write(f"#BSUB -N\n")
    file.write('')
    file.write(f"export OMP_NUM_THREADS=$LSB_DJOB_NUMPROC\n")
    file.write('')
    file.write(f"{delphin_path} {sim_id}.d6p")

    file.close()

    return submit_file, computation_time


def submit_job(submit_file):
    # TODO - SSH to HPC, call bsub < submit_file, get job_id from HPC
    terminal_call = f"bsub < {submit_file}\n"
    return job_id


def wait_until_finished(sim_id, job_id, estimated_run_time):
    # TODO - Look for summary file. If it is created, continue. If it is not created and the estimated time runs out.
    # Then submit a new job continuing the simulation from where it ended.

    pass


def hpc_worker(id_):

    simulation_folder = 'H:/ribuild'

    if not os.path.isdir(simulation_folder):
        os.mkdir(simulation_folder)

    # Download, solve, upload
    time_0 = datetime.now()

    print(f'\nDownloads project with ID: {id_}')
    logger.info(f'Downloads project with ID: {id_}')

    general_interactions.download_full_project_from_database(str(id_), simulation_folder)
    submit_file, estimated_time = create_submit_file(str(id_), simulation_folder)
    job_id = submit_job(submit_file)
    wait_until_finished(str(id_), job_id, estimated_time)

    delta_time = datetime.now() - time_0

    id_result = delphin_interactions.upload_results_to_database(simulation_folder + '/' + id_)

    simulation_interactions.set_simulated(id_)
    simulation_interactions.set_simulation_time(id_, delta_time)


def simulation_worker(sim_location):
    try:
        while True:
            #github_updates()
            id_ = simulation_interactions.find_next_sim_in_queue()
            if id_:
                if sim_location == 'local':
                    local_worker(id_)
                elif sim_location == 'hpc':
                    hpc_worker(id_)
            else:
                pass
    except KeyboardInterrupt:
        return


def main():
    print_header()
    menu()


def print_header():
    print('---------------------------------------------------')
    print('|                                                  |')
    print('|           RiBuild EU Research Project            |')
    print('|           for Hygrothermal Simulations           |')
    print('|                                                  |')
    print('|                 WORK IN PROGRESS                 |')
    print('|              Simulation Environment              |')
    print('|                                                  |')
    print('---------------------------------------------------')


def menu():
    while True:
        print('')
        print('------------------- SIMULATION MENU ---------------------')
        print('')
        print("Available actions:")
        print("[a] Simulate locally")
        print("[b] Simulate on DTU HPC")

        choice = input("> ").strip().lower()

        if choice == 'a':
            simulation_worker('local')

        elif choice == 'b':
            simulation_worker('hpc')
