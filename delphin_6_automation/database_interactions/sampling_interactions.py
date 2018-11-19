__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import numpy as np
import typing

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry, delphin_entry
from delphin_6_automation.sampling import sim_time_prediction
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import simulation_interactions

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def upload_sampling_strategy(sampling_strategy: dict) -> str:
    """
    Upload as given sampling strategy to the database

    :param sampling_strategy: Sampling strategy
    :return: Sampling strategy database ID
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
    :return: Sampling Strategy
    """

    strategy = sample_entry.Strategy.objects(id=strategy_id).first()

    logger.debug(f'Downloaded sampling strategy with ID: {strategy_id}')

    return strategy


def upload_samples(new_samples: dict, sample_iteration: int) -> str:
    """
    Uploads samples to database and returns the sample id

    :param new_samples: Samples
    :param sample_iteration: Number of sample iteration
    :return: Sample Database id
    """

    logger.debug(f'Uploading samples')

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
    :param current_error: Current standard error
    """

    standard_error = strategy_document.standard_error

    if not standard_error:
        for design in current_error.keys():
            standard_error[design] = {}
            standard_error[design]['mould'] = []
            standard_error[design]['heat_loss'] = []

    for design in current_error.keys():
        standard_error[design]['mould'].append(current_error[design]['mould'])
        standard_error[design]['heat_loss'].append(current_error[design]['heat_loss'])

    strategy_document.update(set__standard_error=standard_error)

    logger.info(f'Updated the standard error for sampling strategy with ID: {strategy_document.id}')

    return None


def upload_raw_samples(samples_raw: np.ndarray, sequence_number: int) -> str:
    """Upload raw sample to database"""

    entry = sample_entry.SampleRaw()
    entry.samples_raw = samples_raw.tolist()
    entry.sequence_number = sequence_number
    entry.save()

    logger.debug(f'Uploaded raw samples with ID: {entry.id} for sequence {sequence_number}')

    return entry.id


def add_raw_samples_to_strategy(sampling_strategy: sample_entry.Strategy, samples_raw_id: str) -> str:
    """Connect a raw sample entry to a sample strategy entry"""

    raw_sample_doc = sample_entry.SampleRaw.objects(id=samples_raw_id).first()
    sampling_strategy.update(push__samples_raw=raw_sample_doc)

    logger.debug(f'Added raw samples with ID: {samples_raw_id} to strategy with ID: {sampling_strategy.id}')

    return sampling_strategy.id


def add_delphin_to_sampling(sample_id: str, delphin_ids: list) -> None:
    """Connect a Delphin project to a sample entry"""

    sample_document = sample_entry.Sample.objects(id=sample_id).first()

    for delphin_id in delphin_ids:
        delphin_doc = delphin_entry.Delphin.objects(id=delphin_id).first()
        sample_document.update(push__delphin_docs=delphin_doc)

    logger.debug(f'Added Delphin IDs: {delphin_ids} to sample with ID: {sample_id}')


def add_sample_to_strategy(strategy_id: str, sample_id: str) -> None:
    """Connect a sample entry to a sample strategy entry"""

    sample_document = sample_entry.Sample.objects(id=sample_id).first()
    strategy_document = sample_entry.Strategy.objects(id=strategy_id).first()
    strategy_document.update(push__samples=sample_document)

    logger.debug(f'Added samples with ID: {sample_id} to strategy with ID: {strategy_id}')


def upload_sample_mean(sample_id: str, sample_mean: dict) -> None:
    """Upload the mean of the sample simulation result"""

    sampling_document = sample_entry.Sample.objects(id=sample_id).first()
    sampling_document.update(set__mean=sample_mean)

    logger.debug(f'Uploads sample mean to sample with ID: {sample_id}')

    return None


def upload_sample_std(sample_id: str, sample_std: dict) -> None:
    """Upload the standard deviation of the sample simulation result"""

    sampling_document = sample_entry.Sample.objects(id=sample_id).first()
    sampling_document.update(set__standard_deviation=sample_std)

    logger.debug(f'Uploads sample standard deviation to sample with ID: {sample_id}')

    return None


def upload_sample_iteration_parameters(strategy_doc: sample_entry.Strategy, iteration: int, used_samples: int) -> None:
    """Updates a sample strategy with the current sampling iteration and number of used samples"""

    strategy_doc.update(set__current_iteration=iteration)
    strategy_doc.update(set__used_samples_per_set=used_samples)

    logger.debug(f'Updated strategy with ID: {strategy_doc.id} with current iteration: {iteration} and'
                 f'used samples per set: {used_samples}')

    return None


def get_delphin_for_sample(sample: sample_entry.Sample) -> typing.List[str]:
    """Gets Delphin projects related to a sample"""

    sample.reload()

    logger.debug(f'Fetches Delphin document related to sample with ID: {sample.id}')

    return [delphin.id for delphin in sample.delphin_docs]


def update_queue_priorities(sample_id: str):
    """Updates the queue priorities based on the estimated simulation time."""

    sample_doc = sample_entry.Sample.objects(id=sample_id).first()

    if sample_doc.iteration >= 3:
        sim_time_prediction.queue_priorities_on_time_prediction(sample_doc)
        logger.info(f'Updated queue priorities based on the time prediction')
    else:
        logger.info(f'The current iteration [{sample_doc.iteration}]was below 3, '
                    f'therefore the queue priorities where not updated.')


def update_time_estimation_model(strategy_id: str):
    """Updates the machine learning model for simulation time estimations."""

    strategy_doc = sample_entry.Strategy.objects(id=strategy_id).first()

    if strategy_doc.current_iteration >= 3:
        sim_time_prediction.create_upload_time_prediction_model(strategy_doc)
        logger.info(f'Updated time prediction model')

    else:
        logger.info(f'The current iteration [{strategy_doc.current_iteration}]was below 3, '
                    f'therefore no time prediction model was created.')


def predict_simulation_time(delphin_ids: typing.List[str], strategy_id: str) -> None:
    """
    Predicts the simulation time of a list of Delphin projects. The time prediction model is updated
    before it is applied to the Delphin projects.
    """

    update_time_estimation_model(strategy_id)

    strategy_doc = sample_entry.Strategy.objects(id=strategy_id).first()
    time_model = strategy_doc.time_prediction_model

    if time_model:
        for delphin_id in delphin_ids:
            delphin_doc = delphin_entry.Delphin.objects(id=delphin_id).first()
            sim_time_prediction.simulation_time_prediction_ml(delphin_doc, time_model)

    else:
        for delphin_id in delphin_ids:
            time_estimate = general_interactions.compute_simulation_time(delphin_id)
            simulation_interactions.set_simulation_time_estimate(delphin_id, time_estimate)
