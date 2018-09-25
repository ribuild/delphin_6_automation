__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
from mongoengine.queryset.visitor import Q
import matplotlib.pyplot as plt
import numpy as np

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# Logger
logger = ribuild_logger(__name__)


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def filter_db(config: dict):
    filtered_entries = delphin_entry.Delphin.objects(simulated__exists=True)

    if config['exterior_climate']:
        filtered_entries = filtered_entries.filter(sample_data__exterior_climate=config['exterior_climate'])

    if config['exterior_heat_transfer_coefficient_slope']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__exterior_heat_transfer_coefficient_slope__gte=config[
                'exterior_heat_transfer_coefficient_slope'][0])
            & Q(sample_data__exterior_heat_transfer_coefficient_slope__lte=config[
                'exterior_heat_transfer_coefficient_slope'][1]))

    if config['exterior_moisture_transfer_coefficient']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__exterior_moisture_transfer_coefficient__gte=config['exterior_moisture_transfer_coefficient'][
                0])
            & Q(sample_data__exterior_moisture_transfer_coefficient__lte=
                config['exterior_moisture_transfer_coefficient'][1]))

    if config['solar_absorption']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__solar_absorption__gte=config['solar_absorption'][0])
            & Q(sample_data__solar_absorption__lte=config['solar_absorption'][1]))

    if config['rain_scale_factor']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__rain_scale_factor__gte=config['rain_scale_factor'][0])
            & Q(sample_data__rain_scale_factor__lte=config['rain_scale_factor'][1]))

    if config['interior_climate']:
        filtered_entries = filtered_entries.filter(sample_data__interior_climate=config['interior_climate'])

    if config['interior_heat_transfer_coefficient']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__interior_heat_transfer_coefficient__gte=config['interior_heat_transfer_coefficient'][0])
            & Q(sample_data__interior_heat_transfer_coefficient__lte=config['interior_heat_transfer_coefficient'][1]))

    if config['interior_moisture_transfer_coefficient']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__interior_moisture_transfer_coefficient__gte=config['interior_moisture_transfer_coefficient'][
                0])
            & Q(sample_data__interior_moisture_transfer_coefficient__lte=
                config['interior_moisture_transfer_coefficient'][1]))

    if config['interior_sd_value']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__interior_sd_value__gte=config['interior_sd_value'][0])
            & Q(sample_data__interior_sd_valuen__lte=config['interior_sd_value'][1]))

    if config['wall_orientation']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__wall_orientation__gte=config['wall_orientation'][0])
            & Q(sample_data__wall_orientation__lte=config['wall_orientation'][1]))

    if config['wall_core_width']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__wall_core_width__gte=config['wall_core_width'][0])
            & Q(sample_data__wall_core_width__lte=config['wall_core_width'][1]))

    if config['wall_core_material']:
        filtered_entries = filtered_entries.filter(sample_data__wall_core_material__all=config['wall_core_material'])

    if config['plaster_width']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__plaster_width__gte=config['plaster_width'][0])
            & Q(sample_data__plaster_width__lte=config['plaster_width'][1]))

    if config['plaster_material']:
        filtered_entries = filtered_entries.filter(sample_data__plaster_material__all=config['plaster_material'])

    if config['start_year']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__start_year__gte=config['start_year'][0])
            & Q(sample_data__start_year__lte=config['start_year'][1]))

    if config['exterior_plaster']:
        filtered_entries = filtered_entries.filter(
            sample_data__design_option__exterior_plaster=config['exterior_plaster'])

    if config['system_name']:
        filtered_entries = filtered_entries.filter(sample_data__design_option__system_name__all=config['system_name'])

    if config['insulation_material']:
        filtered_entries = filtered_entries.filter(
            sample_data__design_option__insulation_material__all=config['insulation_material'])

    if config['finish_material']:
        filtered_entries = filtered_entries.filter(
            sample_data__design_option__finish_material__all=config['finish_material'])

    if config['detail_material']:
        filtered_entries = filtered_entries.filter(
            sample_data__design_option__detail_material__all=config['detail_material'])

    if config['insulation_thickness']:
        filtered_entries = filtered_entries.filter(
            Q(sample_data__design_option__insulation_thickness__gte=config['insulation_thickness'][0])
            & Q(sample_data__design_option__insulation_thickness__lte=config['insulation_thickness'][1]))

    logger.info(f'{filtered_entries.count()} found based on given query')
    return filtered_entries


def compute_cdf(delphin_docs: list, quantity: str):
    quantities = [doc.result_processed.thresholds[quantity] for doc in delphin_docs]
    hist, edges = np.histogram(quantities, density=True)
    dx = edges[1] - edges[0]
    cdf = np.cumsum(hist) * dx

    plt.figure()
    plt.plot(edges[1:], cdf)
    plt.show()
