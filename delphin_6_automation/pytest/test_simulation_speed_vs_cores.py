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
from delphin_6_automation.delphin_setup import weather_modeling

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.fixture(params=[2, 4, 6, 8, 12, 16, 20, 24])
def mock_submit_file(monkeypatch, request):

    def mock_return(sim_id: str, simulation_folder: str, restart=False):
        """Create a submit file for the DTU HPC queue system."""

        delphin_path = '~/Delphin-6.0/bin/DelphinSolver'
        computation_time = 15
        cpus = request.param
        ram_per_cpu = '7MB'
        submit_file = f'submit_{sim_id}.sh'

        file = open(f"{simulation_folder}/{submit_file}", 'w', newline='\n')
        file.write("#!/bin/bash\n")
        file.write("#BSUB -J DelphinJob\n")
        file.write("#BSUB -o DelphinJob_%J.out\n")
        file.write("#BSUB -e DelphinJob_%J.err\n")
        file.write("#BSUB -q hpc\n")
        file.write(f"#BSUB -W {computation_time}\n")
        file.write(f'#BSUB -R "rusage[mem={ram_per_cpu}] span[hosts=1]"\n')
        file.write(f"#BSUB -n {cpus}\n")
        file.write(f"#BSUB -N\n")
        file.write('\n')
        file.write(f"export OMP_NUM_THREADS=$LSB_DJOB_NUMPROC\n")
        file.write('\n')

        if not restart:
            file.write(f"{delphin_path} {sim_id}.d6p\n")
        else:
            file.write(f"{delphin_path} --restart {sim_id}.d6p\n")

        file.write('\n')
        file.close()

        return submit_file, computation_time

    monkeypatch.setattr(simulation_worker, 'create_submit_file', mock_return)


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


@pytest.mark.skipif(platform.system() == 'Linux', reason='Test should only run locally')
def test_speed_vs_cores(mock_driving_rain, mock_wait_until_finished, mock_submit_file, db_one_project):

    db_one_project = str(db_one_project)
    folder = 'H:/ribuild'
    simulation_folder = os.path.join(folder, db_one_project)
    os.mkdir(simulation_folder)
    delphin_interactions.change_entry_simulation_length(db_one_project, 1, 'a')
    general_interactions.download_full_project_from_database(db_one_project, simulation_folder)
    submit_file, estimated_time = simulation_worker.create_submit_file(db_one_project, simulation_folder)
    simulation_worker.submit_job(submit_file, db_one_project)

    time_0 = datetime.datetime.now()
    simulation_worker.wait_until_finished(db_one_project, estimated_time, simulation_folder)
    delta_time = datetime.datetime.now() - time_0

    with open(os.path.join(folder, 'time.txt'), 'a') as out:
        out.write(str(delta_time.total_seconds())+'\n')
