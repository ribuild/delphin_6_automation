__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

import numpy as np
import typing


def algae(relative_humidity: typing.List[float], temperature: typing.List[float], material_name, porosity, roughness,
          total_pore_area):
    """
    UNIVPM Algae Model
    Currently a dummy function!

    :param relative_humidity
    :param temperature
    :param material_name: dictionary with relevant properties and their values

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
            "LimeCementMortar": "limestone",
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