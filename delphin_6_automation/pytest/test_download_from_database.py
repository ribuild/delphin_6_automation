__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import codecs
import shutil
import pytest

# RiBuild Modules:
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import sampling_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry

# -------------------------------------------------------------------------------------------------------------------- #
# TEST


def test_download_results_1(add_results, tmpdir, test_folder):

    folder = tmpdir.mkdir('test')
    source_folder = tmpdir.mkdir('source')
    general_interactions.download_raw_result(add_results, folder)
    shutil.unpack_archive(test_folder + '/raw_results/delphin_results.zip', source_folder)

    source_cvode = open(os.path.join(source_folder, 'delphin_results/log/integrator_cvode_stats.tsv'), 'r').readlines()
    test_cvode = open(os.path.join(folder, f'{add_results}/log/integrator_cvode_stats.tsv'), 'r').readlines()
    assert test_cvode == source_cvode

    source_g6a = open(os.path.join(source_folder,
                                   'delphin_results/results/5a5479095d9460327c6970f0_2823182570.g6a'), 'r').readlines()
    test_g6a = open(os.path.join(folder,
                                 f'{add_results}/results/5a5479095d9460327c6970f0_2823182570.g6a'), 'r').readlines()
    assert test_g6a == source_g6a

    source_d6o = open(os.path.join(source_folder,
                                   'delphin_results/results/Surface relative humidity - left side, outdoor.d6o'),
                      'r').readlines()
    del source_d6o[3]
    test_d6o = open(os.path.join(folder,
                                 f'{add_results}/results/Surface relative humidity - left side, outdoor.d6o'),
                    'r').readlines()
    del test_d6o[3]
    assert test_d6o == source_d6o


def test_download_weather_1(db_one_project, test_folder, tmpdir):
    folder = tmpdir.mkdir('test')
    source_folder = test_folder + '/weather'

    # Setup
    delphin_doc = delphin_entry.Delphin.objects().first()
    weather_interactions.download_weather(delphin_doc, folder)

    def get_weather_files(path):
        files = []
        for file in ['short_wave_radiation.ccd', 'indoor_relative_humidity.ccd',
                     'indoor_temperature.ccd', 'long_wave_radiation.ccd', 'relative_humidity.ccd',
                     'temperature.ccd', 'wind_driven_rain.ccd', ]:
            file_obj = open(os.path.join(path, file), 'r')
            files.append(file_obj.readlines())
        return files

    # Get files
    test_files = get_weather_files(folder)
    source_files = get_weather_files(source_folder)

    # Assert
    assert test_files == source_files


@pytest.mark.skip('Weird error on Travis')
def test_download_materials_1(tmpdir, db_one_project, test_folder):

    folder = tmpdir.mkdir('test')
    delphin_doc = delphin_entry.Delphin.objects().first()
    material_interactions.download_materials(delphin_doc, folder)
    source_folder = os.path.join(test_folder, 'materials')

    def get_material_files(path):
        files = []
        for file in ['AltbauziegelDresdenZP_504.m6', 'LimeCementMortarHighCementRatio_717.m6', ]:
            file_path = os.path.join(path, file)
            files.append(codecs.open(file_path, "r", "utf-8").read().splitlines())
        return files

    # Get files
    test_files = get_material_files(folder)
    source_files = get_material_files(source_folder)

    # Assert
    assert test_files == source_files


def test_download_project_1(db_one_project, tmpdir):

    folder = tmpdir.mkdir('test')
    delphin_doc = delphin_entry.Delphin.objects().first()
    delphin_interactions.download_delphin_entry(delphin_doc, folder)

    assert os.path.isfile(os.path.join(folder,  f'{delphin_doc.id}.d6p'))


def test_download_sampling_strategy(add_sampling_strategy):

    strategy_id = sample_entry.Strategy.objects().first().id

    test_strategy = sampling_interactions.get_sampling_strategy(strategy_id)

    assert test_strategy
    assert isinstance(test_strategy, sample_entry.Strategy)
    assert isinstance(test_strategy.strategy, dict)
    assert all(element in list(test_strategy.strategy.keys())
               for element in ['scenario', 'distributions', 'settings'])
    #assert test_strategy['scenario']
    assert test_strategy.strategy['distributions']
    assert test_strategy.strategy['settings']
