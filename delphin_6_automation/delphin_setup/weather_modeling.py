__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import numpy as np
import os
import pickle

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


def driving_rain(precipitation, wind_direction, wind_speed, wall_location, orientation, inclination=90, ):

    # Load catch ratio and catch ratio parameters
    catch_ratio_model = pickle.load(open(os.path.join(os.path.dirname(__file__), 'k_nearest_3_model.sav'), 'rb'))

    # Convert deg to rad
    orientation = np.deg2rad(orientation)
    inclination = np.deg2rad(inclination)
    wind_direction = np.array([np.deg2rad(direction)
                               for direction in wind_direction])

    # Calculate rain load on facade, for each time step
    wind_driven_rain = []

    for time_index in range(0, len(precipitation)):
        local_wind = wind_speed[time_index] * np.cos(wind_direction[time_index] - orientation)

        # Check if wind driven rain falls on facade
        if precipitation[time_index] * local_wind > 0:
            horizontal_rain = catch_ratio_model.predict([[local_wind, precipitation[time_index],
                                                        wall_location['height'], wall_location['width']]])
            wind_driven_rain.append(float(horizontal_rain * np.sin(inclination) +
                                    precipitation[time_index] * np.cos(inclination)))

        else:
            wind_driven_rain.append(precipitation[time_index] * np.cos(inclination))

    return list(wind_driven_rain)


def short_wave_radiation(radiation, longitude, latitude, hour_of_the_year, surface_angle, surface_azimuth):

    sin = lambda x: np.sin(np.radians(x))
    cos = lambda x: np.cos(np.radians(x))
    acos = lambda x: np.degrees(np.arccos(x))

    def day_of_year(hour_of_the_year: int) -> int:
        return int(hour_of_the_year / 24) + 1

    def hour_of_day(hour_of_the_year: int) -> int:
        return hour_of_the_year % 24

    def local_time_constant(longitude: float) -> float:
        """Local time constant K in minutes - DK: Lokal tids konstant"""

        time_median_longitude = int(longitude / 15) * 15
        longitude_deg = longitude / abs(longitude) * (abs(int(longitude)) + abs(longitude) % 1 * 100 / 60)
        local_time_constant = 4 * (time_median_longitude - longitude_deg)
        return local_time_constant

    def time_ekvation(day_of_year: int) -> float:
        """The difference between true solar time and mean solar time in Febuary (+/- 16 min) in minutes -
        DK: tidsækvationen"""

        b = (day_of_year - 1) * 360 / 365
        time_ekvation = 229.2 * (
                    0.000075 + 0.001868 * cos(b) - 0.032077 * sin(b) - 0.014615 * cos(2 * b) - 0.04089 * sin(2 * b))
        return time_ekvation

    def true_solar_time(hour_of_day: float, local_time_constant: float, time_ekvation: float) -> float:
        """True solar time in hours - DK: Sand soltid"""

        true_solar_time = hour_of_day + (local_time_constant - time_ekvation) / 60
        return true_solar_time

    def declination(day_of_year: int) -> float:
        """Deklination - Earth angle compared to route around sun"""

        deklination = 23.45 * sin(((284 + day_of_year) * 360) / 365)
        return deklination

    def latitude_deg(latitude: float) -> float:
        return latitude / abs(latitude) * (int(latitude) + abs(latitude) % 1 * 100 / 60)

    def time_angle(true_solar_time: float) -> float:
        time_angle = 15 * (true_solar_time - 12)
        return time_angle

    def incident_angle(declination: float, latitude_deg: float, surface_angle: float, surface_azimut: float,
                       time_angle: float) -> float:
        """... DK: Indfaldsvinklen"""

        incident_angle = acos(
            sin(declination) * (sin(latitude_deg) * cos(surface_angle) - cos(latitude_deg) * sin(surface_angle) * cos(
                surface_azimut)) + cos(declination) * (cos(latitude_deg) * cos(surface_angle) * cos(time_angle)
                                                       + sin(latitude_deg) * sin(surface_angle) * cos(
                        surface_azimut) * cos(time_angle)
                                                       + sin(surface_angle) * sin(surface_azimut) * sin(time_angle))
        )
        return incident_angle

    def zenit_angle(declination: float, latitude_deg: float, surface_angle: float, surface_azimut: float,
                    time_angle: float) -> float:
        """... DK: Zenitvinkelen"""

        zenit_angle = acos(
            sin(declination) * sin(latitude_deg) + cos(declination) * cos(latitude_deg) * cos(time_angle))
        return zenit_angle

    def radiation_ratio(incident_angle: float, zenit_angle: float) -> float:
        """... DK: Bestrålingsstyrkeforholdet"""

        radiation_ratio = cos(incident_angle) / cos(zenit_angle)
        return radiation_ratio

    def radiation_strength(radiation_ratio: float, radiation: float) -> float:
        """... DK: Bestrålingsstyrken"""

        return radiation_ratio * radiation

    day_of_year = day_of_year(hour_of_the_year)
    hour_of_day = hour_of_day(hour_of_the_year)
    local_time_constant = local_time_constant(longitude)
    time_ekvation = time_ekvation(day_of_year)
    true_solar_time = true_solar_time(hour_of_day, local_time_constant, time_ekvation)
    declination = declination(day_of_year)
    latitude_deg = latitude_deg(latitude)
    time_angle = time_angle(true_solar_time)
    incident_angle = incident_angle(declination, latitude_deg, surface_angle, surface_azimuth, time_angle)
    zenit_angle = zenit_angle(declination, latitude_deg, surface_angle, surface_azimuth, time_angle)
    radiation_ratio = radiation_ratio(incident_angle, zenit_angle)
    radiation_strength = radiation_strength(radiation_ratio, radiation)

    return radiation_strength
