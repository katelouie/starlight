import datetime

import pytz
import timezonefinder
from geopy.geocoders import Nominatim
from rich.console import Console

from starlight.chart import Chart
from starlight.presentation import (
    create_table_dignities,
    create_table_midpoints,
    print_chart_summary,
)
from starlight.drawing import (
    draw_moon_half_phased,
    draw_moon_half_phased_fixed,
    draw_moon_phase,
    draw_moon_phase_pil,
    draw_svg_chart,
)

people = {
    "Me": {
        "birthdate": {"year": 1994, "month": 1, "day": 6, "hour": 11, "minute": 47},
        "city_name": "San Francisco, CA",
    },
    "Hussam": {
        "birthdate": {"year": 1982, "month": 2, "day": 9, "hour": 2, "minute": 0},
        "city_name": "Damascus, Syria",
    },
    "Nac": {
        "birthdate": {"year": 1985, "month": 1, "day": 29, "hour": 14, "minute": 0},
        "city_name": "Portland, OR",
    },
    "Ann": {
        "birthdate": {"year": 1991, "month": 9, "day": 23, "hour": 13, "minute": 35},
        "city_name": "Los Angeles, CA",
    },
    "Nova": {
        "birthdate": {"year": 2025, "month": 2, "day": 1, "hour": 8, "minute": 1},
        "city_name": "Seattle, WA",
    },
    "Nova": {
        "birthdate": {"year": 2025, "month": 2, "day": 1, "hour": 8, "minute": 1},
        "city_name": "Seattle, WA",
    },
    "Nova2": {
        "birthdate": {"year": 2025, "month": 1, "day": 30, "hour": 11, "minute": 21},
        "city_name": "Seattle, WA",
    },
    "Jules": {
        "birthdate": {"year": 1992, "month": 11, "day": 20, "hour": 16, "minute": 45},
        "city_name": "Taipei, Taiwan",
    },
    "Person1": {
        "birthdate": {"year": 2004, "month": 1, "day": 28, "hour": 13, "minute": 23},
        "city_name": "Petropolis, BR",
    },
    "Person2": {
        "birthdate": {"year": 1996, "month": 4, "day": 24, "hour": 10, "minute": 45},
        "city_name": "Perth, AU",  # Unknown, Cancer 18 asc
    },
    "Person3": {
        "birthdate": {"year": 1997, "month": 12, "day": 3, "hour": 21, "minute": 50},
        "city_name": "Quezon City, PH",  # Unknown, Cancer 18 asc
    },
    "Kwame": {
        "birthdate": {"year": 1989, "month": 3, "day": 31, "hour": 12, "minute": 00},
        "city_name": "Tema, Ghana",  # Unknown birth time
    },
    "Chelsea": {
        "birthdate": {"year": 1991, "month": 5, "day": 2, "hour": 12, "minute": 00},
        "city_name": "Seattle, WA",  # Unknown birth time and location
    },
    "Micah": {
        "birthdate": {"year": 1996, "month": 3, "day": 7, "hour": 12, "minute": 00},
        "city_name": "Phoenix, AZ",  # Unknown birth time and location
    },
}

person = "Me"


def generate_chart(person: str, people: dict, houses: str = "Whole Sign"):
    chart = Chart(
        date=people[person]["birthdate"],
        houses="Whole Sign",
        loc_name=people[person]["city_name"],
    )  # Todo: Multiple house systems at once

    # Set up console
    console = Console()

    # Print chart placements and aspects
    console.print(create_table_dignities(chart, plain=True))
    print_chart_summary(chart, console, plain=True)
    console.print(create_table_midpoints(chart, plain=True))


## SVG - drawing the chart


def generate_drawing(person: str, people: dict, houses: str = "Whole Sign"):
    chart = Chart(
        date=people[person]["birthdate"],
        houses="Whole Sign",
        loc_name=people[person]["city_name"],
    )
    draw_svg_chart(chart, filename="nova_chart.svg")


def generate_moon_svg():
    for angle in [
        0,
        45,
        90,
        135,
        180,
        225,
        270,
        315,
    ]:  # New Moon, First Q, Full, Last Q
        # draw_moon_phase(angle, filename=f"moon_phase_{angle}.svg")
        draw_moon_half_phased(angle, filename=f"moon_phase_{angle}.svg")


if __name__ == "__main__":
    # generate_drawing("Ann", people, houses="Placidus")

    # # Example usage:
    # moon_img = draw_moon_phase_pil(45)  # Waxing Crescent
    # moon_img.show()

    generate_moon_svg()
