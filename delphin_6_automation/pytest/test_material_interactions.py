__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest


# RiBuild Modules
from delphin_6_automation.database_interactions import material_interactions

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
