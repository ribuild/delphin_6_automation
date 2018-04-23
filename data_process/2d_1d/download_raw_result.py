from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import dtu_byg
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
import os


mongo_setup.global_init(dtu_byg)


folder = r'U:\RIBuild\2D_1D\Results'


def download(sim_obj):
    result_id = str(sim_obj.results_raw.id)
    general_interactions.download_raw_result(result_id, folder)
    delphin_interactions.download_delphin_entry(str(sim_obj.id), folder + f'/{result_id}')


for entry in delphin_entry.Delphin.objects():
    if entry.simulated and not os.path.exists(folder + f'\{str(entry.results_raw.id)}'):
        print(f"Simulation ID: {str(entry.id)}, Result ID: {str(entry.results_raw.id)}, "
              f"Materials: {' '.join([mat.material_name for mat in entry.materials])}\n")
        download(entry)