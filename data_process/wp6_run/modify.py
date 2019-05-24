__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

import os
import json


folder = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\wp6_run\inputs\materials'




def space(lst):
    new_list = []

    for elem in lst:
        try:
            float(elem)
            new_list.append(elem.strip())
        except ValueError:
            new_list.extend([e.strip() for e in elem.split("\t") if e])

    return new_list


def split_lines(file, line_num):
    file_obj = open(file, 'r').readlines()

    for num in line_num:
        a = space(file_obj[num].strip().split(" "))
        file_obj[num] = "      " + "      ".join(a) + "\n"

    with open(file, 'w') as f:
        f.writelines(file_obj)

    if os.path.exists(file):
        print(f'Formatted {file}')


file = os.path.join(folder, 'DTUBrick_901.m6')
#split_lines(file, [31, 35, 36, 39, 40])

file = os.path.join(folder, 'CasiPlus_903.m6')
#split_lines(file, [31, 35, 36, 39, 40])

file = os.path.join(folder, 'Gneiss from Cresciano_904.m6')
split_lines(file, [34, 37, 42, 44, 45])

file = os.path.join(folder, 'Italian limestone_905.m6')
split_lines(file, [33, 34, 36, 37, 42, 44, 45])

file = os.path.join(folder, 'Italian sandstone_906.m6')
split_lines(file, [33, 36, 37, 42, 44, 45])

file = os.path.join(folder, 'Molasse Sandstone from Bollingen_909.m6')
split_lines(file, [33, 36, 37, 42, 44, 45])

file = os.path.join(folder, 'Molasse sandstone from Villarlod_910.m6')
split_lines(file, [33, 34, 36, 37, 42, 44, 45])

file = os.path.join(folder, 'Shell limestone from Magenwil_911.m6')
split_lines(file, [33, 36, 37, 42, 44, 45])



#designs = os.listdir(r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\wp6_run\inputs\design')

#with open(r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\wp6_run\inputs\sampling_strategy.json', 'r') as file:
#    data = json.load(file)
"""
a = set(data['design'])
b = set([d.split('.')[0] for d in designs])

ab = a - b
print(len(ab))
print(sorted(list(ab)))
"""