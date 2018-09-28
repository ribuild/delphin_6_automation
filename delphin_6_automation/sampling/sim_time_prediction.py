__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import copy
import pandas as pd
import numpy as np
import typing
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsRegressor
import pickle
from bson import Binary

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def get_time_prediction_data() -> pd.DataFrame:
    entries = delphin_entry.Delphin.objects(simulation_time__exists=True)

    col = ['time', ] + list(entries[0].sample_data.keys())[:-1] + list(entries[0].sample_data['design_option'].keys())
    frames = []

    for i in range(len(entries)):
        entry = entries[i]
        data = copy.deepcopy(entry.sample_data)
        del data['sequence']
        del data['design_option']
        data.update(entry.sample_data['design_option'])
        data['time'] = entry.simulation_time

        frames.append(pd.DataFrame(columns=col, data=data, index=[i, ]))

    data_frame = pd.concat(frames)

    return data_frame


def process_time_data(data_frame: pd.DataFrame) -> typing.Tuple[pd.DataFrame, pd.DataFrame]:
    y_data = data_frame['time']

    x_data = data_frame.loc[:, data_frame.columns != 'time']
    x_data = transform_weather(x_data)
    x_data = x_data.fillna(0.0)
    x_data = transform_interior_climate(x_data)
    x_data = transform_system_names(x_data)

    return x_data, y_data


def transform_interior_climate(data: pd.DataFrame) -> pd.DataFrame:
    data.loc[data.loc[:, 'interior_climate'] == 'a', 'interior_climate'] = 0.0
    data.loc[data.loc[:, 'interior_climate'] == 'b', 'interior_climate'] = 1.0

    return data


def transform_weather(data: pd.DataFrame) -> pd.DataFrame:
    data.loc[:, 'exterior_climate'] = np.ones(len(data['exterior_climate']))

    return data


def transform_system_names(data: pd.DataFrame) -> pd.DataFrame:
    data.loc[data.loc[:, 'system_name'] == 'ClimateBoard', 'system_name'] = 1.0

    return data


def compute_model(x_data: pd.DataFrame, y_data: pd.DataFrame):
    ss = ShuffleSplit(n_splits=5, test_size=0.25, random_state=47)
    scaler = MinMaxScaler()
    best_model = {'score': 0, 'features': [1, 'uniform']}

    for nn in [3, 5, 7, 9]:
        for weight in ['uniform', 'distance']:
            knn_reg = KNeighborsRegressor(n_neighbors=nn, weights=weight)
            scores = cross_val_score(knn_reg, scaler.fit_transform(x_data), y_data, cv=ss)
            scores = remove_bad_features(x_data, y_data, scores, knn_reg, scaler, ss)

            if scores.mean() > best_model['score']:
                best_model['score'] = scores.mean()
                best_model['features'] = [nn, weight]
                logger.debug(f'Update best model to: {best_model["features"]} with score: {best_model["score"]}')

    logger.info(f'KNN with {best_model["features"][0]} neighbors and {best_model["features"][1]} weight is the best '
                f'model with R2 of {best_model["score"]:.5f}')

    return KNeighborsRegressor(n_neighbors=best_model['features'][0], weights=best_model['features'][1])


def remove_bad_features(x_data, y_data, basis_score, knn, scaler, shufflesplit) -> np.ndarray:
    features = x_data.columns

    col_del = []
    feature_scores = []
    for feat in features:
        feature_less_data = x_data.loc[:, x_data.columns != feat]
        test_scores = cross_val_score(knn, scaler.fit_transform(feature_less_data), y_data,
                                      cv=shufflesplit, scoring='r2')
        feature_scores.append((feat, test_scores.mean()))
        if test_scores.mean() >= basis_score.mean():
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


def upload_model(model: KNeighborsRegressor, sample_strategy: sample_entry.Strategy):
    pickled_model = pickle.dumps(model)

    sample_strategy.update(set__time_prediction_model=Binary(pickled_model))
    logger.info(f'Updated time prediction model for Sample Strategy with ID {sample_strategy.id}')
