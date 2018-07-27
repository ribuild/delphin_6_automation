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


def upload_sampling_strategy(sampling_strategy: dict) -> str:
    """
    Upload as given sampling strategy to the database

    :param sampling_strategy: Sampling strategy
    :type sampling_strategy: dict
    :return: Sampling strategy database ID
    :rtype: str
    """

    entry = sample_entry.Strategy()
    entry.strategy = sampling_strategy
    entry.save()

    return entry.id


def get_sampling_strategy(strategy_id: str) -> sample_entry.Strategy:
    """
    Downloads the sampling strategy with the given database ID

    :param strategy_id: Sampling strategy database ID
    :type strategy_id: str
    :return: Sampling Strategy
    :rtype: dict
    """

    strategy = sample_entry.Strategy.objects(id=strategy_id).first()

    return strategy


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


def upload_standard_error(strategy_document: sample_entry.Strategy, sampling_id: str, current_error):
    """
    Upload the standard error to the sampling entry

    :param sampling_id: ID of sampling entry to add the standard error to.
    :type sampling_id: str
    :param current_error: Current standard error
    :type current_error: dict
    """

    sampling_document = sample_entry.Sample.objects(id=sampling_id).first()
    sampling_document.update(set__standard_error=current_error)

    strategy_document.update(push__standard_error__mould=current_error['mould'])
    strategy_document.update(push__standard_error__algae=current_error['algae'])
    strategy_document.update(push__standard_error__heat_loss=current_error['heat_loss'])


def upload_raw_samples(samples_raw: np.ndarray, sequence_number: int) -> str:

    entry = sample_entry.SampleRaw()
    entry.samples_raw = samples_raw.tolist()
    entry.sequence_number = sequence_number
    entry.save()

    return entry.id


def add_raw_samples_to_strategy(sampling_strategy: sample_entry.Strategy, samples_raw_id: str):

    raw_sample_doc = sample_entry.SampleRaw.objects(id=samples_raw_id).first()
    sampling_strategy.update(push__samples_raw=raw_sample_doc)

    return sampling_strategy.id


def add_delphin_to_sampling(sampling_id: str, delphin_ids: list):

    sampling_document = sample_entry.Sample.objects(id=sampling_id).first()

    for delphin_id in delphin_ids:
        delphin_doc = delphin_entry.Delphin.objects(id=delphin_id).first()
        sampling_document.update(push__delphin_docs=delphin_doc)


def add_sample_to_strategy(strategy_id: str, sampling_id: str):

    sampling_document = sample_entry.Sample.objects(id=sampling_id).first()
    strategy_document = sample_entry.Strategy.objects(id=strategy_id).first()
    strategy_document.update(push__samples=sampling_document)


def upload_sample_mean(sampling_id: str, sample_mean: dict) -> None:
    sampling_document = sample_entry.Sample.objects(id=sampling_id).first()
    sampling_document.update(set__mean=sample_mean)

    return None


def upload_sample_std(sampling_id: str, sample_std: dict) -> None:
    sampling_document = sample_entry.Sample.objects(id=sampling_id).first()
    sampling_document.update(set__standard_deviation=sample_std)

    return None
