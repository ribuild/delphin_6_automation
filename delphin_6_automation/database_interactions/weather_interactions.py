__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:


# RiBuild Modules:
from delphin_6_automation.nosql.db_templates import delphin_entry as delphin_db

# -------------------------------------------------------------------------------------------------------------------- #
# WEATHER INTERACTIONS


def dict_to_ccd(weather: dict, path: str) -> bool:
    """
    Takes an weather dict and converts it into a .ccd file
    :param weather: material dict
    :param path: Path to where .ccd should be placed.
    :return: True
    """

    # TODO - Create function
    return True


def list_project_weather(sim_id: str) -> list:
    """
    Returns a list with the weather in a project entry.
    :param sim_id: Delphin entry ID
    :return: List with material file names
    """

    weather = delphin_db.Delphin.objects(id=sim_id).first().dp6_file.DelphinProject.Conditions.ClimateConditions.ClimateCondition

    weather_list = [(w.type, w.Filename)
                    for w in weather]

    return weather_list


def assign_weather_to_project():
    """
    Assign weather to a Delphin entry
    :return:
    """

    # TODO - Create function
    return None
