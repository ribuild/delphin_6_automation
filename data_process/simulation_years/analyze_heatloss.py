__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import stats

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

data_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\simulation_years\data'
hdf_file = os.path.join(data_folder, 'processed_data.h5')

heat_loss = pd.read_hdf(hdf_file, 'heat_loss')


def compute_cdf(array):
    hist, edges = np.histogram(array, density=True, bins=50)
    dx = edges[1] - edges[0]
    cdf = np.cumsum(hist) * dx

    return edges[1:], cdf


year0 = compute_cdf(heat_loss.loc[:, 'Year 0'])
year1 = compute_cdf(heat_loss.loc[:, 'Year 1'])
year2 = compute_cdf(heat_loss.loc[:, 'Year 2'])
year3 = compute_cdf(heat_loss.loc[:, 'Year 3'])
year4 = compute_cdf(heat_loss.loc[:, 'Year 4'])
year5 = compute_cdf(heat_loss.loc[:, 'Year 5'])
year6 = compute_cdf(heat_loss.loc[:, 'Year 6'])

print('\nKS-TEST')
print('Year 6 - Year 0')
print(stats.ks_2samp(year6[1], year0[1]))
print('\nYear 6 - Year 1')
print(stats.ks_2samp(year6[1], year1[1]))
print('\nYear 6 - Year 2')
print(stats.ks_2samp(year6[1], year2[1]))
print('\nYear 6 - Year 3')
print(stats.ks_2samp(year6[1], year3[1]))
print('\nYear 6 - Year 4')
print(stats.ks_2samp(year6[1], year4[1]))
print('\nYear 6 - Year 5')
print(stats.ks_2samp(year6[1], year5[1]))
print('\nYear 6 - Year 6')
print(stats.ks_2samp(year6[1], year6[1]))


print(f'Size of DataFrame: {heat_loss.loc[:, "Year 0"].size}')
print(f'Number of bins: {len(year0[0])}')

plt.figure()
plt.title('Yearly Heat Loss')
plt.plot(year0[0], year0[1], label='Year 0')
plt.plot(year1[0], year1[1], label='Year 1')
plt.plot(year2[0], year2[1], label='Year 2')
plt.plot(year3[0], year3[1], label='Year 3')
plt.plot(year4[0], year4[1], label='Year 4')
plt.plot(year5[0], year5[1], label='Year 5')
plt.plot(year6[0], year6[1], label='Year 6')
plt.xlabel('Cumulated Yearly Heat Loss [Wh]')
plt.ylabel('Ratio [-]')
plt.legend()
plt.show()
