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


def add_lambda(entry, index):
    if not index % 1000:
        print(f"Got index: {index}")

    delphin = entry.delphin
    insulation_id = delphin.sample_data.get("design_option", {}).get("insulation_material", None)
    if insulation_id:
        material = material_entry.Material.objects(material_id=insulation_id).first()
        lambda_value = material.material_data.get("TRANSPORT_BASE_PARAMETERS-LAMBDA", None)
        entry.lambda_value = lambda_value
        entry.save()


def get_ids():
    entries_ = normalized_entry.Normalized.objects(lambda_value__exists=False)
    logger.info(f"Got {entries_.count()} without lambda values")
    return list(entries_)


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    entries = get_ids()

    for index, entry in enumerate(entries):
        add_lambda(entry, index)

    mongo_setup.global_end_ssh(server)
