__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import os
import yaml

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import validation as auth_dict
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import sampling_interactions
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions.db_templates import weather_entry
from delphin_6_automation.sampling import inputs
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def get_excel(folder):

    heat = pd.DataFrame()
    temp = pd.DataFrame()
    relhum = pd.DataFrame()

    return heat, temp, relhum


def download_results(delphin_doc, design_folder):
    result_doc = delphin_doc.results_raw
    result_folder = os.path.join(design_folder, str(result_doc.id))
    try:
        os.mkdir(result_folder)
    except FileExistsError:
        return result_folder

    general_interactions.download_raw_result(str(result_doc.id), design_folder)
    general_interactions.download_sample_data(str(delphin_doc.id), result_folder)

    return result_folder


def append_sample_data(sample_data):
    heat, temp, relhum = [], [], []

    heat.append(sample_data['wall_orientation'])
    temp.append(sample_data['wall_orientation'])
    relhum.append(sample_data['wall_orientation'])

    heat.append(sample_data['exterior_heat_transfer_coefficient'])
    temp.append(sample_data['exterior_heat_transfer_coefficient'])
    relhum.append(sample_data['exterior_heat_transfer_coefficient'])

    heat.append(sample_data['exterior_moisture_transfer_coefficient'])
    temp.append(sample_data['exterior_moisture_transfer_coefficient'])
    relhum.append(sample_data['exterior_moisture_transfer_coefficient'])

    heat.append(sample_data['solar_absorption'])
    temp.append(sample_data['solar_absorption'])
    relhum.append(sample_data['solar_absorption'])

    heat.append(sample_data['interior_heat_transfer_coefficient'])
    temp.append(sample_data['interior_heat_transfer_coefficient'])
    relhum.append(sample_data['interior_heat_transfer_coefficient'])

    heat.append(sample_data['interior_moisture_transfer_coefficient'])
    temp.append(sample_data['interior_moisture_transfer_coefficient'])
    relhum.append(sample_data['interior_moisture_transfer_coefficient'])

    heat.append(sample_data['initial_temperature'])
    temp.append(sample_data['initial_temperature'])
    relhum.append(sample_data['initial_temperature'])

    heat.append(sample_data['initial_relhum'])
    temp.append(sample_data['initial_relhum'])
    relhum.append(sample_data['initial_relhum'])

    heat.append(sample_data['wall_core_material'])
    temp.append(sample_data['wall_core_material'])
    relhum.append(sample_data['wall_core_material'])

    heat.extend([None, None])
    temp.extend([None, None])
    relhum.extend([None, None])

    return heat, temp, relhum


def append_results(dataframes, result_folder, index):

    sim_index = index + 1

    # Sample Data
    with open(os.path.join(result_folder, 'sample_data.txt')) as sdf:
        sample_data = yaml.load(sdf)

    heat, temp, relhum = append_sample_data(sample_data)

    # Put in the results
    results = os.path.join(result_folder, 'results')

    # HEAT LOSS
    heat_data = delphin_parser.d6o_to_dict(results, 'heat loss.d6o', 17520)
    heat.extend(heat_data[0])

    # TEMPERATURE
    temp_data = delphin_parser.d6o_to_dict(results, 'temperature mould.d6o', 17520)
    temp.extend(temp_data[0])

    # RELATIVE HUMIDITY
    relhum_data = delphin_parser.d6o_to_dict(results, 'relative humidity mould.d6o', 17520)
    relhum.extend(relhum_data[0])

    # Append to Dateframes
    heat_df, temp_df, relhum_df = dataframes

    heat_df[f'sim {sim_index}'] = heat
    temp_df[f'sim {sim_index}'] = temp
    relhum_df[f'sim {sim_index}'] = relhum

    return heat_df, temp_df, relhum_df


def save_and_close(dataframes, folder, design):
    heat, temp, relhum = dataframes

    file = os.path.join(folder, f'{design} - Ouputs.xlsx')
    with pd.ExcelWriter(file) as writer:
        heat.to_excel(writer, sheet_name='heat loss')
        temp.to_excel(writer, sheet_name='interf T')
        relhum.to_excel(writer, sheet_name='interf RH')


def main():
    folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\output'
    frames = get_excel(folder)

    strategies = sample_entry.Strategy.objects()

    for strategy in strategies:
        design = strategy.strategy['design'][0]
        design_folder = os.path.join(folder, design)

        try:
            os.mkdir(design_folder)
        except FileExistsError:
            pass

        index = 0
        for sample in strategy.samples:
            for delphin_doc in sample.delphin_docs:
                result_folder = download_results(delphin_doc, design_folder)
                frames = append_results(frames, result_folder, index)
                index += 1

        save_and_close(frames, folder, design)


def hans():
    folder_h = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\test\Hans'
    folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\output'
    frames = get_excel(folder)

    index = 0
    files = ['Ms-11-5-DWD Weimar - DirDif', 'Ms-11-5-DWD Weimar - Dif']
    for f in files:
        print(f)
        result_folder = os.path.join(folder_h, f)
        frames = append_results(frames, result_folder, index)
        index += 1

    save_and_close(frames, folder_h, 'Hans')


if __name__ == "__main__":
    server = mongo_setup.global_init(auth_dict)

    hans()

    mongo_setup.global_end_ssh(server)
