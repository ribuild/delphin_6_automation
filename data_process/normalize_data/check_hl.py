# Modules
from multiprocessing import Pool
import bson

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions.db_templates import normalized_entry
from data_process.normalize_data.algea import update_project
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import delphin_entry, material_entry, weather_entry
import numpy as np

# Logger
logger = ribuild_logger(__name__)


def update_heat_loss(entry, index):
    if not index % 100:
        print(f"Got index: {index}")

    delphin = entry.delphin
    results = delphin.result_processed
    heat_loss_ = np.asarray(bson.BSON.decode(results.results_raw.results.read())["heat loss"]["result"])
    heat_loss = heat_loss_[8760:]  # Get rid of the first year
    if not heat_loss.size:
        heat_loss = heat_loss_
    value = heat_loss[heat_loss > 0].sum() / (heat_loss.size / 8760)

    entry.heat_loss = value
    entry.save()



def get_ids():
    #entries_ = normalized_entry.Normalized.objects(heat_loss__exists=False)
    #entries_ = normalized_entry.Normalized.objects(heat_loss='nan')
    entries_ = normalized_entry.Normalized.objects(heat_loss__lt=0)
    logger.info(f"Got {entries_.count()} without heat loss")
    return entries_


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    entries = get_ids()

    for index, entry in enumerate(entries):
        update_heat_loss(entry, index)

    mongo_setup.global_end_ssh(server)
