__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import matplotlib.pyplot as plt
import numpy as np

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)

filtered_entries = delphin_entry.Delphin.objects(simulated__exists=True).filter(sample_data__design_option__dim='1D')
gt_day = filtered_entries.filter(simulation_time__gt=84000)


def get_time(projects):
    time = []
    for p in projects:
        time.append(p.simulation_time)

    return np.array(time)/60


sim_time = get_time(filtered_entries)

print()
print('STATS')
print(f'\tMin: {np.min(sim_time):.02f}')
print(f'\tMean: {np.mean(sim_time):.02f}')
print(f'\tMax: {np.max(sim_time):.02f}')
print('')
print(f'\tQ25: {np.quantile(sim_time, 0.25):.02f}')
print(f'\tMedian: {np.quantile(sim_time, 0.50):.02f}')
print(f'\tQ75: {np.quantile(sim_time, 0.75):.02f}')
print(f'\tQ95: {np.quantile(sim_time, 0.95):.02f}')
print(f'\tSimulations that takes longer than 1400min: {gt_day.count()} = '
      f'{gt_day.count()/filtered_entries.count()*100:.02f}%')
print('')
print('PREDICTIONS')
print('\tAverage:')
print(f'\t- (24h x 60min) / Simulation Time x 60 parallel x (10 months x 30days): '
      f'{24*60/np.mean(sim_time)*60*10*30:.01f} simulation per user')
print(f'\t- 6 users: {24*60/np.mean(sim_time)*60*10*30*6:.04e} simulations')
print('\n\tMedian:')
print(f'\t- (24h x 60min) / Simulation Time x 60 parallel x (10 months x 30days): '
      f'{24*60/np.quantile(sim_time, 0.50)*60*10*30:.01f} simulations per user')
print(f'\t- 6 users: {24*60/np.quantile(sim_time, 0.50)*60*10*30*6:.04e} simulations')
print('')

plt.figure()
plt.hist(sim_time, bins='auto', density=True)
plt.title('1D Simulation Time')
plt.xlabel('Simulation Time in Minutes')
plt.ylabel('Number of Simulations')
plt.xlim(0, 250)
plt.show()

mongo_setup.global_end_ssh(server)
