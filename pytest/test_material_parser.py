__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.file_parsing import material_parser
import shutil
import os
import pytest

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.mark.parametrize('mat', ['AltbauziegelDresdenZP_504.m6', 'LimeCementMortarHighCementRatio_717.m6'])
def test_parse_material(test_folder, tmpdir, mat):
    folder = tmpdir
    folder.mkdir('origin')
    file = os.path.join(folder, 'origin', mat)
    parsed_file = os.path.join(folder, mat)
    shutil.copyfile(os.path.join(test_folder, 'materials', mat), file)

    mat_dict = {'material_data': material_parser.material_file_to_dict(file)}
    material_parser.dict_to_m6(mat_dict, folder)

    with open(parsed_file, 'r') as pf:
        parsed_data = pf.readlines()

    with open(file, 'r') as f:
        data = f.readlines()

    assert parsed_data == data