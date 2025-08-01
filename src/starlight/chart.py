"""Define a chart (birth chart) object that contains objects and analysis."""

import copy
import os
from datetime import datetime
from typing import Union, Optional

import pytz
import swisseph as swe
import timezonefinder
from geopy.geocoders import Nominatim

from starlight.objects import (
    Angle,
    Midpoint,
    Object,
    Planet,
    ArabicPart,
    _cached_date_conversion,
    _cached_houses,
    ARABIC_PARTS_CATALOG,
    HOUSE_SYSTEMS,
)
from starlight.cache import cached
from starlight.signs import DIGNITIES


def _set_ephemeris_path():
    """Set the path to Swiss Ephemeris data files."""
    # Get project root directory (two levels up from src/starlight/)
    PATH_LIB = os.path.dirname(__file__)  # src/starlight/
    PATH_PROJECT = os.path.dirname(os.path.dirname(PATH_LIB))  # project root
    PATH_DATA = os.path.join(PATH_PROJECT, "data", "swisseph", "ephe") + os.sep
    swe.set_ephe_path(PATH_DATA)


class Chart:
    def __init__(
        self,
        datetime_utc: datetime,
        houses: str,
        loc: Union[tuple[float, float], None] = None,
        loc_name: str = "",
        time_known: bool = True,
    ) -> None:
        # Set ephemeris path
        _set_ephemeris_path()

        # Validate inputs
        if loc is None and loc_name == "":
            raise ValueError("Need either coordinates or place name.")

        # Store datetime (must be UTC)
        if datetime_utc.tzinfo is None:
            raise ValueError("datetime must be timezone-aware (preferably UTC)")

        self.datetime_utc = (
            datetime_utc.astimezone(pytz.UTC)
            if datetime_utc.tzinfo != pytz.UTC
            else datetime_utc
        )
        self.house_system = houses
        self.loc_name = loc_name
        self.is_time_known = time_known

        # Handle location - prioritize coordinates if provided
        if loc is not None:
            self.loc = loc
            if loc_name:
                print(f"{loc_name} ({self.loc[0]}, {self.loc[1]})")
        elif loc_name:
            self.get_lat_long()
        else:
            raise ValueError("Need either coordinates or place name.")

        # Calculate Julian day
        self.julian = self._calc_julian_day()

        # Initialize collections
        self.objects: list[Object] = []
        self.objects_dict: dict[str, Object] = {}
        self.planets: list[Planet] = []
        self.angles: list[Angle] = []

        # Build chart
        self._make_planets()
        self._make_houses_and_angles()
        self._make_lunar_parts()
        self._make_asteroids()
        self._make_arabic_parts()
        self._make_midpoints()

    def _register_object(self, obj: Object, typed_collection: list | None = None) -> None:
        """Add object to all appropriate collections."""
        self.objects.append(obj)
        self.objects_dict[obj.name] = obj
        if typed_collection is not None:
            typed_collection.append(obj)

    @property
    def lat(self) -> float:
        if self.loc is None:
            raise ValueError("Location not set")
        return self.loc[0]

    @property
    def long(self) -> float:
        if self.loc is None:
            raise ValueError("Location not set")
        return self.loc[1]

    @property
    def year(self) -> int:
        return self.datetime_utc.year

    @property
    def month(self) -> int:
        return self.datetime_utc.month

    @property
    def day(self) -> int:
        return self.datetime_utc.day

    @property
    def hour(self) -> int:
        return self.datetime_utc.hour

    @property
    def minute(self) -> int:
        return self.datetime_utc.minute

    def _calc_julian_day(self) -> float:
        """Calculate Julian day from datetime."""
        dt = self.datetime_utc
        hour_decimal = dt.minute / 60.0 + dt.second / 3600.0
        return _cached_date_conversion(
            dt.year, dt.month, dt.day, dt.hour + hour_decimal
        )[1]

    def _make_planets(self) -> None:
        # Main 10 Planets
        for id in range(10):
            try:
                planet = Planet(swe.get_planet_name(id), id, self.julian)
                self._register_object(planet, self.planets)
            except swe.Error as e:
                print(e)

    def _make_houses_and_angles(self) -> None:
        # Get house system code from catalog
        system = HOUSE_SYSTEMS.get(self.house_system)
        if system is None:
            raise ValueError(
                f"Unsupported house system: {self.house_system}. "
                f"Supported systems: {list(HOUSE_SYSTEMS.keys())}"
            )

        cusps, angles = _cached_houses(self.julian, self.lat, self.long, hsys=system)
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
            self._register_object(angle, self.angles)

    def _make_lunar_parts(self) -> None:
        for swe_id in [11, 13]:  # [10, 11, 12, 13]:
            lunar_obj = Planet(swe.get_planet_name(swe_id), swe_id, self.julian)
            self._register_object(lunar_obj, self.planets)
            if swe_id == 11:  # add south node
                south_node = copy.deepcopy(lunar_obj)
                south_node.name = "South Node"
                south_node.swe = -1  # Special ID for calculated South Node
                south_node.long = (lunar_obj.long + 180) % 360
                south_node._make_sign_pos()
                self._register_object(south_node, self.planets)

    def _make_asteroids(self) -> None:
        for swe_id in [15, 16, 17, 18, 19, 20]:
            asteroid = Planet(swe.get_planet_name(swe_id), swe_id, self.julian)
            self._register_object(asteroid, self.planets)

    def _make_arabic_parts(self) -> None:
        """Calculate common Arabic Parts."""
        self.arabic_parts = []
        sect = self.get_sect()

        for part_name, part_data in ARABIC_PARTS_CATALOG.items():
            points = [self.objects_dict[p] for p in part_data["points"]]
            part = ArabicPart(
                part_name, points[0], points[1], points[2], sect, part_data["sect_flip"]
            )
            self._register_object(part, self.arabic_parts)

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
        """Print the chart date in a human-readable format."""
        utc_str = self.datetime_utc.strftime("%B %d, %Y at %H:%M Universal Time")
        print(f"Date: {utc_str}")

    def get_lat_long(self) -> None:
        # Get lat/long from cached geocoding
        location_data = _cached_geocode(self.loc_name)

        if location_data:
            self.loc = (location_data["latitude"], location_data["longitude"])
            print(f"{location_data['address']} ({self.loc[0]}, {self.loc[1]})")
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

    def get_local_datetime(self) -> Optional[datetime]:
        """Get the local datetime for this chart's location."""
        if not hasattr(self, "loc") or self.loc is None:
            return None

        tf = timezonefinder.TimezoneFinder()
        timezone_name = tf.certain_timezone_at(lat=self.lat, lng=self.long)

        if timezone_name is None:
            print("Could not determine the time zone")
            return None

        local_tz = pytz.timezone(timezone_name)
        return self.datetime_utc.astimezone(local_tz)

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

    def get_planetary_dignities(self, traditional: bool = True) -> dict:
        """Calculate planetary dignity scores.

        Args:
            traditional: If True, use traditional rulerships. If False, use modern.

        Returns:
            Dictionary with planet names as keys and dignity info as values.
        """
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

        planet_dignities = {}
        core_planets = [self.objects_dict[name] for name in core_names]
        sect = self.get_sect()  # Day or Night chart

        for p in core_planets:
            sign_dict = DIGNITIES[p.sign]
            sign_pos = p.sign_deg  # Degree within the sign (0-29)
            dignity_system = "traditional" if traditional else "modern"
            essential_dict = sign_dict[dignity_system]

            dignities = []
            total_score = 0

            # Check rulership
            if essential_dict["ruler"] == p.name:
                dignities.append("ruler")
                total_score += scores["ruler"]

            # Check exaltation
            if essential_dict["exhalt"] == p.name:
                dignities.append("exhalt")
                total_score += scores["exhalt"]

            # Check detriment
            if essential_dict["detriment"] == p.name:
                dignities.append("detriment")
                total_score += scores["detriment"]

            # Check fall
            if essential_dict["fall"] == p.name:
                dignities.append("fall")
                total_score += scores["fall"]

            # Check triplicity (based on sect)
            triplicity_dict = sign_dict["triplicity"]
            if sect == "Day" and triplicity_dict["day"] == p.name:
                dignities.append("triplicity")
                total_score += scores["triplicity"]
            elif sect == "Night" and triplicity_dict["night"] == p.name:
                dignities.append("triplicity")
                total_score += scores["triplicity"]
            elif triplicity_dict["coop"] == p.name:
                dignities.append("triplicity")
                total_score += (
                    scores["triplicity"] - 1
                )  # Cooperating triplicity is slightly less

            # Check bounds (Egyptian system)
            bound_planet = self._get_bound_ruler(sign_dict["bound_egypt"], sign_pos)
            if bound_planet == p.name:
                dignities.append("bound")
                total_score += scores["bound"]

            # Check decan (using Triplicity system)
            decan_planet = self._get_decan_ruler(sign_dict["decan_trip"], sign_pos)
            if decan_planet == p.name:
                dignities.append("decan")
                total_score += scores["decan"]

            planet_dignities[p.name] = {
                "sign": p.sign,
                "degree": round(sign_pos, 2),
                "dignities": dignities,
                "total_score": total_score,
                "bound_ruler": bound_planet,
                "decan_ruler": decan_planet,
            }

        return planet_dignities

    def _get_bound_ruler(self, bounds_dict: dict, degree: float) -> str:
        """Get the ruler of Egyptian bounds for a given degree."""
        for start_degree in sorted(bounds_dict.keys(), reverse=True):
            if degree >= start_degree:
                return bounds_dict[start_degree]
        return list(bounds_dict.values())[0]  # Fallback to first ruler

    def _get_decan_ruler(self, decan_list: list, degree: float) -> str:
        """Get the decan ruler for a given degree (0-9.99, 10-19.99, 20-29.99)."""
        decan_index = int(degree // 10)
        return decan_list[min(decan_index, len(decan_list) - 1)]

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
                        aspect_result = p.aspect(
                            other_obj, aspect_data["degree"], aspect_data["orb"]
                        )
                        if aspect_result[0]:
                            aspects.append(
                                {
                                    "planet1": p,
                                    "planet2": other_obj,
                                    "aspect_name": aspect_name,
                                    "orb": aspect_result[1],
                                    "distance": aspect_result[2],
                                    "movement": aspect_result[3],
                                }
                            )
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
                    aspect_result = mp_close.aspect(
                        p, aspect_data["degree"], aspect_data["orb"]
                    )
                    if aspect_result[0]:
                        midpoint_aspects.append(
                            {
                                "midpoint": mp,
                                "planet": p,
                                "aspect_name": aspect_name,
                                "orb": aspect_result[1],
                                "distance": aspect_result[2],
                                "movement": aspect_result[3],
                            }
                        )

        return midpoint_aspects


# Cached geocoding function
@cached(cache_type="geocoding", max_age_seconds=604800)  # Cache for 1 week
def _cached_geocode(location_name: str) -> dict:
    """Cached wrapper for geocoding API calls."""
    try:
        geolocator = Nominatim(user_agent="starlight_geocoder")
        location = geolocator.geocode(location_name)

        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": str(location),
            }
        else:
            return {}
    except Exception as e:
        print(f"Geocoding error: {e}")
        return {}


# def format_long(long: float) -> str:
#     # Format longitude for printing in degrees - minutes - seconds: D°M'S".
#     degree = long % 30
#     min = (long % 1) * 60
#     sec = (min % 1) * 60

#     return f"{round(degree)}°{round(min)}'" + f'{round(sec)}"'
