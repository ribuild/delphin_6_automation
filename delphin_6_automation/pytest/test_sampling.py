__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import pytest

# RiBuild Modules
from delphin_6_automation.sampling import sampling
import delphin_6_automation.database_interactions.sampling_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry

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


@pytest.mark.skip()
def test_add_delphin_to_sampling(db_one_project, add_sampling):

    delphin_doc = delphin_entry.Delphin.objects().first()
    sample = sample_entry.Sample.objects().first()

    sampling_doc = delphin_6_automation.database_interactions.sampling_interactions.add_delphin_to_sampling(sample, [delphin_doc, ])

    assert sampling_doc.delphin_ids
