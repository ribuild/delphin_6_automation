__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import os

# RiBuild Modules
from delphin_6_automation.file_parsing import dp6_to_dict
from delphin_6_automation.delphin_setup.delphin_permutations import change_layer_width
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
    '''
    Generate Delphin files to cover all the design options.
    Options arise from separate insulation systems X variation within those e.g. thickness of insulation layer.
    :return:
    '''

    folder = os.path.dirname(os.path.realpath(__file__)) + '/input_files'
    constructions = pd.read_excel(folder + '/InsulationSystems.xlsx')

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

    # material_ID's and their thickness - currently only insulation
    material_ID_and_dim = []

    # two loops - split string into to interegers and also formating those - within a loop
    for idx, row in constructions.iterrows():
        material_ID_and_dim.append([[int(j) for j in row[i].split(', ')] for i in ['Material ID', 'Provided dim.[mm]']])

    # above give amount of Delphin files, below each system
    for system in material_ID_and_dim:

        for file in to_copy(system[0]):
            design = dp6_to_dict(folder + '/delphin/' + file)

            # general material names (template projects) - values in order: insulation, finish, detail
            material_names = {'insulation' : 'Climate Board (until 2001) [571]',
                              'finish' : 'Climate plaster [125]',
                              'detail' : 'Calsitherm KP Glue Mortar [705]'}

            for layer in material_names.values():
                design = change_layer_width(design, layer, system[0][0])
                #save xmltodict.unparse(delphin_dict, output=open(os.path.join(path, f'{delphin_document.id}.d6p'), 'w'), pretty=True)

    return construction_types()
