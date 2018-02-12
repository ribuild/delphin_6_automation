__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
from collections import OrderedDict

import xmltodict
from delphin_6_automation.database_interactions.auth import dtu_byg

import delphin_6_automation.database_interactions.mongo_setup as mongo_setup
import delphin_6_automation.pytest.pytest_helper_functions as helper
# RiBuild Modules:
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.delphin_setup import delphin_permutations
from delphin_6_automation.file_parsing import delphin_parser

# -------------------------------------------------------------------------------------------------------------------- #
# TEST

mongo_setup.global_init(dtu_byg)

# TODO - Update test permutations

def test_get_layers_1():
    id_ = "5a5479095d9460327c6970f0"
    test_path, source_path = helper.setup_test_folders()
    delphin_interactions.download_delphin_entry(id_, test_path)
    delphin_dict = delphin_parser.dp6_to_dict(test_path + '/' + id_ + '.d6p')
    delphin_layers = delphin_permutations.get_layers(delphin_dict)
    helper.clean_up_test_folders()

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
    id_ = "5a5479095d9460327c6970f0"
    test_path, source_path = helper.setup_test_folders()
    delphin_interactions.download_delphin_entry(id_, test_path)
    delphin_dict = delphin_parser.dp6_to_dict(test_path + '/' + id_ + '.d6p')
    new_material = OrderedDict((('@name', 'Aerated Concrete [6]'),
                                ('@color', '#ff404060'),
                                ('@hatchCode', '13'),
                                ('#text', '${Material Database}/AeratedConcrete_6.m6')))
    new_delphin = delphin_permutations.change_layer_material(delphin_dict, 'Normal Brick [512]', new_material)
    xmltodict.unparse(new_delphin, output=open(test_path + '/' + id_ + '.d6p', 'w'), pretty=True)
    helper.clean_up_test_folders()


def test_change_layer_width():
    id_ = "5a5479095d9460327c6970f0"
    test_path, source_path = helper.setup_test_folders()
    delphin_interactions.download_delphin_entry(id_, test_path)
    delphin_dict = delphin_parser.dp6_to_dict(test_path + '/' + id_ + '.d6p')
    old_width = sum(delphin_permutations.convert_discretization_to_list(delphin_dict))
    new_delphin = delphin_permutations.change_layer_width(delphin_dict, 'Normal Brick [512]', 1.0)
    xmltodict.unparse(new_delphin, output=open(test_path + '/' + id_ + '_test.d6p', 'w'), pretty=True)
    helper.clean_up_test_folders()
    assert sum(delphin_permutations.convert_discretization_to_list(new_delphin)) - old_width - 0.65 <= 0.002


def test_change_weather():
    id_ = "5a5479095d9460327c6970f0"
    test_path, source_path = helper.setup_test_folders()
    delphin_interactions.download_delphin_entry(id_, test_path)
    delphin_dict = delphin_parser.dp6_to_dict(test_path + '/' + id_ + '.d6p')
    new_delphin = delphin_permutations.change_weather(delphin_dict,
                                               'Temp Out',
                                               r'C:/Program Files (x86)/IBK/Delphin 5.9/DB_climate_data/Germany/Kassel/Temperature.ccd')
    xmltodict.unparse(new_delphin, output=open(test_path + '/' + id_ + '_test.d6p', 'w'), pretty=True)
    helper.clean_up_test_folders()
