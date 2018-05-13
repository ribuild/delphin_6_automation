__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import os
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import linregress
import datetime

# RiBuild Modules
from delphin_6_automation.file_parsing import delphin_parser
from delphin_6_automation.delphin_setup import damage_models


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


# Functions
def acronym_table(path):
    table_ = pd.read_excel(path).dropna()

    return table_


def match_2d_1d(acronym_table_):
    map_dict = {}

    for index, acro in enumerate(acronym_table_['Acronym']):
        if acro.endswith('_2d'):
            map_dict[acro[:-3]]['2d'] = acronym_table_['Result ID'].iloc[index]

        elif acro.startswith('mortar'):
            looking_for_acro = acro[7:-3]

            for acro_key in map_dict.keys():
                if looking_for_acro in acro_key:
                    map_dict[acro_key]['mortar'] = acronym_table_['Result ID'].iloc[index]
        else:
            map_dict.setdefault(acro[:-3], dict())
            map_dict[acro[:-3]]['brick'] = acronym_table_['Result ID'].iloc[index]

    return map_dict


def load_results(folder, quantity, acro_dict):
    df = pd.DataFrame()

    indices = 0
    result_folder_ = f"{folder}/{acro_dict['brick']}/results"
    for file in os.listdir(result_folder_):
        if quantity in file:
            value_dict = delphin_parser.d6o_to_dict(result_folder_, file)[0]['result']
            cell = list(value_dict.keys())[0]
            values = value_dict[cell]
            df[file.split('.')[0][-1]] = values
            indices += 1

    df.index = pd.DatetimeIndex(start=datetime.datetime(2020, 1, 1),
                                freq='h', periods=len(values))
    df.columns = pd.MultiIndex.from_arrays([df.columns, ['brick', ] * indices, ['out', ] * indices],
                                           names=['location', 'simulation type', 'value type'])

    indices = 0
    result_folder_ = f"{folder}/{acro_dict['mortar']}/results"
    for file in os.listdir(result_folder_):
        if quantity in file:
            value_dict = delphin_parser.d6o_to_dict(result_folder_, file)[0]['result']
            cell = list(value_dict.keys())[0]
            values = value_dict[cell]
            df[file.split('.')[0][-1], 'mortar', 'out'] = values
            indices += 1

    indices = 0
    result_folder_ = f"{folder}/{acro_dict['2d']}/results"
    for file in os.listdir(result_folder_):
        if quantity in file:
            value_dict = delphin_parser.d6o_to_dict(result_folder_, file)[0]['result']
            cell = list(value_dict.keys())[0]
            values = value_dict[cell]
            df[file.split('.')[0][-1], '2d', 'out'] = values
            indices += 1

    df = df.sort_index(axis=1)
    return df


def abs_diff(x1, x2):
    return x2 - x1


def rel_diff(x1, x2):
    return np.absolute(x2 - x1) / np.absolute(x2) * 100


def compute_differences(data_frame):
    for column in data_frame.columns.levels[0]:
        data_frame[column, 'brick', 'rel_diff'] = rel_diff(data_frame[column, 'brick', 'out'],
                                                           data_frame[column, '2d', 'out'])
        data_frame[column, 'brick', 'abs_diff'] = abs_diff(data_frame[column, 'brick', 'out'],
                                                           data_frame[column, '2d', 'out'])

        data_frame[column, 'mortar', 'rel_diff'] = rel_diff(data_frame[column, 'mortar', 'out'],
                                                            data_frame[column, '2d', 'out'])
        data_frame[column, 'mortar', 'abs_diff'] = abs_diff(data_frame[column, 'mortar', 'out'],
                                                            data_frame[column, '2d', 'out'])

    data_frame = data_frame.sort_index(axis=1)
    return data_frame


def save_to_hdf(data_frame, acronym, quantity, folder):

    hdf_file = folder + f'/{quantity}.h5'
    data_frame.to_hdf(hdf_file, acronym, append=True)


def process_results(excel_file, result_folder, out_folder):

    table = acronym_table(excel_file)
    map_ = match_2d_1d(table)

    quantities = ['heat loss', 'temperature', 'relative humidity', 'moisture content', 'moisture integral']

    for quantity in quantities:
        for acronym in map_.keys():
            new_table = load_results(result_folder, quantity, map_[acronym])
            new_table = compute_differences(new_table)
            save_to_hdf(new_table, acronym, quantity, out_folder)

        create_totals(out_folder, quantity)


def create_totals(out_folder, quantity):
    hdf_file = out_folder + '/' + quantity + '.h5'
    store = pd.HDFStore(hdf_file)

    store_names = {'1a': {'48': {'insulated': [], 'uninsulated': []},
                          '36': {'insulated': [], 'uninsulated': []},
                          '24': {'insulated': [], 'uninsulated': []}
                          },
                   '2a': {'48': {'insulated': [], 'uninsulated': []},
                          '36': {'insulated': [], 'uninsulated': []},
                          '24': {'insulated': [], 'uninsulated': []}
                          },
                   '3a': {'48': {'insulated': [], 'uninsulated': []},
                          '36': {'insulated': [], 'uninsulated': []},
                          '24': {'insulated': [], 'uninsulated': []}
                          },
                   '4a': {'48': {'insulated': [], 'uninsulated': []},
                          '36': {'insulated': [], 'uninsulated': []},
                          '24': {'insulated': [], 'uninsulated': []}
                          }}

    for group in store.groups():
        group_name = group._v_name

        if '_4a' in group_name:
            if '_48_' in group_name:
                if '_insulated_' in group_name:
                    store_names['4a']['48']['insulated'].append(group_name)
                else:
                    store_names['4a']['48']['uninsulated'].append(group_name)
            elif '_36_' in group_name:
                if '_insulated_' in group_name:
                    store_names['4a']['36']['insulated'].append(group_name)
                else:
                    store_names['4a']['36']['uninsulated'].append(group_name)
            elif '_24_' in group_name:
                if '_insulated_' in group_name:
                    store_names['4a']['24']['insulated'].append(group_name)
                else:
                    store_names['4a']['24']['uninsulated'].append(group_name)

    for key0 in store_names.keys():
        for key1 in store_names[key0].keys():
            for key2 in store_names[key0][key1].keys():

                if store_names[key0][key1][key2]:
                    frame_list = []
                    for frame in store_names[key0][key1][key2]:
                        frame_list.append(store.select(frame))

                    store.append(value=pd.concat(frame_list), key=f'total_{key0}_{key1}_{key2}')

    store.close()


def plot_linear_relation(data_frame, material, bounds, quantity, title):

    quantities = ['heat loss', 'temperature', 'relative humidity', 'moisture content', 'moisture integral', 'damage',
                  'wood rot', 'mould index', 'frost']
    units = ['W/m$^2$', '$^o$C', '%', 'kg/m$^3$', 'kg', '-', '%', '-', '-']
    i = quantities.index(quantity.lower())

    if quantity.lower() in ['heat loss', 'moisture integral']:
        fig, axes = plt.subplots(figsize=(16, 8), )
        fig.suptitle(f'{title} - {quantity}\n{material.title()}')

    elif quantity.lower() in ['mould index', 'wood rot', 'frost']:
        fig, axes = plt.subplots(ncols=2, nrows=1, sharex=True, sharey=True, figsize=(16, 8), )
        fig.suptitle(f'{title} - {quantity}\n{material.title()}')
        axes = axes.flatten()

    elif 'Uninsulated' in title:
        fig, axes = plt.subplots(ncols=3, nrows=2, sharex=True, sharey=True, figsize=(16, 8), )
        fig.suptitle(f'{title} - {quantity}\n{material.title()}')
        axes = axes.flatten()

    else:
        fig, axes = plt.subplots(ncols=4, nrows=2, sharex=True, sharey=True, figsize=(16, 8), )
        fig.suptitle(f'{title} - {quantity}\n{material.title()}')
        axes = axes.flatten()

    for location in data_frame.columns.levels[0]:
        if quantity.lower() in ['heat loss', 'moisture integral', ]:
            ax = axes
        else:
            ax = axes[int(location)]
            ax.set_title(f'Location {location}')

        slope, intercept, r_value, p_value, std_err = linregress(data_frame[location, material, 'out'],
                                                                 data_frame[location, '2d', 'out'])
        ax.scatter(data_frame[location, material, 'out'], data_frame[location, '2d', 'out'], label='Data')
        ax.plot(data_frame[location, material, 'out'], intercept + slope * data_frame[location, material, 'out'], 'r',
                label=f'f(x) = {slope:.4f} * x + {intercept:.4f}\nR$^2$ = {r_value:.2f}')
        ax.set_ylim(bounds[0], bounds[1])
        ax.set_xlim(bounds[0], bounds[1])
        ax.set_ylabel(f'2D Result - {units[i]}')
        ax.set_xlabel(f'1D Result - {units[i]}')
        ax.legend()


def abs_diff_boxplot(data_frame, bounds, quantity, title):

    quantities = ['heat loss', 'temperature', 'relative humidity', 'moisture content', 'moisture integral', 'wood rot',
                  'mould index']
    units = ['W/m$^2$', '$^o$C', '%', 'kg/m$^3$', 'kg', '%', '-']
    i = quantities.index(quantity.lower())
    abs_frame = data_frame.loc[:, pd.IndexSlice[:, :, 'abs_diff']]
    abs_frame.columns = abs_frame.columns.droplevel(level=2)
    plt.figure(figsize=(16, 8), tight_layout=True)
    plt.title(f'Absolute Difference - {quantity}\n'
              f'{title}')
    abs_frame.boxplot(showfliers=False)
    plt.ylim(bounds[0], bounds[1])
    plt.ylabel(f'{quantity} - {units[i]}')


def rel_diff_boxplot(data_frame, bounds, quantity, title, log=False):

    rel_frame = data_frame.loc[:, pd.IndexSlice[:, :, 'rel_diff']]
    rel_frame.columns = rel_frame.columns.droplevel(level=2)
    plt.figure(figsize=(16, 8), tight_layout=True)
    plt.title(f'Relative Difference - {quantity}\n'
              f'{title}')
    rel_frame.boxplot(showfliers=False)
    plt.ylim(bounds[0], bounds[1])
    plt.ylabel(f'Relative Difference - %')

    if log:
        plt.gca().set_yscale('log')


def compute_damage_models(excel_file, folder):

    table = acronym_table(excel_file)
    acro_dict = match_2d_1d(table)

    def frost(location):
        damage_df[location, 'brick', 'out'] = damage_models.frost_risk(
            pd.read_hdf(relative_humidity_file, key=acro_key)[location, 'brick', 'out'],
            pd.read_hdf(temperature_file, key=acro_key)[location, 'brick', 'out'])

        damage_df[location, 'mortar', 'out'] = damage_models.frost_risk(
            pd.read_hdf(relative_humidity_file, key=acro_key)[location, 'mortar', 'out'],
            pd.read_hdf(temperature_file, key=acro_key)[location, 'mortar', 'out'])

        damage_df[location, '2d', 'out'] = damage_models.frost_risk(
            pd.read_hdf(relative_humidity_file, key=acro_key)[location, '2d', 'out'],
            pd.read_hdf(temperature_file, key=acro_key)[location, '2d', 'out'])

    def rot(location):
        damage_df[location, 'brick', 'out'] = damage_models.wood_rot(
            pd.read_hdf(relative_humidity_file, key=acro_key)[location, 'brick', 'out'],
            pd.read_hdf(temperature_file, key=acro_key)[location, 'brick', 'out'])[0]

        damage_df[location, 'mortar', 'out'] = damage_models.wood_rot(
            pd.read_hdf(relative_humidity_file, key=acro_key)[location, 'mortar', 'out'],
            pd.read_hdf(temperature_file, key=acro_key)[location, 'mortar', 'out'])[0]

        damage_df[location, '2d', 'out'] = damage_models.wood_rot(
            pd.read_hdf(relative_humidity_file, key=acro_key)[location, '2d', 'out'],
            pd.read_hdf(temperature_file, key=acro_key)[location, '2d', 'out'])[0]

    def mould(location):
        damage_df[location, 'brick', 'out'] = damage_models.mould_index(
            pd.read_hdf(relative_humidity_file, key=acro_key)[location, 'brick', 'out'],
            pd.read_hdf(temperature_file, key=acro_key)[location, 'brick', 'out'], 3, 3, 1)

        damage_df[location, 'mortar', 'out'] = damage_models.mould_index(
            pd.read_hdf(relative_humidity_file, key=acro_key)[location, 'mortar', 'out'],
            pd.read_hdf(temperature_file, key=acro_key)[location, 'mortar', 'out'], 3, 3, 1)

        damage_df[location, '2d', 'out'] = damage_models.mould_index(
            pd.read_hdf(relative_humidity_file, key=acro_key)[location, '2d', 'out'],
            pd.read_hdf(temperature_file, key=acro_key)[location, '2d', 'out'], 3, 3, 1)

    def heat_loss():
        damage_df['surface', 'mortar', 'out'] = pd.read_hdf(heat_loss_file, key=acro_key)['s', 'mortar', 'out'].cumsum()
        damage_df['surface', 'brick', 'out'] = pd.read_hdf(heat_loss_file, key=acro_key)['s', 'brick', 'out'].cumsum()
        damage_df['surface', '2d', 'out'] = pd.read_hdf(heat_loss_file, key=acro_key)['s', '2d', 'out'].cumsum()

    temperature_file = folder + '/temperature.h5'
    relative_humidity_file = folder + '/relative humidity.h5'
    heat_loss_file = folder + '/heat loss.h5'

    for acro_key in acro_dict.keys():

        if 'uninsulated' in acro_key:
            damage_df = pd.DataFrame(columns=['0', '1', '2', '3', '4', '5', 'surface'] * 3)
            damage_df.columns = pd.MultiIndex.from_arrays([damage_df.columns, ['brick', 'mortar', '2d'] * 7, ['out', ] * 21],
                                                           names=['location', 'simulation type', 'value type'])
            # Frost
            frost('0')
            frost('1')

            # Rot
            rot('2')
            rot('3')

            # Mould
            mould('4')
            mould('5')

            # Heat Loss
            heat_loss()

        else:
            damage_df = pd.DataFrame(columns=['0', '1', '2', '3', '4', '5', '6', 'surface']*3)
            damage_df.columns = pd.MultiIndex.from_arrays([damage_df.columns, ['brick', 'mortar', '2d'] * 8, ['out', ] * 24],
                                                           names=['location', 'simulation type', 'value type'])
            # Frost
            frost('0')
            frost('1')

            # Rot
            rot('2')
            rot('3')

            # Mould
            mould('4')
            mould('5')
            mould('6')

            # Heat Loss
            heat_loss()

        damage_df = compute_differences(damage_df)
        save_to_hdf(damage_df, acro_key, 'damage', folder)

    create_totals(folder, 'damage')


def plot_linear_relation_damage(data_frame, material, bounds, quantity, title):

    def damage_plot(ax, bounds, data_frame, location, material):
        slope, intercept, r_value, p_value, std_err = linregress(data_frame[location, material, 'out'],
                                                                 data_frame[location, '2d', 'out'])
        ax.scatter(data_frame[location, material, 'out'], data_frame[location, '2d', 'out'], label='Data')
        ax.plot(data_frame[location, material, 'out'], intercept + slope * data_frame[location, material, 'out'], 'r',
                label=f'f(x) = {slope:.4f} * x + {intercept:.4f}\nR$^2$ = {r_value:.4f}')
        ax.set_ylim(bounds[0], bounds[1])
        ax.set_xlim(bounds[0], bounds[1])
        ax.set_ylabel(f'2D Result - {units[i]}')
        ax.set_xlabel(f'1D Result - {units[i]}')
        ax.legend()

    quantities = ['heat loss', 'wood rot', 'mould index']
    units = ['W/m$^2$', '%', '-']
    i = quantities.index(quantity.lower())

    if quantity.lower() in ['heat loss']:
        fig, axes = plt.subplots(figsize=(16, 8), )
        fig.suptitle(f'{title} - {quantity}\n{material.title()}')

        location = 'surface'
        damage_plot(axes, bounds, data_frame, location, material)

    elif quantity.lower() in ['mould index', 'wood rot']:
        fig, axes = plt.subplots(ncols=2, nrows=1, sharex=True, sharey=True, figsize=(16, 8), )
        fig.suptitle(f'{title} - {quantity}\n{material.title()}')
        axes = axes.flatten()

        if quantity.lower() == 'mould index':
            location = ['4', '5']
        elif quantity.lower() == 'wood rot':
            location = ['2', '3']

        axes[0].set_title(f'Location {location[0]}')
        axes[1].set_title(f'Location {location[1]}')
        damage_plot(axes[0], bounds, data_frame, location[0], material)
        damage_plot(axes[1], bounds, data_frame, location[1], material)

    elif 'Insulated' in title and quantity.lower() == 'mould index':
        fig, axes = plt.subplots(ncols=3, nrows=1, sharex=True, sharey=True, figsize=(16, 8), )
        fig.suptitle(f'{title} - {quantity}\n{material.title()}')
        axes = axes.flatten()

        location = ['4', '5', '6']
        axes[0].set_title(f'Location {location[0]}')
        axes[1].set_title(f'Location {location[1]}')
        axes[2].set_title(f'Location {location[2]}')
        damage_plot(axes[0], bounds, data_frame, location[0], material)
        damage_plot(axes[1], bounds, data_frame, location[1], material)
        damage_plot(axes[2], bounds, data_frame, location[2], material)
