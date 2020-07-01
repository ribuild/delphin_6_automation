__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import numpy as np
from typing import Tuple

import bson


# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.delphin_setup.damage_models import algae
from delphin_6_automation.database_interactions.db_templates import result_processed_entry, result_raw_entry, \
    delphin_entry, material_entry

# Logger
logger = ribuild_logger(__name__)

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def update_project(delphin_id):
    logger.info(f'Computing algae on project: {delphin_id}')
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

    logger.info(f'Done with computing algea project: {delphin_id}')

    if isinstance(algae_growth, list):
        return max(algae_growth)
    else:
        return algae_growth


def update_result(project_id, algae_growth):
    max_algae = max(algae_growth)
    logger.info(f'Max algae: {max_algae} for project: {project_id}')

    result = result_processed_entry.ProcessedResult.objects(delphin=project_id).first()
    result['thresholds']['algae'] = max_algae
    result.algae.replace(np.asarray(algae_growth).tobytes())

    result.save()

    logger.info(f'Uploaded algae to result with ID: {result.id}')


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
