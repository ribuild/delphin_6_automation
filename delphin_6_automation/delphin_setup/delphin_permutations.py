__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import numpy as np
from scipy.optimize import fsolve

# RiBuild Modules:

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN PERMUTATION FUNCTIONS


def change_layer_width(delphin_dict: dict, original_material: str, new_width: float) -> dict:
    layers = get_layers(delphin_dict)
    x_list = convert_discretization_to_list(delphin_dict)
    new_x_list = None

    for layer in layers:
        if layers[layer]['material'] == original_material:
            range_ = layers[layer]['x_index']
            steps = range_[1] - range_[0]
            new_discretization = discrete_layer(new_width, steps)
            new_x_list = x_list[:range_[0]] + new_discretization + x_list[range_[1]:]

    if new_x_list:
        delphin_dict['DelphinProject']['Discretization']['XSteps']['#text'] = ' '.join([str(value_)
                                                                                        for value_ in new_x_list])
    else:
        raise KeyError(f'Could not find original_material in DelphinProject. original_material given was: '
                       f'{original_material}')

    return delphin_dict


def change_layer_material(delphin_dict: dict, original_material: str, new_material: dict) -> dict:

    # Find original material
    for mat_index in range(0, len(delphin_dict['DelphinProject']['Materials']['MaterialReference'])):
        if delphin_dict['DelphinProject']['Materials']['MaterialReference'][mat_index]['@name'] == original_material:
            # Replace with new material
            delphin_dict['DelphinProject']['Materials']['MaterialReference'][mat_index] = new_material

    # Find original material assignment
    for assign_index in range(0, len(delphin_dict['DelphinProject']['Assignments']['Assignment'])):
        if delphin_dict['DelphinProject']['Assignments']['Assignment'][assign_index]['Reference'] == original_material:
            # Replace with new material
            delphin_dict['DelphinProject']['Assignments']['Assignment'][assign_index]['Reference'] = \
                new_material['@name']

    return delphin_dict


def change_weather(delphin_dict: dict, original_weather: str, new_weather: str) -> dict:

    # Find original weather
    climate_conditions = delphin_dict['DelphinProject']['Conditions']['ClimateConditions']['ClimateCondition']
    for weather_index in range(0, len(climate_conditions)):
        if climate_conditions[weather_index]['@name'] == original_weather:
            climate_conditions[weather_index]['Filename'] = new_weather

    return delphin_dict


def add_layers():
    pass


def remove_layers():
    pass


def get_layers(delphin_dict: dict) -> dict:
    x_list = convert_discretization_to_list(delphin_dict)

    index = 0
    layers_dict = dict()
    for assignment in delphin_dict['DelphinProject']['Assignments']['Assignment']:
        if assignment['@type'] == 'Material':
            layer = dict()
            layer['material'] = assignment['Reference']
            range_ = [int(x)
                      for x in assignment['Range'].split(' ')]
            layer['x_width'] = sum(x_list[range_[0]:range_[2]+1])
            layer['x_index'] = range_[0], range_[2]
            layers_dict[index] = layer
            index += 1

    return layers_dict


def discrete_layer(width: float, steps: int) -> list:
    min_x = 0.001
    steps = steps/2

    def sum_function(stretch_factor):
        return width - min_x * ((1 - stretch_factor**steps)/(1 - stretch_factor))

    stretch = float(fsolve(sum_function, 1.3)[0])

    return sub_division(width, min_x, stretch)


def convert_discretization_to_list(delphin_dict: dict) -> list:
    x_list = [float(x)
              for x in delphin_dict['DelphinProject']['Discretization']['XSteps']['#text'].split(' ')]

    return x_list


def sub_division(width: float, minimum_division: float, stretch_factor: float) -> list:
    """
    Creates a subdivision of the material to be used for the discretization.
    :param width: Width of the material to be subdivided
    :param minimum_division: Width of the smallest division
    :param stretch_factor: Increase in subdivisions
    :return: List containing width of subdivisions
    """

    sum_x = 0
    next_ = minimum_division
    new_grid = []
    max_dx = 20/100
    x = width/2

    while sum_x < x:
        remaining = x - sum_x

        if next_ > max_dx:
            n = np.ceil(remaining/max_dx)

            if n == 0:
                new_grid.append(remaining)

            next_ = remaining/n

            for _ in range(0, int(n)):
                new_grid.append(next_)
                sum_x += next_

            remaining = x - sum_x

        if next_ < remaining:
            new_grid.append(next_)
            sum_x += next_
        else:
            remaining += new_grid[-1]
            new_grid[-1] = remaining/2
            new_grid.append(remaining/2)
            sum_x = x

        next_ = next_ * stretch_factor

    x1 = new_grid[::-1]
    x2 = new_grid+x1

    return x2
