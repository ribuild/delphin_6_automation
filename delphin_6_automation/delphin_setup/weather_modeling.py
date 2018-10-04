__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import numpy as np
from sklearn.externals import joblib
import os
import typing

# RiBuild Modules:
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# WEATHER MODELS


def convert_weather_to_indoor_climate(temperature: list, indoor_class, calculation_method='en15026') \
        -> typing.Tuple[typing.Iterable, typing.Iterable]:
    """
    Calculates the indoor climate based on the outdoor temperature and the indoor class.
    Can either be calculated as EN13788 or EN15026
    """

    # Create daily temperature average
    temperature = np.array(temperature).flatten()
    total_days = int(len(temperature) / 24)
    temperature_matrix = np.reshape(temperature, (total_days, 24))
    daily_temperature_average = np.sum(temperature_matrix, 1) / 24

    if calculation_method == 'en15026':
        logger.debug(f'Calculates indoor climate after EN15026')
        return en15026(indoor_class, daily_temperature_average)

    elif calculation_method == 'en13788':
        logger.debug(f'Calculates indoor climate after EN13788')
        return en13788(indoor_class, daily_temperature_average)

    else:
        raise ValueError(f'The chosen calculation method is not recognized. Only en13788 or en15026 is allowed. '
                         f'Method given was: {calculation_method}')


def en15026(indoor_class: str, daily_temperature_average_: np.ndarray) \
        -> typing.Tuple[typing.Iterable, typing.Iterable]:
    """
    Calculates the indoor climate after EN15026.
    Only the continental class is implemented.

    :param indoor_class: Either a or b
    :param daily_temperature_average_: daily average of air temperature
    :return: Indoor temperature and relative humidity
    """

    if not isinstance(indoor_class, str):
        raise TypeError(f"Wrong indoor class. Type has to be a string. "
                        f"Value given was: < {indoor_class} > with type: {type(indoor_class)}")
    elif indoor_class.lower() == 'a':
        humidity_load = {'a': 30,
                         'b': 60,
                         'c': 40}
    elif indoor_class.lower() == 'b':
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

    return np.ravel(indoor_temperature_).tolist(), np.ravel(indoor_relative_humidity_).tolist()


def en13788(indoor_class: str, daily_temperature_average_: np.array) -> typing.Tuple[typing.Iterable, typing.Iterable]:
    """
    Calculates the indoor climate after EN13788.
    Only the continental class is implemented.

    :param indoor_class: Either a or b
    :param daily_temperature_average_: daily average of air temperature
    :return: Indoor temperature and relative humidity
    """

    if not isinstance(indoor_class, str):
        raise TypeError(f"Wrong indoor class. Type has to be a string. "
                        f"Value given was: >{indoor_class}< with type: {type(indoor_class)}")
    elif indoor_class.lower() == 'a':
        delta_rh = 0
    elif indoor_class.lower() == 'b':
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

    return np.ravel(indoor_temperature_).tolist(), np.ravel(indoor_relative_humidity_).tolist()


def driving_rain(precipitation: list, wind_direction: list, wind_speed: list, wall_location: dict,
                 orientation: typing.Union[int, float], inclination=90, catch_ratio=None) -> typing.Iterable:
    """
    Calculates the driving rain load on a wall.

    Source:
    Blocken, B, and J Carmeliet. 2002.
    “Spatial and Temporal Distribution of Driving Rain on a Low-Rise Building.”
    Wind and Structures 5 (5).
    TECHNO-PRESS: 441–62.
    """

    # Convert to NumPy
    precipitation = np.asarray(precipitation)
    wind_direction = np.asarray(wind_direction)
    wind_speed = np.asarray(wind_speed)

    # Load catch ratio and catch ratio parameters
    model_path = os.path.join(os.path.dirname(__file__), 'k_nearest_3_model.joblib')
    catch_ratio_model = joblib.load(model_path)

    # Convert deg to rad
    orientation = np.deg2rad(orientation)
    inclination = np.deg2rad(inclination)
    wind_direction = np.deg2rad(wind_direction)

    # Calculate rain load on facade, for each time step
    wind_driven_rain = np.zeros(len(precipitation))

    local_wind = wind_speed * np.cos(wind_direction - orientation)
    rain_hit = precipitation * local_wind > 0

    if not catch_ratio:
        horizontal_rain = catch_ratio_model.predict([local_wind[rain_hit], precipitation[rain_hit],
                                                     np.ones(len(local_wind[rain_hit])) * wall_location['height'],
                                                     np.ones(len(local_wind[rain_hit])) * wall_location['width']])
        wind_driven_rain[rain_hit] = horizontal_rain * np.sin(inclination) + precipitation[rain_hit] * np.cos(
            inclination)
    else:
        wind_driven_rain[rain_hit] = catch_ratio * precipitation[rain_hit] * np.sin(inclination) + \
                                     precipitation[rain_hit] * np.cos(inclination)

    wind_driven_rain[~rain_hit] = precipitation[~rain_hit] * np.cos(inclination)

    return wind_driven_rain.tolist()


def short_wave_radiation(radiation: np.array, longitude: float, latitude: float,
                         inclination: float, orientation: float) -> list:
    """
    Calculates the short wave radiation on a wall.

    Source:
    Svendsen, S.Å., Danmarks tekniske højskole, DTH, and LfV.
    1984.
    Solstråling. Laboratoriet for Varmeisolering,
    """

    hour_of_the_year = np.array([int(i) for i in range(8760)] * int(len(radiation) / 8760))

    def sin_deg(x):
        return np.sin(np.radians(x))

    def cos_deg(x):
        return np.cos(np.radians(x))

    def arccos_deg(x):
        return np.degrees(np.arccos(x))

    def day_of_year(hour_of_the_year_: np.array) -> np.array:
        return (hour_of_the_year_ / 24).astype(int) + 1

    def hour_of_day(hour_of_the_year_: np.array) -> np.array:
        return hour_of_the_year_ % 24

    def local_time_constant(longitude_: float) -> float:
        """Local time constant K in minutes - DK: Lokal tids konstant"""

        time_median_longitude = int(longitude_ / 15) * 15
        longitude_deg = longitude / abs(longitude_) * (abs(int(longitude_)) + abs(longitude_) % 1 * 100 / 60)

        return 4 * (time_median_longitude - longitude_deg)

    def time_ecvation(day_of_year_: np.array) -> np.array:
        """The difference between true solar time and mean solar time in Febuary (+/- 16 min) in minutes -
        DK: tidsækvationen"""

        b = (day_of_year_ - 1) * 360 / 365

        return 229.2 * (0.000075 + 0.001868 * cos_deg(b) - 0.032077 * sin_deg(b) - 0.014615 * cos_deg(
            2 * b) - 0.04089 * sin_deg(2 * b))

    def true_solar_time(hour_of_day_: np.array, local_time_constant_: float, time_ecvation_: np.array) -> np.array:
        """True solar time in hours - DK: Sand soltid"""

        return hour_of_day_ + (local_time_constant_ - time_ecvation_) / 60

    def declination(day_of_year_: np.array) -> np.array:
        """Declination - Earth angle compared to route around sun"""

        return 23.45 * sin_deg(((284 + day_of_year_) * 360) / 365)

    def latitude_deg(latitude_: float) -> float:
        return latitude_ / abs(latitude_) * (int(latitude_) + abs(latitude_) % 1 * 100 / 60)

    def time_angle(true_solar_time_: np.array) -> np.array:
        return 15 * (true_solar_time_ - 12)

    def incident_angle(declination_: np.array, latitude_deg_: float, surface_angle: float, surface_azimuth: float,
                       time_angle_: np.array) -> np.array:
        """... DK: Indfaldsvinklen"""

        incident_angle_ = arccos_deg(
            sin_deg(declination_) * (sin_deg(latitude_deg_) * cos_deg(surface_angle) - cos_deg(latitude_deg_) * sin_deg(
                surface_angle) * cos_deg(
                surface_azimuth)) + cos_deg(declination_) * (
                        cos_deg(latitude_deg_) * cos_deg(surface_angle) * cos_deg(time_angle_)
                        + sin_deg(latitude_deg_) * sin_deg(surface_angle) * cos_deg(
                    surface_azimuth) * cos_deg(time_angle_)
                        + sin_deg(surface_angle) * sin_deg(surface_azimuth) * sin_deg(time_angle_))
        )
        return incident_angle_

    def zenith_angle(declination_: np.array, latitude_deg_: float, time_angle_: float) -> np.array:
        """... DK: Zenitvinkelen"""

        return arccos_deg(
            sin_deg(declination_) * sin_deg(latitude_deg_) + cos_deg(declination_) * cos_deg(latitude_deg_) * cos_deg(
                time_angle_))

    def radiation_ratio(incident_angle_: np.array, zenith_angle_: np.array) -> np.array:
        """... DK: Bestrålingsstyrkeforholdet"""

        return np.maximum(0, cos_deg(incident_angle_) / cos_deg(zenith_angle_))

    def radiation_strength(radiation_ratio_: np.array, radiation_: np.array) -> np.array:
        """... DK: Bestrålingsstyrken"""

        return radiation_ratio_ * radiation_

    day_of_year = day_of_year(hour_of_the_year)
    hour_of_day = hour_of_day(hour_of_the_year)
    local_time_constant = local_time_constant(longitude)
    time_ecvation = time_ecvation(day_of_year)
    true_solar_time = true_solar_time(hour_of_day, local_time_constant, time_ecvation)
    declination = declination(day_of_year)
    latitude_deg = latitude_deg(latitude)
    time_angle = time_angle(true_solar_time)
    incident_angle = incident_angle(declination, latitude_deg, inclination, orientation, time_angle)
    zenith_angle = zenith_angle(declination, latitude_deg, inclination)
    radiation_ratio = radiation_ratio(incident_angle, zenith_angle)

    return radiation_strength(radiation_ratio, radiation).tolist()
