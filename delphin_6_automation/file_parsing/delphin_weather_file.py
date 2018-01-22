__author__ = "Christian Kongsgaard"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import numpy as np

# RiBuild Modules:


# -------------------------------------------------------------------------------------------------------------------- #
# WEATHER PARSING

def dict_to_ccd(weather: dict, path: str) -> bool:
    """
    Takes an weather dict and converts it into a .ccd file

    :param weather: material dict
    :param path: Path to where .ccd should be placed.
    :return: True
    """

    # TODO - Create function
    return True


def convert_weather_to_indoor_climate(temperature: list, indoor_class) -> tuple:

    # Create daily temperature average
    temperature_matrix = np.reshape(temperature, (365, 24))
    daily_temperature_average = np.sum(temperature_matrix, 1) / 24

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

        if indoor_class_.lower() == 'a':
            delta_rh = 0
        elif indoor_class_.lower() == 'b':
            delta_rh = 5
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

    return en13788(indoor_class, daily_temperature_average)
