from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import dtu_byg
from delphin_6_automation.database_interactions import delphin_interactions
mongo_setup.global_init(dtu_byg)
result_id = '5ad70f792e2cb22ff0a202af'
folder = r'C:\Users\ocni\Desktop\2D_1D'
sim_id = '5ad706125d9460bbdaaa432c'
general_interactions.download_raw_result(result_id, folder)
delphin_interactions.download_delphin_entry(sim_id, folder + f'/{result_id}')