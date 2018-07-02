__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger(__name__)

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def load_scheme(path):
    # TODO - Load sampling scheme
    # The sampling scheme file could be a json

    return None


def load_existing_samples():
    # TODO - Load existing samples from database
    # Look up the existing sample entries in the database
    # If there is not previous samples in database return empty dict or dataframe
    # Download them
    # Combine them into one
    # Return the samples as a dict or dataframe

    return None


def create_samples(sampling_scheme, previous_samples):
    # TODO - Create new samples based on the old ones and the sampling scheme
    # Call Sobol to create new samples based on scheme and previous samples
    # If previous samples are an empty dict/dataframe, create samples purely based on sampling scheme

    return None


def create_delphin_projects(sampling_scheme, samples):
    # TODO - Create new delphin files based on the samples
    # The paths for the base delphin files should be found in the sampling scheme
    # Permutate the base files according to the samples
    # Upload the new delphin files
    # Return the database ids for the delphin files

    return None


def upload_samples(new_samples):
    # TODO - Upload the samples to the database
    # Return the entry id

    return None


def add_delphin_to_sampling(sampling_document, delphin_ids):
    # TODO - Add the delphin ids to the sampling database entry

    return None


def calculate_error(delphin_ids):
    # TODO - Calculated the standard error on the results from the given delphin simulations
    # Return the error
    return None


def upload_standard_error(sampling_document, current_error):
    # TODO - Upload the standard error to the sampling entry

    return None


def check_convergence(sampling_scheme, standard_error):
    # TODO - Check if the standard error is lower than the threshold value in the sampling scheme
    # If it is return True otherwise return False

    return None