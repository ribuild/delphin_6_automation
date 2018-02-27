"""
Backend user interface:
- Add new simulation(s)
- Monitor the simulation process
- Queue and watch finished simulations
"""

import os

from delphin_6_automation.database_interactions.auth import dtu_byg

import delphin_6_automation.database_interactions.mongo_setup as mongo_setup
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry as delphin_db
from delphin_6_automation.database_interactions.material_interactions import upload_material_file
from delphin_6_automation.simulation_worker import simulation_worker

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
            add_to_queue()

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

    save = str(input('Save Simulation ID to text file? (y/n)'))
    if save == 'y':
        print('Simulation will be saved on the Desktop as simulation_id.txt ')
        user_desktop = os.path.join(os.environ["HOMEPATH"], "Desktop")
        id_file = open(user_desktop + '/simulation_id.txt', 'w')
        id_file.write(str(sim_id))
        id_file.close()

    else:
        print('Simulation ID was not saved.')
        return


def list_latest_added_simulations():
    documents = delphin_db.Delphin.objects.order_by("added_date")

    for document in documents:
        print("ID: {} - Added: {} - With priority: {}".format(
            document.id,
            document.added_date,
            document.queue_priority))


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


if __name__ == "__main__":

   config_mongo()
   main()
   #start_simulation()
