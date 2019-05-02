__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import numpy as np
import os

# RiBuild Modules
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

folder = r'C:\Users\ocni\Desktop\simulation_years_data'
projects = os.listdir(folder)


def add_to_df(lst, file):
    file_path = os.path.join(result_folder, file)
    if file.endswith('.txt'):
        data = np.loadtxt(file_path)[:61320]
        try:
            assert len(data) == 61320
        except AssertionError:
            print(f'{file} didnt contain a full 7 year set. Skipping')
            return

        data_split = np.split(data, 7)
        row = [project] + [np.max(year) for year in data_split]

    elif file.endswith('.d6o'):
        data = np.array(delphin_parser.d6o_to_dict(result_folder, file)[0][:61320])
        try:
            assert len(data) == 61320
        except AssertionError:
            print(f'{file} didnt contain a full 7 year set. Skipping')
            return
        data_split = np.split(data, 7)
        row = [project] + [np.sum(year) for year in data_split]

    lst.append(row)


mould_interface_array = []
mould_interior_array = []
heat_loss_array = []

index = 0
print('Starting Processing Projects\n')
for project in projects:
    for content in os.listdir(os.path.join(folder, project)):
        if os.path.isdir(os.path.join(folder, project, content)):
            result_folder = os.path.join(folder, project, content, 'results')

            if os.path.exists(os.path.join(result_folder, 'mould_interface.txt')):
                print(f'Processing {project}')
                add_to_df(mould_interface_array, 'mould_interface.txt')
                add_to_df(mould_interior_array, 'mould_interior_surface.txt')
                add_to_df(heat_loss_array, 'heat loss.d6o')
            else:
                print(f'No mould_interface.txt was found in {project}')

            index += 1
            if index % 250 == 0:
                print(f'\n{index} projects have been downloaded\n')

data_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\simulation_years\data'
hdf_file = os.path.join(data_folder, 'processed_data.h5')

columns = ['ID', 'Year 0', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5', 'Year 6']
mould_interface = pd.DataFrame(mould_interface_array, columns=columns)
mould_interior = pd.DataFrame(mould_interior_array, columns=columns)
heat_loss = pd.DataFrame(heat_loss_array, columns=columns)

mould_interface.to_hdf(hdf_file, 'mould_interface', append=True)
mould_interior.to_hdf(hdf_file, 'mould_interior', append=True)
heat_loss.to_hdf(hdf_file, 'heat_loss', append=True)
