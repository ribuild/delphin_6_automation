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

mould_interface = pd.read_hdf(hdf_file, 'mould_interior')


def compute_cdf(array):
    hist, edges = np.histogram(array, density=True, bins=50)
    dx = edges[1] - edges[0]
    cdf = np.cumsum(hist) * dx

    return edges[1:], cdf


year0 = mould_interface.loc[:, 'Year 0']
year1 = mould_interface.loc[:, ['Year 0', 'Year 1']].max(axis=1)
year2 = mould_interface.loc[:, ['Year 0', 'Year 1', 'Year 2']].max(axis=1)
year3 = mould_interface.loc[:, ['Year 0', 'Year 1', 'Year 2', 'Year 3']].max(axis=1)
year4 = mould_interface.loc[:, ['Year 0', 'Year 1', 'Year 2', 'Year 3', 'Year 4']].max(axis=1)
year5 = mould_interface.loc[:, ['Year 0', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']].max(axis=1)
year6 = mould_interface.max(axis=1)

year0_cfd = compute_cdf(year0)
year1_cfd = compute_cdf(year1)
year2_cfd = compute_cdf(year2)
year3_cfd = compute_cdf(year3)
year4_cfd = compute_cdf(year4)
year5_cfd = compute_cdf(year5)
year6_cfd = compute_cdf(year6)

print('\nKS-TEST')
print('Year 6 - Year 0')
print(stats.ks_2samp(year6_cfd[1], year0_cfd[1]))
print('\nYear 6 - Year 1')
print(stats.ks_2samp(year6_cfd[1], year1_cfd[1]))
print('\nYear 6 - Year 2')
print(stats.ks_2samp(year6_cfd[1], year2_cfd[1]))
print('\nYear 6 - Year 3')
print(stats.ks_2samp(year6_cfd[1], year3_cfd[1]))
print('\nYear 6 - Year 4')
print(stats.ks_2samp(year6_cfd[1], year4_cfd[1]))
print('\nYear 6 - Year 5')
print(stats.ks_2samp(year6_cfd[1], year5_cfd[1]))
print('\nYear 6 - Year 6')
print(stats.ks_2samp(year6_cfd[1], year6_cfd[1]))


print(f'\nSize of DataFrame: {mould_interface.loc[:, "Year 0"].size}')
print(f'Number of bins: {len(year0_cfd[0])}')

plt.figure()
plt.title('Mould at Interior')
plt.plot(year0_cfd[0], year0_cfd[1], label='Year 0')
plt.plot(year1_cfd[0], year1_cfd[1], label='Year 1')
plt.plot(year2_cfd[0], year2_cfd[1], label='Year 2')
plt.plot(year3_cfd[0], year3_cfd[1], label='Year 3')
plt.plot(year4_cfd[0], year4_cfd[1], label='Year 4')
plt.plot(year5_cfd[0], year5_cfd[1], label='Year 5')
plt.plot(year6_cfd[0], year6_cfd[1], label='Year 6')
plt.xlabel('Mould Index [-]')
plt.ylabel('Ratio [-]')
plt.legend()
plt.show()
