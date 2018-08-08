__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
from collections import OrderedDict
import pytest
import xmltodict
import os

# RiBuild Modules:
from delphin_6_automation.delphin_setup import delphin_permutations
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# TEST


def test_get_layers_1(delphin_file_path):

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    delphin_layers = delphin_permutations.get_layers(delphin_dict)

    correct_layer_dict = {0: {'material': 'Lime cement mortar [717]',
                              'x_width': 0.012,
                              'x_index': (0, 7)},

                          1: {'material': 'Old Building Brick Dresden ZP [504]',
                              'x_width': 0.3479997,
                              'x_index': (8, 38)},

                          2: {'material': 'Lime cement mortar [717]',
                              'x_width': 0.012,
                              'x_index': (39, 46)},
                          }
    assert delphin_layers == correct_layer_dict


def test_change_material_1(delphin_file_path):
    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)

    new_material = OrderedDict((('@name', 'Aerated Concrete [6]'),
                                ('@color', '#ff404060'),
                                ('@hatchCode', '13'),
                                ('#text', '${Material Database}/AeratedConcrete_6.m6')))

    new_delphin = delphin_permutations.change_layer_material(delphin_dict,
                                                             'Old Building Brick Dresden ZP [504]',
                                                             new_material)

    assert new_delphin['DelphinProject']['Materials']['MaterialReference'][1] == new_material


@pytest.mark.parametrize('width', [0.1, 0.3, 0.5, 0.75, 1.0])
def test_change_layer_width(delphin_file_path, width):

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    new_delphin = delphin_permutations.change_layer_width(delphin_dict, 'Old Building Brick Dresden ZP [504]', width)
    new_width = delphin_permutations.get_layers(new_delphin)[1]['x_width']

    assert width == pytest.approx(new_width)


def test_change_weather(test_folder, delphin_file_path):

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    weather_path = test_folder + '/weather/temperature.ccd'
    new_delphin = delphin_permutations.change_weather(delphin_dict,
                                                      'exterior temperature',
                                                      weather_path)
    new_weather = new_delphin['DelphinProject']['Conditions']['ClimateConditions']['ClimateCondition'][0]['Filename']

    assert new_weather == weather_path


@pytest.mark.parametrize('orientation',
                         [0, 15, 30, 45, 90, 180, 220, 300, 360, 0.3, 23.56])
def test_change_orientation(delphin_file_path, orientation):

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    new_delphin = delphin_permutations.change_orientation(delphin_dict, orientation)
    new_orientation = new_delphin['DelphinProject']['Conditions'][
        'Interfaces']['Interface'][0]['IBK:Parameter']['#text']

    assert new_orientation == str(orientation)


@pytest.mark.parametrize('orientation',
                         [-10, 430])
@pytest.mark.xfail()
def test_change_orientation_fail(delphin_file_path, orientation):

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    new_delphin = delphin_permutations.change_orientation(delphin_dict, orientation)
    new_orientation = new_delphin['DelphinProject']['Conditions'][
        'Interfaces']['Interface'][0]['IBK:Parameter']['#text']

    assert new_orientation == str(orientation)


@pytest.mark.parametrize('coefficient',
                         [0.3, 10, 20])
def test_change_coefficient_1(delphin_file_path, coefficient):

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    new_delphin = delphin_permutations.change_boundary_coefficient(delphin_dict,
                                                                   'IndoorHeatConduction',
                                                                   'ExchangeCoefficient',
                                                                   coefficient)

    assert new_delphin['DelphinProject']['Conditions']['BoundaryConditions'][
               'BoundaryCondition'][5]['IBK:Parameter']['#text'] == str(coefficient)


@pytest.mark.parametrize('coefficient',
                         [0.3, 10**-6, 20])
@pytest.mark.parametrize('sd_value',
                         [0.3, 10, 20])
def test_change_coefficient_2(delphin_file_path, coefficient, sd_value):

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    delphin_permutations.change_boundary_coefficient(delphin_dict, 'IndoorVaporDiffusion',
                                                                   'ExchangeCoefficient', coefficient)
    new_delphin = delphin_permutations.change_boundary_coefficient(delphin_dict, 'IndoorVaporDiffusion',
                                                                   'SDValue', sd_value)

    assert new_delphin['DelphinProject']['Conditions']['BoundaryConditions'][
               'BoundaryCondition'][6]['IBK:Parameter'][0]['#text'] == str(coefficient)
    assert new_delphin['DelphinProject']['Conditions']['BoundaryConditions'][
               'BoundaryCondition'][6]['IBK:Parameter'][1]['#text'] == str(sd_value)


def test_get_simulation_length(delphin_file_path):

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    length = delphin_permutations.get_simulation_length(delphin_dict)

    assert length == (4, 'a')


@pytest.mark.parametrize('length',
                         [0, 0.5, 3, 10])
@pytest.mark.parametrize('value',
                         ['a', 'h'])
def test_change_simulation_length(delphin_file_path, length, value):

    delphin_dict = delphin_parser.dp6_to_dict(delphin_file_path)
    modified_dict = delphin_permutations.change_simulation_length(delphin_dict, length, value)

    assert delphin_permutations.get_simulation_length(modified_dict) == (length, value)


@pytest.mark.parametrize('width', [0.1, 0.3, 0.5])
def test_update_output_locations(delphin_with_insulation, width, request):

    delphin_permutations.change_layer_width(delphin_with_insulation,
                                            'Old Building Brick Dresden ZP [504]',
                                            width)
    delphin_permutations.update_output_locations(delphin_with_insulation)

    x_steps = delphin_permutations.convert_discretization_to_list(delphin_with_insulation)
    for assignment in delphin_with_insulation['DelphinProject']['Assignments']['Assignment']:
        if assignment['@type'] == 'Output':
            if assignment['Reference'].endswith('algae'):
                assert assignment['IBK:Point3D'] == '0.0005 0.034 0'

            elif assignment['Reference'].endswith('frost'):
                assert assignment['IBK:Point3D'] == '0.005 0.034 0'

            elif assignment['Reference'] == 'heat loss':
                assert assignment['Range'] == f'{len(x_steps)-1} 0 {len(x_steps)-1} 0'

            elif assignment['Reference'].endswith('interior surface'):
                if 'exterior' not in request.node.name and 'insulated' not in request.node.name:
                    correct_width = width + 0.0125
                elif 'exterior' in request.node.name and 'insulated' in request.node.name:
                    correct_width = width + 0.0685
                elif 'interior' in request.node.name and 'insulated' in request.node.name:
                    correct_width = width + 0.0565
                else:
                    correct_width = width + 0.0245
                found_location = float(assignment['IBK:Point3D'].split(' ')[0])
                assert pytest.approx(found_location) == correct_width

            elif assignment['Reference'].endswith('mould'):
                if 'exterior' not in request.node.name and 'insulated' not in request.node.name:
                    correct_width = width + 0.0005
                elif 'exterior' in request.node.name and 'insulated' in request.node.name:
                    correct_width = width + 0.0245
                else:
                    correct_width = width + 0.0125
                found_location = float(assignment['IBK:Point3D'].split(' ')[0])
                assert pytest.approx(found_location) == correct_width


@pytest.mark.parametrize('change_to', [True, False])
def test_change_kirchhoff_potential(delphin_file_path, change_to):

    delphin_project = delphin_parser.dp6_to_dict(delphin_file_path)
    delphin_permutations.change_kirchhoff_potential(delphin_project, change_to)

    kirchhoff = delphin_project['DelphinProject']['Init']['SimulationParameter']['IBK:Flag']['#text']

    if kirchhoff == 'false':
        assert not change_to

    elif kirchhoff == 'true':
        assert change_to


@pytest.mark.parametrize('rel_tol', [1e-05, 1e-04, 1e-03])
def test_change_solver_relative_tolerance(delphin_file_path, rel_tol):

    delphin_project = delphin_parser.dp6_to_dict(delphin_file_path)
    delphin_permutations.change_solver_relative_tolerance(delphin_project, rel_tol)

    solver_tol = float(delphin_project['DelphinProject']['Init']['SolverParameter']['IBK:Parameter']['#text'])

    assert solver_tol == rel_tol
