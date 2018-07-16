__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import os

# RiBuild Modules

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

