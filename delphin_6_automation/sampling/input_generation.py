__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def heat_conduction_interior(random_number):

    return 5 + 5 * random_number


def heat_conduction_exterior(random_number):

    return 1 + 3 * random_number


def vapour_diffusion(random_number, heat_conduction):

    a = 4 * 10**-9 + random_number * 6 * 10**-9
    return a * heat_conduction


def short_wave(random_number):

    return 0.4 + random_number * 0.4


def rain_exposure(random_number):

    return random_number * 2.0


def orientation(random_number):

    return random_number * 360


def indoor_climate(random_number):

    if random_number > 0.5:
        return 'a'

    else:
        return 'b'

