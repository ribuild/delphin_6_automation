from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import dtu_byg
from delphin_6_automation.database_interactions import delphin_interactions
mongo_setup.global_init(dtu_byg)


result_ids = ['5ad723b82e2cb22ff0a202f1', '5ad7240c2e2cb22ff0a20333', '5ad858392e2cb24344ad4ecb']
sim_ids = ['5ad7229b5d9460f77e36d297', '5ad7229c5d9460f77e36d298', '5ad726ca5d9460090787f5e9']
folder = r'U:\RIBuild\2D_1D\Results'


def download(result_id, sim_id):
    general_interactions.download_raw_result(result_id, folder)
    delphin_interactions.download_delphin_entry(sim_id, folder + f'/{result_id}')


for i in range(len(result_ids)):
    download(result_ids[i], sim_ids[i])
