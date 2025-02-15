"""Define a chart (birth chart) object that contains objects and analysis."""

import copy
import os
from calendar import month_name
from datetime import datetime as dt
from typing import Union

import pytz
import svg
import svgwrite
import swisseph as swe
import timezonefinder
from geopy.geocoders import Nominatim
from rich.console import Console
from rich.table import Table

# from starlight.ephemeris import calc_aspect
from starlight.objects import (ASPECTS, Angle, Midpoint, Object, Planet,
                               format_long, format_long_sign,
                               get_ephemeris_object)


class Date:
    def __init__(
        self, year: int, month: int, day: int, hour: int = 12, minute: int = 00
    ) -> None:
        self.set_ephe_path()
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute

        self._calc_julian_day()

    def set_ephe_path(self):
        PATH_LIB = os.path.dirname(__file__) + os.sep
        PATH_DATA = PATH_LIB + "data" + os.sep

        swe.set_ephe_path(PATH_DATA + "swisseph" + os.sep + "ephe" + os.sep)

    def __str__(self) -> str:
        return (
            f"Date: {month_name[self.month]} {self.day}, {self.year}"
            f" at {self.hour}:{self.minute} Universal Time"
        )

    @property
    def has_time(self) -> bool:
        return self.hour is not None

    def _calc_julian_day(self) -> None:
        hour_decimal: float = self.minute / 60

        self.julian: float = swe.date_conversion(
            self.year, self.month, self.day, self.hour + hour_decimal
        )[1]


class Chart:
    def __init__(
        self,
        date: dict[str, int],
        houses: str,
        loc: Union[tuple[(float, float)], None] = None,
        loc_name: str = "",
    ) -> None:
        if loc is None and loc_name == "":
            raise ValueError("Need either coordinates or place name.")
        elif loc_name != "":
            self.loc_name = loc_name
            self.get_lat_long()
        else:
            self.loc = loc

        self.date = Date(**date)  # Date defaults to input local time
        self.date_raw = date
        self.house_system = houses
        self.loc_name = loc_name

        self.convert_time()

        self.objects: list[Object] = []
        self.objects_dict: dict[str, Object] = {}
        self.planets: list[Planet] = []
        self.angles: list[Angle] = []

        self.calc_julian()
        self._make_planets()
        self._make_houses_and_angles()
        self._make_lunar_parts()
        self._make_asteroids()
        self._make_midpoints()

    @property
    def lat(self) -> float:
        return self.loc[0]

    @property
    def long(self) -> float:
        return self.loc[1]

    @property
    def year(self) -> int:
        return self.date.year

    @property
    def month(self) -> int:
        return self.date.month

    @property
    def day(self) -> int:
        return self.date.day

    @property
    def hour(self) -> int:
        return self.date.hour

    @property
    def minute(self) -> int:
        return self.date.minute

    def calc_julian(self) -> None:
        self.julian = self.date.julian

    def _make_planets(self) -> None:
        # Main 10 Planets
        for id in range(10):
            try:
                planet = Planet(swe.get_planet_name(id), id, self.julian)
                self.objects.append(planet)
                self.objects_dict[planet.name] = planet
                self.planets.append(planet)
            except swe.Error as e:
                print(e)

    def _make_houses_and_angles(self) -> None:
        if self.house_system == "Placidus":
            system = b"P"
        elif self.house_system == "Whole Sign":
            system = b"W"
        else:
            return

        cusps, angles = swe.houses(self.julian, self.lat, self.long, hsys=system)
        self.cusps = cusps

        angle_labels = [
            "ASC",
            "MC",
            "ARMC",
            "VERTEX",
            "EQUASC",
            "COASC1",
            "COASC2",
            "POLASC",
            "NASCMC",
        ]
        for ix, value in enumerate(angles):
            angle = Angle(angle_labels[ix], value)
            self.objects.append(angle)
            self.objects_dict[angle.name] = angle
            self.angles.append(angle)

    def _make_lunar_parts(self) -> None:
        for swe_id in [11, 13]:  # [10, 11, 12, 13]:
            lunar_obj = Planet(swe.get_planet_name(swe_id), swe_id, self.julian)
            self.objects.append(lunar_obj)
            self.objects_dict[lunar_obj.name] = lunar_obj
            self.planets.append(lunar_obj)
            if swe_id == 11:  # add south node
                south_node = Object("South Node", "southnode")
                south_node.long = (lunar_obj.long + 180) % 360
                self.objects.append(south_node)
                self.objects_dict[south_node.name] = south_node
                self.planets.append(south_node)

    def _make_asteroids(self) -> None:
        for swe_id in [15, 16, 17, 18, 19, 20]:
            asteroid = Planet(swe.get_planet_name(swe_id), swe_id, self.julian)
            self.objects.append(asteroid)
            self.objects_dict[asteroid.name] = asteroid
            self.planets.append(asteroid)

    def calc_arabic_part(self, part_name: str) -> float | None:
        if part_name.lower() == "fortune":
            return self.angles[0].long + self.planets[0].long - self.planets[1].long
        else:
            return None

    def _make_midpoints(self):
        self.midpoints = []
        common_midpoints = [
            ("Sun", "Moon"),
            ("ASC", "MC"),
            ("Venus", "Mars"),
            ("Mercury", "Uranus"),
            ("Jupiter", "Saturn"),
            ("true Node", "South Node"),
            ("Moon", "Venus"),
            ("Moon", "Mars"),
            ("Sun", "Chiron"),
            ("Moon", "Chiron"),
            ("Venus", "Chiron"),
            ("ASC", "Chiron"),
            ("MC", "Chiron"),
            ("Mercury", "Chiron"),
            ("Mars", "Chiron"),
            ("Jupiter", "Chiron"),
            ("Saturn", "Chiron"),
        ]

        for pair in common_midpoints:
            object1 = self.objects_dict[pair[0]]
            object2 = self.objects_dict[pair[1]]
            self.midpoints.append(Midpoint(object1, object2))

    def print_date(self) -> None:
        print(f"{self.date} (Local {Date(**self.date_raw)})")

    def get_lat_long(self) -> None:
        # Get lat/long from geopy
        geolocator = Nominatim(user_agent="my_geocoder")
        location = geolocator.geocode(self.loc_name, language="en")

        if location:
            self.loc = (location.latitude, location.longitude)
            print(f"{location} ({self.loc[0]}, {self.loc[1]})")
        else:
            raise ValueError("Location not found.")

    def convert_time(self) -> None:
        # Convert local time to UTC for swisseph
        tf = timezonefinder.TimezoneFinder()
        timezone = tf.certain_timezone_at(lat=self.lat, lng=self.long)
        if timezone is None:
            print("Could not determine the time zone")
        else:
            tz = pytz.timezone(timezone)
            utc_timezone = pytz.utc
            print("Timezone:", tz)
            timestamp = dt(**self.date_raw)
            utc_time = timestamp.astimezone(utc_timezone)
            self.date = Date(
                **{
                    "year": utc_time.year,
                    "month": utc_time.month,
                    "day": utc_time.day,
                    "hour": utc_time.hour,
                    "minute": utc_time.minute,
                }
            )


# def format_long(long: float) -> str:
#     # Format longitude for printing in degrees - minutes - seconds: D°M'S".
#     degree = long % 30
#     min = (long % 1) * 60
#     sec = (min % 1) * 60

#     return f"{round(degree)}°{round(min)}'" + f'{round(sec)}"'


def get_planet_house(chart: Chart, p: Planet) -> int:
    cusp_list = list(chart.cusps)
    for i, c in enumerate(cusp_list):
        if (i == len(cusp_list) - 1) and (p.long >= c):
            return i + 1
        else:
            second_cusp = cusp_list[i + 1]
            if second_cusp < c:  # hit the end of the circle
                second_cusp += 360
            if p.long >= c and p.long < second_cusp:
                return i + 1


def create_table_planets(chart: Chart, plain: bool) -> Union[Table, str]:
    # Create a rich table of all planet placements for console printing.

    if plain is True:
        output = "Planet Placements\n"
        output += "-" * 60 + "\n"
        for p in chart.planets:
            house = get_planet_house(chart, p)
            display_name = get_ephemeris_object(p.swe)["alias"]
            output += f"{display_name:>13} | {p.sign:<12} | {p.sign_deg_str:<10} | House {house}\n"
            # if p.swe = 11 # North Node:
            #     # calculate south node and display
            #     output += f"{display_name.replace('North', 'South'):>13}" |
        return output

    else:
        table_planets = Table(title="Planet Placements")

        for column in ["Planet", "ID", "Sign", "Longitude", "Speed", "Sign Degrees"]:
            table_planets.add_column(column)

        for p in chart.planets:
            row = [
                p.name,
                str(p.swe),
                p.sign,
                f"{round(p.long, 2)}°",
                f"{round(p.speed_long, 2)}",
                p.sign_deg_str,
            ]
            table_planets.add_row(*row)

        return table_planets


def create_table_houses(chart: Chart, plain: bool) -> Union[Table, str]:
    # Create a rich table of house cusps.
    if plain is True:
        output = "House Cusps\n"
        output += "-" * 30 + "\n"
        for i, c in enumerate(chart.cusps):
            output += f"{i+1:>3} | {format_long_sign(c):<12} | {format_long(c):<10}\n"
        return output

    else:
        table_cusps = Table(title="House Cusps")
        for col in ["House", "Cusp Sign", "Cusp Degrees"]:
            table_cusps.add_column(col)

        for i, c in enumerate(chart.cusps):
            table_cusps.add_row(str(i + 1), format_long_sign(c), format_long(c))

        return table_cusps


def create_table_angles(chart: Chart, plain: bool) -> Union[Table, str]:
    # Create a rich table of chart angles.
    if plain is True:
        ...
        output = "Chart Angles\n"
        output += "-" * 30 + "\n"
        for angle in chart.angles:
            display_name = get_ephemeris_object(angle.name)["alias"]
            if angle.name in ["ASC", "MC", "VERTEX"]:
                output += f"{display_name:<6} | {format_long_sign(angle.long):<12} | {format_long(angle.long):<10}\n"
                if angle.name in ["ASC", "MC"]:
                    new_long = (angle.long + 180) % 360
                    if angle.name == "ASC":
                        new_name = "DSC"
                    if angle.name == "MC":
                        new_name = "IC"
                    new_dname = get_ephemeris_object(new_name)["alias"]
                    output += f"{new_dname:<6} | {format_long_sign(new_long):<12} | {format_long(new_long):<10}\n"
        return output
    else:

        table_angles = Table(title="Chart Angles")
        for col in ["Name", "ID", "Sign", "Degrees"]:
            table_angles.add_column(col)

        for angle in chart.angles:
            table_angles.add_row(
                angle.name,
                str(angle.swe),
                format_long_sign(angle.long),
                format_long(angle.long),
            )
            if angle.name in ["ASC", "MC"]:
                new_long = (angle.long + 180) % 360
                if angle.name == "ASC":
                    new_name = "DSC"
                if angle.name == "MC":
                    new_name = "IC"
                table_angles.add_row(
                    new_name,
                    str(angle.swe),
                    format_long_sign(new_long),
                    format_long(new_long),
                )

        return table_angles


ASPECT_COLORS = {
    "Conjunct": "white",
    "Square": "red",
    "Opposition": "red",
    "Sextile": "green",
    "Trine": "green",
}


def create_table_aspects(chart: Chart, plain: bool) -> Union[Table, str]:
    # Create a rich table of all planet aspects for console printing.
    if plain is True:
        output = "Planet Aspects\n"
        output += "-" * 60 + "\n"
        pairs = []
        for p in chart.planets:
            for other_obj in [*chart.planets, *chart.angles]:
                if (
                    (other_obj.name != p.name)
                    and (
                        other_obj.swe in list(range(12))
                        or other_obj.name in ["ASC", "MC", "DSC", "IC"]
                    )
                    and ((p, other_obj) not in pairs)
                ):
                    for a, v in ASPECTS.items():
                        aspect = p.aspect(other_obj, v["degree"], v["orb"])
                        if aspect[0]:
                            name1 = get_ephemeris_object(p.swe)["alias"]
                            if other_obj.swe is not None:
                                name2 = get_ephemeris_object(other_obj.swe)["alias"]
                            else:
                                name2 = get_ephemeris_object(other_obj.name)["alias"]
                            color = ASPECT_COLORS.get(a, "white")  # use white otherwise
                            output += f"{name1:>13} | {name2:<13} | [{color}]{a:<10}[/{color}] | {round(aspect[1]):>2}° | {aspect[3]}\n"
                            pairs.append((other_obj, p))
            output += "\n"

        return output
    else:
        table_aspects = Table(title="Planet Aspects")
        for col in ["Planet A", "Planet B", "Aspect", "Orb", "Movement"]:
            table_aspects.add_column(col)

        for p in chart.planets:
            if p.swe in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                # if True:
                for other_obj in [*chart.planets, *chart.angles]:
                    if (other_obj.name != p.name) and other_obj.swe in list(range(13)):
                        for a, v in ASPECTS.items():
                            aspect = p.aspect(other_obj, v["degree"], v["orb"])
                            if aspect[0]:
                                # print(p.name, other_obj.name, a, aspect)
                                row_list = [
                                    p.name,
                                    other_obj.name,
                                    a,
                                    f"{round(aspect[1])}°",
                                    aspect[3] if aspect[3] is not None else "-",
                                ]
                                table_aspects.add_row(*row_list)

        return table_aspects


def create_table_midpoints(chart: Chart, plain: bool) -> Union[Table, str]:
    if plain:
        output = "Chart Midpoints\n"
        output += "-" * 42 + "\n"
        for mp in chart.midpoints:
            name = f"{mp.obj1.name}-{mp.obj2.name}"
            output += f"{name:14} | {format_long_sign(mp.long):<12} | {format_long(mp.long):<10}\n"

        output += "\nMidpoint Aspects\n"
        output += "-" * 60 + "\n"
        for mp in chart.midpoints:
            name = f"{mp.obj1.name}-{mp.obj2.name}"
            for p in chart.planets:
                # use closer midpoint
                mp_2 = copy.deepcopy(mp)
                mp_2.long = (mp.long + 180) % 360
                if abs(p.long - mp.long) < abs(p.long - mp_2.long):
                    mp_close = mp
                else:
                    mp_close = mp_2
                for a, v in ASPECTS.items():
                    aspect = mp_close.aspect(p, v["degree"], v["orb"])
                    if aspect[0]:
                        color = ASPECT_COLORS.get(a, "white")  # use white otherwise
                        pname = get_ephemeris_object(p.swe)["alias"]
                        output += f"{name:>14} | {pname:<12} | [{color}]{a:<10}[/{color}] | {round(aspect[1]):>2}° | {aspect[3]}\n"
            output += "\n"
        return output

    else:
        ...


def print_chart_summary(chart: Chart, console: Console, plain: bool = False) -> None:
    # Prints birthdate, location (coord), planet table and aspect table to console.
    chart.print_date()
    console.print()
    console.print(create_table_planets(chart, plain=plain))
    console.print()
    console.print(create_table_houses(chart, plain=plain))
    console.print()
    console.print(create_table_angles(chart, plain=plain))
    console.print()
    console.print(create_table_aspects(chart, plain=plain))
