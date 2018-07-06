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
from delphin_6_automation.database_interactions.db_templates import sample_entry


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
                         {'type': 'discrete', 'range': list(general_interactions.list_weather_stations().keys()),
                          'sample_values': []},

                     'exterior heat transfer coefficient slope':
                         {'type': 'uniform', 'range': [1, 4], 'sample_values': []},

                     'exterior moisture transfer coefficient':
                         {'type': 'uniform', 'range': [4 * 10 ** -9, 10 ** -9], 'sample_values': []},

                     'solar absorption':
                         {'type': 'uniform', 'range': [0.4, 0.8], 'sample_values': []},

                     'rain scale factor':
                         {'type': 'uniform', 'range': [0, 2], 'sample_values': []},

                     'interior climate':
                         {'type': 'discrete', 'range': ['a', 'b'], 'sample_values': []},

                     'interior heat transfer coefficient':
                         {'type': 'uniform', 'range': [5, 10], 'sample_values': []},

                     'interior moisture transfer coefficient':
                         {'type': 'uniform', 'range': [4 * 10 ** -9, 10 ** -9], 'sample_values': []},

                     'interior sd value':
                         {'type': 'uniform', 'range': [0.0, 0.6], 'sample_values': []},

                     'wall orientation':
                         {'type': 'uniform', 'range': [0, 360], 'sample_values': []},

                     'construction type':
                         {'type': 'discrete', 'range': inputs.construction_types(), 'sample_values': []},

                     'wall core width':
                         {'type': 'uniform', 'range': [0.1, 0.9], 'sample_values': []},

                     'wall core material':
                         {'type': 'discrete', 'range': inputs.wall_core_materials(), 'sample_values': []},

                     'plaster width':
                         {'type': 'uniform', 'range': [0.01, 0.02], 'sample_values': []},

                     'plaster material':
                         {'type': 'discrete', 'range': inputs.plaster_materials(), 'sample_values': []},

                     'insulation type':
                         {'type': 'discrete', 'range': inputs.insulation_type(), 'sample_values': []},

                     'insulation width':
                         {'type': 'uniform', 'range': [0.01, 0.3], 'sample_values': []},

                     'start year':
                         {'type': 'discrete', 'range': 24, 'sample_values': []},
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


def load_existing_samples(sampling_scheme_id):
    """
    Look up the existing sample entries in the database connected to the scheme
    If there is not previous samples in database return empty dict

    :param sampling_scheme_id: Sampling scheme id
    :type sampling_scheme_id: str
    :return: Return the samples as a dict
    :rtype: dict
    """

    scheme = sample_entry.Scheme.objects(id=sampling_scheme_id).first()

    if scheme.samples:
        samples_list = scheme.samples
        samples = samples_list[0].samples

        for sample in samples_list[1:]:

            for parameter in sample.keys():
                samples[parameter]['sample_values'].append(sample[parameter]['sample_values'])

        return samples

    else:
        return {}


def load_latest_sample(sampling_scheme_id: str) -> dict:
    """
    Look up the last existing sample entries in the database connected to the scheme
    If there is not previous samples in database return empty dict

    :param sampling_scheme_id: Sampling scheme id
    :type sampling_scheme_id: str
    :return: Return the samples as a dict
    :rtype: dict
    """

    scheme = sample_entry.Scheme.objects(id=sampling_scheme_id).first()

    if scheme.samples:
        samples_list = scheme.samples
        return samples_list[-1].samples

    else:
        return {}


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
    # GET - sample.id above and create_delphin_projects aboveX2
    delphin_document.update(set__dp6_file=delphin_dict)

    return None

def calculate_error(delphin_ids):
    # TODO - Calculated the standard error on the results from the given delphin simulations
    # Return the error
    return None


def check_convergence(sampling_scheme, standard_error):
    # TODO - Check if the standard error is lower than the threshold value in the sampling scheme
    # If it is return True otherwise return False

    return None
