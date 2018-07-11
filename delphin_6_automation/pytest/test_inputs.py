__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest

# RiBuild Modules
from delphin_6_automation.sampling import inputs

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_wall_core_materials():

    materials = inputs.wall_core_materials()

    assert materials
    assert isinstance(materials, list)
    assert all(isinstance(material_id, int)
               for material_id in materials)


@pytest.mark.skip('Not yet implemented')
def test_plaster_materials():

    materials = inputs.plaster_materials()

    assert materials
    assert isinstance(materials, list)
    assert all(isinstance(material_id, int)
               for material_id in materials)


@pytest.mark.skip('Not yet implemented')
def test_insulation():

    materials = inputs.insulation_type()

    assert materials
    assert isinstance(materials, list)
    assert all(isinstance(material_id, int)
               for material_id in materials)


def test_construction_types():

    constructions = inputs.construction_types()

    assert constructions
    assert isinstance(constructions, list)
    assert all([file.endswith('.d6p')
               for file in constructions])