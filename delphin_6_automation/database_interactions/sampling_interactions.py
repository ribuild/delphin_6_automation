__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import numpy as np

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry, delphin_entry
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger(__name__)

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

    logger.debug(f'Uploaded sampling strategy with ID: {entry.id}')

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
    logger.debug(f'Downloaded sampling strategy with ID: {strategy_id}')

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

    logger.debug(f'Uploaded samples with ID: {sample.id}')

    return sample.id


def upload_standard_error(strategy_document: sample_entry.Strategy, current_error: dict) -> None:
    """
    Upload the standard error to the sampling entry

    :param strategy_document: Sampling strategy to add the standard error to.
    :type strategy_document: sample_entry.Strategy
    :param current_error: Current standard error
    :type current_error: dict
    """

    standard_error = strategy_document.standard_error

    if not standard_error:
        for design in current_error.keys():
            standard_error[design] = {}
            standard_error[design]['mould'] = []
            standard_error[design]['algae'] = []
            standard_error[design]['heat_loss'] = []

    for design in current_error.keys():
        standard_error[design]['mould'].append(current_error[design]['mould'])
        standard_error[design]['algae'].append(current_error[design]['algae'])
        standard_error[design]['heat_loss'].append(current_error[design]['heat_loss'])

    strategy_document.update(set__standard_error=standard_error)
    logger.info(f'Updated the standard error for sampling strategy with ID: {strategy_document.id}')

    return None


def upload_raw_samples(samples_raw: np.ndarray, sequence_number: int) -> str:

    entry = sample_entry.SampleRaw()
    entry.samples_raw = samples_raw.tolist()
    entry.sequence_number = sequence_number
    entry.save()

    logger.debug(f'Uploaded raw samples with ID: {entry.id} for sequence {sequence_number}')

    return entry.id


def add_raw_samples_to_strategy(sampling_strategy: sample_entry.Strategy, samples_raw_id: str) -> str:

    raw_sample_doc = sample_entry.SampleRaw.objects(id=samples_raw_id).first()
    sampling_strategy.update(push__samples_raw=raw_sample_doc)

    logger.debug(f'Added raw samples with ID: {samples_raw_id} to strategy with ID: {sampling_strategy.id}')

    return sampling_strategy.id


def add_delphin_to_sampling(sample_id: str, delphin_ids: list) -> None:

    sample_document = sample_entry.Sample.objects(id=sample_id).first()

    for delphin_id in delphin_ids:
        delphin_doc = delphin_entry.Delphin.objects(id=delphin_id).first()
        sample_document.update(push__delphin_docs=delphin_doc)

    logger.debug(f'Added Delphin IDs: {delphin_ids} to sample with ID: {sample_id}')


def add_sample_to_strategy(strategy_id: str, sample_id: str) -> None:

    sample_document = sample_entry.Sample.objects(id=sample_id).first()
    strategy_document = sample_entry.Strategy.objects(id=strategy_id).first()
    strategy_document.update(push__samples=sample_document)

    logger.debug(f'Added samples with ID: {sample_id} to strategy with ID: {strategy_id}')


def upload_sample_mean(sampling_id: str, sample_mean: dict) -> None:
    sampling_document = sample_entry.Sample.objects(id=sampling_id).first()
    sampling_document.update(set__mean=sample_mean)

    return None


def upload_sample_std(sampling_id: str, sample_std: dict) -> None:
    sampling_document = sample_entry.Sample.objects(id=sampling_id).first()
    sampling_document.update(set__standard_deviation=sample_std)

    return None


def upload_sample_iteration_parameters(strategy_doc: sample_entry.Strategy, iteration: int, used_samples: int) -> None:

    strategy_doc.update(set__current_iteration=iteration)
    strategy_doc.update(set__used_samples_per_set=used_samples)

    logger.debug(f'Updated strategy with ID: {strategy_doc.id} with current iteration: {iteration} and'
                 f'used samples per set: {used_samples}')

    return None
