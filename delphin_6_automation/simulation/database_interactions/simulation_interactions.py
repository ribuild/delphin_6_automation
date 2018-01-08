__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os

# RiBuild Modules:
import delphin_6_automation.simulation.nosql.db_templates.delphin_entry as delphin_db
from delphin_6_automation.simulation.database_interactions import general_interactions as general_interact

# -------------------------------------------------------------------------------------------------------------------- #
# RIBUILD SIMULATION FUNCTIONS AND CLASSES


def download_simulation_result(sim_id, download_path, raw_or_processed='raw'):
    object_ = delphin_db.Delphin.objects(id=sim_id).first()

    download_extended_path = download_path + '/' + str(sim_id)
    os.mkdir(download_extended_path)

    if raw_or_processed == 'raw':
        result_id = object_.result_id
        general_interact.download_raw_result(result_id, download_extended_path)

    elif raw_or_processed == 'processed':
        pass
        # TODO - Download processed results from database

    else:
        raise ValueError('raw_or_processed has to be raw or processed. Value given was: ' + str(raw_or_processed))

    return True


def start_simulation(sim_id: str):
    return None
