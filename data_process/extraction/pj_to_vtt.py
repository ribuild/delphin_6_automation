__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import numpy as np

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.delphin_setup import damage_models

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)

entries = delphin_entry.Delphin.objects(simulated__exists=True)

for delphin in entries:
    pro_result = delphin.result_processed
    raw_result = delphin.results_raw
    relative_humidity_mould =
    temperature_mould =
    mould = damage_models.mould_index(relative_humidity_mould, temperature_mould,
                                      draw_back=1, sensitivity_class=3, surface_quality=0)
    pro_result.mould.replace(np.asarray(mould).tobytes())
    pro_result.save()
    pro_result.update(threshold__mould__set=max(mould))
mongo_setup.global_end_ssh(server)