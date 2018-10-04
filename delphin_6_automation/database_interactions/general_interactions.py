__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import pickle
import numpy as np

# RiBuild Modules:
from delphin_6_automation.database_interactions.db_templates import delphin_entry as delphin_db, delphin_entry
from delphin_6_automation.database_interactions.db_templates import result_raw_entry as result_db
from delphin_6_automation.database_interactions.db_templates import weather_entry as weather_db
from delphin_6_automation.database_interactions.db_templates import material_entry as material_db
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# MATERIAL INTERACTIONS


def download_raw_result(result_id: str, download_path: str) -> bool:
    """
    Downloads a result entry from the database.rst.

    :param result_id: Database entry id
    :param download_path: Path where the result should be written
    :return: True
    """

    result_obj = result_db.Result.objects(id=result_id).first()
    download_path = os.path.join(download_path, str(result_id))

    if not os.path.exists(download_path):
        os.mkdir(download_path)

    # delphin_parser.write_log_files(result_obj, download_path)
    delphin_interactions.download_result_files(result_obj, download_path)

    return True


def queue_priorities(priority: str)-> int:
    """
    Generate a queue priority number.

    :param priority: High, medium or low priority
    :return: Priority number
    """

    priority_list = [obj.queue_priority
                     for obj in delphin_db.Delphin.objects.order_by('queue_priority')]

    if not priority_list:
        return 1

    else:
        min_priority = min(priority_list)
        max_priority = max(priority_list)
        span = max_priority - min_priority

        if priority == 'high':
            priority_number = int(max_priority)

        elif priority == 'medium':
            priority_number = int(span + 0.5 * min_priority)

        elif priority == 'low':
            priority_number = int(span + 0.25 * min_priority)

        else:
            raise ValueError('priority has to be: high, medium or low. Value given was: ' + str(priority))

        return priority_number


def add_to_simulation_queue(delphin_file: str, priority: str)-> str:
    """
    Uploads and adds a Delphin project file to the simulation queue.

    :param delphin_file: Delphin 6 project file path
    :param priority: High, medium or low priority
    :return: Database entry id
    """

    priority_number = queue_priorities(priority)
    simulation_id = delphin_interactions.upload_delphin_to_database(delphin_file, priority_number)

    logger.debug(f'Added Delphin project with ID: {simulation_id} to queue with priority: {priority}')

    return simulation_id


def is_simulation_finished(sim_id: str) -> bool:
    """
    Checks if a Delphin project entry is simulated or not.

    :param sim_id: Database entry to check
    :return: True if it is simulated otherwise returns False.
    """

    object_ = delphin_db.Delphin.objects(id=sim_id).first()

    if object_.simulated:
        logger.debug(f'Delphin project with ID: {sim_id} is finished simulating')
        return True
    else:
        logger.debug(f'Delphin project with ID: {sim_id} is not finished simulating')
        return False


def list_finished_simulations() -> list:
    """Returns a list with Delphin entry ID's for simulated entries."""

    finished_list = [document.id
                     for document in delphin_db.Delphin.objects()
                     if document.simulated]

    return finished_list


def download_full_project_from_database(document_id: str, folder: str) -> bool:
    """
    Downloads a Delphin project file from the database.rst with all of its materials and weather.

    :param document_id: Database entry id
    :param folder: Path where the files should be written.
    :return: True
    """

    delphin_document = delphin_db.Delphin.objects(id=document_id).first()

    material_interactions.download_materials(delphin_document, os.path.join(folder, 'materials'))
    weather_interactions.download_weather(delphin_document, os.path.join(folder, 'weather'))
    #delphin_interactions.download_delphin_entry(delphin_document, folder)

    logger.debug(f'Download Delphin project with ID: {document_id} from database with weather and materials.')

    return True


def list_weather_stations() -> dict:
    """List the weather stations currently in database"""

    weather_stations = dict()

    for document in weather_db.Weather.objects():
        if document.location_name in weather_stations.keys():
            weather_stations[document.location_name]['years'].append(document.year)
        else:
            weather_stations[str(document.location_name)] = dict()
            weather_stations[str(document.location_name)]['location'] = document.location
            weather_stations[str(document.location_name)]['years'] = [document.year, ]

    return weather_stations


def print_weather_stations_dict(weather_station_dict):

    for key in weather_station_dict.keys():
        print(f'Weather Station: {key} at location: {weather_station_dict[key]["location"]} contains '
              f'{len(weather_station_dict[key]["years"])} years.\n'
              f'\t The years are: {weather_station_dict[key]["years"]}')


def list_materials():
    """List materials currently in the database"""

    materials = dict()
    for document in material_db.Material.objects():
        materials[str(document.material_name)] = dict()
        materials[str(document.material_name)]['material_id'] = document.material_id
        materials[str(document.material_name)]['database_id'] = document.id

    return materials


def print_material_dict(materials):

    for key in materials.keys():
        print(f'Material:\n'
              f'\tName: {key}\n'
              f'\tDelphin Material ID: {materials[key]["material_id"]}\n'
              f'\tDatabase ID: {materials[key]["database_id"]}\n')


def does_simulation_exists(sim_id: str) -> bool:
    """
    Checks if a Delphin project entry is in the database or not.

    :param sim_id: Database entry to check
    :return: True if it is in database otherwise returns False.
    """

    object_ = delphin_db.Delphin.objects(id=sim_id).first()

    if object_:
        return True
    else:
        return False


def compute_simulation_time(sim_id: str) -> int:
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
        avg_time = int(np.ceil(np.mean(sim_time) / 60))
        logger.debug(f'Average simulation time for Delphin projects in {dimension}D: {avg_time}min')
        return avg_time

    elif dimension == 2:
        logger.debug(f'No previous simulations found. Setting time to 180min for a 2D simulation')
        return 240

    else:
        logger.debug(f'No previous simulations found. Setting time to 60min for a 1D simulation')
        return 120


def simulation_time_prediction_ml(delphin_doc: delphin_entry.Delphin) -> int:

    inputs = delphin_doc.sample_data
    time_model = pickle.load(open(os.path.join(os.path.dirname(__file__), 'sim_time_model.sav'), 'rb'))
    sim_time_secs = time_model.predict()

    return sim_time_secs / 60
