__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest
import pandas as pd

# RiBuild Modules
from delphin_6_automation.sampling import sim_time_prediction


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_get_time_prediction_data(add_delphin_for_time_estimation):
    df = sim_time_prediction.get_time_prediction_data()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['time', 'exterior_climate', 'interior_climate',
                                'exterior_plaster', 'system_name', 'insulation_material', 'finish_material',
                                'detail_material', 'insulation_thickness']


def test_process_time_data(time_prediction_data):
    x_data, y_data = sim_time_prediction.process_time_data(time_prediction_data)

    assert isinstance(x_data, pd.DataFrame)
    assert isinstance(y_data, pd.DataFrame)


def test_transform_interior_climate(time_prediction_data):
    data = sim_time_prediction.transform_interior_climate(time_prediction_data)

    assert {0.0, 1.0} >= set(data.loc[:, 'interior_climate'])


def test_transform_weather(time_prediction_data):
    assert True


def test_transform_system_names(time_prediction_data):
    data = sim_time_prediction.transform_system_names(time_prediction_data)
    assert data


def test_compute_model():
    assert True


def test_remove_bad_features():
    assert True


def test_create_time_prediction_model():
    assert True


def test_upload_model():
    assert True


def test_process_inputs():
    assert True


def test_simulation_time_prediction_ml():
    assert True
