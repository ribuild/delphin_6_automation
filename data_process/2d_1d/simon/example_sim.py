__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import json
import pandas as pd
import xmltodict
import shutil

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_2d_1d as auth_dict
from delphin_6_automation.sampling import inputs
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.delphin_setup import delphin_permutations
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)


def create_2d_designs(folder=r'C:\Users\ocni\Desktop\1D-2D\2D'):
    bricks = pd.read_excel(os.path.join(folder, 'Brick.xlsx'))
    plasters = pd.read_excel(os.path.join(folder, 'Plaster.xlsx'))
    ref_folder = os.path.join(folder, 'delphin')

    for file in os.listdir(ref_folder):
        delphin_dict = delphin_parser.dp6_to_dict(os.path.join(ref_folder, file))

        for p_index, p_id in enumerate(plasters['Material ID']):
            new_material = material_interactions.get_material_info(p_id)
            plaster_delphin = delphin_permutations.change_layer_material(delphin_dict,
                                                                         'Lime cement mortar [717]',
                                                                         new_material)

            for index, mat_id in enumerate(bricks['Material ID']):
                new_material = material_interactions.get_material_info(mat_id)
                new_delphin = delphin_permutations.change_layer_material(plaster_delphin,
                                                                         'Old Building Brick Dresden ZP [504]',
                                                                         new_material)
                file_name = f'{file.split(".")[0]}_{plasters.iloc[p_index, 1]}_{bricks.iloc[index, 1]}.d6p'
                xmltodict.unparse(new_delphin,
                                  output=open(os.path.join(folder, 'design', file_name),
                                              'w'), pretty=True)


def create_1d_designs(folder=r'C:\Users\ocni\Desktop\1D-2D\1D'):
    bricks = pd.read_excel(os.path.join(folder, 'Brick.xlsx'))
    plasters = pd.read_excel(os.path.join(folder, 'Plaster.xlsx'))

    ref_folder = os.path.join(folder, 'delphin')
    temp_folder = os.path.join(folder, 'temp')

    thickness = [0.24, 0.36, 0.48]

    for file in os.listdir(ref_folder):
        for thick in thickness:
            delphin_dict = delphin_parser.dp6_to_dict(os.path.join(ref_folder, file))
            thick_delphin = delphin_permutations.change_layer_width(delphin_dict,
                                                                    'Old Building Brick Dresden ZP [504]',
                                                                    thick)

            for p_index, p_id in enumerate(plasters['Material ID']):
                new_material = material_interactions.get_material_info(p_id)
                new_delphin = delphin_permutations.change_layer_material(thick_delphin,
                                                                         'Lime cement mortar [717]',
                                                                         new_material)
                file_name = '_'.join(file.split('_')[:1]) + f'_{int(thick*100)}cm_1D_{plasters.iloc[p_index, 1]}.d6p'
                xmltodict.unparse(new_delphin,
                                  output=open(os.path.join(temp_folder, file_name),
                                              'w'), pretty=True)

    for file in os.listdir(temp_folder):
        delphin_dict = delphin_parser.dp6_to_dict(os.path.join(temp_folder, file))

        for index, mat_id in enumerate(bricks['Material ID']):
            new_material = material_interactions.get_material_info(mat_id)
            new_delphin = delphin_permutations.change_layer_material(delphin_dict,
                                                                     'Old Building Brick Dresden ZP [504]',
                                                                     new_material)
            file_name = f'{file.split(".")[0]}_{bricks.iloc[index, 1]}.d6p'
            xmltodict.unparse(new_delphin,
                              output=open(os.path.join(folder, 'design', file_name),
                                          'w'), pretty=True)


def create_sampling_strategy(path: str, design_option) -> dict:
    """
    Create a sampling strategy for WP6 Delphin Automation. The sampling strategy will be name 'sampling_strategy.json'
    and be located at the given folder.

    :param path: Folder, where the strategy will be saved.
    :type path: str
    :return: Created sampling strategy
    :rtype: dict
    """

    design = design_option

    scenario = {'generic_scenario': None}

    distributions = {'exterior_climate':
                         {'type': 'discrete', 'range': ['Weimar', 'Bremen', 'MuenchenAirp']},

                     'exterior_heat_transfer_coefficient_slope':
                         {'type': 'uniform', 'range': [1, 4], },

                     'solar_absorption':
                         {'type': 'uniform', 'range': [0.4, 0.8], },

                     'rain_scale_factor':
                         {'type': 'uniform', 'range': [0, 2], },

                     'interior_climate':
                         {'type': 'discrete', 'range': ['a', 'b'], },

                     'wall_orientation':
                         {'type': 'uniform', 'range': [0, 360], },

                     'plaster_material':
                         {'type': 'discrete', 'range': inputs.plaster_materials(r'C:\Users\ocni\Desktop\1D-2D'), },

                     'start_year':
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

    return combined_dict


def copy_designs(folder=r'C:\Users\ocni\Desktop\1D-2D'):
    folder_1d = os.path.join(folder, '1D', 'design')
    folder_2d = os.path.join(folder, '2D', 'design')
    dst_folder = os.path.join(folder, 'designs')

    print('Copy 1D')
    for file1d in os.listdir(folder_1d):
        shutil.copyfile(os.path.join(folder_1d, file1d), os.path.join(dst_folder, file1d))

    print('Copy 2D')
    for file2d in os.listdir(folder_2d):
        shutil.copyfile(os.path.join(folder_2d, file2d), os.path.join(dst_folder, file2d))


create_1d_designs()
# create_2d_designs()
# copy_designs()

design_options = os.listdir(r'C:\Users\ocni\Desktop\1D-2D\designs')
# create_sampling_strategy(r'C:\Users\ocni\Desktop\1D-2D\sampling_strategy', design_options)

mongo_setup.global_end_ssh(server)
