__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import numpy as np
import matplotlib.pyplot as plt
import os

# RiBuild Modules
from delphin_6_automation.file_parsing import weather_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\validation\inputs\weather'

dirdif = np.array(weather_parser.ccd_to_list(os.path.join(folder, 'Imposed Sun.ccd')))
difdif = np.array(weather_parser.ccd_to_list(os.path.join(folder, 'Imposed Sun - Dif.ccd')))

dif = dirdif - difdif
x = np.arange(0, len(dif))
plt.figure()
plt.plot(x, dif, label='Difference')
plt.legend()
plt.show()