__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:


# RiBuild Modules:
from delphin_6_automation.nosql.db_templates import delphin_entry as delphin_db
from delphin_6_automation.nosql.db_templates import result_raw_entry as result_db
from delphin_6_automation.database_interactions import delphin_interactions as delphin_interact
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.file_parsing import material_parser
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# MATERIAL INTERACTIONS


def download_raw_result(result_id: str, download_path: str) -> bool:
    """
    Downloads a result entry from the database.

    :param result_id: Database entry id
    :param download_path: Path where the result should be written
    :return: True
    """

    result_obj = result_db.Result.objects(id=result_id).first()

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


def download_materials(sim_id: str, path: str) -> bool:

    materials_list = delphin_db.Delphin.objects(id=sim_id).first().materials

    for material in materials_list:
        material_parser.dict_to_m6(material, path)

    return True


def download_full_project_from_database(document_id: str, folder: str) -> bool:
    """
    Downloads a Delphin project file from the database with all of its materials and weather.

    :param document_id: Database entry id
    :param folder: Path where the files should be written.
    :return: True
    """

    delphin_interact.download_delphin_entry(document_id, folder)
    download_materials(document_id, folder)
    weather_interactions.download_weather(document_id, folder)

    return True
