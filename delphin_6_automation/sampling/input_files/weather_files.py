__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import geocoder
import os

# RiBuild Modules
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions import auth

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def get_weather_stations_in_ribuild():
    weather_folder = r'D:\Weatherdata\RAW\Climate for Culture\CTL_2021_2050'

    stations_in_ribuild = []
    for file in os.listdir(weather_folder):
        if file.endswith('.WAC'):
            title = file.split('_')

            if len(title) == 6:
                city, long, lat, *_ = title
            elif len(title) == 7:
                city, country, long, lat, *_ = title
            elif len(title) == 8:
                __, ___, city, long, lat, *_ = title
            elif len(title) == 9:
                city, street, place, country, long, lat, *_ = title
            else:
                raise KeyError(f'List is {len(title)} long. Title was {title}')

            geo = geocoder.osm([float(lat), float(long)], method='reverse')

            if geo.country in ['Sverige', 'Danmark', 'Latvija', 'Deutschland',
                               'België / Belgique / Belgien', 'Italia', 'Schweiz/Suisse/Svizzera/Svizra']:
                stations_in_ribuild.append(file)

    return stations_in_ribuild


def create_file_with_stations():
    stations = get_weather_stations_in_ribuild()
    #print(len(stations))

    out_path = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\delphin_6_automation\sampling\input_files\weather_stations.txt'

    with open(out_path, 'w') as out_file:
        for station in stations:
            out_file.write(station + '\n')


def upload_weather_stations():

    mongo_setup.global_init(auth.auth_dict)
    ws_path = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\delphin_6_automation\sampling\input_files\weather_stations.txt'

    with open(ws_path, 'w') as file:
        files = file.readlines()

    weather_folder = r'D:\Weatherdata\RAW\Climate for Culture\CTL_2021_2050'
    for ws in files:
        weather_interactions.upload_weather_to_db(os.path.join(weather_folder, ws))
