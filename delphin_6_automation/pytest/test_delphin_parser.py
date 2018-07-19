__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import shutil
import os

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
