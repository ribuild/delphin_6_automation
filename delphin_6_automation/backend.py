__author__ = "Thomas Perkov"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os

# RiBuild Modules:
import delphin_6_automation.database_interactions.mongo_setup as mongo_setup

from delphin_6_automation.database_interactions.auth import dtu_byg
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry as delphin_db
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.simulation_worker import simulation_worker

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN PERMUTATION FUNCTIONS

"""
Backend user interface:
- Add new simulation(s)
- Monitor the simulation process
- Queue and watch finished simulations
"""


def main():
    print_header()
    config_mongo()
    main_menu()


def print_header():
    print('---------------------------------------------------')
    print('|                                                  |')
    print('|           RiBuild EU research project            |')
    print('|           for hygrothermal simulations           |')
    print('|              (WIP) Test environment              |')
    print('|                                                  |')
    print('---------------------------------------------------')


def config_mongo():
    mongo_setup.global_init(dtu_byg)


def main_menu():
    while True:
        print()
        print("Available actions:")
        print("[a] Add new simulation to queue")
        print("[b] Add new simulation with permutations to queue")
        print("[c] List simulations")
        print("[d] List materials")
        print("[m] Add Delphin material to the database")
        print("[g] Add Ribuild Geometry file to database")
        print("[f] Find simulation")
        print("[w] Queue and view weather data")
        print("[s] Start simulation worker")
        print("[x] Exit")
        print()

        choice = input("> ").strip().lower()

        if choice == 'a':
            [sim_id, *_] = add_to_queue()
            save_ids(sim_id)

        elif choice == 'b':
            id_list = add_permutations_to_queue()
            save_ids(id_list)

        elif choice == 'c':
            list_latest_added_simulations()

        elif choice == 'd':
            view_material_data()

        elif choice == 'm':
            add_delphin_material_to_db()

        elif choice == 'g':
            add_geometry_file_to_db()

        elif choice == 'f':
            find_simulations()

        elif choice == 'w':
            view_weather_data()

        elif choice == 's':
            start_simulation()

        elif not choice or choice == 'x':
            print("see ya!")
            break


def get_simulation_status(id_):
    delphin_document = delphin_db.Delphin.objects(id=id_).first()

    if delphin_document.simulating:
        status = "Is currently being simulated."
    elif delphin_document.simulated:
        status = f"Was simulated on {delphin_document.simulated}"
    else:
        status = 'Is waiting to be simulated'

    print('')
    print(f'Simulation with ID: {id_}\n'
          f'\tAdded: {delphin_document.added_date}\n'
          f'\t{status}')

    if status == f"Was simulated on {delphin_document.simulated}":
        print('')
        download = input("Do you wish to download the results? y/n >")

        if download == 'y':
            print(f'Simulation result will be saved on the Desktop as in the folder: {id_}')
            user_desktop = os.path.join(os.environ["HOMEPATH"], "Desktop")
            general_interactions.download_raw_result(delphin_document.results_raw.id, user_desktop + f'/{id_}')


def find_simulations():
    print('')
    print("The simulations will be identified by their database ID")

    database_ids = input("What is the database ID?\n"
                         "If more than 1 simulation is wished, then the IDs have to be separated with a comma. >")
    database_ids = [id_.strip()
                    for id_ in database_ids.split(',')]
    for id_ in database_ids:
        get_simulation_status(id_)


def view_material_data():

    while True:
        print('')
        print("[l] List materials")
        print("[m] Add Delphin material to the database")
        print("[d] Download material")
        print("[x] Return to main menu")
        print('')

        choice = input("> ").strip().lower()

        if choice == 'l':
            print('The RIBuild Database currently contains the following materials:\n')
            materials = general_interactions.list_materials()
            general_interactions.print_material_dict(materials)

        elif choice == 'm':
            add_delphin_material_to_db()

        elif choice == 'd':
            download_delphin_material()

        elif choice == 'x':
            return None


def view_weather_data():

    while True:
        print('')
        print("[v] List weather stations")
        print("[x] Return to main menu")
        print('')

        choice = input("> ").strip().lower()

        if choice == 'v':
            print('The RIBuild Database currently contains the following weather stations:\n')
            weather_stations = general_interactions.list_weather_stations()
            general_interactions.print_weather_stations_dict(weather_stations)

        elif choice == 'x':
            return None


def add_to_queue():

    delphin_file = str(input("File path for the Delphin file >"))
    priority = str(input("Simulation Priority - high, medium or low >"))
    climate_class = str(input('What climate class should be assigned? A or B can be chosen. >'))

    sim_id = general_interactions.add_to_simulation_queue(delphin_file, priority)
    weather_interactions.assign_indoor_climate_to_project(sim_id, climate_class)
    location_name, years = add_weather_to_simulation(sim_id)

    print('Simulation ID:', sim_id,
          '\n To retrieve the results of a simulation the simulation ID is needed.')

    return sim_id, general_interactions.queue_priorities(priority), location_name, years, climate_class


def add_permutations_to_queue():
    print('First upload the original file. Afterwards permutations can be chosen.')

    id_list = []
    original_id, priority, location_name, years, climate_class = add_to_queue()
    id_list.append(original_id)
    modified_ids, choice = list_permutation_options(original_id, priority)

    if choice != 'c':
        for id_ in modified_ids:
            weather_interactions.assign_weather_by_name_and_years(id_, location_name, years)
            weather_interactions.assign_indoor_climate_to_project(id_, climate_class)

    id_list.extend(modified_ids)

    return id_list


def save_ids(simulation_id):

    save = str(input('Save Simulation ID to text file? (y/n)'))
    if save == 'y':
        print('Simulation will be saved on the Desktop as simulation_id.txt ')
        user_desktop = os.path.join(os.environ["HOMEPATH"], "Desktop")
        id_file = open(user_desktop + '/simulation_id.txt', 'w')

        if not isinstance(simulation_id, list):
            id_file.write(str(simulation_id))

        else:
            for id_ in simulation_id:
                id_file.write(str(id_) + '\n')

        id_file.close()

    else:
        print('Simulation ID was not saved.')
        return


def add_weather_to_simulation(simulation_id):

    location_name = str(input("What weather station should be used? >"))
    years = input("Which years should be used?.\n"
                  "If more than 1 year is wished, then the values have to be separated with a comma. >")
    years = [int(year.strip())
             for year in years.split(',')]
    weather_interactions.assign_weather_by_name_and_years(simulation_id, location_name, years)

    return location_name, years


def list_permutation_options(original_id, priority):

    print()
    print("Available actions:")
    print("[a] Change layer width")
    print("[b] Change layer material")
    print("[c] Change weather")
    print("[d] Change wall orientation")
    print("[e] Change boundary coefficient")
    print("[x] Exit")
    print()

    choice = input("> ").strip().lower()

    if choice == 'a':
        ids = layer_width_permutation(original_id, priority)

    elif choice == 'b':
        ids = layer_material_permutation(original_id, priority)

    elif choice == 'c':
        ids = weather_permutation(original_id, priority)

    elif choice == 'd':
        ids = wall_permutation(original_id, priority)

    elif choice == 'e':
        ids = boundary_permutation(original_id, priority)

    else:
        ids = ''

    return ids, choice


def layer_width_permutation(simulation_id, priority):

    print('')
    print("The layer will be identified by the name of the material in the layer.")

    layer_material = input("What is the name of the material? >")
    widths = input("Input wished layer widths in meter.\n"
                   "If more than 1 width is wished, then the values have to be separated with a comma. >")
    widths = [float(width.strip())
              for width in widths.split(',')]

    print('')
    print(f'Following values given: {widths}')
    print('')

    ids = delphin_interactions.change_entry_layer_width(simulation_id, layer_material, widths, priority)

    return ids


def layer_material_permutation(original_id, priority):

    print('')
    print("The layer will be identified by the name of the material in the layer.")

    layer_material = input("What is the name of the material? >")
    material_list = input("Input wished layer materials.\n"
                          "If more than 1 material is wished, then the values have to be separated with a comma. >")
    materials = []
    for material in material_list.split(','):
        try:
            materials.append(int(material.strip()))
            print('Material identified by ID')
        except ValueError:
            materials.append(material.strip())
            print('Material identified by Material Name')

    print('')
    print(f'Following values given: {materials}')
    print('')

    ids = delphin_interactions.change_entry_layer_material(original_id, layer_material, materials, priority)

    return ids


def weather_permutation(original_id, priority):
    print('')

    weather_stations = {'years': [], 'stations': []}

    stations = input("Input wished weather stations.\n"
                     "If more than 1 weather station with the same years is wished, "
                     "then the weather station have to be separated with a comma. >")

    for station in stations.split(','):
        weather_stations['stations'].append(station.strip())

    year_list = input(f"Input wished years for the following weather stations: {stations}.\n"
                      f"If more than 1 year is wished, then the years have to be separated with a comma. >")

    year_list = [[int(year.strip())
                  for year in years.strip().split(' ')]
                 for years in year_list.split(',')]

    weather_stations['years'] = year_list

    print('')
    print(f'Following values given: {weather_stations}')
    print('')

    return delphin_interactions.change_entry_weather(original_id, weather_stations, priority)


def wall_permutation(original_id, priority):

    print('')

    orientation_list = input("Input wished orientations.\n"
                             "If more than 1 orientation is wished, "
                             "then the values have to be separated with a comma. >")
    orientation_list = [int(orientation.strip())
                        for orientation in orientation_list.split(',')]

    print('')
    print(f'Following values given: {orientation_list}')
    print('')

    return delphin_interactions.change_entry_orientation(original_id, orientation_list, priority)


def boundary_permutation(original_id, priority):
    # TODO - boundary_permutation

    print('')

    boundary_condition = input("Input wished boundary condition to change.\n")
    coefficient_name = input("Input wished climate coefficient to change.\n")
    coefficient_list = input("Input wished boundary coefficients.\n"
                             "If more than 1 coefficient is wished, "
                             "then the values have to be separated with a comma. >")
    coefficient_list = [float(coefficient.strip())
                        for coefficient in coefficient_list.split(',')]

    print('')
    print(f'Following values given: {coefficient_list}')
    print('')

    return delphin_interactions.change_entry_boundary_coefficient(original_id, boundary_condition, coefficient_name,
                                                                  coefficient_list, priority)


def list_latest_added_simulations():
    documents = delphin_db.Delphin.objects.order_by("added_date")

    for document in documents:
        print(f"ID: {document.id} - Added: {document.added_date} - With priority: {document.queue_priority}")


def add_delphin_material_to_db():

    user_input = input("Please type the path a .m6 file or a folder with multiple files: ")
    id_ = material_interactions.upload_material_file(user_input)
    print(f'\nMaterial was upload with ID: {id_}')


def download_delphin_material():
    # TODO - download_delphin_material
    print('Not implemented')
    return


def download_simulation_result():
    sim_id = str(input('Simulation ID to retrieve? >'))
    if general_interactions.is_simulation_finished(sim_id):
        print('Simulation is ready to download.')
        download_path = str(input('Download Path? >'))
        general_interactions.download_raw_result(sim_id, download_path)
    else:
        print('Simulation is not done yet. Please return later')
        return


def start_simulation():
    answer = input("Have you read and followed the the PDF guideline for installing and setups? (y/n): ")
    if answer == "y":
        simulation_worker()
    else:
        print("Please start by reading and following the PDF guidelines!")
        return
