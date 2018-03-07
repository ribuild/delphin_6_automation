__author__ = "Christian Kongsgaard"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:


# RiBuild Modules:
from delphin_6_automation.database_interactions.db_templates import delphin_entry as delphin_db
from delphin_6_automation.file_parsing import weather_parser
from delphin_6_automation.delphin_setup import weather_modeling
import delphin_6_automation.database_interactions.db_templates.weather_entry as weather_db

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

    delphin_document.update(push_all__weather=weather_documents)

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

    return delphin_document.id


def concatenate_weather(delphin_document: delphin_db.Delphin) -> dict:

    weather_dict = {'temperature': [], 'relative_humidity': [],
                    'vertical_rain': [], 'wind_direction': [],
                    'wind_speed': [], 'long_wave_radiation': [],
                    'diffuse_radiation': [], 'direct_radiation': [],
                    'year': [], 'location_name': [], 'altitude': []}

    for weather_document in delphin_document.weather:

        weather_document_as_dict = weather_document.to_mongo()
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

            elif weather_key in ['year', 'location_name', 'altitude']:
                weather_dict[weather_key].append(weather_document_as_dict[weather_key])

    return weather_dict


def change_weather_file_location(delphin_id: str, folder: str):

    delphin_document = delphin_db.Delphin.objects(id=delphin_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    climate_conditions = delphin_dict['DelphinProject']['Conditions']['ClimateConditions']['ClimateCondition']

    for index in range(0, len(climate_conditions)):
            if climate_conditions[index]['@type'] == 'Temperature':
                if 'indoor' in climate_conditions[index]['@name']:
                    climate_conditions[index]['Filename'] = folder + '/indoor_temperature.ccd'
                else:
                    climate_conditions[index]['Filename'] = folder + '/temperature.ccd'

            elif climate_conditions[index]['@type'] == 'RelativeHumidity':
                if 'indoor' in climate_conditions[index]['@name']:
                    climate_conditions[index]['Filename'] = folder + '/indoor_relative_humidity.ccd'
                else:
                    climate_conditions[index]['Filename'] = folder + '/relative_humidity.ccd'

            elif climate_conditions[index]['@type'] == 'SWRadiationDiffuse':
                climate_conditions[index]['Filename'] = folder + '/diffuse_radiation.ccd'

            elif climate_conditions[index]['@type'] == 'SWRadiationDirect':
                climate_conditions[index]['Filename'] = folder + '/direct_radiation.ccd'

            elif climate_conditions[index]['@type'] == 'RainFluxHorizontal':
                climate_conditions[index]['Filename'] = folder + '/vertical_rain.ccd'

            elif climate_conditions[index]['@type'] == 'WindDirection':
                climate_conditions[index]['Filename'] = folder + '/wind_direction.ccd'

            elif climate_conditions[index]['@type'] == 'WindVelocity':
                climate_conditions[index]['Filename'] = folder + '/wind_speed.ccd'

            elif climate_conditions[index]['@type'] == 'LWRadiationBalance':
                climate_conditions[index]['Filename'] = folder + '/long_wave_radiation.ccd'

    delphin_document.update(set__dp6_file=delphin_dict)

    return delphin_document.id


def download_weather(delphin_id: str, folder: str) -> bool:

    delphin_document = delphin_db.Delphin.objects(id=delphin_id).first()

    weather = concatenate_weather(delphin_document)
    weather['indoor_temperature'], weather['indoor_relative_humidity'] = \
        weather_modeling.convert_weather_to_indoor_climate(weather['temperature'],
                                                           delphin_document.indoor_climate)
    weather_parser.dict_to_ccd(weather, folder)
    change_weather_file_location(delphin_id, folder)

    return True
