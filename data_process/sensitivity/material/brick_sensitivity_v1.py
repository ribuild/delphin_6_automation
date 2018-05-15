__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime

# RiBuild Modules
from data_process.sensitivity import data_process_functions as dp

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

excel_file = r'U:\RIBuild\Material_Sensitivity\simulation table_no_hydrophobation.xlsx'
result_folder = r'U:\RIBuild\Material_Sensitivity\Results'
out_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\sensitivity\material\processed_data'
#dp.process_results(excel_file, result_folder, out_folder)

quantities = ['heat loss', 'temperature', 'relative humidity', 'moisture content', 'moisture integral']
quantity = quantities[4]
hdf_file = out_folder + '/' + quantity + '.h5'

data = pd.read_hdf(hdf_file)

data.columns = data.columns.droplevel(level=0)

#plt.figure()
data.cumsum().plot()

proc_data = pd.DataFrame(np.array([data.min(axis=1), data.max(axis=1), data.mean(axis=1)]).T, columns=['min', 'max', 'mean'])
proc_data.index = pd.DatetimeIndex(start=datetime.datetime(2020, 1, 1),
                            freq='h', periods=data.shape[0])
print(proc_data.head())

proc_data.plot()

plt.figure()
(proc_data['max'] - proc_data['min']).plot()
plt.show()
