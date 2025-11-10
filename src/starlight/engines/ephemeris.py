"""Ephemeris calculation engines."""

import os

import swisseph as swe

from starlight.cache import cached
from starlight.core.models import (
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    ObjectType,
)


def _set_ephemeris_path() -> None:
    """Set the path to Swiss Ephemeris data files."""
    path_lib = os.path.dirname(os.path.dirname(__file__))
    path_project = os.path.dirname(path_lib)
    path_data = os.path.join(path_project, "data", "swisseph", "ephe") + os.sep
    swe.set_ephe_path(path_data)


# Swiss Ephemeris object IDs
# Source: swe.h (Swiss Ephemeris C library constants)
SWISS_EPHEMERIS_IDS = {
    # --- Main Planets & Luminaries ---
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
    "Uranus": 7,
    "Neptune": 8,
    "Pluto": 9,
    # --- Earth ---
    # Note: Earth is rarely used, as charts are geocentric
    "Earth": 14,
    # --- Lunar Nodes & Apsides ---
    "Mean Node": 10,
    "True Node": 11,
    "Mean Apogee": 12,  # Mean Lilith (Black Moon)
    "True Apogee": 13,  # True/Osculating Lilith
    # --- Major Asteroids & Centaurs ---
    "Chiron": 15,
    "Pholus": 16,
    "Ceres": 17,
    "Pallas": 18,
    "Juno": 19,
    "Vesta": 20,
    # --- Fictitious / Uranian / Hamburg School ---
    "Cupido": 40,
    "Hades": 41,
    "Zeus": 42,
    "Kronos": 43,
    "Apollon": 44,
    "Admetos": 45,
    "Vulkanus": 46,
    "Poseidon": 47,
    # --- Other "Planets" ---
    "Isis": 48,
    "Nibiru": 49,
    "Harrington": 50,
    "Leverrier": 51,
    "Adams": 52,
    "Lowell": 53,
    "Pickering": 54,
    # --- Special Points (Calculated by swe.houses) ---
    # These are NOT calculated with swe.calc_ut
    # They are returned by the swe.houses() function.
    # The IDs are listed here for completeness.
    "Ascendant": -2,  # SE_ASC constant
    "Midheaven": -3,  # SE_MC constant
    "Vertex": -5,  # SE_VERTEX constant
    # --- How to use Asteroid Numbers ---
    #
    # Asteroids not in the main list are calculated by their
    # Minor Planet Center (MPC) number.
    #
    # You do NOT add the offset. The `pyswisseph` library handles it.
    #
    # E.g., to get Eris (MPC number 136199):
    # swe.calc_ut(julian_day, 136199, flags)
    #
    # Here are a few common examples you might want to map:
    "Eris": 136199,
    "Sedna": 90377,
    "Quaoar": 50000,
    "Makemake": 136472,
    "Haumea": 136108,
    "Orcus": 90482,
}


class SwissEphemerisEngine:
    """
    Swiss Ephemeris calculation engine.

    This is our default, high-precision ephemeris calculator. Uses the pyswisseph
    library for accurate planetary positions.
    """

    def __init__(self):
        """Initialize Swiss Ephemeris."""
        _set_ephemeris_path()
        self._object_ids = SWISS_EPHEMERIS_IDS.copy()

    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: list[str] | None = None,
    ) -> list[CelestialPosition]:
        """
        Calculate positions using Swiss Ephemeris.

        Args:
            datetime: When to calculate
            location: Where to calculate from
            objects: Which objects to calculate (None = all standard)

        Returns:
            List of CelestialPosition objects
        """
        # Default to all major objects
        if objects is None:
            objects = [
                "Sun",
                "Moon",
                "Mercury",
                "Venus",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
                "True Node",
                "Chiron",
            ]

        positions = []

        for obj_name in objects:
            if obj_name not in self._object_ids:
                continue

            obj_id = self._object_ids[obj_name]
            position = self._calculate_single_position(
                datetime.julian_day, obj_id, obj_name
            )
            positions.append(position)

            # Add South Node (opposite of True Node)
            if "True Node" in objects:
                north_node = next(p for p in positions if p.name == "True Node")
                south_node = CelestialPosition(
                    name="South Node",
                    object_type=ObjectType.PLANET,
                    longitude=(north_node.longitude + 180) % 360,
                    latitude=-north_node.latitude,
                    speed_longitude=-north_node.speed_longitude,
                    speed_latitude=-north_node.speed_latitude,
                )
                positions.append(south_node)

        return positions

    @cached(cache_type="ephemeris", max_age_seconds=86400)
    def _calculate_single_position(
        self, julian_day: float, object_id: int, object_name: str
    ) -> CelestialPosition:
        """
        Calculate position for a single object (cached).

        Args:
            julian_day: Julian day number
            object_id: Swiss Ephemeris object ID
            object_name: Name of the object

        Returns:
            CelestialPosition
        """
        try:
            result = swe.calc_ut(julian_day, object_id)

            return CelestialPosition(
                name=object_name,
                object_type=ObjectType.PLANET,
                longitude=result[0][0],
                latitude=result[0][1],
                distance=result[0][2],
                speed_longitude=result[0][3],
                speed_latitude=result[0][4],
                speed_distance=result[0][5],
            )
        except swe.Error as e:
            raise RuntimeError(f"Failed to calculate {object_name}: {e}") from swe.Error


class MockEphemerisEngine:
    """
    Mock ephemeris engine for testing.

    Returns fixed positions instead of calculating them.

    Useful for:
    - Unit tests
    - Development
    - Benchmarking other components
    """

    def __init__(self, mock_data: dict[str, float] | None = None) -> None:
        """
        Initialize mock engine.

        Args:
            mock_data: Optional dict of {object_name: longitude}
        """
        self._mock_data = mock_data or {
            "Sun": 0.0,  # 0° Aries
            "Moon": 90.0,  # 0° Cancer
            "Mercury": 30.0,  # 0° Taurus
            "Venus": 60.0,  # 0° Gemini
            "Mars": 120.0,  # 0° Leo
        }

    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: list[str] | None = None,
    ) -> list[CelestialPosition]:
        """Return mock positions."""
        if objects is None:
            objects = list(self._mock_data.keys())

        positions = []
        for obj_name in objects:
            if obj_name in self._mock_data:
                positions.append(
                    CelestialPosition(
                        name=obj_name,
                        object_type=ObjectType.PLANET,
                        longitude=self._mock_data[obj_name],
                        speed_longitude=1.0,  # Direct motion
                    )
                )

        return positions
