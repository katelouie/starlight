import datetime

import pytz
import timezonefinder
from geopy.geocoders import Nominatim
from rich.console import Console

from starlight.chart import create_table_midpoints  # format_long,
from starlight.chart import Chart, print_chart_summary

# Usage Example
birthdate = {"year": 1994, "month": 1, "day": 6, "hour": 11, "minute": 47}  # me
city_name = "San Francisco, CA"
# location = (37.386051, -122.083855)  # Todo: City -> Coordinates

# birthdate = {"year": 1982, "month": 2, "day": 9, "hour": 2, "minute": 0}
# location = (33.510414, 36.2768)  # Todo: City -> Coordinates

# birthdate = {"year": 1985, "month": 1, "day": 29, "hour": 14, "minute": 0}  # Nac
# location = (45.5152, -122.6784)  # Todo: City -> Coordinates # Portland

# birthdate = {"year": 1991, "month": 9, "day": 23, "hour": 13, "minute": 35}  # UTC Ann
# # location = (34.0549, -118.2426)  # Todo: City -> Coordinates
# city_name = "Los Angeles, CA"

# birthdate = {"year": 2025, "month": 2, "day": 1, "hour": 16, "minute": 1}  # UTC
# location = (47.6061, -122.3328)  # Todo: City -> Coordinates # Nova

# geolocator = Nominatim(user_agent="my_geocoder")

# # city_name = "Portland, OR"

# location = geolocator.geocode(city_name, language="en")

# if location:
#     print(city_name)
#     print(location)
#     print("Latitude:", location.latitude)
#     print("Longitude:", location.longitude)
# else:
#     print("Location not found.")

# print(birthdate)

# tf = timezonefinder.TimezoneFinder()
# timezone = tf.certain_timezone_at(lat=location.latitude, lng=location.longitude)

# if timezone is None:
#     print("Could not determine the time zone")
# else:
#     # Display the current time in that time zone
#     tz = pytz.timezone(timezone)
#     print(tz)
#     utc_timezone = pytz.utc
#     dt = datetime.datetime(**birthdate)
#     utc_time = dt.astimezone(utc_timezone)
#     print(utc_time)

# birthdate = {
#     "year": utc_time.year,
#     "month": utc_time.month,
#     "day": utc_time.day,
#     "hour": utc_time.hour,
#     "minute": utc_time.minute,
# }

chart = Chart(
    birthdate, "Whole Sign", loc_name=city_name
)  # Todo: Multiple house systems at once

# Set up console
console = Console()

# Print chart placements and aspects
console.print(create_table_midpoints(chart, plain=True))
# print_chart_summary(chart, console, plain=True)
# print(chart.cusps)
# print([x.long for x in chart.planets if x.name == "Moon"])
## WIP SVG - drawing the chart


def svg_example():
    canvas = svg.SVG(
        width=120,
        height=120,
        elements=[
            svg.Circle(
                cx=60,
                cy=50,
                r=20,
                stroke="black",
                fill="white",
                stroke_width=2,
            ),
            svg.Line(x1=60, y1=30, x2=60, y2=70, stroke="red", stroke_width=2),
        ],
    )
    return canvas


# im = svg_example()

# with open("svg_example_circle.svg", "w") as file:
#     file.write(str(im))
#     file.write(str(im))
