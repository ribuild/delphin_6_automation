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
    for index in result['indices']:
        x_ = geo['element_geometry'][index][1]
        y_ = geo['element_geometry'][index][2]
        points.append({'cell': index, 'x': x_, 'y': y_})

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
projects = ['5ad723b82e2cb22ff0a202f1', '5ad7240c2e2cb22ff0a20333', '5ad858392e2cb24344ad4ecb']
files = ['Moisture content integral.d6o']

parsed_dicts = {'brick_1d': {'moisture': {}, 'geo': {}},
                'mortar_1d': {'moisture': {}, 'geo': {}},
                '2d': {'moisture': {}, 'geo': {}}, }

map_projects = {'5ad723b82e2cb22ff0a202f1': 'brick_1d', '5ad7240c2e2cb22ff0a20333': 'mortar_1d',
                '5ad858392e2cb24344ad4ecb': '2d'}
for project in projects:
    for mp_key in map_projects.keys():
        if project == mp_key:
            key = map_projects[mp_key]

    folder = result_folder + f'/{project}/results'
    geo_file = [file
                for file in os.listdir(folder)
                if file.endswith('.g6a')][0]

    parsed_dicts[key]['moisture'], _ = delphin_parser.d6o_to_dict(folder, files[0])
    parsed_dicts[key]['geo'] = delphin_parser.g6a_to_dict(folder, geo_file)

x = np.linspace(0, len(parsed_dicts['brick_1d']['moisture']['result']['cell_0'][8760:]),
                len(parsed_dicts['brick_1d']['moisture']['result']['cell_0'][8760:]))
x_date = [datetime.datetime(2020, 1, 1) + datetime.timedelta(hours=i)
          for i in range(len(parsed_dicts['brick_1d']['moisture']['result']['cell_0'][8760:]))]
x_2d = np.linspace(0, len(parsed_dicts['2d']['moisture']['result']['cell_66'][8760:]),
                   len(parsed_dicts['2d']['moisture']['result']['cell_66'][8760:]))
x_date_2d = [datetime.datetime(2020, 1, 1) + datetime.timedelta(hours=i)
             for i in range(len(parsed_dicts['2d']['moisture']['result']['cell_66'][8760:]))]

# Brick 1D
brick_1d = get_points(parsed_dicts['brick_1d']['moisture'], parsed_dicts['brick_1d']['geo'])
brick_1d.sort(key=lambda point: point['x'])
add_data_to_points(brick_1d, parsed_dicts['brick_1d']['moisture'], 'moisture_integral')


# Mortar 1D
mortar_1d = get_points(parsed_dicts['mortar_1d']['moisture'], parsed_dicts['mortar_1d']['geo'])
mortar_1d.sort(key=lambda point: point['x'])
add_data_to_points(mortar_1d, parsed_dicts['mortar_1d']['moisture'], 'moisture_integral')

# 2D
sim_2d = get_points(parsed_dicts['2d']['moisture'], parsed_dicts['2d']['geo'])
sim_2d.sort(key=lambda point: (point['x'], point['y']))
add_data_to_points(sim_2d, parsed_dicts['2d']['moisture'], 'moisture_integral')


# Plots


# Moisture Integral
plt.figure()
plt.title('Moisture Integral')
plt.plot(x_date, brick_1d[0]['moisture_integral'], color=colors['1d_brick'], label=f"1D Brick")
plt.plot(x_date, mortar_1d[0]['moisture_integral'], color=colors['1d_mortar'], label=f"1D Mortar")
plt.plot(x_date_2d, sim_2d[10]['moisture_integral']*7.351860020585208, color=colors['bottom'], label=f"2D")
plt.legend()
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
plt.ylabel('kg')


def abs_diff(x1, x2):
    return x2 - x1


def rel_diff(x1, x2):
    return (abs(x2 - x1))/x2 * 100


brick_abs = abs_diff(brick_1d[0]['moisture_integral'],
                     sim_2d[10]['moisture_integral']*7.351860020585208)
mortar_abs = abs_diff(mortar_1d[0]['moisture_integral'],
                      sim_2d[10]['moisture_integral']*7.351860020585208)
brick_rel = rel_diff(brick_1d[0]['moisture_integral'],
                     sim_2d[10]['moisture_integral']*7.351860020585208)
mortar_rel = rel_diff(mortar_1d[0]['moisture_integral'],
                      sim_2d[10]['moisture_integral']*7.351860020585208)

# Moisture Integral
plt.figure()
plt.title('Moisture Integral - Absolute Difference')
plt.plot(x_date_2d, brick_abs, color=colors['1d_brick'], label=f"1D Brick")
plt.plot(x_date_2d, mortar_abs, color=colors['1d_mortar'], label=f"1D Mortar")
plt.legend()
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
plt.ylabel('kg')

plt.figure()
plt.title('Moisture Integral - Relative Difference')
plt.plot(x_date_2d, brick_rel, color=colors['1d_brick'], label=f"1D Brick")
plt.plot(x_date_2d, mortar_rel, color=colors['1d_mortar'], label=f"1D Mortar")
plt.legend()
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B'))
plt.ylabel('%')

plt.show()

absolute_df = pd.DataFrame(columns=['brick', 'mortar', ],
                           index=pd.DatetimeIndex(start=datetime.datetime(2020, 1, 1),
                                                  freq='h', periods=len(brick_rel)),
                           data=np.vstack([brick_abs, mortar_abs]).T)

relative_df = pd.DataFrame(columns=['brick', 'mortar', ],
                           index=pd.DatetimeIndex(start=datetime.datetime(2020, 1, 1),
                                                  freq='h', periods=len(brick_rel)),
                           data=np.vstack([brick_rel, mortar_rel]).T)

plt.figure()
ax = absolute_df.boxplot()
ax.set_ylabel('Moisture Content - kg')
ax.set_title('Absolute Differences')
plt.show()


def excel():
    out_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\2d_1d\processed_data'
    writer = pd.ExcelWriter(out_folder + '/moisture_integral.xlsx')
    relative_df.describe().to_excel(writer, 'relative')
    absolute_df.describe().to_excel(writer, 'absolute')
    writer.save()


#excel()