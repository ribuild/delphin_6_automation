__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild
server = mongo_setup.global_init(auth_dict)

"""
sample = sample_entry.Sample.objects(id="5d458cd13563d900012271fc").first()


print(f'Adding {sample.id} to strategy {strategy.id}')
strategy.update(push__samples=sample.id)

strategy.reload()


strategy = sample_entry.Strategy.objects().first()
print('Samples in Strategy')
print(f'Current Iteration {strategy.current_iteration}')
[print(s.id) for s in strategy.samples]
print()
"""

samples = sample_entry.Sample.objects(id="5e549199fd1c580001776e78").first()
print(len(samples.mean))
#print(samples)
#print('Samples in DB')
#[print(s.iteration, s.id) for s in samples]

mongo_setup.global_end_ssh(server)
