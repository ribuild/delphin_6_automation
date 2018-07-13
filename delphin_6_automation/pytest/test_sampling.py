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


def test_create_sampling_strategy(tmpdir, add_three_years_weather):

    folder = tmpdir.mkdir('test')
    test_strategy = sampling.create_sampling_strategy(folder)

    assert os.path.isfile(os.path.join(folder, 'sampling_strategy.json'))
    assert all(element in list(test_strategy.keys())
               for element in ['design', 'scenario', 'distributions', 'settings'])
    assert test_strategy['design']
    assert test_strategy['scenario']
    assert test_strategy['distributions']
    assert test_strategy['settings']


def test_load_strategy(tmpdir):

    folder = tmpdir.mkdir('test')
    source_strategy = sampling.create_sampling_strategy(folder)
    test_strategy = sampling.load_strategy(folder)

    assert source_strategy == test_strategy


@pytest.mark.skip('not yet implemented')
def test_add_delphin_to_sampling(db_one_project, add_sampling):

    delphin_doc = delphin_entry.Delphin.objects().first()
    sample = sample_entry.Sample.objects().first()

    sampling_doc = sampling_interactions.add_delphin_to_sampling(sample, [delphin_doc, ])

    assert sampling_doc.delphin_ids


@pytest.mark.parametrize('second_dimension',
                         [1, 2, 3, 5, 6, 9])
def test_sobol(second_dimension):

    first_dimension = 2**12
    sobol_sampling = sampling.sobol(m=first_dimension, dimension=second_dimension)

    assert isinstance(sobol_sampling, np.ndarray)
    assert sobol_sampling.shape == (first_dimension, second_dimension)
    assert np.all(sobol_sampling[(sobol_sampling < 1.0) & (sobol_sampling > 0.0)])


@pytest.mark.parametrize('step_counter',
                         [0, 2, ])
def test_get_raw_samples(strategy_with_raw_samples, step_counter):

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
def test_compute_sampling_distributions(strategy_with_raw_samples, used_samples_per_set):

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
def test_create_samples(strategy_with_raw_samples, used_samples_per_set):

    strategy = sample_entry.Strategy.objects().first()

    samples = sampling.create_samples(strategy, used_samples_per_set)

    assert samples
    assert isinstance(samples, dict)
    assert len(samples.keys()) == strategy.strategy['settings']['sequence']
    assert all([isinstance(key, str) for key in samples.keys()])
