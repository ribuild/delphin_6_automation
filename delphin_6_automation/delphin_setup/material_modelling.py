__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import copy
import os
import scipy.interpolate as ip
import numpy as np
import datetime

# RiBuild Modules
from delphin_6_automation.file_parsing import material_parser


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def compute_hybrid_material(mat1_path, mat2_path, mat1_percentage, mat2_percentage):
    mat1_file = material_parser.material_file_to_dict(mat1_path)
    mat2_file = material_parser.material_file_to_dict(mat2_path)
    hybrid = copy.deepcopy(mat1_file)

    def average_function(quantity_1, quantity_2, percentage_1, percentage_2):
        return (quantity_1 * percentage_1 + quantity_2 * percentage_2) / (percentage_1 + percentage_2)

    def spline_function(function_name):
        spline1 = ip.splrep(mat1_file[f'{function_name}-X'],
                            mat1_file[f'{function_name}-Y'], s=0)
        spline2 = ip.splrep(mat2_file[f'{function_name}-X'],
                            mat2_file[f'{function_name}-Y'], s=0)

        xn = np.linspace(min(mat1_file[f'{function_name}-X'] + mat2_file[f'{function_name}-X']),
                         max(mat1_file[f'{function_name}-X'] + mat2_file[f'{function_name}-X']),
                         len(mat1_file[f'{function_name}-X']))
        spline_eval1 = ip.splev(xn, spline1)
        spline_eval2 = ip.splev(xn, spline2)

        return spline_eval1, spline_eval2, xn

    # Info
    hybrid['IDENTIFICATION-NAME'] = f'Hybrid of {mat1_percentage}% {os.path.split(mat1_path)[-1]} ' \
                                    f'and {mat2_percentage}% {os.path.split(mat2_path)[-1]}'
    hybrid['IDENTIFICATION-AQUISITION_ID'] = '000'
    hybrid['IDENTIFICATION-PRODUCT_ID'] = 'Hybrid'
    hybrid['IDENTIFICATION-LABORATORY'] = 'Hybrid Material. Source: Dario Bottino'
    hybrid['IDENTIFICATION-DATE'] = datetime.datetime.now().strftime('%d.%m.%y')
    hybrid['IDENTIFICATION-CATEGORY'] = 'HYBRID'

    # Parameters
    # Storage Parameters
    hybrid['STORAGE_BASE_PARAMETERS-RHO'] = average_function(mat1_file['STORAGE_BASE_PARAMETERS-RHO'],
                                                             mat2_file['STORAGE_BASE_PARAMETERS-RHO'],
                                                             mat1_percentage, mat2_percentage)

    hybrid['STORAGE_BASE_PARAMETERS-CE'] = average_function(mat1_file['STORAGE_BASE_PARAMETERS-CE'],
                                                            mat2_file['STORAGE_BASE_PARAMETERS-CE'],
                                                            mat1_percentage * mat1_file['STORAGE_BASE_PARAMETERS-RHO'],
                                                            mat2_percentage * mat2_file['STORAGE_BASE_PARAMETERS-RHO'])

    hybrid['STORAGE_BASE_PARAMETERS-THETA_POR'] = average_function(mat1_file['STORAGE_BASE_PARAMETERS-THETA_POR'],
                                                                   mat2_file['STORAGE_BASE_PARAMETERS-THETA_POR'],
                                                                   mat1_percentage, mat2_percentage)

    hybrid['STORAGE_BASE_PARAMETERS-THETA_EFF'] = average_function(mat1_file['STORAGE_BASE_PARAMETERS-THETA_EFF'],
                                                                   mat2_file['STORAGE_BASE_PARAMETERS-THETA_EFF'],
                                                                   mat1_percentage, mat2_percentage)

    hybrid['STORAGE_BASE_PARAMETERS-THETA_CAP'] = average_function(mat1_file['STORAGE_BASE_PARAMETERS-THETA_CAP'],
                                                                   mat2_file['STORAGE_BASE_PARAMETERS-THETA_CAP'],
                                                                   mat1_percentage, mat2_percentage)

    hybrid['STORAGE_BASE_PARAMETERS-THETA_80'] = average_function(mat1_file['STORAGE_BASE_PARAMETERS-THETA_80'],
                                                                  mat2_file['STORAGE_BASE_PARAMETERS-THETA_80'],
                                                                  mat1_percentage, mat2_percentage)
    # Transport Parameters
    hybrid['TRANSPORT_BASE_PARAMETERS-LAMBDA'] = average_function(mat1_file['TRANSPORT_BASE_PARAMETERS-LAMBDA'],
                                                                  mat2_file['TRANSPORT_BASE_PARAMETERS-LAMBDA'],
                                                                  mat1_percentage * mat1_file[
                                                                      'STORAGE_BASE_PARAMETERS-RHO'],
                                                                  mat2_percentage * mat2_file[
                                                                      'STORAGE_BASE_PARAMETERS-RHO'])

    hybrid['TRANSPORT_BASE_PARAMETERS-AW'] = average_function(mat1_file['TRANSPORT_BASE_PARAMETERS-AW'],
                                                              mat2_file['TRANSPORT_BASE_PARAMETERS-AW'],
                                                              mat1_percentage, mat2_percentage)

    hybrid['TRANSPORT_BASE_PARAMETERS-MEW'] = average_function(mat1_file['TRANSPORT_BASE_PARAMETERS-MEW'],
                                                               mat2_file['TRANSPORT_BASE_PARAMETERS-MEW'],
                                                               mat1_percentage, mat2_percentage)

    hybrid['TRANSPORT_BASE_PARAMETERS-KLEFF'] = average_function(mat1_file['TRANSPORT_BASE_PARAMETERS-KLEFF'],
                                                                 mat2_file['TRANSPORT_BASE_PARAMETERS-KLEFF'],
                                                                 mat1_percentage, mat2_percentage)
    # Functions
    # Storage Functions
    Theta_lpC = spline_function('MOISTURE_STORAGE-FUNCTION-Theta_l(pC)_de')
    hybrid['MOISTURE_STORAGE-FUNCTION-Theta_l(pC)_de-X'] = Theta_lpC[2].tolist()
    hybrid['MOISTURE_STORAGE-FUNCTION-Theta_l(pC)_de-Y'] = average_function(Theta_lpC[0], Theta_lpC[1],
                                                                            mat1_percentage, mat2_percentage).tolist()

    pCTheta_l = spline_function('MOISTURE_STORAGE-FUNCTION-pC(Theta_l)_de')
    hybrid['MOISTURE_STORAGE-FUNCTION-pC(Theta_l)_de-X'] = pCTheta_l[2].tolist()
    hybrid['MOISTURE_STORAGE-FUNCTION-pC(Theta_l)_de-Y'] = average_function(pCTheta_l[0], pCTheta_l[1],
                                                                            mat1_percentage, mat2_percentage)

    # Transport Functions
    lgKlTheta_l = spline_function('MOISTURE_TRANSPORT-FUNCTION-lgKl(Theta_l)')
    hybrid['MOISTURE_TRANSPORT-FUNCTION-lgKl(Theta_l)-X'] = lgKlTheta_l[2].tolist()
    hybrid['MOISTURE_TRANSPORT-FUNCTION-lgKl(Theta_l)-Y'] = average_function(lgKlTheta_l[0], lgKlTheta_l[1],
                                                                             mat1_percentage, mat2_percentage).tolist()

    lgKvTheta_l = spline_function('MOISTURE_TRANSPORT-FUNCTION-lgKv(Theta_l)')
    hybrid['MOISTURE_TRANSPORT-FUNCTION-lgKv(Theta_l)-X'] = lgKvTheta_l[2].tolist()
    hybrid['MOISTURE_TRANSPORT-FUNCTION-lgKv(Theta_l)-Y'] = average_function(lgKvTheta_l[0], lgKvTheta_l[1],
                                                                             mat1_percentage, mat2_percentage).tolist()


def create_hybrid_material():
    pass


path = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\delphin_6_automation\pytest\test_files\materials'
mat1 = path + '/AltbauziegelDresdenZP_504.m6'
mat2 = path + '/LimeCementMortarHighCementRatio_717.m6'

compute_hybrid_material(mat1, mat2, 0.8, 0.2)
