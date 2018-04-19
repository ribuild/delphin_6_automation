from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import dtu_byg
from delphin_6_automation.database_interactions import delphin_interactions
mongo_setup.global_init(dtu_byg)


result_ids = ['5ad894572e2cb21b4c5bdd07', '5ad894e72e2cb21b4c5bdd44', '5ad895882e2cb21b4c5bdd81',
              '5ad896442e2cb21b4c5bddbe', '5ad898312e2cb21b4c5bddfb', '5ad898a02e2cb21b4c5bde38',
              '5ad899592e2cb21b4c5bde75', '5ad89b592e2cb21b4c5bdeb2']
sim_ids = ['5ad892e65d9460a45f7bddeb', '5ad892e85d9460a45f7bddec', '5ad892e85d9460a45f7bdded',
           '5ad892e85d9460a45f7bddee', '5ad892fb5d94609e5b584f69', '5ad892fc5d94609e5b584f6a',
           '5ad892fc5d94609e5b584f6b', '5ad892fd5d94609e5b584f6c']

folder = r'U:\RIBuild\2D_1D\Results'


def download(result_id, sim_id):
    general_interactions.download_raw_result(result_id, folder)
    delphin_interactions.download_delphin_entry(sim_id, folder + f'/{result_id}')


for i in range(len(result_ids)):
    download(result_ids[i], sim_ids[i])
