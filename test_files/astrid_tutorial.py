# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import xmltodict
from collections import OrderedDict

# RiBuild Modules:
from delphin_6_automation.delphin_setup import delphin_permutations
from delphin_6_automation.file_parsing import delphin_parser
import delphin_6_automation.pytest.pytest_helper_functions as helper

# -------------------------------------------------------------------------------------------------------------------- #
# Tutorial


def change_orientation():
    # I specifies the path where the basic Delphin Project file is located
    source_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/delphin_6_automation/pytest/test_files'

    # I turn the Delphin file into a dict
    delphin_dict = delphin_parser.dp6_to_dict(source_path + '/delphin_project.d6p')

    # I create some folders where I can put the result.
    # They are in ../delphin_6_automation/pytest/test_dir
    test_path, _ = helper.setup_test_folders()

    # I change the orientation of the wall
    new_delphin = delphin_permutations.change_orientation(delphin_dict, 300)

    # I save it to a new file
    xmltodict.unparse(new_delphin, output=open(test_path + '/new_orientation_delphin_project.d6p', 'w'), pretty=True)


def change_material():
    # I specifies the path where the basic Delphin Project file is located
    source_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/delphin_6_automation/pytest/test_files'

    # I turn the Delphin file into a dict
    delphin_dict = delphin_parser.dp6_to_dict(source_path + '/delphin_project.d6p')

    # I create some folders where I can put the result.
    # They are in ../delphin_6_automation/pytest/test_dir
    test_path, _ = helper.setup_test_folders()

    # I specify the properties of the new material (here aerated concrete)
    new_material = OrderedDict((('@name', 'Aerated Concrete [6]'),
                                ('@color', '#ff404060'),
                                ('@hatchCode', '13'),
                                ('#text', '${Material Database}/AeratedConcrete_6.m6')))

    # I exchange the "Normal Brick" material with the aerated concrete specified above
    new_delphin = delphin_permutations.change_layer_material(delphin_dict, 'Normal Brick [512]', new_material)

    # I save it
    xmltodict.unparse(new_delphin, output=open(test_path + '/aerated_concrete_delphin_project.d6p', 'w'), pretty=True)


def change_surface_resistance():
    # I specifies the path where the basic Delphin Project file is located
    source_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/delphin_6_automation/pytest/test_files'

    # I turn the Delphin file into a dict
    delphin_dict = delphin_parser.dp6_to_dict(source_path + '/delphin_project.d6p')

    # I create some folders where I can put the result.
    # They are in ../delphin_6_automation/pytest/test_dir
    test_path, _ = helper.setup_test_folders()

    # I change the surface resistance to 12
    new_delphin = delphin_permutations.change_boundary_coefficient(delphin_dict, 'Indoor heat conduction',
                                                                   'ExchangeCoefficient', 12)

    # I save it
    xmltodict.unparse(new_delphin,
                      output=open(test_path + '/modified_resistance_delphin_project.d6p', 'w'), pretty=True)


# Run functions
change_orientation()
change_material()
change_surface_resistance()