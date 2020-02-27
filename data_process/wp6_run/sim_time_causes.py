__author__ = "Christian Kongsgaard"
__license__ = 'MIT'


# Modules
import matplotlib.pyplot as plt
import numpy as np

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import delphin_entry

server = mongo_setup.global_init(auth_dict)

filtered_entries = delphin_entry.Delphin.objects(simulated__exists=True).only('simulation_time', 'sample_data')
print('got entries')

entries = [(entry.simulation_time/60, entry.sample_data['rain_scale_factor']) for entry in filtered_entries]
time, rain = zip(*entries)

mongo_setup.global_end_ssh(server)

plt.figure()

plt.scatter(time, rain)
plt.show()
