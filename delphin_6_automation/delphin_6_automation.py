"""
import nosql.mongo_setup as mongo_setup

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
    mongo_setup.global_init()"shell_cmd": "C:\\Users\\thper\\Google_Drive\\DTU\\delphin_automation\\delphin_6_automation\\venv\\Scripts\\python.exe"


def user_loop():
    while True:
        print("add something...")



if __name__ == "__main__":
    main()

"""
import mongoengine
print(43)
