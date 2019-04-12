__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import numpy as np

# RiBuild Modules
from delphin_6_automation.file_parsing import weather_parser
from delphin_6_automation.delphin_setup import weather_modeling

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\inputs\weather'
direct = os.path.join(folder, 'DWD_Weimar_DirectRadiation.ccd')
diffuse = os.path.join(folder, 'DWD_Weimar_DiffuseRadiation.ccd')
direct_radiation = weather_parser.ccd_to_list(direct)
diffuse_radiation = weather_parser.ccd_to_list(diffuse)
radiation = np.array(direct_radiation) + np.array(diffuse_radiation)
short_wave_radiation = weather_modeling.short_wave_radiation(radiation, 11.19, 50.59, 0, 180)
short = os.path.join(folder, 'Imposed Sun.ccd')
weather_parser.list_to_ccd(short_wave_radiation, {'location_name': 'Weimar', 'year': 2017,
                                                  'description': 'Short Wave Radiation [W/m2] (ISD)',
                                                  'intro': 'SHWRAD   W/m2'},
                           short)
