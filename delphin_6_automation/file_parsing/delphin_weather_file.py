__author__ = "Christian Kongsgaard"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import numpy as np
import datetime
import os

# RiBuild Modules:
from delphin_6_automation.nosql.db_templates import weather_entry as weather_db

# -------------------------------------------------------------------------------------------------------------------- #
# WEATHER PARSING


def dict_to_ccd(weather: dict, path: str) -> bool:
    """
    Takes an weather dict and converts it into a .ccd file

    :param weather: material dict
    :param path: Path to where .ccd should be placed.
    :return: True
    """

    # TODO - Create function
    return True


def wac_to_dict(file_path: str) -> dict:
    weather_dict = {'longitude': '',
                    'latitude': '',
                    'altitude': '',
                    'time': [],
                    'temperature': [],
                    'relative_humidity': [],
                    'horizontal_global_solar_radiation': [],
                    'diffuse_horizontal_solar_radiation': [],
                    'air_pressure': [],
                    'vertical_rain': [],
                    'wind_direction': [],
                    'wind_speed': [],
                    'cloud_index': [],
                    'atmospheric_counter_horizontal_long_wave_radiation': [],
                    'atmospheric_horizontal_long_wave_radiation': [],
                    'ground_temperature': [],
                    'ground_reflectance': []
                    }

    file_obj = open(file_path, 'r')
    file_lines = file_obj.readlines()
    file_obj.close()

    weather_dict['longitude'] = float(file_lines[4].split('\t')[0].strip())
    weather_dict['latitude'] = float(file_lines[5].split('\t')[0].strip())
    weather_dict['altitude'] = float(file_lines[6].split('\t')[0].strip())

    for line in file_lines[12:]:
        splitted_line = line.split('\t')
        weather_dict['time'].append(datetime.datetime.strptime(splitted_line[0].strip(), '%Y-%m-%d %H:%M'))
        weather_dict['temperature'].append(float(splitted_line[1].strip()))
        weather_dict['relative_humidity'].append(float(splitted_line[2].strip()))
        weather_dict['horizontal_global_solar_radiation'].append(float(splitted_line[3].strip()))
        weather_dict['diffuse_horizontal_solar_radiation'].append(float(splitted_line[4].strip()))
        weather_dict['air_pressure'].append(float(splitted_line[5].strip()))
        weather_dict['vertical_rain'].append(float(splitted_line[6].strip()))
        weather_dict['wind_direction'].append(float(splitted_line[7].strip()))
        weather_dict['wind_speed'].append(float(splitted_line[8].strip()))
        weather_dict['cloud_index'].append(float(splitted_line[9].strip()))
        weather_dict['atmospheric_counter_horizontal_long_wave_radiation'].append(float(splitted_line[10].strip()))
        weather_dict['atmospheric_horizontal_long_wave_radiation'].append(float(splitted_line[11].strip()))
        weather_dict['ground_temperature'].append(float(splitted_line[12].strip()))
        weather_dict['ground_reflectance'].append(float(splitted_line[13].strip()))

    return weather_dict


def wac_to_db(file_path: str) -> list:

    weather_dict = wac_to_dict(file_path)

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
             for hour in hours_per_year(weather_dict['time'][0].year,
                                        weather_dict['time'][-1].year)]

    accumulated_hours = accumulate_hours(hours)

    # Add yearly weather entries
    entry_ids = []
    for year_index in range(1, len(accumulated_hours)):
        yearly_weather_entry = weather_db.Weather()

        # Meta Data
        yearly_weather_entry.location_name = os.path.split(file_path)[-1].split('_')[0]
        year_dates = weather_dict['time'][accumulated_hours[year_index - 1]: accumulated_hours[year_index]]
        yearly_weather_entry.dates = {'start': year_dates[0],
                                      'stop': year_dates[-1]}

        yearly_weather_entry.year = year_dates[0].year

        yearly_weather_entry.location = [weather_dict['longitude'], weather_dict['latitude']]
        yearly_weather_entry.altitude = weather_dict['altitude']

        yearly_weather_entry.source = {'comment': 'Climate for Culture',
                                       'url': 'https://www.climateforculture.eu/',
                                       'file': os.path.split(file_path)[-1]}

        yearly_weather_entry.units = {'temperature': 'C',
                                      'relative_humidity': '-',
                                      'vertical_rain': 'mm/h',
                                      'wind_direction': 'degrees',
                                      'wind_speed': 'm/s',
                                      'long_wave_radiation': 'W/m2',
                                      'diffuse_radiation': 'W/m2',
                                      'direct_radiation': 'W/m2'
                                      }

        # Climate Data
        yearly_weather_entry.temperature = weather_dict['temperature'][
                                           accumulated_hours[year_index - 1]:
                                           accumulated_hours[year_index]]

        yearly_weather_entry.relative_humidity = weather_dict['relative_humidity'][
                                                 accumulated_hours[year_index - 1]:
                                                 accumulated_hours[year_index]]

        yearly_weather_entry.vertical_rain = weather_dict['vertical_rain'][
                                             accumulated_hours[year_index - 1]:
                                             accumulated_hours[year_index]]

        yearly_weather_entry.wind_direction = weather_dict['wind_direction'][
                                              accumulated_hours[year_index - 1]:
                                              accumulated_hours[year_index]]

        yearly_weather_entry.wind_speed = weather_dict['wind_speed'][
                                          accumulated_hours[year_index - 1]:
                                          accumulated_hours[year_index]]

        yearly_weather_entry.long_wave_radiation = weather_dict['atmospheric_counter_horizontal_long_wave_radiation'][
                                                   accumulated_hours[year_index - 1]:
                                                   accumulated_hours[year_index]]

        yearly_weather_entry.diffuse_radiation = weather_dict['diffuse_horizontal_solar_radiation'][
                                                 accumulated_hours[year_index - 1]:
                                                 accumulated_hours[year_index]]

        yearly_weather_entry.direct_radiation = weather_dict['horizontal_global_solar_radiation'][
                                                accumulated_hours[year_index - 1]:
                                                accumulated_hours[year_index]]
        yearly_weather_entry.save()
        entry_ids.append(yearly_weather_entry.id)

    return entry_ids


def convert_weather_to_indoor_climate(temperature: list, indoor_class) -> tuple:

    # Create daily temperature average
    temperature_matrix = np.reshape(temperature, (365, 24))
    daily_temperature_average = np.sum(temperature_matrix, 1) / 24

    def en13788(indoor_class_: str, daily_temperature_average_: np.array) -> tuple:
        """
        Only the continental class is implemented.

        :param indoor_class_: Either a or b
        :type indoor_class_: str
        :param daily_temperature_average_: daily average of air temperature
        :type daily_temperature_average_: numpy array
        :return: Indoor temperature and relative humidity
        :rtype: tuple
        """

        if indoor_class_.lower() == 'a':
            delta_rh = 0
        elif indoor_class_.lower() == 'b':
            delta_rh = 0.05
        else:
            raise ValueError(f"Wrong indoor class. It has to be either a or b. Value given was: {indoor_class}")

        indoor_temperature_ = []
        indoor_relative_humidity_ = []

        # Create indoor temperature
        for t in daily_temperature_average_:
            if t <= 10:
                indoor_temperature_.append([20, ] * 24)
            elif t >= 20:
                indoor_temperature_.append([25, ] * 24)
            else:
                indoor_temperature_.append([0.5 * t + 15, ] * 24)

        # Create indoor relative humidity
        for rh in daily_temperature_average_:
            if rh <= -10:
                indoor_relative_humidity_.append([0.35 + delta_rh, ] * 24)
            elif rh >= 20:
                indoor_relative_humidity_.append([0.65 + delta_rh, ] * 24)
            else:
                indoor_relative_humidity_.append([rh + 0.45 + delta_rh, ] * 24)

        return list(np.ravel(indoor_temperature_)), list(np.ravel(indoor_relative_humidity_))

    return en13788(indoor_class, daily_temperature_average)
