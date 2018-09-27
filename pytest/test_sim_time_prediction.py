__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
try:
    from delphin_6_automation.database_interactions.auth import auth_dict
except ImportError:
    pass
from delphin_6_automation.sampling import sim_time_prediction

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.mark.skip('Only local run')
def try_create_time_prediction_model():
    server = mongo_setup.global_init(auth_dict)

    sim_time_prediction.create_time_prediction_model()

    mongo_setup.global_end_ssh(server)


#try_create_time_prediction_model()
