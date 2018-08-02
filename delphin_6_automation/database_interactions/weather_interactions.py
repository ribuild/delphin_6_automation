__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import numpy as np
import bson

# RiBuild Modules:
from delphin_6_automation.database_interactions.db_templates import delphin_entry as delphin_db
from delphin_6_automation.file_parsing import weather_parser
from delphin_6_automation.delphin_setup import weather_modeling
import delphin_6_automation.database_interactions.db_templates.weather_entry as weather_db
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger(__name__)

# -------------------------------------------------------------------------------------------------------------------- #
# WEATHER INTERACTIONS


def list_project_weather(sim_id: str) -> list:
    """
    Returns a list with the weather in a project entry.

    :param sim_id: Delphin entry ID
    :return: List with material file names
    """

    weather = delphin_db.Delphin.objects(id=sim_id).first().dp6_file.DelphinProject.Conditions.ClimateConditions.ClimateCondition

    weather_list = [(w.type, w.Filename)
                    for w in weather]

    return weather_list


def assign_weather_by_name_and_years(delphin_id: str, weather_station_name: str, years: list) -> str:

    weather_documents = []
    for year in years:
        weather_documents.append(weather_db.Weather.objects(location_name=weather_station_name, year=year).first())

    delphin_id = assign_weather_to_project(delphin_id, weather_documents)
    logger.debug(f'Assigned weather from {weather_station_name} '
                 f'for years: {years} to Delphin project with ID: {delphin_id}')

    return delphin_id


def assign_weather_to_project(delphin_id: str, weather_documents: list) -> str:
    """
    Assign weather to a Delphin entry

    :param delphin_id: Delphin document database.rst ID
    :type delphin_id: str
    :param weather_documents: List with weather entries
    :type weather_documents: list
    :return: Database ID
    :rtype: str
    """

    # Save climate class to delphin document
    delphin_document = delphin_db.Delphin.objects(id=delphin_id).first()

    if delphin_document.weather:
        delphin_document.update(pull_all__weather=delphin_document.weather)

    [delphin_document.update(push__weather=weather) for weather in weather_documents]

    logger.debug(f'Weather documents with IDs: {[weather for weather in weather_documents]} '
                 f'assigned to Delphin project with ID: {delphin_id}')

    return delphin_document.id


def assign_indoor_climate_to_project(delphin_id: str, climate_class: str) -> str:
    """
    Assign indoor climate class to a Delphin entry

    :param delphin_id: Database ID
    :type delphin_id: str
    :param climate_class: Climate class can be either a or b
    :type climate_class: str
    :return: Database ID
    :rtype: str
    """

    # Make check
    if not climate_class.lower() in ['a', 'b']:
        raise ValueError(f'Wrong climate class. It has to be either a or b. '
                         f'Climate class given was: {climate_class}')

    # Save climate class to delphin document
    delphin_document = delphin_db.Delphin.objects(id=delphin_id).first()
    delphin_document.update(set__indoor_climate=climate_class.lower())

    logger.debug(f'Added indoor climate class {climate_class} to Delphin project with ID: {delphin_id}')

    return delphin_document.id


def concatenate_weather(delphin_document: delphin_db.Delphin) -> dict:

    weather_dict = {'temperature': [], 'relative_humidity': [],
                    'vertical_rain': [], 'wind_direction': [],
                    'wind_speed': [], 'long_wave_radiation': [],
                    'diffuse_radiation': [], 'direct_radiation': [],
                    'year': [], 'location_name': [], 'altitude': []}
    sim_id = delphin_document.id

    for index in range(len(delphin_document.weather)):
        reloaded_delphin = delphin_db.Delphin.objects(id=sim_id).first()

        weather_document_as_dict: dict = bson.BSON.decode(reloaded_delphin.weather[index].weather_data.read())
        for weather_key in weather_document_as_dict:
            if weather_key in ['temperature', 'vertical_rain',
                               'wind_direction', 'wind_speed',
                               'long_wave_radiation', 'diffuse_radiation',
                               'direct_radiation']:

                weather_dict[weather_key].extend(weather_document_as_dict[weather_key])

            elif weather_key == 'relative_humidity':
                relhum = [rh * 100
                          for rh in weather_document_as_dict[weather_key]]
                weather_dict[weather_key].extend(relhum)

        weather_dict['year'].append(reloaded_delphin.weather[index].year)
        weather_dict['location_name'].append(reloaded_delphin.weather[index].location_name)
        weather_dict['altitude'].append(reloaded_delphin.weather[index].altitude)

    logger.debug(f'Concatenated weather for Delphin project with ID: {sim_id}')

    return weather_dict


def change_weather_file_location(delphin_document: delphin_db.Delphin):

    folder = '${Project Directory}/weather'
    delphin_dict = dict(delphin_document.dp6_file)
    climate_conditions = delphin_dict['DelphinProject']['Conditions']['ClimateConditions']['ClimateCondition']

    for index in range(0, len(climate_conditions)):
            if climate_conditions[index]['@type'] == 'Temperature':
                if 'indoor' in climate_conditions[index]['@name'] or 'interior' in climate_conditions[index]['@name']:
                    climate_conditions[index]['Filename'] = folder + '/indoor_temperature.ccd'
                else:
                    climate_conditions[index]['Filename'] = folder + '/temperature.ccd'

            elif climate_conditions[index]['@type'] == 'RelativeHumidity':
                if 'indoor' in climate_conditions[index]['@name'] or 'interior' in climate_conditions[index]['@name']:
                    climate_conditions[index]['Filename'] = folder + '/indoor_relative_humidity.ccd'
                else:
                    climate_conditions[index]['Filename'] = folder + '/relative_humidity.ccd'

            elif climate_conditions[index]['@type'] == 'SWRadiationDiffuse':
                climate_conditions[index]['Filename'] = folder + '/diffuse_radiation.ccd'

            elif climate_conditions[index]['@type'] == 'SWRadiationDirect':
                climate_conditions[index]['Filename'] = folder + '/direct_radiation.ccd'

            elif climate_conditions[index]['@type'] == 'SWRadiationImposed':
                climate_conditions[index]['Filename'] = folder + '/short_wave_radiation.ccd'

            elif climate_conditions[index]['@type'] == 'RainFluxNormal':
                climate_conditions[index]['Filename'] = folder + '/wind_driven_rain.ccd'

            elif climate_conditions[index]['@type'] == 'WindDirection':
                climate_conditions[index]['Filename'] = folder + '/wind_direction.ccd'

            elif climate_conditions[index]['@type'] == 'WindVelocity':
                climate_conditions[index]['Filename'] = folder + '/wind_speed.ccd'

            elif climate_conditions[index]['@type'] == 'LWRadiationSkyEmission':
                climate_conditions[index]['Filename'] = folder + '/long_wave_radiation.ccd'

    delphin_document.update(set__dp6_file=delphin_dict)

    logger.debug(f'Changed weather directory to {folder} for Delphin project with ID: {delphin_document.id}')

    return delphin_document.id


def download_weather(delphin_document: delphin_db.Delphin, folder: str) -> bool:

    weather = concatenate_weather(delphin_document)
    weather['indoor_temperature'], weather['indoor_relative_humidity'] = \
        weather_modeling.convert_weather_to_indoor_climate(weather['temperature'],
                                                           delphin_document.indoor_climate)
    orientation = float(delphin_document.dp6_file['DelphinProject']['Conditions']['Interfaces'][
                          'Interface'][0]['IBK:Parameter']['#text'])
    wall_location = {'height': 5, 'width': 5}
    weather['wind_driven_rain'] = weather_modeling.driving_rain(weather['vertical_rain'], weather['wind_direction'],
                                                                weather['wind_speed'], wall_location, orientation,
                                                                inclination=90, catch_ratio=1)

    delphin_document.reload()
    latitude = delphin_document.weather[0].location[0]
    longitude = delphin_document.weather[0].location[1]
    radiation = np.array(weather['diffuse_radiation']) + np.array(weather['diffuse_radiation'])
    weather['short_wave_radiation'] = weather_modeling.short_wave_radiation(radiation, longitude,
                                                                            latitude, 0, orientation)

    for weather_key in weather.keys():
        if weather_key not in ['year', 'location_name', 'altitude']:
            weather[weather_key].extend(weather[weather_key][-2:])

    weather_parser.dict_to_ccd(weather, folder)
    change_weather_file_location(delphin_document)

    logger.debug(f'Downloaded weather for Delphin project with ID: {delphin_document.id} to {folder}')

    return True


def update_short_wave_condition(delphin_dict):

    climate_conditions = delphin_dict['DelphinProject']['Conditions']['ClimateConditions']['ClimateCondition']

    for climate_condition in climate_conditions:
        if climate_condition['@type'] == 'SWRadiationDiffuse':
            diffuse_radiation = climate_condition['@name']
        elif climate_condition['@type'] == 'SWRadiationDirect':
            direct_radiation = climate_condition['@name']

    boundary_conditions = delphin_dict['DelphinProject']['Conditions']['BoundaryConditions']['BoundaryCondition']

    """
    for boundary_condition in boundary_conditions:
        if boundary_condition['@type'] == 'ShortWaveRadiation':
            try:
                for cc_ref in boundary_condition['CCReference']:
                    if cc_ref['@type'] == 'SWRadiationDirect':
                        cc_ref['#text'] = direct_radiation

                    elif cc_ref['@type'] == 'SWRadiationDiffuse':
                        cc_ref['#text'] = diffuse_radiation
            except KeyError:
                boundary_condition['CCReference'] = [OrderedDict((('@type', 'SWRadiationDirect'),
                                                                 ('#text', direct_radiation))),
                                                     OrderedDict((('@type', 'SWRadiationDiffuse'),
                                                                 ('#text', diffuse_radiation)))]
    """

    return delphin_dict


def upload_weather_to_db(file_path: str) -> list:
    weather_dict = weather_parser.wac_to_dict(file_path)

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
        weather = {
            'temperature': weather_dict['temperature'][
                           accumulated_hours[year_index - 1]:
                           accumulated_hours[year_index]],
            'relative_humidity': weather_dict['relative_humidity'][
                                 accumulated_hours[year_index - 1]:
                                 accumulated_hours[year_index]],
            'vertical_rain': weather_dict['vertical_rain'][
                             accumulated_hours[year_index - 1]:
                             accumulated_hours[year_index]],
            'wind_direction': weather_dict['wind_direction'][
                              accumulated_hours[year_index - 1]:
                              accumulated_hours[year_index]],
            'wind_speed': weather_dict['wind_speed'][
                          accumulated_hours[year_index - 1]:
                          accumulated_hours[year_index]],
            'long_wave_radiation': weather_dict['atmospheric_counter_horizontal_long_wave_radiation'][
                                   accumulated_hours[year_index - 1]:
                                   accumulated_hours[year_index]],
            'diffuse_radiation': weather_dict['diffuse_horizontal_solar_radiation'][
                                 accumulated_hours[year_index - 1]:
                                 accumulated_hours[year_index]],
            'direct_radiation': weather_dict['horizontal_global_solar_radiation'][
                                accumulated_hours[year_index - 1]:
                                accumulated_hours[year_index]]
        }

        yearly_weather_entry.weather_data.put(bson.BSON.encode(weather))
        yearly_weather_entry.save()
        entry_ids.append(yearly_weather_entry.id)

        yearly_weather_entry.reload()

        logger.debug(f'Uploaded weather files from {yearly_weather_entry.location_name} '
                     f'for year {yearly_weather_entry.year}')

    return entry_ids
