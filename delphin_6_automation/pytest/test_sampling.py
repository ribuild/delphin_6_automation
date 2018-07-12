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


def test_create_sampling_strategy(tmpdir):

    folder = tmpdir.mkdir('test')
    test_strategy = sampling.create_sampling_strategy(folder)

    assert os.path.isfile(os.path.join(folder, 'sampling_strategy.json'))
    assert all(element in list(test_strategy.keys())
               for element in ['scenario', 'distributions', 'settings'])
    #assert test_strategy['scenario']
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
