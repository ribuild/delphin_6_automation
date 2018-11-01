__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from bson.objectid import ObjectId

# RiBuild Modules
from delphin_6_automation.sampling import sim_time_prediction
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions.db_templates import time_model_entry
from delphin_6_automation.database_interactions.db_templates import delphin_entry


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
    assert isinstance(y_data, pd.Series)
    assert y_data.name == 'time'
    assert (x_data.columns != 'time').all()
    assert {'bool', 'int64', 'float64'} == {str(x) for x in set(x_data.dtypes)}


def test_transform_interior_climate(time_prediction_data):
    data = sim_time_prediction.transform_interior_climate(time_prediction_data)

    assert {0.0, 1.0} >= set(data.loc[:, 'interior_climate'])


def test_transform_weather(time_prediction_data):
    time_prediction_data = time_prediction_data.fillna(0.0)
    data = sim_time_prediction.transform_weather(time_prediction_data)

    assert data is not None
    assert isinstance(data, pd.DataFrame)
    assert (data.columns == time_prediction_data.columns).all()
    assert data.shape == time_prediction_data.shape
    assert data.loc[:, 'exterior_climate'].dtype == 'int64'


def test_transform_system_names(time_prediction_data):
    time_prediction_data = time_prediction_data.fillna(0.0)
    data = sim_time_prediction.transform_system_names(time_prediction_data)

    assert data is not None
    assert isinstance(data, pd.DataFrame)
    assert (data.columns == time_prediction_data.columns).all()
    assert data.shape == time_prediction_data.shape
    assert data.loc[:, 'system_name'].dtype == 'int64'


def test_compute_model(time_prediction_data):
    x_data, y_data = sim_time_prediction.process_time_data(time_prediction_data)
    model, model_data = sim_time_prediction.compute_model(x_data, y_data)

    assert isinstance(model, KNeighborsRegressor)
    assert isinstance(model_data, dict)
    assert set(model_data.keys()) == {'score', 'parameters', 'features'}


def test_upload_model(add_sampling_strategy):
    strategy_doc = sample_entry.Strategy.objects(id=add_sampling_strategy).first()
    model = KNeighborsRegressor()
    model_data = {'score': 0.9, 'parameters': [1, 'uniform'], 'features': ['test1', 'test2']}
    sim_time_prediction.upload_model(model, model_data, strategy_doc)

    model_entry = time_model_entry.TimeModel.objects().first()
    assert model_entry
    assert model_entry.model
    assert model_entry.test_score == model_data['score']
    assert model_entry.model_parameters == model_data['parameters']
    assert model_entry.model_features == model_data['features']

    strategy_doc.reload()
    model_data1 = {'score': 0.8, 'parameters': [3, 'distance'], 'features': ['test3', 'test4']}
    sim_time_prediction.upload_model(model, model_data1, strategy_doc)
    model_entry.reload()

    assert model_entry
    assert model_entry.model
    assert model_entry.test_score == model_data1['score']
    assert model_entry.model_parameters == model_data1['parameters']
    assert model_entry.model_features == model_data1['features']


def test_create_upload_time_prediction_model(add_delphin_for_time_estimation, add_sampling_strategy):
    strategy_doc = sample_entry.Strategy.objects().first()
    model_id = sim_time_prediction.create_upload_time_prediction_model(strategy_doc)

    assert isinstance(model_id, ObjectId)
    assert time_model_entry.TimeModel.objects(id=model_id)


def test_process_inputs(create_time_model):
    delphin_doc = delphin_entry.Delphin.objects().first()
    inputs = delphin_doc.sample_data
    model = time_model_entry.TimeModel.objects().first()
    model_data = model.model_features
    processed_input = sim_time_prediction.process_inputs(inputs, model_data)

    assert not processed_input.empty
    assert isinstance(processed_input, pd.DataFrame)


def test_simulation_time_prediction_ml(create_time_model):
    delphin_doc = delphin_entry.Delphin.objects().first()
    model = time_model_entry.TimeModel.objects().first()
    time = sim_time_prediction.simulation_time_prediction_ml(delphin_doc, model)

    assert time == 10


def test_queue_priorities_on_time_prediction(delphin_with_estimated_time):
    sample_doc = sample_entry.Sample.objects().first()
    sim_time_prediction.queue_priorities_on_time_prediction(sample_doc)

    assert all([0.0 <= num <= 1.0 for num in [doc.queue_priority for doc in sample_doc.delphin_docs]])
