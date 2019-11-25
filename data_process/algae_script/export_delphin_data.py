from copy import deepcopy
from typing import Tuple

import bson

from delphin_6_automation.database_interactions.db_templates import delphin_entry, result_processed_entry, \
    result_raw_entry

__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
from multiprocessing import Pool
# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger(__name__)


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def get_delphin_ids():
    ids = delphin_entry.Delphin.objects[:10].only('id')
    logger.info(f'Got {ids.count()} projects')

    ids = [project.id for project in ids]

    return ids


def get_result_data(project_id) -> Tuple[list, list]:
    result = result_raw_entry.Result.objects(delphin=project_id).first()
    data = bson.BSON.decode(result.results.read())

    return data['temperature algae']['result'][:43800], data['relative humidity algae']['result'][:43800]


def process_data(project_id):
    logger.info(f'Processing project: {project_id}')
    temp, rh = get_result_data(project_id)

    if len(temp) != 43800:
        return None
    else:
        data = {'temperature': temp, 'relative humidity': rh}

        return data


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)
    project_ids = get_delphin_ids()

    data = {}
    for id_ in project_ids:
        ret = process_data(id_)
        if ret:
            data[id_] = ret

    mongo_setup.global_end_ssh(server)

    reform = {(outerKey, innerKey): values for outerKey, innerDict in data.items() for innerKey, values in
              innerDict.items()}
    data_frame = pd.DataFrame(reform)

    data_frame.to_excel("Delphin Projects.xlsx")
