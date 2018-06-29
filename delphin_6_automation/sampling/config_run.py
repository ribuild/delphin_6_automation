# -*- coding: utf-8 -*-
"""
Example of how to use shark to for probabilistic Monte-Carlo simulations with DELPHIN 5.8.
===============================================================================
2018-05-04

In this script, you first have to define the parameter distributions, as are all the 
other variables needed for the probabilistic assessment. 

Next, the script automatically samples the given parameter distributions according 
to the specified sampling strategy. The parameter values of the original Delphin 
files are edited using these samples and the edited Delphin files are then 
saved as new variation Delphin files for simulation. Subsequently, the files are
simulated.

Next, the output files are read and postprocessed (see postproc_convergence.py)
and convergence is monitored. If convergence is not reached, new samples are selected,
new Delphin files are created and simulated, and their output is postprocessed.
This continues until convergence is reached or the maximum number of samples is 
reached.
"""

import pandas as pd

# Interior climate model
interior_climate_type = 'EN15026'  # Use 'EN15026' or 'EN13788'

# Scenario layer - scenario's
scenario = {'parameter': 'brick material',
            'value': ['Brick1', 'Brick2', 'Brick3']}  # currently, only one scenario parameter is supported

# Uncertainty layer - Parameter distributions

# Why are we using Pandas and not just a dict?
distributions = pd.DataFrame([{'parameter': 'solar absorption', 'type': 'uniform', 'value': [0.4, 0.8]},
                              {'parameter': 'ext climate', 'type': 'discrete',
                               'value': ['Oostende', 'Gent', 'StHubert', 'Gaasbeek']},
                              {'parameter': 'exterior heat transfer coefficient slope', 'type': 'uniform',
                               'value': [1, 4]},
                              {'parameter': 'int climate', 'type': 'discrete', 'value': ['a', 'b']},
                              {'parameter': 'scale factor catch ratio', 'type': 'uniform', 'value': [0, 2]},
                              {'parameter': 'wall orientation', 'type': 'uniform', 'value': [0, 360]},
                              {'parameter': 'start year', 'type': 'discrete', 'value': 24},
                              {'parameter': 'brick dimension', 'type': 'uniform', 'value': [0.2, 0.5]},
                              ])

# Change dimensions of building component
# [first column/row of building component, last column/row of building component]
# - assign 'buildcomp = None' if no building components need to be changed
buildcomp = [1, 17]

# building component column/row which dimensions needs to be changed and discretised
# - assign 'buildcomp_elem = None' if no building components need to be changed
buildcomp_elem = 5

# 'column' if building componentis column, 'row' if building component is row
#  - assign 'dir_cr = None' if no building components need to be changed
dir_cr = 'column'

# Climate info
# Number of years that need to be extracted from the climate files to perform simulation for full duration
number_of_years = 7

# If wind driven rain is incluced in the simulations, use True.
# If wind driven rain is excluced in the simulations, use False (not recommended).
# Why would WP6 need this option?
simulate_wdrain = True

# Sampling details
# Where can I find info on what to use for WP6?
init_samples_per_set = 1  # Initial number of samples per replication
add_samples_per_run = 1  # Number of samples added if accuracy is not reached
max_samples = 500  # Maximum number of samples per replication
seq = 10  # Number of replications
SE_threshold = 0.1  # Targeted accuracy

# Specify the path to the Delphin executable
delphin_executable = 'C:\Program Files (x86)\IBK\Delphin 5.8\delphin_solver.exe'

"""
###############################################################################
# Run - no changes below this line
###############################################################################
"""

import os
from shark import autovar, sampling, supp, solver
import sys
import math as m
import numpy as np
from postproc_convergence import postprocess


def main():

    # Checks. If we are keeping this, then raise errors instead and log them
    if len(buildcomp) != 2 and buildcomp != None:
        print('ERROR: buildcomp has the wrong formatting, this should be [first column/row of building component, '
              'last column/row of building component]')
        sys.exit()

    if buildcomp != None and buildcomp_elem == None:
        print('ERROR: buildcomp is defined to change building component dimensions '
              'but the corresponding row/column was not defined by buildcomp_elem!')
        sys.exit()

    if buildcomp != None and dir_cr == None:
        print('ERROR: buildcomp is defined to change building component dimensions '
              'but the discretisation direction was not defined by dir_cr!')
        sys.exit()

    # Needs to be changed for WP6. We have to hook this up with the database
    path = {}
    # read project file path
    path['project'] = os.path.dirname(__file__)
    # read samples path
    path['samples'] = os.path.join(path['project'], 'Sampling scheme')

    # Generate samples and Delphin files
    new_samples_per_set = init_samples_per_set
    used_samples_per_set = 0

    # Write-out convergence
    conv = False
    # What is c?
    c = 0
    output = []

    while conv == False:
        print('Run %i' % c)
        print('Generating samples and Delphin files')

        # Upload sample file and files after looping
        for r in range(seq):
            print('Sequence %i' % r)

            # Generate samples
            samples_all = sampling.main(scenario=scenario, dist=distributions,
                                        runs=used_samples_per_set + new_samples_per_set, sets=1,
                                        strat='sobol convergence', path=path['samples'], seq=r)
            samples_new = samples_all[used_samples_per_set:]

            # Generate Delphin files
            # Rewrite to fit WP6 implementation
            if buildcomp != None:
                autovar.main(path, samples_new,
                             buildcomp={'component': buildcomp, 'cell': buildcomp_elem, 'dir': dir_cr},
                             number_of_years=number_of_years, intclimType=interior_climate_type,
                             simulRain=simulate_wdrain, seq=r, start_num=used_samples_per_set, feedback=False)
            else:
                autovar.main(path, samples_new, number_of_years=number_of_years, intclimType=interior_climate_type,
                             simulRain=simulate_wdrain,
                             seq=r, start_num=used_samples_per_set, feedback=False)

        # Wait until simulations ends
        # Run Delphin files
        run()

        # Postprocess
        ind_list = ['-%03i.' % i for i in range(1, used_samples_per_set + 1)]
        print('Reading and postprocessing output')
        output_dict = dict()

        for r in range(seq):
            print('Sequence %i' % r)
            output_dict[str(r)] = postprocess(seq=r, ind_list=ind_list)

        output = pd.concat(output_dict.values(), axis=1, keys=output_dict.keys())
        output = output.swaplevel(axis=1)

        # Cacluate mean, std and standard error
        print('Calculating standard error')

        SE = pd.DataFrame(index=['mean', 'std'])
        SE_dict = dict()

        for p in output.keys().levels[0]:
            se_mean = standardError(output[p], 'mean')
            se_std = standardError(output[p], 'std')
            se = pd.concat([se_mean, se_std], axis=1)
            SE_dict[p] = se

        SE = pd.concat(SE_dict.values(), axis=1, keys=SE_dict.keys())
        SE.to_excel('SE.xlsx')

        print(SE)

        used_samples_per_set += new_samples_per_set
        new_samples_per_set = add_samples_per_run
        c += 1

        if (SE.values < SE_threshold).all():
            conv = True

        if used_samples_per_set >= max_samples:
            print('Maximum number of samples reached: simulated %i samples per set' % used_samples_per_set)
            break

    # How do we monitor the progress in the simulation system?
    print('Done!')


# Rename to remove camel case
def standardError(x, param):
    # Isn't there an already existing function out there?
    # What is do?
    do = x.index.levels[0].tolist()
    # What is se_rel?
    se_rel = pd.DataFrame(index=do)

    for d in do:
        # q?
        q = x.loc[(d, param), :]
        mean_q = np.mean(q)
        # se_d?
        se_d = m.sqrt(1 / (seq * (seq - 1)) * sum([(x - mean_q) ** 2 for x in q]))

        # Isn't it better to check if mean_q is zero?
        try:
            # What is se_rel_d?
            se_rel_d = se_d / mean_q
        except ZeroDivisionError:
            se_rel_d = se_d

        se_rel.loc[d, param] = se_rel_d

    return se_rel


# Not interesting for WP6
def run():
    files = []
    for r in range(seq):
        path = os.path.join(os.path.dirname(__file__), 'Delphin files', 'Variations', str(r))
        files = files + supp.getFileList(path, '.dpj')[1]

    simstatus = solver.checkFinSim(files)
    print('%i files were already simulated succesfully, now simulating %i files' % (
        sum(simstatus), len(simstatus) - sum(simstatus)))
    simfiles = [x for i, x in enumerate(files) if not simstatus[i]]

    if simfiles:
        solver.main(delphin_executable, simfiles, feedback=False)


if __name__ == '__main__':
    __spec__ = None
    main()
