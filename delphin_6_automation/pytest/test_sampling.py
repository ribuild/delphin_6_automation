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


def test_create_sampling_strategy(tmpdir, add_three_years_weather, mock_design_options):
    folder = tmpdir.mkdir('test')
    test_strategy = sampling.create_sampling_strategy(folder)

    assert os.path.isfile(os.path.join(folder, 'sampling_strategy.json'))
    assert all(element in list(test_strategy.keys())
               for element in ['design', 'scenario', 'distributions', 'settings'])
    assert test_strategy['design']
    assert test_strategy['scenario']
    assert test_strategy['distributions']
    assert test_strategy['settings']


def test_load_strategy(mock_design_options, add_three_years_weather, tmpdir):
    folder = tmpdir.mkdir('test')
    source_strategy = sampling.create_sampling_strategy(folder)
    test_strategy = sampling.load_strategy(folder)

    assert source_strategy == test_strategy


def test_add_delphin_to_sampling(db_one_project, add_dummy_sample):
    delphin_doc = delphin_entry.Delphin.objects().first()
    sample = sample_entry.Sample.objects().first()

    sampling_interactions.add_delphin_to_sampling(sample.id, [delphin_doc.id, ])

    assert not sample.delphin_docs
    sample.reload()
    assert sample.delphin_docs
    assert isinstance(sample.delphin_docs, list)
    assert sample.delphin_docs[0] == delphin_doc


@pytest.mark.parametrize('second_dimension',
                         [1, 2, 3, 6, 9])
def test_sobol(second_dimension):
    first_dimension = 2 ** 12
    sobol_sampling = sampling.sobol(m=first_dimension, dimension=second_dimension)

    assert isinstance(sobol_sampling, np.ndarray)
    assert sobol_sampling.shape == (first_dimension, second_dimension)
    assert np.all(sobol_sampling[(sobol_sampling < 1.0) & (sobol_sampling > 0.0)])


@pytest.mark.parametrize('step_counter',
                         [0, 2, ])
def test_get_raw_samples(strategy_with_raw_dummy_samples, step_counter, mock_sobol):
    strategy = sample_entry.Strategy.objects().first()
    samples_before = len(strategy.samples_raw)

    raw_samples = sampling.get_raw_samples(strategy, step_counter)
    strategy.reload()

    assert isinstance(raw_samples, np.ndarray)
    assert raw_samples.shape == (2 ** 12, len(strategy.strategy['distributions'].keys()))
    assert strategy.samples_raw[-1].sequence_number == step_counter
    assert strategy.samples_raw[-1].samples_raw == raw_samples.tolist()

    if step_counter > 1:
        assert samples_before < len(strategy.samples_raw)
    else:
        assert samples_before == len(strategy.samples_raw)


@pytest.mark.parametrize('used_samples_per_set',
                         [0, 1, 2])
def test_compute_sampling_distributions(strategy_with_raw_dummy_samples, used_samples_per_set):
    strategy = sample_entry.Strategy.objects().first()
    raw_samples = np.array(strategy.samples_raw[0].samples_raw)

    distribution_dict = sampling.compute_sampling_distributions(strategy.strategy, raw_samples, used_samples_per_set)

    assert distribution_dict
    assert isinstance(distribution_dict, dict)
    for design in distribution_dict:
        for scenario in distribution_dict[design]:
            for param in distribution_dict[design][scenario]:
                assert len(distribution_dict[design][scenario][param]) == 1


@pytest.mark.parametrize('used_samples_per_set',
                         [0, 1, 2])
def test_create_samples(add_sampling_strategy, used_samples_per_set, mock_sobol):
    strategy = sample_entry.Strategy.objects().first()

    samples = sampling.create_samples(strategy, used_samples_per_set)

    assert samples
    assert isinstance(samples, dict)
    assert len(samples.keys()) == strategy.strategy['settings']['sequence']
    assert all([isinstance(key, str) for key in samples.keys()])


def test_load_design_options(add_three_years_weather, mock_design_options, delphin_design_folder):

    strategy = sampling.create_sampling_strategy(delphin_design_folder)
    design_options = sampling.load_design_options(strategy['design'], delphin_design_folder)

    assert design_options
    assert isinstance(design_options, list)
    assert all(isinstance(project, dict)
               for project in design_options)


def test_create_delphin_projects(create_samples, mock_material_info, add_five_materials, mock_design_options,
                                 delphin_design_folder):
    strategy = sample_entry.Strategy.objects().first()
    delphin_ids = sampling.create_delphin_projects(strategy.strategy, create_samples, delphin_design_folder)

    assert delphin_ids
    assert isinstance(delphin_ids, list)

    for delphin_id in delphin_ids:
        delphin_doc = delphin_entry.Delphin.objects(id=delphin_id).first()
        assert delphin_doc.sample_data
        assert isinstance(delphin_doc.sample_data, dict)
        assert delphin_doc.sample_data['design_option']
        assert delphin_doc.sample_data['sequence']


def test_calculate_error(add_sample_for_errors):
    strategy = sample_entry.Strategy.objects().first()

    standard_error = sampling.calculate_error(strategy)

    assert standard_error
    assert isinstance(standard_error, dict)
    for design in standard_error.keys():
        for damage_model in standard_error[design].keys():
            assert isinstance(standard_error[design][damage_model], float)


@pytest.mark.parametrize('error',
                         [1.0, 0.1, 0.01])
def test_upload_standard_error(add_strategy_for_errors, error):
    strategy = sample_entry.Strategy.objects().first()
    current_error = {'Test Design': {'mould': error,
                                     'algae': error,
                                     'heat_loss': error}}

    sampling_interactions.upload_standard_error(strategy, current_error)

    strategy.reload()

    assert strategy.standard_error
    assert isinstance(strategy.standard_error, dict)
    assert isinstance(strategy.standard_error['Test Design']['mould'], list)
    assert strategy.standard_error['Test Design']['mould'][-1] == error
    assert isinstance(strategy.standard_error['Test Design']['algae'], list)
    assert strategy.standard_error['Test Design']['algae'][-1] == error
    assert isinstance(strategy.standard_error['Test Design']['heat_loss'], list)
    assert strategy.standard_error['Test Design']['heat_loss'][-1] == error


@pytest.mark.parametrize('error',
                         [0.3, 0.101, 0.1, 0.01])
def test_check_convergence(add_strategy_for_errors, add_dummy_sample, error):
    strategy = sample_entry.Strategy.objects().first()
    sample = sample_entry.Sample.objects().first()
    current_error = {'Test Design': {'mould': error,
                                     'algae': error,
                                     'heat_loss': error}}

    sampling_interactions.upload_standard_error(strategy, current_error)

    strategy.reload()
    threshold = strategy.strategy['settings']['standard error threshold']
    assert (error <= threshold) == sampling.check_convergence(strategy)


def test_calculate_sample_output(empty_database, add_strategy_for_errors, add_dummy_sample, add_delphin_for_errors):
    strategy_doc = sample_entry.Strategy.objects().first()
    sample_doc = sample_entry.Sample.objects().first()

    sampling.calculate_sample_output(strategy_doc.strategy, sample_doc.id)

    assert not sample_doc.mean
    assert not sample_doc.standard_deviation
    sample_doc.reload()

    assert sample_doc.mean
    assert isinstance(sample_doc.mean, dict)
    for key in sample_doc.mean.keys():
        assert isinstance(key, str)
        assert isinstance(int(key), int)

    assert sample_doc.standard_deviation
    assert isinstance(sample_doc.standard_deviation, dict)
    for key in sample_doc.standard_deviation.keys():
        assert isinstance(key, str)
        assert isinstance(int(key), int)


def test_initialize_sampling(add_sampling_strategy):

    strategy = sample_entry.Strategy.objects().first()
    iteration, convergence, new_samples_per_set, used_samples_per_set = sampling.initialize_sampling(strategy)

    assert iteration == 0
    assert not convergence
    assert new_samples_per_set == 1
    assert used_samples_per_set == 0
