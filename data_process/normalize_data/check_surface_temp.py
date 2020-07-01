# Modules
import bson

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions.db_templates import normalized_entry
from data_process.normalize_data.algea import update_project
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
import numpy as np
import matplotlib.pyplot as plt

# Logger
logger = ribuild_logger(__name__)


def update_surf_temp(entry_, index):
    print(f"Updating {entry_.id} / {index}")


    delphin = entry_.delphin
    results = delphin.result_processed
    result_data = bson.BSON.decode(results.results_raw.results.read())


    temp = result_data["temperature interior surface"]["result"]
    avg_temp, min_temp = get_surface_temps(temp)

    temp = np.asarray(temp)
    temp = temp[temp > avg_temp / 1.5]

    entry.avg_surface_temp = np.mean(temp)
    entry.min_surface_temp = np.min(temp)
    entry.save()

    """
    print(f'MIN: {min_temp} - AVG: {avg_temp}')
    print(f'DIF: {avg_temp - min_temp} - REL DIF: {(avg_temp - min_temp) / avg_temp}')
    print(f'LEN: {len(result_data["temperature interior surface"]["result"])}\n')
    
    #temp = result_data["temperature interior surface"]["result"]
    relhum = result_data["relative humidity interior surface"]["result"]
    plt.figure()
    plt.title(f"Project: {str(delphin.id)[:8]} - City: {entry_.city} - Insulation: {entry_.insulation_system}")
    plt.plot(np.arange(len(temp)), temp, label="Temp")
    plt.plot(np.arange(len(relhum)), relhum, label="RELHUM")
    plt.legend()

    entry.algae = get_algea(results, delphin.id)
    entry.avg_surface_temp = avg_temp
    entry.min_surface_temp = min_temp
    entry.save()
    """

def get_st():
    #entries_ = normalized_entry.Normalized.objects(avg_surface_temp__exists=False)
    #logger.info(f"Got {entries_.count()} without avg_surface_temp")

    temp = -4
    entries_ = normalized_entry.Normalized.objects(min_surface_temp__lt=temp)
    logger.info(f"Got {entries_.count()} with min_surface_temp less than {temp}")
    return entries_


def get_surface_temps(results_):
    results = results_[8760:]  # Get rid of the first year
    if not len(results):
        results = results_

    min_temp = min(results)
    avg_temp = sum(results) / len(results)

    return avg_temp, min_temp


def get_algea(results, delphin_id):
    try:
        value = results['thresholds']['algae']
    except KeyError:
        value = update_project(delphin_id)

    return value


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    entries = get_st()
    for index, entry in enumerate(entries):
        update_surf_temp(entry, index)

    plt.show()
    mongo_setup.global_end_ssh(server)