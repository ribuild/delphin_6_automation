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


def get_hl():
    entries_ = normalized_entry.Normalized.objects(heat_loss__exists=False)
    logger.info(f"Got {entries_.count()} without heat loss")
    entries_ = normalized_entry.Normalized.objects(heat_loss__lt=0)
    logger.info(f"Got {entries_.count()} with heat loss below 0")
    return entries_


def get_algae():
    entries_ = normalized_entry.Normalized.objects(algae__exists=False)
    logger.info(f"Got {entries_.count()} without algae")
    entries_ = normalized_entry.Normalized.objects(algae=None)
    logger.info(f"Got {entries_.count()} with algae=None")
    entries_ = normalized_entry.Normalized.objects(algae=-1)
    logger.info(f"Got {entries_.count()} with algae=-1")
    return entries_


def get_st():
    entries_ = normalized_entry.Normalized.objects(avg_surface_temp__exists=False)
    logger.info(f"Got {entries_.count()} without avg_surface_temp")
    entries_ = normalized_entry.Normalized.objects(min_surface_temp__exists=False)
    logger.info(f"Got {entries_.count()} without min_surface_temp")
    entries_ = normalized_entry.Normalized.objects(min_surface_temp__lt=0)
    logger.info(f"Got {entries_.count()} with min_surface_temp less than 0")
    return entries_


def get_all():
    entries_ = normalized_entry.Normalized.objects()
    logger.info(f"There is {entries_.count()} entries in the database")


def get_mould():
    entries_ = normalized_entry.Normalized.objects(mould__gt=0.5)
    logger.info(f"Got {entries_.count()} with mould greater than 0.5")

    entries_ = normalized_entry.Normalized.objects(mould__gt=1)
    logger.info(f"Got {entries_.count()} with mould greater than 1")


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    get_all()
    get_hl()
    get_algae()
    get_st()
    get_mould()

    mongo_setup.global_end_ssh(server)
