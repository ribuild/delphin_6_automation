__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import json
import os
import pandas as pd
from scipy.stats import norm
from scipy.stats import randint
from scipy.stats import uniform
import numpy as np
import collections
import typing

# RiBuild Modules
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import sampling_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.delphin_setup import delphin_permutations
from delphin_6_automation.sampling import inputs
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.sampling import sobol_lib


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


def get_raw_samples(sampling_scheme: sample_entry.Scheme, step: int) -> np.array:
    sampling_scheme.reload()

    # Check if the scheme has a raw sampling with the same sequence number as step
    for raw_sample in sampling_scheme.samples_raw:
        if raw_sample.sequence_number == step:
            return np.array(raw_sample.samples_raw)

    # If not create a new raw sampling
    distribution_dimension = len(sampling_scheme.scheme['distributions'].keys())
    samples_raw = sobol(m=2 ** 12, dimension=distribution_dimension, sets=1)
    samples_raw_id = sampling_interactions.upload_raw_samples(samples_raw, step)
    sampling_interactions.add_raw_samples_to_scheme(sampling_scheme, samples_raw_id)

    return samples_raw


def create_samples(sampling_scheme: sample_entry.Scheme) -> dict:
    # TODO - Create new samples based on the old ones and the sampling scheme
    # Loop through the sampling sequences and generate samples each time
    # Call Sobol to create new samples based on scheme and previous samples
    samples = dict()

    for step in range(sampling_scheme['settings']['sequence']):
        # if sampling sequence iteration exists download that.
        # if not create new sampling
        # used the sampling to create the distributions
        # return the raw samples and distributions
        raw_samples = get_raw_samples(sampling_scheme, step)
        samples_subset = compute_sampling_distributions(sampling_scheme, raw_samples)

        samples[step] = samples_subset

    return samples


def create_delphin_projects(sampling_scheme: dict, samples: dict) -> typing.List[str]:
    # TODO - Create new delphin files based on the samples
    # The paths for the base delphin files should be found in the sampling scheme
    # Permutate the base files according to the samples
    # Upload the new delphin files
    # Return the database ids for the delphin files

    delphin_ids = []
    # TODO - Create all delphin projects and load them as dicts
    delphin_dicts = []
    for index, delphin in enumerate(delphin_dicts):
        for parameter in samples.keys():
            if parameter == 'exterior heat transfer coefficient slope':
                # TODO - Figure out how to calculate the exchange slope
                delphin_permutations.change_boundary_coefficient(delphin, )

            elif parameter == 'exterior moisture transfer coefficient':
                outdoor_moisture_transfer = samples[parameter][index] * outdoor_heat_transfer
                delphin_permutations.change_boundary_coefficient(delphin, 'OutdoorVaporDiffusion',
                                                                 'ExchangeCoefficient', outdoor_moisture_transfer)

            elif parameter == 'solar absorption':
                delphin_permutations.change_boundary_coefficient(delphin, 'OutdoorShortWaveRadiation',
                                                                 'SurfaceAbsorptionCoefficient',
                                                                 samples[parameter][index])

            elif parameter == 'rain scale factor':
                delphin_permutations.change_boundary_coefficient(delphin, 'OutdoorWindDrivenRain',
                                                                 'ExposureCoefficient',
                                                                 samples[parameter][index])

            elif parameter == 'interior heat transfer coefficient':
                delphin_permutations.change_boundary_coefficient(delphin, 'IndoorHeatConduction',
                                                                 'ExchangeCoefficient',
                                                                 samples[parameter][index])

            elif parameter == 'interior moisture transfer coefficient':
                indoor_heat_transfer = samples['interior heat transfer coefficient'][index]
                indoor_moisture_transfer = samples[parameter][index] * indoor_heat_transfer
                delphin_permutations.change_boundary_coefficient(delphin, 'IndoorVaporDiffusion',
                                                                 'ExchangeCoefficient',
                                                                 indoor_moisture_transfer)

            elif parameter == 'interior sd value':
                delphin_permutations.change_boundary_coefficient(delphin, 'IndoorVaporDiffusion',
                                                                 'SDValue',
                                                                 samples[parameter][index])

            elif parameter == 'wall orientation':
                delphin_permutations.change_orientation(delphin, samples[parameter][index])

            elif parameter == 'wall core width':
                delphin_permutations.change_layer_width(delphin, 'Old Building Brick Dresden ZP [504]',
                                                        samples[parameter][index])

            elif parameter == 'wall core material':
                # TODO - Fix new material
                new_material = collections.OrderedDict()
                delphin_permutations.change_layer_material(delphin, 'Old Building Brick Dresden ZP [504]',
                                                           new_material)

            elif parameter == 'plaster width':
                delphin_permutations.change_layer_width(delphin, 'Lime cement mortar [717]',
                                                        samples[parameter][index])

            elif parameter == 'plaster material':
                # TODO - Fix new material
                new_material = collections.OrderedDict()
                delphin_permutations.change_layer_material(delphin, 'Lime cement mortar [717]',
                                                           new_material)

        delphin_ids.append(delphin_interactions.upload_delphin_dict_to_database(delphin, 1))

    # upload delphin

    start_years = samples['start year']
    years = []

    for index in range(len(delphin_ids)):
        weather_interactions.assign_weather_by_name_and_years(delphin_ids[index],
                                                              samples['exterior climate'][index], years[index])
        weather_interactions.assign_indoor_climate_to_project(delphin_ids[index],
                                                              samples['interior climate'][index])

    return delphin_ids


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
    for delphin_id in delphin_ids:
        delphin_doc = delphin_entry.Delphin.objects(id=delphin_id).first()
        sampling_document.update(push__delphin_ids=delphin_doc)

    return None


def calculate_error(delphin_ids):
    # TODO - Calculated the standard error on the results from the given delphin simulations
    # Return the error
    return None


def check_convergence(sampling_scheme, standard_error):
    # TODO - Check if the standard error is lower than the threshold value in the sampling scheme
    # If it is return True otherwise return False

    return None


def compute_sampling_distributions(sampling_scheme, samples_raw):
    scenarios = sampling_scheme['scenario'].keys()
    sample_parameters = sampling_scheme['distributions'].keys()
    distributions = dict()

    for scenario in scenarios.keys():

        for index, sample_param in enumerate(sample_parameters):
            sample_column = samples_raw[:, index]

            if sampling_scheme['distributions'][sample_param]['type'] == 'discrete':

                range_ = sampling_scheme['distributions'][sample_param]['range']
                if isinstance(range_, int):
                    high_bound = range_ + 1
                    values = randint.ppf(sample_column, low=1, high=high_bound).tolist()

                else:
                    high_bound = len(range_)
                    values = randint.ppf(sample_column, low=0, high=high_bound).tolist()

            elif sampling_scheme['distributions'][sample_param]['type'] == 'uniform':

                range_ = sampling_scheme['distributions'][sample_param]['range']
                values = uniform.ppf(sample_column, loc=range_[0], scale=range_[1] - range_[0]).tolist()

            elif sampling_scheme['distributions'][sample_param]['type'] == 'normal':

                range_ = sampling_scheme['distributions'][sample_param]['range']
                values = norm.ppf(sample_column, loc=range_[0], scale=range_[1]).tolist()

            else:
                raise KeyError(f'Unknown distribution for: {sample_param}. Distribution given was: '
                               f'{sampling_scheme["distributions"][sample_param]["type"]}')

            distributions[scenario][sample_param] = values

    return distributions


def sobol(m, dimension, sets=1):
    design = np.empty([0, dimension])

    for i in range(sets):
        d = sobol_lib.scrambled_sobol_generate(k=dimension, N=m, skip=2, leap=0)
        design = np.vstack((design, d))

    return design
