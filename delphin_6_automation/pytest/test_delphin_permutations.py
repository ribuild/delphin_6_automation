__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
from collections import OrderedDict
import os
import xmltodict

# RiBuild Modules:
from delphin_6_automation.database_interactions.auth import dtu_byg
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.delphin_setup import delphin_permutations
from delphin_6_automation.file_parsing import delphin_parser
import delphin_6_automation.database_interactions.mongo_setup as mongo_setup
import delphin_6_automation.pytest.pytest_helper_functions as helper

# -------------------------------------------------------------------------------------------------------------------- #
# TEST

mongo_setup.global_init(dtu_byg)


def test_get_layers_1():
    source_path = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    delphin_dict = delphin_parser.dp6_to_dict(source_path + '/delphin_project.d6p')
    delphin_layers = delphin_permutations.get_layers(delphin_dict)

    correct_layer_dict = {0: {'material': 'Lime Cement Plaster light [630]',
                              'x_width': 0.009999999999999998,
                              'x_index': (0, 6)},
                          1: {'material': 'Normal Brick [512]',
                              'x_width': 0.3499998,
                              'x_index': (7, 37)},
                          2: {'material': 'iQ-Fix [437]',
                              'x_width': 0.005,
                              'x_index': (45, 49)},
                          3: {'material': 'iQ-Therm [438]',
                              'x_width': 0.08,
                              'x_index': (50, 68)},
                          4: {'material': 'iQ-Top [726]',
                              'x_width': 0.009999999999999998,
                              'x_index': (69, 75)},
                          5: {'material': 'Restoration Render [210]',
                              'x_width': 0.010000000000000002,
                              'x_index': (38, 44)}
                          }
    assert delphin_layers == correct_layer_dict


def test_change_material_1():
    source_path = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    test_path, _ = helper.setup_test_folders()
    delphin_dict = delphin_parser.dp6_to_dict(source_path + '/delphin_project.d6p')
    new_material = OrderedDict((('@name', 'Aerated Concrete [6]'),
                                ('@color', '#ff404060'),
                                ('@hatchCode', '13'),
                                ('#text', '${Material Database}/AeratedConcrete_6.m6')))
    new_delphin = delphin_permutations.change_layer_material(delphin_dict, 'Normal Brick [512]', new_material)
    xmltodict.unparse(new_delphin, output=open(test_path + '/modified_delphin_project.d6p', 'w'), pretty=True)
    helper.clean_up_test_folders()

    assert new_delphin['DelphinProject']['Materials']['MaterialReference'][1] == new_material


def test_change_layer_width():
    source_path = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    test_path, _ = helper.setup_test_folders()
    delphin_dict = delphin_parser.dp6_to_dict(source_path + '/delphin_project.d6p')
    old_width = sum(delphin_permutations.convert_discretization_to_list(delphin_dict))

    new_delphin = delphin_permutations.change_layer_width(delphin_dict, 'Normal Brick [512]', 1.0)
    xmltodict.unparse(new_delphin, output=open(test_path + '/modified_delphin_project.d6p', 'w'), pretty=True)
    helper.clean_up_test_folders()

    assert sum(delphin_permutations.convert_discretization_to_list(new_delphin)) - old_width - 0.65 <= 0.002


def test_change_weather():
    source_path = os.path.dirname(os.path.realpath(__file__)) + '/test_files'
    test_path, _ = helper.setup_test_folders()
    delphin_dict = delphin_parser.dp6_to_dict(source_path + '/delphin_project.d6p')
    weather_path = os.path.dirname(os.path.realpath(__file__)) + '/test_files/temperature.ccd'
    new_delphin = delphin_permutations.change_weather(delphin_dict,
                                                      'Temp Out',
                                                      weather_path)
    xmltodict.unparse(new_delphin, output=open(test_path + '/modified_delphin_project.d6p', 'w'), pretty=True)
    helper.clean_up_test_folders()

    assert new_delphin['DelphinProject']['Conditions']['ClimateConditions']['ClimateCondition'][2]['Filename'] == weather_path
