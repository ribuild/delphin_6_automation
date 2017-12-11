__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:


# RiBuild Modules:
from delphin_6_automation.nosql.db_templates.delphin_entry import delphin_db
from delphin_6_automation.nosql.db_templates.result_entry import result_db

# -------------------------------------------------------------------------------------------------------------------- #
# DATABASE INTERACTIONS


def gather_material_list(delphin_id: str)->list:
    """
    Gathers the material file names of Delphin file in the database
    :param delphin_id: database id
    :return: list of material file names
    """

    delphin_document = delphin_db.objects(id=delphin_id).first()

    material_list = []
    for material_dict in delphin_document['dp6_file']['DelphinProject']['Materials']['MaterialReference']:
        material_list.append(material_dict['#text'].split('/')[-1])

    return material_list


def download_raw_result(result_id, download_path):
    result_obj = result_db.objects(id=result_id).first()

    delphin_interact.write_log_files(result_obj, download_path)
    delphin_interact.write_result_files(result_obj, download_path)
    delphin_interact.write_geometry_files(result_obj, download_path)

    return True


def download_result(result_id, download_path):
    object_ = delphin_db.Delphin.objects(id=sim_id).first()
    result_id = object_.id

    return None


def queue_priorities(priority: str)-> int:
    priority_list = [obj.queue_priority
                     for obj in delphin_db.Delphin.objects.order_by('queue_priority')]

    min_priority = min(priority_list)
    span = max(priority_list) - min_priority

    if priority == 'high':
        priority_number = int(span * 0.75 + min_priority)

    elif priority == 'medium':
        priority_number = int(span * 0.5 + min_priority)

    elif priority == 'low':
        priority_number = int(span * 0.25 + min_priority)

    else:
        raise ValueError('priority has to be: high, medium or low. Value given was: ' + str(priority))

    return priority_number


def add_to_queue(delphin_file: str, priority: str)-> str:
    priority_number = queue_priorities(priority)
    simulation_id = delphin.upload_to_database(delphin_file, priority_number)

    return simulation_id


def start_simulation(sim_id: str):
    return None


def is_simulation_finished(sim_id):
    object_ = delphin_db.Delphin.objects(id=sim_id).first()
    if object_.simulated:
        return True
    else:
        return False