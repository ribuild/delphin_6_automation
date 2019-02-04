__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_2d_1d as auth_dict

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)
strategy = sample_entry.Strategy.objects().first()

mould = []
heat = []


for design in strategy.standard_error:
    mould.append(strategy.standard_error[design]['mould'])
    heat.append(strategy.standard_error[design]['heat_loss'])

mould = np.array(mould)
heat = np.array(heat)

mould_avg = np.nanmean(mould, axis=0)
mould_min = np.nanmin(mould, axis=0)
mould_max = np.nanmax(mould, axis=0)
heat_avg = np.nanmean(heat, axis=0)
heat_min = np.nanmin(heat, axis=0)
heat_max = np.nanmax(heat, axis=0)
x = np.arange(0, len(heat_avg))

plt.figure()
plt.plot(x, mould_avg, color='firebrick', label='Mould - Average Absolute Error')
plt.plot(x, mould_min, linestyle='--', color='firebrick', label='Mould - Minimum Absolute Error')
plt.plot(x, mould_max, linestyle=':', color='firebrick', label='Mould - Maximum Absolute Error')

plt.plot(x, heat_avg, color='darkslateblue', label='Heat Loss - Average Absolute Error')
plt.plot(x, heat_min, linestyle='--', color='darkslateblue', label='Heat Loss - Minimum Absolute Error')
plt.plot(x, heat_max, linestyle=':', color='darkslateblue', label='Heat Loss - Maximum Absolute Error')

plt.axhline(y=0.1, linestyle=':', color='k', label='Convergence Criteria')
plt.ylabel('Absolute Error')
plt.xlabel('Sample Iteration')
plt.title('Convergence')
plt.legend()

plt.show()

mongo_setup.global_end_ssh(server)
