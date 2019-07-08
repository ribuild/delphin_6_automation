__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from data_process.wp6_run.sim_reports.utils import *

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


if __name__ == "__main__":
    server = mongo_setup.global_init(auth_dict)

    #get_convergence_mould()
    #get_convergence_heatloss()
    #get_mould_cdf()
    #get_heatloss_cdf()
    #get_actual_average_simulation_time()
    #get_simulation_time()
    #get_simulation_time_plot()

    mongo_setup.global_end_ssh(server)
