__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import pytest
import numpy as np
from matplotlib import pyplot as plt
import platform
from scipy import stats

# RiBuild Modules
from delphin_6_automation.sampling import sampling
from delphin_6_automation.database_interactions import sampling_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.backend import sampling_worker
from delphin_6_automation.file_parsing import delphin_parser


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.fixture(params=[5, ], ids=['5 dimensions '])
def add_mock_strategy(empty_database, request):
    sampling_settings = {'initial samples per set': 1,
                         'add samples per run': 1,
                         'max samples': 500,
                         'sequence': 10,
                         'standard error threshold': 0.05,
                         'raw sample size': 2 ** 9}
    distributions = {str(i): 'test distribution'
                     for i in range(request.param)}
    strategy = {'design': {'Test Design': ''}, 'scenario': {'Test Scenario': ''},
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
def mock_create_delphin(monkeypatch, delphin_file_path, add_two_materials):
    def mockreturn(sampling_strategy: dict, samples: dict):
        delphin_ids = []
        for sequence in samples.keys():
            delphin_id = delphin_interactions.upload_delphin_dict_to_database(
                delphin_parser.dp6_to_dict(delphin_file_path),
                1)
            delphin_interactions.add_sampling_dict(delphin_id, {'input': samples[sequence][0].tolist(),
                                                                'output': None})

            delphin_ids.append(delphin_id)

        return delphin_ids

    monkeypatch.setattr(sampling, 'create_delphin_projects', mockreturn)


def sobol_test_function1(array: np.ndarray) -> np.ndarray:
    return np.prod(1 + (array ** 2 - array - 1 / 6))


def sobol_test_function2(array: np.ndarray) -> np.ndarray:
    return np.prod(1 + (array ** 6 - 3 * array ** 5 + 5 / 2 * array ** 4 - 1 / 2 * array ** 2 + 1 / 42))


@pytest.fixture(params=[1, 2], ids=[' 2nd Bernoulli', ' 6th Bernoulli'])
def mock_wait_until_finished(monkeypatch, request):
    def mock_return(delphin_ids):
        for delphin_id in delphin_ids:
            delphin_doc = delphin_entry.Delphin.objects(id=delphin_id).first()
            input_array = np.array(delphin_doc.sample_data['input'])

            if request.param == 1:
                output_array = sobol_test_function1(input_array)
            elif request.param == 2:
                output_array = sobol_test_function2(input_array)

            delphin_doc.update(set__sample_data__output=float(output_array))

    monkeypatch.setattr(simulation_interactions, 'wait_until_simulated', mock_return)


@pytest.fixture()
def mock_calculate_error(monkeypatch):
    def mock_return(sample_strategy):
        input_list = []
        output_list = []
        delphin_docs = delphin_entry.Delphin.objects()

        for delphin in delphin_docs:
            # input_list.append(delphin.sample_data['input'])
            output_list.append(delphin.sample_data['output'])

        # input_list = np.asarray(input_list)
        # output_list = np.asarray(output_list)
        # output_list = np.tile(output_list, (input_list.shape[1], 1)).T
        # integrated_value = np.nansum(integrate.simps(output_list, input_list))
        # return np.abs(1.0 - integrated_value)
        return sampling.relative_standard_error(output_list, sample_strategy['settings']['sequence'])

    monkeypatch.setattr(sampling, 'calculate_error', mock_return)


@pytest.fixture()
def mock_upload_error(monkeypatch):
    def mock_return(strategy_document: sample_entry.Strategy, sampling_id: str, current_error):
        sampling_document = sample_entry.Sample.objects(id=sampling_id).first()
        sampling_document.update(set__standard_error__mould=current_error)
        strategy_document.update(push__standard_error__mould=current_error)

    monkeypatch.setattr(sampling_interactions, 'upload_standard_error', mock_return)


@pytest.fixture()
def mock_check_convergence(monkeypatch):
    def mock_return(strategy_document: sample_entry.Strategy):
        strategy_document.reload()
        if strategy_document.standard_error['mould'][-1] <= strategy_document.strategy['settings'][
            'standard error threshold']:
            return True
        else:
            return False

    monkeypatch.setattr(sampling, 'check_convergence', mock_return)


@pytest.mark.skipif(platform.system() == 'Linux', reason='Test should only run locally')
def test_sampling_worker(add_mock_strategy, mock_sampling_distribution, mock_create_delphin,
                         mock_wait_until_finished, mock_calculate_error, mock_upload_error, mock_check_convergence):

    with pytest.raises(SystemExit) as exc_info:
        sampling_worker.sampling_worker(add_mock_strategy)

    strategy_doc = sample_entry.Strategy.objects(id=add_mock_strategy).first()
    threshold = strategy_doc.strategy['settings']['standard error threshold']
    number_of_runs = len(strategy_doc.standard_error['mould'])

    assert number_of_runs < 1/threshold ** 2
    assert number_of_runs < 1/threshold
