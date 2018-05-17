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
quantity = quantities[1]
hdf_file = out_folder + '/' + quantity + '.h5'

data = pd.read_hdf(hdf_file)


for location in data.columns.levels[0]:
    data_local = data.loc[:, pd.IndexSlice[location, :]]
    data_local.columns = data_local.columns.droplevel(level=0)

    #data_local = data_local.cumsum()
    data_local = data_local.rolling(24).mean()
    #data_local = data_local.diff()

    data_local.plot()
    plt.title(f"Location: {location}\nRolling Mean\n{quantity.capitalize()}")

    proc_data = pd.DataFrame(np.array([data_local.quantile(.25, axis=1), data_local.quantile(.75, axis=1), data_local.quantile(.50, axis=1)]).T,
                             columns=['q25', 'q75', 'q50'])
    proc_data.index = pd.DatetimeIndex(start=datetime.datetime(2020, 1, 1), freq='h', periods=data_local.shape[0])

    proc_data.plot()
    plt.title(f"Location: {location}\nMin-Mean-Max\n{quantity.capitalize()}")

    range_ = (proc_data['q75'] - proc_data['q25'])
    #range_.plot()
    normalized_data = pd.DataFrame()
    normalized_data['IQR'] = range_
    normalized_data.plot()
    plt.title(f"Location: {location}\nRelative Difference\n{quantity.capitalize()}")

plt.show()
