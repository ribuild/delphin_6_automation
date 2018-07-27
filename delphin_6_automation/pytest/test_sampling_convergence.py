__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import pytest
import numpy as np
import platform

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


@pytest.fixture(params=[5, 15], ids=['5 dimensions ', '15 dimensions '])
def add_mock_strategy(empty_database, request):
    sampling_settings = {'initial samples per set': 1,
                         'add samples per run': 1,
                         'max samples': 500,
                         'sequence': 10,
                         'standard error threshold': 0.01,
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
                                                                'output': None,
                                                                'design_option': 'Test Design',
                                                                'sequence': sequence})
            delphin_ids.append(delphin_id)

        return delphin_ids

    monkeypatch.setattr(sampling, 'create_delphin_projects', mockreturn)


def sobol_test_function1(array: np.ndarray) -> np.ndarray:
    return np.prod(1 + (array ** 2 - array + 1 / 6))


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
def mock_calculate_sample_output(monkeypatch):

    def mock_return(sample_strategy: dict, sampling_id: str):
        sample_mean = dict()
        sample_std = dict()
        sequence = sample_strategy['settings']['sequence']
        for sequence_index in range(sequence):
            sample_mean[str(sequence_index)] = dict()
            sample_std[str(sequence_index)] = dict()

            for design in sample_strategy['design']:
                projects_given_design = delphin_entry.Delphin.objects(sample_data__design_option=design,
                                                                      sample_data__sequence=str(sequence_index))
                mould = []
                algae = []
                heat_loss = []

                # TODO - Speed up this with a better query
                for project in projects_given_design:
                    mould.append(project.sample_data['output'])
                    algae.append(project.sample_data['output'])
                    heat_loss.append(project.sample_data['output'])

                sample_mean[str(sequence_index)][design] = {'mould': np.mean(mould),
                                                            'algae': np.mean(algae),
                                                            'heat_loss': np.mean(heat_loss)}
                sample_std[str(sequence_index)][design] = {'mould': np.std(mould),
                                                           'algae': np.std(algae),
                                                           'heat_loss': np.std(heat_loss)}

        sampling_interactions.upload_sample_mean(sampling_id, sample_mean)
        sampling_interactions.upload_sample_std(sampling_id, sample_std)

    monkeypatch.setattr(sampling, 'calculate_sample_output', mock_return)


@pytest.mark.skipif(platform.system() == 'Linux', reason='Test should only run locally')
def test_sampling_worker(add_mock_strategy, mock_sampling_distribution, mock_create_delphin,
                         mock_wait_until_finished, mock_calculate_sample_output,
                         ):

    with pytest.raises(SystemExit) as exc_info:
        sampling_worker.sampling_worker(add_mock_strategy)

    strategy_doc = sample_entry.Strategy.objects(id=add_mock_strategy).first()
    threshold = strategy_doc.strategy['settings']['standard error threshold']
    keys = list(strategy_doc.standard_error.keys())
    number_of_runs = len(strategy_doc.standard_error[keys[0]]['mould'])

    assert number_of_runs < 1/threshold ** 2
    assert number_of_runs < 1/threshold
