__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [10, 5]
import datetime

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import result_processed_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions import simulation_interactions
from delphin_6_automation.backend import result_extraction


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

def get_time(projects):
    time = []
    for p in projects:
        time.append(p.simulation_time)

    return np.array(time) / 60


def get_simulation_time():
    filtered_entries = delphin_entry.Delphin.objects(simulated__exists=True).only('simulation_time')
    gt_250 = filtered_entries.filter(simulation_time__gt=15000)
    sim_time = get_time(filtered_entries)

    return {
        'min': np.min(sim_time),
        'q25': np.quantile(sim_time, 0.25),
        'mean': np.mean(sim_time),
        'median': np.quantile(sim_time, 0.50),
        'q75': np.quantile(sim_time, 0.75),
        'q95': np.quantile(sim_time, 0.95),
        'max': np.max(sim_time),
        'gt_250': gt_250.count()
    }


def get_simulation_time_plot():
    filtered_entries = delphin_entry.Delphin.objects(simulated__exists=True).only('simulation_time')
    sim_time = get_time(filtered_entries)
    hist, edges = np.histogram(sim_time, density=True, bins=200)
    dx = edges[1] - edges[0]
    cdf = np.cumsum(hist) * dx

    plt.figure(figsize=(10, 5))
    plt.plot(edges[1:], cdf, color='darkslateblue')
    plt.axvline(x=np.mean(sim_time), linestyle=':', color='k', label='Mean')
    plt.axvline(x=np.median(sim_time), linestyle='--', color='k', label='Median')
    plt.title('Simulation Time')
    plt.xlabel('Simulation Time in Minutes')
    plt.ylabel('Ratio of Simulations')
    plt.legend()
    plt.xlim(-5, 260)
    plt.show()


def get_actual_average_simulation_time():
    start_time = delphin_entry.Delphin.objects(simulated__exists=True).only('simulated').order_by('simulated').first()['simulated']
    delta_time = (datetime.datetime.now() - start_time).total_seconds()/60

    return delta_time/get_simulated_projects_count()


def get_convergence_mould():
    strategy = sample_entry.Strategy.objects().only('standard_error').first()

    mould = []

    for design in strategy.standard_error:
        mould.append(strategy.standard_error[design]['mould'])

    mould = np.array(mould)

    mould_avg = np.nanmean(mould, axis=0)
    mould_min = np.nanmin(mould, axis=0)
    mould_max = np.nanmax(mould, axis=0)
    x = np.arange(0, len(mould_avg))

    plt.figure(figsize=(10, 5))
    plt.plot(x, mould_avg, color='k', label='Average Absolute Error')
    plt.fill_between(x, mould_min, mould_max, alpha=0.7, color='firebrick', label='Max-Min Absolute Error')

    plt.axhline(y=0.01, linestyle=':', color='k', label='Convergence Criteria')
    plt.ylabel('Absolute Error')
    plt.xlabel('Sample Iteration')
    plt.title('Convergence - Mould')
    plt.legend()

    plt.show()


def get_convergence_heatloss():
    strategy = sample_entry.Strategy.objects().only('standard_error').first()

    hl = []

    for design in strategy.standard_error:
        hl.append(strategy.standard_error[design]['heat_loss'])

    hl = np.array(hl)

    hl_avg = np.nanmean(hl, axis=0)
    hl_min = np.nanmin(hl, axis=0)
    hl_max = np.nanmax(hl, axis=0)
    x = np.arange(0, len(hl_avg))

    plt.figure(figsize=(10, 5))
    plt.plot(x, hl_avg, color='k', label='Average Absolute Error')
    plt.fill_between(x, hl_min, hl_max, alpha=0.7, color='darkslateblue', label='Max-Min Absolute Error')

    plt.axhline(y=0.01, linestyle=':', color='k', label='Convergence Criteria')
    plt.ylabel('Absolute Error')
    plt.xlabel('Sample Iteration')
    plt.title('Convergence - Heat Loss')
    plt.legend()

    plt.show()


def get_mould_cdf():
    results = result_processed_entry.ProcessedResult.objects.only('thresholds.mould')
    x, y = compute_cdf(results, 'mould')

    plt.figure(figsize=(10, 5))
    plt.plot(x, y)
    plt.title('CDF - Mould')
    plt.xlabel('Mould Index')
    plt.ylabel('Ratio')
    #plt.show()


def get_heatloss_cdf():
    results = result_processed_entry.ProcessedResult.objects.only('thresholds.heat_loss')
    x, y = compute_cdf(results, 'heat_loss')

    plt.figure(figsize=(10, 5))
    plt.plot(x, y)
    plt.title('CDF - Heat Loss')
    plt.xlabel('Wh')
    plt.ylabel('Ratio')
    plt.show()


def compute_cdf(results: list, quantity: str):
    quantities = [doc.thresholds[quantity] for doc in results]
    hist, edges = np.histogram(quantities, density=True, bins=50)
    dx = edges[1] - edges[0]
    cdf = np.cumsum(hist) * dx

    return edges[1:], cdf


def get_simulated_projects_count():
    return delphin_entry.Delphin.objects(simulated__exists=True).count()


def get_simulation_years():
    pass


def save_plot():
    pass
