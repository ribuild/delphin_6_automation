from delphin_6_automation.sampling.sampling import compute_sampling_distributions

__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
# Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry
import numpy as np
import pandas as pd
from multiprocessing import Pool


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def get_data():
    server = mongo_setup.global_init(auth_dict)

    strategy = sample_entry.Strategy.objects().first()
    print(f'Got Strategy: {strategy.id}')

    samples_raw = sample_entry.SampleRaw.objects()
    print(f'Got {samples_raw.count()} samples')

    samples = list(samples_raw)
    strategy = dict(strategy.strategy)

    mongo_setup.global_end_ssh(server)
    return strategy, samples


def process_data(data):
    sequence, samples_raw, strategy = data
    print(f'Starting processing sequence: {sequence}')
    raw = samples_raw[sequence]
    df = None
    for i in range(512):
        print(f'Running row {i} of sequence {sequence}')

        samples = compute_sampling_distributions(strategy, np.array(raw.samples_raw), i)
        sample = samples['1d_bare_MineralFoamMulltipor_595_125_77_60']['generic_scenario']

        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame.from_dict(sample)
        else:
            df_add = pd.DataFrame.from_dict(sample)
            df = df.append(df_add)

    return df


if __name__ == '__main__':

    strategy, samples_raw = get_data()

    pool = Pool(4)
    input_data = [(i, samples_raw, strategy) for i in range(10)]
    data_frames = pool.map(process_data, input_data)

    print('\nDone with data processing. Starting to write Excel')

    with pd.ExcelWriter('Actual Values.xlsx') as writer:
        for index, df in enumerate(data_frames):
            df.to_excel(writer, sheet_name=f'Sequence-{index}', index=False)
