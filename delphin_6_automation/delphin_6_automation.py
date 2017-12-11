"""
Backend user interface
- Add new simulation(s)
- Monitor the simulation process
- Queue and watch finished simulations
"""

import delphin_6_automation.nosql.mongo_setup as mongo_setup
import delphin_6_automation.nosql.simulation as simulation


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
    mongo_setup.global_init()


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
    sim_id = simulation.add_to_queue(delphin_file, priority)
    simulation.start_simulation(sim_id)
    print('Simulation ID:', sim_id,
          '\n To retrieve the results of a simulation the simulation ID is needed.')

    save = str(input('Save Simulation ID to text file? (y/n)'))
    if save == 'y':
        print('Simulation will be saved on the Desktop as simulation_id.txt ')
        # save txt file
    else:
        print('Simulation ID was not saved.')
        return


def list_latest_added_simulations():
    documents = simulation.simulation_db.objects.order_by("date_added")

    for document in documents:
        print("Added: {} - Simulation from {} starting {}".format(
            document.date_added,
            document.country,
            document.start_year))


def download_simulation_result():
    sim_id = str(input('Simulation ID to retrieve? >'))
    if simulation.is_simulation_finished(sim_id):
        print('Simulation is ready to download.')
        download_path = str(input('Download Path? >'))
        simulation.download_simulation_result(sim_id, download_path)
    else:
        print('Simulation is not done yet. Please return later')
        return


def exit_app():
    print()
    print('Bye')
    raise KeyboardInterrupt()


if __name__ == "__main__":
    main()
