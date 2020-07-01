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

# Logger
logger = ribuild_logger(__name__)


def add_rain(entry_, index_):
    if not index % 1000:
        logger.info(f"RAIN UPDATE - Got index: {index_}")

    delphin = entry_.delphin
    rain = delphin.sample_data.get("rain_scale_factor")
    entry_.rain = rain
    entry_.save()


def get_ids():
    entries_ = normalized_entry.Normalized.objects(rain__exists=False)
    logger.info(f"Got {entries_.count()} without rain values")
    return list(entries_)


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    entries = get_ids()

    for index, entry in enumerate(entries):
        add_rain(entry, index)

    mongo_setup.global_end_ssh(server)
