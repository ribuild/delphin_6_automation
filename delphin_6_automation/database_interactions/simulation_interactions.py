__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import datetime
import time
import shutil
import typing

# RiBuild Modules:
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import general_interactions as general_interact
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.backend import simulation_worker

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# RIBUILD SIMULATION FUNCTIONS AND CLASSES


def download_simulation_result(sim_id: str, download_path: str, raw_or_processed='raw') -> None:
    """
    Downloads Delphin simulation results from the database.

    :param sim_id: Delphin project ID
    :param download_path: Path to download to
    :param raw_or_processed: Whether to download the raw results or the processed ones
    :return: None
    """

    delphin_doc = delphin_entry.Delphin.objects(id=sim_id).first()

    download_extended_path = download_path + '/' + str(sim_id)
    os.mkdir(download_extended_path)

    if raw_or_processed == 'raw':
        result_id = delphin_doc.results_raw
        logger.info(f'Downloads raw result with ID: {result_id} from Delphin project with ID: {sim_id}')
        general_interact.download_raw_result(result_id.id, download_extended_path)

    elif raw_or_processed == 'processed':
        pass
        # TODO - Download processed results from database

    else:
        raise ValueError('raw_or_processed has to be raw or processed. Value given was: ' + str(raw_or_processed))

    return None


def find_next_sim_in_queue() -> typing.Optional[str]:
    """
    Finds the next entry in the simulation queue, which is not yet simulated and has the highest queue priority.

    :return: If a entry is found the id will be returned otherwise None.
    """

    try:
        id_ = delphin_entry.Delphin.objects(simulating=False, simulated=None).order_by('-queue_priority').first().id
        set_simulating(str(id_), True)
        logger.debug(f'Found unsimulated Delphin project with ID: {id_}')
        return str(id_)

    except AttributeError:
        logger.info('All Delphin Projects in the queue are simulated!')
        time.sleep(60)
        return None


def set_simulating(id_: str, set_to: bool) -> str:
    """
    Set the simulating flag of an entry.

    :param id_: ID of the entry
    :param set_to: What to set simulating to. Should be either True or False.
    :return: ID of the entry
    """

    delphin_doc = delphin_entry.Delphin.objects(id=id_).first()
    delphin_doc.update(set__simulating=set_to)
    logger.debug(f'For Delphin project with ID: {id_}, simulation was change to: {set_to}')

    return delphin_doc.id


def set_simulated(id_: str) -> str:
    """
    Flags an entry for finishing the simulation.

    :param id_: ID of the entry
    :return: ID of the entry
    """

    simulation = delphin_entry.Delphin.objects(id=id_).first()
    simulation.update(set__simulated=datetime.datetime.now())
    set_simulating(id_, False)
    logger.debug(f'For Delphin project with ID: {id_}, simulated was changed to: {datetime.datetime.now()}')

    return simulation.id


def clean_simulation_folder(path: str) -> bool:
    """
    Cleans the simulation folder for content

    :param path: Path to the simulation folder
    :return: True on success
    """

    shutil.rmtree(path)
    logger.debug(f'Deleted {path}')

    return True


def set_simulation_time(sim_id: str, computation_time: datetime.timedelta) -> str:
    """Sets the time it took to simulate Delphin project"""

    delphin_doc = delphin_entry.Delphin.objects(id=sim_id).first()
    delphin_doc.update(set__simulation_time=computation_time.total_seconds())
    logger.debug(f'For Delphin project with ID: {sim_id}, '
                 f'simulation time was changed to: {computation_time.total_seconds()}')

    return sim_id


def set_simulation_time_estimate(sim_id: str, computation_time: int) -> str:
    """Sets the estimate simulation time for a Delphin project"""

    delphin_doc = delphin_entry.Delphin.objects(id=sim_id).first()
    delphin_doc.update(set__estimated_simulation_time=computation_time)
    logger.debug(f'For Delphin project with ID: {sim_id}, '
                 f'simulation time was changed to: {computation_time}')

    return sim_id


def get_simulation_time_estimate(delphin_id: str) -> int:
    """Returns the estimated simulation time of Delphin project, given its ID"""

    delphin_doc = delphin_entry.Delphin.objects(id=delphin_id).first()

    if delphin_doc.estimated_simulation_time:
        return delphin_doc.estimated_simulation_time
    else:
        return general_interact.compute_simulation_time(delphin_id)


def wait_until_simulated(delphin_ids: list) -> bool:
    """
    Wait until all simulations in the given list is simulated.

    :param delphin_ids: List with Delphin database ids
    :return: True
    """

    simulated = [False] * len(delphin_ids)
    logger.info(f'Checking if Delphin projects have been simulated')

    while not all(simulated):
        for index, id_ in enumerate(delphin_ids):
            entry = delphin_entry.Delphin.objects(id=id_).first()

            if entry.simulated:
                simulated[index] = True

            else:
                logger.debug('Waiting until all projects are simulated')
                time.sleep(180)

    logger.info('All projects are simulated')
    return True


def find_exceeded() -> typing.Optional[str]:
    """
    Finds a Delphin project which has exceeded the simulation run time limit.

    :return: If a entry is found the id will be returned otherwise None.
    """

    try:
        id_ = delphin_entry.Delphin.objects(simulating=False,
                                            exceeded_time_limit=True).order_by('-queue_priority').first().id
        set_simulating(str(id_), True)
        logger.debug(f'Found exceeded Delphin project with ID: {id_}')
        return str(id_)

    except AttributeError:
        logger.info('No exceeded Delphin Projects in the database!')
        time.sleep(60)
        return None


def check_simulations(auth_file: str) -> None:
    """Submits a job (submit file) to the DTU HPC queue."""

    terminal_call = f"bstat\n"

    client = simulation_worker.connect_to_hpc(auth_file)

    channel = client.invoke_shell()
    channel_data = ''
    time.sleep(0.5)
    channel.send(terminal_call)
    time.sleep(1.0)
    channel_bytes = channel.recv(9999)
    channel_data += channel_bytes.decode("utf-8")

    print(channel_data)

    channel.close()
    client.close()
