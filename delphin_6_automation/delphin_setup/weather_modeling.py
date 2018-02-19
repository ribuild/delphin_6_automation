__author__ = "Christian Kongsgaard"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import numpy as np
import datetime
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
            humidity_load = {'a':30,
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
                indoor_temperature_.append(20)
            elif daily_temperature_average_[i] > 20:
                indoor_temperature_.append(25)
            else:
                indoor_temperature_.append(0.5 * daily_temperature_average_[i] + 15)

        # Indoor relative humidity
        for i in range(len(daily_temperature_average_)):
            if daily_temperature_average_[i] < -10:
                indoor_relative_humidity_.append(humidity_load['a'])
            elif daily_temperature_average_[i] > 20:
                indoor_relative_humidity_.append(humidity_load['b'])
            else:
                indoor_relative_humidity_.append(daily_temperature_average_[i] + humidity_load['c'])

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



def driving_rain(vertical_rain, wind_direction, wind_speed, location, orientation, inclination=90,):

    # Load catch ratio and catch ratio parameters
    catch_ratio = np.load(os.path.join(os.path.dirname(__file__), 'data', 'catch_ratio.npy'))
    catch_parameters = {'height': [0.0, 5.0, 8.0, 8.5, 9.0, 9.25, 9.5, 9.75, 10.0],
                        'horizontal rain intensity': [0.0, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0,
                                                      12.0, 15.0, 20.0, 25.0, 30.0],
                        'width': [0.0, 2.5, 5.0, 7.5, 10.0],
                        'wind speed': [0, 1, 2, 3, 4, 5, 6, 8, 10]}

    # Convert deg to rad
    orientation = np.deg2rad(orientation)
    inclination = np.deg2rad(inclination)
    wind_direction = np.array([np.deg2rad(direction)
                               for direction in wind_direction])

    # Calculate rain load on facade, for each time step
    horizontal_rain = []
    wind_driven_rain = []

    for time_index in range(len(vertical_rain)):
        pass

    return None


"""
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
"""