from datetime import datetime

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

def create_datetime_utc(year: int, month: int, day: int, hour: int, minute: int, timezone_name: str) -> datetime:
    """Create a UTC datetime from local time and timezone."""
    # Create naive datetime (local time)
    local_dt = datetime(year, month, day, hour, minute)
    
    # Get timezone and localize
    tz = pytz.timezone(timezone_name)
    local_dt_aware = tz.localize(local_dt)
    
    # Convert to UTC
    return local_dt_aware.astimezone(pytz.UTC)


people = {
    "Me": {
        "datetime_utc": create_datetime_utc(1994, 1, 6, 11, 47, "America/Los_Angeles"),
        "city_name": "San Francisco, CA",
    },
    "Hussam": {
        "datetime_utc": create_datetime_utc(1982, 2, 9, 2, 0, "Asia/Damascus"),
        "city_name": "Damascus, Syria",
    },
    "Nac": {
        "datetime_utc": create_datetime_utc(1985, 1, 29, 14, 0, "America/Los_Angeles"),
        "city_name": "Portland, OR",
    },
    "Ann": {
        "datetime_utc": create_datetime_utc(1991, 9, 23, 13, 35, "America/Los_Angeles"),
        "city_name": "Los Angeles, CA",
    },
    "Nova": {
        "datetime_utc": create_datetime_utc(2025, 2, 1, 8, 1, "America/Los_Angeles"),
        "city_name": "Seattle, WA",
    },
    "Nova2": {
        "datetime_utc": create_datetime_utc(2025, 1, 30, 11, 21, "America/Los_Angeles"),
        "city_name": "Seattle, WA",
    },
    "Jules": {
        "datetime_utc": create_datetime_utc(1992, 11, 20, 16, 45, "Asia/Taipei"),
        "city_name": "Taipei, Taiwan",
    },
    "Person1": {
        "datetime_utc": create_datetime_utc(2004, 1, 28, 13, 23, "America/Sao_Paulo"),
        "city_name": "Petropolis, BR",
    },
    "Person2": {
        "datetime_utc": create_datetime_utc(1996, 4, 24, 10, 45, "Australia/Perth"),
        "city_name": "Perth, AU",
    },
    "Person3": {
        "datetime_utc": create_datetime_utc(1997, 12, 3, 21, 50, "Asia/Manila"),
        "city_name": "Quezon City, PH",
    },
    "Kwame": {
        "datetime_utc": create_datetime_utc(1989, 3, 31, 12, 0, "Africa/Accra"),
        "city_name": "Tema, Ghana",
    },
    "Chelsea": {
        "datetime_utc": create_datetime_utc(1991, 5, 2, 12, 0, "America/Los_Angeles"),
        "city_name": "Seattle, WA",
    },
    "Micah": {
        "datetime_utc": create_datetime_utc(1996, 3, 7, 12, 0, "America/Phoenix"),
        "city_name": "Phoenix, AZ",
    },
}

person = "Me"


def generate_chart(person: str, people: dict, houses: str = "Whole Sign"):
    chart = Chart(
        datetime_utc=people[person]["datetime_utc"],
        houses=houses,
        loc_name=people[person]["city_name"],
    )

    # Set up console
    console = Console()

    # Print chart placements and aspects
    console.print(create_table_dignities(chart, plain=True))
    print_chart_summary(chart, console, plain=True)
    console.print(create_table_midpoints(chart, plain=True))


## SVG - drawing the chart


def generate_drawing(person: str, people: dict, houses: str = "Whole Sign"):
    chart = Chart(
        datetime_utc=people[person]["datetime_utc"],
        houses=houses,
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
