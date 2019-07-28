__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions import simulation_interactions

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

if __name__ == "__main__":
    server = mongo_setup.global_init(auth_dict)

    simulating = delphin_entry.Delphin.objects(simulating__ne=None).count()
    simulated = delphin_entry.Delphin.objects(simulated__exists=True).count()
    projects = delphin_entry.Delphin.objects().count()
    avg_time = delphin_entry.Delphin.objects(simulated__exists=False,
                                             estimated_simulation_time__exists=True
                                             ).average("estimated_simulation_time")
    auth_path = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\test\checks'
    file = os.path.join(auth_path, 'ocni.json')
    bstat, pending = simulation_interactions.check_simulations(file, only_count=True)
    strategy = sample_entry.Strategy.objects().first()

    print()
    print(f'Projects Currently Simulating: {simulating}')
    print(f'Projects Running in BSTAT: {bstat} - {pending} Projects Pending')
    print(f'Simulated Projects: {simulated}')
    print(f'Projects in DB: {projects}')
    print(f'Remaining Projects: {projects - simulated}')
    print(f'Average Estimated Simulation Time for Remaining Projects: {avg_time:.02f} min')
    print()
    print(f'Current Iteration: {strategy.current_iteration}')
    #print(f'Number of Samples in Strategy: {len(strategy.samples)}')
    print()
    mongo_setup.global_end_ssh(server)
