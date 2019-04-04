__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_2d_1d as auth_dict
# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

server = mongo_setup.global_init(auth_dict)

sample = sample_entry.Sample.objects(id="5c8a66c80243e20001478254").first()
strategy = sample_entry.Strategy.objects().first()
print(strategy.samples)
print(sample)

strategy.update(push__samples=sample.id)

strategy.reload()
print(strategy.samples)
mongo_setup.global_end_ssh(server)
