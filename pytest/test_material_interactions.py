__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest
import os
import codecs

# RiBuild Modules
from delphin_6_automation.database_interactions import material_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import material_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


@pytest.mark.parametrize('material_id', [504, 717])
def test_get_material_info(add_two_materials, material_id):

    material_info = material_interactions.get_material_info(material_id)

    assert material_info
    assert isinstance(material_info, dict)
    assert all(key in material_info.keys()
               for key in ['@name', '@color', '@hatchCode', '#text'])
    assert str(material_id) in material_info['@name']
    assert str(material_id) in material_info['#text']


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
            files.append(open(file_path, "r", encoding="utf-8").readlines())
        return files

    # Get files
    test_files = get_material_files(folder)
    source_files = get_material_files(source_folder)

    # Assert
    for index in range(len(test_files)):
        assert test_files[index] == source_files[index]


def test_upload_materials_1(test_folder, empty_database):
    # Local Files
    material_file = 'AltbauziegelDresdenZP_504.m6'

    # Upload
    material_interactions.upload_material_file(test_folder + '/materials/' + material_file)

    assert len(material_entry.Material.objects()) == 1

    material = material_entry.Material.objects().first()
    assert material.material_name == 'AltbauziegelDresdenZP'
    assert material.material_id == 504
    assert isinstance(material.material_data, dict)
