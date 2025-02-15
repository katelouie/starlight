"""Define objects in a chart (incl planets, angles, midpoints, meteors, stars, etc.)"""

import swisseph as swe

from starlight import signs


<<<<<<< HEAD
=======
def format_long(long: float) -> str:
    # Format longitude for printing in degrees - minutes - seconds: D°M'S".
    degree = long % 30
    min = (long % 1) * 60
    sec = (min % 1) * 60

    return f"{round(degree)}°{round(min)}'" + f'{round(sec)}"'


def format_long_sign(long: float) -> str:
    # Get sign from longitude
    return signs.sign_names[int(long // 30)]


>>>>>>> master
class Object:
    """Generic chart object. Planets, Angles, etc. inherit from this."""

    def __init__(self, name: str, swe: int) -> None:
        self.name = name
        self.swe = swe

        # output from swisseph.calc_ut()
        self.long: float
        self.lat: float
        self.dist: float
        self.speed_long: float
        self.speed_decl: float
        self.speed_dist: float

    @property
    def has_speed(self) -> bool:
        return self.speed_long is not None

    @property
    def is_retro(self) -> bool:
        return self.speed_long < 0

    def _get_eph(self, julian_day: float) -> None:
        eph = swe.calc_ut(julian_day, self.swe)[0]

        self.long, self.lat = eph[0], eph[1]
        self.dist = eph[2]
        self.speed_long, self.speed_decl, self.speed_dist = eph[3], eph[4], eph[5]

    def _make_sign_pos(self) -> None:
        # get sign
        self.sign: str = signs.sign_names[int(self.long // 30)]
        # get angle of sign
        self.sign_deg: float = self.long % 30
        self.sign_min: float = (self.long % 1) * 60
        self.sign_sec: float = (self.sign_min % 1) * 60
        self.sign_deg_str: str = (
            f"{round(self.sign_deg)}°{round(self.sign_min)}'"
            + f'{round(self.sign_sec)}"'
        )

    def _make_house_pos(self, cusps: list[float]) -> None:
        def __get_house(self, cusps):
            house = None

            for ix, x in enumerate(cusps):
                if house is None:
                    house = ix

                if self.long == x:
                    return ix + 1
                elif self.long > x:
                    house = ix
                else:
                    return house

            return 12

        self.house = __get_house(self, cusps)

        cusp = cusps[self.house - 1]
        self.house_deg = self.long - cusp
        self.house_min = (self.house_deg % 1) * 60
        self.house_sec = (self.house_min % 1) * 60

    def aspect(
        self, other: "Object", degrees: int, orb: int
    ) -> tuple[bool, float | None, float, str | None]:
        distance: float = abs(self.long - other.long)
        if distance > 180:
            distance = 360 - abs(self.long - other.long)

        is_aspect: bool = abs(distance - degrees) <= orb
        aspect_orb: float | None = abs(distance - degrees) if is_aspect else None

        if self.has_speed and other.has_speed:
            if (self.long > other.long) and (self.speed_long < other.speed_long):
                movement: str | None = "Applying"
            elif (self.long < other.long) and (self.speed_long > other.speed_long):
                movement = "Applying"
            else:
                movement = "Separating"
        else:
            movement = None

        return is_aspect, aspect_orb, distance, movement

    def midpoint(self, other: "Object") -> float:
        return (self.long + other.long) / 2


class Planet(Object):
    """Planetary Body.

    Sun, Moon | Mercury, Venus, Mars | Jupiter, Saturn | Uranus, Neptune, Pluto.
    """

    def __init__(self, name: str, swe: int, julian: float) -> None:
        super().__init__(name, swe)
        self.julian = julian

        self._get_eph(self.julian)
        self._make_sign_pos()

        if swe == 1:
            self._get_phase()

    def _get_phase(self) -> None:
        phase_data = swe.pheno_ut(self.julian, self.swe)
        self.phase_angle = phase_data[0]
        self.phase_frac = phase_data[1]  # illuminated fraction of disc
        self.phase_para = phase_data[5]  # geocentric horizontal parallax (Moon)

    @property
    def kind(self) -> str:
        if self.name in ["Sun", "Moon"]:
            return "Lights"
        elif self.name in ["Mercury", "Venus", "Mars"]:
            return "Personal"
        elif self.name in ["Jupiter", "Saturn"]:
            return "Impersonal"

        return "Generational"


class Meteor(Object):
    def __init__(self, name: str, swe: int, julian: float) -> None:
        super().__init__(name, swe)
        self.julian = julian

        self._get_eph(self.julian)
        self._make_sign_pos()


class Angle(Object):
    # requires a house system
    def __init__(self, name: str, long: float, swe: int | None = None) -> None:
        self.name = name
        self.swe = swe
        self.long = long

    @property
    def has_speed(self) -> bool:
        return False

    @property
    def is_retro(self) -> bool:
        return False

<<<<<<< HEAD
=======
    def __str__(self) -> str:
        return f"name: {self.name} id={self.swe} long={self.long}"

>>>>>>> master

class FixedStar(Object): ...


class Midpoint(Object):
    def __init__(self, object_1: Object, object_2: Object) -> None:
        self.name = f"{object_1.name}-{object_2.name}"

        self.obj1 = object_1
        self.obj2 = object_2

        self.long1 = object_1.long
        self.long2 = object_2.long

<<<<<<< HEAD
=======
        self.long = (self.long1 + self.long2) / 2

    def __repr__(self) -> str:
        return f"{self.obj1.name}-{self.obj2.name} Midpoint: {self.long}"

>>>>>>> master
    @property
    def has_speed(self) -> bool:
        return False

    @property
    def is_retro(self) -> bool:
        return False

<<<<<<< HEAD
    @property
    def long(self) -> float:
        return (self.long1 + self.long2) / 2


aspects = {
    "Conjunct": {"degree": 0, "orb": 10},
    "Sextile": {"degree": 60, "orb": 10},
    "Square": {"degree": 90, "orb": 10},
    "Trine": {"degree": 120, "orb": 10},
    "Opposition": {"degree": 180, "orb": 10},
}
=======

ASPECTS = {
    "Conjunct": {"degree": 0, "orb": 8},
    "Sextile": {"degree": 60, "orb": 8},
    "Square": {"degree": 90, "orb": 8},
    "Trine": {"degree": 120, "orb": 8},
    "Opposition": {"degree": 180, "orb": 8},
}

# Redefining the dictionary after execution state reset

# Define a dictionary mapping Swiss Ephemeris IDs to their standard and aliased names

SWISS_EPHEMERIS_OBJECTS = {
    0: {"name": "Sun", "alias": "Sun ☉"},
    1: {"name": "Moon", "alias": "Moon ☽"},
    2: {"name": "Mercury", "alias": "Mercury ☿"},
    3: {"name": "Venus", "alias": "Mars ♀"},
    4: {"name": "Mars", "alias": "Venus ♂"},
    5: {"name": "Jupiter", "alias": "Jupiter ♃"},
    6: {"name": "Saturn", "alias": "Saturn ♄"},
    7: {"name": "Uranus", "alias": "Uranus ♅"},
    8: {"name": "Neptune", "alias": "Neptune ♆"},
    9: {"name": "Pluto", "alias": "Pluto ♇"},
    10: {"name": "Mean North Node", "alias": "North Node ☊ (Mean)"},
    11: {"name": "True North Node", "alias": "North Node ☊"},
    12: {"name": "Mean Black Moon Lilith", "alias": "BM Lilith ⚸ (Mean)"},
    13: {"name": "True Black Moon Lilith", "alias": "BM Lilith ⚸"},
    15: {"name": "Chiron", "alias": "Chiron ⚷"},
    16: {"name": "Pholus", "alias": "Pholus 𝛷"},
    17: {"name": "Ceres", "alias": "Ceres ⚳"},
    18: {"name": "Pallas", "alias": "Pallas ⚴"},
    19: {"name": "Juno", "alias": "Juno ⚵"},
    20: {"name": "Vesta", "alias": "Vesta ⚶"},
    "ASC": {"name": "Ascendant", "alias": "Asc"},
    "MC": {"name": "Midheaven", "alias": "MC"},
    "DSC": {"name": "Descendant", "alias": "Desc"},
    "IC": {"name": "Imum Coeli", "alias": "IC"},
    "VERTEX": {"name": "Vertex", "alias": "Vertex"},
    "southnode": {"name": "South Node", "alias": "South Node ☋"},
}


def get_ephemeris_object(identifier):
    """
    Retrieve the name and alias of a celestial object from its Swiss Ephemeris ID or alias key.

    Parameters:
    - identifier (int or str): The Swiss Ephemeris ID or alias key (e.g., "mean_apogee" for Black Moon Lilith).

    Returns:
    - dict: A dictionary containing "name" and "alias" keys.
    """
    return SWISS_EPHEMERIS_OBJECTS.get(identifier, {"name": "Unknown", "alias": "?"})


# Example usage
example_objects = [0, 1, 10, "mean_apogee", "MC"]
example_results = {obj: get_ephemeris_object(obj) for obj in example_objects}
example_results
>>>>>>> master
