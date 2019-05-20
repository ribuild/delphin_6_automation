__author__ = "Christian Kongsgaard, Simon Jørgensen"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import numpy as np
import xmltodict
import os
from collections import defaultdict
import typing
import shutil

# RiBuild Modules
from delphin_6_automation.file_parsing.delphin_parser import dp6_to_dict
from delphin_6_automation.delphin_setup import delphin_permutations
from delphin_6_automation.database_interactions.material_interactions import get_material_info

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def construction_types() -> typing.List[str]:
    """Gets available template strings.

    :return: list of file name strings
    """

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files/delphin'

    return os.listdir(folder)


def wall_core_materials(folder=os.path.dirname(os.path.realpath(__file__)) + '/input_files') -> typing.List[str]:
    """All included material IDs relevant for a wall's core.

    :return: list of IDs
    """

    brick_path = os.path.join(folder, 'Brick.xlsx')
    natural_stone_path = os.path.join(folder, 'Natural Stone.xlsx')
    material_list = []

    if os.path.isfile(brick_path):
        bricks = pd.read_excel(brick_path)
        material_list.extend(bricks['Material ID'].tolist())

    if os.path.isfile(natural_stone_path):
        natural_stones = pd.read_excel(natural_stone_path)
        material_list.extend(natural_stones['Material ID'].tolist())

    return material_list


def plaster_materials(folder=os.path.dirname(os.path.realpath(__file__)) + '/input_files') -> typing.List[str]:
    """All included material IDs relevant for plastering of a wall.

    :return: list of IDs
    """

    plasters = pd.read_excel(folder + '/Plaster.xlsx')['Material ID'].tolist()

    return plasters


def insulation_type(folder=os.path.dirname(os.path.realpath(__file__)) + '/input_files') \
        -> typing.List[typing.List[int]]:
    """All included material IDs in insulation systems as such."""

    insulation = pd.read_excel(folder + '/InsulationSystems.xlsx')['Material ID'].str.split(', ')

    return [[int(i) for i in sublist]
            for sublist in insulation.tolist()]


def insulation_systems(folder: str, rows_to_read=11, excel_file='InsulationSystems') -> pd.DataFrame:
    """Reformat insulation DataFrame to different design options DataFrame"""

    constructions = pd.read_excel(folder + f'/{excel_file}.xlsx', usecols=[0, 3, 4, 5], nrows=rows_to_read)

    systems = pd.DataFrame()
    level_1 = []
    level_2 = np.array([])

    for idx, row in constructions.iterrows():
        material_id_and_dim = []

        # provide distinction between ID strings, dimensions and ect..
        for col in row:

            if isinstance(col, (float, int, bool)):
                material_id_and_dim.append([col])

            else:
                material_id_and_dim.append([int(j) for j in col.split(', ')])

        # re-combine values in a DataFrame (first element is ID's)
        columns = []
        elements = ['insulation_', 'finish_', 'detail_']

        # each element: insulation, finish, detail
        for i, ID in enumerate(material_id_and_dim[0]):

            part = pd.DataFrame({'ID': ID,
                                 'Dimension': material_id_and_dim[i + 1]})

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


def delphin_templates(folder: str) -> dict:
    """Titles on delphin files to variate (select by amount of layers).

    :return: dictionary with integer keys according to layers
    """

    # available template files indexed using amount of layers
    to_copy = defaultdict(lambda: [])

    for root, dirs, files in os.walk(folder + '/delphin'):

        for title in files:

            if title.endswith('plaster.d6p'):
                to_copy[0].append(title)

            elif title.endswith('insulated2layers.d6p'):
                to_copy[2].append(title)

            elif title.endswith('insulated3layers.d6p'):
                to_copy[3].append(title)

    return to_copy


def construct_delphin_reference(folder: str) -> typing.List[str]:
    """Generate Delphin files for models without insulation."""

    copied_files = []
    design_folder = os.path.join(folder, 'design')

    if os.path.exists(design_folder):
        shutil.rmtree(design_folder)
        os.mkdir(design_folder)
    else:
        os.mkdir(design_folder)

    for file in delphin_templates(folder)[0]:

        if 'exterior' in file:
            new_name = '1d_exterior.d6p'
        else:
            new_name = '1d_interior.d6p'

        from_file = os.path.join(folder, 'delphin', file)
        to_file = os.path.join(design_folder, new_name)
        copied_files.append(new_name)
        shutil.copyfile(from_file, to_file)

    return copied_files


def implement_system_materials(delphin_dict: dict, system: pd.DataFrame) -> dict:
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
                                                                  material.split('[')[-1],
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


def implement_insulation_widths(delphin_dict: dict, system: pd.DataFrame) -> typing.List[dict]:
    """Permutate width of system applied materials"""

    # look up current material assume system
    db_material = get_material_info(system.loc['insulation' + '_00', 'ID'])
    insulation_select = ['insulation' in row for row in system.index]

    new_widths = system.loc[insulation_select, 'Dimension'].astype(float) * 10e-4
    permutated_dicts = delphin_permutations.change_layer_widths(delphin_dict,
                                                                db_material['@name'],
                                                                new_widths.tolist()
                                                                )

    return permutated_dicts


def implement_interior_paint(delphin_paths: typing.List[str], folder: str, excel_file: str) -> typing.List[str]:
    """Permutate interior paint"""

    permutated_files = []
    excel_file = os.path.join(folder, f'{excel_file}.xlsx')
    system_data = pd.read_excel(excel_file, usecols=[1, 6], nrows=11)
    system_names = system_data.iloc[:, 0].tolist()

    for file in delphin_paths:
        if file in ['1d_exterior.d6p', '1d_interior.d6p']:
            permutated_files.append(file)

        else:
            system_name = file.split('_')[2]
            index = system_names.index(system_name)
            sd_values = system_data.iloc[index, 1]

            if sd_values:
                sd_values = [float(sd) for sd in sd_values.split(', ')]
                design = dp6_to_dict(os.path.join(folder, 'design', file))

                for sd in sd_values:
                    delphin_permutations.change_boundary_coefficient(design, 'IndoorVaporDiffusion', 'SDValue', sd)

                    file_name = file.split('.')[0] + f'_SD{sd}.d6p'
                    permutated_files.append(file_name)
                    xmltodict.unparse(design,
                                      output=open(os.path.join(folder,
                                                               'design',
                                                               file_name),
                                                  'w'), pretty=True)

            else:
                permutated_files.append(file)

    return permutated_files


def construct_design_files(folder: str) -> typing.List[str]:
    """
    Generate Delphin files to cover all the design options.
    Options arise from separate insulation systems X variation within those e.g. thickness of insulation layer.
    """

    # appreciate formatted insulation systems
    excel_file = 'InsulationSystems'
    systems = insulation_systems(folder=folder, excel_file=excel_file)
    file_names = construct_delphin_reference(folder)

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

        for file in delphin_templates(folder)[layers]:

            # each template as dict to be permutated
            design = dp6_to_dict(os.path.join(folder, 'delphin', file))

            # material and dimension change
            delphin_with_system_materials = implement_system_materials(design, system)
            option_dicts = implement_insulation_widths(delphin_with_system_materials, system)

            if len(option_dicts) != sum(insulation_select):
                message = 'no length match'
                raise TypeError(message)

            # write option files (above dicts)
            for i, dim in enumerate(system.loc[insulation_select, 'Dimension']):
                if 'exterior' in file:
                    new_name = '1d_exterior_'
                else:
                    new_name = '1d_interior_'

                insulation_name = pd.read_excel(folder + f'/{excel_file}.xlsx', usecols=[1]).loc[system_number, 'Name']

                if layers == 2:
                    new_name += f'{insulation_name}_{system.loc["insulation_00", "ID"]}_' \
                                f'{system.loc["finish_00", "ID"]}_{dim}'
                elif layers == 3:
                    new_name += f'{insulation_name}_{system.loc["insulation_00", "ID"]}_' \
                                f'{system.loc["finish_00", "ID"]}_{system.loc["detail_00", "ID"]}_{dim}'

                file_name = new_name + '.d6p'
                file_names.append(file_name)
                xmltodict.unparse(option_dicts[i],
                                  output=open(os.path.join(folder,
                                                           'design',
                                                           file_name),
                                              'w'), pretty=True)

    design_files = implement_interior_paint(file_names, folder, excel_file)

    return design_files


def design_options(folder=os.path.dirname(os.path.realpath(__file__)) + '/input_files') -> typing.List[str]:

    design_files = construct_design_files(folder)

    return [file.split('.')[0] for file in design_files]
