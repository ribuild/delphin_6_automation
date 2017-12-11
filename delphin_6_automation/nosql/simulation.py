__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:


# RiBuild Modules:
import delphin_6_automation.delphin_db as delphin
import delphin_6_automation.nosql.db_templates.delphin_entry as delphin_db
import delphin_6_automation.nosql.database_interactions as db_interact

# -------------------------------------------------------------------------------------------------------------------- #
# RIBUILD SIMULATION FUNCTIONS AND CLASSES


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


simulation_db = delphin_db.Delphin


def is_simulation_finished(sim_id):
    object_ = delphin_db.Delphin.objects(id=sim_id).first()
    if object_.simulated:
        return True
    else:
        return False


def download_simulation_result(sim_id, download_path):
    object_ = delphin_db.Delphin.objects(id=sim_id).first()
    result_id = object_.id

    db_interact.download_result(result_id, download_path)
    return True