__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import pandas as pd
import matplotlib.pyplot as plt

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

data_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\simtime_prediction\data'
excel_file = os.path.join(data_folder, 'sim_time.xlsx')

data = pd.read_excel(excel_file)


(df['time'][df['time'] < 1500 * 60] / 60).plot('hist', bins=50)
plt.show()