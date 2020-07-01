from typing import Tuple

import bson

from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import delphin_entry, result_raw_entry, material_entry, \
    result_processed_entry
from delphin_6_automation.delphin_setup.damage_models import algae
from multiprocessing import Pool
import numpy as np
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger()


def get_result_data(project_id) -> Tuple[list, list]:
    result = result_raw_entry.Result.objects(delphin=project_id).first()
    data = bson.BSON.decode(result.results.read())

    return data['temperature algae']['result'], data['relative humidity algae']['result']


def get_material_data(project_id):
    sample_data = delphin_entry.Delphin.objects(id=project_id).only('sample_data').first().sample_data
    plaster = sample_data['design_option'].get('exterior_plaster', None)

    if plaster:
        material = sample_data['exterior_plaster_material']
    else:
        material = sample_data['wall_core_material']

    return get_porosity_and_type(material)


def get_porosity_and_type(material):
    material = material_entry.Material.objects(material_id=material).first()
    porosity = material.material_data.get('STORAGE_BASE_PARAMETERS-THETA_POR', 0.5)
    material_name = material.material_name

    logger.info(f'Material: {material.material_name} - Porosity: {porosity}')
    return material_name, porosity


def update_result(project_id, algae_growth):
    max_algae = max(algae_growth)
    logger.info(f'Max algae: {max_algae} for project: {project_id}')

    result = result_processed_entry.ProcessedResult.objects(delphin=project_id).first()
    result['thresholds']['algae'] = max_algae
    result.algae.replace(np.asarray(algae_growth).tobytes())

    result.save()

    logger.info(f'Uploaded algae to result with ID: {result.id}')


def get_delphin_ids():
    index = 3900
    ids = delphin_entry.Delphin.objects[index:5000].only('id')
    logger.info(f'Got {ids.count()} projects')
    logger.info(f'Starting at index {index}')

    ids = [project_.id for project_ in ids]

    return ids, index


def update_project(delphin_id, index):
    logger.info(f'Starting on project: {delphin_id}. Index: {index}')
    temperature, relative_humidity = get_result_data(delphin_id)
    material_name, porosity = get_material_data(delphin_id)

    if 0.19 <= porosity <= 0.44:
        algae_growth = algae(relative_humidity, temperature, material_name=material_name, porosity=porosity,
                             roughness=5.5,
                             total_pore_area=6.5)
    else:
        logger.info(
            f'Project {delphin_id} with material {material_name} has a porosity {porosity} outside the accepted range.')
        algae_growth = [-1, ]
    update_result(delphin_id, algae_growth)

    logger.info(f'Done with project: {delphin_id}')


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)
    project_ids, i = get_delphin_ids()

    #pool = Pool(4)
    #pool.map(update_project, project_ids)

    for index, project in enumerate(project_ids):
        update_project(project, index + i)

    mongo_setup.global_end_ssh(server)
