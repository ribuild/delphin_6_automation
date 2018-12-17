__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import matplotlib.pyplot as plt
import numpy as np

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_2d_1d as auth_dict
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.backend import result_extraction

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)

filters_none = {}
filters = {'exterior_climate': 'MuenchenAirp',}
filters2 = {'exterior_climate': 'MuenchenAirp', 'wall_orientation': [200, 250]}
filters3 = {'exterior_climate': 'MuenchenAirp', 'wall_orientation': [200, 250], 'wall_core_thickness': 48}
filters4 = {'exterior_climate': 'MuenchenAirp', 'wall_orientation': [200, 250], 'system_name': 'Calsitherm'}
filters5 = {'exterior_climate': 'MuenchenAirp', 'rain_scale_factor': [0.0, 0.15]}
projects = result_extraction.filter_db(filters_none)


def lookup(projects_):
    ori = []
    rain = []
    for p in projects_:
        ori.append(p.sample_data['wall_orientation'])
        rain.append(p.sample_data['rain_scale_factor'])

    ori = set(ori)
    rain = set(rain)
    print(f'Orientations: {ori}')
    print(f'Rain: {rain}')


lookup(projects)
x, y = result_extraction.compute_cdf(projects, 'mould')
a = np.nonzero(x < 2.0)
print(y[a][-1])
plt.figure()
plt.plot(x, y)
plt.show()

mongo_setup.global_end_ssh(server)
