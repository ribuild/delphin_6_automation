__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os

# RiBuild Modules:
import delphin_6_automation.database_interactions.mongo_setup as mongo_setup
import delphin_6_automation.delphin_setup.delphin_permutations as permutations

from delphin_6_automation.database_interactions.auth import dtu_byg
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry as delphin_db
from delphin_6_automation.database_interactions.material_interactions import upload_material_file
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
        print("[b] Add new simulation with permutation to queue")
        print("[l] List simulations")
        print("[m] Add Delphin material to the database")
        print("[g] Add Ribuild Geometry file to database")
        print("[f] Find simulation")
        print("[w] Queue and view weather data")
        print("[s] Start simulation worker")
        print("[x] Exit")
        print()

        choice = input("> ").strip().lower()

        if choice == 'a':
            sim_id, _ = add_to_queue()
            save_ids(sim_id)

        elif choice == 'b':
            id_list = add_permutations_to_queue()
            save_ids(id_list)

        elif choice == 'l':
            list_latest_added_simulations()

        elif choice == 'm':
            add_delphin_material_to_db()

        elif choice == 'g':
            add_geometry_file_to_db()

        elif choice == 'f':
            pass

        elif choice == 'w':
            pass

        elif choice == 's':
            start_simulation()

        elif not choice or choice == 'x':
            print("see ya!")
            break


def add_to_queue():
    delphin_file = str(input("File path for the Delphin file >"))
    priority = str(input("Simulation Priority - high, medium or low >"))
    sim_id = general_interactions.add_to_simulation_queue(delphin_file, priority)
    print('Simulation ID:', sim_id,
          '\n To retrieve the results of a simulation the simulation ID is needed.')

    return sim_id, general_interactions.queue_priorities(priority)


def add_permutations_to_queue():
    print('First upload the original file. Afterwards permutations can be chosen.')

    id_list = []
    original_id, priority = add_to_queue()
    id_list.append(original_id)
    id_list.append(list_permutation_options(original_id, priority))

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

    else:
        ids = ''

    return ids


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
                          "If more than 1 width is wished, then the values have to be separated with a comma. >")
    material_list = [material.strip()
                     for material in material_list.split(',')]

    print('')
    print(f'Following values given: {material_list}')
    print('')

    ids = delphin_interactions.change_entry_layer_material(original_id, layer_material, material_list, priority)

    return ids


def list_latest_added_simulations():
    documents = delphin_db.Delphin.objects.order_by("added_date")

    for document in documents:
        print(f"ID: {document.id} - Added: {document.added_date} - With priority: {document.queue_priority}")


def add_delphin_material_to_db():
    user_input = input("Please type the path a .m6 file or a folder with multiple files: ")
    upload_material_file(user_input)


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
