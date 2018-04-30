__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import matplotlib.pyplot as plt

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

out_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\2d_1d\processed_data'
hdf_file = out_folder + '/relative_moisture_content.h5'
dresdenzp_highratio_4a = pd.read_hdf(hdf_file, 'dresdenzp_highratio_4a')
dresdenzd_highratio_4a = pd.read_hdf(hdf_file, 'dresdenzd_highratio_4a')
postdam_highratio_4a = pd.read_hdf(hdf_file, 'postdam_highratio_4a')


def plots():
    plt.figure()
    dresdenzp_highratio_4a.boxplot()
    plt.ylim(-25, 2500)
    plt.title('Weighted Relative Difference between 1D and 2D\n'
              'Moisture Content\n'
              'Brick: Dresden ZP - Mortar: High Cement Ratio')
    plt.tight_layout()
    plt.figure()
    dresdenzd_highratio_4a.boxplot()
    plt.ylim(-25, 2500)
    plt.title('Weighted Relative Difference between 1D and 2D\n'
              'Moisture Content\n'
              'Brick: Dresden ZD - Mortar: High Cement Ratio')
    plt.tight_layout()
    plt.figure()
    postdam_highratio_4a.boxplot()
    plt.ylim(-25, 2500)
    plt.title('Weighted Relative Difference between 1D and 2D\n'
              'Moisture Content\n'
              'Brick: Potsdam - Mortar: High Cement Ratio')
    plt.tight_layout()
    plt.show()


#plots()

#print(dresdenzd_highratio_4a.std())
out_2std_zd = dresdenzd_highratio_4a[dresdenzd_highratio_4a > 2*dresdenzd_highratio_4a.std()]
out_2std_zp = dresdenzp_highratio_4a[dresdenzp_highratio_4a > 2*dresdenzp_highratio_4a.std()]
out_2std_pd = postdam_highratio_4a[postdam_highratio_4a > 2*postdam_highratio_4a.std()]

print('out_2std_zd')
print(out_2std_zd.notnull().sum()/out_2std_zd.shape[0])
print('')
print('out_2std_zp')
print(out_2std_zp.notnull().sum()/out_2std_zp.shape[0])
print('')
print('out_2std_pd')
print(out_2std_pd.notnull().sum()/out_2std_pd.shape[0])
