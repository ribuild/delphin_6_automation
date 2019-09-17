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
from scipy.optimize import curve_fit

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

figure_size = (20, 10)

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

    plt.figure(figsize=figure_size)
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

    return get_simulated_projects_count()/delta_time


def get_convergence_mould():
    strategy = sample_entry.Strategy.objects().only('standard_error').first()

    mould = []

    for design in strategy.standard_error:
        mould.append(strategy.standard_error[design]['mould'])

    mould = np.array(mould)

    mould_avg = np.nanmean(mould, axis=0)
    mould_min = np.nanmin(mould, axis=0)
    mould_max = np.nanmax(mould, axis=0)
    mould_q25 = np.nanquantile(mould, 0.25, axis=0)
    mould_q50 = np.nanquantile(mould, 0.50, axis=0)
    mould_q75 = np.nanquantile(mould, 0.75, axis=0)
    x = np.arange(0, len(mould_avg))

    plt.figure(figsize=figure_size)
    plt.plot(x, mould_avg, color='k', label='Average Absolute Error')
    plt.plot(x, mould_q25, color='#721616', label='Q25 Absolute Error')
    plt.plot(x, mould_q50, color='#d73030', label='Median Absolute Error')
    plt.plot(x, mould_q75, color='#db4545', label='Q75 Absolute Error')
    plt.fill_between(x, mould_min, mould_max, alpha=0.7, color='firebrick', label='Max-Min Absolute Error')

    plt.axhline(y=0.1, linestyle=':', color='k', label='Convergence Criteria - 10%')
    plt.ylabel('Absolute Error')
    plt.xlabel('Sample Iteration')
    plt.title('Convergence - Mould')
    plt.legend()

    plt.show()

    return {
        'min': mould_min,
        'q25': mould_q25,
        'mean': mould_avg,
        'median': mould_q50,
        'q75': mould_q75,
        'max': mould_max,
    }


def get_convergence_heatloss(mode=None):
    strategy = sample_entry.Strategy.objects().only('standard_error').first()

    hl = []

    for design in strategy.standard_error:
        hl.append(strategy.standard_error[design]['heat_loss'])

    hl = np.array(hl)

    hl_avg = np.nanmean(hl, axis=0)
    hl_min = np.nanmin(hl, axis=0)
    hl_max = np.nanmax(hl, axis=0)
    hl_q25 = np.nanquantile(hl, 0.25, axis=0)
    hl_q50 = np.nanquantile(hl, 0.50, axis=0)
    hl_q75 = np.nanquantile(hl, 0.75, axis=0)
    x = np.arange(0, len(hl_avg))

    plt.figure(figsize=figure_size)
    plt.plot(x, hl_avg, color='k', label='Average Absolute Error')
    plt.plot(x, hl_q25, color='#0000b3', label='Q25 Absolute Error')
    plt.plot(x, hl_q50, color='#3333ff', label='Median Absolute Error')
    plt.plot(x, hl_q75, color='#4d4dff', label='Q75 Absolute Error')
    plt.fill_between(x, hl_min, hl_max, alpha=0.7, color='darkslateblue', label='Max-Min Absolute Error')

    plt.axhline(y=0.1, linestyle=':', color='k', label='Convergence Criteria - 10%')
    plt.ylabel('Absolute Error')
    plt.xlabel('Sample Iteration')
    plt.title('Convergence - Heat Loss')

    if not mode:
        plt.ylim(-0.5, 1.2)

    plt.legend()

    plt.show()

    return {
        'min': hl_min,
        'q25': hl_q25,
        'mean': hl_avg,
        'median': hl_q50,
        'q75': hl_q75,
        'max': hl_max,
    }


def get_mould_cdf():
    results = result_processed_entry.ProcessedResult.objects.only('thresholds.mould')
    x, y = compute_cdf(results, 'mould')

    plt.figure(figsize=figure_size)
    plt.plot(x, y)
    plt.title('Cumulative Distribution Function\nMould')
    plt.xlabel('Mould Index')
    plt.ylabel('Ratio')
    #plt.show()


def get_heatloss_cdf():
    results = result_processed_entry.ProcessedResult.objects.only('thresholds.heat_loss')
    x, y = compute_cdf(results, 'heat_loss')

    plt.figure(figsize=figure_size)
    plt.plot(x, y)
    plt.title('Cumulative Distribution Function\nHeat Loss')
    plt.xlabel('Wh')
    plt.ylabel('Ratio')
    plt.xlim(0, 1.3*10**8)
    #plt.show()


def compute_cdf(results: list, quantity: str):
    quantities = [doc.thresholds[quantity] for doc in results]
    hist, edges = np.histogram(quantities, density=True, bins=50)
    dx = edges[1] - edges[0]
    cdf = np.cumsum(hist) * dx

    return edges[1:], cdf


def get_simulated_projects_count():
    return delphin_entry.Delphin.objects(simulated__exists=True).count()


def estimate_future_convergence(data, dmg_model, max_):
    def curve_func(x, a, b):
        return a * x + b

    plt.figure(figsize=figure_size)
    plt.title(f'Convergence Estimation\n{dmg_model.upper()}')
    colors = {'mould': {'mean': 'k', 'q25': '#721616', 'median': '#d73030', 'q75': '#db4545'},
              'heat loss': {'mean': 'k', 'q25': '#0000b3', 'median': '#3333ff', 'q75': '#4d4dff'}}
    for key in data.keys():
        if key in ['min', 'max']:
            continue
        else:
            popt, pcov = curve_fit(curve_func, np.arange(0, len(data[key])), data[key])
            xdata = np.linspace(0, max_)
            plt.plot(xdata, curve_func(xdata, *popt), colors[dmg_model][key], label=f'{key.upper()}')
    plt.legend()