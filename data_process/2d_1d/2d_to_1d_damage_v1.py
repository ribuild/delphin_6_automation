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

#dp.compute_damage_models(acronym_file, out_folder)
quantity = 'damage'
hdf_file = out_folder + '/' + quantity + '.h5'


# Open HDF
total_uninsulated_4a = pd.read_hdf(hdf_file, 'total_4a_36_uninsulated')
total_insulated_4a = pd.read_hdf(hdf_file, 'total_4a_36_insulated')


def uninsulated(save=False, plot=True):

    summary = total_uninsulated_4a.loc[:, pd.IndexSlice['2':, :, ('abs_diff')]].describe()
    print(summary)
    if save:
        writer = pd.ExcelWriter(f'{graphic_folder}/damage_summary_uninsulated.xlsx')
        summary.to_excel(writer, 'Summary Statistics')
        writer.save()

    # Wood Rot
    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['2':'3', :, 'out']], 'mortar',
                                   (-5, 50), 'Wood Rot', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_linear_relation_mortar_uninsulated.png')

    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['2':'3', :, 'out']], 'brick',
                                   (-5, 50), 'Wood Rot', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_linear_relation_brick_uninsulated.png')

    # Mould Index
    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['4':'5', :, 'out']], 'mortar',
                                   (-1, 7), 'Mould Index', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_linear_relation_mortar_uninsulated.png')

    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['4':'5', :, 'out']], 'brick',
                                   (-1, 7), 'Mould Index', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_linear_relation_brick_uninsulated.png')

    # Heat Loss
    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['surface', :, 'out']], 'mortar',
                                   (-10000, 800000), 'Heat Loss', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/heat_loss_linear_relation_mortar_uninsulated.png')

    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['surface', :, 'out']], 'brick',
                                   (-10000, 800000), 'Heat Loss', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/heat_loss_linear_relation_brick_uninsulated.png')

    if not plot:
        plt.close('all')

#uninsulated(True, False)


def insulated(save=False, plot=True):

    summary = total_insulated_4a.loc[:, pd.IndexSlice['2':, :, ('abs_diff', 'rel_diff')]].describe()
    print(summary)
    if save:
        writer = pd.ExcelWriter(f'{graphic_folder}/damage_summary_insulated.xlsx')
        summary.to_excel(writer, 'Summary Statistics')
        writer.save()

    # Wood Rot
    dp.plot_linear_relation_damage(total_insulated_4a.loc[:, pd.IndexSlice['2':'3', :, 'out']], 'mortar',
                                   (-5, 105), 'Wood Rot', '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_linear_relation_mortar_insulated.png')

    dp.plot_linear_relation_damage(total_insulated_4a.loc[:, pd.IndexSlice['2':'3', :, 'out']], 'brick',
                                   (-5, 105), 'Wood Rot', '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_linear_relation_brick_insulated.png')

    dp.abs_diff_boxplot(total_insulated_4a.loc[:, pd.IndexSlice['2':'3', :, :]], (-30, 105), 'Wood Rot', '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_abs_diff_insulated.png')

    dp.rel_diff_boxplot(total_insulated_4a.loc[:, pd.IndexSlice['2':'3', :, :]], (-5, 200), 'Wood Rot', '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_rel_diff_insulated.png')

    # Mould Index
    dp.plot_linear_relation_damage(total_insulated_4a.loc[:, pd.IndexSlice['4':'5', :, 'out']], 'mortar',
                                   (-1, 7), 'Mould Index', '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_linear_relation_mortar_insulated.png')

    dp.plot_linear_relation_damage(total_insulated_4a.loc[:, pd.IndexSlice['4':'5', :, 'out']], 'brick',
                                   (-1, 7), 'Mould Index', '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_linear_relation_brick_insulated.png')

    dp.abs_diff_boxplot(total_insulated_4a.loc[:, pd.IndexSlice['4':'6', :, :]], (-2, 10), 'Mould Index',
                        '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_abs_diff_insulated.png')

    dp.rel_diff_boxplot(total_insulated_4a.loc[:, pd.IndexSlice['4':'6', :, :]], (-2, 105), 'Mould Index',
                        '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_rel_diff_insulated.png')

    # Heat Loss
    dp.plot_linear_relation_damage(total_insulated_4a.loc[:, pd.IndexSlice['surface', :, 'out']], 'mortar',
                                   (-10000, 310000), 'Heat Loss', '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/heat_loss_linear_relation_mortar_insulated.png')

    dp.plot_linear_relation_damage(total_insulated_4a.loc[:, pd.IndexSlice['surface', :, 'out']], 'brick',
                                   (-10000, 310000), 'Heat Loss', '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/heat_loss_linear_relation_brick_insulated.png')

    dp.abs_diff_boxplot(total_insulated_4a.loc[:, pd.IndexSlice['surface', :, :]], (-1000, 90000), 'Heat Loss',
                        '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/heat_loss_abs_diff_insulated.png')

    dp.rel_diff_boxplot(total_insulated_4a.loc[:, pd.IndexSlice['surface', :, :]], (-2, 60), 'Heat Loss',
                        '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/heat_loss_rel_diff_insulated.png')

    if not plot:
        plt.close('all')


insulated(True, False)

plt.show()
