__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import numpy as np
import os

# RiBuild Modules
from delphin_6_automation.delphin_setup import damage_models


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_u_value(uvalue_data):
    u_value = damage_models.u_value(*uvalue_data)

    assert isinstance(u_value, float)
    assert 0.0 < u_value < 1.0


def test_algea_model():
    folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\pytest\test_files\damage_models\algae'
    temperature_file = os.path.join(folder, 'temperature.txt')
    relative_humidity_file = os.path.join(folder, 'rh.txt')
    covered_file = os.path.join(folder, 'covered_result.txt')

    expected_result = np.loadtxt(covered_file)
    temperature = np.loadtxt(temperature_file)
    relative_humidity = np.loadtxt(relative_humidity_file)

    porosity = 0.25
    roughness = 2.95
    total_pore_area = 2.22

    algea = damage_models.algae(relative_humidity, temperature, 'brick', porosity, roughness, total_pore_area)

    assert all(algea[1:366] == expected_result)
