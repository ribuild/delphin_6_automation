__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS
import pandas as pd

from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import sample_entry


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

def get_data():
    server = mongo_setup.global_init(auth_dict)

    samples = sample_entry.SampleRaw.objects()

    print(f'Got {samples.count()} samples')
    samples = list(samples)
    mongo_setup.global_end_ssh(server)
    return samples


samples = get_data()
with pd.ExcelWriter('Sobol Samples.xlsx') as writer:  # doctest: +SKIP
    for sequence in samples:
        print(f'Exporting {sequence.sequence_number}')
        df = pd.DataFrame.from_dict(sequence.samples_raw)
        df.to_excel(writer, sheet_name=f'Sequence-{sequence.sequence_number}', index=False)
