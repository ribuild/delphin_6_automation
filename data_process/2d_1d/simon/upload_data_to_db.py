__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_2d_1d as auth_dict
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import sampling_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)


def upload_materials(folder):
    for file in os.listdir(folder):
        material_interactions.upload_material_file(os.path.join(folder, file))


def upload_weather(folder):
    for file in os.listdir(folder):
        print(file)
        weather_interactions.upload_weather_to_db(os.path.join(folder, file))


def upload_strategy(folder):
    strategy = os.path.join(folder, 'sampling_strategy.json')
    sampling_interactions.upload_sampling_strategy(strategy)


# upload_weather(r'C:\Users\ocni\Desktop\1D-2D\weather')
# upload_materials(r'C:\Program Files\IBK\Delphin 6.0\resources\DB_materials')
upload_strategy(r'C:\Users\ocni\Desktop\1D-2D\sampling_strategy')

mongo_setup.global_end_ssh(server)
