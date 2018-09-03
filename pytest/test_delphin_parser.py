__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import shutil
import os
import pytest

# RiBuild Modules
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_cvode_stats(test_folder, tmpdir):
    temp_folder = tmpdir.mkdir('test')
    result_zip = test_folder + '/raw_results/delphin_results.zip'
    shutil.unpack_archive(result_zip, temp_folder)
    integrator_dict = delphin_parser.cvode_stats_to_dict(os.path.join(temp_folder,
                                                                      'delphin_results/log'))

    assert isinstance(integrator_dict, dict)


def test_d6o_to_dict(result_files, request):

    for file in os.listdir(result_files):
        if file.endswith('.d6o'):
            if '4' not in request.node.name:
                result, meta = delphin_parser.d6o_to_dict(result_files, file)
                assert isinstance(result, list)
                assert isinstance(meta, dict)
            else:
                result, meta = delphin_parser.d6o_to_dict(result_files, file, 7*8760)
                assert isinstance(result, list)
                assert len(result) == 7 * 8760
                assert isinstance(meta, dict)


@pytest.mark.parametrize('number', [0, 1, 2])
def test_restart_to_dict(test_folder, number):

    restart_folder = os.path.join(test_folder, 'restart', f'var_{number}')

    data = delphin_parser.restart_data(restart_folder)

    assert data
    assert isinstance(data, dict)

    for element in data.values():
        assert isinstance(element, bytes) or element is None


@pytest.mark.parametrize('number', [0, 1, 2])
def test_restart_data_to_file(test_folder, number, tmpdir):
    folder = tmpdir.mkdir('test')

    restart_folder = os.path.join(test_folder, 'restart', f'var_{number}')
    data = delphin_parser.restart_data(restart_folder)

    delphin_parser.restart_data_to_file(folder, data)

    bin_file = os.path.join(folder, 'restart.bin')
    tmp_file = os.path.join(folder, 'restart.bin.tmp')

    assert os.path.exists(bin_file)
    assert delphin_parser.restart_data(folder) == data

    if data['tmp_data']:
        assert os.path.exists(tmp_file)
