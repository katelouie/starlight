import datetime

import pytz
import timezonefinder
from geopy.geocoders import Nominatim
from rich.console import Console

from starlight.chart import create_table_midpoints  # format_long,
from starlight.chart import Chart, print_chart_summary

people = {
    "Me": {
        "birthdate": {"year": 1994, "month": 1, "day": 6, "hour": 11, "minute": 47},
        "city_name": "San Francisco, CA"
    },
    "Hussam": {
        "birthdate": {"year": 1982, "month": 2, "day": 9, "hour": 2, "minute": 0},
        "city_name": "Damascus, Syria"
    },
    "Nac": {
        "birthdate": {"year": 1985, "month": 1, "day": 29, "hour": 14, "minute": 0},
        "city_name": "Portland, OR"
    },
    "Ann": {
        "birthdate": {"year": 1991, "month": 9, "day": 23, "hour": 13, "minute": 35},
        "city_name": "Los Angeles, CA"
    },
    "Nova": {
        "birthdate": {"year": 2025, "month": 2, "day": 1, "hour": 8, "minute": 1},
        "city_name": "Seattle, WA"
    },
}

person = "Me"

chart = Chart(
    birthdate=people[person]["birthdate"], "Whole Sign", loc_name=city_name
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
