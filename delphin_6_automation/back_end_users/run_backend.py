"""
Backend user interface:
- Add new simulation(s)
- Monitor the simulation process
- Queue and watch finished simulations
"""

import delphin_6_automation.nosql.mongo_setup as mongo_setup
import delphin_6_automation.database_interactions as db_interact
from delphin_6_automation.nosql.db_templates import delphin_entry as delphin_db
from delphin_6_automation.nosql.auth import dtu_byg
import os


def main():
    print_header()
    config_mongo()
    user_loop()


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


def user_loop():
    while True:
        print()
        print("Available actions:")
        print("* [a]dd new simulation to queue")
        print("* [l]ist simulations")
        #print("* [f]ind simulation")
        #print("* [f]ind results")
        print("* e[x]it")
        print()
        choice = input("> ").strip().lower()
        if choice == 'a':
            add_to_queue()
        elif choice == 'l':
            list_latest_added_simulations()
        elif not choice or choice == 'x':
            print("see ya!")
            break


def show_commands(command):
    if command == 'start_up':
        print()
        print("Available actions:")
        print("* [a]dd new simulation to queue")
        print("* [l]ist simulations")
        # print("* [f]ind simulation")
        # print("* [f]ind results")
        print("* e[x]it")
        print()


def add_to_queue():
    delphin_file = str(input("File path for the Delphin file >"))
    priority = str(input("Simulation Priority - high, medium or low >"))
    sim_id = db_interact.general_interactions.add_to_simulation_queue(delphin_file, priority)
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


def download_simulation_result():
    sim_id = str(input('Simulation ID to retrieve? >'))
    if db_interact.general_interactions.is_simulation_finished(sim_id):
        print('Simulation is ready to download.')
        download_path = str(input('Download Path? >'))
        db_interact.general_interactions.download_raw_result(sim_id, download_path)
    else:
        print('Simulation is not done yet. Please return later')
        return


def exit_app():
    print()
    print('Bye')
    raise KeyboardInterrupt()


#if __name__ == "__main__":
#    main()
print(42)
