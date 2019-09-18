__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

if __name__ == "__main__":
    server = mongo_setup.global_init(auth_dict)

    filtered_entries = delphin_entry.Delphin.objects(simulated__exists=True).only('simulation_time')
    gt_300 = filtered_entries.filter(simulation_time__gt=300 * 60)
    print('GT 300', gt_300.count())

    #gt_300.update(set__simulation_time=275 * 60)

    filtered_entries = delphin_entry.Delphin.objects(simulated__exists=True).only('simulation_time')
    gt_300 = filtered_entries.filter(simulation_time__gt=300 * 60)
    print('GT 300', gt_300.count())
    mongo_setup.global_end_ssh(server)


