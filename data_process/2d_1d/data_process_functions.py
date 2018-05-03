__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import os
import datetime

# RiBuild Modules
from delphin_6_automation.file_parsing import delphin_parser

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

    for subfolder in os.listdir(folder):
        result_folder_ = f"{folder}/{subfolder}/results"

        if subfolder == acro_dict['brick']:

            indices = 0
            for file in os.listdir(result_folder_):
                if quantity in file:
                    value_dict = delphin_parser.d6o_to_dict(result_folder_, file)[0]['result']
                    cell = list(value_dict.keys())[0]
                    values = value_dict[cell]
                    df[file[-1]] = values
                    indices += 1

            df.index = pd.DatetimeIndex(start=datetime.datetime(2020, 1, 1),
                                        freq='h', periods=len(values))
            df.columns = pd.MultiIndex.from_arrays([df.columns, ['brick' * len(indices)], ['out' * len(indices)]],
                                                   names=['location', 'simulation type', 'value type'])

        elif subfolder == acro_dict['mortar']:

            indices = 0
            for file in os.listdir(result_folder_):
                if quantity in file:
                    value_dict = delphin_parser.d6o_to_dict(result_folder_, file)[0]['result']
                    cell = list(value_dict.keys())[0]
                    values = value_dict[cell]
                    df[file[-1]] = values
                    indices += 1

            df.columns = pd.MultiIndex.from_arrays([df.columns, ['mortar' * len(indices)], ['out' * len(indices)]],
                                                   names=['location', 'simulation type', 'value type'])

        elif subfolder == acro_dict['2d']:

            indices = 0
            for file in os.listdir(result_folder_):
                if quantity in file:
                    value_dict = delphin_parser.d6o_to_dict(result_folder_, file)[0]['result']
                    cell = list(value_dict.keys())[0]
                    values = value_dict[cell]
                    df[file[-1]] = values
                    indices += 1

            df.columns = pd.MultiIndex.from_arrays([df.columns, ['2d' * len(indices)], ['out' * len(indices)]],
                                                   names=['location', 'simulation type', 'value type'])

# Tests
if __name__ == '__main__':

    excel_file = r'U:\RIBuild\2D_1D\2D to 1D Transformation.xlsx'
    result_folder = r'U:\RIBuild\2D_1D\Results'

    table = acronym_table(excel_file)

    map_ = match_2d_1d(table)

    #print(map_)

    load_results(result_folder, 'temperature', map_['dresden_zp_high_cement_uninsulated_36_4a'])


