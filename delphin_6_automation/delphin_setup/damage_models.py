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
logger = ribuild_logger()


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

def mould_index(relative_humidity: typing.List[float], temperature: typing.List[float], draw_back: int,
                sensitivity_class: int, surface_quality: int) -> typing.List[float]:
    """
    Computes a time series of the mould index

    Source:
    T. Ojanen, H. Viitanen
    Mold growth modeling of building structures using sensitivity classes of materials
    2010
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

        result.append(min(m, 6.0))

    return result


def frost_risk(relative_humidity: np.array, temperature: np.array) -> np.array:
    """
    Evaluates frost risk

    Source:
    John Grünewalds Frost Model

    :return: a list Containing 0's and 1's. Where a 0 indicates no frost risk and an 1 indicate frost risk
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
    Outputs Frost curves

    Source:
    John Grünewalds Frost Model
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
        -> typing.Tuple[list, list]:
    """
    Calculates the mass loss of wood due to rot

    Source:
    Viitanen, H., Toratti, T., Makkonen, L. et al.
    Towards modelling of decay risk of wooden materials
    Eur. J. Wood Prod.
    2010
    """

    def time_critical(relative_humidity, temperature):
        return (2.3 * temperature + 0.035 * relative_humidity - 0.024 * temperature * relative_humidity) / \
               (-42.9 + 0.14 * temperature + 0.45 * relative_humidity) * 30 * 34

    def delta_alpha(relative_humidity, temperature):

        if temperature > 0 and relative_humidity > 0.95:
            return 1 / time_critical(relative_humidity, temperature)
        else:
            return -1 / 17520

    def delta_mass_loss(relative_humidity, temperature):
        return max(-5.96 * 10 ** (-2) + 1.96 * 10 ** (-4) * temperature + 6.25 * 10 ** (-4) * relative_humidity, 0)

    alpha = [0.0, ]
    mass_loss = [0.0, ]

    for i in range(len(relative_humidity_list)):
        alpha.append(max(alpha[-1] + delta_alpha(relative_humidity_list[i], temperature_list[i]), 0))

        if alpha[-1] >= 1:
            mass_loss.append(
                min(mass_loss[-1] + delta_mass_loss(relative_humidity_list[i], temperature_list[i]), 100.0))
        else:
            mass_loss.append(mass_loss[-1])

    return mass_loss[1:], alpha[1:]


def mould_pj(relative_humidity: typing.List[float], temperature: typing.List[float], aed_group='b') \
        -> typing.Tuple[typing.Iterable, typing.Iterable]:
    """Outputs RH difference between measured and critical RH for each time step and two limits.
    Positive values imply how much RH exceed the critical RH. A low and upper critical RH are applied.

    Literature:
    """

    betas = {'a': 0.043, 'b': 0.036, 'c': 0.028, 'd': 0.021, 'e': 0.014}
    temperature = np.asarray(temperature)
    relative_humidity = np.asarray(relative_humidity)

    def relative_humidity_crit_low(temperature_):
        return 105 + betas[aed_group] * (temperature_ ** 2 - 54 * temperature_)

    def relative_humidity_crit_up(temperature_):
        return 105 + (betas[aed_group] - 0.007) * (temperature_ ** 2 - 54 * temperature_)

    difference_crit_low = relative_humidity - relative_humidity_crit_low(temperature)

    difference_crit_up = relative_humidity - relative_humidity_crit_up(temperature)

    logger.debug(f'Difference between relative humidity and lower critical value for {len(difference_crit_low)} values:'
                 f' Mean: {np.mean(difference_crit_low)}, StD: {np.std(difference_crit_low)}')
    logger.debug(f'Difference between relative humidity and upper critical value for {len(difference_crit_up)} values:'
                 f' Mean: {np.mean(difference_crit_up)}, StD: {np.std(difference_crit_up)}')

    return difference_crit_low.tolist(), difference_crit_up.tolist()


def algae(relative_humidity: typing.List[float], temperature: typing.List[float], material_name, porosity, roughness,
          total_pore_area):
    """Implement UNIVPM Algae Model
    Currently a dummy function!

    :param relative_humidity
    :param temperature
    :param material: dictionary with relevant properties and their values

    :return growth: list with eval. values
    """

    def extract_material_type(material: str):
        materials = {
            "BrickBernhard": "brick",
            "BrickJoens": "brick",
            "HistoricalBrickClusterEdge": "brick",
            "HistoricalBrickCluster4DD": "brick",
            "HistoricalBrickCluster": "brick",
            "WienerbergerNormalBrick": "brick",
            "AltbauziegelDresdenZQ": "brick",
            "AltbauziegelDresdenZA": "brick",
            "AltbauziegelDresdenZC": "brick",
            "AltbauziegelDresdenZD": "brick",
            "AltbauziegelDresdenZE": "brick",
            "AltbauziegelDresdenZF": "brick",
            "AltbauziegelDresdenZG": "brick",
            "AltbauziegelDresdenZH": "brick",
            "AltbauziegelDresdenZI": "brick",
            "AltbauziegelDresdenZJ": "brick",
            "AltbauziegelDresdenZK": "brick",
            "AltbauziegelDresdenZL": "brick",
            "AltbauziegelDresdenZM": "brick",
            "AltbauziegelDresdenZN": "brick",
            "AltbauziegelDresdenZO": "brick",
            "AltbauziegelElbphilharmonie": "brick",
            "WienerbergerHochlochBrick": "brick",
            "BrickWienerberger": "brick",
            "CeramicBrick": "brick",
            "AltbauklinkerHamburgHolstenkamp": "brick",
            "AltbauziegelAmWeinbergBerlin": "brick",
            "AltbauziegelAmWeinbergBerlininside": "brick",
            "AltbauziegelAussenziegelII": "brick",
            "AltbauziegelBolonga3enCult": "brick",
            "AltbauziegelDresdenZb": "brick",
            "AltbauziegelPersiusspeicher": "brick",
            "AltbauziegelReithallePotsdamAussenziegel1": "brick",
            "AltbauziegelReithallePotsdamAussenziegel2": "brick",
            "AltbauziegelReithallePotsdamAussenziegel3": "brick",
            "AltbauziegelRoteKasernePotsdamAussenziegel1": "brick",
            "AltbauziegelRoteKasernePotsdamAussenziegel2": "brick",
            "AltbauziegelRoteKasernePotsdamInnenziegel1": "brick",
            "AltbauziegelRoteKasernePotsdamInnenziegel2": "brick",
            "AltbauziegelSchlossGueterfeldeEGAussenwand1": "brick",
            "AltbauziegelSchlossGueterfeldeEGAussenwand2": "brick",
            "AltbauziegelTivoliBerlinAussenziegel1": "brick",
            "AltbauziegelTivoliBerlinAussenziegel2": "brick",
            "AltbauziegelTivoliBerlinInnenziegel": "brick",
            "AltbauziegelUSHauptquartierBerlin": "brick",
            "ZiegelSchlagmannVollziegel": "brick",
            "ZiegelSchlagmannWDZZiegelhuelle": "brick",
            "Brick": "brick",
            "LehmbausteinUngebrannt": "brick",
            "DTUBrick": "brick",
            "LimeSandBrickIndustrial": "brick",
            "LimeSandBrickTraditional": "brick",
            "SandstoneCotta": "sandstone",
            "SandstonePosta": "sandstone",
            "SandstoneReinhardsdorf": "sandstone",
            "WeatheredGranite": "sandstone",
            "BundsandsteinrotHessen": "sandstone",
            "CarraraMamor": "sandstone",
            "KrensheimerMuschelkalk": "sandstone",
            "SandsteinBadBentheim": "sandstone",
            "SandsteinHildesheim": "sandstone",
            "SandstoneIndiaNewSaInN": "sandstone",
            "SandsteinMuehlleiteeisenhaltigeBank": "sandstone",
            "SandsteinRuethen": "sandstone",
            "SandsteinVelbke": "sandstone",
            "Tuffstein": "other",
            "TuffsteinJapan": "other",
            "limesandstone": "sandstone",
            "LimeSandBrick": "limestone",
            "XellaKalksandstein": "sandstone",
            "KalksandsteinXellaYtong2002": "other",
            "KalksandsteinXellaYtong2004": "other",
            "BundsandsteinIndienHumayunVerwittert": "sandstone",
            "CarraraMamorSkluptur": "sandstone",
            "SandstoneArholzen": "sandstone",
            "SandstoneKarlshafener": "sandstone",
            "SandstoneKrenzheimer": "sandstone",
            "SandstoneMonteMerlo": "sandstone",
            "SandstoneOberkirchner": "sandstone",
            "SandstoneSander": "sandstone",
            "SandstoneSchleerither": "sandstone",
            "LimeSandbrick": "limestone",
            "Lime Cement Plaster Light": "limestone",
            "Lime Cement Mortar(High Cement Ratio)": "sandstone",
            "Lime Cement Mortar(Low Cement Ratio)": "limestone",
            "DTUMortar": "sandstone",
            "LimePlasterHist": "limestone"
        }

        return materials[material]

    def material_parameters(material_name):
        material_type = extract_material_type(material_name)
        default_parameters = {"alfa": 1, "beta": 1, "gamma": 1, "deltaA": 1, "etaA": 1, "lambdaA": 1, "muA": 1,
                              "deltaK": 1, "etaK": 1, "lambdaK": 1, "muK": 1}

        if material_type == 'sandstone':
            default_parameters.update({'alfa': 2, "beta": 1.724, "gamma": 0.2})

        elif material_type == 'limestone':
            default_parameters.update({'alfa': 100, "beta": 6.897, "gamma": 1.6})

        return default_parameters

    def create_a_parameters(porosity, roughness, material_parameters):
        A1 = 3.8447E-4
        A2 = -4.0800E-6
        A3 = -2.1164E-4
        B1 = -2.7874E-2
        B2 = 2.95905E-4
        B3 = 1.1856E-2
        C1 = 5.5270E-1
        C2 = -5.8670E-3
        C3 = -1.4727E-1
        D1 = -2.1146
        D2 = 2.2450E-2
        D3 = 4.7041E-1

        ra = material_parameters['deltaA'] * (A1 * porosity + A2 * roughness + A3)
        sa = material_parameters['etaA'] * (B1 * porosity + B2 * roughness + B3)
        ua = material_parameters['lambdaA'] * (C1 * porosity + C2 * roughness + C3)
        va = material_parameters['muA'] * (D1 * porosity + D2 * roughness + D3)

        return ra, sa, ua, va

    def create_k_parameters(porosity, roughness, material_parameters):
        E1 = 8.3270E-5
        E2 = 6.7E-7
        E3 = -1.8459E-4
        F1 = -6.0378E-3
        F2 = -4.88E-5
        F3 = 9.877E-3
        G1 = 1.1971E-1
        G2 = 9.69E-4
        G3 = -1.0759E-1
        H1 = -4.5803E-1
        H2 = -3.71E-3
        H3 = 3.1809E-1

        rk = material_parameters['deltaK'] * (E1 * porosity + E2 * roughness + E3)
        sk = material_parameters['etaK'] * (F1 * porosity + F2 * roughness + F3)
        uk = material_parameters['lambdaK'] * (G1 * porosity + G2 * roughness + G3)
        vk = material_parameters['muK'] * (H1 * porosity + H2 * roughness + H3)

        return rk, sk, uk, vk

    def initial_t(roughness, gamma):
        if roughness == 5.02:
            return 30
        else:
            return gamma * (5 / ((roughness - 5.02) ** 2))

    def create_ac_at(alfa, porosity, roughness):
        ac_at = (1 - np.exp(-alfa * (2.48 * porosity + 0.126 * roughness) ** 4))

        if ac_at < 0:
            ac_at = 0
        elif ac_at > 1:
            ac_at = 1

        return ac_at

    def create_k_rate_coefficient(beta, porosity, total_pore_area):
        k_rate_coefficient = (1 - np.exp(-beta * ((4.49e-3 * (porosity * total_pore_area) - 5.79e-3) / 2.09) ** 2))
        k_rate_coefficient = np.max([0.0, k_rate_coefficient])

        return k_rate_coefficient

    def tau_a_func(temp, ra, sa, ua, va):
        tau_a = ra * temp ** 3 + sa * temp ** 2 + ua * temp + va
        return float(np.clip(tau_a, 0, 1))

    def tau_k_func(temp, rk, sk, uk, vk):
        tau_k = rk * temp ** 3 + sk * temp ** 2 + uk * temp + vk
        return float(np.clip(tau_k, 0, 1))

    def favourable_growth_conditions(rh, temp, time, t1):
        if rh >= 0.98 and 5 < temp < 40 and time > t1:
            return True
        else:
            return False

    material = material_parameters(material_name)
    rk, sk, uk, vk = create_k_parameters(porosity, roughness, material)
    ra, sa, ua, va = create_a_parameters(porosity, roughness, material)
    t1 = initial_t(roughness, material['gamma'])
    ac_at = create_ac_at(material['alfa'], porosity, roughness)
    k_rate_coefficient = create_k_rate_coefficient(material['beta'], porosity, total_pore_area)
    covered_area = [0, ]

    for time in range(len(temperature)):
        temp = temperature[time]
        try:
            rh = relative_humidity[time]
        except IndexError:
            break

        if favourable_growth_conditions(rh, temp, time, t1):
            tau_a = tau_a_func(temp, ra, sa, ua, va)
            tau_k = tau_k_func(temp, rk, sk, uk, vk)

            if covered_area[-1] < tau_a * ac_at:
                delta_t = (-(1 / (tau_k * k_rate_coefficient)) * np.log(1 - (covered_area[-1] / (tau_a * ac_at)))) ** (
                        1 / 4) - (time - 1 - t1)
                covered_area.append(
                    tau_a * ac_at * (1 - np.exp(-tau_k * k_rate_coefficient * (time + delta_t - t1) ** 4)))
            else:
                covered_area.append(covered_area[-1])

        else:
            covered_area.append(covered_area[-1])

    return covered_area


def u_value(heat_loss: typing.Union[np.ndarray, list], exterior_temperature: typing.Union[np.ndarray, list],
            interior_temperature: typing.Union[np.ndarray, list], area=0.68) -> float:
    """Calculates the mean U-value given the outdoor and indoor temperature and the heat loss"""

    heat_loss = np.absolute(np.asarray(heat_loss))
    exterior_temperature = np.asarray(exterior_temperature)
    interior_temperature = np.asarray(interior_temperature)

    delta_temperature = np.absolute(exterior_temperature - interior_temperature)
    u_value_ = heat_loss / (delta_temperature * area)
    u_value_ = u_value_[~np.isinf(u_value_)]
    u_value_mean = np.nanmean(u_value_)

    logger.debug(f'Calculated U-value to: {u_value_mean}')

    return float(u_value_mean)
