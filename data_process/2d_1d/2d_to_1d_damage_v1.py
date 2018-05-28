__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import data_process_functions as dp
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import datetime
import matplotlib.dates as mdates

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

acronym_file = r'U:\RIBuild\2D_1D\4A_36_Acronyms.xlsx'
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
                                   (-5, 105), 'Wood Rot', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_linear_relation_mortar_uninsulated.png')

    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['2':'3', :, 'out']], 'brick',
                                   (-5, 105), 'Wood Rot', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_linear_relation_brick_uninsulated.png')

    """
    dp.abs_diff_boxplot(total_uninsulated_4a.loc[:, pd.IndexSlice['2':'3', :, :]], (-60, 60), 'Wood Rot', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_abs_diff_uninsulated.png')

    dp.rel_diff_boxplot(total_uninsulated_4a.loc[:, pd.IndexSlice['2':'3', :, :]], (0.01, 400), 'Wood Rot', '4A 36cm Uninsulated', log=True)
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_rel_diff_uninsulated.png')
    """

    # Mould Index
    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['4':'5', :, 'out']], 'mortar',
                                   (-1, 7), 'Mould Index', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_linear_relation_mortar_uninsulated.png')

    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['4':'5', :, 'out']], 'brick',
                                   (-1, 7), 'Mould Index', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_linear_relation_brick_uninsulated.png')

    """
    dp.abs_diff_boxplot(total_uninsulated_4a.loc[:, pd.IndexSlice['4':'6', :, :]], (-2, 4), 'Mould Index',
                        '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_abs_diff_uninsulated.png')

    dp.rel_diff_boxplot(total_uninsulated_4a.loc[:, pd.IndexSlice['4':'5', :, :]], (0.01, 400), 'Mould Index',
                        '4A 36cm Uninsulated', log=True)
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_rel_diff_uninsulated.png')
    """
    """
    # Heat Loss
    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['surface', :, 'out']], 'mortar',
                                   (-10000, 800000), 'Heat Loss', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/heat_loss_linear_relation_mortar_uninsulated.png')

    dp.plot_linear_relation_damage(total_uninsulated_4a.loc[:, pd.IndexSlice['surface', :, 'out']], 'brick',
                                   (-10000, 800000), 'Heat Loss', '4A 36cm Uninsulated')
    if save:
        plt.savefig(f'{graphic_folder}/heat_loss_linear_relation_brick_uninsulated.png')
    """

    if not plot:
        plt.close('all')

#uninsulated(True, False)


def insulated(save=False, plot=True):

    summary = total_insulated_4a.loc[:, pd.IndexSlice['2':, :, ('abs_diff', 'rel_diff')]].describe()
    #print(summary)
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

    dp.abs_diff_boxplot(total_insulated_4a.loc[:, pd.IndexSlice['2':'3', :, :]], (-60, 60), 'Wood Rot', '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/wood_rot_abs_diff_insulated.png')

    dp.rel_diff_boxplot(total_insulated_4a.loc[:, pd.IndexSlice['2':'3', :, :]], (0.01, 400), 'Wood Rot', '4A 36cm Insulated', log=True)
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

    dp.abs_diff_boxplot(total_insulated_4a.loc[:, pd.IndexSlice['4':'6', :, :]], (-2, 4), 'Mould Index',
                        '4A 36cm Insulated')
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_abs_diff_insulated.png')

    dp.rel_diff_boxplot(total_insulated_4a.loc[:, pd.IndexSlice['4':'5', :, :]], (0.01, 400), 'Mould Index',
                        '4A 36cm Insulated', log=True)
    if save:
        plt.savefig(f'{graphic_folder}/mould_index_rel_diff_insulated.png')

    """
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
    """

    if not plot:
        plt.close('all')


#insulated(False, True)


def time_plots(save=False):
    insulation = 'insulated'
    acros = [f'dresden_zp_high_cement_{insulation}_36_4a', f'potsdam_low_cement_{insulation}_36_4a']

    time_frame = pd.DataFrame()

    for acro in acros:
        if 'dresden' in acro:
            brick_name = 'Brick: Dresden ZP, Mortar: High Cement Ratio'
        else:
            brick_name = 'Brick: Potsdam, Mortar: Low Cement Ratio'

        acro_data_frame = pd.read_hdf(hdf_file, acro)

        time_frame = acro_data_frame.loc[:, pd.IndexSlice[('4', '5'), :, 'out']]

        indices = pd.DataFrame(columns=['2d', 'brick', 'mortar'])
        indices['2d'] = np.arange(1, len(time_frame)+1)
        indices['brick'] = np.arange(1, len(time_frame)+1)
        indices['mortar'] = np.arange(1, len(time_frame)+1)
        indices.index = pd.DatetimeIndex(start=datetime.datetime(2020, 1, 1),
                                         freq='h', periods=len(indices))

        #running_mean = time_frame.loc[:, pd.IndexSlice[:, :, 'out']].cumsum().divide(indices, level=1)
        running_mean = time_frame.loc[:, pd.IndexSlice[:, :, 'out']]

        fig, axes = plt.subplots(ncols=2, nrows=1, sharex=True, sharey=True, figsize=(16, 8), )
        fig.suptitle(f'{brick_name} - {insulation.capitalize()}\nMould Index')
        axes = axes.flatten()
        var_x = pd.Series(running_mean.index)

        axes[0].set_title('Location 4')
        axes[0].plot(var_x, running_mean.loc[:, pd.IndexSlice['4', '2d', 'out']].values, label='2D')
        axes[0].plot(var_x, running_mean.loc[:, pd.IndexSlice['4', 'mortar', 'out']].values, label='Mortar')
        axes[0].plot(var_x, running_mean.loc[:, pd.IndexSlice['4', 'brick', 'out']].values, label='Brick')

        axes[1].set_title('Location 5')
        axes[1].plot(var_x, running_mean.loc[:, pd.IndexSlice['5', '2d', 'out']].values, label='2D')
        axes[1].plot(var_x, running_mean.loc[:, pd.IndexSlice['5', 'mortar', 'out']].values, label='Mortar')
        axes[1].plot(var_x, running_mean.loc[:, pd.IndexSlice['5', 'brick', 'out']].values, label='Brick')

        axes[0].set_ylabel(f'Mould Index - -')
        date_format = mdates.DateFormatter('%b %Y')
        axes[0].xaxis.set_major_formatter(date_format)
        axes[1].xaxis.set_major_formatter(date_format)
        plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=45, horizontalalignment='right')
        plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45, horizontalalignment='right')
        axes[0].legend()
        axes[1].legend()

        if save:
            plt.savefig(f'{graphic_folder}/mould_{acro}.pdf')

time_plots(True)


plt.show()
