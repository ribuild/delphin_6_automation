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

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

acronym_file = r'U:\RIBuild\2D_1D\4A_36_Acronyms.xlsx'
out_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\2d_1d\processed_data'
result_folder = r'U:\RIBuild\2D_1D\Results'
graphic_folder = r'U:\RIBuild\2D_1D\Processed Results\4A'
#dp.process_results(acronym_file, result_folder, out_folder)

quantities = ['heat loss', 'temperature', 'relative humidity', 'moisture content', 'moisture integral']
quantity = quantities[0]
hdf_file = out_folder + '/' + quantity + '.h5'


# Open HDF
#total_uninsulated_4a = pd.read_hdf(hdf_file, 'total_4a_36_uninsulated')
#total_insulated_4a = pd.read_hdf(hdf_file, 'total_4a_36_insulated')


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


def rolling_mean_plots(mean_hours, save=False):
    insulation = 'insulated'
    acros = [f'dresden_zp_high_cement_{insulation}_36_4a', f'dresden_zd_high_cement_{insulation}_36_4a',
             f'potsdam_high_cement_{insulation}_36_4a', f'dresden_zp_low_cement_{insulation}_36_4a',
             f'dresden_zd_low_cement_{insulation}_36_4a', f'potsdam_low_cement_{insulation}_36_4a']

    time_frame = pd.DataFrame()

    for acro in acros:
        acro_data_frame = pd.read_hdf(hdf_file, acro)

        time_frame = pd.concat([time_frame,
                                acro_data_frame.loc[:, pd.IndexSlice[:, :, 'out']].rolling(mean_hours).mean()],
                               ignore_index=True)

    time_frame = dp.compute_differences(time_frame)
    #time_frame_mortar = dp.remove_outlier(time_frame, 'abs_diff', 'brick')
    #time_frame_brick = dp.remove_outlier(time_frame, 'abs_diff', 'mortar')

    dp.abs_diff_boxplot(time_frame, (-2.5, 2.5), quantity.title(),
                        f'4A 36cm {insulation.capitalize()}\nRolling Mean of {mean_hours} Hours')
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_rolling_mean_absolute_difference_{insulation}.png')

    dp.rel_diff_boxplot(time_frame, (0., 40), quantity.title(),
                        f'4A 36cm {insulation.capitalize()}\nRolling Mean of {mean_hours} Hours', log=False)
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_rolling_mean_relative_difference_{insulation}.png')

    dp.plot_linear_relation(time_frame, 'brick', (-10, 20), quantity.title(),
                            f'4A 36cm {insulation.capitalize()}\nRolling Mean of {mean_hours} Hours')
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_rolling_mean_linear_relation_brick_{insulation}.png')

    dp.plot_linear_relation(time_frame, 'mortar', (-10, 20), quantity.title(),
                            f'4A 36cm {insulation.capitalize()}\nRolling Mean of {mean_hours} Hours')
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_rolling_mean_linear_relation_mortar_{insulation}.png')


#rolling_mean_plots(24, True)


def accumulated_plots(save=False):
    insulation = 'uninsulated'
    acros = [f'dresden_zp_high_cement_{insulation}_36_4a', f'dresden_zd_high_cement_{insulation}_36_4a',
             f'potsdam_high_cement_{insulation}_36_4a', f'dresden_zp_low_cement_{insulation}_36_4a',
             f'dresden_zd_low_cement_{insulation}_36_4a', f'potsdam_low_cement_{insulation}_36_4a']

    time_frame = pd.DataFrame()

    for acro in acros:
        acro_data_frame = pd.read_hdf(hdf_file, acro)

        time_frame = pd.concat([time_frame, acro_data_frame.loc[:, pd.IndexSlice[:, :, 'out']].cumsum()],
                               ignore_index=True)

    time_frame = time_frame.divide(len(time_frame))
    time_frame = dp.compute_differences(time_frame)


    dp.abs_diff_boxplot(time_frame, (-15000, 5000), quantity.title(),
                        f'4A 36cm {insulation.capitalize()}\nAccumulated Sum')
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_accumulated_sum_absolute_difference_{insulation}.png')

    dp.rel_diff_boxplot(time_frame, (0.0, 200), quantity.title(),
                        f'4A 36cm {insulation.capitalize()}\nAccumulated Sum', log=False)
    if save:
        plt.savefig(f'{graphic_folder}/{quantity}_accumulated_sum_relative_difference_{insulation}.png')

    types = ['mortar', 'brick']
    for type_ in types:
        dp.plot_linear_relation(time_frame, type_, (-10, 30), quantity.title(),
                                f'4A 36cm {insulation.capitalize()}\nAccumulated Sum')
        if save:
            plt.savefig(f'{graphic_folder}/{quantity}_accumulated_sum_linear_relation_{type_}_{insulation}.png')


#accumulated_plots(False)


def time_plots(save=False):
    insulation = 'uninsulated'
    acros = [f'dresden_zp_high_cement_{insulation}_36_4a', f'potsdam_low_cement_{insulation}_36_4a']

    time_frame = pd.DataFrame()

    for acro in acros:
        if 'dresden' in acro:
            brick_name = 'Brick: Dresden ZP, Mortar: High Cement Ratio'
        else:
            brick_name = 'Brick: Potsdam, Mortar: Low Cement Ratio'

        acro_data_frame = pd.read_hdf(hdf_file, acro)

        time_frame = acro_data_frame.loc[:, pd.IndexSlice[:, :, 'out']]

        indices = pd.DataFrame(columns=['2d', 'brick', 'mortar'])
        indices['2d'] = np.arange(1, len(time_frame)+1)
        indices['brick'] = np.arange(1, len(time_frame)+1)
        indices['mortar'] = np.arange(1, len(time_frame)+1)
        indices.index = pd.DatetimeIndex(start=datetime.datetime(2019, 1, 1),
                                         freq='h', periods=len(indices))

        running_mean = time_frame.loc[:, pd.IndexSlice[:, :, 'out']].cumsum().divide(indices, level=1)
        dp.plot_running_mean(running_mean.iloc[8760:], (-20, 50), quantity.title(),
                             f'4A 36cm {insulation.capitalize()}- {brick_name}\nRunning Mean')
        if save:
            plt.savefig(f'{graphic_folder}/{quantity}_running_mean_{acro}.pdf')

        dp.plot_running_mean(time_frame.iloc[8760:].loc[:, pd.IndexSlice[:, :, 'out']], (-20, 50), quantity.title(),
                             f'4A 36cm {insulation.capitalize()} - {brick_name}\nOutput Values')
        if save:
            plt.savefig(f'{graphic_folder}/{quantity}_output_values_{acro}.pdf')


time_plots(False)

plt.show()
