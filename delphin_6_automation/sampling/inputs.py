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
    # constructions = pd.read_excel(folder + '/InsulationSystems.xlsx', usecols=[0,3,4,5,6])
    constructions = pd.read_excel(folder + '/InsulationSystems_test.xlsx', usecols=[0, 3, 4, 5, 6])

    # change format on constructions DataFrame
    systems = pd.DataFrame()
    level_1 = []
    level_2 = np.array([])

    for idx, row in constructions.iterrows():
        material_ID_and_dim = []

        # provide distinction between ID's and dimensions
        for col in row:

            if type(col) is float:
                material_ID_and_dim.append([col])

            elif type(col) is int:
                material_ID_and_dim.append([col])

            elif type(col) is bool:
                material_ID_and_dim.append([col])

            else:
                material_ID_and_dim.append([int(j) for j in col.split(', ')])

        # re-combine values in a DataFrame (first element is ID's)
        columns = []
        elements = ['insulation_', 'finish_', 'detail_']

        # each element: insulation, finish, detail
        for i, ID in enumerate(material_ID_and_dim[0]):

            part = pd.DataFrame({'ID': ID,
                                 'Dimension': material_ID_and_dim[i + 1]}
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


def construct_design_options():
    """Generate Delphin files to cover all the design options.

    Options arise from separate insulation systems X variation
     within those e.g. thickness of insulation layer.
    :return:
    """

    # general material names (template projects) - in order: insulation, finish, detail
    material_names = {'insulation': 'CalsithermCalciumsilikatHamstad_571',
                      'finish': 'Climate plaster [125]',
                      'detail': 'Calsitherm KP Glue Mortar [705]'}

    # appreciate formatted insulation systems
    systems = insulation_systems()

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'

    # each reference wall with number for title
    for i, file in enumerate(delphin_templates()[0]):
        design = dp6_to_dict(folder + '/delphin/' + file)

        xmltodict.unparse(design,
                          output=open(os.path.join(folder,
                                                   'design',
                                                   'reference_' + str(i).zfill(2) + '_insulation_00.d6p'),
                                      'w'), pretty=True)

    # one system at a time, each with many possible variations
    for system_number in systems.index.levels[0]:
        system = systems.loc[system_number]

        insulation_select = ['insulation' in string for string in system.index]

        # three/two layers
        if any('detail' in string for string in system.index):

            # three layers - two models = two loops
            for file in delphin_templates()[3]:
                delphin = dp6_to_dict(folder + '/delphin/' + file)

                # in current model each layer type, #01 insulation
                for layer, material in material_names.items():

                    # material dict
                    db_material = get_material_info(system.loc[layer + '_00', 'ID'])

                    # step 1 new delphin dict - input dict, str, dict
                    delphin = delphin_permutations.change_layer_material(delphin,
                                                                         material,
                                                                         db_material
                                                                         )

                    # step 2 new delphin dict - input dict, str (original added above), float
                    if layer != 'insulation':
                        delphin = delphin_permutations.change_layer_width(delphin,
                                                                          db_material['@name'],
                                                                          system.loc[layer + '_00', 'Dimension'].astype(float)
                                                                          )
                    else:
                        delphin = delphin_permutations.change_layer_width(delphin,
                                                                          db_material['@name'],
                                                                          system.loc[layer + '_00', 'Dimension'].astype(
                                                                              float)
                                                                          )
            # one delphin dict completed now variated



                # write to new directory write the same twice?
                for idx, variation in system.loc[insulation_select].iterrows():
                    if idx == 0:
                        xmltodict.unparse(delphin,
                                          output=open(os.path.join(folder,
                                                                   'design',
                                                                   'system_' + str(system_number).zfill(2) + '_insulation_00.d6p'),
                                                      'w'), pretty=True)

                        continue
                    else:
                        db_material = get_material_info(variation['ID'])

                        delphin = delphin_permutations.change_layer_width(delphin,
                                                                          db_material['@name'],
                                                                          variation['Dimension'].astype(float))
                        xmltodict.unparse(delphin,
                                          output=open(os.path.join(folder,
                                                                   'design',
                                                                   'system_' + str(system_number).zfill(
                                                                       2) + '_insulation_' + str(idx).zfill(2) + '.d6p'),
                                                      'w'), pretty=True)

    # file names in list
    return systems
