__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import pandas as pd
import copy

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions import auth
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


data_folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\simtime_prediction\data'

server = mongo_setup.global_init(auth.auth_dict)

entries = delphin_entry.Delphin.objects(simulation_time__exists=True)

col = ['time', ] + list(entries[0].sample_data.keys())[:-1] + list(entries[0].sample_data['design_option'].keys())
frames = []

for i in range(len(entries)):
    entry = entries[i]
    data = copy.deepcopy(entry.sample_data)
    del data['sequence']
    del data['design_option']
    data.update(entry.sample_data['design_option'])
    data['time'] = entry.simulation_time
    """
    for key in col:
        if key not in ['time', 'design_option']:
            data.append(entry.sample_data[key])
    """

    frames.append(pd.DataFrame(columns=col, data=data, index=[i, ]))

data_frame = pd.concat(frames)

writer = pd.ExcelWriter(os.path.join(data_folder, 'sim_time.xlsx'))
data_frame.to_excel(writer, 'simtime')
writer.save()
print('done')

mongo_setup.global_end_ssh(server)
