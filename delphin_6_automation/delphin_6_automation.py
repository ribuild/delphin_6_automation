import nosql.mongo_setup as mongo_setup
import nosql.simulation as sim_db


def main():
    print_header()
    config_mongo()
    add_to_queue()


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


#def user_loop():
#    #while True:
    #    print("add something...")


def add_to_queue():
    country = "Denmark" # str(input("country? (string)"))
    start_year = 2000 # int(input("what is something? (int)"))

    queue_db = sim_db.Simulation()
    queue_db.country = country
    queue_db.start_year = start_year

    queue_db.save()





if __name__ == "__main__":
    main()

