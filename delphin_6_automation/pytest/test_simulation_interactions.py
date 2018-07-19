__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import datetime
import os

# RiBuild Modules
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_set_simulating(db_one_project):
    delphin_doc = delphin_entry.Delphin.objects().first()

    assert not delphin_doc.simulating

    simulation_interactions.set_simulating(delphin_doc.id, True)
    delphin_doc.reload()
    assert delphin_doc.simulating

    simulation_interactions.set_simulating(delphin_doc.id, False)
    delphin_doc.reload()
    assert not delphin_doc.simulating


def test_set_simulated(db_one_project):
    delphin_doc = delphin_entry.Delphin.objects().first()

    simulation_interactions.set_simulated(delphin_doc.id)
    delphin_doc.reload()

    assert delphin_doc.simulated
    assert isinstance(delphin_doc.simulated, datetime.datetime)
    assert not delphin_doc.simulating


def test_set_simulation_time(db_one_project):
    delphin_doc = delphin_entry.Delphin.objects().first()

    sim_time = datetime.timedelta(minutes=10)
    simulation_interactions.set_simulation_time(delphin_doc.id, sim_time)

    delphin_doc.reload()
    assert delphin_doc.simulation_time == sim_time.total_seconds()


def test_clean_simulation_folder(tmpdir):

    folder1 = tmpdir.mkdir('test')
    folder2 = folder1.mkdir('test2')
    folder3 = folder2.mkdir('test3')

    simulation_interactions.clean_simulation_folder(folder1)

    assert not os.path.exists(folder1)
    assert not os.path.exists(folder2)
    assert not os.path.exists(folder3)
