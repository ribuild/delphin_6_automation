# Modules
import bson

from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import normalized_entry, delphin_entry

# RiBuild Modules
from delphin_6_automation.delphin_setup.damage_models import mould_index
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger("check_mould")


def update_mould(entry, index):
    logger.info(f"MOULD UPDATE - Got index: {index}")

    delphin = entry.delphin
    results = delphin.result_processed
    data = bson.BSON.decode(results.results_raw.results.read())

    temp_ = data["temperature mould"]["result"]
    if len(temp_) > 8760:
        temp = temp_[8760:]
    else:
        temp = temp_

    relhum_ = data["relative humidity mould"]["result"]
    if len(relhum_) > 8760:
        relhum = relhum_[8760:]
    else:
        relhum = relhum_

    if len(temp) > len(relhum):
        temp = temp[:len(relhum)]
    elif len(relhum) > len(temp):
        relhum = relhum[:len(temp)]

    mould = mould_index(temp, relhum, draw_back=1, sensitivity_class=4, surface_quality=0)
    max_mould = max(mould)

    entry.mould = max_mould
    entry.save()


def get_ids(start_):
    entries_ = normalized_entry.Normalized.objects()
    logger.info(f"Got {entries_.count()} entries")
    return list(entries_)[start_:106118]


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    start = 94089
    entries = get_ids(start)

    for index, entry in enumerate(entries):
        update_mould(entry, index + start)

    mongo_setup.global_end_ssh(server)
