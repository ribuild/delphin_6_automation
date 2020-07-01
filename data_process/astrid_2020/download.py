import bson
import numpy as np

from data_process.astrid_2020.auth import auth_dict
from delphin_6_automation.database_interactions import mongo_setup, delphin_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry, result_raw_entry, sample_entry
from delphin_6_automation.database_interactions.general_interactions import download_full_project_from_database
from delphin_6_automation.database_interactions.weather_interactions import concatenate_weather
from delphin_6_automation.delphin_setup import weather_modeling, delphin_permutations


def get_delphin_ids(start: int, end: int) -> list:
    #ids = delphin_entry.Delphin.objects[start:end].only('id')
    #print(f'Got {ids.count()} projects')
    #print(f'Starting at index {start}')

    #ids = [project.id for project in ids]
    ids = delphin_entry.Delphin.objects(sample_data__design_option__name__in=['1d_bare'])
    print('IDS', ids.count())
    return ids


def download_project(project_id: str, index_: int) -> None:
    """Here you can do your download manipulation."""
    print(f'Processing Project with ID: {project_id} and index: {index_}')

    #get_materials(project_id)
    #get_result_data(project_id)
    #get_sample_data(project_id)
    get_weather_data(project_id)
    #download_to_simulate(project_id)


def get_result_data(project_id: str) -> dict:
    """This function will download the result data from a single Delphin project"""
    result = result_raw_entry.Result.objects(delphin=project_id).first()

    # You have to do this bson decode thing. We save the result as binary blobs to save space.
    data = bson.BSON.decode(result.results.read())

    print(f'Downloading result data for project {project_id}')

    return data


def get_materials(project_id: str) -> dict:
    """Download material data for a Delphin project"""
    delphin_project = delphin_entry.Delphin.objects(id=project_id).only('materials').first()

    print(f'Downloading material data for project {project_id}')

    return delphin_project.materials


def get_sample_data(project_id: str) -> dict:
    """Download the parameters used to generate the Delphin project."""
    delphin_project = delphin_entry.Delphin.objects(id=project_id).only('sample_data').first()

    print(f'Downloading sample data for project {project_id}')

    return delphin_project.sample_data


def get_weather_data(project_id: str) -> dict:
    """This function will download the weather data related to a Delphin project"""
    print(f'Downloading weather data for project {project_id}')
    delphin_document = delphin_entry.Delphin.objects(id=project_id).first()
    weather = concatenate_weather(delphin_document)

    # If there is not already given indoor climate data, then generate them for the standard
    if not weather.get('indoor_temperature') and not weather.get('indoor_relative_humidity'):
        weather['indoor_temperature'], weather['indoor_relative_humidity'] = \
            weather_modeling.convert_weather_to_indoor_climate(weather['temperature'],
                                                               delphin_document.indoor_climate)

    orientation = delphin_permutations.get_orientation(delphin_document.dp6_file)

    # Compute the wind driven rain, if wind and rain are given
    if weather.get('vertical_rain') and weather.get('wind_direction') and weather.get('wind_speed'):

        wall_location = {'height': 5, 'width': 5}
        weather['wind_driven_rain'] = weather_modeling.driving_rain(weather['vertical_rain'], weather['wind_direction'],
                                                                    weather['wind_speed'], wall_location, orientation,
                                                                    inclination=90, catch_ratio=1)

    delphin_document.reload()
    latitude = delphin_document.weather[0].location[0]
    longitude = delphin_document.weather[0].location[1]
    radiation = np.array(weather['direct_radiation']) + np.array(weather['diffuse_radiation'])
    weather['short_wave_radiation'] = weather_modeling.short_wave_radiation(radiation, longitude,
                                                                            latitude, 0, orientation)

    for weather_key in weather.keys():
        if weather_key not in ['year', 'location_name', 'altitude']:
            weather[weather_key].extend(weather[weather_key][-2:])

    print(f'Got weather data for project {project_id}')

    return weather


def download_to_simulate(project_id: str) -> None:
    """Download everything needed to run a Delphin simulation"""
    print(f'Download full Delphin project for ID: {project_id}')
    folder = r"C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\astrid_2020"
    download_full_project_from_database(project_id, folder)


def download_strategy():
    strategy_doc = sample_entry.Strategy.objects().first()
    print('Got Sampling Strategy')

    # Now you have the sampling strategy.
    # You have access to all information it contains.
    # The fields available can be seen: delphin_6_automation/database_interactions/db_templates/sample_entry
    # What you most likely want is either strategy_doc.strategy (the scheme with the variables) strategy_doc.samples_raw (sobol samples)


def download_designs():
    print('Getting design files')
    designs = delphin_entry.Design.objects()
    folder = ""

    # Now you have the designs. They are Delphin projects
    # You can download them with:
    for design in designs:
        print(f'Downloading design: {design.design_name}')
        delphin_interactions.download_delphin_entry(design.d6p_file, folder)


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    # Here you can set which slices of the database you want to download. Start by setting end_point a bit low.
    # Pulling the data for +275k simulation will take some time.
    start_point = 5650
    end_point = 5651

    project_ids = get_delphin_ids(start_point, end_point)

    #for index, project in enumerate(project_ids):
    #    download_project(project, index + start_point)

    mongo_setup.global_end_ssh(server)
