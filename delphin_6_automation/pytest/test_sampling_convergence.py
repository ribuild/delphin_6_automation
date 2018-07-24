__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import pytest
import numpy as np

# RiBuild Modules
from delphin_6_automation.sampling import sampling
from delphin_6_automation.database_interactions import sampling_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.fixture(params=[5, 15])
def add_mock_strategy(empty_database):
    sampling_settings = {'initial samples per set': 1,
                         'add samples per run': 1,
                         'max samples': 500,
                         'sequence': 10,
                         'standard error threshold': 0.1}
    distributions = {str(i): 'test distribution'
                     for i in range(request.params)}
    strategy = {'design': 'Test Design', 'scenario': 'Test Scenario',
     'distributions': distributions, 'settings': sampling_settings}
    strategy_id = sampling_interactions.upload_sampling_strategy(strategy)

    return strategy_id


@pytest.fixture()
def mock_sampling_distribution(monkeypatch):

    def mockreturn(sampling_strategy, samples_raw, used_samples_per_set):

        new_samples_per_set = sampling_strategy['settings']['initial samples per set']
        samples_raw = samples_raw[used_samples_per_set:used_samples_per_set + new_samples_per_set, :]

        return samples_raw

    monkeypatch.setattr(sampling, 'compute_sampling_distributions', mockreturn)


@pytest.fixture()
def mock_create_delphin(monkeypatch):
    def mockreturn(sampling_strategy: dict, samples: dict):

        return [None, None]

    monkeypatch.setattr(sampling, 'create_delphin_projects', mockreturn)


@pytest.fixture()
def mock_add_delphin_to_sample(monkeypatch):

    def mockreturn(sampling_id: str, delphin_ids: list):

        return None

    monkeypatch.setattr(sampling_interactions, 'add_delphin_to_sampling', mockreturn)


@pytest.fixture()
def mock_wait_until_finished(monkeypatch):
    pass


@pytest.fixture()
def mock_sampling_worker(add_mock_strategy, mock_sampling_distribution, mock_create_delphin,
                         mock_add_delphin_to_sample, mock_wait_until_finished):
    pass


def test_function_one():


    assert True