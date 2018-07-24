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


@pytest.fixture()
def add_mock_strategy(empty_database, monkeypatching):
    pass


@pytest.fixture()
def mock_sampling_distribution(monkeypathcing):
    pass


@pytest.fixture()
def mock_create_delphin(monkeypatching):
    pass


@pytest.fixture()
def mock_add_delphin_to_sample():
    pass


@pytest.fixture()
def mock_wait_until_finished(monkeypatching):
    pass


@pytest.fixture()
def mock_sampling_worker(add_mock_strategy, mock_sampling_distribution, mock_create_delphin,
                         mock_add_delphin_to_sample, mock_wait_until_finished):
    pass


def test_function_one():


    assert True