__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import datetime

# RiBuild Modules
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_set_simulated():
    assert True


def test_set_simulation_time(db_one_project):
    delphin_doc = delphin_entry.Delphin.objects().first()

    sim_time = datetime.timedelta(minutes=10)
    simulation_interactions.set_simulation_time(delphin_doc.id, sim_time)

    delphin_doc.reload()
    assert delphin_doc.simulation_time == sim_time.total_seconds()


def test_clean_simulation_folder():
    assert True
