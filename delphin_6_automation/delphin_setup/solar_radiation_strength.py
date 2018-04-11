longitude = -122.25
latitude = 37.46
radiation = 200
hour_of_the_year = 28*24+10
surface_angle = 45.0
surface_azimut = 22.5

sin = lambda x: math.sin(math.radians(x))
cos = lambda x: math.cos(math.radians(x))
acos = lambda x: math.degrees(math.acos(x))

def day_of_year(hour_of_the_year: int) -> int:
    return int(hour_of_the_year / 24) + 1


def hour_of_day(hour_of_the_year: int) -> int:
    return hour_of_the_year % 24


def local_time_constant(longitude: float) -> float:
    """Local time constant K in minutes - DK: Lokal tids konstant"""
    time_median_longitude = int(longitude/15)*15
    longitude_deg = longitude / abs(longitude) * (abs(int(longitude)) + abs(longitude) % 1 * 100 / 60)
    local_time_constant = 4 * (time_median_longitude - longitude_deg)
    return local_time_constant


def time_ekvation(day_of_year: int) -> float:
    """The difference between true solar time and mean solar time in Febuary (+/- 16 min) in minutes -  DK: tidsækvationen"""
    b = (day_of_year - 1) * 360 / 365
    time_ekvation = 229.2 * (0.000075 + 0.001868 * cos(b) - 0.032077 * sin(b) - 0.014615 * cos(2*b) - 0.04089 * sin(2*b))
    return time_ekvation


def true_solar_time(hour_of_day: float, local_time_constant: float, time_ekvation: float) -> float:
    """True solar time in hours - DK: Sand soltid"""
    true_solar_time = hour_of_day + (local_time_constant - time_ekvation) / 60
    return true_solar_time


def declination(day_of_year: int) -> float:
    """Deklination - Earth angle compared to route around sun"""
    deklination = 23.45 * sin(((284 + day_of_year)*360)/365)
    return deklination


def latitude_deg(latitude: float) -> float:
    return  latitude / abs(latitude) * (int(latitude) + abs(latitude) % 1 * 100 / 60)


def time_angle(true_solar_time: float) -> float:
    time_angle = 15 * (true_solar_time - 12)
    return time_angle


def incident_angle(declination: float, latitude_deg: float, surface_angle: float, surface_azimut: float, time_angle: float) -> float:
    """... DK: Indfaldsvinklen"""

    incident_angle = acos(
    sin(declination)*(sin(latitude_deg)*cos(surface_angle)-cos(latitude_deg)*sin(surface_angle)*cos(surface_azimut))+cos(declination)*(cos(latitude_deg)*cos(surface_angle)*cos(time_angle)
    +sin(latitude_deg)*sin(surface_angle)*cos(surface_azimut)*cos(time_angle)
    +sin(surface_angle)*sin(surface_azimut)*sin(time_angle))
    )
    return incident_angle


def zenit_angle(declination: float, latitude_deg: float, surface_angle: float, surface_azimut: float, time_angle: float) -> float:
    """... DK: Zenitvinkelen"""
    zenit_angle = acos(sin(declination)*sin(latitude_deg)+cos(declination)*cos(latitude_deg)*cos(time_angle))
    return zenit_angle


def radiation_ratio(incident_angle: float, zenit_angle: float) -> float:
    """... DK: Bestrålingsstyrkeforholdet"""
    radiation_ratio = cos(incident_angle)/cos(zenit_angle)
    return radiation_ratio


def radiation_strength(radiation_ratio: float, radiation: float) -> float:
    """... DK: Bestrålingsstyrken"""
    return radiation_ratio*radiation


day_of_year = day_of_year(hour_of_the_year)
hour_of_day = hour_of_day(hour_of_the_year)
local_time_constant = local_time_constant(longitude)
time_ekvation = time_ekvation(day_of_year)
true_solar_time = true_solar_time(hour_of_day, local_time_constant, time_ekvation)
declination = declination(day_of_year)
latitude_deg = latitude_deg(latitude)
time_angle = time_angle(true_solar_time)
incident_angle = incident_angle(declination, latitude_deg, surface_angle, surface_azimut, time_angle)
zenit_angle = zenit_angle(declination, latitude_deg, surface_angle, surface_azimut, time_angle)
radiation_ratio = radiation_ratio(incident_angle, zenit_angle)
radiation_strength = radiation_strength(radiation_ratio, radiation)

print(radiation_strength)

# TODO - Build this sh#t into the project...
