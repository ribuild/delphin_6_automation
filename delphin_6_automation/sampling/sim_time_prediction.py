__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import copy
import pandas as pd
import numpy as np
import typing
from sklearn.model_selection import ShuffleSplit, cross_val_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsRegressor
import pickle
from bson import Binary

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions.db_templates import time_model_entry

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def get_time_prediction_data() -> pd.DataFrame:
    entries = delphin_entry.Delphin.objects(simulation_time__exists=True)

    col = ['time', ] + list(entries[0].sample_data.keys()) + list(entries[0].sample_data['design_option'].keys())
    frames = []

    for i in range(len(entries)):
        entry = entries[i]
        data = copy.deepcopy(entry.sample_data)
        data.update(entry.sample_data['design_option'])
        data['time'] = entry.simulation_time

        frames.append(pd.DataFrame(columns=col, data=data, index=[i, ]))

    data_frame = pd.concat(frames)
    data_frame = data_frame.loc[:, data_frame.columns != 'design_option']
    data_frame = data_frame.loc[:, data_frame.columns != 'sequence']

    return data_frame


def process_time_data(data_frame: pd.DataFrame) -> typing.Tuple[pd.DataFrame, pd.Series]:
    y_data = data_frame['time']

    x_data = data_frame.loc[:, data_frame.columns != 'time']
    x_data = x_data.fillna(0.0)
    x_data = transform_weather(x_data)
    x_data = transform_interior_climate(x_data)
    x_data = transform_system_names(x_data)

    return x_data, y_data


def transform_interior_climate(data: pd.DataFrame) -> pd.DataFrame:
    data.loc[data.loc[:, 'interior_climate'] == 'a', 'interior_climate'] = 0.0
    data.loc[data.loc[:, 'interior_climate'] == 'b', 'interior_climate'] = 1.0

    return data


def transform_weather(data: pd.DataFrame) -> pd.DataFrame:
    sys_names = set(data.loc[:, 'exterior_climate'])

    mapper = {}
    for i, name in enumerate(sys_names):
        mapper[name] = i

    data.loc[:, 'exterior_climate'] = data.loc[:, 'exterior_climate'].map(mapper)

    return data


def transform_system_names(data: pd.DataFrame) -> pd.DataFrame:
    sys_names = set(data.loc[data.loc[:, 'system_name'] != 0, 'system_name'])

    mapper = {0: 0}
    for i, name in enumerate(sys_names, 1):
        mapper[name] = i

    data.loc[:, 'system_name'] = data.loc[:, 'system_name'].map(mapper)

    return data


def compute_model(x_data: pd.DataFrame, y_data: pd.Series):
    ss = ShuffleSplit(n_splits=5, test_size=0.25, random_state=47)
    scaler = MinMaxScaler()
    best_model = {'score': 0, 'parameters': [1, 'uniform']}

    for nn in [3, 5, 7, 9]:
        for weight in ['uniform', 'distance']:
            knn_reg = KNeighborsRegressor(n_neighbors=nn, weights=weight)
            scores = cross_val_score(knn_reg, scaler.fit_transform(x_data), y_data, cv=ss)
            scores = remove_bad_features(x_data, y_data, scores, knn_reg, scaler, ss)

            if scores.mean() > best_model['score']:
                best_model['score'] = scores.mean()
                best_model['parameters'] = [nn, weight]
                logger.debug(f'Update best model to: {best_model["parameters"]} with score: {best_model["score"]}')

    logger.info(f'KNN with {best_model["parameters"][0]} neighbors and {best_model["parameters"][1]} weight is the '
                f'best model with R2 of {best_model["score"]:.5f}')

    return KNeighborsRegressor(n_neighbors=best_model['parameters'][0], weights=best_model['parameters'][1])


def remove_bad_features(x_data, y_data, basis_score, knn, scaler, shufflesplit) -> np.ndarray:
    features = x_data.columns

    col_del = []
    feature_scores = []
    for feat in features:
        feature_less_data = x_data.loc[:, x_data.columns != feat]
        test_scores = cross_val_score(knn, scaler.fit_transform(feature_less_data), y_data,
                                      cv=shufflesplit, scoring='r2')
        feature_scores.append((feat, test_scores.mean()))
        if test_scores.mean() > basis_score.mean():
            col_del.append(feat)

    logger.debug(f'Columns to delete: {col_del}')

    clean_col = x_data.columns[[c not in col_del
                                for c in x_data.columns.tolist()]]
    cleaned_data = x_data.loc[:, clean_col]
    clean_scores = cross_val_score(knn, scaler.fit_transform(cleaned_data), y_data, cv=shufflesplit, scoring='r2')

    return clean_scores


def create_time_prediction_model() -> KNeighborsRegressor:

    simulation_data = get_time_prediction_data()
    x_data, y_data = process_time_data(simulation_data)

    return compute_model(x_data, y_data)


def upload_model(model: KNeighborsRegressor, model_data: dict, sample_strategy: sample_entry.Strategy):

    time_model_doc = sample_strategy.time_prediction_model
    pickled_model = pickle.dumps(model)

    if time_model_doc:
        time_model_doc.update(set__model=Binary(pickled_model))
        time_model_doc.update(set__test_score=model_data['score'])
        time_model_doc.update(set__model_parameters=model_data['parameters'])
        time_model_doc.update(set__model_features=model_data['features'])
    else:
        time_model_doc = time_model_entry.TimeModel()
        time_model_doc.model = Binary(pickled_model)
        time_model_doc.test_score = model_data['score']
        time_model_doc.model_parameters = model_data['parameters']
        time_model_doc.model_features = model_data['features']
        time_model_doc.sample_strategy = sample_strategy
        time_model_doc.save()

        sample_strategy.update(set__time_prediction_model=time_model_doc)

    logger.info(f'Updated time prediction model with ID {time_model_doc.id} for Sample Strategy with ID '
                f'{sample_strategy.id}')


def process_inputs(raw_inputs, model_features):

    data = {'time': None}
    for key in raw_inputs.ekys():
        if key in model_features:
            data[key] = raw_inputs[key]

    df = pd.DataFrame(data)

    return process_time_data(df)[0]


def simulation_time_prediction_ml(delphin_doc: delphin_entry.Delphin, model_entry: time_model_entry.TimeModel) -> int:

    time_model = pickle.loads(model_entry.model)
    inputs = process_inputs(delphin_doc.sample_data, model_entry.model_features)
    sim_time_secs = time_model.predict(inputs)

    return sim_time_secs / 60
