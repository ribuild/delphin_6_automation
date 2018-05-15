from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
import os
import pandas as pd
import numpy as np

mongo_setup.global_init(auth_dict)


folder = r'U:\RIBuild\Material_Sensitivity\Results'


def download(sim_obj):
    result_id = str(sim_obj.results_raw.id)
    general_interactions.download_raw_result(result_id, folder)
    delphin_interactions.download_delphin_entry(str(sim_obj.id), folder + f'/{result_id}')


sim_id = []
result_id = []
bricks = []

for entry in delphin_entry.Delphin.objects():
    if entry.simulated:  # and not os.path.exists(folder + f'\{str(entry.results_raw.id)}'):
        sim_id.append(str(entry.id))
        result_id.append(str(entry.results_raw.id))
        bricks.extend([f'{mat.material_name}_{mat.material_id}' for mat in entry.materials if mat.material_name != 'LimeCementMortarHighCementRatio'])
        #print(f"Simulation ID: {str(entry.id)}, Result ID: {str(entry.results_raw.id)}, "
        #      f"Materials: {' '.join([mat.material_name for mat in entry.materials])}\n")
        #download(entry)

lists = np.vstack([sim_id, result_id, bricks]).T
data = pd.DataFrame(lists, columns=('Simulation IDs', 'Result IDs', 'Brick Type'))
print(data.head())

excel_file = r'U:\RIBuild\Material_Sensitivity\simulation table.xlsx'
writer = pd.ExcelWriter(excel_file)
data.to_excel(writer, 'Sheet1')
writer.save()
