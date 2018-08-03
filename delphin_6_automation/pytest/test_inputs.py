__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest
import pandas as pd

# RiBuild Modules
from delphin_6_automation.sampling import inputs
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_wall_core_materials():

    materials = inputs.wall_core_materials()

    assert materials
    assert isinstance(materials, list)
    assert all(isinstance(material_id, int)
               for material_id in materials)


def test_plaster_materials():

    materials = inputs.plaster_materials()

    assert materials
    assert isinstance(materials, list)
    assert all(isinstance(material_id, int)
               for material_id in materials)


def test_insulation():

    materials = inputs.insulation_type()

    assert materials
    assert isinstance(materials, list)
    assert all(isinstance(material_id, int)
               for sublist in materials
               for material_id in sublist)


def test_construction_types():

    constructions = inputs.construction_types()

    assert constructions
    assert isinstance(constructions, list)
    assert all([file.endswith('.d6p')
               for file in constructions])


def test_construct_design_options(add_five_materials):

    variations = inputs.construct_design_options()

    assert isinstance(variations, pd.DataFrame)

def test_insulation_systems():

    systems = inputs.insulation_systems()

    assert isinstance(systems, pd.DataFrame)

def test_delphin_templates():

    to_copy = inputs.delphin_templates()

    assert isinstance(to_copy, dict)

def test_construct_delphin_reference():

    inputs.construct_delphin_reference()


def test_implement_system_materials(delphin_with_insulation, add_five_materials):

    systems = inputs.insulation_systems()

    inputs.implement_system_materials(delphin_with_insulation, systems.loc[0])

def test_implement_insulation_widths(delphin_with_insulation, add_five_materials):

    systems = inputs.insulation_systems()

    delphin_with_system_materials = inputs.implement_system_materials(delphin_with_insulation, systems.loc[0])

    permutated_dicts = inputs.implement_insulation_widths(delphin_with_system_materials, systems.loc[0])

    assert  isinstance(permutated_dicts, list)

