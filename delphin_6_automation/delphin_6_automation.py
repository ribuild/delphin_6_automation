"""
Backend user interface
- Add new simulation(s)
- Monitor the simulation process
- Queue and watch finished simulations
"""

import nosql.mongo_setup as mongo_setup
from nosql.simulation import Simulation

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


def add_to_queue():
    country = str(input("country? >"))
    start_year = int(input("year? >")) # int(input("what is something? (int)"))
    sim = Simulation()
    sim.country = country
    sim.start_year = start_year
    sim.save()


def list_latest_added_simulations():
    #sim = Simulation()
    #sim = Simulation.objects().order_by("-date_added")
    documents = Simulation.objects.order_by("date_added")

    for document in documents:
        print("Added: {} - Simulation from {} starting {}".format(
            document.date_added,
            document.country,
            document.start_year))


if __name__ == "__main__":
    main()
