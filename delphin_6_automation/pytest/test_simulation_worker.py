__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest
import datetime

# RiBuild Modules
from delphin_6_automation.backend import simulation_worker
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import simulation_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_create_submit_file(tmpdir):

    assert True


def test_submit_job():
    assert True


def test_wait_until_finished():
    assert True


def test_hpc_worker():
    assert True

@pytest.mark.parametrize('sim_time',
                         [False, True])
def test_get_average_computation_time(db_one_project, sim_time):

    delphin_id = delphin_entry.Delphin.objects().first().id
    if sim_time:
        delta_time = datetime.timedelta(minutes=3)
        simulation_interactions.set_simulation_time(delphin_id, delta_time)

    computation_time = simulation_worker.get_average_computation_time(delphin_id)

    assert computation_time
    assert isinstance(computation_time, int)

    if sim_time:
        assert computation_time == 3
    else:
        assert computation_time == 15
