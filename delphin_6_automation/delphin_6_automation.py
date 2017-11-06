import nosql.mongo_setup as mongo_setup
import nosql.simulation as sim_db



def main():
    print_header()
    config_mongo()
    user_loop()


def print_header():
    print('---------------------------------------------------')
    print('|                                                  |')
    print('|           RiBuild EU Research Project            |')
    print('|           for Hygrothermal Simulations           |')
    print('|              (WIP) Test Environment              |')
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
        elif choice == 'l':
            list_latest_added_simulations()
        elif not ch or ch == 'x':
            print("see ya!")
            break


def add_to_queue():
    country = str(input("country? >"))
    start_year = int(input("year? >")) # int(input("what is something? (int)"))

    sim = sim_db.Simulation()
    sim.country = country
    sim.start_year = start_year
    sim.save()


def list_latest_added_simulations():
    sim = sim_db.Simulation()
    documents = sim_db.Simulation.objects.order_by(
        "country",
        "date_added",
        "start_year"
        )

    for document in documents[:9]:
        print("Added: {} - Simulation from {} starting {}".format(
            sim.date_added.date(),
            sim.country,
            sim.start_year))


if __name__ == "__main__":
    main()
