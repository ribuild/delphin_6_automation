__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import numpy as np
import xmltodict
import os
from collections import defaultdict

# RiBuild Modules
from delphin_6_automation.file_parsing.delphin_parser import dp6_to_dict
from delphin_6_automation.delphin_setup import delphin_permutations
from delphin_6_automation.database_interactions.material_interactions import get_material_info

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def construction_types() -> list:
    """Gets available template strings.

    :return: list of file name strings
    """

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files/delphin'

    return os.listdir(folder)


def wall_core_materials() -> list:
    """All included material IDs relevant for a wall's core.

    :return: list of IDs
    """

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'

    bricks = pd.read_excel(folder + '/Brick.xlsx')
    natural_stones = pd.read_excel(folder + '/Natural Stone.xlsx')

    material_list = bricks['Material ID'].tolist() + natural_stones['Material ID'].tolist()

    return material_list


def plaster_materials() -> list:
    """All included material IDs relevant for plastering of a wall.

    :return: list of IDs
    """

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'

    plasters = pd.read_excel(folder + '/Plaster.xlsx')['Material ID'].tolist()

    return plasters


def insulation_type() -> list:
    """All included material IDs in insulation systems as such.

    :return:
    """

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'
    insulation = pd.read_excel(folder + '/InsulationSystems.xlsx')['Material ID'].str.split(', ')

    return [[int(i) for i in sublist]
            for sublist in insulation.tolist()]


def insulation_systems() -> pd.DataFrame:
    """Reformat insulation DataFrame to different design options DataFrame

    :return:
    """

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'

    # partial insulation system portfolio and test file functional 20180807 SBJ
    constructions = pd.read_excel(folder + '/InsulationSystems.xlsx', usecols=[0, 3, 4, 5, 6], nrows=2)
    # constructions = pd.read_excel(folder + '/InsulationSystems_test.xlsx', usecols=[0, 3, 4, 5, 6])

    systems = pd.DataFrame()
    level_1 = []
    level_2 = np.array([])

    for idx, row in constructions.iterrows():
        material_id_and_dim = []

        # provide distinction between ID strings, dimensions and ect..
        for col in row:

            if type(col) is float:
                material_id_and_dim.append([col])

            elif type(col) is int:
                material_id_and_dim.append([col])

            elif type(col) is bool:
                material_id_and_dim.append([col])

            else:
                material_id_and_dim.append([int(j) for j in col.split(', ')])

        # re-combine values in a DataFrame (first element is ID's)
        columns = []
        elements = ['insulation_', 'finish_', 'detail_']

        # each element: insulation, finish, detail
        for i, ID in enumerate(material_id_and_dim[0]):

            part = pd.DataFrame({'ID': ID,
                                 'Dimension': material_id_and_dim[i + 1]}
                                )
            # each variation title
            for index in part.index:
                columns.append(elements[i] + str(index).zfill(2))

            systems = systems.append(part)

        # preperation to multiindex
        level_1 = np.append(level_1, [idx] * len(columns))
        level_2 = np.append(level_2, columns)

    # assign multiindex
    systems.index = [level_1.astype('int'), level_2]

    return systems


def delphin_templates() -> dict:
    """Titles on delphin files to variate (select by amount of layers).

    :return: dictionary with integer keys according to layers
    """

    # available template files indexed using amount of layers
    to_copy = defaultdict(lambda: [])
    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'

    for root, dirs, files in os.walk(folder + '/delphin'):

        for title in files:

            fileinfo = title.split('_')[-1]

            if fileinfo == 'plaster.d6p':
                to_copy[0].append(title)

            elif fileinfo == 'insulated2layers.d6p':
                to_copy[2].append(title)

            elif fileinfo == 'insulated3layers.d6p':
                to_copy[3].append(title)

    return to_copy


def construct_delphin_reference():
    """Generate Delphin files for models without insulation.

    :return:
    """

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'

    # each reference wall (0 layers) with number for specfic identification
    for i, file in enumerate(delphin_templates()[0]):
        design = dp6_to_dict(folder + '/delphin/' + file)

        xmltodict.unparse(design,
                          output=open(os.path.join(folder,
                                                   'design',
                                                   file.split('.')[0] + '_reference.d6p'), 'w'), pretty=True)


def implement_system_materials(delphin_dict: dict, system: pd.DataFrame):
    """Loop through materials of the system.

    :param delphin_dict: relevant template delphin dict
    :param system: one insulation system's Dataframe
    :return: new delphin dict with all system materials implemented
    """

    # general material names (template projects) - in order: insulation, finish, detail
    material_names = {'insulation': 'CalsithermCalciumsilikatHamstad [571]',
                      'finish': 'KlimaputzMKKQuickmix [125]',
                      'detail': 'Calsitherm KP Glue Mortar [705]'}
    """material_names = {'insulation': 'TecTem Insulation Board Indoor 50 + 60 mm [659]',
                      'finish': 'TecTem Clay-based plaster [665]',
                      'detail': 'TecTem Adhesive Mortar [664]'}"""

    # for two layer systems reduce materials
    if not any('detail' in string for string in system.index):
        del material_names['detail']

    # in current model each layer type
    for layer, material in material_names.items():

        # material dict all layers representative as _00 instances
        db_material = get_material_info(system.loc[layer + '_00', 'ID'])

        # step 1 new delphin dict - input dict, str, dict
        delphin_dict = delphin_permutations.change_layer_material(delphin_dict,
                                                                  material,
                                                                  db_material
                                                                  )

        if layer != 'insulation':
            # thickness of layer detail
            select_layer = [layer in string for string in system.index]
            new_width = round(system.loc[select_layer, 'Dimension'].astype(float).values[0] * 10e-4, 3)
            delphin_dict = delphin_permutations.change_layer_width(delphin_dict,
                                                                   db_material['@name'],
                                                                   new_width
                                                                   )

    return delphin_dict


def implement_insulation_widths(delphin_dict: dict, system: pd.DataFrame) -> list:
    """Permutate with of system applied materials.

    :param delphin_dict:
    :param system:
    :return:
    """

    # look up current material assume system
    db_material = get_material_info(system.loc['insulation' + '_00', 'ID'])
    insulation_select = ['insulation' in row for row in system.index]

    new_widths = system.loc[insulation_select, 'Dimension'].astype(float) * 10e-4
    permutated_dicts = delphin_permutations.change_layer_widths(delphin_dict,
                                                                db_material['@name'],
                                                                new_widths.tolist()
                                                                )
    # inspection of result
    for delphin_dict in permutated_dicts:
        layers = delphin_permutations.get_layers(delphin_dict)

    return permutated_dicts


def construct_design_options():
    """Generate Delphin files to cover all the design options.

        Options arise from separate insulation systems X variation
         within those e.g. thickness of insulation layer.
        :return:
    """

    # appreciate formatted insulation systems
    systems = insulation_systems()
    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'

    # permutation of insulation systems
    for system_number in systems.index.levels[0]:

        # one insulation system each loop
        system = systems.loc[system_number]
        insulation_select = ['insulation' in row for row in system.index]

        # appreciate template - three or two layers
        if any('detail' in row for row in system.index):
            layers = 3
        else:
            layers = 2

        for file in delphin_templates()[layers]:

            # each template as dict to be permutated
            design = dp6_to_dict(folder + '/delphin/' + file)

            # material and dimension change
            delphin_with_system_materials = implement_system_materials(design, system)
            option_dicts = implement_insulation_widths(delphin_with_system_materials, system)

            if len(option_dicts) != sum(insulation_select):
                message = 'no length match'
                raise TypeError(message)

            # write option files (above dicts)
            for i, dim in enumerate(system.loc[insulation_select, 'Dimension']):
                xmltodict.unparse(option_dicts[i],
                                  output=open(os.path.join(folder,
                                                           'design',
                                                           file.split('.')[0] + '_option' + str(system_number).zfill(2)\
                                                           + '-' + str(dim).zfill(3) + '.d6p'),
                                              'w'), pretty=True)