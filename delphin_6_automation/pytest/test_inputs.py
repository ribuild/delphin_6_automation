__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest
import pandas as pd
import os
import shutil

# RiBuild Modules
from delphin_6_automation.sampling import inputs
from delphin_6_automation.file_parsing import delphin_parser
from delphin_6_automation.delphin_setup import delphin_permutations

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_wall_core_materials(input_sets):
    materials = inputs.wall_core_materials(input_sets)

    assert materials
    assert isinstance(materials, list)
    assert all(isinstance(material_id, int)
               for material_id in materials)


def test_plaster_materials(input_sets):
    materials = inputs.plaster_materials(input_sets)

    assert materials
    assert isinstance(materials, list)
    assert all(isinstance(material_id, int)
               for material_id in materials)


def test_insulation(input_sets):
    materials = inputs.insulation_type(input_sets)

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


def test_insulation_systems(input_sets):

    systems = inputs.insulation_systems(input_sets, rows_to_read=2)

    assert isinstance(systems, pd.DataFrame)
    assert (11, 2) == systems.shape


def test_delphin_templates(test_folder):

    to_copy = inputs.delphin_templates(test_folder)

    assert isinstance(to_copy, dict)


def test_construct_delphin_reference(delphin_reference_folder):

    files = inputs.construct_delphin_reference(delphin_reference_folder)

    for file in files:
        assert os.path.exists(os.path.join(delphin_reference_folder, 'design', file))


def test_implement_system_materials(delphin_with_insulation, add_insulation_materials, dummy_systems, request):

    if '3' in request.node.name:
        index = 0
    else:
        index = 1

    delphin = inputs.implement_system_materials(delphin_with_insulation, dummy_systems.loc[index])
    layers = delphin_permutations.get_layers(delphin)

    for material_id in dummy_systems.loc[index, 'ID'].values:
        assert delphin_permutations.identify_layer(layers, str(material_id))


def test_implement_insulation_widths(delphin_with_insulation, add_insulation_materials, dummy_systems, request):

    if '3' in request.node.name:
        index = 0
        insulation_id = 39
    else:
        index = 1
        insulation_id = 187

    delphin_with_system_materials = inputs.implement_system_materials(delphin_with_insulation, dummy_systems.loc[index])

    permutated_dicts = inputs.implement_insulation_widths(delphin_with_system_materials, dummy_systems.loc[index])

    assert isinstance(permutated_dicts, list)
    insulation_widths = dummy_systems.loc[index, 'Dimension'].values.tolist()

    for i, delphin in enumerate(permutated_dicts):
        assert isinstance(delphin, dict)
        layers = delphin_permutations.get_layers(delphin)
        insulation_layer = delphin_permutations.identify_layer(layers, str(insulation_id))
        assert insulation_widths[i] * 10e-04 == insulation_layer['x_width']


def test_construct_design_files(mock_insulation_systems,
                                add_insulation_materials, delphin_reference_folder):

    file_names = inputs.construct_design_files(delphin_reference_folder)

    for file in file_names:
        assert os.path.exists(os.path.join(delphin_reference_folder, 'design', file))


def test_design_options(mock_insulation_systems,
                        add_insulation_materials, delphin_reference_folder):

    designs = inputs.design_options(delphin_reference_folder)

    assert isinstance(designs, list)

    for design in designs:
        assert isinstance(design, str)
        assert not design.endswith('.d6p')
