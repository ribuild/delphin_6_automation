__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def upload_sampling_scheme(sampling_scheme: dict):

    entry = sample_entry.Scheme()
    scheme = sampling_scheme
    entry.save()

    return entry.id


def download_sampling_scheme(scheme_id):
    # TODO - Download sampling scheme

    return None


def upload_samples(new_samples, sample_iteration):
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


def add_delphin_to_sampling(sampling_document, delphin_ids):
    # TODO - Add the delphin ids to the sampling database entry
    # Test Simon

    return None


def upload_standard_error(sampling_document, current_error):
    # TODO - Upload the standard error to the sampling entry

    return None
