__author__ = 'Christian Kongsgaard, Thomas Perkov'
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import platform
from pathlib import Path
import subprocess
import datetime
import numpy as np
import time
import threading
import paramiko
import typing
import shutil

# RiBuild Modules:
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import general_interactions
import delphin_6_automation.database_interactions.db_templates.result_raw_entry as result_db
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
try:
    from delphin_6_automation.database_interactions.auth import hpc
except ModuleNotFoundError:
    pass

# Logger
logger = ribuild_logger(__name__)

# -------------------------------------------------------------------------------------------------------------------- #
# RIBUILD SIMULATION WORKER, DELPHIN SOLVER,


def local_worker(id_: str) -> typing.Optional[bool]:
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
    time_0 = datetime.datetime.now()

    logger.info(f'Downloads project with ID: {id_}')

    general_interactions.download_full_project_from_database(str(id_), delphin_path)
    solve_delphin(delphin_path + '/' + id_ + '.d6p', delphin_exe=exe_path, verbosity_level=0)
    id_result = delphin_interactions.upload_results_to_database(delphin_path + '/' + id_)

    delta_time = datetime.datetime.now() - time_0

    # Check if uploaded:
    test_doc = result_db.Result.objects(id=id_result).first()

    simulation_interactions.set_simulated(id_)
    simulation_interactions.set_simulation_time(id_, delta_time)

    if test_doc:
        simulation_interactions.clean_simulation_folder(delphin_path)
        logger.info(f'Finished solving {id_}. Simulation duration: {delta_time}')
        return True
    else:
        logger.error('Could not find result entry')
        raise FileNotFoundError('Could not find result entry')


def solve_delphin(file: str, delphin_exe=r'C:/Program Files/IBK/Delphin 6.0/DelphinSolver.exe', verbosity_level=1) \
        -> bool:
    """Solves a delphin file locally"""

    logger.info(f'Solves {file}')

    verbosity = "verbosity-level=" + str(verbosity_level)
    command_string = '"' + str(delphin_exe) + '" --close-on-exit --' + verbosity + ' "' + file + '"'
    process = subprocess.run(command_string, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

    output = process.stdout.decode()
    if output:
        logger.info(output)

    return True


def github_updates():
    """
    if general_interactions.get_github_version() != general_interactions.get_git_revision_hash():
        logger.info('New version of Delphin 6 Automation is available on Github!!')
        return False
    else:
        return True
    """
    raise NotImplementedError


def get_average_computation_time(sim_id: str) -> int:
    """
    Get the average time for this type of construction (2D or 1D)

    :param sim_id: Delphin entry id from database
    :return: Average simulation time in minutes
    """

    sim_obj = delphin_entry.Delphin.objects(id=sim_id).first()
    dimension = sim_obj.dimensions

    sim_time = [simulation_entry.simulation_time
                for simulation_entry in delphin_entry.Delphin.objects(dimensions=dimension,
                                                                      simulation_time__exists=True)]

    if sim_time:
        avg_time = int(np.ceil(np.mean(sim_time)/60))
        logger.debug(f'Average simulation time for Delphin projects in {dimension}D: {avg_time}min')
        return avg_time

    elif dimension == 2:
        logger.debug(f'No previous simulations found. Setting time to 180min for a 2D simulation')
        return 240

    else:
        logger.debug(f'No previous simulations found. Setting time to 60min for a 1D simulation')
        return 120


def create_submit_file(sim_id: str, simulation_folder: str, computation_time: int, restart=False) -> str:
    """Create a submit file for the DTU HPC queue system."""

    delphin_path = '~/Delphin-6.0/bin/DelphinSolver'
    cpus = 2
    ram_per_cpu = '14MB'
    submit_file = f'submit_{sim_id}.sh'

    file = open(f"{simulation_folder}/{submit_file}", 'w', newline='\n')
    file.write("#!/bin/bash\n")
    file.write("#BSUB -J DelphinJob\n")
    file.write("#BSUB -o DelphinJob_%J.out\n")
    file.write("#BSUB -e DelphinJob_%J.err\n")
    file.write("#BSUB -q hpc\n")
    file.write(f"#BSUB -W {computation_time}\n")
    file.write(f'#BSUB -R "rusage[mem={ram_per_cpu}] span[hosts=1]"\n')
    file.write(f"#BSUB -n {cpus}\n")
    file.write(f"#BSUB -N\n")
    file.write('\n')
    file.write(f"export OMP_NUM_THREADS=$LSB_DJOB_NUMPROC\n")
    file.write('\n')

    if not restart:
        file.write(f"{delphin_path} {sim_id}.d6p\n")
    else:
        file.write(f"{delphin_path} --restart {sim_id}.d6p\n")

    file.write('\n')
    file.close()

    logger.debug(f'Create a submit file for {sim_id} with restart = {restart}')

    return submit_file


def submit_job(submit_file: str, sim_id: str) -> None:
    """Submits a job (submit file) to the DTU HPC queue."""

    terminal_call = f"cd ~/ribuild/{sim_id}\n", f"bsub < {submit_file}\n"

    key = paramiko.RSAKey.from_private_key_file(hpc['key_path'], password=hpc['key_pw'])
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    logger.debug(f'Connecting to HPC to upload simulation with ID: {sim_id}')
    client.connect(hostname=hpc['ip'], username=hpc['user'], port=hpc['port'], pkey=key)

    channel = client.invoke_shell()
    channel_data = ''
    time.sleep(0.5)
    channel.send(terminal_call[0])
    channel.send(terminal_call[1])
    time.sleep(0.5)
    channel_bytes = channel.recv(9999)
    channel_data += channel_bytes.decode("utf-8")

    logger.debug(channel_data)

    logger.info(f'Submitted job {sim_id}\n')

    channel.close()
    client.close()


def wait_until_finished(sim_id: str, estimated_run_time: int, simulation_folder: str):
    """
    Look for summary file. If it is created, continue. If it is not created and the estimated time runs out.
    Then submit a new job continuing the simulation from where it ended.
    """

    finished = False
    start_time = None

    while not start_time:
        if os.path.exists(f"{simulation_folder}/{sim_id}"):
            start_time = datetime.datetime.now()
        else:
            time.sleep(2)

    time_limit = start_time + datetime.timedelta(days=1)

    while not finished:
        simulation_ends = start_time + datetime.timedelta(minutes=estimated_run_time)

        if os.path.exists(f"{simulation_folder}/{sim_id}/log/summary.txt"):
            finished = True

        elif datetime.datetime.now() > simulation_ends + datetime.timedelta(seconds=10):
            files_in_folder = len(os.listdir(simulation_folder))
            estimated_run_time = min(int(estimated_run_time * 1.5), 1440)
            submit_file = create_submit_file(sim_id, simulation_folder, estimated_run_time, restart=True)
            submit_job(submit_file, sim_id)

            while True:
                logger.debug(f'Simulation with ID: {sim_id} is waiting to get simulated.')
                if files_in_folder < len(os.listdir(simulation_folder)):
                    break
                else:
                    time.sleep(5)

            start_time = datetime.datetime.now()
            logger.debug(f'Rerunning simulation with ID: {sim_id} '
                         f'with new estimated run time of: {estimated_run_time}')
        elif datetime.datetime.now() > time_limit:
            finished = True
            logger.warning(f'Simulation with ID: {sim_id} exceeded the simulaiton time limit of 24 hours.')
            return 'time limit reached'

        else:
            if os.path.exists(os.path.join(simulation_folder, sim_id, 'log', 'screenlog.txt')):
                with open(os.path.join(simulation_folder, sim_id, 'log', 'screenlog.txt'), 'r') as logfile:
                    log_data = logfile.readlines()

                if len(log_data) > 1:
                    if "Critical error, simulation aborted." in log_data[-1]:
                        submit_file = create_submit_file(sim_id, simulation_folder, estimated_run_time, restart=True)
                        files_in_folder = len(os.listdir(simulation_folder))
                        submit_job(submit_file, sim_id)

                        while True:
                            logger.debug(f'Simulation with ID: {sim_id} is waiting to get simulated.')
                            if files_in_folder < len(os.listdir(simulation_folder)):
                                break
                            else:
                                time.sleep(5)

                        start_time = datetime.datetime.now()
                        logger.warning(f'Simulation with ID: {sim_id} encountered a critical error: {log_data[-4:]} '
                                       f'\nRerunning failed simulation with new estimated run '
                                       f'time of: {estimated_run_time}')
                    else:
                        time.sleep(60)

            else:
                time.sleep(60)


def hpc_worker(id_: str, folder='H:/ribuild'):
    """Solves a Delphin project through DTU HPC"""

    simulation_folder = os.path.join(folder, id_)

    if not os.path.isdir(simulation_folder):
        os.mkdir(simulation_folder)
    else:
        simulation_interactions.clean_simulation_folder(simulation_folder)
        os.mkdir(simulation_folder)

    # Download, solve, upload
    logger.info(f'Downloads project with ID: {id_}')

    general_interactions.download_full_project_from_database(id_, simulation_folder)
    estimated_time = get_average_computation_time(id_)
    submit_file = create_submit_file(id_, simulation_folder, estimated_time)
    submit_job(submit_file, id_)

    time_0 = datetime.datetime.now()
    return_code = wait_until_finished(id_, estimated_time, simulation_folder)
    delta_time = datetime.datetime.now() - time_0

    if return_code:
        simulation_hours = None
    else:
        simulation_hours = len(delphin_entry.Delphin.objects(id=id_).first().weather) * 8760

    result_id = delphin_interactions.upload_results_to_database(os.path.join(simulation_folder, id_),
                                                                delete_files=False, result_length=simulation_hours)
    delphin_interactions.upload_processed_results(os.path.join(simulation_folder, id_),
                                                  id_, result_id, return_code)

    if return_code:
        delphin_interactions.set_exceeding_time_limit(id_)

    simulation_interactions.set_simulated(id_)
    simulation_interactions.set_simulation_time(id_, delta_time)
    simulation_interactions.clean_simulation_folder(simulation_folder)

    logger.info(f'Finished solving {id_}. Simulation duration: {delta_time}\n')


def simulation_worker(sim_location: str, folder='H:/ribuild') -> None:
    """Solves Delphin projects in the database until interrupted"""

    try:
        while True:
            id_ = simulation_interactions.find_next_sim_in_queue()

            if id_:
                if sim_location == 'local':
                    local_worker(str(id_))

                elif sim_location == 'hpc':
                    try:
                        hpc_worker(str(id_), folder)

                    except Exception as err:
                        simulation_interactions.set_simulating(str(id_), False)
                        logger.exception(err)

                        if not os.path.isdir(os.path.join(folder, 'failed')):
                            os.mkdir(os.path.join(folder, 'failed'))

                        shutil.copytree(os.path.join(folder, str(id_)),
                                        os.path.join(folder, 'failed', str(id_)))
                        time.sleep(5)
                        pass

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

    print('')
    print('------------------- SIMULATION MENU ---------------------')
    print('')
    print("Available actions:")
    print("[a] Simulate locally")
    print("[b] Simulate on DTU HPC")
    print("[x] Exit")

    choice = input("> ").strip().lower()

    if choice == 'a':
        logger.info('Local Simulation Chosen\n')
        simulation_worker('local')

    elif choice == 'b':
        logger.info('Simulation on DTU HPC Chosen\n')
        n_threads = 84
        threads = []

        for n in range(n_threads):
            t_name = f"Worker_{n}"
            logger.info(f'Created thread with name: {t_name}\n')
            thread = threading.Thread(target=simulation_worker, args=('hpc', ))
            thread.name = t_name
            thread.daemon = True
            thread.start()
            threads.append(thread)

            time.sleep(10)

        for thread in threads:
            thread.join()

    elif choice == 'x':
        print("Goodbye")
