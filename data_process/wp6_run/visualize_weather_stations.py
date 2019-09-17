__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pandas as pd
import plotly
import plotly.graph_objects as go
plotly.tools.set_credentials_file(username='thp44', api_key='rbwjjm28va')


# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def extract_location_from_filename(stations):
    longitude_list = []
    latitude_list = []

    for station in stations:
        longitude_list.append(station.split("_")[1])
        latitude_list.append(station.split("_")[2])

    return longitude_list, latitude_list


def stationXY(longitude_list, latitude_list, title_str):  # create plotly plot with all stations in Europe.
    df = pd.DataFrame({"lat": latitude_list, "long": longitude_list})

    scl = [[0, "rgb(5, 10, 172)"], [0.35, "rgb(40, 60, 190)"], [0.5, "rgb(70, 100, 245)"],
           [0.6, "rgb(90, 120, 245)"], [0.7, "rgb(106, 137, 247)"], [1, "rgb(220, 220, 220)"]]

    data = [dict(
        type='scattergeo',
        lon=df['long'],
        lat=df['lat'],

        mode='markers',
        marker=dict(
            size=5,
            opacity=0.6,
            reversescale=True,
            autocolorscale=False,
            symbol='square'
        ))]

    layout = dict(
        title=title_str,

        geo=dict(
            scope='europe',
            projection=dict(type='natural earth'),
            resolution=50,
            showland=True,
            landcolor="rgb(230, 230, 230)",
            subunitcolor="rgb(217, 217, 217)",
            countrycolor="rgb(150, 150, 150)",
            countrywidth=0.5,
            subunitwidth=0.5
        ),
    )

    fig = dict(data=data, layout=layout)
    #plotly.offline.plot(fig, filename=str(title_str) + '.html')
    figure = go.Figure(fig)
    figure.write_image(f"{title_str}.pdf")


with open(r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\wp6_run\inputs\weather_stations.txt') as file:
    weather_stations = file.readlines()

lat_lon_lists = extract_location_from_filename(weather_stations)

stationXY(lat_lon_lists[0], lat_lon_lists[1], "Weather Stations")
