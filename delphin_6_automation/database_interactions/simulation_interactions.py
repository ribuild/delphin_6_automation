__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import datetime
import time
import shutil

# RiBuild Modules:
import delphin_6_automation.database_interactions.db_templates.delphin_entry as delphin_db
from delphin_6_automation.database_interactions import general_interactions as general_interact
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger(__name__)

# -------------------------------------------------------------------------------------------------------------------- #
# RIBUILD SIMULATION FUNCTIONS AND CLASSES


def download_simulation_result(sim_id, download_path, raw_or_processed='raw'):
    object_ = delphin_db.Delphin.objects(id=sim_id).first()

    download_extended_path = download_path + '/' + str(sim_id)
    os.mkdir(download_extended_path)

    if raw_or_processed == 'raw':
        result_id = object_.result_id
        logger.info(f'Downloads raw result with ID: {result_id} from Delphin project with ID: {sim_id}')
        general_interact.download_raw_result(result_id, download_extended_path)

    elif raw_or_processed == 'processed':
        pass
        # TODO - Download processed results from database

    else:
        raise ValueError('raw_or_processed has to be raw or processed. Value given was: ' + str(raw_or_processed))

    return True


def find_next_sim_in_queue():
    """
    Finds the next entry in the simulation queue, which is not yet simulated and has the highest queue priority.

    :return: If a entry is found the id will be returned otherwise None.
    :rtype: str or None
    """

    try:
        id_ = delphin_db.Delphin.objects(simulating=False, simulated=None).order_by('-queue_priority').first().id
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
    :type id_: str
    :param set_to: What to set simulating to. Should be either True or False.
    :type set_to: bool
    :return: ID of the entry
    :rtype: str
    """

    simulation = delphin_db.Delphin.objects(id=id_).first()
    simulation.update(set__simulating=set_to)
    logger.debug(f'For Delphin project with ID: {id_}, simulation was change to: {set_to}')

    return simulation.id


def set_simulated(id_: str):
    """
    Flags an entry for finishing the simulation.

    :param id_: ID of the entry
    :type id_: str
    :return: ID of the entry
    :rtype: str
    """

    simulation = delphin_db.Delphin.objects(id=id_).first()
    simulation.update(set__simulated=datetime.datetime.now())
    set_simulating(id_, False)
    logger.debug(f'For Delphin project with ID: {id_}, simulated was changed to: {datetime.datetime.now()}')

    return simulation.id


def clean_simulation_folder(path: str) -> bool:
    """
    Cleans the simulation folder for content

    :param path: Path to the simulation folder
    :type path: str
    :return: True on success
    :rtype: bool
    """

    shutil.rmtree(path)
    logger.debug(f'Deleted {path}')

    return True


def set_simulation_time(sim_id: str, computation_time: datetime.timedelta):

    delphin_entry = delphin_db.Delphin.objects(id=sim_id).first()
    delphin_entry.update(set__simulation_time=computation_time.total_seconds())
    logger.debug(f'For Delphin project with ID: {id_}, '
                 f'simulation time was changed to: {computation_time.total_seconds()}')

    return sim_id


def wait_until_simulated(delphin_ids: list) -> bool:
    """
    Wait until all simulations in the given list is simulated.

    :param delphin_ids: List with Delphin database ids
    :type delphin_ids: list
    :return: True
    :rtype: bool
    """

    simulated = [False] * len(delphin_ids)

    while not all(simulated):
        for index, id_ in enumerate(delphin_ids):
            entry = delphin_db.Delphin.objects(id=id_).first()

            if entry.simulated:
                simulated[index] = True

            else:
                logger.debug('Waiting until all projects are simulated')
                time.sleep(180)

    logger.debug('All projects are simulated')
    return True
