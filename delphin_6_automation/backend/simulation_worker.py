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
import time
import threading
import paramiko
import typing
import shutil
import json
import re

# RiBuild Modules:
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import general_interactions
import delphin_6_automation.database_interactions.db_templates.result_raw_entry as result_db
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger()


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
        folder = r'C:/ribuild'
        exe_path = r'C:/Program Files/IBK/Delphin 6.0/DelphinSolver.exe'
    elif system == 'Linux':
        home = str(Path.home())
        folder = home + '/ribuild'
        exe_path = ''
    else:
        logger.error('OS not supported')
        raise NameError('OS not supported')

    simulation_folder = os.path.join(folder, id_)

    if not os.path.isdir(simulation_folder):
        os.mkdir(simulation_folder)
    else:
        simulation_interactions.clean_simulation_folder(simulation_folder)
        os.mkdir(simulation_folder)

    # Download, solve, upload
    time_0 = datetime.datetime.now()

    logger.info(f'Downloads project with ID: {id_}')

    general_interactions.download_full_project_from_database(str(id_), simulation_folder)
    solve_delphin(os.path.join(simulation_folder, f'{id_}.d6p'), delphin_exe=exe_path, verbosity_level=0)
    result_id = delphin_interactions.upload_results_to_database(os.path.join(simulation_folder, id_),
                                                                delete_files=False)
    delphin_interactions.upload_processed_results(os.path.join(simulation_folder, id_),
                                                  id_, result_id)

    delta_time = datetime.datetime.now() - time_0

    # Check if uploaded:
    test_doc = result_db.Result.objects(id=result_id).first()

    simulation_interactions.set_simulated(id_)
    simulation_interactions.set_simulation_time(id_, delta_time)

    if test_doc:
        simulation_interactions.clean_simulation_folder(simulation_folder)
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


def submit_job(submit_file: str, sim_id: str) -> bool:
    """Submits a job (submit file) to the DTU HPC queue."""

    terminal_call = f"cd /work3/ocni/ribuild/{sim_id} && bsub < {submit_file}\n"

    client = connect_to_hpc()
    logger.debug(f'Connecting to HPC to upload simulation with ID: {sim_id}')

    submitted = False
    retries = 0
    channel = client.invoke_shell()
    time.sleep(0.5)

    while not submitted and retries < 3:
        channel.send(terminal_call)
        response = simulation_interactions.get_command_results(channel)
        submitted = parse_hpc_log(response)
        logger.info(f'HPC response: {submitted}')

        if submitted:
            logger.info(f'Submitted job {sim_id} on {retries}. try')
            channel.close()
            client.close()
            return True

        retries += 1
        time.sleep(30)

    channel.close()
    client.close()

    logger.debug('No job was submitted')

    return False


def parse_hpc_log(raw_data: str) -> typing.Union[str, bool]:
    """Parses the output from HPC to check whether or not the job has been submitted"""

    data = raw_data.split('\n')
    for line in data[::-1]:
        if re.search(r".*submitted to queue.", line.strip()):
            return line.strip()

    return False


def connect_to_hpc(key_file: str = 'hpc_access') -> paramiko.SSHClient:
    system = platform.system()

    if system == 'Windows':
        from delphin_6_automation.database_interactions.auth import hpc
        key = paramiko.RSAKey.from_private_key_file(hpc['key_path'], password=hpc['key_pw'])

    elif system == 'Linux':
        secret_path = '/run/secrets'
        key_path = os.path.join(secret_path, 'ssh_key')
        key = paramiko.RSAKey.from_private_key_file(key_path)
        hpc_path = os.path.join(secret_path, key_file)

        with open(hpc_path, 'r') as file:
            hpc = json.load(file)

    else:
        logger.error('OS not supported')
        raise NameError('OS not supported')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname=hpc['ip'], username=hpc['user'], port=hpc['port'], pkey=key)

    return client


def wait_until_finished(sim_id: str, estimated_run_time: int, simulation_folder: str):
    """
    Look for summary file. If it is created, continue. If it is not created and the estimated time runs out.
    Then submit a new job continuing the simulation from where it ended.
    """

    finished = False
    start_time = None
    consecutive_errors = 0

    while not start_time:
        if os.path.exists(f"{simulation_folder}/{sim_id}"):
            start_time = datetime.datetime.now()
        else:
            time.sleep(2)

    time_limit = start_time + datetime.timedelta(minutes=250)

    while not finished:
        simulation_ends = start_time + datetime.timedelta(minutes=estimated_run_time)

        if os.path.exists(f"{simulation_folder}/{sim_id}/log/summary.txt"):
            finished = True

        elif datetime.datetime.now() > simulation_ends + datetime.timedelta(seconds=10):
            estimated_run_time, start_time = simulation_exceeded_hpc_time(simulation_folder, estimated_run_time, sim_id,
                                                                          time_limit)
            consecutive_errors = 0

        elif datetime.datetime.now() > time_limit:
            finished = True
            logger.warning(f'Simulation with ID: {sim_id} exceeded the simulation time limit of 250 minutes.')
            return 'time limit reached'

        else:
            if os.path.exists(os.path.join(simulation_folder, sim_id, 'log', 'screenlog.txt')):
                with open(os.path.join(simulation_folder, sim_id, 'log', 'screenlog.txt'), 'r') as logfile:
                    log_data = logfile.readlines()

                if len(log_data) > 1:
                    start_time, consecutive_errors = critical_error_occurred(log_data, sim_id, simulation_folder,
                                                                             estimated_run_time, start_time,
                                                                             consecutive_errors)

                    if consecutive_errors >= 3:
                        finished = True
                        logger.warning(f'Simulation with ID: {sim_id} encountered 3 consecutive errors and has '
                                       f'therefore been terminated.')
                        return 'consecutive errors'

                else:
                    time.sleep(60)

            else:
                time.sleep(60)


def minutes_left(time_limit):
    seconds_left = (datetime.datetime.now() - time_limit).total_seconds()
    return int(seconds_left / 60)


def simulation_exceeded_hpc_time(simulation_folder, estimated_run_time, sim_id, time_limit):
    files_in_folder = len(os.listdir(simulation_folder))
    estimated_run_time = min(int(estimated_run_time * 1.5), minutes_left(time_limit))
    submit_file = create_submit_file(sim_id, simulation_folder, estimated_run_time, restart=True)
    submitted = submit_job(submit_file, sim_id)

    if not submitted:
        raise RuntimeError(f'Could not submit job to HPC for simulation with ID: {sim_id}')

    new_files_in_simulation_folder(simulation_folder, files_in_folder, sim_id)

    start_time = datetime.datetime.now()
    logger.info(f'Rerunning simulation with ID: {sim_id} '
                f'with new estimated run time of: {estimated_run_time}')

    return estimated_run_time, start_time


def critical_error_occurred(log_data, sim_id, simulation_folder, estimated_run_time, start_time, consecutive_errors):
    if "Critical error, simulation aborted." in log_data[-1]:
        submit_file = create_submit_file(sim_id, simulation_folder, estimated_run_time, restart=True)
        files_in_folder = len(os.listdir(simulation_folder))
        submitted = submit_job(submit_file, sim_id)

        if not submitted:
            raise RuntimeError(f'Could not submit job to HPC for simulation with ID: {sim_id}')

        new_files_in_simulation_folder(simulation_folder, files_in_folder, sim_id)

        start_time = datetime.datetime.now()
        logger.warning(f'Simulation with ID: {sim_id} encountered a critical error: {log_data[-4:]} '
                       f'\nRerunning failed simulation with new estimated run '
                       f'time of: {estimated_run_time}')

        consecutive_errors += 1
        logger.debug(f'Simulation with ID: {sim_id} encountered an critical error. Raising the number of '
                     f'consecutive errors to: {consecutive_errors}')

        return start_time, consecutive_errors

    else:
        consecutive_errors = 0
        return start_time, consecutive_errors


def new_files_in_simulation_folder(simulation_folder, files_in_folder, sim_id):
    while True:
        logger.debug(f'Simulation with ID: {sim_id} is waiting to get simulated.')
        if files_in_folder < len(os.listdir(simulation_folder)):
            break
        else:
            time.sleep(5)


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
    #estimated_time = simulation_interactions.get_simulation_time_estimate(id_)
    estimated_time = 251
    submit_file = create_submit_file(id_, simulation_folder, estimated_time)
    submitted = submit_job(submit_file, id_)

    if submitted:
        logger.debug('Job successfully submitted. Waiting for completion and processing results.')

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

        if return_code == 'time limit reached':
            delphin_interactions.set_exceeding_time_limit(id_)
            delphin_interactions.upload_restart_data(simulation_folder, id_)

        elif return_code == 'consecutive errors':
            delphin_interactions.set_critical_error(id_)
            delphin_interactions.upload_restart_data(simulation_folder, id_)

        simulation_interactions.set_simulated(id_)
        simulation_interactions.set_simulation_time(id_, delta_time)
        simulation_interactions.clean_simulation_folder(simulation_folder)

        logger.info(f'Finished solving {id_}. Simulation duration: {delta_time}\n')

    else:
        logger.warning(f'Could not submit project with ID: {id_} to HPC.')
        simulation_interactions.clean_simulation_folder(simulation_folder)
        simulation_interactions.set_simulating(id_, False)


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

                        if not os.path.exists(os.path.join(folder, 'failed')):
                            os.mkdir(os.path.join(folder, 'failed'))

                            shutil.copytree(os.path.join(folder, str(id_)),
                                            os.path.join(folder, 'failed', str(id_)))
                        time.sleep(5)
                        pass

            else:
                pass

    except KeyboardInterrupt:
        return


def docker_worker(sim_location: str, folder='/app/data') -> None:
    """Solves Delphin projects in the database until interrupted"""

    id_ = simulation_interactions.find_next_sim_in_queue()

    if id_:
        if sim_location == 'local':
            local_worker(str(id_))

        elif sim_location == 'hpc':
            logger.info('Starting at HPC')
            try:
                hpc_worker(str(id_), folder)

            except Exception as err:
                logger.info('Error encountered')
                simulation_interactions.set_simulating(str(id_), False)
                logger.exception(err)

                if not os.path.isdir(os.path.join(folder, 'failed')):
                    os.mkdir(os.path.join(folder, 'failed'))

                shutil.copytree(os.path.join(folder, str(id_)),
                                os.path.join(folder, 'failed', str(id_)))
                raise RuntimeError

    else:
        logger.info('No ID found')
        return None


def exceeded_worker(sim_location: str, folder='/app/data') -> None:
    """Solves Delphin projects in the database which has exceeded the run time limit"""

    id_ = simulation_interactions.find_exceeded()

    if id_:
        if sim_location == 'local':
            local_worker(str(id_))

        elif sim_location == 'hpc':
            logger.info('Starting at HPC')
            try:
                hpc_worker(str(id_), folder)

            except Exception as err:
                logger.info('Error encountered')
                simulation_interactions.set_simulating(str(id_), False)
                logger.exception(err)

                if not os.path.isdir(os.path.join(folder, 'failed')):
                    os.mkdir(os.path.join(folder, 'failed'))

                shutil.copytree(os.path.join(folder, str(id_)),
                                os.path.join(folder, 'failed', str(id_)))
                raise RuntimeError

    else:
        logger.info('No ID found')
        return None


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
    print("[c] Simulate exceeded simulations on DTU HPC")
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
            thread = threading.Thread(target=simulation_worker, args=('hpc',))
            thread.name = t_name
            thread.daemon = True
            thread.start()
            threads.append(thread)

            time.sleep(10)

        for thread in threads:
            thread.join()

    elif choice == 'c':
        raise NotImplementedError

    elif choice == 'x':
        print("Goodbye")
