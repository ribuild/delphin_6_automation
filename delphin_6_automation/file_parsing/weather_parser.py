__author__ = "Christian Kongsgaard"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import datetime
import os

# RiBuild Modules:


# -------------------------------------------------------------------------------------------------------------------- #
# WEATHER PARSING


def dict_to_ccd(weather_dict: dict, folder: str) -> bool:
    """
    Takes an weather dict and converts it into a .ccd file

    :param weather_dict: weather dict from mongo_db
    :param folder: Folder to where .ccd's should be placed.
    :return: True
    """

    if not os.path.isdir(folder):
        os.mkdir(folder)

    parameter_dict = {
        "temperature": {"description": "Air temperature [C] (TA)",
                        "intro": "TEMPER   C",
                        "factor": 1,
                        "abr": "TA"},

        "relative_humidity": {"description": "Relative Humidity [%] (HREL)",
                              "intro": "RELHUM   %",
                              "factor": 1,
                              "abr": "HREL"},

        "diffuse_radiation": {"description": "Diffuse Horizontal Solar Radiation [W/m2] (ISD)",
                              "intro": "DIFRAD   W/m2",
                              "factor": 1,
                              "abr": "ISD"},

        "short_wave_radiation": {"description": "Short Wave Radiation [W/m2] (ISD)",
                                 "intro": "SHWRAD   W/m2",
                                 "factor": 1,
                                 "abr": "SWR"},

        "wind_direction": {"description": "Wind Direction [degrees] (WD)",
                           "intro": "WINDDIR   Deg",
                           "factor": 1,
                           "abr": "WD"},

        "wind_speed": {"description": "Wind Velocity [m/s] (WS)",
                       "intro": "WINDVEL   m/s",
                       "factor": 1,
                       "abr": "WS"},

        "CloudCover": {"description": "Cloud Cover [-] (CI)",
                       "intro": "CLOUDCOV   ---",
                       "factor": 1,
                       "abr": "CI"},

        "direct_radiation": {"description": "Direct Horizontal Solar Radiation [W/m2] (ISvar) [ISGH - ISD]",
                             "intro": "DIRRAD  W/m2",
                             "factor": 1,
                             "abr": "ISVAR"},

        "vertical_rain": {"description": "Rain intensity[mm/h] (RN)",
                          "intro": "HORRAIN   l/m2h",
                          "factor": 1,
                          "abr": "RN"},

        "wind_driven_rain": {"description": "Rain intensity[mm/h] (RN)",
                             "intro": "NORRAIN   l/m2h",
                             "factor": 1,
                             "abr": "RN"},

        "TotalPressure": {"description": "Air pressure [hPa] (PSTA)",
                          "intro": "GASPRESS   hPa",
                          "factor": 1,
                          "abr": "PSTA"},

        "long_wave_radiation": {"description": "Atmospheric Horizontal Long wave Radiation [W/m2] (ILTH)",
                                "intro": "SKYEMISS  W/m2",
                                "factor": 1,
                                "abr": "ILTH"},

        "TerrainCounterRadiation": {"description": "Terrain counter radiation [W/m2](ILAH)",
                                    "intro": "GRINDEMISS  W/m2",
                                    "factor": 1,
                                    "abr": "ILAH"},

        "GlobalRadiation": {"description": "Horizontal Global Solar Radiation [W/m2] (ISGH)",
                            "intro": "SKYEMISS  W/m2",
                            "factor": 1,
                            "abr": "ISGH"},

        "indoor_relative_humidity": {"description": "Indoor Relative Humidity after EN15026 [%] (HREL)",
                                     "intro": "RELHUM   %",
                                     "factor": 1},

        "indoor_temperature": {"description": "Indoor Air temperature after EN15026 [C] (TA)",
                               "intro": "TEMPER   C",
                               "factor": 1},
    }

    for weather_key in weather_dict.keys():
        if weather_key in ['temperature', 'relative_humidity',
                           'wind_driven_rain',
                           'long_wave_radiation',
                           'short_wave_radiation',
                           'indoor_temperature',
                           'indoor_relative_humidity', 'wind_speed']:

            info_dict = dict(parameter_dict[weather_key], **{'year': weather_dict['year']})
            info_dict.update({'location_name': weather_dict['location_name']})
            list_to_ccd(weather_dict[weather_key], info_dict, os.path.join(folder, f'{weather_key}.ccd'))

    return True


def list_to_ccd(weather_list: list, parameter_info: dict, file_path: str) -> bool:
    """
    Converts a weather list into a Delphin weather file (.ccd)

    :param weather_list: List with hourly weather values
    :param parameter_info: Dict with meta data for the weather file. Should contain the following keys: location_name, year, description and intro.
    :param file_path: Full file path for where the .ccd file should be saved.
    :return: True
    """

    # Write meta data
    file_obj = open(file_path, 'w')
    file_obj.write(f"# {parameter_info['location_name']}\n")
    file_obj.write(f"# Year {parameter_info['year']}\n")
    file_obj.write(f"# RIBuild - Hourly values, {parameter_info['description']} \n\n")
    file_obj.write(parameter_info["intro"] + "\n\n")

    # Write data
    day = 0
    hour = 0
    for i in range(len(weather_list)):

        # leap year 29th febuary removal

        if i % 24 == 0 and i != 0:
            hour = 0
            day += 1

        hour_str = str(hour) + ":00:00"
        data = weather_list[i]
        file_obj.write(f'{day:>{6}}{hour_str:>{9}}  {data:.2f}\n')

        hour += 1

    file_obj.close()

    return True


def wac_to_dict(file_path: str) -> dict:
    """Converts a WAC file into a dict"""

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


def ccd_to_list(file_path: str) -> list:
    """Converts a .ccd file into a dict"""

    file = open(file_path, 'r')
    lines = file.readlines()
    file.close()

    data = []

    for line in lines:
        if line.startswith(' '):
            data.append(float(line.split(' ')[-1].strip()))

    return data
