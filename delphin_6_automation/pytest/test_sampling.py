__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os

# RiBuild Modules
from delphin_6_automation.sampling import sampling

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_create_sampling_scheme(tmpdir):

    folder = tmpdir.mkdir('test')
    test_scheme = sampling.create_sampling_scheme(folder)

    assert os.path.isfile(os.path.join(folder, 'sampling_scheme.json'))
    assert all(element in list(test_scheme.keys())
               for element in ['scenario', 'distributions', 'settings'])
    #assert test_scheme['scenario']
    assert test_scheme['distributions']
    assert test_scheme['settings']


def test_load_scheme(tmpdir):

    folder = tmpdir.mkdir('test')
    source_scheme = sampling.create_sampling_scheme(folder)
    test_scheme = sampling.load_scheme(folder)

    assert source_scheme == test_scheme


def test_add_delphin_to_sampling(samples, docs):

    sampling_doc = sampling.add_delphin_to_sampling(samples, docs)

    assert sampling_doc.delphin_ids
