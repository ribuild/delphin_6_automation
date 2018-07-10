__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import mongoengine
import numpy as np

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry, delphin_entry


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def upload_sampling_scheme(sampling_scheme: dict) -> str:
    """
    Upload as given sampling scheme to the database

    :param sampling_scheme: Sampling scheme
    :type sampling_scheme: dict
    :return: Sampling scheme database ID
    :rtype: str
    """

    entry = sample_entry.Scheme()
    entry.scheme = sampling_scheme
    entry.save()

    return entry.id


def get_sampling_scheme(scheme_id: str) -> sample_entry.Scheme:
    """
    Downloads the sampling scheme with the given database ID

    :param scheme_id: Sampling scheme database ID
    :type scheme_id: str
    :return: Sampling Scheme
    :rtype: dict
    """

    scheme = sample_entry.Scheme.objects(id=scheme_id).first()

    return scheme


def upload_samples(new_samples: dict, sample_iteration: int) -> str:
    """
    Uploads samples to database and returns the sample id

    :param new_samples: Samples
    :type new_samples: dict
    :param sample_iteration: Number of sample iteration
    :type sample_iteration: int
    :return: Sample Database id
    :rtype: mongoengine.ObjectID
    """

    sample = sample_entry.Sample()
    sample.samples = new_samples
    sample.iteration = sample_iteration
    sample.save()

    return sample.id


def upload_standard_error(sampling_id: str, current_error):
    """
    Upload the standard error to the sampling entry

    :param sampling_id: ID of sampling entry to add the standard error to.
    :type sampling_id: str
    :param current_error: Current standard error
    :type current_error: dict
    """

    sampling_document = sample_entry.Sample.objects(id=sampling_id).first()
    sampling_document.update(push__standard_error=current_error)


def upload_raw_samples(samples_raw: np.array, sequence_number: int) -> str:

    entry = sample_entry.SampleRaw()
    entry.samples_raw = samples_raw.tolist()
    entry.sequence_number = sequence_number
    entry.save()

    return entry.id


def add_raw_samples_to_scheme(sampling_scheme: sample_entry.Scheme, samples_raw_id: str):

    raw_sample_doc = sample_entry.SampleRaw.objects(id=samples_raw_id).first()
    sampling_scheme.update(push__samples_raw=raw_sample_doc)

    return sampling_scheme.id


def add_delphin_to_sampling(sampling_id: str, delphin_ids: list):

    sampling_document = sample_entry.Sample.objects(id=sampling_id).first()

    for delphin_id in delphin_ids:
        delphin_doc = delphin_entry.Delphin.objects(id=delphin_id).first()
        sampling_document.update(push__delphin_ids=delphin_doc)
