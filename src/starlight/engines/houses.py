"""House system calculation engines."""

from dataclasses import replace

import swisseph as swe

from starlight.cache import cached
from starlight.core.models import (
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
    ObjectType,
)

# Swiss Ephemeris house system codes
HOUSE_SYSTEM_CODES = {
    "Placidus": b"P",
    "Koch": b"K",
    "Porphyry": b"O",
    "Regiomontanus": b"R",
    "Campanus": b"C",
    "Equal": b"A",
    "Equal (MC)": b"D",
    "Vehlow Equal": b"V",
    "Whole Sign": b"W",
    "Alcabitius": b"B",
    "Topocentric": b"T",
    "Morinus": b"M",
}


class SwissHouseSystemBase:
    """
    Provides a default implementation for calling swisseph and assigning houses.

    This is NOT a protocol, just a helper class for code reuse.
    """

    @property
    def system_name(self) -> str:
        return "BaseClass"

    @cached(cache_type="ephemeris", max_age_seconds=86400)
    def _calculate_swiss_houses(
        self, julian_day: float, latitude: float, longitude: float, system_code: bytes
    ) -> tuple:
        """Cached Swiss Ephemeris house calculation."""
        return swe.houses(julian_day, latitude, longitude, hsys=system_code)

    def assign_houses(
        self, positions: list[CelestialPosition], cusps: HouseCusps
    ) -> dict[str, int]:
        """Assign house numbers to positions. Returns a simple name: house dict."""
        placements = {}
        for pos in positions:
            house_num = self._find_house(pos.longitude, cusps.cusps)
            placements[pos.name] = house_num
        return placements

    def _find_house(self, longitude: float, cusps: tuple) -> int:
        """Find which house a longitude falls into."""
        cusp_list = list(cusps)

        for i in range(12):
            cusp1 = cusp_list[i]
            cusp2 = cusp_list[(i + 1) % 12]

            # Handles wrapping about 360 degrees
            if cusp2 < cusp1:
                cusp2 += 360
                test_long = longitude if longitude >= cusp1 else longitude + 360
            else:
                test_long = longitude

            if cusp1 <= test_long < cusp2:
                return i + 1

        return 1  # fallback

    def calculate_house_data(
        self, datetime: ChartDateTime, location: ChartLocation
    ) -> tuple[HouseCusps, list[CelestialPosition]]:
        """Calculate house system's house cusps and chart angles."""
        # Cusps
        cusps_list, angles_list = self._calculate_swiss_houses(
            datetime.julian_day,
            location.latitude,
            location.longitude,
            HOUSE_SYSTEM_CODES[self.system_name],
        )
        cusps = HouseCusps(system=self.system_name, cusps=tuple(cusps_list))

        # Chart angles
        asc = angles_list[0]
        mc = angles_list[1]
        vertex = angles_list[3]

        angles = [
            CelestialPosition(name="ASC", object_type=ObjectType.ANGLE, longitude=asc),
            CelestialPosition(name="MC", object_type=ObjectType.ANGLE, longitude=mc),
            # Derive Dsc and IC
            CelestialPosition(
                name="DSC", object_type=ObjectType.ANGLE, longitude=(asc + 180) % 360
            ),
            CelestialPosition(
                name="IC", object_type=ObjectType.ANGLE, longitude=(mc + 180) % 360
            ),
            # Include Vertex
            CelestialPosition(
                name="Vertex", object_type=ObjectType.ANGLE, longitude=vertex
            ),
        ]

        return cusps, angles


class PlacidusHouses(SwissHouseSystemBase):
    """Placidus house system engine."""

    @property
    def system_name(self) -> str:
        return "Placidus"


class WholeSignHouses(SwissHouseSystemBase):
    """Whole sign house system engine."""

    @property
    def system_name(self) -> str:
        return "Whole Sign"


class KochHouses(SwissHouseSystemBase):
    """Koch house system engine."""

    @property
    def system_name(self) -> str:
        return "Koch"


class EqualHouses(SwissHouseSystemBase):
    """Equal house system engine."""

    @property
    def system_name(self) -> str:
        return "Koch"
