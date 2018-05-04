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

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

acronym_file = r'U:\RIBuild\2D_1D\2D to 1D Transformation_tmp.xlsx'
out_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\2d_1d\processed_data'
result_folder = r'U:\RIBuild\2D_1D\Results'
# dp.process_results(acronym_file, result_folder, out_folder)

hdf_file = out_folder + '/moisture content.h5'

# Open HDF
# Uninsulated
dresdenzp_high_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zp_high_cement_uninsulated_36_4a')
dresdenzd_high_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zd_high_cement_uninsulated_36_4a')
postdam_high_uninsulated_4a = pd.read_hdf(hdf_file, 'potsdam_high_cement_uninsulated_36_4a')
dresdenzp_low_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zp_low_cement_uninsulated_36_4a')
dresdenzd_low_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zd_low_cement_uninsulated_36_4a')
postdam_low_uninsulated_4a = pd.read_hdf(hdf_file, 'potsdam_low_cement_uninsulated_36_4a')

total_uninsulated_4a = pd.concat([dresdenzp_high_uninsulated_4a, dresdenzd_high_uninsulated_4a,
                                  postdam_high_uninsulated_4a, dresdenzp_low_uninsulated_4a,
                                  dresdenzd_low_uninsulated_4a, postdam_low_uninsulated_4a])


#dp.plot_linear_relation(total_uninsulated_4a, 'mortar', (0, 225))
dp.abs_diff_boxplot(total_uninsulated_4a, (-50, 50))


plt.show()
