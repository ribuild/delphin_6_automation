__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import data_process_functions as dp
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import linregress
import statsmodels

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

acronym_file = r'U:\RIBuild\2D_1D\2D to 1D Transformation.xlsx'
out_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\2d_1d\processed_data'
result_folder = r'U:\RIBuild\2D_1D\Results'
graphic_folder = r'U:\RIBuild\2D_1D\Processed Results\4A'
#dp.process_results(acronym_file, result_folder, out_folder)

quantities = ['heat loss', 'temperature', 'relative humidity', 'moisture content', 'moisture integral']
quantity = quantities[2]
hdf_file = out_folder + '/' + quantity + '.h5'


# Open HDF
#total_uninsulated_4a = pd.read_hdf(hdf_file, 'total_4a_36_uninsulated')
#total_insulated_4a = pd.read_hdf(hdf_file, 'total_4a_36_insulated')

insulation = 'insulated'
acros = [f'dresden_zp_high_cement_{insulation}_36_4a', f'dresden_zd_high_cement_{insulation}_36_4a',
         f'potsdam_high_cement_{insulation}_36_4a', f'dresden_zp_low_cement_{insulation}_36_4a',
         f'dresden_zd_low_cement_{insulation}_36_4a', f'potsdam_low_cement_{insulation}_36_4a']

acro_data_frame = pd.read_hdf(hdf_file, acros[1])

for i in range(7):
    test_data = acro_data_frame.loc[:, pd.IndexSlice[str(i), :, 'out']].rolling(24*7).mean()
    test_data.plot()

#granger_test_brick = statsmodels.grangercausalitytests(test_data)
plt.show()
