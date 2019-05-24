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

#file = os.path.join(folder, 'Italian limestone_905.m6')
#file = os.path.join(folder, 'Italian sandstone_906.m6')
#file = os.path.join(folder, 'Molasse Sandstone from Bollingen_909.m6')
#file = os.path.join(folder, 'Molasse sandstone from Villarlod_910.m6')
file = os.path.join(folder, 'Shell limestone from Magenwil_911.m6')
#file = os.path.join(folder, 'Shell limestone from Magenwil_911.m6')

file_obj = open(file, 'r').readlines()
#data = [float(i) for i in file_obj[36].split(" ")]


def space(lst):
    new_list = []

    for elem in lst:
        try:
            float(elem)
            new_list.append(elem.strip())
        except ValueError:
            new_list.extend([e.strip() for e in elem.split("\t") if e])

    return new_list


a = space(file_obj[36].strip().split(" "))
file_obj[36] = "\t ".join(a) + "\n"
b = space(file_obj[44].strip().split(" "))
file_obj[44] = "\t ".join(b) + "\n"

with open(file, 'w') as f:
    f.writelines(file_obj)


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