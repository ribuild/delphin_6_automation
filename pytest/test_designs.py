import os
import pytest
from delphin_6_automation.file_parsing import delphin_parser


@pytest.fixture()
def files():
    folder = r"C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\wp6_v2\inputs\design"

    file1 = "1d_exterior_PhenolicFoam_689_599_20.d6p"
    path1 = os.path.join(folder, file1)
    file2 = "1d_exterior_PhenolicFoam_689_599_20_SD00.d6p"
    path2 = os.path.join(folder, file2)

    yield path1, path2


def test_file_design(files):
    path1, path2 = files

    with open(path1, 'r') as file:
        data1 = file.read()

    with open(path2, 'r') as file:
        data2 = file.read()

    assert data1 == data2


def test_dict_design(files):
    path1, path2 = files
    dd1 = delphin_parser.dp6_to_dict(path1)
    dd2 = delphin_parser.dp6_to_dict(path2)
    del dd1['DelphinProject']['ProjectInfo']
    del dd2['DelphinProject']['ProjectInfo']

    for key in dd2['DelphinProject'].keys():
        equal = dd1['DelphinProject'][key] == dd2['DelphinProject'][key]
        assert equal

    #assert dd1['DelphinProject'] == dd2['DelphinProject']
