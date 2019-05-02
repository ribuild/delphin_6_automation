__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import os
import numpy as np

# RiBuild Modules
from delphin_6_automation.delphin_setup import damage_models
from delphin_6_automation.file_parsing import delphin_parser
# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

folder = r'C:\Users\ocni\Desktop\simulation_years_data'

projects = os.listdir(folder)


def make_damage(folder_, name):
    if name == 'interface' and not os.path.exists(os.path.join(folder_, f'mould_{name}.txt')):
        rh = delphin_parser.d6o_to_dict(folder_, 'relative humidity mould.d6o')[0]
        temp = delphin_parser.d6o_to_dict(folder_, 'temperature mould.d6o')[0]

        if len(rh) not in [61321, 61320]:
            print(f'Encountered Non-finished project at {folder_}. Skipping')
            return

        try:
            assert len(rh) == len(temp)
        except AssertionError:
            print(f'RH: {len(rh)}')
            print(f'TEMP: {len(temp)}')
            print(folder_ + '\n')
            if len(rh) > len(temp):
                temp.append(temp[-1])
            elif len(temp) > len(rh):
                rh.append(rh[-1])
        finally:

            mould = damage_models.mould_index(rh, temp, draw_back=1, sensitivity_class=3, surface_quality=0)
            np.savetxt(os.path.join(folder_, f'mould_{name}.txt'), mould)

    elif name == 'interior_surface' and not os.path.exists(os.path.join(folder_, f'mould_{name}.txt')):
        rh = delphin_parser.d6o_to_dict(folder_, 'relative humidity interior surface.d6o')[0]
        temp = delphin_parser.d6o_to_dict(folder_, 'temperature interior surface.d6o')[0]

        if len(rh) not in [61321, 61320]:
            print(f'Encountered Non-finished project at {folder_}. Skipping')
            return

        try:
            assert len(rh) == len(temp)
        except AssertionError:
            print(f'RH: {len(rh)}')
            print(f'TEMP: {len(temp)}')
            print(folder_ + '\n')
            if len(rh) > len(temp):
                temp.append(temp[-1])
            elif len(temp) > len(rh):
                rh.append(rh[-1])
        finally:
            mould = damage_models.mould_index(rh, temp, draw_back=1, sensitivity_class=3, surface_quality=0)
            np.savetxt(os.path.join(folder_, f'mould_{name}.txt'), mould)


print('Starting Processing Projects\n')
index = 0
for project in projects:
    for content in os.listdir(os.path.join(folder, project)):
        if os.path.isdir(os.path.join(folder, project, content)):
            result_folder = os.path.join(folder, project, content, 'results')

            make_damage(result_folder, 'interface')
            make_damage(result_folder, 'interior_surface')
            print(f'Computed Mould Index for project with ID: {project}')

    index += 1
    if index % 250 == 0:
        print(f'\n{index} projects have been downloaded\n')
