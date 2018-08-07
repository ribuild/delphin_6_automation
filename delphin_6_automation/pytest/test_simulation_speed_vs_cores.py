__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest
import datetime
import os
import platform

# RiBuild Modules
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.backend import simulation_worker
from delphin_6_automation.database_interactions import delphin_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.mark.skipif(platform.system() == 'Linux', reason='Test should only run locally')
@pytest.mark.parametrize('cores', [4, 8, 12, 16, 20, 24])
def test_speed_vs_cores(cores, db_one_project, tmpdir):

    db_one_project = str(db_one_project)
    folder = 'H:/ribuild'
    simulation_folder = os.path.join(folder, db_one_project)
    delphin_interactions.change_entry_simulation_length(db_one_project, 10, 'd')
    general_interactions.download_full_project_from_database(db_one_project, folder)
    submit_file, estimated_time = simulation_worker.create_submit_file(db_one_project, simulation_folder)
    simulation_worker.submit_job(submit_file, db_one_project)

    time_0 = datetime.datetime.now()
    simulation_worker.wait_until_finished(db_one_project, estimated_time, simulation_folder)
    delta_time = datetime.datetime.now() - time_0

    with open(os.path.join(tmpdir, 'time.txt'), 'a') as out:
        out.write(str(delta_time.total_seconds()))
