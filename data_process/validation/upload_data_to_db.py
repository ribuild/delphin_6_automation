__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import json
import pandas as pd
import datetime
import bson

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import validation as auth_dict
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import sampling_interactions
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions.db_templates import weather_entry
from delphin_6_automation.sampling import inputs
from delphin_6_automation.file_parsing import weather_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)


def upload_materials(folder):
    print('Uploading Materials')

    for file in os.listdir(os.path.join(folder, 'materials')):
        print(file)
        material_interactions.upload_material_file(os.path.join(folder, 'materials', file))

    bricks = pd.read_excel(folder + '/Brick.xlsx')

    delphin_mats = r'C:\Program Files\IBK\Delphin 6.0\resources\DB_materials'

    for i in range(len(bricks)):
        name = f'{bricks.loc[i, "Name"]}_{bricks.loc[i, "Material ID"]}.m6'
        if name == 'Masonry_3.m6':
            pass
        else:
            print(name, os.path.exists(os.path.join(delphin_mats, name)))
            material_interactions.upload_material_file(os.path.join(delphin_mats, name))


def upload_weather(folder):
    stations = ['Ms-11-5', 'Ms-24-1']
    weather_dict = {'time': [2017, 2019]}

    for dwd_file in os.listdir(folder):
        if dwd_file.endswith('DiffuseRadiation.ccd'):
            key = 'diffuse_radiation'
        elif dwd_file.endswith('DirectRadiation.ccd'):
            key = 'direct_radiation'
        elif dwd_file.endswith('SkyRadiation.ccd'):
            key = 'long_wave_radiation'

        if key:
            weather_dict[key] = weather_parser.ccd_to_list(os.path.join(folder, dwd_file))

        key = None

    for station in stations:
        weather_folder = os.path.join(folder, station)

        for file in os.listdir(weather_folder):
            if file.startswith('rH') and file.endswith('In.ccd'):
                key = 'relative_humidity_indoor'
            elif file.startswith('rH') and file.endswith('Out.ccd'):
                key = 'relative_humidity'
            elif file.startswith('T') and file.endswith('In.ccd'):
                key = 'temperature_indoor'
            elif file.startswith('T') and file.endswith('Out.ccd'):
                key = 'temperature'

            if key:
                weather_dict[key] = weather_parser.ccd_to_list(os.path.join(weather_folder, file))

            key = None

        # Split years
        def hours_per_year(start, stop):
            while start < stop:
                yield 8760
                start += 1

        def accumulate_hours(hour_list):
            accumulated_list = [0, ]

            for i in range(0, len(hour_list)):
                accumulated_list.append(accumulated_list[i] + hour_list[i])

            return accumulated_list

        hours = [hour
                 for hour in hours_per_year(weather_dict['time'][0],
                                            weather_dict['time'][1])]

        accumulated_hours = accumulate_hours(hours)

        # Add yearly weather entries
        entry_ids = []
        for year_index in range(1, len(accumulated_hours)):
            yearly_weather_entry = weather_entry.Weather()

            yearly_weather_entry.location_name = station
            yearly_weather_entry.dates = {'start': datetime.datetime(year=2016 + year_index, month=1, day=1, hour=1),
                                          'stop': datetime.datetime(year=2017 + year_index, month=1, day=1, hour=0)}

            yearly_weather_entry.year = 2016 + year_index

            yearly_weather_entry.location = [11.19, 50.59]
            yearly_weather_entry.altitude = 208

            yearly_weather_entry.source = {'comment': 'TU Dresden', 'url': None, 'file': 'multiple'}

            yearly_weather_entry.units = {'temperature': 'C',
                                          'relative_humidity': '-',
                                          'long_wave_radiation': 'W/m2',
                                          'diffuse_radiation': 'W/m2',
                                          'direct_radiation': 'W/m2'
                                          }

            # Climate Data
            weather = {
                'temperature': weather_dict['temperature'][
                               accumulated_hours[year_index - 1]:
                               accumulated_hours[year_index]],
                'relative_humidity': weather_dict['relative_humidity'][
                                     accumulated_hours[year_index - 1]:
                                     accumulated_hours[year_index]],
                'temperature_indoor': weather_dict['temperature_indoor'][
                                      accumulated_hours[year_index - 1]:
                                      accumulated_hours[year_index]],
                'relative_humidity_indoor': weather_dict['relative_humidity_indoor'][
                                            accumulated_hours[year_index - 1]:
                                            accumulated_hours[year_index]],
                'long_wave_radiation': weather_dict['long_wave_radiation'][
                                       accumulated_hours[year_index - 1]:
                                       accumulated_hours[year_index]],
                'diffuse_radiation': weather_dict['diffuse_radiation'][
                                     accumulated_hours[year_index - 1]:
                                     accumulated_hours[year_index]],
                'direct_radiation': weather_dict['direct_radiation'][
                                    accumulated_hours[year_index - 1]:
                                    accumulated_hours[year_index]]
            }

            yearly_weather_entry.weather_data.put(bson.BSON.encode(weather))
            yearly_weather_entry.save()
            entry_ids.append(yearly_weather_entry.id)

            yearly_weather_entry.reload()

            print(f'Uploaded weather files from {yearly_weather_entry.location_name} '
                  f'for year {yearly_weather_entry.year}')


def create_strategy(folder):
    design = []

    scenario = {'generic_scenario': None}

    distributions = {'exterior_heat_transfer_coefficient_slope':
                         {'type': 'uniform', 'range': [1, 4], },

                     'solar_absorption':
                         {'type': 'uniform', 'range': [0.4, 0.8], },

                     'interior_heat_transfer_coefficient':
                         {'type': 'uniform', 'range': [5, 10], },

                     'interior_moisture_transfer_coefficient':
                         {'type': 'uniform', 'range': [1*10 ** -8, 3*10 ** -8], },

                     'wall_orientation':
                         {'type': 'uniform', 'range': [135, 225], },

                     'wall_core_material':
                         {'type': 'discrete', 'range': inputs.wall_core_materials(folder), },

                     'initial_temperature':
                         {'type': 'uniform', 'range': [0, 10], },

                     'initial_relhum':
                         {'type': 'uniform', 'range': [50, 90], },

                     'exterior_climate': {
                         'type': 'discrete',
                         'range': ['Ms-11-5']
                         }
                     }

    sampling_settings = {'initial samples per set': 1,
                         'add samples per run': 1,
                         'max samples': 500,
                         'sequence': 10,
                         'standard error threshold': 0.1,
                         'raw sample size': 2 ** 9}

    combined_dict = {'design': design, 'scenario': scenario,
                     'distributions': distributions, 'settings': sampling_settings}

    with open(os.path.join(folder, 'sampling_strategy.json'), 'w') as file:
        json.dump(combined_dict, file)


def upload_strategy(folder):
    strategy = os.path.join(folder, 'sampling_strategy.json')

    with open(strategy) as file:
        data = json.load(file)

    sampling_interactions.upload_sampling_strategy(data)


def upload_designs(folder):
    strategy = sample_entry.Strategy.objects().first()

    #for file in os.listdir(folder):
    file = 'Ms-11-5-DWD Weimar.d6p'
    delphin_interactions.upload_design_file(os.path.join(folder, file), strategy.id)


# upload_weather(r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\inputs\weather')
# upload_materials(r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\inputs')
create_strategy(r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\inputs')
upload_strategy(r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\inputs')
upload_designs(r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\inputs\design')

mongo_setup.global_end_ssh(server)
