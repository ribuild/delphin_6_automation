__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest
import datetime
import os

# RiBuild Modules
from delphin_6_automation.backend import simulation_worker
from delphin_6_automation.delphin_setup import weather_modeling

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.fixture()
def mock_wait_until_finished(monkeypatch):

    def mock_return(sim_id: str, estimated_run_time: int, simulation_folder: str):
        finished = False
        start_time = None

        while not start_time:
            if os.path.exists(f"{simulation_folder}/{sim_id}"):
                start_time = datetime.datetime.now()

        while not finished:

            if os.path.exists(f"{simulation_folder}/{sim_id}/log/summary.txt"):
                finished = True

    monkeypatch.setattr(simulation_worker, 'wait_until_finished', mock_return)


@pytest.fixture()
def mock_driving_rain(monkeypatch):

    def mock_return(precipitation: list, wind_direction: list, wind_speed: list, wall_location: dict,
                 orientation, inclination=90, catch_ratio=None):
        return [0.0 for _ in range(len(precipitation))]

    monkeypatch.setattr(weather_modeling, 'driving_rain', mock_return)