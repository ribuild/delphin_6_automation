__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas

# RiBuild Modules
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


data_folder = os.path.join(os.path.dirname(__file__), 'data')

rot = []
rot_avg = []
mould = []
mould_avg = []
moisture = []
moisture_avg = []

for folder in os.listdir(data_folder):
    results_folder = os.path.join(data_folder, folder, folder, 'results')
    mould_data = np.array(delphin_parser.d6o_to_dict(results_folder, 'relative humidity mould.d6o')[0])
    mould.append(len(mould_data[mould_data > 90.0])/len(mould_data))
    mould_avg.append(np.mean(mould_data))

    rot_data = np.array(delphin_parser.d6o_to_dict(results_folder, 'relative humidity wood rot.d6o')[0])
    rot.append(len(rot_data[rot_data > 90.0]) / len(rot_data))
    rot_avg.append(np.mean(rot_data))

    moist = np.array(delphin_parser.d6o_to_dict(results_folder, 'moisture content frost.d6o')[0])
    moisture.append(len(moist[moist > 90.0]) / len(moist))
    moisture_avg.append(np.mean(moist))


x = np.arange(len(mould))
plt.figure('Hours over 90%')
plt.scatter(x, mould, label='Mould')
plt.scatter(x, rot, label='Rot')
plt.scatter(x, moisture, label='Moisture Content')
plt.ylim(-0.1, 1.1)
plt.legend()

plt.figure('Average')
plt.scatter(x, mould_avg, label='Mould')
plt.scatter(x, rot_avg, label='Rot')
plt.ylim(45, 110)
plt.legend()

plt.figure('Average Moisture')
plt.scatter(x, moisture_avg, label='Moisture Content', color='green')
plt.legend()
plt.ylim(50, 160)
plt.show()
