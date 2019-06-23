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

    simulating = delphin_entry.Delphin.objects(simulating=True).count()
    simulated = delphin_entry.Delphin.objects(simulated__exists=True).count()
    projects = delphin_entry.Delphin.objects().count()
    avg_time = delphin_entry.Delphin.objects(simulated__exists=False,
                                             estimated_simulation_time__exists=True
                                             ).average("estimated_simulation_time")

    print()
    print(f'Projects Currently Simulating: {simulating}')
    print(f'Simulated Projects: {simulated}')
    print(f'Projects in DB: {projects}')
    print(f'Remaining Projects: {projects - simulated}')
    print(f'Average Estimated Simulation Time for Remaining Projects: {avg_time:.02f} min')
    print()

    mongo_setup.global_end_ssh(server)
