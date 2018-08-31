__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import numpy as np
import bson
import matplotlib.pyplot as plt

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions import auth
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


data_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\simtime_prediction\data'


mongo_setup.global_init(auth.auth_dict)

entries = delphin_entry.Delphin.objects(simulation_time__exists=True)

mould = []
rot = []
mould_avg = []
rot_avg = []
#interior = []
moisture = []
moisture_avg = []
time = []

for i in range(len(entries)):
    entry = entries[i]
    time.append(entry.simulation_time / 60)

    result_dict: dict = bson.BSON.decode(entry.results_raw.results.read())

    rh_mould = np.array(result_dict['relative humidity mould']['result'])
    mould.append(len(rh_mould[rh_mould > 90.0]) / len(rh_mould))
    mould_avg.append(np.mean(rh_mould))

    rh_rot = np.array(result_dict['relative humidity wood rot']['result'])
    rot.append(len(rh_rot[rh_rot > 90.0]) / len(rh_rot))
    rot_avg.append(np.mean(rh_rot))

    moist = np.array(result_dict['moisture content frost']['result'])
    moisture.append(len(moist[moist > 90.0]) / len(moist))
    moisture_avg.append(np.mean(moist))


plt.figure()
plt.title('Hours over 90% Relative Humidity')
plt.scatter(time, mould, label='Mould')
plt.scatter(time, rot, label='Rot')
#plt.scatter(time, moisture, label='Moisture Content')
#plt.scatter(time, interior, label='Int Surface')
plt.xlabel('Time in minutes')
plt.ylabel('Share of totals hours, where RH is over 90%')
plt.ylim(-0.05, 1.05)
plt.legend()

plt.figure()
plt.title('Average Relative Humidity')
plt.scatter(time, mould_avg, label='Mould')
plt.scatter(time, rot_avg, label='Rot')
#plt.scatter(time, interior, label='Int Surface')
plt.xlabel('Time in minutes')
plt.ylabel('Relative Humidity - %')
plt.ylim(45, 110)
plt.legend()

plt.figure()
plt.title('Average Moisture Content')
plt.scatter(time, moisture_avg, label='Moisture Content', color='green')
plt.xlabel('Time in minutes')
plt.ylabel('Moisture Content - kg/m3')
plt.ylim(50, 160)
plt.legend()

plt.show()
