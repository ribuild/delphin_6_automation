__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import numpy as np
import os

# RiBuild Modules:

# -------------------------------------------------------------------------------------------------------------------- #
# WEATHER MODELS


def convert_weather_to_indoor_climate(temperature: list, indoor_class, calculation_method='en15026') -> tuple:

    def en13788(indoor_class_: str, daily_temperature_average_: np.array) -> tuple:
        """
        Only the continental class is implemented.

        :param indoor_class_: Either a or b
        :type indoor_class_: str
        :param daily_temperature_average_: daily average of air temperature
        :type daily_temperature_average_: numpy array
        :return: Indoor temperature and relative humidity
        :rtype: tuple
        """

        if not isinstance(indoor_class, str):
            raise TypeError(f"Wrong indoor class. Type has to be a string. "
                            f"Value given was: >{indoor_class}< with type: {type(indoor_class)}")
        elif indoor_class_.lower() == 'a':
            delta_rh = 0
        elif indoor_class_.lower() == 'b':
            delta_rh = 0.05
        else:
            raise ValueError(f"Wrong indoor class. It has to be either a or b. Value given was: {indoor_class}")

        indoor_temperature_ = []
        indoor_relative_humidity_ = []

        # Create indoor temperature
        for t in daily_temperature_average_:
            if t <= 10:
                indoor_temperature_.append([20, ] * 24)
            elif t >= 20:
                indoor_temperature_.append([25, ] * 24)
            else:
                indoor_temperature_.append([0.5 * t + 15, ] * 24)

        # Create indoor relative humidity
        for rh in daily_temperature_average_:
            if rh <= -10:
                indoor_relative_humidity_.append([35 + delta_rh, ] * 24)
            elif rh >= 20:
                indoor_relative_humidity_.append([65 + delta_rh, ] * 24)
            else:
                indoor_relative_humidity_.append([rh + 45 + delta_rh, ] * 24)

        return list(np.ravel(indoor_temperature_)), list(np.ravel(indoor_relative_humidity_))

    def en15026(indoor_class_: str, daily_temperature_average_: np.array) -> tuple:
        """
        Only the continental class is implemented.

        :param indoor_class_: Either a or b
        :type indoor_class_: str
        :param daily_temperature_average_: daily average of air temperature
        :type daily_temperature_average_: numpy array
        :return: Indoor temperature and relative humidity
        :rtype: tuple
        """

        if not isinstance(indoor_class, str):
            raise TypeError(f"Wrong indoor class. Type has to be a string. "
                            f"Value given was: < {indoor_class} > with type: {type(indoor_class)}")
        elif indoor_class_.lower() == 'a':
            humidity_load = {'a': 30,
                             'b': 60,
                             'c': 40}
        elif indoor_class_.lower() == 'b':
            humidity_load = {'a': 40,
                             'b': 70,
                             'c': 50}
        else:
            raise ValueError(f"Wrong indoor class. It has to be either a or b. Value given was: {indoor_class}")

        indoor_temperature_ = []
        indoor_relative_humidity_ = []

        # Indoor temperature
        for i in range(len(daily_temperature_average_)):
            if daily_temperature_average_[i] < 10:
                indoor_temperature_.append([20, ] * 24)
            elif daily_temperature_average_[i] > 20:
                indoor_temperature_.append([25, ] * 24)
            else:
                indoor_temperature_.append([0.5 * daily_temperature_average_[i] + 15] * 24)

        # Indoor relative humidity
        for i in range(len(daily_temperature_average_)):
            if daily_temperature_average_[i] < -10:
                indoor_relative_humidity_.append([humidity_load['a'], ] * 24)
            elif daily_temperature_average_[i] > 20:
                indoor_relative_humidity_.append([humidity_load['b'], ] * 24)
            else:
                indoor_relative_humidity_.append([daily_temperature_average_[i] + humidity_load['c'], ] * 24)

        return list(np.ravel(indoor_temperature_)), list(np.ravel(indoor_relative_humidity_))

    # Create daily temperature average
    temperature = np.array(temperature).flatten()
    total_days = int(len(temperature)/24)
    temperature_matrix = np.reshape(temperature, (total_days, 24))
    daily_temperature_average = np.sum(temperature_matrix, 1) / 24

    if calculation_method == 'en15026':
        return en15026(indoor_class, daily_temperature_average)

    elif calculation_method == 'en13788':
        return en13788(indoor_class, daily_temperature_average)

    else:
        raise ValueError(f'The chosen calculation method is not recognized. Only en13788 or en15026 is allowed. '
                         f'Method given was: {calculation_method}')


def driving_rain(precipitation, wind_direction, wind_speed, location, orientation, inclination=90, ):

    # Load catch ratio and catch ratio parameters
    catch_ratio = np.load(os.path.join(os.path.dirname(__file__), 'data', 'catch_ratio.npy'))
    catch_parameters = {'height': [0.0, 5.0, 8.0, 8.5, 9.0, 9.25, 9.5, 9.75, 10.0],
                        'horizontal_rain_intensity': [0.0, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0,
                                                      12.0, 15.0, 20.0, 25.0, 30.0],
                        'width': [0.0, 2.5, 5.0, 7.5, 10.0],
                        'wind_speed': [0, 1, 2, 3, 4, 5, 6, 8, 10]}

    # Convert deg to rad
    orientation = np.deg2rad(orientation)
    inclination = np.deg2rad(inclination)
    wind_direction = np.array([np.deg2rad(direction)
                               for direction in wind_direction])

    # Calculate rain load on facade, for each time step
    wind_driven_rain = []

    for time_index in range(len(precipitation)):
        local_wind = wind_speed[time_index] * np.cos(wind_direction[time_index] - orientation)

        # Check if wind driven rain falls on facade
        if precipitation * local_wind > 0:
            pass

        else:
            wind_driven_rain.append(0)

    return wind_driven_rain


def calcRainLoad(path_climate, ori, number, loc=[5, 5], path_save=None):
    # If the inclination of the wall is not specified, set default incination 90 deg
    if not isinstance(ori, list):
        ori = [ori]
        ori.append(90)

    # Load catch ratio and catch ratio parameters
    catch_ratio = np.load(os.path.join(os.path.dirname(__file__), 'data', 'catch_ratio.npy'))
    catch_param = {'height': [0.0, 5.0, 8.0, 8.5, 9.0, 9.25, 9.5, 9.75, 10.0],
                   'horizontal rain intensity': [0.0, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0,
                                                 20.0, 25.0, 30.0],
                   'width': [0.0, 2.5, 5.0, 7.5, 10.0],
                   'wind speed': [0, 1, 2, 3, 4, 5, 6, 8, 10]}

    # Calculate rain load on facade, for each time step
    rain = list()
    rain_v = list()

    for t in range(len(rain_h)):
        # Wind speed at facade
        Vloc = windvel[t] * m.cos(winddir[t] - ori[1])
        # Check if wind driven rain falls on facade
        if rain_h[t] * Vloc > 0:
            
            # STEP 1: interpolation based on vertical and horizontal location
            # 1.1a Interpolation boundary for vertical location
            k = len(catch_param['height']) - 2
            for knm in range(len(catch_param['height']) - 1):
                if loc[0] >= catch_param['height'][knm] and loc[0] < catch_param['height'][knm + 1]:
                    k = knm
                    break
            
            # 1.1b Interpolation boundary for horizontal location
            l = len(catch_param['width']) - 2
            for lnm in range(len(catch_param['width']) - 1):
                if loc[1] >= catch_param['width'][lnm] and loc[1] < catch_param['width'][lnm + 1]:
                    l = lnm
                    break
            
            # 1.2 Interpolating horizontal and vertical location
            # interpolating horizontal location for vertical location 1
            x = loc[1]
            x1, x2 = catch_param['width'][l], catch_param['width'][l + 1]
            y1, y2 = catch_ratio[:, :, k, l], catch_ratio[:, :, k, l + 1]
            catc5 = y1 + (y2 - y1) * ((x - x1) / (x2 - x1))
            
            # interpolating horizontal location for vertical location 2
            y1, y2 = catch_ratio[:, :, k + 1, l], catch_ratio[:, :, k + 1, l + 1]
            catc6 = y1 + (y2 - y1) * ((x - x1) / (x2 - x1))
            
            # interpolating vertical location for interpolated horizontal location
            x = loc[0]
            x1, x2 = catch_param['height'][k], catch_param['height'][k + 1]
            catc = catc5 + (catc6 - catc5) * ((x - x1) / (x2 - x1))

            # STEP 2: interpolation based on wind speed and rain intensity
            # 2.1a Interpolation boundary for wind speed
            i = catc.shape[0] - 2
            for inm in range(catc.shape[0] - 1):
                if Vloc >= catch_param['wind speed'][inm] and Vloc < catch_param['wind speed'][inm + 1]:
                    i = inm
                    break
            
            # 2.1a Interpolation boundary for rain intensity
            j = catc.shape[1] - 2
            for jnm in range(catc.shape[1] - 1):
                if rain_h[t] >= catch_param['horizontal rain intensity'][jnm] and rain_h[t] < \
                        catch_param['horizontal rain intensity'][jnm + 1]:
                    j = jnm
                    break
            
            # 2.2 Interpolation wind speed and rain intensity
            # interpolating rain intensity for wind speed 1
            x = rain_h[t]
            x1, x2 = catch_param['horizontal rain intensity'][j], catch_param['horizontal rain intensity'][j + 1]
            y1, y2 = catc[i, j], catc[i, j + 1]
            cat5 = y1 + (y2 - y1) * ((x - x1) / (x2 - x1))
            
            # interpolating rain intensity for wind speed 2
            y1, y2 = catc[i + 1, j], catc[i + 1, j + 1]
            cat6 = y1 + (y2 - y1) * ((x - x1) / (x2 - x1))
            
            # interpolation wind speed for interpolated rain intensity
            x = Vloc
            x1, x2 = catch_param['wind speed'][i], catch_param['wind speed'][i + 1]
            cat = (cat5 + (cat6 - cat5) * (x - x1) / (x2 - x1))

            # STEP 3: Calculate wind driven rain
            rain_v.append(rain_h[t] * cat)

        # No wind driven rain on facade
        else:
            rain_v.append(0)

        # Calculate total rain load (horizontal + wind driven) on facade
        rain.append(round(rain_h[t] * m.cos(ori[1]) + rain_v[t] * m.sin(ori[1]), 8))


def short_wave_radiation():
    Pi2_365 = m.pi * 2 / 365
    Pi_180 = m.pi / 180
    Pi2 = m.pi * 2
    Kt1 = 10 + 365 / 4
    Fakt1 = -23.5
    Fakt2 = Fakt1 * Pi_180
    Fakt3 = Fakt1 * Pi_180 * Pi2_365

    def solar_time_shift(time_days):

        factor_1 = 1.1*10**-4
        factor_2 = 0.123*np.cos(2*time_days*180/365 + 85.88)
        factor_3 = 0.166*np.cos(4*time_days*180/365 + 108.896)
        factor_4 = 0.005645*np.cos(6*time_days*180/365+195.195)

        return factor_1 + factor_2 + factor_3 + factor_4

    def solar_time(time_days, longitude, time_hours=0, time_zone=1):
        return time_hours + solar_time_shift(time_days) + 1/15 * longitude - time_zone

    def solar_angle(time_days, longitude, time_hours=0, time_zone=1):
        """Calculates the solar angle in degrees"""

        return 15 * solar_time(time_days, longitude, time_hours, time_zone)

    def solar_declination(time_days):

        factor_1 = 23.256 * np.cos(2 * time_days * 180/365 + 9.053)
        factor_2 = 0.392 * np.cos(4 * time_days * 180/365 + 5.329)
        factor_3 = 0.176 * np.cos(6 * time_days * 180/365 - 10.084)

        return 0.395 - factor_1 - factor_2 - factor_3

    def ecliptical_length(time_days):
        return 0.986 * (time_days - 2.875) + 1.914 * np.sin(0.017 * (time_days - 2.875)) - 77.94

    def sun_height(geographical_location, time_days):
        delt = Fakt2 * np.sin(Pi2_365 * (time_days + Kt1))
        ret = np.sin(phi) * np.sin(delt)
        return ret - np.cos(phi) * np.cos(delt) * np.cos(Pi2 * time_days)

    return None


def calcSWRad(path_climate, ori, sun_abs, number, loc_geo=50.8, gr_relf=0.2, path_save=None):
    # Inner functions
    def signum(val):
        if val < 0.0:
            return -1.0
        else:
            return 1.0

    def f_deltG(t):
        return Fakt1 * m.sin(Pi2_365 * (t + Kt1))

    def f_delta(t):
        return f_deltG(t) * Pi_180

    def f_sin_h(phi, t):
        delt = Fakt2 * m.sin(Pi2_365 * (t + Kt1))
        ret = m.sin(phi) * m.sin(delt)
        return ret - m.cos(phi) * m.cos(delt) * m.cos(Pi2 * t)

    def f_cos_h(phi, t):
        sinh = f_sin_h(phi, t)
        return m.sqrt(1 - sinh * sinh)

    def f_h_t(phi, t):
        return m.asin(f_sin_h(phi, t))

    def f_D_t(sinh):
        if m.asin(sinh) >= 0.0:
            return 1.0
        else:
            return 0.0

    def f_sin_a(phi, t):
        ret = m.cos(f_delta(t)) * m.sin(Pi2 * t)
        return ret / f_cos_h(phi, t)

    def f_sinK1(t):
        return Fakt2 * m.sin(Pi2_365 * (t + Kt1))

    def f_cosK1(t):
        return Fakt3 * m.cos(Pi2_365 * (t + Kt1))

    def f_csKt(t):
        return m.cos(f_sinK1(t))

    def f_ssKt(t):
        return m.sin(f_sinK1(t))

    def f_dsin_a(phi, t):
        sPhi = m.sin(phi)
        cPhi = m.cos(phi)
        spi2t = m.sin(Pi2 * t)
        cpi2t = m.cos(Pi2 * t)
        CssKt = f_ssKt(t)
        CcsKt = f_csKt(t)
        fakt = sPhi * CssKt - cPhi * CcsKt * cpi2t
        Nenner = m.sqrt(1.0 - fakt * fakt)
        CcosK1 = f_cosK1(t)

        f1 = -CssKt * CcosK1 * spi2t / Nenner
        f1 = f1 + CcsKt * cpi2t * Pi2 / Nenner
        f2 = sPhi * CssKt - cPhi * CcsKt * cpi2t
        f2 = f2 * CcosK1 * (sPhi * CcsKt * + cPhi * CssKt * cpi2t) + cPhi * CcsKt * spi2t * Pi2
        f2 = f2 * CcsKt * spi2t / Nenner / Nenner
        return f1 + f2

    def f_a1(phi, t):
        ret = f_sin_a(phi, t) * -1.0
        return ret * signum(f_dsin_a(phi, t))

    def f_B2(sinh, beta, phi, t):
        sina = f_sin_a(phi, t)
        ret = m.sqrt(1.0 - sina * sina) * m.cos(beta) * signum(f_dsin_a(phi, t))
        ret = ret + sina * m.sin(beta)
        ret = ret / sinh
        return ret * m.sqrt(1.0 - sinh * sinh)

    def f_S(Dt, b2, alpha):
        calpha = m.cos(alpha)
        if Dt == 0.0 or calpha == 1.0:
            if calpha > 0.0:
                return 1.0
            else:
                return 0.0
        else:
            s1 = calpha + m.sin(alpha) * b2 * Dt
            if s1 > 0.0:
                return 1.0
            else:
                return 0.0

    # If the inclination of the wall is not specified, set default incination 90 deg
    if not isinstance(ori, list):
        ori = [ori]
        ori.append(90)
    # Load exterior climate (rain, wind direction, wind speed)
    if number != None and path_climate[-4:] == '%03i_' % number:
        dirrad = supp.readccd(path_climate + 'DirectRadiation.ccd')
        diffrad = supp.readccd(path_climate + 'DiffuseRadiation.ccd')
    else:
        dirrad = supp.readccd(path_climate + 'DirectRadiation.ccd')
        diffrad = supp.readccd(path_climate + 'DiffuseRadiation.ccd')
    # Parameters
    alpha = m.radians(ori[1])  # inlination, radians
    beta = m.radians(ori[0])  # orientation, radians
    phi = m.radians(loc_geo)  # geographical location, radians

    # Calculate H_soldir
    # f_DirRad
    f_DirRad = list()
    Pi2_365 = m.pi * 2 / 365
    Pi_180 = m.pi / 180
    Pi2 = m.pi * 2
    Kt1 = 10 + 365 / 4
    Fakt1 = -23.5
    Fakt2 = Fakt1 * Pi_180
    Fakt3 = Fakt1 * Pi_180 * Pi2_365
    for s in range(1, len(dirrad) + 1):  # Loop over time [h]
        t = s / 24  # Loop over time [d]
        sinh = f_sin_h(phi, t)  # sun height h
        Dt = f_D_t(sinh)
        if Dt == 0.0:  # if sun is to low, no radiation on surface
            f_DirRadfact = 0.0
        else:
            cB2 = f_B2(sinh, beta, phi, t)
            cS = f_S(Dt, cB2, alpha)
            if cS == 0.0:
                f_DirRadfact = 0.0
            else:
                ret = m.cos(alpha)
                ret = ret + m.sin(alpha) * cB2
                ret = ret * cS * Dt
                if ret < 0.0:
                    f_DirRadfact = 0.0
                else:
                    if ret > 5.0:
                        f_DirRadfact = 5.0
                    else:
                        f_DirRadfact = ret
        f_DirRad.append(f_DirRadfact)
    # H_soldir
    H_dir_n = [f * dirr for f, dirr in zip(f_DirRad, dirrad)]  # W/m2

    # Calculate H_soldiff
    H_diff_n = [
        m.cos(alpha / 2) * m.cos(alpha / 2) * diffr + gr_relf * m.sin(alpha / 2) * m.sin(alpha / 2) * (dirr + diffr) for
        diffr, dirr in zip(dirrad, diffrad)]  # W/m2

    # Calculate H_sol
    H_sol = [sun_abs * (Hdir + Hdiff) for Hdir, Hdiff in zip(H_dir_n, H_diff_n)]  # W/m2

    # Save short wave radiation to ccd or return rain load
    if path_save == None:
        return H_sol
    else:
        if number != None:
            supp.saveccd(os.path.join(path_save, '%03i_ShortWaveRadiation.ccd' % number), H_sol)
        else:
            supp.saveccd(os.path.join(path_save, 'ShortWaveRadiation.ccd'), H_sol)

