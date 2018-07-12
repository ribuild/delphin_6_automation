__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import json
import os
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
from delphin_6_automation.sampling import sobol_lib


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def create_sampling_strategy(path: str) -> dict:
    """
    Create a sampling strategy for WP6 Delphin Automation. The sampling strategy will be name 'sampling_strategy.json' and
    be located at the given folder.

    :param path: Folder, where the strategy will be saved.
    :type path: str
    :return: Created sampling strategy
    :rtype: dict
    """

    design = {'construction type':
                   {'type': 'discrete',
                    'range': inputs.construction_types()}}

    scenario = {}

    distributions = {'exterior climate':
                         {'type': 'discrete', 'range': list(general_interactions.list_weather_stations().keys())},

                     'exterior heat transfer coefficient slope':
                         {'type': 'uniform', 'range': [1, 4], },

                     'exterior moisture transfer coefficient':
                         {'type': 'uniform', 'range': [4 * 10 ** -9, 10 ** -8], },

                     'solar absorption':
                         {'type': 'uniform', 'range': [0.4, 0.8], },

                     'rain scale factor':
                         {'type': 'uniform', 'range': [0, 2], },

                     'interior climate':
                         {'type': 'discrete', 'range': ['a', 'b'], },

                     'interior heat transfer coefficient':
                         {'type': 'uniform', 'range': [5, 10], },

                     'interior moisture transfer coefficient':
                         {'type': 'uniform', 'range': [4 * 10 ** -9, 10 ** -8], },

                     'interior sd value':
                         {'type': 'uniform', 'range': [0.0, 0.6], },

                     'wall orientation':
                         {'type': 'uniform', 'range': [0, 360], },

                     'wall core width':
                         {'type': 'uniform', 'range': [0.1, 0.9], },

                     'wall core material':
                         {'type': 'discrete', 'range': inputs.wall_core_materials(), },

                     'plaster width':
                         {'type': 'uniform', 'range': [0.01, 0.02], },

                     'plaster material':
                         {'type': 'discrete', 'range': inputs.plaster_materials(), },

                     'insulation type':
                         {'type': 'discrete', 'range': inputs.insulation_type(), },

                     'insulation width':
                         {'type': 'uniform', 'range': [0.01, 0.3], },

                     'start year':
                         {'type': 'discrete', 'range': 24, },
                     }

    sampling_settings = {'initial samples per set': 1,
                         'add samples per run': 1,
                         'max samples': 500,
                         'sequence': 10,
                         'standard error threshold': 0.1}

    combined_dict = {'design': design, 'scenario': scenario,
                     'distributions': distributions, 'settings': sampling_settings}

    with open(os.path.join(path, 'sampling_strategy.json'), 'w') as file:
        json.dump(combined_dict, file)

    return combined_dict


def load_strategy(path: str) -> dict:
    """
    Load a sampling strategy from a JSON file.

    :param path: Folder, where the sampling strategy is located
    :type path: string
    :return: Sampling strategy
    :rtype: dict
    """

    with open(os.path.join(path, 'sampling_strategy.json'), 'r') as file:
        sampling_strategy = json.load(file)

    return sampling_strategy


def load_existing_samples(sampling_strategy_id):
    """
    Look up the existing sample entries in the database connected to the strategy
    If there is not previous samples in database return empty dict

    :param sampling_strategy_id: Sampling strategy id
    :type sampling_strategy_id: str
    :return: Return the samples as a dict
    :rtype: dict
    """

    strategy = sample_entry.Strategy.objects(id=sampling_strategy_id).first()

    if strategy.samples:
        samples_list = strategy.samples
        samples = samples_list[0].samples

        for sample in samples_list[1:]:

            for parameter in sample.keys():
                samples[parameter]['sample_values'].append(sample[parameter]['sample_values'])

        return samples

    else:
        return {}


def load_latest_sample(sampling_strategy_id: str) -> dict:
    """
    Look up the last existing sample entries in the database connected to the strategy
    If there is not previous samples in database return empty dict

    :param sampling_strategy_id: Sampling strategy id
    :type sampling_strategy_id: str
    :return: Return the samples as a dict
    :rtype: dict
    """

    strategy = sample_entry.Strategy.objects(id=sampling_strategy_id).first()

    if strategy.samples:
        samples_list = strategy.samples
        return samples_list[-1].samples

    else:
        return {}


def get_raw_samples(sampling_strategy: sample_entry.Strategy, step: int) -> np.array:
    sampling_strategy.reload()

    # Check if the strategy has a raw sampling with the same sequence number as step
    for raw_sample in sampling_strategy.samples_raw:
        if raw_sample.sequence_number == step:
            return np.array(raw_sample.samples_raw)

    # If not create a new raw sampling
    distribution_dimension = len(sampling_strategy.strategy['distributions'].keys())
    samples_raw = sobol(m=2 ** 12, dimension=distribution_dimension, sets=1)
    samples_raw_id = sampling_interactions.upload_raw_samples(samples_raw, step)
    sampling_interactions.add_raw_samples_to_strategy(sampling_strategy, samples_raw_id)

    return samples_raw


def create_samples(sampling_strategy: sample_entry.Strategy) -> dict:
    # TODO - Create new samples based on the old ones and the sampling strategy
    # Loop through the sampling sequences and generate samples each time
    # Call Sobol to create new samples based on strategy and previous samples
    samples = dict()

    for step in range(sampling_strategy['settings']['sequence']):
        # if sampling sequence iteration exists download that.
        # if not create new sampling
        # used the sampling to create the distributions
        # return the raw samples and distributions
        raw_samples = get_raw_samples(sampling_strategy, step)
        samples_subset = compute_sampling_distributions(sampling_strategy, raw_samples)

        samples[step] = samples_subset

    return samples


def create_delphin_projects(sampling_strategy: dict, samples: dict) -> typing.List[str]:
    # TODO - Create new delphin files based on the samples
    # The paths for the base delphin files should be found in the sampling strategy
    # Permutate the base files according to the samples
    # Upload the new delphin files
    # Return the database ids for the delphin files

    delphin_ids = []
    # TODO - Create all delphin projects and load them as dicts
    delphin_dicts = []
    for index, delphin in enumerate(delphin_dicts):
        sample_dict = dict()

        for parameter in samples.keys():
            if parameter == 'exterior heat transfer coefficient slope':
                delphin_permutations.change_boundary_coefficient(delphin, 'OutdoorHeatConduction',
                                                                 'ExchangeSlope', samples[parameter][index])
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'exterior moisture transfer coefficient':
                outdoor_moisture_transfer = \
                    delphin_permutations.compute_vapour_diffusion_slope(
                        samples['exterior heat transfer coefficient slope'][index], samples[parameter][index])

                delphin_permutations.change_boundary_coefficient(delphin, 'OutdoorVaporDiffusion',
                                                                 'ExchangeSlope', outdoor_moisture_transfer[0])
                delphin_permutations.change_boundary_coefficient(delphin, 'OutdoorVaporDiffusion',
                                                                 'ExchangeCoefficient', outdoor_moisture_transfer[1])
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'solar absorption':
                delphin_permutations.change_boundary_coefficient(delphin, 'OutdoorShortWaveRadiation',
                                                                 'SurfaceAbsorptionCoefficient',
                                                                 samples[parameter][index])
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'rain scale factor':
                delphin_permutations.change_boundary_coefficient(delphin, 'OutdoorWindDrivenRain',
                                                                 'ExposureCoefficient',
                                                                 samples[parameter][index])
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'interior heat transfer coefficient':
                delphin_permutations.change_boundary_coefficient(delphin, 'IndoorHeatConduction',
                                                                 'ExchangeCoefficient',
                                                                 samples[parameter][index])
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'interior moisture transfer coefficient':
                indoor_heat_transfer = samples['interior heat transfer coefficient'][index]
                indoor_moisture_transfer = samples[parameter][index] * indoor_heat_transfer
                delphin_permutations.change_boundary_coefficient(delphin, 'IndoorVaporDiffusion',
                                                                 'ExchangeCoefficient',
                                                                 indoor_moisture_transfer)
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'interior sd value':
                delphin_permutations.change_boundary_coefficient(delphin, 'IndoorVaporDiffusion',
                                                                 'SDValue',
                                                                 samples[parameter][index])
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'wall orientation':
                delphin_permutations.change_orientation(delphin, samples[parameter][index])
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'wall core width':
                delphin_permutations.change_layer_width(delphin, 'Old Building Brick Dresden ZP [504]',
                                                        samples[parameter][index])
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'wall core material':
                # TODO - Fix new material
                new_material = collections.OrderedDict()
                delphin_permutations.change_layer_material(delphin, 'Old Building Brick Dresden ZP [504]',
                                                           new_material)
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'plaster width':
                delphin_permutations.change_layer_width(delphin, 'Lime cement mortar [717]',
                                                        samples[parameter][index])
                sample_dict[parameter] = samples[parameter][index]

            elif parameter == 'plaster material':
                new_material = collections.OrderedDict()
                delphin_permutations.change_layer_material(delphin, 'Lime cement mortar [717]',
                                                           new_material)
                sample_dict[parameter] = samples[parameter][index]

        # Upload project
        delphin_id = delphin_interactions.upload_delphin_dict_to_database(delphin, 1)

        start_year = samples['start year'][index]
        years = [start_year, ] + [year for year in range(start_year, start_year + 5)]
        weather_interactions.assign_weather_by_name_and_years(delphin_id,
                                                              samples['exterior climate'][index], years)
        weather_interactions.assign_indoor_climate_to_project(delphin_ids[index],
                                                              samples['interior climate'][index])
        sample_dict['start year'] = samples['start year'][index]
        sample_dict['exterior climate'] = samples['exterior climate'][index]
        sample_dict['interior climate'] = samples['interior climate'][index]
        delphin_interactions.add_sampling_dict(delphin_id, sample_dict)

        delphin_ids.append(delphin_id)

    return delphin_ids


def calculate_error(delphin_ids):
    # TODO - Calculated the standard error on the results from the given delphin simulations
    # Return the error
    return None


def check_convergence(sampling_strategy, standard_error):
    # TODO - Check if the standard error is lower than the threshold value in the sampling strategy
    # If it is return True otherwise return False

    return None


def compute_sampling_distributions(sampling_strategy, samples_raw):
    scenarios = sampling_strategy['scenario'].keys()
    sample_parameters = sampling_strategy['distributions'].keys()
    distributions = dict()

    for scenario in scenarios.keys():

        for index, sample_param in enumerate(sample_parameters):
            sample_column = samples_raw[:, index]

            if sampling_strategy['distributions'][sample_param]['type'] == 'discrete':

                range_ = sampling_strategy['distributions'][sample_param]['range']
                if isinstance(range_, int):
                    high_bound = range_ + 1
                    values = randint.ppf(sample_column, low=1, high=high_bound).tolist()

                else:
                    high_bound = len(range_)
                    values = randint.ppf(sample_column, low=0, high=high_bound).tolist()

            elif sampling_strategy['distributions'][sample_param]['type'] == 'uniform':

                range_ = sampling_strategy['distributions'][sample_param]['range']
                values = uniform.ppf(sample_column, loc=range_[0], scale=range_[1] - range_[0]).tolist()

            elif sampling_strategy['distributions'][sample_param]['type'] == 'normal':

                range_ = sampling_strategy['distributions'][sample_param]['range']
                values = norm.ppf(sample_column, loc=range_[0], scale=range_[1]).tolist()

            else:
                raise KeyError(f'Unknown distribution for: {sample_param}. Distribution given was: '
                               f'{sampling_strategy["distributions"][sample_param]["type"]}')

            distributions[scenario][sample_param] = values

    return distributions


def sobol(m, dimension, sets=1):
    design = np.empty([0, dimension])

    for i in range(sets):
        d = sobol_lib.scrambled_sobol_generate(k=dimension, N=m, skip=2, leap=0)
        design = np.vstack((design, d))

    return design
