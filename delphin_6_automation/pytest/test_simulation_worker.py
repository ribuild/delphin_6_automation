__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest
import datetime
import os
import time
import shutil

# RiBuild Modules
from delphin_6_automation.backend import simulation_worker
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import simulation_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.mark.parametrize('restart',
                         [False, True])
def test_create_submit_file(tmpdir, db_one_project, restart):

    folder = tmpdir.mkdir('test')
    delphin_id = delphin_entry.Delphin.objects().first().id

    expected_submit_file = ["#!/bin/bash\n", "#BSUB -J DelphinJob\n", "#BSUB -o DelphinJob_%J.out\n",
                            "#BSUB -e DelphinJob_%J.err\n", "#BSUB -q hpc\n", "#BSUB -W 15\n",
                            '#BSUB -R "rusage[mem=3MB] span[hosts=1]"\n', "#BSUB -n 24\n", "#BSUB -N\n",
                            '\n', "export OMP_NUM_THREADS=$LSB_DJOB_NUMPROC\n", '\n',
                            f"~/Delphin-6.0/bin/DelphinSolver {delphin_id}.d6p\n", '\n']

    expected_restart = f"~/Delphin-6.0/bin/DelphinSolver --restart {delphin_id}.d6p\n"
    submit_file, _ = simulation_worker.create_submit_file(delphin_id, folder, restart)

    assert submit_file
    assert submit_file == f'submit_{delphin_id}.sh'
    assert os.path.exists(os.path.join(folder, submit_file))

    with open(os.path.join(folder, submit_file), 'r') as file:
        submit_data = file.readlines()

    if not restart:
        assert submit_data == expected_submit_file

    else:
        expected_submit_file[-2] = expected_restart
        assert submit_data == expected_submit_file


def test_submit_job():
    assert True


def test_wait_until_finished():
    assert True


def test_hpc_worker(tmpdir, db_one_project, mock_submit_job, monkeypatch, test_folder):
    folder = tmpdir.mkdir('test')
    delphin_doc = delphin_entry.Delphin.objects().first()

    def mockreturn(sim_id, estimated_run_time, simulation_folder):
        result_zip = test_folder + '/raw_results/delphin_results1.zip'
        delphin_folder = os.path.join(folder, str(delphin_doc.id))
        shutil.unpack_archive(result_zip, delphin_folder)
        os.rename(os.path.join(delphin_folder, 'delphin_id'), os.path.join(delphin_folder, str(delphin_doc.id)))

        time.sleep(2)
        return None

    monkeypatch.setattr(simulation_worker, 'wait_until_finished', mockreturn)

    simulation_worker.hpc_worker(str(delphin_doc.id), 'Test_Thread', folder)

    delphin_doc.reload()

    assert not os.path.exists(os.path.join(folder, str(delphin_doc.id)))
    assert delphin_doc.results_raw
    assert delphin_doc.result_processed
    assert delphin_doc.simulated
    assert delphin_doc.simulation_time


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


def test_simulation_worker(mock_hpc_worker, mock_find_next_sim_in_queue, capsys):

    with pytest.raises(SystemExit) as exc_info:
        simulation_worker.simulation_worker('hpc', 'Test_Thread')
        out, err = capsys.readouterr()
        assert out == 'hpc called\n'
        assert 'None' in str(exc_info.value)


def test_simulation_worker_exception(db_one_project, mock_hpc_worker_exception, mock_sleep_exception, ):

    with pytest.raises(SystemExit) as exc_info:
        simulation_worker.simulation_worker('hpc', 'Test_Thread')

        delphin_doc = delphin_entry.Delphin.objects().first()
        assert 'None' in str(exc_info.value)
        assert not delphin_doc.simulating
