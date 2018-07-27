__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import datetime
import pytest

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import sampling_interactions
from delphin_6_automation.sampling import sampling


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_download_sampling_strategy(add_sampling_strategy):
    strategy_id = sample_entry.Strategy.objects().first().id

    test_strategy = sampling_interactions.get_sampling_strategy(strategy_id)

    assert test_strategy
    assert isinstance(test_strategy, sample_entry.Strategy)
    assert isinstance(test_strategy.strategy, dict)
    assert all(element in list(test_strategy.strategy.keys())
               for element in ['design', 'scenario', 'distributions', 'settings'])
    assert test_strategy.strategy['scenario']
    assert test_strategy.strategy['design']
    assert test_strategy.strategy['distributions']
    assert test_strategy.strategy['settings']


def test_upload_sampling_strategy(add_three_years_weather, tmpdir):
    test_dir = tmpdir.mkdir('test')
    strategy = sampling.create_sampling_strategy(test_dir)
    strategy_id = sampling_interactions.upload_sampling_strategy(strategy)

    strategy_doc = sample_entry.Strategy.objects().first()

    # Checks
    assert isinstance(strategy_doc.added_date, datetime.datetime)
    assert not strategy_doc.samples
    assert not strategy_doc.standard_error
    assert strategy_doc.strategy

    # Strategy Check
    assert isinstance(strategy_doc.strategy, dict)
    assert all(element in list(strategy_doc.strategy.keys())
               for element in ['design', 'scenario', 'distributions', 'settings'])

    # Strategy Scenario Check
    assert strategy_doc.strategy['scenario']
    assert isinstance(strategy_doc.strategy['scenario'], dict)

    # Strategy Distributions Check
    assert strategy_doc.strategy['distributions']
    assert isinstance(strategy_doc.strategy['distributions'], dict)
    for distribution in strategy_doc.strategy['distributions'].keys():
        assert all(element in list(strategy_doc.strategy['distributions'][distribution].keys())
                   for element in ['type', 'range'])
        assert strategy_doc.strategy['distributions'][distribution]['type']
        assert strategy_doc.strategy['distributions'][distribution]['range']

    # Strategy Settings Check
    assert strategy_doc.strategy['settings']
    setting_elements = ['initial samples per set', 'add samples per run',
                        'max samples', 'sequence', 'standard error threshold']
    assert all(element in list(strategy_doc.strategy['settings'].keys())
               for element in setting_elements)
    for setting in strategy_doc.strategy['settings'].keys():
        assert strategy_doc.strategy['settings'][setting]


def test_upload_raw_samples(empty_database):
    raw_id = sampling_interactions.upload_raw_samples(sampling.sobol(m=2 ** 12, dimension=3), 1)
    raw_entry = sample_entry.SampleRaw.objects(id=raw_id).first()

    assert raw_entry
    assert isinstance(raw_entry.added_date, datetime.datetime)
    assert isinstance(raw_entry.samples_raw, list)
    assert raw_entry.sequence_number == 1


def test_add_raw_samples_to_strategy(add_sampling_strategy, add_raw_sample):
    raw_entry = sample_entry.SampleRaw.objects().first()
    strategy_entry = sample_entry.Strategy.objects().first()

    sampling_interactions.add_raw_samples_to_strategy(strategy_entry, raw_entry.id)
    strategy_entry.reload()

    assert isinstance(strategy_entry.samples_raw, list)
    assert strategy_entry.samples_raw[0] == raw_entry


@pytest.mark.parametrize('iteration',
                         [0, 1, 2])
def test_upload_samples(setup_database, dummy_sample, iteration):
    sample_id = sampling_interactions.upload_samples(dummy_sample, iteration)
    sample_doc = sample_entry.Sample.objects(id=sample_id).first()

    assert sample_doc
    assert isinstance(sample_doc.added_date, datetime.datetime)

    assert sample_doc.samples
    assert isinstance(sample_doc.samples, dict)
    assert sample_doc.iteration == iteration
    assert not sample_doc.delphin_docs
    assert not sample_doc.standard_deviation
    assert not sample_doc.mean


def test_add_sample_to_strategy(add_sampling_strategy, add_dummy_sample):
    sample_doc = sample_entry.Sample.objects().first()
    strategy_entry = sample_entry.Strategy.objects().first()

    sampling_interactions.add_sample_to_strategy(strategy_entry.id, sample_doc.id)
    strategy_entry.reload()

    assert isinstance(strategy_entry.samples, list)
    assert strategy_entry.samples[0] == sample_doc


def test_upload_sample_mean(empty_database, add_dummy_sample):
    sample_mean = {'0': {'design_0': [0.5, 0.5],
                         'design_1': [0.5, 0.5]},
                   '1': {'design_0': [0.5, 0.5],
                         'design_1': [0.5, 0.5]}
                   }

    sampling_document = sample_entry.Sample.objects().first()
    sampling_interactions.upload_sample_mean(sampling_document.id, sample_mean)

    assert not sampling_document.mean
    sampling_document.reload()
    assert sampling_document.mean
    assert isinstance(sampling_document.mean, dict)


def test_upload_sample_std(add_dummy_sample):
    sample_std = {'0': {'design_0': [0.5, 0.5],
                        'design_1': [0.5, 0.5]},
                  '1': {'design_0': [0.5, 0.5],
                        'design_1': [0.5, 0.5]}
                  }

    sampling_document = sample_entry.Sample.objects().first()
    sampling_interactions.upload_sample_std(sampling_document.id, sample_std)

    assert not sampling_document.standard_deviation
    sampling_document.reload()
    assert sampling_document.standard_deviation
    assert isinstance(sampling_document.standard_deviation, dict)
