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
graphic_folder = r'U:\RIBuild\2D_1D\Processed Results\4A'
hdf_file = out_folder + '/relative_humidity.h5'
dresdenzp_highratio_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zp_high_ratio_uninsulated_4a')
dresdenzd_highratio_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zd_high_ratio_uninsulated_4a')
postdam_highratio_uninsulated_4a = pd.read_hdf(hdf_file, 'potsdam_high_ratio_uninsulated_4a')
dresdenzp_lowratio_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zp_low_ratio_uninsulated_4a')
dresdenzd_lowratio_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zd_low_ratio_uninsulated_4a')
postdam_lowratio_uninsulated_4a = pd.read_hdf(hdf_file, 'potsdam_low_ratio_uninsulated_4a')
total_uninsulated_4a = pd.concat([dresdenzp_highratio_uninsulated_4a, dresdenzd_highratio_uninsulated_4a,
                                  postdam_highratio_uninsulated_4a, dresdenzp_lowratio_uninsulated_4a,
                                  dresdenzd_lowratio_uninsulated_4a, postdam_lowratio_uninsulated_4a])


def plots(plot, save=False):
    if plot == 'uninsulated' or plot == 'all':
        plt.figure('dresdenzp_highratio_uninsulated_4a_relhum', figsize=(16, 8), tight_layout=True)
        dresdenzp_highratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 60)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Relative Humidity\n'
                  'Brick: Dresden ZP - Mortar: High Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzp_highratio_uninsulated_4a_relhum")

        plt.figure('dresdenzd_highratio_uninsulated_4a_relhum', figsize=(16, 8), tight_layout=True)
        dresdenzd_highratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 60)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Relative Humidity\n'
                  'Brick: Dresden ZD - Mortar: High Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzd_highratio_uninsulated_4a_relhum")

        plt.figure('postdam_highratio_uninsulated_4a_relhum', figsize=(16, 8), tight_layout=True)
        postdam_highratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 60)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Relative Humidity\n'
                  'Brick: Potsdam - Mortar: High Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/postdam_highratio_uninsulated_4a_relhum")

        plt.figure('dresdenzp_lowratio_uninsulated_4a_relhum', figsize=(16, 8), tight_layout=True)
        dresdenzp_lowratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 60)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Relative Humidity\n'
                  'Brick: Dresden ZP - Mortar: Low Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzp_lowratio_uninsulated_4a_relhum")

        plt.figure('dresdenzd_lowratio_uninsulated_4a_relhum', figsize=(16, 8), tight_layout=True)
        dresdenzd_lowratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 60)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Relative Humidity\n'
                  'Brick: Dresden ZD - Mortar: Low Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzd_lowratio_uninsulated_4a_relhum")

        plt.figure('postdam_lowratio_uninsulated_4a_relhum', figsize=(16, 8), tight_layout=True)
        postdam_lowratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 60)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Relative Humidity\n'
                  'Brick: Potsdam - Mortar: Low Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/postdam_lowratio_uninsulated_4a_relhum")

        plt.figure('total_uninsulated_4a_relhum', figsize=(16, 8), tight_layout=True)
        total_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 60)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Relative Humidity\n'
                  'Brick: All - Mortar: All - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/total_uninsulated_4a_relhum")

    if plot == 'insulated' or plot == 'all':
        pass

    plt.show()


plots('all', True)


def std2_ratio(print_=False, excel=False):
    std2_total_uninsulated = total_uninsulated_4a[total_uninsulated_4a > 2 * total_uninsulated_4a.std()]
    std2_zd_high_uninsulated = dresdenzd_highratio_uninsulated_4a[dresdenzd_highratio_uninsulated_4a
                                                                  > 2 * dresdenzd_highratio_uninsulated_4a.std()]
    std2_zp_high_uninsulated = dresdenzp_highratio_uninsulated_4a[dresdenzp_highratio_uninsulated_4a
                                                                  > 2 * dresdenzp_highratio_uninsulated_4a.std()]
    std2_pd_high_uninsulated = postdam_highratio_uninsulated_4a[postdam_highratio_uninsulated_4a
                                                                > 2 * postdam_highratio_uninsulated_4a.std()]
    std2_zd_low_uninsulated = dresdenzd_lowratio_uninsulated_4a[dresdenzd_lowratio_uninsulated_4a
                                                                > 2 * dresdenzd_lowratio_uninsulated_4a.std()]
    std2_zp_low_uninsulated = dresdenzp_lowratio_uninsulated_4a[dresdenzp_lowratio_uninsulated_4a
                                                                > 2 * dresdenzp_lowratio_uninsulated_4a.std()]
    std2_pd_low_uninsulated = postdam_lowratio_uninsulated_4a[postdam_lowratio_uninsulated_4a
                                                              > 2 * postdam_lowratio_uninsulated_4a.std()]

    std2_total_uninsulated_ratio = std2_total_uninsulated.notnull().sum() / std2_total_uninsulated.shape[0]
    std2_zd_high_uninsulated_ratio = std2_zd_high_uninsulated.notnull().sum() / std2_zd_high_uninsulated.shape[0]
    std2_zp_high_uninsulated_ratio = std2_zp_high_uninsulated.notnull().sum() / std2_zp_high_uninsulated.shape[0]
    std2_pd_high_uninsulated_ratio = std2_pd_high_uninsulated.notnull().sum() / std2_pd_high_uninsulated.shape[0]
    std2_zd_low_uninsulated_ratio = std2_zd_low_uninsulated.notnull().sum() / std2_zd_low_uninsulated.shape[0]
    std2_zp_low_uninsulated_ratio = std2_zp_low_uninsulated.notnull().sum() / std2_zp_low_uninsulated.shape[0]
    std2_pd_low_uninsulated_ratio = std2_pd_low_uninsulated.notnull().sum() / std2_pd_low_uninsulated.shape[0]

    std2_uninsulated_ratio_ = pd.concat([std2_total_uninsulated_ratio, std2_zd_high_uninsulated_ratio,
                                         std2_zp_high_uninsulated_ratio, std2_pd_high_uninsulated_ratio,
                                         std2_zd_low_uninsulated_ratio, std2_zp_low_uninsulated_ratio,
                                         std2_pd_low_uninsulated_ratio], axis=1)
    std2_uninsulated_ratio_.columns = ["Brick: All - Mortar: All - Insulation: None",
                                       "Brick: Dresden ZD - Mortar: High Cement Ratio - Insulation: None",
                                       "Brick: Dresden ZP - Mortar: High Cement Ratio - Insulation: None",
                                       "Brick: Potsdam - Mortar: High Cement Ratio - Insulation: None",
                                       "Brick: Dresden ZD - Mortar: Low Cement Ratio - Insulation: None",
                                       "Brick: Dresden ZP - Mortar: Low Cement Ratio - Insulation: None",
                                       "Brick: Potsdam - Mortar: Low Cement Ratio - Insulation: None"]

    if print_:
        print(std2_uninsulated_ratio_)

    if excel:
        writer = pd.ExcelWriter(f'{out_folder}/relhum_std_ratios.xlsx')
        std2_uninsulated_ratio_.to_excel(writer, 'Uninsulated')
        writer.save()


std2_ratio(True, True)
