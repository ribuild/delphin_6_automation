__author__ = "Christian Kongsgaard"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import numpy as np
import datetime

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
                    'rain_intensity': [],
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
        weather_dict['rain_intensity'].append(float(splitted_line[6].strip()))
        weather_dict['wind_direction'].append(float(splitted_line[7].strip()))
        weather_dict['wind_speed'].append(float(splitted_line[8].strip()))
        weather_dict['cloud_index'].append(float(splitted_line[9].strip()))
        weather_dict['atmospheric_counter_horizontal_long_wave_radiation'].append(float(splitted_line[10].strip()))
        weather_dict['atmospheric_horizontal_long_wave_radiation'].append(float(splitted_line[11].strip()))
        weather_dict['ground_temperature'].append(float(splitted_line[12].strip()))
        weather_dict['ground_reflectance'].append(float(splitted_line[13].strip()))

    return weather_dict


def wac_to_db(file_path: str) -> str:

    weather_dict = wac_to_dict(file_path)
    entry = weather_db.Weather()

    entry.temperature = weather_dict['temperature']
    entry.relative_humidity = weather_dict['relative_humidity']
    entry.vertical_rain = weather_dict['rain_intensity']
    entry.wind_direction = weather_dict['wind_direction']
    entry.wind_speed = weather_dict['wind_speed']
    entry.long_wave_radiation = weather_dict['atmospheric_horizontal_long_wave_radiation']
    entry.diffuse_radiation = weather_dict['diffuse_horizontal_solar_radiation']
    entry.direct_radiation = weather_dict['horizontal_global_solar_radiation']
    entry.dates = weather_dict['time']

    entry.location = [weather_dict['longitude'],
                      weather_dict['latitude'],
                      ]
    entry.altitude = weather_dict['altitude']

    entry.source = {'comment': 'Culture for Climate',
                    'file': file_path}

    entry.units = {'temperature': 'C',
                   'relative_humidity': '-',
                   'rain_intensity': 'mm/h',
                   'wind_direction': 'degrees',
                   'wind_speed': 'm/s',
                   'atmospheric_horizontal_long_wave_radiation': 'W/m2',
                   'diffuse_horizontal_solar_radiation': 'W/m2',
                   'horizontal_global_solar_radiation': 'W/m2'
                   }

    entry.save()

    return entry.id


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
            delta_rh = 5
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
                indoor_relative_humidity_.append([35 + delta_rh, ] * 24)
            elif rh >= 20:
                indoor_relative_humidity_.append([65 + delta_rh, ] * 24)
            else:
                indoor_relative_humidity_.append([rh + 45 + delta_rh, ] * 24)

        return list(np.ravel(indoor_temperature_)), list(np.ravel(indoor_relative_humidity_))

    return en13788(indoor_class, daily_temperature_average)
