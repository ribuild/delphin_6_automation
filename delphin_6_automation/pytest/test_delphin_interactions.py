__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import shutil

# RiBuild Modules
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import result_raw_entry
from delphin_6_automation.database_interactions.db_templates import result_processed_entry
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_download_project_1(db_one_project, tmpdir):

    folder = tmpdir.mkdir('test')
    delphin_doc = delphin_entry.Delphin.objects().first()
    delphin_interactions.download_delphin_entry(delphin_doc, folder)

    assert os.path.isfile(os.path.join(folder,  f'{delphin_doc.id}.d6p'))


def test_upload_project_1(delphin_file_path, empty_database, add_two_materials):
    """Test upload of delphin project without any weather"""

    delphin_interactions.upload_delphin_to_database(delphin_file_path, 10)

    assert len(delphin_entry.Delphin.objects()) == 1
    test_doc = delphin_entry.Delphin.objects().first()

    assert not test_doc.simulating
    assert test_doc.dimensions == 1
    assert isinstance(test_doc.dp6_file, dict)
    assert isinstance(test_doc.materials, list)
    assert not test_doc.weather
    assert not test_doc.indoor_climate
    assert not test_doc.results_raw
    assert not test_doc.simulated
    assert not test_doc.simulation_time


def test_upload_results_1(db_one_project, test_folder, tmpdir):
    temp_folder = tmpdir.mkdir('test')
    delphin_doc = delphin_entry.Delphin.objects().first()

    # Upload results
    result_zip = test_folder + '/raw_results/delphin_results.zip'
    shutil.unpack_archive(result_zip, temp_folder)
    os.rename(os.path.join(temp_folder, 'delphin_results'), os.path.join(temp_folder, str(delphin_doc.id)))
    result_id = delphin_interactions.upload_results_to_database(os.path.join(temp_folder, str(delphin_doc.id)))

    # Prepare test
    assert result_raw_entry.Result.objects()

    result_doc = result_raw_entry.Result.objects(id=result_id).first()
    delphin_doc.reload()

    # Assert
    assert result_doc.delphin == delphin_doc
    assert delphin_doc.results_raw == result_doc
    assert result_doc.results
    assert isinstance(result_doc.geometry_file, dict)
    assert result_doc.geometry_file_hash


def test_delphin_file_checker_1(delphin_file_path):

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    assert not delphin_interactions.check_delphin_file(delphin_dict)


def test_upload_project_2(delphin_file_path, empty_database, add_two_materials, add_three_years_weather):
    """Test upload of delphin project with weather"""

    id_ = delphin_interactions.upload_delphin_to_database(delphin_file_path, 10)
    weather_interactions.assign_weather_to_project(id_, add_three_years_weather)

    assert len(delphin_entry.Delphin.objects()) == 1
    test_doc = delphin_entry.Delphin.objects().first()

    assert not test_doc.simulating
    assert test_doc.dimensions == 1
    assert isinstance(test_doc.dp6_file, dict)
    assert isinstance(test_doc.materials, list)
    assert len(test_doc.weather) == 3
    assert not test_doc.indoor_climate
    assert not test_doc.results_raw
    assert not test_doc.simulated
    assert not test_doc.simulation_time


def test_upload_processed_results(add_results, tmpdir, test_folder):

    folder = tmpdir.mkdir('test')
    weather_folder = folder.mkdir('weather')
    result_zip = test_folder + '/raw_results/delphin_results1.zip'
    shutil.unpack_archive(result_zip, folder)
    shutil.copy(f'{test_folder}/weather/temperature.ccd', f'{weather_folder}/temperature.ccd')
    shutil.copy(f'{test_folder}/weather/indoor_temperature.ccd', f'{weather_folder}/indoor_temperature.ccd')
    result_doc = result_raw_entry.Result.objects().first()
    delphin_doc = delphin_entry.Delphin.objects().first()

    result_folder = os.path.join(folder, 'delphin_id')
    result_id = delphin_interactions.upload_processed_results(result_folder, delphin_doc.id, result_doc.id)

    result_doc.reload()
    delphin_doc.reload()

    process_result_doc = result_processed_entry.ProcessedResult.objects(id=result_id).first()
    assert process_result_doc
    assert process_result_doc.heat_loss
    assert process_result_doc.mould
    assert process_result_doc.algae
    assert process_result_doc.thresholds
    assert process_result_doc.u_value
    assert delphin_doc.result_processed == process_result_doc
    assert result_doc.result_processed == process_result_doc

