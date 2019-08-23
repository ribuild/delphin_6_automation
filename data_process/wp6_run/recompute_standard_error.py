__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import copy

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.sampling import sampling
from delphin_6_automation.database_interactions.auth import auth_dict

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def calculate_error(sample, sequence_length) -> dict:
    """Calculates the standard error on the results from the given delphin simulations"""

    standard_error = dict()
    mould = {design: []
             for sequence in sample.mean.keys()
             for design in sample.mean[sequence].keys()}
    heat_loss = copy.deepcopy(mould)

    for sequence in sample.mean.keys():

        for design in sample.mean[sequence].keys():
            mould[design].append(sample.mean[sequence][design]['mould'])
            heat_loss[design].append(sample.mean[sequence][design]['heat_loss'])

    for design in mould.keys():
        logger.debug(f'Calculates standard error for design: {design}')

        design_standard_error = {'mould': sampling.relative_standard_error(mould[design], sequence_length),
                                 'heat_loss': sampling.relative_standard_error(heat_loss[design], sequence_length)}

        standard_error[design] = design_standard_error

    return standard_error


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


if __name__ == "__main__":

    server = mongo_setup.global_init(auth_dict)

    print('Starting')
    strategy_doc = sample_entry.Strategy.objects().first()
    strategy_id = strategy_doc.id
    sequence_length = strategy_doc.strategy['settings']['sequence']
    #strategy_doc.update(set__standard_error=None)
    #strategy_doc.reload()

    for index, sample in enumerate(strategy_doc.samples):
        print(f'Current Iteration is: {index}')
        current_error = calculate_error(sample, sequence_length)
        upload_standard_error(strategy_doc, current_error)

    mongo_setup.global_end_ssh(server)
