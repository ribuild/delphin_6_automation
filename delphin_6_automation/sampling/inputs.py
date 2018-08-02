__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import numpy as np
import xmltodict
import os

# RiBuild Modules
from delphin_6_automation.file_parsing.delphin_parser import dp6_to_dict
from delphin_6_automation.delphin_setup import delphin_permutations
from delphin_6_automation.database_interactions.material_interactions import get_material_info

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def construction_types():

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files/delphin'

    return os.listdir(folder)


def wall_core_materials():

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'
    bricks = pd.read_excel(folder + '/Brick.xlsx')
    natural_stones = pd.read_excel(folder + '/Natural Stone.xlsx')

    material_list = bricks['Material ID'].tolist() + natural_stones['Material ID'].tolist()

    return material_list


def plaster_materials():

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'
    plasters = pd.read_excel(folder + '/Plaster.xlsx')['Material ID'].tolist()

    return plasters


def insulation_type():

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'
    insulation = pd.read_excel(folder + '/InsulationSystems.xlsx')['Material ID'].str.split(', ')

    return [[int(i) for i in sublist]
            for sublist in insulation.tolist()]


def construct_design_options():
    """
    Generate Delphin files to cover all the design options.
    Options arise from separate insulation systems X variation within those e.g. thickness of insulation layer.
    :return:
    """

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'
    #constructions = pd.read_excel(folder + '/InsulationSystems.xlsx', usecols=[0,3,4,5,6])
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


    # which template files (amount of layers) to load and alternate before writing to /input_files/design
    to_copy = {0: [], 2: [], 3: []}

    for root, dirs, files in os.walk(folder + '/delphin'):
        for title in files:  # one filename from dir per loop
            fileinfo = title.split('_')[-1]
            if fileinfo == 'plaster.d6p':
                to_copy[0].append(title)

            elif fileinfo == 'insulated2layers.d6p':
                to_copy[2].append(title)

            elif fileinfo == 'insulated3layers.d6p':
                to_copy[3].append(title)

    # general material names (template projects) - values in order: insulation, finish, detail
    material_names = {'insulation': 'Climate Board (until 2001) [571]',
                      'finish': 'Climate plaster [125]',
                      'detail': 'Calsitherm KP Glue Mortar [705]'}

    # each insulation system
    for system_number in systems.index.levels[0]:
        system = systems.loc[system_number]

        insulation_select = ['insulation' in string for string in system.index]

        # three/two layers
        if any('detail' in string for string in system.index):

            # each file
            for file in to_copy[3]:
                design = dp6_to_dict(folder + '/delphin/' + file)

                # each layer, #01 insulation
                for layer, material in material_names.items():
                    db_material = get_material_info(system.loc[layer + '_00', 'ID'])

                    variant = delphin_permutations.change_layer_material(design,
                                                                         material,
                                                                         db_material
                                                                         )

                    variant = delphin_permutations.change_layer_width(variant,
                                                                      db_material['@name'],
                                                                      system.loc[layer + '_00', 'Dimension']
                                                                      )


                # write to new directory write the same twice?
                for idx, variation in system.loc[insulation_select].iterrows():
                    if idx == 0:
                        xmltodict.unparse(variant,
                                          output=open(os.path.join(folder,
                                                                   'design',
                                                                   'system_' + str(system_number).zfill(2) + '_insulation_00.d6p'),
                                                      'w'), pretty=True)

                        continue
                    else:
                        db_material = get_material_info(variation['ID'])

                        variant = delphin_permutations.change_layer_width(variant,
                                                                          db_material['@name'],
                                                                          variation['Dimension'])
                        xmltodict.unparse(variant,
                                          output=open(os.path.join(folder,
                                                                   'design',
                                                                   'system_' + str(system_number).zfill(
                                                                       2) + '_insulation_' + str(idx).zfill(2) + '.d6p'),
                                                      'w'), pretty=True)

    # file names in list
    return systems
