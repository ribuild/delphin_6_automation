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
hdf_file = out_folder + '/relative_moisture_content.h5'

# Open HDF
# Uninsulated
dresdenzp_highratio_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zp_high_ratio_uninsulated_4a')
dresdenzd_highratio_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zd_high_ratio_uninsulated_4a')
postdam_highratio_uninsulated_4a = pd.read_hdf(hdf_file, 'potsdam_high_ratio_uninsulated_4a')
dresdenzp_lowratio_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zp_low_ratio_uninsulated_4a')
dresdenzd_lowratio_uninsulated_4a = pd.read_hdf(hdf_file, 'dresden_zd_low_ratio_uninsulated_4a')
postdam_lowratio_uninsulated_4a = pd.read_hdf(hdf_file, 'potsdam_low_ratio_uninsulated_4a')

total_uninsulated_4a = pd.concat([dresdenzp_highratio_uninsulated_4a, dresdenzd_highratio_uninsulated_4a,
                                  postdam_highratio_uninsulated_4a, dresdenzp_lowratio_uninsulated_4a,
                                  dresdenzd_lowratio_uninsulated_4a, postdam_lowratio_uninsulated_4a])

# Insulated
dresdenzp_highratio_insulated_4a = pd.read_hdf(hdf_file, 'dresden_zp_high_ratio_insulated_4a')
dresdenzd_highratio_insulated_4a = pd.read_hdf(hdf_file, 'dresden_zd_high_ratio_insulated_4a')
postdam_highratio_insulated_4a = pd.read_hdf(hdf_file, 'potsdam_high_ratio_insulated_4a')
dresdenzp_lowratio_insulated_4a = pd.read_hdf(hdf_file, 'dresden_zp_low_ratio_insulated_4a')
dresdenzd_lowratio_insulated_4a = pd.read_hdf(hdf_file, 'dresden_zd_low_ratio_insulated_4a')
postdam_lowratio_insulated_4a = pd.read_hdf(hdf_file, 'potsdam_low_ratio_insulated_4a')

total_insulated_4a = pd.concat([dresdenzp_highratio_insulated_4a, dresdenzd_highratio_insulated_4a,
                                postdam_highratio_insulated_4a, dresdenzp_lowratio_insulated_4a,
                                dresdenzd_lowratio_insulated_4a, postdam_lowratio_insulated_4a])


def plots(plot, save=False):
    """
    Creates box plots from all the wall scenarios
    """

    if plot == 'uninsulated' or plot == 'all':
        plt.figure('dresdenzp_highratio_uninsulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        dresdenzp_highratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 1100)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Dresden ZP - Mortar: High Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzp_highratio_uninsulated_4a_moisture")

        plt.figure('dresdenzd_highratio_uninsulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        dresdenzd_highratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 1100)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Dresden ZD - Mortar: High Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzd_highratio_uninsulated_4a_moisture")

        plt.figure('postdam_highratio_uninsulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        postdam_highratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 1100)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Potsdam - Mortar: High Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/postdam_highratio_uninsulated_4a_moisture")

        plt.figure('dresdenzp_lowratio_uninsulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        dresdenzp_lowratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 1100)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Dresden ZP - Mortar: Low Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzp_lowratio_uninsulated_4a_moisture")

        plt.figure('dresdenzd_lowratio_uninsulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        dresdenzd_lowratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 1100)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Dresden ZD - Mortar: Low Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzd_lowratio_uninsulated_4a_moisture")

        plt.figure('postdam_lowratio_uninsulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        postdam_lowratio_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 1100)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Potsdam - Mortar: Low Cement Ratio - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/postdam_lowratio_uninsulated_4a_moisture")

        plt.figure('total_uninsulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        total_uninsulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 1100)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: All - Mortar: All - Insulation: None')
        if save:
            plt.savefig(f"{graphic_folder}/total_uninsulated_4a_moisture")

    if plot == 'insulated' or plot == 'all':
        plt.figure('dresdenzp_highratio_insulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        dresdenzp_highratio_insulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 2000)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Dresden ZP - Mortar: High Cement Ratio - Insulation: Calcium Silicate')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzp_highratio_insulated_4a_moisture")

        plt.figure('dresdenzd_highratio_insulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        dresdenzd_highratio_insulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 2000)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Dresden ZD - Mortar: High Cement Ratio - Insulation: Calcium Silicate')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzd_highratio_insulated_4a_moisture")

        plt.figure('postdam_highratio_insulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        postdam_highratio_insulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 2000)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Potsdam - Mortar: High Cement Ratio - Insulation: Calcium Silicate')
        if save:
            plt.savefig(f"{graphic_folder}/postdam_highratio_insulated_4a_moisture")

        plt.figure('dresdenzp_lowratio_insulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        dresdenzp_lowratio_insulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 2000)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Dresden ZP - Mortar: Low Cement Ratio - Insulation: Calcium Silicate')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzp_lowratio_insulated_4a_moisture")

        plt.figure('dresdenzd_lowratio_insulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        dresdenzd_lowratio_insulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 2000)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Dresden ZD - Mortar: Low Cement Ratio - Insulation: Calcium Silicate')
        if save:
            plt.savefig(f"{graphic_folder}/dresdenzd_lowratio_insulated_4a_moisture")

        plt.figure('postdam_lowratio_insulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        postdam_lowratio_insulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 2000)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: Potsdam - Mortar: Low Cement Ratio - Insulation: Calcium Silicate')
        if save:
            plt.savefig(f"{graphic_folder}/postdam_lowratio_insulated_4a_moisture")

        plt.figure('total_insulated_4a_moisture', figsize=(16, 8), tight_layout=True)
        total_insulated_4a.boxplot(showfliers=False)
        plt.ylim(-5, 2000)
        plt.ylabel('Relative Difference in %')
        plt.title('Weighted Relative Difference between 1D and 2D\n'
                  'Moisture Content\n'
                  'Brick: All - Mortar: All - Insulation: Calcium Silicate')
        if save:
            plt.savefig(f"{graphic_folder}/total_insulated_4a_moisture")

    plt.show()


plots('all', False)


def std3_ratio(print_=False, excel=False):
    """Computes ratio of outliers in the data sets. Outliers is here defined as data points deviating with more
    the 3 standard deviations from the mean."""

    std3_uninsulated_ratio_ = uninsulated()
    std3_insulated_ratio_ = insulated()

    if print_:
        print('Uninsulated')
        print(std3_uninsulated_ratio_)
        print('')
        print('Insulated')
        print(std3_insulated_ratio_)

    if excel:
        writer = pd.ExcelWriter(f'{out_folder}/moisture_std_ratios.xlsx')
        std3_uninsulated_ratio_.to_excel(writer, 'Uninsulated')
        std3_insulated_ratio_.to_excel(writer, 'Insulated')
        writer.save()


def uninsulated():
    """Computes the outliers for the uninsulated cases"""

    outliers_total_uninsulated = (total_uninsulated_4a.shape[0] -
                                  total_uninsulated_4a.sub(total_uninsulated_4a.mean())
                                  .div(total_uninsulated_4a.std()).abs().lt(3).sum()) / total_uninsulated_4a.shape[0]

    outliers_zd_high_uninsulated = (dresdenzd_highratio_uninsulated_4a.shape[0] -
                                    dresdenzd_highratio_uninsulated_4a.sub(dresdenzd_highratio_uninsulated_4a.mean())
                                    .div(dresdenzd_highratio_uninsulated_4a.std()).abs().lt(3).sum()) \
                                   / dresdenzd_highratio_uninsulated_4a.shape[0]

    outliers_zp_high_uninsulated = (dresdenzp_highratio_uninsulated_4a.shape[0] -
                                    dresdenzp_highratio_uninsulated_4a.sub(dresdenzp_highratio_uninsulated_4a.mean())
                                    .div(dresdenzp_highratio_uninsulated_4a.std()).abs().lt(3).sum()) \
                                   / dresdenzp_highratio_uninsulated_4a.shape[0]

    outliers_pd_high_uninsulated = (postdam_highratio_uninsulated_4a.shape[0] -
                                    postdam_highratio_uninsulated_4a.sub(postdam_highratio_uninsulated_4a.mean())
                                    .div(postdam_highratio_uninsulated_4a.std()).abs().lt(3).sum()) \
                                   / postdam_highratio_uninsulated_4a.shape[0]

    outliers_zd_low_uninsulated = (dresdenzd_lowratio_uninsulated_4a.shape[0] -
                                   dresdenzd_lowratio_uninsulated_4a.sub(dresdenzd_lowratio_uninsulated_4a.mean())
                                   .div(dresdenzd_lowratio_uninsulated_4a.std()).abs().lt(3).sum()) \
                                  / dresdenzd_lowratio_uninsulated_4a.shape[0]

    outliers_zp_low_uninsulated = (dresdenzp_lowratio_uninsulated_4a.shape[0] -
                                   dresdenzp_lowratio_uninsulated_4a.sub(dresdenzp_lowratio_uninsulated_4a.mean())
                                   .div(dresdenzp_lowratio_uninsulated_4a.std()).abs().lt(3).sum()) \
                                  / dresdenzp_lowratio_uninsulated_4a.shape[0]

    outliers_pd_low_uninsulated = (postdam_lowratio_uninsulated_4a.shape[0] -
                                   postdam_lowratio_uninsulated_4a.sub(postdam_lowratio_uninsulated_4a.mean())
                                   .div(postdam_lowratio_uninsulated_4a.std()).abs().lt(3).sum()) \
                                  / postdam_lowratio_uninsulated_4a.shape[0]

    outliers_uninsulated_ratio_ = pd.concat([outliers_total_uninsulated, outliers_zd_high_uninsulated,
                                             outliers_zp_high_uninsulated, outliers_pd_high_uninsulated,
                                             outliers_zd_low_uninsulated, outliers_zp_low_uninsulated,
                                             outliers_pd_low_uninsulated], axis=1)

    outliers_uninsulated_ratio_.columns = ["Brick: All - Mortar: All - Insulation: None",
                                           "Brick: Dresden ZD - Mortar: High Cement Ratio - Insulation: None",
                                           "Brick: Dresden ZP - Mortar: High Cement Ratio - Insulation: None",
                                           "Brick: Potsdam - Mortar: High Cement Ratio - Insulation: None",
                                           "Brick: Dresden ZD - Mortar: Low Cement Ratio - Insulation: None",
                                           "Brick: Dresden ZP - Mortar: Low Cement Ratio - Insulation: None",
                                           "Brick: Potsdam - Mortar: Low Cement Ratio - Insulation: None"]
    return outliers_uninsulated_ratio_


def insulated():
    """Computes the outliers for the insulated cases"""

    outliers_total_insulated = (total_insulated_4a.shape[0] - total_insulated_4a.sub(total_insulated_4a.mean())
                                .div(total_insulated_4a.std()).abs().lt(3).sum()) / total_insulated_4a.shape[0]

    outliers_zd_high_insulated = (dresdenzd_highratio_insulated_4a.shape[0] -
                                  dresdenzd_highratio_insulated_4a.sub(dresdenzd_highratio_insulated_4a.mean())
                                  .div(dresdenzd_highratio_insulated_4a.std()).abs().lt(3).sum()) \
                                 / dresdenzd_highratio_insulated_4a.shape[0]

    outliers_zp_high_insulated = (dresdenzp_highratio_insulated_4a.shape[0] -
                                  dresdenzp_highratio_insulated_4a.sub(dresdenzp_highratio_insulated_4a.mean())
                                  .div(dresdenzp_highratio_insulated_4a.std()).abs().lt(3).sum()) \
                                 / dresdenzp_highratio_insulated_4a.shape[0]

    outliers_pd_high_insulated = (postdam_highratio_insulated_4a.shape[0] -
                                  postdam_highratio_insulated_4a.sub(postdam_highratio_insulated_4a.mean())
                                  .div(postdam_highratio_insulated_4a.std()).abs().lt(3).sum()) \
                                 / postdam_highratio_insulated_4a.shape[0]

    outliers_zd_low_insulated = (dresdenzd_lowratio_insulated_4a.shape[0] -
                                 dresdenzd_lowratio_insulated_4a.sub(dresdenzd_lowratio_insulated_4a.mean())
                                 .div(dresdenzd_lowratio_insulated_4a.std()).abs().lt(3).sum()) \
                                / dresdenzd_lowratio_insulated_4a.shape[0]

    outliers_zp_low_insulated = (dresdenzp_lowratio_insulated_4a.shape[0] -
                                 dresdenzp_lowratio_insulated_4a.sub(dresdenzp_lowratio_insulated_4a.mean())
                                 .div(dresdenzp_lowratio_insulated_4a.std()).abs().lt(3).sum()) \
                                / dresdenzp_lowratio_insulated_4a.shape[0]

    outliers_pd_low_insulated = (postdam_lowratio_insulated_4a.shape[0] -
                                 postdam_lowratio_insulated_4a.sub(postdam_lowratio_insulated_4a.mean())
                                 .div(postdam_lowratio_insulated_4a.std()).abs().lt(3).sum()) \
                                / postdam_lowratio_insulated_4a.shape[0]

    std2_insulated_ratio_ = pd.concat([outliers_total_insulated, outliers_zd_high_insulated,
                                       outliers_zp_high_insulated, outliers_pd_high_insulated,
                                       outliers_zd_low_insulated, outliers_zp_low_insulated,
                                       outliers_pd_low_insulated], axis=1)

    std2_insulated_ratio_.columns = ["Brick: All - Mortar: All - Insulation: None",
                                     "Brick: Dresden ZD - Mortar: High Cement Ratio - Insulation: Calcium Silicate",
                                     "Brick: Dresden ZP - Mortar: High Cement Ratio - Insulation: Calcium Silicate",
                                     "Brick: Potsdam - Mortar: High Cement Ratio - Insulation: Calcium Silicate",
                                     "Brick: Dresden ZD - Mortar: Low Cement Ratio - Insulation: Calcium Silicate",
                                     "Brick: Dresden ZP - Mortar: Low Cement Ratio - Insulation: Calcium Silicate",
                                     "Brick: Potsdam - Mortar: Low Cement Ratio - Insulation: Calcium Silicate"]
    return std2_insulated_ratio_


#std3_ratio(False, True)
