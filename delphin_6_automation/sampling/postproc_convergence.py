# -*- coding: utf-8 -*-
"""
Example of how to use shark to for probabilistic Monte-Carlo simulations with DELPHIN 5.8.
===============================================================================
2018-05-04

This script contains functions to postprocess the output of Delphin simulations when monitoring the convergence.
"""

from shark import supp, dpm


def exclude_files():
    """ Define which output files are not necessary for postprocessing """
    return ['cap_press']

# What is X? Needs renaming
def calc_heatloss(X):

    """ Calculate heatloss through building component """

    # 'heatflux' is the name of the output file (underscores and dashes are removed)
    # [1:] means we exclude the first output time step - this depends on the way the output files and
    # output grids are defined
    # rename Q to heat loss
    Q = list(X['heatflux'])[1:]

    # substract last heatflux Q[-1] from first heatflux Q[0]
    # to get total heat loss over whole period (defined by output grid)
    # Is this needed? It might be implemented different in WP6
    dQ = abs(Q[-1] - Q[0])

    return dQ

# What is X? Needs renaming
# Not needed for WP6
def calc_frost(X):

    """ Calculate moist freeze-thaw cycles """

    # 'temperature' is the name of the output file (underscores and dashes are removed)
    # [:,1] means we select the second column of the output file (note that python indexing starts from 0)
    # - see output file for which column is needed
    # [1:] means we exclude the first output time step
    # - this depends on the way the output files and output grids are defined
    # Renaming
    T = list(X['temperature'][:, 1])[1:]

    # 'relhum' is the name of the output file (underscores and dashes are removed)
    # [:,1] means we select the second column of the output file (note that python indexing starts from 0)
    # - see output file for which column is needed
    # [1:] means we exclude the first output time step
    # - this depends on the way the output files and output grids are defined
    # Renaming
    RH = list(X['relhum'][:, 1])[1:]

    # 'moistmass' is the name of the output file (underscores and dashes are removed)
    # [:,0] means we select the first column of the output file (note that python numbering starts from 0)
    #  - see output file for which column is needed
    # [1:] means we exclude the first output time step
    # - this depends on the way the output files and output grids are defined
    # Renaming
    W = list(X['moistmass'][:, 0])[1:]

    wperc = 0.25  # define critical degree of saturation at which damage occurs
    mft = dpm.freezeThawCyclesDTU(T, RH, W, wperc)[1]
    # Calculate moist freeze-thaw cycles
    # freezeThawCyclesDTU(...)[1] return the moist freeze-thaw cycles, freezeThawCyclesDTU(...)[0] would return the freeze-thaw cycles
    return mft


# Not needed for WP6
def calc_mould_surf(X):
    """ Calculate mould growth on interior surface """
    sens_class = 'vs'  # sensitivity class
    T = list(X['temperature'][:, 4])[1:]
    # 'temperature' is the name of the output file (underscores and dashes are removed)
    # [:,4] means we select the fifth column of the output file (note that python indexing starts from 0) - see output file for which column is needed
    # [1:] means we exclude the first output time step - this depends on the way the output files and output grids are defined
    RH = list(X['relhum'][:, 4])[1:]
    # 'relhum' is the name of the output file (underscores and dashes are removed)
    # [:,4] means we select the fifth column of the output file (note that python indexing starts from 0) - see output file for which column is needed
    # [1:] means we exclude the first output time step - this depends on the way the output files and output grids are defined
    mi = dpm.mouldVTTupdate(T, RH, sens_class, C_eff=1)
    # Calculate mould index
    return mi


# Not needed for WP6
def calc_mould_interf(X):
    """ Calculate mould growth on interface between masonry and insulation """
    sens_class = 'mr'  # sensitivity class
    T = list(X['temperature'][:, 3])[1:]
    # 'temperature' is the name of the output file (underscores and dashes are removed)
    # [:,3] means we select the fourth column of the output file (note that python indexing starts from 0) - see output file for which column is needed
    # [1:] means we exclude the first output time step - this depends on the way the output files and output grids are defined
    RH = list(X['relhum'][:, 3])[1:]
    # 'relhum' is the name of the output file (underscores and dashes are removed)
    # [:,3] means we select the fourth column of the output file (note that python indexing starts from 0) - see output file for which column is needed
    # [1:] means we exclude the first output time step - this depends on the way the output files and output grids are defined
    mi = dpm.mouldVTTupdate(T, RH, sens_class, C_eff=1)
    # Calculate mould index
    return mi


# Not needed for WP6
def calc_wooddecay(X):
    """ Calculate wood decay at wooden beam ends """
    T = list(X['temperature'][:, 2])[1:]
    # 'temperature' is the name of the output file (underscores and dashes are removed)
    # [:,2] means we select the third column of the output file (note that python indexing starts from 0) - see output file for which column is needed
    # [1:] means we exclude the first output time step - this depends on the way the output files and output grids are defined
    RH = list(X['relhum'][:, 2])[1:]
    # 'relhum' is the name of the output file (underscores and dashes are removed)
    # [:,2] means we select the third column of the output file (note that python indexing starts from 0) - see output file for which column is needed
    # [1:] means we exclude the first output time step - this depends on the way the output files and output grids are defined
    ml = dpm.woodDecayVTT(T, RH)
    # Calculate wood mass loss
    return ml


"""
###############################################################################
# Postprocess - No changes required below this point if the same outputs are monitored
###############################################################################
"""

import os
import pandas as pd
import numpy as np
import multiprocessing


# TODO - WP6: post process and upload to database
def postprocess(seq, ind_list=[]):
    # seq - sequence?
    # ind_list ?

    # Read output files
    exclude = exclude_files() + ind_list
    path = os.path.join(os.path.dirname(__file__), 'Delphin files', 'Output', str(seq))

    output_raw = supp.readOutput(path, exclude=exclude)[0]

    damage_patterns = ['heatloss', 'frost', 'mould index surface', 'mould index interface', 'wood mass loss beam']

    file = os.path.join(path, 'Output_proc')
    do = output_raw.index.levels[0].tolist()
    try:
        output_proc = pd.read_pickle(file)
    except FileNotFoundError:
        output_proc = pd.DataFrame(index=do, columns=damage_patterns)

    num_cores = min(multiprocessing.cpu_count() - 1, len(damage_patterns))
    pool = multiprocessing.Pool(num_cores)
    args = [(do, p, output_proc.loc[:, p], output_raw) for p in damage_patterns]
    results = pool.map(processOutput, args)
    pool.close()
    pool.join()

    output_proc_new = pd.concat([x[0] for x in results], axis=1)
    output = pd.concat([x[1] for x in results], axis=1)

    output_proc_new.to_pickle(file)

    output.to_excel(os.path.join(path, 'output' + str(seq) + '.xlsx'))

    return output


# TODO - WP6 Threshold function
def processOutput(args):
    do, p, output_proc, output_raw = args

    idc = ['mean', 'std'] * len(do)
    tuples = list(zip(*[np.repeat(do, 2), idc]))
    output = pd.DataFrame(index=pd.MultiIndex.from_tuples(tuples))

    output_proc_new = pd.DataFrame(index=do, columns=[p])

    for d in do:
        X = output_proc.loc[d]
        if np.isnan(X).all():
            X = list()
        for ind, row in output_raw.iterrows():
            if ind[0] == d:
                if p == 'heatloss':
                    X.append(calc_heatloss(row))
                    continue
                if p == 'frost':
                    X.append(calc_frost(row))
                    continue
                if p == 'mould index surface':
                    X.append(max(calc_mould_surf(row)))
                    continue
                if p == 'mould index interface':
                    X.append(max(calc_mould_interf(row)))
                    continue
                if p == 'wood mass loss beam':
                    X.append(max(calc_wooddecay(row)))
                    continue

        output_proc_new.loc[d, p] = X

        output.loc[(d, 'mean'), p] = np.mean(X)
        output.loc[(d, 'std'), p] = np.std(X)

    return output_proc_new, output
