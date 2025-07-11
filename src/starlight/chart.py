"""Define a chart (birth chart) object that contains objects and analysis."""

import copy
import os
from calendar import month_name
from datetime import datetime as dt
from typing import Union

import pytz
import swisseph as swe
import timezonefinder
from geopy.geocoders import Nominatim

from starlight.objects import (
    Angle,
    Midpoint,
    Object,
    Planet,
)


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
        time_known: bool = True,
    ) -> None:
        if loc is None and loc_name == "":
            raise ValueError("Need either coordinates or place name.")
        elif loc_name != "":
            self.loc_name = loc_name
            self.get_lat_long()
        else:
            self.loc = loc

        self.date = Date(**date)  # Date defaults to input local time as UTC
        self.date_raw = date
        self.house_system = houses
        self.loc_name = loc_name
        self.is_time_known = time_known

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
                south_node = copy.deepcopy(lunar_obj)
                south_node.name = "South Node"
                south_node.swe = "southnode"
                south_node.long = (lunar_obj.long + 180) % 360
                south_node._make_sign_pos()
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
        tz = pytz.timezone(self.timezone)
        print(f"{self.date} (Local: {tz.localize(dt(**self.date_raw))})")

    def get_lat_long(self) -> None:
        # Get lat/long from geopy
        geolocator = Nominatim(user_agent="my_geocoder")
        location = geolocator.geocode(self.loc_name, language="en")

        if location:
            self.loc = (location.latitude, location.longitude)
            print(f"{location} ({self.loc[0]}, {self.loc[1]})")
        else:
            raise ValueError("Location not found.")
        
    def get_timezone(self) -> None:
        # Get timezone from timezonefinder
        tf = timezonefinder.TimezoneFinder()
        timezone = tf.certain_timezone_at(lat=self.lat, lng=self.long)
        if timezone is None:
            print("Could not determine the time zone")
            self.timezone = None
        else:
            self.timezone = timezone
            print(f"Timezone: {self.timezone}")

    def attach_timezone(self) -> None:
        tz = pytz.timezone(self.timezone)
        self.date_local = tz.localize(datetime.datetime(**self.date))
        self.date_utc = self.date_local.astimezone(pytz.utc)
        self.date_julian = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                     utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600,
                     swe.GREG_CAL)

    def convert_time(self) -> None:
        # Convert local time to UTC for swisseph
        tf = timezonefinder.TimezoneFinder()
        timezone = tf.certain_timezone_at(lat=self.lat, lng=self.long)
        if timezone is None:
            print("Could not determine the time zone")
            self.timezone = None
        else:
            self.timezone = timezone
            tz = pytz.timezone(timezone)
            utc_timezone = pytz.utc
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
    
    def get_planet_house(self, p: Planet) -> int:
        """Calculate which house a planet is in based on house cusps."""
        cusp_list = list(self.cusps)
        for i, c in enumerate(cusp_list):
            if (i == len(cusp_list) - 1) and (p.long >= c):
                return i + 1
            else:
                second_cusp = cusp_list[i + 1]
                if second_cusp < c:  # hit the end of the circle
                    second_cusp += 360
                if p.long >= c and p.long < second_cusp:
                    return i + 1
        return 1  # fallback
    
    def get_sect(self) -> str:
        """Determine if chart is a day or night chart."""
        asc = self.objects_dict["ASC"]
        sun = self.objects_dict["Sun"]
        
        desc_long = (asc.long + 180) % 360
        sect = "Night"  # Default
        
        if asc.long < desc_long:
            if sun.long >= desc_long:
                sect = "Day"
        elif asc.long > desc_long:
            if (sun.long >= desc_long) and (sun.long < asc.long):
                sect = "Day"
        
        return sect
    
    def get_planetary_dignities(self) -> dict:
        """Calculate planetary dignity scores."""
        from starlight.signs import DIGNITIES
        from starlight.objects import format_long
        
        core_names = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        
        scores = {
            "ruler": 5,
            "exhalt": 4,
            "triplicity": 3,
            "bound": 2,
            "decan": 1,
            "detriment": -5,
            "fall": -4,
        }
        
        planet_scores = {}
        core_planets = [self.objects_dict[name] for name in core_names]
        
        for p in core_planets:
            planet_scores[p.name] = 0
            sign_dict = DIGNITIES[p.sign]
            sign_pos = int(format_long(p.long).split("°")[0])
            essential_dict = sign_dict["traditional"]
            # TODO: Complete dignity calculation
        
        return planet_scores
    
    def get_all_aspects(self) -> list[dict]:
        """Get all aspects in the chart as a list of dictionaries."""
        from starlight.objects import ASPECTS
        
        aspects = []
        pairs = []
        
        for p in self.planets:
            for other_obj in [*self.planets, *self.angles]:
                if (
                    (other_obj.name != p.name)
                    and (
                        other_obj.swe in list(range(12))
                        or other_obj.name in ["ASC", "MC", "DSC", "IC"]
                    )
                    and ((p, other_obj) not in pairs)
                ):
                    for aspect_name, aspect_data in ASPECTS.items():
                        aspect_result = p.aspect(other_obj, aspect_data["degree"], aspect_data["orb"])
                        if aspect_result[0]:
                            aspects.append({
                                "planet1": p,
                                "planet2": other_obj,
                                "aspect_name": aspect_name,
                                "orb": aspect_result[1],
                                "distance": aspect_result[2],
                                "movement": aspect_result[3],
                            })
                            pairs.append((other_obj, p))
        
        return aspects
    
    def get_midpoint_aspects(self) -> list[dict]:
        """Get all midpoint aspects in the chart."""
        from starlight.objects import ASPECTS
        
        midpoint_aspects = []
        
        for mp in self.midpoints:
            for p in self.planets:
                # use closer midpoint
                mp_2 = copy.deepcopy(mp)
                mp_2.long = (mp.long + 180) % 360
                if abs(p.long - mp.long) < abs(p.long - mp_2.long):
                    mp_close = mp
                else:
                    mp_close = mp_2
                
                for aspect_name, aspect_data in ASPECTS.items():
                    aspect_result = mp_close.aspect(p, aspect_data["degree"], aspect_data["orb"])
                    if aspect_result[0]:
                        midpoint_aspects.append({
                            "midpoint": mp,
                            "planet": p,
                            "aspect_name": aspect_name,
                            "orb": aspect_result[1],
                            "distance": aspect_result[2],
                            "movement": aspect_result[3],
                        })
        
        return midpoint_aspects


# def format_long(long: float) -> str:
#     # Format longitude for printing in degrees - minutes - seconds: D°M'S".
#     degree = long % 30
#     min = (long % 1) * 60
#     sec = (min % 1) * 60

#     return f"{round(degree)}°{round(min)}'" + f'{round(sec)}"'


