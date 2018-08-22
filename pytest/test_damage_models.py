__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.delphin_setup import damage_models

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_u_value(uvalue_data):

    u_value = damage_models.u_value(*uvalue_data)

    assert isinstance(u_value, float)
    assert 0.0 < u_value < 1.0
