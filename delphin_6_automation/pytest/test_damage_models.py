__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
#from delphin_6_automation.database_interactions import mongo_setup
#from delphin_6_automation.database_interactions import auth
from delphin_6_automation.delphin_setup import damage_models
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import simulation_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_u_value(uvalue_data):

    u_value = damage_models.u_value(*uvalue_data)

    assert isinstance(u_value, float)
    assert 0.0 < u_value < 1.0
