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



colors = {'top': '#FBBA00', 'mid': '#B81A5D', 'bottom': '#79C6C0', '1d_brick': '#000000', '1d_mortar': '#BDCCD4'}

project_dict = {'dresden_zp_high_ratio_uninsulated_4a':
                    {'map':
                         {'5ad9e0352e2cb22f2c4f15b4': 'brick_1d',
                          '5ad9e3bf2e2cb22f2c4f166b': 'mortar_1d',
                          '5adb0a102e2cb22f2c4f17e9': '2d'}
                     },
                'dresden_zd_high_ratio_uninsulated_4a':
                    {'map':
                         {'5ad9e0ba2e2cb22f2c4f15f1': 'brick_1d',
                          '5ad9e3bf2e2cb22f2c4f166b': 'mortar_1d',
                          '5adb2dc02e2cb22f2c4f1873': '2d'}
                     },
                'potsdam_high_ratio_uninsulated_4a':
                    {'map':
                         {'5ad9e3462e2cb22f2c4f162e': 'brick_1d',
                          '5ad9e3bf2e2cb22f2c4f166b': 'mortar_1d',
                          '5adcc9702e2cb22f2c4f18fd': '2d'}
                     },
                'dresden_zp_low_ratio_uninsulated_4a':
                    {'map':
                         {'5ad9e6192e2cb22f2c4f175f': 'brick_1d',
                          '5ad9e5812e2cb22f2c4f1722': 'mortar_1d',
                          '5adda7172e2cb20baca57c6e': '2d'}
                     },
                'dresden_zd_low_ratio_uninsulated_4a':
                    {'map':
                         {'5ad9e44f2e2cb22f2c4f16a8': 'brick_1d',
                          '5ad9e5812e2cb22f2c4f1722': 'mortar_1d',
                          '5adcd4402e2cb22f2c4f1987': '2d'}
                     },
                'potsdam_low_ratio_uninsulated_4a':
                    {'map': {'5ad9e4f22e2cb22f2c4f16e5': 'brick_1d',
                             '5ad9e5812e2cb22f2c4f1722': 'mortar_1d',
                             '5add9b902e2cb20baca57be4': '2d'}
                     },
                'dresden_zp_high_ratio_insulated_4a':
                    {'map': {'5ae824252e2cb22d48db5955': 'brick_1d',
                             '5ae82c222e2cb2156000902b': 'mortar_1d',
                             '5ae355cf2e2cb2201055c1a4': '2d'}
                     },
                'dresden_zd_high_ratio_insulated_4a':
                    {'map': {'5ae824d82e2cb22d48db5998': 'brick_1d',
                             '5ae82c222e2cb2156000902b': 'mortar_1d',
                             '5ae398f12e2cb2201055c263': '2d'}
                     },
                'potsdam_high_ratio_insulated_4a':
                    {'map':
                         {'5ae82bac2e2cb21560008fe8': 'brick_1d',
                          '5ae82c222e2cb2156000902b': 'mortar_1d',
                          '5ae6ca982e2cb2201055c322': '2d'}
                     },
                'dresden_zp_low_ratio_insulated_4a':
                    {'map':
                         {'5ae82e5d2e2cb21560009137': 'brick_1d',
                          '5ae82dc02e2cb215600090f4': 'mortar_1d',
                          '5ae6fdbf2e2cb20d5891272f': '2d'}
                     },
                'dresden_zd_low_ratio_insulated_4a':
                    {'map':
                         {'5ae82cb12e2cb2156000906e': 'brick_1d',
                          '5ae82dc02e2cb215600090f4': 'mortar_1d',
                          '5ae6d9bf2e2cb2201055c3e1': '2d'}
                     },
                'potsdam_low_ratio_insulated_4a':
                    {'map':
                         {'5ae82d3b2e2cb215600090b1': 'brick_1d',
                          '5ae82dc02e2cb215600090f4': 'mortar_1d',
                          '5ae6edaf2e2cb20d58912670': '2d'}
                     },
                }

result_folder = r'U:\RIBuild\2D_1D\Results'
files = ['moisture content profile.d6o']

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
def main(project_):
    projects = list(project_dict[project_]['map'].keys())
    parsed_dicts = {'brick_1d': {'moisture_content': {}, 'geo': {}},
                    'mortar_1d': {'moisture_content': {}, 'geo': {}},
                    '2d': {'moisture_content': {}, 'geo': {}}, }

    for p_ in projects:
        for mp_key in project_dict[project_]['map'].keys():
            if p_ == mp_key:
                key = project_dict[project_]['map'][mp_key]

        folder = result_folder + f'/{p_}/results'
        geo_file = [file
                    for file in os.listdir(folder)
                    if file.endswith('.g6a')][0]

        parsed_dicts[key]['moisture_content'], _ = delphin_parser.d6o_to_dict(folder, files[0])
        parsed_dicts[key]['geo'] = delphin_parser.g6a_to_dict(folder, geo_file)

    x_date = [datetime.datetime(2020, 1, 1) + datetime.timedelta(hours=i)
              for i in range(len(parsed_dicts['brick_1d']['moisture_content']['result']['cell_0'][8760:]))]

    # Brick 1D
    brick_1d = get_points(parsed_dicts['brick_1d']['moisture_content'], parsed_dicts['brick_1d']['geo'])
    brick_1d.sort(key=lambda point: point['x'])
    add_data_to_points(brick_1d, parsed_dicts['brick_1d']['moisture_content'], 'moisture_content')

    # Mortar 1D
    mortar_1d = get_points(parsed_dicts['mortar_1d']['moisture_content'], parsed_dicts['mortar_1d']['geo'])
    mortar_1d.sort(key=lambda point: point['x'])
    add_data_to_points(mortar_1d, parsed_dicts['mortar_1d']['moisture_content'], 'moisture_content')

    # 2D
    sim_2d = get_points(parsed_dicts['2d']['moisture_content'], parsed_dicts['2d']['geo'])
    sim_2d.sort(key=lambda point: (point['x'], point['y']))
    add_data_to_points(sim_2d, parsed_dicts['2d']['moisture_content'], 'moisture_content')


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


    #plot_locations(quantity='moisture_content')
    #plt.show()


    def abs_diff(x1, x2):
        return x2 - x1


    def rel_diff(x1, x2):
        return (abs(x2 - x1))/x2 * 100


    def differences(i, plot=False):

        avg_2d = np.mean([sim_2d[i]['moisture_content'],  sim_2d[i+2]['moisture_content'],  sim_2d[i+2]['moisture_content']], axis=0)
        brick_abs = abs_diff(brick_1d[i]['moisture_content'], avg_2d)
        mortar_abs = abs_diff(mortar_1d[i]['moisture_content'], avg_2d)
        brick_rel = rel_diff(brick_1d[i]['moisture_content'], avg_2d)
        mortar_rel = rel_diff(mortar_1d[i]['moisture_content'], avg_2d)

        if plot:
            # Plot
            plt.figure()
            plt.title(f"Moisture Content - Absolute Difference\n"
                      f"1D-Location: {brick_1d[i]['x']:.4f} and 2D-Location: {sim_2d[i*3]['x']:.4f}")
            plt.plot(x_date, brick_abs, color=colors['1d_brick'], label=f"1D Brick")
            plt.plot(x_date, mortar_abs, color=colors['1d_mortar'], label=f"1D Mortar")
            plt.legend()
            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
            plt.ylabel('kg/m3')

            plt.figure()
            plt.title(f"Moisture Content - Relative Difference\n"
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


    def differences_weighted(i, plot=False):

        avg_2d = np.average(a=[sim_2d[i]['moisture_content'],
                               sim_2d[i+2]['moisture_content'],
                               sim_2d[i+2]['moisture_content']],
                            axis=0,
                            weights=[56, 24, 56])
        brick_abs = abs_diff(brick_1d[i]['moisture_content'], avg_2d)
        mortar_abs = abs_diff(mortar_1d[i]['moisture_content'], avg_2d)
        brick_rel = rel_diff(brick_1d[i]['moisture_content'], avg_2d)
        mortar_rel = rel_diff(mortar_1d[i]['moisture_content'], avg_2d)

        if plot:
            # Plot
            plt.figure()
            plt.title(f"Moisture Content - Weighted Absolute Difference\n"
                      f"1D-Location: {brick_1d[i]['x']:.4f} and 2D-Location: {sim_2d[i*3]['x']:.4f}")
            plt.plot(x_date, brick_abs, color=colors['1d_brick'], label=f"1D Brick")
            plt.plot(x_date, mortar_abs, color=colors['1d_mortar'], label=f"1D Mortar")
            plt.legend()
            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
            plt.ylabel('kg/m3')

            plt.figure()
            plt.title(f"Moisture Content - Weighted Relative Difference\n"
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
        plt.show()

    result_dataframe = pd.concat(dataframes, axis=1)
    w_result_dataframe = pd.concat(weighted_dataframes, axis=1)

    absolute_df = result_dataframe.loc[:, pd.IndexSlice[:, :, 'absolute']]
    absolute_df.columns = absolute_df.columns.droplevel(level=2)
    relative_df = result_dataframe.loc[:, pd.IndexSlice[:, :, 'relative']]
    relative_df.columns = relative_df.columns.droplevel(level=2)

    w_absolute_df = w_result_dataframe.loc[:, pd.IndexSlice[:, :, 'absolute']]
    w_absolute_df.columns = w_absolute_df.columns.droplevel(level=2)
    w_relative_df = w_result_dataframe.loc[:, pd.IndexSlice[:, :, 'relative']]
    w_relative_df.columns = w_relative_df.columns.droplevel(level=2)


    def boxplots():
        global w_absolute_df, w_absolute_df

        plt.figure()
        ax = absolute_df.boxplot()
        ax.set_ylabel('Moisture Content - kg/m3')
        ax.set_title('Non-Weighted Absolute Differences')


        plt.figure()
        ax = w_absolute_df.boxplot()
        ax.set_ylabel('Moisture Content- kg/m3')
        ax.set_title('Weighted Absolute Differences')
        plt.show()


    #boxplots()
    out_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\2d_1d\processed_data'


    def excel_summery():
        writer = pd.ExcelWriter(out_folder + '/moisture_content_DresdenZD_HighRatio.xlsx')
        relative_df.describe().to_excel(writer, 'relative')
        w_relative_df.describe().to_excel(writer, 'relative_weighted')
        absolute_df.describe().to_excel(writer, 'absolute')
        w_absolute_df.describe().to_excel(writer, 'absolute_weighted')
        writer.save()


    #excel_summery()


    def save_relative():
        hdf_file = out_folder + '/relative_moisture_content.h5'
        w_relative_df.to_hdf(hdf_file, project_, append=True)

    save_relative()


for project_key in project_dict.keys():
    print(f'Processing {project_key}')
    main(project_key)