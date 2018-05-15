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

acronym_file = r'U:\RIBuild\2D_1D\2D to 1D Transformation.xlsx'
out_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\2d_1d\processed_data'
result_folder = r'U:\RIBuild\2D_1D\Results'
graphic_folder = r'U:\RIBuild\2D_1D\Processed Results\4A'
#dp.process_results(acronym_file, result_folder, out_folder)

quantities = ['heat loss', 'temperature', 'relative humidity', 'moisture content', 'moisture integral']
quantity = quantities[1]
hdf_file = out_folder + '/' + quantity + '.h5'


# Open HDF
total_uninsulated_4a = pd.read_hdf(hdf_file, 'total_4a_36_uninsulated')
total_insulated_4a = pd.read_hdf(hdf_file, 'total_4a_36_insulated')


def uninsulated(save=False):

    dp.abs_diff_boxplot(total_uninsulated_4a, (-2, 2), quantity.title(), '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_abs_diff_uninsulated.png')

    dp.rel_diff_boxplot(total_uninsulated_4a, (0, 250), quantity.title(), '4A 36cm Uninsulated', log=False)
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_rel_diff_uninsulated.png')

    dp.plot_linear_relation(total_uninsulated_4a, 'mortar', (-50, 200), quantity.title(), '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_linear_relation_mortar_uninsulated.png')

    dp.plot_linear_relation(total_uninsulated_4a, 'brick', (-50, 200), quantity.title(), '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_linear_relation_brick_uninsulated.png')


#uninsulated(False)


def insulated(save=False):

    dp.abs_diff_boxplot(total_insulated_4a, (-5, 5), quantity.title(), '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_abs_diff_insulated.png')

    dp.rel_diff_boxplot(total_insulated_4a, (0.1, 120), quantity.title(), '4A 36cm Insulated', log=False)
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_rel_diff_insulated.png')

    dp.plot_linear_relation(total_insulated_4a, 'mortar', (0, 5), quantity.title(), '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_linear_relation_mortar_insulated.png')

    dp.plot_linear_relation(total_insulated_4a, 'brick', (0, 5), quantity.title(), '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_linear_relation_brick_insulated.png')


#insulated(True)


def time_plots():
    insulation = 'insulated'
    acros = [f'dresden_zp_high_cement_{insulation}_36_4a', f'dresden_zd_high_cement_{insulation}_36_4a',
             f'potsdam_high_cement_{insulation}_36_4a', f'dresden_zp_low_cement_{insulation}_36_4a',
             f'dresden_zd_low_cement_{insulation}_36_4a', f'potsdam_low_cement_{insulation}_36_4a']

    for acro in acros:
        acro_data_frame = pd.read_hdf(hdf_file, acro)

        for i in range(5):
            acro_data_frame.loc[:, pd.IndexSlice[str(i), :, 'out']].cumsum().plot()
            plt.title(f'{acro}\n{quantity}')

time_plots()

plt.show()
