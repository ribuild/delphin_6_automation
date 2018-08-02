__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import copy
from collections import namedtuple
import typing

# RiBuild Modules:
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger(__name__)

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN PERMUTATION FUNCTIONS


def change_layer_width(delphin: dict, original_material: str, new_width: float) -> dict:
    """
    Changes the width of a single layer, while keeping number of elements in the project.
    :param delphin: Delphin dict to change.
    :param original_material: Name of material to change the width of.
    :param new_width: New width in m
    :return: Modified Delphin dict
    """

    layers = get_layers(delphin)
    layer = identify_layer(layers, original_material)
    new_discretization = discretize_layer(new_width)
    update_range_of_assignments(delphin, layer, new_discretization)

    logger.debug(f'Changed layer {layer["material"]} to {new_width} m')

    return delphin


def identify_layer(layers: dict, identifier: typing.Union[str, int]) -> dict:
    """
    Returns a layer given a identifier of that layer. Identifiers can be name of the material or the index of the
    material.

    :param layers: Layers to look in
    :param identifier: Identifier to identify layer by
    :return: The found layer
    """

    if isinstance(identifier, int):
        return layers[identifier]

    elif isinstance(identifier, str):
        for layer_ in layers:
            if layers[layer_]['material'] == identifier:
                return layers[layer_]
    else:
        error_message = f'identifier should be int or str. Type given was: {type(identifier)}'
        logger.ERROR(error_message)
        raise TypeError(error_message)


def update_range_of_assignments(delphin_dict: dict, layer: dict, new_discretization: list) -> dict:
    """
    Update the ranges of all assignments in a Delphin dict, given a layer and a new discretization of that layer

    :param delphin_dict: Delphin dict to update
    :param layer: Layer to update
    :param new_discretization: New discretization
    :return: Updated Delphin dict
    """

    # Update discretization
    logger.debug('Updated range assignment for Delphin project')
    current_x_list = convert_discretization_to_list(delphin_dict)
    range_ = layer['x_index']
    new_x_list = current_x_list[:range_[0]] + new_discretization + current_x_list[range_[1]:]
    delphin_dict['DelphinProject']['Discretization']['XSteps']['#text'] = ' '.join([str(value_)
                                                                                    for value_ in new_x_list])
    # Update layer range
    old_range_length = range_[1] - range_[0]
    new_range_length = len(new_discretization)

    if old_range_length == new_range_length:
        return delphin_dict

    else:
        delta_range = new_range_length - old_range_length

        for assignment in delphin_dict['DelphinProject']['Assignments']['Assignment']:
            if assignment['@location'] != 'Coordinate':
                update_assignment_range(assignment, delta_range, range_[1])

        return delphin_dict


def update_assignment_range(assignment: dict, delta_range: int, range_to_update_after: int) -> None:
    """
    Updates the range of a single assignment.

    :param assignment: Assignment to change
    :param delta_range: Change in range
    :param range_to_update_after: After which the ranges should be updated
    """

    range_list = [int(r)
                  for r in assignment['Range'].split(' ')]
    if range_list[0] >= range_to_update_after:
        range_list[0] += delta_range

    if range_list[2] >= range_to_update_after:
        range_list[2] += delta_range

    assignment['Range'] = ' '.join([str(r)
                                    for r in range_list])

    return None


def change_layer_widths(delphin_dict: dict, layer_material: str, widths: list) -> list:
    """
    Creates a new Delphin dict with the width of each value in widths.

    :param delphin_dict: Delphin dict to change.
    :param layer_material: Name of material to change the width of.
    :param widths: New widths in m
    :return: List with modified Delphin dicts
    """

    permutated_dicts = []

    for width in widths:
        permutated_dicts.append(change_layer_width(delphin_dict, layer_material, width))

    return permutated_dicts


def change_layer_material(delphin_dict: dict, original_material: str, new_material: dict) -> dict:
    """
    Changes the material of a layer.

    :param delphin_dict: Delphin dict to change.
    :param original_material: Name of material that should be changed.
    :param new_material: New material given as a dict. Dict should have the following keys: @name, @color, @hatchCode and #text.
    :return: Modified Delphin dict
    """

    new_delphin_dict = copy.deepcopy(delphin_dict)

    # Find original material
    for mat_index in range(0, len(delphin_dict['DelphinProject']['Materials']['MaterialReference'])):
        if delphin_dict['DelphinProject']['Materials']['MaterialReference'][mat_index]['@name'] == original_material:
            # Replace with new material
            new_delphin_dict['DelphinProject']['Materials']['MaterialReference'][mat_index] = new_material

    # Find original material assignment
    for assign_index in range(0, len(delphin_dict['DelphinProject']['Assignments']['Assignment'])):
        if delphin_dict['DelphinProject']['Assignments']['Assignment'][assign_index]['Reference'] == original_material:
            # Replace with new material
            new_delphin_dict['DelphinProject']['Assignments']['Assignment'][assign_index]['Reference'] = \
                new_material['@name']

    logger.debug(f'Changed material {original_material} to {new_material["@name"]}')

    return new_delphin_dict


def change_weather(delphin_dict: dict, original_weather: str, new_weather: str) -> dict:
    """
    Changes the weather file of a weather instance. Can therefore only be used on climate conditions that is loaded
    from a file.

    :param delphin_dict: Delphin dict to change.
    :param original_weather: Name of the original weather
    :param new_weather: New weather file path
    :return: Modified Delphin dict
    """

    # Find original weather
    climate_conditions = delphin_dict['DelphinProject']['Conditions']['ClimateConditions']['ClimateCondition']
    for weather_index in range(0, len(climate_conditions)):
        if climate_conditions[weather_index]['@name'] == original_weather:
            climate_conditions[weather_index]['Filename'] = new_weather

    return delphin_dict


def change_orientation(delphin_dict: dict, new_orientation: int) -> dict:
    """
    Changes the orientation of the Delphin project.

    :param delphin_dict: Delphin dict to change.
    :param new_orientation: New orientation. Value between 0 and 360
    :return: Modified Delphin dict
    """

    assert 0 <= new_orientation <= 360

    # Find current orientation
    interfaces = delphin_dict['DelphinProject']['Conditions']['Interfaces']['Interface']

    for index in range(len(interfaces)):
        try:
            interfaces[index]['IBK:Parameter']['#text'] = str(new_orientation)
        except KeyError:
            pass

    logger.debug(f'Changed orientation to {new_orientation} degrees from North')
    return delphin_dict


def change_boundary_coefficient(delphin_dict: dict, boundary_condition: str, coefficient: str, new_value: float) \
        -> dict:
    """
    Changes a boundary coefficient of a boundary condition instance.

    :param delphin_dict: Delphin dict to change.
    :param boundary_condition: Name of the boundary condition
    :param coefficient: Name of the coefficient to change
    :param new_value: New value of the coefficient
    :return: Modified Delphin dict
    """

    boundary_conditions = delphin_dict['DelphinProject']['Conditions']['BoundaryConditions']['BoundaryCondition']

    for index in range(len(boundary_conditions)):
        if boundary_conditions[index]['@name'] == boundary_condition:
            if isinstance(boundary_conditions[index]['IBK:Parameter'], list):
                for sub_index in range(len(boundary_conditions[index]['IBK:Parameter'])):
                    if boundary_conditions[index]['IBK:Parameter'][sub_index]['@name'] == coefficient:
                        boundary_conditions[index]['IBK:Parameter'][sub_index]['#text'] = str(new_value)
            else:
                if boundary_conditions[index]['IBK:Parameter']['@name'] == coefficient:
                    boundary_conditions[index]['IBK:Parameter']['#text'] = str(new_value)

    logger.debug(f'Changed the {coefficient} of {boundary_condition} to: {new_value}')

    return delphin_dict


def get_layers(delphin_dict: dict) -> dict:
    """
    Get the layers of a Delphin dict.

    :param delphin_dict: Delphin dict to get layers from.
    :return: Dict of dicts. Each nested dict has the keys: material, x_width, x_index
    """

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


def convert_discretization_to_list(delphin_dict: dict) -> list:
    """
    Get the discretized elements of a project.

    :param delphin_dict: Delphin dict to look in.
    :return: A list with the discretizated values.
    """

    x_list = [float(x)
              for x in delphin_dict['DelphinProject']['Discretization']['XSteps']['#text'].split(' ')]

    return x_list


def discretize_layer(width: float, stretch_factor: float = 1.3,  minimum_division=0.001, maximum_division=0.2) -> list:
    """
    Creates a subdivision of the material to be used for the discretization.

    :param width: Width of the material to be subdivided
    :param minimum_division: Width of the smallest division
    :param stretch_factor: Increase in subdivisions
    :param maximum_division: Maximum size of a cell
    :return: List containing width of subdivisions
    """

    processed_width = 0
    next_ = minimum_division
    left_side = []
    right_side = []

    while processed_width < width:
        remaining = width - processed_width

        if next_*2 <= remaining:
            left_side.append(next_)
            right_side.append(next_)
            processed_width += next_*2

        else:
            if remaining <= maximum_division:
                left_side.append(remaining)
                processed_width += remaining
            else:
                left_side.append(remaining/2)
                right_side.append(remaining/2)
                processed_width += remaining

        next_ = min(next_ * stretch_factor, maximum_division)

    new_grid = left_side + right_side[::-1]

    return new_grid


def change_simulation_length(delphin_dict: dict, simulation_length: int, length_unit: str) -> dict:

    simulation_properties = delphin_dict['DelphinProject']['Init']['SimulationParameter']['Interval']['IBK:Parameter']
    simulation_properties['#text'] = str(simulation_length)
    simulation_properties['@unit'] = length_unit

    return delphin_dict


def get_simulation_length(delphin_dict: dict) -> tuple:

    SimulationLength = namedtuple('SimulationLength', ['length', 'unit'])

    simulation_properties = delphin_dict['DelphinProject']['Init']['SimulationParameter']['Interval']['IBK:Parameter']

    return SimulationLength(float(simulation_properties['#text']), simulation_properties['@unit'])


def compute_vapour_diffusion_slope(heat_slope, vapour_exchange):

    heat_exchange = 4
    return heat_slope * vapour_exchange, heat_exchange * vapour_exchange


def update_output_locations(delphin: dict) -> dict:

    x_steps = convert_discretization_to_list(delphin)
    layers = get_layers(delphin)

    for assignment in delphin['DelphinProject']['Assignments']['Assignment']:
        if assignment['@type'] == 'Output':
            if assignment['Reference'].endswith('algae'):
                assignment['IBK:Point3D'] = '0.0005 0.034 0'

            elif assignment['Reference'].endswith('frost'):
                assignment['IBK:Point3D'] = '0.005 0.034 0'

            elif assignment['Reference'] == 'heat loss':
                assignment['Range'] = f'{len(x_steps)-1} 0 {len(x_steps)-1} 0'

            elif assignment['Reference'].endswith('interior surface'):
                assignment['IBK:Point3D'] = f'{sum(x_steps) - 0.0005} 0.034 0'

            elif assignment['Reference'].endswith('mould'):
                if len(layers) == 2:
                    width = layers[0]["x_width"] - 0.0005
                    assignment['IBK:Point3D'] = f'{width} 0.034 0'

                elif len(layers) in [3, 5]:
                    width = layers[0]["x_width"] + layers[1]["x_width"] - 0.0005
                    assignment['IBK:Point3D'] = f'{width} 0.034 0'

                elif len(layers) == 6:
                    width = layers[0]["x_width"] + layers[1]["x_width"] + layers[2]["x_width"] - 0.0005
                    assignment['IBK:Point3D'] = f'{width} 0.034 0'

    return delphin
