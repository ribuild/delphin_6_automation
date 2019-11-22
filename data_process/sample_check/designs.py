from delphin_6_automation.sampling.sampling import create_design_info

__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS
import pandas as pd
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
# Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def get_data():
    server = mongo_setup.global_init(auth_dict)

    strategy = sample_entry.Strategy.objects().first()
    print(f'Got Strategy: {strategy.id}')
    strategy = dict(strategy.strategy)
    mongo_setup.global_end_ssh(server)
    return strategy


df = None
strategy = get_data()
for index, design in enumerate(strategy['design']):
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(create_design_info(design), index=[index])

    else:
        df_add = pd.DataFrame(create_design_info(design), index=[index])
        df = df.append(df_add)

df.to_excel('Designs.xlsx', index=False)
