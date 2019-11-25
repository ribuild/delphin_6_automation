from copy import deepcopy

from delphin_6_automation.database_interactions.db_templates import delphin_entry, result_processed_entry

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
    ids = delphin_entry.Delphin.objects[:550].only('id')
    logger.info(f'Got {ids.count()} projects')

    ids = [project.id for project in ids]

    return ids


def get_algae(project_id):
    result = result_processed_entry.ProcessedResult.objects(delphin=project_id).first()
    try:
        algae = result['thresholds']['algae']
    except KeyError:
        algae = None
    logger.info(f'Max algae: {algae} for project: {project_id}')
    return algae


def get_sample_data(project_id):
    project = delphin_entry.Delphin.objects(id=project_id).only('sample_data').first()
    data = deepcopy(project.sample_data)
    del data['sequence']
    design = data['design_option']
    del data['design_option']
    data.update(design)


    return data


def process_data(project_id):
    data = get_sample_data(project_id)
    data['algae'] = get_algae(project_id)
    data[id] = project_id

    return pd.DataFrame(data, index=[0])


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)
    project_ids = get_delphin_ids()


    #pool = Pool(4)
    #data_frames = pool.map(process_data, project_ids)
    data_frames = [process_data(id_) for id_ in project_ids]
    mongo_setup.global_end_ssh(server)
    data_frame = None

    for df in data_frames:

        if not isinstance(data_frame, pd.DataFrame):
            data_frame = df
        else:
            df_add = pd.DataFrame.from_dict(df)
            data_frame = data_frame.append(df_add)

    data_frame.to_excel("Algae Growth.xlsx", index=False)
