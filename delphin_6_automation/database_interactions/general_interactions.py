__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os

# RiBuild Modules:
from delphin_6_automation.database_interactions.db_templates import delphin_entry as delphin_db
from delphin_6_automation.database_interactions.db_templates import result_raw_entry as result_db
from delphin_6_automation.database_interactions.db_templates import weather_entry as weather_db
from delphin_6_automation.database_interactions.db_templates import material_entry as material_db
from delphin_6_automation.file_parsing import delphin_parser

from delphin_6_automation.database_interactions import delphin_interactions as delphin_interact
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions.db_templates import user_entry

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

    if not os.path.exists(download_path):
        os.mkdir(download_path)

    delphin_parser.write_log_files(result_obj, download_path)
    delphin_interact.download_result_files(result_obj, download_path)

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
            priority_number = int(span * 0.5 + min_priority)

        elif priority == 'low':
            priority_number = int(span * 0.25 + min_priority)

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
    simulation_id = delphin_interact.upload_delphin_to_database(delphin_file, priority_number)

    return simulation_id


def is_simulation_finished(sim_id: str) -> bool:
    """
    Checks if a Delphin project entry is simulated or not.

    :param sim_id: Database entry to check
    :return: True if it is simulated otherwise returns False.
    """

    object_ = delphin_db.Delphin.objects(id=sim_id).first()

    if object_.simulated:
        return True
    else:
        return False


def list_finished_simulations() -> list:
    """
    Returns a list with Delphin entry ID's for simulated entries.

    :return: List
    """

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

    material_interactions.download_materials(document_id, folder + '/materials')
    weather_interactions.download_weather(document_id, folder + '/weather')
    delphin_interact.download_delphin_entry(document_id, folder)

    return True


def list_weather_stations() -> dict:

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


def create_account(name: str, email: str) -> user_entry.User:
    user = user_entry.User()
    user.name = name
    user.email = email

    user.save()

    return user


def find_account_by_email(email: str) -> user_entry.User:
    user = user_entry.User.objects(email=email).first()

    return user
