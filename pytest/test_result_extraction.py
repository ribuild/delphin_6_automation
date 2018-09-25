__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.backend import result_extraction

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.mark.skip('Only local run')
def test_filter_db():
    server = mongo_setup.global_init(auth_dict)

    config_dict = {'exterior_climate': 'KobenhavnTaastrup',
                   'exterior_heat_transfer_coefficient_slope': None,
                   'exterior_moisture_transfer_coefficient': None,
                   'solar_absorption': None,
                   'rain_scale_factor': None,
                   'interior_climate': None,
                   'interior_heat_transfer_coefficient': None,
                   'interior_moisture_transfer_coefficient': None,
                   'interior_sd_value': None,
                   'wall_orientation': None,
                   'wall_core_width': None,
                   'wall_core_material': None,
                   'plaster_width': None,
                   'plaster_material': None,
                   'start_year': None,

                   'exterior_plaster': None,
                   'system_name': ['ClimateBoard', ],
                   'insulation_material': None,
                   'finish_material': None,
                   'detail_material': None,
                   'insulation_thickness': [35, 100]}

    delphin_docs = result_extraction.filter_db(config_dict)
    result_extraction.compute_cdf(delphin_docs, 'heat_loss')
    mongo_setup.global_end_ssh(server)
