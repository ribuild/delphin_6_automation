__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import numpy as np
import typing

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger(__name__)


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

def mould_index(relative_humidity: typing.List[float], temperature: typing.List[float], draw_back: int,
                sensitivity_class: int, surface_quality: int) -> typing.List[float]:
    """
    Computes a time series of the mould index
    Source: T. Ojanen, H. Viitanen - Mold growth modeling of building structures using sensitivity classes of materials - 2010
    """

    # Initial setup:
    if sensitivity_class == 1:
        sensitivity_class = ((1, 2), (1, 7, 2), 80)
    elif sensitivity_class == 2:
        sensitivity_class = ((0.578, 0.386), (0.3, 6, 1), 80)
    elif sensitivity_class == 3:
        sensitivity_class = ((0.072, 0.097), (0, 5, 1.5), 85)
    elif sensitivity_class == 4:
        sensitivity_class = ((0.033, 0.014), (0, 3, 1), 85)

    if draw_back == 1:
        draw_back = 1
    elif draw_back == 2:
        draw_back = 0.5
    elif draw_back == 3:
        draw_back = 0.25
    elif draw_back == 4:
        draw_back = 0.1

    if surface_quality < 0:
        surface_quality = 0
    elif surface_quality > 1:
        surface_quality = 1
    else:
        surface_quality = surface_quality

    k1_m1 = sensitivity_class[0][0]
    k1_m3 = sensitivity_class[0][1]
    a = sensitivity_class[1][0]
    b = sensitivity_class[1][1]
    c = sensitivity_class[1][2]
    rh_min = sensitivity_class[2]

    m = 0
    t = 0
    result = []

    for i in range(len(relative_humidity)):

        if temperature[i] > 20:
            rh_critical = rh_min
        else:
            rh_critical = -0.00267 * temperature[i] ** 3 + 0.16 * temperature[i] ** 2 - 3.13 * temperature[i] + 100

        m_max = a + b * (rh_critical - relative_humidity[i]) / (rh_critical - 100) - c * (
                (rh_critical - relative_humidity[i]) / (rh_critical - 100)) ** 2

        if m < 1:
            k1 = k1_m1
        else:
            k1 = k1_m3

        try:
            k2 = max((1 - np.exp(2.3 * (m - m_max))), 0)
        except OverflowError:
            k2 = 1

        if relative_humidity[i] < rh_critical or temperature[i] <= 0:
            if t < 6:
                delta_m = draw_back * -0.00133
                t += 1
            elif 6 <= t <= 24:
                delta_m = 0
                t += 1
            else:
                delta_m = draw_back * -0.000667
                t += 1

        else:
            delta_m = 1 / (7 * np.exp(-0.68 * np.log(temperature[i]) - 13.9 * np.log(
                relative_humidity[i]) - 0.33 * surface_quality + 66.02)) * k1 * k2
            t = 0

        m += delta_m

        if m < 0:
            m = 0

        result.append(m)

    return result


def frost_risk(relative_humidity: np.array, temperature: np.array) -> np.array:
    """
    Evaluates frost risk
    Returns: List - Containing 0's and 1's. Where a 0 indicates no frost risk and an 1 indicate frost risk
    Source: John Grünewalds Frost Model
    """

    # Constants
    water_density = 1000  # kg/m3
    specific_heat_capacity_water = 4187  # J/(kgK)
    specific_heat_capacity_water_ice = 2100  # J/(kgK)
    reference_temperature = 273.15  # K
    enthalpy_water_ice = -333500  # J/kg
    gas_constant_vapour = 461.5  # J/(kgK)

    temperature_in_kelvin = temperature + reference_temperature

    f_pu = water_density * (-(enthalpy_water_ice / reference_temperature *
                              (temperature_in_kelvin - reference_temperature)) +
                            (specific_heat_capacity_water - specific_heat_capacity_water_ice) *
                            (temperature_in_kelvin * np.log(temperature_in_kelvin / reference_temperature) -
                             (temperature_in_kelvin - reference_temperature)))

    f_phi = np.exp(f_pu / (water_density * gas_constant_vapour * temperature_in_kelvin)) * 100

    return (relative_humidity > f_phi).astype(int)


def frost_curves(temperature: typing.List[float]):
    """
    Outputs Frost curve
    """

    # Constants
    water_density = 1000  # kg/m3
    specific_heat_capacity_water = 4187  # J/(kgK)
    specific_heat_capacity_water_ice = 2100  # J/(kgK)
    temperature_kelvin = 273.15  # K
    enthalpy_water_ice = -333500  # J/kg
    gas_constant_vapour = 461.5  # J/(kgK)

    result = []
    temperature_max = max(temperature)
    temperature_min = min(temperature)
    temperature = np.linspace(temperature_min, temperature_max, 200)

    for temp in temperature:
        f_pu = water_density * (-(enthalpy_water_ice / temperature_kelvin * (temp - temperature_kelvin)) + (
                    specific_heat_capacity_water - specific_heat_capacity_water_ice) * (
                                            temp * np.log(temp / temperature_kelvin) - (temp - temperature_kelvin)))
        f_phi = np.exp(f_pu / (water_density * gas_constant_vapour * temp)) * 100
        result.append(f_phi)

    return result


def wood_rot(relative_humidity_list: typing.List[float], temperature_list: typing.List[float]) \
        -> tuple:

    def time_critical(relative_humidity, temperature):
        return (2.3 * temperature + 0.035 * relative_humidity - 0.024 * temperature * relative_humidity) / \
               (-42.9 + 0.14 * temperature + 0.45 * relative_humidity) * 30 * 34

    def delta_alpha(relative_humidity, temperature):

        if temperature > 0 and relative_humidity > 0.95:
            return 1/time_critical(relative_humidity, temperature)
        else:
            return -1/17520

    def delta_mass_loss(relative_humidity, temperature):
        return -5.96 * 10**(-2) + 1.96 * 10**(-4) * temperature + 6.25 * 10**(-4) * relative_humidity

    alpha = [0, ]
    mass_loss = [0, ]

    for i in range(len(relative_humidity_list)):
        alpha.append(max(alpha[-1] + delta_alpha(relative_humidity_list[i], temperature_list[i]), 0))

        if alpha[-1] >= 1:
            mass_loss.append(mass_loss[-1] + delta_mass_loss(relative_humidity_list[i], temperature_list[i]))
        else:
            mass_loss.append(mass_loss[-1])

    return mass_loss[1:], alpha[1:]
