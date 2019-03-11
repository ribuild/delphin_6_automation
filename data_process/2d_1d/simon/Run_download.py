

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

import sys
import os
import time
import pandas as pd
import subprocess

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

#  Loop download

range_start = 0

for step in range(50):
    print('Started step: ', step)
    range_start = range_start + 90 * step
    series = pd.Series(range_start)
    series.to_csv('range.txt')
    #os.system('download.py')
    p = subprocess.run(['py', 'download.py'], stdout=sys.stdout, shell=True)
    print('waiting')
    time.sleep(60)

