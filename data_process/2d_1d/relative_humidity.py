__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime
import matplotlib.dates as mdates
import pandas as pd

# RiBuild Modules
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


# Functions
def get_points(result: dict, geo: dict):

    points = []
    for index_ in result['indices']:
        x_ = geo['element_geometry'][index_][1]
        y_ = geo['element_geometry'][index_][2]
        points.append({'cell': index_, 'x': x_, 'y': y_})

    return points


def add_data_to_points(points: list, results: dict, result_name: str):
    for cell_ in results['result'].keys():
        cell_index = int(cell_.split('_')[1])

        for point in points:
            if point['cell'] == cell_index:
                point[result_name] = np.array(results['result'][cell_][8760:])
                break


# Application
colors = {'top': '#FBBA00', 'mid': '#B81A5D', 'bottom': '#79C6C0', '1d_brick': '#000000', '1d_mortar': '#BDCCD4'}
result_folder = r'U:\RIBuild\2D_1D\Results'
projects = ['5ad9e0ba2e2cb22f2c4f15f1', '5ad9e3bf2e2cb22f2c4f166b', '5adb2dc02e2cb22f2c4f1873']
files = ['temperature profile.d6o']

parsed_dicts = {'brick_1d': {'rh': {}, 'geo': {}},
                'mortar_1d': {'rh': {}, 'geo': {}},
                '2d': {'rh': {}, 'geo': {}}, }

map_projects = {'5ad9e0ba2e2cb22f2c4f15f1': 'brick_1d', '5ad9e3bf2e2cb22f2c4f166b': 'mortar_1d',
                '5adb2dc02e2cb22f2c4f1873': '2d'}

for project in projects:
    for mp_key in map_projects.keys():
        if project == mp_key:
            key = map_projects[mp_key]

    folder = result_folder + f'/{project}/results'
    geo_file = [file
                for file in os.listdir(folder)
                if file.endswith('.g6a')][0]

    parsed_dicts[key]['rh'], _ = delphin_parser.d6o_to_dict(folder, files[0])
    parsed_dicts[key]['geo'] = delphin_parser.g6a_to_dict(folder, geo_file)

x = np.linspace(0, len(parsed_dicts['brick_1d']['rh']['result']['cell_0'][8760:]),
                len(parsed_dicts['brick_1d']['rh']['result']['cell_0'][8760:]))
x_date = [datetime.datetime(2020, 1, 1) + datetime.timedelta(hours=i)
          for i in range(len(parsed_dicts['brick_1d']['rh']['result']['cell_0'][8760:]))]

# Brick 1D
brick_1d = get_points(parsed_dicts['brick_1d']['rh'], parsed_dicts['brick_1d']['geo'])
brick_1d.sort(key=lambda point: point['x'])
add_data_to_points(brick_1d, parsed_dicts['brick_1d']['rh'], 'relative_humidity')

# Mortar 1D
mortar_1d = get_points(parsed_dicts['mortar_1d']['rh'], parsed_dicts['mortar_1d']['geo'])
mortar_1d.sort(key=lambda point: point['x'])
add_data_to_points(mortar_1d, parsed_dicts['mortar_1d']['rh'], 'relative_humidity')

# 2D
sim_2d = get_points(parsed_dicts['2d']['rh'], parsed_dicts['2d']['geo'])
sim_2d.sort(key=lambda point: (point['x'], point['y']))
add_data_to_points(sim_2d, parsed_dicts['2d']['rh'], 'relative_humidity')


# Plots
def plot_locations(quantity):
    # Axes 00
    plt.figure()
    plt.title(f"{quantity}\n1D-Location: {brick_1d[0]['x']:.4f} and 2D-Location: {sim_2d[0]['x']:.4f}")
    plt.plot(x_date, brick_1d[0][quantity], color=colors['1d_brick'], label=f"1D Brick")
    plt.plot(x_date, mortar_1d[0][quantity], color=colors['1d_mortar'], label=f"1D Mortar")
    plt.plot(x_date, sim_2d[0][quantity], color=colors['bottom'], label=f"2D Bottom")
    plt.plot(x_date, sim_2d[1][quantity], color=colors['mid'], label=f"2D Mid")
    plt.plot(x_date, sim_2d[2][quantity], color=colors['top'], label=f"2D Top")
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
    plt.ylabel(f'{quantity}')

    # Axes 01
    plt.figure()
    plt.title(f"{quantity}\n1D-Location: {brick_1d[1]['x']:.4f} and 2D-Location: {sim_2d[3]['x']:.4f}")
    plt.plot(x_date, brick_1d[1][quantity], color=colors['1d_brick'], label=f"1D Brick")
    plt.plot(x_date, mortar_1d[1][quantity], color=colors['1d_mortar'], label=f"1D Mortar")
    plt.plot(x_date, sim_2d[3][quantity], color=colors['bottom'], label=f"2D Bottom")
    plt.plot(x_date, sim_2d[4][quantity], color=colors['mid'], label=f"2D Mid")
    plt.plot(x_date, sim_2d[5][quantity], color=colors['top'], label=f"2D Top")
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
    plt.ylabel(f'{quantity}')

    # Axes 10
    plt.figure()
    plt.title(f"{quantity}\n1D-Location: {brick_1d[2]['x']:.4f} and 2D-Location: {sim_2d[6]['x']:.4f}")
    plt.plot(x_date, brick_1d[2][quantity], color=colors['1d_brick'], label=f"1D Brick")
    plt.plot(x_date, mortar_1d[2][quantity], color=colors['1d_mortar'], label=f"1D Mortar")
    plt.plot(x_date, sim_2d[6][quantity], color=colors['bottom'], label=f"2D Bottom")
    plt.plot(x_date, sim_2d[7][quantity], color=colors['mid'], label=f"2D Mid")
    plt.plot(x_date, sim_2d[8][quantity], color=colors['top'], label=f"2D Top")
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
    plt.ylabel(f'{quantity}')

    # Axes 11
    plt.figure()
    plt.title(f"{quantity}\n1D-Location: {brick_1d[3]['x']:.4f} and 2D-Location: {sim_2d[9]['x']:.4f}")
    plt.plot(x_date, brick_1d[3][quantity], color=colors['1d_brick'], label=f"1D Brick")
    plt.plot(x_date, mortar_1d[3][quantity], color=colors['1d_mortar'], label=f"1D Mortar")
    plt.plot(x_date, sim_2d[9][quantity], color=colors['bottom'], label=f"2D Bottom")
    plt.plot(x_date, sim_2d[10][quantity], color=colors['mid'], label=f"2D Mid")
    plt.plot(x_date, sim_2d[11][quantity], color=colors['top'], label=f"2D Top")
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
    plt.ylabel(f'{quantity}')

    # Axes 20
    plt.figure()
    plt.title(f"{quantity}\n1D-Location: {brick_1d[4]['x']:.4f} and 2D-Location: {sim_2d[12]['x']:.4f}")
    plt.plot(x_date, brick_1d[4][quantity], color=colors['1d_brick'], label=f"1D Brick")
    plt.plot(x_date, mortar_1d[4][quantity], color=colors['1d_mortar'], label=f"1D Mortar")
    plt.plot(x_date, sim_2d[12][quantity], color=colors['bottom'], label=f"2D Bottom")
    plt.plot(x_date, sim_2d[13][quantity], color=colors['mid'], label=f"2D Mid")
    plt.plot(x_date, sim_2d[14][quantity], color=colors['top'], label=f"2D Top")
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
    plt.ylabel(f'{quantity}')

    # Axes 21
    plt.figure()
    plt.title(f"{quantity}\n1D-Location: {brick_1d[5]['x']:.4f} and 2D-Location: {sim_2d[15]['x']:.4f}")
    plt.plot(x_date, brick_1d[5][quantity], color=colors['1d_brick'], label=f"1D Brick")
    plt.plot(x_date, mortar_1d[5][quantity], color=colors['1d_mortar'], label=f"1D Mortar")
    plt.plot(x_date, sim_2d[15][quantity], color=colors['bottom'], label=f"2D Bottom")
    plt.plot(x_date, sim_2d[16][quantity], color=colors['mid'], label=f"2D Mid")
    plt.plot(x_date, sim_2d[17][quantity], color=colors['top'], label=f"2D Top")
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
    plt.ylabel(f'{quantity}')


#plot_locations(quantity='relative_humidity')
#plt.show()


def abs_diff(x1, x2):
    return x2 - x1


def rel_diff(x1, x2):
    return (abs(x2 - x1))/x2 * 100


def differences(i, plots=False):

    avg_2d = np.mean([sim_2d[i]['relative_humidity'],  sim_2d[i+2]['relative_humidity'],  sim_2d[i+2]['relative_humidity']], axis=0)
    brick_abs = abs_diff(brick_1d[i]['relative_humidity'], avg_2d)
    mortar_abs = abs_diff(mortar_1d[i]['relative_humidity'], avg_2d)
    brick_rel = rel_diff(brick_1d[i]['relative_humidity'], avg_2d)
    mortar_rel = rel_diff(mortar_1d[i]['relative_humidity'], avg_2d)

    if plots:
        # Plot
        plt.figure()
        plt.title(f"relative_humidity - Absolute Difference\n"
                  f"1D-Location: {brick_1d[i]['x']:.4f} and 2D-Location: {sim_2d[i*3]['x']:.4f}")
        plt.plot(x_date, brick_abs, color=colors['1d_brick'], label=f"1D Brick")
        plt.plot(x_date, mortar_abs, color=colors['1d_mortar'], label=f"1D Mortar")
        plt.legend()
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
        plt.ylabel('%')

        plt.figure()
        plt.title(f"relative_humidity - Relative Difference\n"
                  f"1D-Location: {brick_1d[i]['x']:.4f} and 2D-Location: {sim_2d[i*3]['x']:.4f}")
        plt.plot(x_date, brick_rel, color=colors['1d_brick'], label=f"1D Brick")
        plt.plot(x_date, mortar_rel, color=colors['1d_mortar'], label=f"1D Mortar")
        plt.legend()
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
        plt.ylabel('%')

    local_df = pd.DataFrame(columns=[f"{brick_1d[i]['x']:.04f}", f"{brick_1d[i]['x']:.04f}",
                                     f"{brick_1d[i]['x']:.04f}", f"{brick_1d[i]['x']:.04f}"],
                            index=pd.DatetimeIndex(start=datetime.datetime(2020, 1, 1),
                                                   freq='h', periods=len(brick_rel)),
                            data=np.vstack([brick_rel, brick_abs, mortar_rel, mortar_abs]).T)

    local_df.columns = pd.MultiIndex.from_arrays([local_df.columns, ['brick', 'brick', 'mortar', 'mortar'],
                                                 ['relative', 'absolute', 'relative', 'absolute']],
                                                 names=['location', 'material', 'type'])

    return local_df


def differences_weighted(i, plots=False):

    avg_2d = np.average(a=[sim_2d[i]['relative_humidity'],
                           sim_2d[i+2]['relative_humidity'],
                           sim_2d[i+2]['relative_humidity']],
                        axis=0,
                        weights=[56, 24.02, 56])
    brick_abs = abs_diff(brick_1d[i]['relative_humidity'], avg_2d)
    mortar_abs = abs_diff(mortar_1d[i]['relative_humidity'], avg_2d)
    brick_rel = rel_diff(brick_1d[i]['relative_humidity'], avg_2d)
    mortar_rel = rel_diff(mortar_1d[i]['relative_humidity'], avg_2d)

    if plots:
        # Plot
        plt.figure()
        plt.title(f"Relative Humidity - Weighted Absolute Difference\n"
                  f"1D-Location: {brick_1d[i]['x']:.4f} and 2D-Location: {sim_2d[i*3]['x']:.4f}")
        plt.plot(x_date, brick_abs, color=colors['1d_brick'], label=f"1D Brick")
        plt.plot(x_date, mortar_abs, color=colors['1d_mortar'], label=f"1D Mortar")
        plt.legend()
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
        plt.ylabel('%')

        plt.figure()
        plt.title(f"Relative Humidity - Weighted Relative Difference\n"
                  f"1D-Location: {brick_1d[i]['x']:.4f} and 2D-Location: {sim_2d[i*3]['x']:.4f}")
        plt.plot(x_date, brick_rel, color=colors['1d_brick'], label=f"1D Brick")
        plt.plot(x_date, mortar_rel, color=colors['1d_mortar'], label=f"1D Mortar")
        plt.legend()
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
        plt.ylabel('%')

    local_df = pd.DataFrame(columns=[f"{brick_1d[i]['x']:.04f}", f"{brick_1d[i]['x']:.04f}",
                                     f"{brick_1d[i]['x']:.04f}", f"{brick_1d[i]['x']:.04f}"],
                            index=pd.DatetimeIndex(start=datetime.datetime(2020, 1, 1),
                                                   freq='h', periods=len(brick_rel)),
                            data=np.vstack([brick_rel, brick_abs, mortar_rel, mortar_abs]).T)

    local_df.columns = pd.MultiIndex.from_arrays([local_df.columns, ['brick', 'brick', 'mortar', 'mortar'],
                                                 ['relative', 'absolute', 'relative', 'absolute']],
                                                 names=['location', 'material', 'type'])

    return local_df


dataframes = []
weighted_dataframes = []
for index in range(len(brick_1d)):
    dataframes.append(differences(index))
    weighted_dataframes.append(differences_weighted(index))
    #plt.show()

result_dataframe = pd.concat(dataframes, axis=1)
w_result_dataframe = pd.concat(weighted_dataframes, axis=1)

#print(result_dataframe.loc[:, pd.IndexSlice[:, :, 'absolute']].describe())

absolute_df = result_dataframe.loc[:, pd.IndexSlice[:, :, 'absolute']]
absolute_df.columns = absolute_df.columns.droplevel(level=2)
relative_df = result_dataframe.loc[:, pd.IndexSlice[:, :, 'relative']]
relative_df.columns = relative_df.columns.droplevel(level=2)

w_absolute_df = w_result_dataframe.loc[:, pd.IndexSlice[:, :, 'absolute']]
w_absolute_df.columns = w_absolute_df.columns.droplevel(level=2)
w_relative_df = w_result_dataframe.loc[:, pd.IndexSlice[:, :, 'relative']]
w_relative_df.columns = w_relative_df.columns.droplevel(level=2)


def boxplots():
    plt.figure()
    ax = absolute_df.boxplot()
    ax.set_ylim(-20, 20)
    ax.set_ylabel('Relative Humidity - %')
    ax.set_title('Non-Weighted Absolute Differences')
    plt.figure()
    ax = w_absolute_df.boxplot()
    ax.set_ylim(-20, 20)
    ax.set_ylabel('Relative Humidity - %')
    ax.set_title('Weighted Absolute Differences')
    # plt.show()


boxplots()

out_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\2d_1d\processed_data'


def excel():

    writer = pd.ExcelWriter(out_folder + '/relative_humidity.xlsx')
    relative_df.describe().to_excel(writer, 'relative')
    w_relative_df.describe().to_excel(writer, 'relative_weighted')
    absolute_df.describe().to_excel(writer, 'absolute')
    w_absolute_df.describe().to_excel(writer, 'absolute_weighted')
    writer.save()


#excel()


def save_relative():
    hdf_file = out_folder + '/relative_humidity.h5'
    w_relative_df.to_hdf(hdf_file, 'dresdenzd_highratio_4a', append=True)


save_relative()