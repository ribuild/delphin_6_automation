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
sample = sample_entry.Sample.objects(id="5cf51c6f8686fe00018ba8b1").first()
strategy = sample_entry.Strategy.objects().first()
print(strategy.samples)
print(sample)

strategy.update(push__samples=sample.id)

strategy.reload()
print(strategy.samples)
mongo_setup.global_end_ssh(server)
