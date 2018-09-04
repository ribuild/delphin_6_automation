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
import typing
import copy

# RiBuild Modules
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import sampling_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.delphin_setup import delphin_permutations
from delphin_6_automation.file_parsing import delphin_parser
from delphin_6_automation.sampling import inputs
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.sampling import sobol_lib
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger(__name__)

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def create_sampling_strategy(path: str) -> dict:
    """
    Create a sampling strategy for WP6 Delphin Automation. The sampling strategy will be name 'sampling_strategy.json'
    and be located at the given folder.

    :param path: Folder, where the strategy will be saved.
    :type path: str
    :return: Created sampling strategy
    :rtype: dict
    """

    design = inputs.design_options()

    scenario = {'generic scenario': None}

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

                     'insulation width':
                         {'type': 'uniform', 'range': [0.01, 0.3], },

                     'start year':
                         {'type': 'discrete', 'range': [i for i in range(2020, 2046)], },
                     }

    sampling_settings = {'initial samples per set': 1,
                         'add samples per run': 1,
                         'max samples': 500,
                         'sequence': 10,
                         'standard error threshold': 0.1,
                         'raw sample size': 2 ** 9}

    combined_dict = {'design': design, 'scenario': scenario,
                     'distributions': distributions, 'settings': sampling_settings}

    with open(os.path.join(path, 'sampling_strategy.json'), 'w') as file:
        json.dump(combined_dict, file)

    logger.info(f'Created new sampling strategy')
    logger.debug(f'Saved sampling strategy to: {path}')

    return combined_dict


def load_strategy(path: str) -> dict:
    """
    Load a sampling strategy from a JSON file.

    :param path: Folder, where the sampling strategy is located
    :return: Sampling strategy
    """

    with open(os.path.join(path, 'sampling_strategy.json'), 'r') as file:
        sampling_strategy = json.load(file)

    logger.debug(f'Loads sampling strategy from {path}')

    return sampling_strategy


def load_latest_sample(sampling_strategy_id: str) -> typing.Optional[sample_entry.Sample]:
    """
    Look up the last existing sample entries in the database connected to the strategy
    If there is not previous samples in database return empty dict

    :param sampling_strategy_id: Sampling strategy id
    :return: Return the samples as a dict
    """

    strategy = sample_entry.Strategy.objects(id=sampling_strategy_id).first()

    if strategy.samples:
        samples_list = strategy.samples

        logger.debug(f'Found latest sample with ID: {samples_list[-1].id} for strategy with ID: {sampling_strategy_id}')

        return samples_list[-1]

    else:
        logger.debug(f'No samples found assosiated with strategy with ID: {sampling_strategy_id}')

        return None


def get_raw_samples(sampling_strategy: sample_entry.Strategy, step: int) -> np.ndarray:
    """
    Collects raw samples from database associated with sampling strategy. If the raw samples do not exists in
    the database new ones will be created by calling the Sobol function
    """

    sampling_strategy.reload()

    for raw_sample in sampling_strategy.samples_raw:
        if raw_sample.sequence_number == step:

            logger.debug(f'Found existing raw sample with sequence #{step}')

            return np.array(raw_sample.samples_raw)

    logger.debug(f'Creating new raw sample with sequence #{step}')

    distribution_dimension = len(sampling_strategy.strategy['distributions'].keys())
    samples_raw = sobol(m=sampling_strategy.strategy['settings']['raw sample size'],
                        dimension=distribution_dimension, sets=1)
    samples_raw_id = sampling_interactions.upload_raw_samples(samples_raw, step)
    sampling_interactions.add_raw_samples_to_strategy(sampling_strategy, samples_raw_id)

    return samples_raw


def sample_exists(sampling_strategy: sample_entry.Strategy) -> typing.Optional[sample_entry.Sample]:
    """Check whether a sample exists with the same iteration as the current iteration in the sampling strategy"""

    sample = load_latest_sample(sampling_strategy.id)
    if sample and sample.iteration == sampling_strategy.current_iteration:

        logger.info(f'Found existing sample for the current sampling iteration #{sampling_strategy.current_iteration}')

        return sample

    else:
        return None


def create_samples(sampling_strategy: sample_entry.Strategy, used_samples_per_set: int) -> dict:
    """
    Creates new samples fitting the sampling strategy. Raw samples are generated if they do not exist already.
    The function loops through the sampling sequences and generate samples each time.

    :param sampling_strategy: Sampling Strategy
    :param used_samples_per_set: How many samples should be generated per set
    :return: The generated samples
    """

    samples = dict()

    for step in range(sampling_strategy.strategy['settings']['sequence']):

        logger.debug(f'Generates samples for sequence #{step}')

        raw_samples = get_raw_samples(sampling_strategy, step)
        samples_subset = compute_sampling_distributions(sampling_strategy.strategy, raw_samples,
                                                        used_samples_per_set)

        samples[str(step)] = samples_subset

    return samples


def load_design_options(designs: typing.List[str], folder: str) -> typing.List[dict]:
    """Loads the Delphin files into memory associated with the design options"""

    delphin_projects = []

    logger.debug(f'Loads {len(designs)} design Delphin projects')

    for design in designs:
        delphin_projects.append(delphin_parser.dp6_to_dict(os.path.join(folder, f'{design}.d6p')))

    return delphin_projects


def create_delphin_projects(sampling_strategy: dict, samples: dict,
                            folder=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'input_files/design')) \
        -> typing.List[str]:
    """Generate the Delphin project associated with the given sample"""

    delphin_ids = []
    delphin_projects = load_design_options(sampling_strategy['design'], folder)

    for sequence in samples.keys():

        logger.debug(f'Generates Delphin projects for sequence #{sequence}')

        for design in samples[sequence].keys():

            logger.debug(f'Generates Delphin projects for design: {design}')

            sample_dict = dict()
            design_index = sampling_strategy['design'].index(design)
            design_variation = copy.deepcopy(delphin_projects[design_index])

            for parameter in samples[sequence][design]['generic scenario'].keys():
                if parameter == 'exterior heat transfer coefficient slope':
                    delphin_permutations.change_boundary_coefficient(design_variation, 'OutdoorHeatConduction',
                                                                     'ExchangeSlope',
                                                                     samples[sequence][design][
                                                                         'generic scenario'][parameter][0])
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'exterior moisture transfer coefficient':
                    outdoor_moisture_transfer = \
                        delphin_permutations.compute_vapour_diffusion_slope(
                            samples[sequence][design]['generic scenario'][
                                'exterior heat transfer coefficient slope'][0],
                            samples[sequence][design]['generic scenario'][parameter][0])

                    delphin_permutations.change_boundary_coefficient(design_variation, 'OutdoorVaporDiffusion',
                                                                     'ExchangeSlope', outdoor_moisture_transfer[0])
                    delphin_permutations.change_boundary_coefficient(design_variation, 'OutdoorVaporDiffusion',
                                                                     'ExchangeCoefficient', outdoor_moisture_transfer[1])
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'solar absorption':
                    delphin_permutations.change_boundary_coefficient(design_variation, 'OutdoorShortWaveRadiation',
                                                                     'SurfaceAbsorptionCoefficient',
                                                                     samples[sequence][design][
                                                                         'generic scenario'][parameter][0])
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'rain scale factor':
                    delphin_permutations.change_boundary_coefficient(design_variation, 'OutdoorWindDrivenRain',
                                                                     'ExposureCoefficient',
                                                                     samples[sequence][design][
                                                                         'generic scenario'][parameter][0])
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'interior heat transfer coefficient':
                    delphin_permutations.change_boundary_coefficient(design_variation, 'IndoorHeatConduction',
                                                                     'ExchangeCoefficient',
                                                                     samples[sequence][design][
                                                                         'generic scenario'][parameter][0])
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'interior moisture transfer coefficient':
                    indoor_heat_transfer = samples[sequence][design]['generic scenario'][
                        'interior heat transfer coefficient'][0]
                    indoor_moisture_transfer = samples[sequence][design][
                                                   'generic scenario'][parameter][0] * indoor_heat_transfer
                    delphin_permutations.change_boundary_coefficient(design_variation, 'IndoorVaporDiffusion',
                                                                     'ExchangeCoefficient',
                                                                     indoor_moisture_transfer)
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'interior sd value':
                    delphin_permutations.change_boundary_coefficient(design_variation, 'IndoorVaporDiffusion',
                                                                     'SDValue',
                                                                     samples[sequence][design][
                                                                         'generic scenario'][parameter][0])
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'wall orientation':
                    delphin_permutations.change_orientation(design_variation, samples[sequence][design][
                        'generic scenario'][parameter][0])
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'wall core width':
                    delphin_permutations.change_layer_width(design_variation, 'Old Building Brick Dresden ZP [504]',
                                                            samples[sequence][design]['generic scenario'][parameter][0])
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'wall core material':
                    new_material = material_interactions.get_material_info(samples[sequence][design][
                                                                               'generic scenario'][parameter][0])
                    delphin_permutations.change_layer_material(design_variation, 'Old Building Brick Dresden ZP [504]',
                                                               new_material)
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'plaster width':
                    delphin_permutations.change_layer_width(design_variation, 'Lime cement mortar [717]',
                                                            samples[sequence][design]['generic scenario'][parameter][0])
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

                elif parameter == 'plaster material':
                    new_material = material_interactions.get_material_info(samples[sequence][design][
                                                                               'generic scenario'][parameter][0])
                    delphin_permutations.change_layer_material(design_variation, 'Lime cement mortar [717]',
                                                               new_material)
                    sample_dict[parameter] = samples[sequence][design]['generic scenario'][parameter][0]

            # Upload project
            delphin_permutations.update_output_locations(design_variation)
            delphin_id = delphin_interactions.upload_delphin_dict_to_database(design_variation, 1)

            start_year = int(samples[sequence][design]['generic scenario']['start year'][0])
            years = [start_year, ] + [year for year in range(start_year, start_year + 6)]
            weather_interactions.assign_weather_by_name_and_years(delphin_id,
                                                                  samples[sequence][design][
                                                                      'generic scenario']['exterior climate'][0], years)
            weather_interactions.assign_indoor_climate_to_project(delphin_id,
                                                                  samples[sequence][design][
                                                                      'generic scenario']['interior climate'][0])
            delphin_interactions.change_entry_simulation_length(delphin_id, len(years), 'a')

            sample_dict['start year'] = samples[sequence][design]['generic scenario']['start year'][0]
            sample_dict['exterior climate'] = samples[sequence][design]['generic scenario']['exterior climate'][0]
            sample_dict['interior climate'] = samples[sequence][design]['generic scenario']['interior climate'][0]
            sample_dict['design_option'] = create_design_info(design)
            sample_dict['sequence'] = sequence

            delphin_interactions.add_sampling_dict(delphin_id, sample_dict)

            delphin_ids.append(delphin_id)

    return delphin_ids


def create_design_info(design: str) -> dict:

    design_data = design.split('_')
    if len(design_data) == 7:
        design_info = {'exterior_plaster': design_data[1] == 'exterior',
                       'system_name': design_data[2],
                       'insulation_material': int(design_data[3]),
                       'finish_material': int(design_data[4]),
                       'detail_material': int(design_data[5]),
                       'insulation_thickness': int(design_data[6]),
                       }

    elif len(design_data) == 6:
        design_info = {'exterior_plaster': design_data[1] == 'exterior',
                       'system_name': design_data[2],
                       'insulation_material': int(design_data[3]),
                       'finish_material': int(design_data[4]),
                       'detail_material': None,
                       'insulation_thickness': int(design_data[5]),
                       }

    elif len(design_data) == 2:
        design_info = {'exterior_plaster': design_data[1] == 'exterior',
                       'system_name': None,
                       'insulation_material': None,
                       'finish_material': None,
                       'detail_material': None,
                       'insulation_thickness': None,
                       }
    else:
        error = f'Unknown design string. Given design was: {design}'
        logger.error(error)
        raise ValueError(error)

    return design_info


def calculate_error(sample_strategy: sample_entry.Strategy) -> dict:
    """Calculates the standard error on the results from the given delphin simulations"""

    standard_error = dict()
    sequence_length = sample_strategy.strategy['settings']['sequence']
    sample = load_latest_sample(sample_strategy.id)
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

        design_standard_error = {'mould': relative_standard_error(mould[design], sequence_length),
                                 'heat_loss': relative_standard_error(heat_loss[design], sequence_length)}

        standard_error[design] = design_standard_error

    return standard_error


def relative_standard_error(series: list, sequence_length: int) -> float:
    """
    Calculate the relative standard error

    Source:
    Hou, T, et. al.
    Quasi-Monte Carlo based uncertainty analysis: sampling effciency and error estimation
    Reliability Engineering & System Safety
    2018
    """

    series = np.asarray(series)
    standard_error = np.sqrt(1/(sequence_length * (sequence_length - 1)) * np.sum((series - np.mean(series)) ** 2))

    mean_standard_error = standard_error / np.mean(series)

    logger.debug(f'Mean Standard Error was: {mean_standard_error}')

    return mean_standard_error


def check_convergence(strategy_document: sample_entry.Strategy) -> bool:
    """
    Check if the standard error is lower than the threshold value in the sampling strategy
    If it is return True otherwise return False
    """

    standard_error = strategy_document.standard_error
    checks = [standard_error[design][damage_model][-1]
              for design in standard_error.keys()
              for damage_model in standard_error[design].keys()]

    logger.debug(f'Current standard errors: {checks}')
    if all(check <= strategy_document.strategy['settings']['standard error threshold']
           for check in checks):
        logger.info(f'Convergence found')
        return True
    else:
        logger.info(f'Convergence not found')
        return False


def compute_sampling_distributions(sampling_strategy: dict, samples_raw: np.ndarray, used_samples_per_set: int) -> dict:
    """Compute the sampling values for the sampling strategy"""

    designs = [design_
               for design_ in sampling_strategy['design']]

    scenarios = sampling_strategy['scenario'].keys()
    sample_parameters = sampling_strategy['distributions'].keys()
    distributions = dict()
    new_samples_per_set = sampling_strategy['settings']['initial samples per set']
    samples_raw = samples_raw[used_samples_per_set:used_samples_per_set + new_samples_per_set, :]

    for design in designs:
        distributions[design] = dict()

        for scenario in scenarios:
            distributions[design][scenario] = dict()

            for index, sample_param in enumerate(sample_parameters):
                sample_column = samples_raw[:, index]

                if sampling_strategy['distributions'][sample_param]['type'] == 'discrete':

                    range_ = sampling_strategy['distributions'][sample_param]['range']
                    if isinstance(range_, int):
                        high_bound = range_ + 1
                        values = randint.ppf(sample_column, low=1, high=high_bound).tolist()

                    else:
                        high_bound = len(range_)
                        values = randint.ppf(sample_column, low=0, high=high_bound).astype('int64').tolist()
                        values = [range_[x] for x in values]

                elif sampling_strategy['distributions'][sample_param]['type'] == 'uniform':

                    range_ = sampling_strategy['distributions'][sample_param]['range']
                    values = uniform.ppf(sample_column, loc=range_[0], scale=range_[1] - range_[0]).tolist()

                elif sampling_strategy['distributions'][sample_param]['type'] == 'normal':

                    range_ = sampling_strategy['distributions'][sample_param]['range']
                    values = norm.ppf(sample_column, loc=range_[0], scale=range_[1]).tolist()

                else:
                    raise KeyError(f'Unknown distribution for: {sample_param}. Distribution given was: '
                                   f'{sampling_strategy["distributions"][sample_param]["type"]}')

                distributions[design][scenario][sample_param] = values

    logger.debug(f'Finished computing sampling distributions')

    return distributions


def sobol(m: int, dimension: int, sets: int=1) -> np.ndarray:
    """Compute the Sobol sequence"""

    design = np.empty([0, dimension])

    for i in range(sets):
        d = sobol_lib.scrambled_sobol_generate(k=dimension, N=m, skip=2, leap=0)
        design = np.vstack((design, d))

    logger.debug(f'Created {m}x{dimension} Sobol matrix')

    return design


def calculate_sample_output(sample_strategy: dict, sampling_id: str) -> None:
    """Compute the mean and standard deviation of the simulation results for a given sample"""

    sample_mean = dict()
    sample_std = dict()
    sequence = sample_strategy['settings']['sequence']

    for sequence_index in range(sequence):

        logger.debug(f'Calculates the sample output for sequence #{sequence_index}')

        sample_mean[str(sequence_index)] = dict()
        sample_std[str(sequence_index)] = dict()

        for design in sample_strategy['design']:
            design_dict = create_design_info(design)
            projects_given_design = delphin_entry.Delphin.objects(sample_data__design_option=design_dict,
                                                                  sample_data__sequence=str(sequence_index))
            mould = []
            heat_loss = []

            # TODO - Speed up this with a better query
            for project in projects_given_design:
                mould.append(project.result_processed['thresholds']['mould'])
                heat_loss.append(project.result_processed['thresholds']['heat_loss'])

            sample_mean[str(sequence_index)][design] = {'mould': np.mean(mould),
                                                        'heat_loss': np.mean(heat_loss)}
            sample_std[str(sequence_index)][design] = {'mould': np.std(mould),
                                                       'heat_loss': np.std(heat_loss)}

            logger.debug(f'Sample mean: {sample_mean[str(sequence_index)][design]} for design: {design}')
            logger.debug(f'Sample std: {sample_std[str(sequence_index)][design]} for design: {design}')

    sampling_interactions.upload_sample_mean(sampling_id, sample_mean)
    sampling_interactions.upload_sample_std(sampling_id, sample_std)

    return None


def initialize_sampling(strategy_doc: sample_entry.Strategy) -> tuple:
    """Initialize a sampling"""

    iteration = strategy_doc.current_iteration
    convergence = False
    new_samples_per_set = strategy_doc.strategy['settings']['initial samples per set']
    used_samples_per_set = strategy_doc.used_samples_per_set

    logger.info('Initializing sampling scheme')
    logger.info(f'Iteration: {iteration}')
    logger.info(f'Convergence: {convergence}')
    logger.info(f'New Samples per Set: {new_samples_per_set}')
    logger.info(f'Used Samples per Set: {used_samples_per_set}\n')

    return iteration, convergence, new_samples_per_set, used_samples_per_set
