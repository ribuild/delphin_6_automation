__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import json
import os

# RiBuild Modules
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.sampling import inputs

# Logger


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def create_sampling_scheme(path: str) -> dict:
    """
    Create a sampling scheme for WP6 Delphin Automation. The sampling scheme will be name 'sampling_scheme.json' and
    be located at the given folder.

    :param path: Folder, where the scheme will be saved.
    :type path: str
    :return: Created sampling scheme
    :rtype: dict
    """

    # TODO - Create scenarios
    scenario = {}

    distributions = {'exterior climate':
                         {'type': 'discrete', 'value': list(general_interactions.list_weather_stations().keys())},

                     'exterior heat transfer coefficient slope':
                         {'type': 'uniform', 'value': [1, 4]},

                     'exterior moisture transfer coefficient':
                         {'type': 'uniform', 'value': [4 * 10 ** -9, 10 ** -9]},

                     'solar absorption':
                         {'type': 'uniform', 'value': [0.4, 0.8]},

                     'rain scale factor':
                         {'type': 'uniform', 'value': [0, 2]},

                     'interior climate':
                         {'type': 'discrete', 'value': ['a', 'b']},

                     'interior heat transfer coefficient':
                         {'type': 'uniform', 'value': [5, 10]},

                     'interior moisture transfer coefficient':
                         {'type': 'uniform', 'value': [4 * 10 ** -9, 10 ** -9]},

                     'interior sd value':
                         {'type': 'uniform', 'value': [0.0, 0.6]},

                     'wall orientation':
                         {'type': 'uniform', 'value': [0, 360]},

                     'construction type':
                         {'type': 'discrete', 'value': inputs.construction_types()},

                     'wall core width':
                         {'type': 'uniform', 'value': [0.1, 0.9]},

                     'wall core material':
                         {'type': 'discrete', 'value': inputs.wall_core_materials()},

                     'plaster width':
                         {'type': 'uniform', 'value': [0.01, 0.02]},

                     'plaster material':
                         {'type': 'discrete', 'value': inputs.plaster_materials()},

                     'insulation type':
                         {'type': 'discrete', 'value': inputs.insulation_type()},

                     'insulation width':
                         {'type': 'uniform', 'value': [0.01, 0.3]},

                     'start year':
                         {'type': 'discrete', 'value': 24},
                     }

    sampling_settings = {'initial samples per set': 1,
                         'add samples per run': 1,
                         'max samples': 500,
                         'sequence': 10,
                         'standard error threshold': 0.1}

    combined_dict = {'scenario': scenario, 'distributions': distributions, 'settings': sampling_settings}

    with open(os.path.join(path, 'sampling_scheme.json'), 'w') as file:
        json.dump(combined_dict, file)

    return combined_dict


def load_scheme(path: str) -> dict:
    """
    Load a sampling scheme from a JSON file.

    :param path: Folder, where the sampling scheme is located
    :type path: string
    :return: Sampling scheme
    :rtype: dict
    """

    with open(os.path.join(path, 'sampling_scheme.json'), 'r') as file:
        sampling_scheme = json.load(file)

    return sampling_scheme


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


def upload_samples(new_samples, sample_iteration):
    # TODO - Upload the samples to the database
    # Add samples to sampling scheme
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
