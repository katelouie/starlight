"""
Immutable data models for astrological calculations.

These are pure data containers - no business logic, no calculations.

They represent the OUTPUT of calculations, not the process.
"""

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ObjectType(Enum):
    """Type of astrological object."""

    PLANET = "planet"
    ANGLE = "angle"
    ASTEROID = "asteroid"
    POINT = "point"
    NODE = "node"
    ARABIC_PART = "arabic_part"
    MIDPOINT = "midpoint"
    FIXED_STAR = "fixed_star"


@dataclass(frozen=True)
class ChartLocation:
    """Immutable location data for chart calculation."""

    latitude: float
    longitude: float
    name: str = ""
    timezone: str = ""

    def __post_init__(self) -> None:
        """Validate coordinates"""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalud latitude: {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}")


@dataclass(frozen=True)
class ChartDateTime:
    """Immutable datetime data for chart calculation."""

    utc_datetime: dt.datetime
    julian_day: float
    local_datetime: dt.datetime | None = None

    def __post_init__(self) -> None:
        """Ensure datetime is timezone-aware."""
        if self.utc_datetime.tzinfo is None:
            raise ValueError("DateTime must be timezone-aware")


@dataclass(frozen=True)
class CelestialPosition:
    """Immutable representation of a celestial object's position.

    This is the OUTPUT of ephemeris calculations.
    """

    # Identity
    name: str
    object_type: ObjectType

    # Positional data
    longitude: float  # 0-360 degrees
    latitude: float = 0.0
    distance: float = 0.0

    # Velocity data
    speed_longitude: float = 0.0
    speed_latitude: float = 0.0
    speed_distance: float = 0.0

    # Derived data (calculated from longitude)
    sign: str = field(init=False)
    sign_degree: float = field(init=False)

    # Optional metadata
    is_retrograde: bool = field(init=False)

    def __post_init__(self) -> None:
        """Calculate derived fields."""
        # Use object.__setattr__ because the dataclass is frozen!
        signs = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]
        object.__setattr__(self, "sign", signs[int(self.longitude // 30)])
        object.__setattr__(self, "sign_degree", self.longitude % 30)
        object.__setattr__(self, "is_retrograde", self.speed_longitude < 0)

    @property
    def sign_position(self) -> str:
        """Human-readable sign position (e.g. 15°23' Aries)"""
        degrees = int(self.sign_degree)
        minutes = int((self.sign_degree % 1) * 60)
        return f"{degrees}°{minutes:02d}' {self.sign}"


@dataclass(frozen=True)
class MidpointPosition(CelestialPosition):
    """
    Specialized position type for midpoints between two celestial objects.

    A midpoint represents the halfway point between two celestial objects,
    either along the shorter arc (direct) or the longer arc (indirect).

    Attributes:
        object1: First component object
        object2: Second component object
        is_indirect: True if this is the indirect (opposite) midpoint

    Example:
        # Sun at 10° Aries, Moon at 20° Aries
        # Direct midpoint: 15° Aries
        # Indirect midpoint: 15° Libra (opposite)

        midpoint = MidpointPosition(
            name="Midpoint:Sun/Moon",
            object_type=ObjectType.MIDPOINT,
            longitude=15.0,  # 15° Aries
            object1=sun_position,
            object2=moon_position,
            is_indirect=False,
        )
    """

    # Use field with default_factory=None pattern to handle required fields after optional ones
    object1: CelestialPosition = field(default=None)  # type: ignore
    object2: CelestialPosition = field(default=None)  # type: ignore
    is_indirect: bool = False

    def __post_init__(self) -> None:
        """Validate that object1 and object2 are provided."""
        # Call parent __post_init__ first
        super().__post_init__()

        # Validate required fields
        if self.object1 is None:
            raise ValueError("object1 is required for MidpointPosition")
        if self.object2 is None:
            raise ValueError("object2 is required for MidpointPosition")


@dataclass(frozen=True)
class HouseCusps:
    """Immutable house cusp data."""

    system: str
    cusps: tuple[float, ...]  # 12 cusps, 0-360 degrees

    def __post_init__(self) -> None:
        """Validate cusp count."""
        if len(self.cusps) != 12:
            raise ValueError(f"Expected 12 cusps, got {len(self.cusps)}")

    def get_cusp(self, house_number: int) -> float:
        """Get cusp for a specific house (1-12)"""
        if not 1 <= house_number <= 12:
            raise ValueError(f"House number must be 1-12, got {house_number}")
        return self.cusps[house_number - 1]


@dataclass(frozen=True)
class Aspect:
    """Immutable aspect between two objects."""

    object1: CelestialPosition
    object2: CelestialPosition
    aspect_name: str
    aspect_degree: int  # 0, 60, 90, 120, 180, etc.
    orb: float  # Actual orb in degrees
    is_applying: bool | None = None

    @property
    def description(self) -> str:
        """Human-readable aspect description."""
        if self.is_applying is None:
            applying = ""
        elif self.is_applying:
            applying = " (applying)"
        else:  # is separating
            applying = " (separating)"

        return f"{self.object1.name} {self.aspect_name} {self.object2.name} (orb: {self.orb:.2f}°){applying}"


@dataclass(frozen=True)
class CalculatedChart:
    """
    Complete calculated chart - the final output.

    This is what a ChartBuilder returns. It's immutable and contains everything
    you need to analyze or visualize the chart.
    """

    # Input parameters
    datetime: ChartDateTime
    location: ChartLocation

    # Calculated data
    positions: tuple[CelestialPosition, ...]
    house_systems: dict[str, HouseCusps] = field(default_factory=dict)
    # chart.placements["Placidus"]["Sun"] -> 10
    house_placements: dict[str, dict[str, int]] = field(default_factory=dict)
    aspects: tuple[Aspect, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    # Metadata
    calculation_timestamp: dt.datetime = field(
        default_factory=lambda: dt.datetime.now(dt.UTC)
    )

    def _get_default_house_system(self) -> str:
        """
        Get the default house system to use.

        Returns the first (and typically only) house system in the chart.
        Raises ValueError if no house systems are available.
        """
        if not self.house_systems:
            raise ValueError(
                "No house systems calculated. Add a house system engine when building the chart."
            )

        # Get the first system (dict maintains insertion order in Python 3.7+)
        return next(iter(self.house_systems.keys()))

    @property
    def default_house_system(self) -> str:
        return self._get_default_house_system()

    def get_house(self, object_name: str, system_name: str | None = None) -> int | None:
        """
        Helper method to get the house number for a specific object in a specific system.
        """
        if system_name is None:
            system_name = self.default_house_system
        return self.house_placements.get(system_name, {}).get(object_name)

    def get_houses(self, system_name: str | None = None) -> HouseCusps:
        """Get all cusps for a specific system (or default system)."""
        if system_name is None:
            system_name = self.default_house_system

        return self.house_systems[system_name]

    def get_object(self, name: str) -> CelestialPosition | None:
        """Get a celestial object by name."""
        for obj in self.positions:
            if obj.name == name:
                return obj

        return None

    def get_planets(self) -> list[CelestialPosition]:
        """Get all planetary objects."""
        return [p for p in self.positions if p.object_type == ObjectType.PLANET]

    def get_angles(self) -> list[CelestialPosition]:
        """Get all chart angles."""
        return [p for p in self.positions if p.object_type == ObjectType.ANGLE]

    def get_points(self) -> list[CelestialPosition]:
        """Get all calculated points (Vertex, Lilith, etc.)."""
        return [p for p in self.positions if p.object_type == ObjectType.POINT]

    def get_nodes(self) -> list[CelestialPosition]:
        """Get all nodes (True Node, South Node, etc.)."""
        return [p for p in self.positions if p.object_type == ObjectType.NODE]

    def get_dignities(self, system: str = "traditional") -> dict[str, Any]:
        """
        Get essential dignity calculations.

        Args:
            system: "traditional" or "modern"

        Returns:
            Dictionary of planet dignities, or empty dict if not calculated
        """
        dignity_data = self.metadata.get("dignities", {})
        planet_dignities = dignity_data.get("planet_dignities", {})

        result = {}
        for planet_name, data in planet_dignities.items():
            if system in data:
                result[planet_name] = data[system]

        return result

    def get_planet_dignity(
        self, planet_name: str, system: str = "traditional"
    ) -> dict[str, Any] | None:
        """
        Get dignity calculation for a specific planet.

        Args:
            planet_name: Name of the planet (e.g., "Sun", "Moon")
            system: "traditional" or "modern"

        Returns:
            Dignity data for the planet, or None if not found
        """
        dignities = self.get_dignities(system)
        return dignities.get(planet_name)

    def get_mutual_receptions(
        self, system: str = "traditional"
    ) -> list[dict[str, Any]]:
        """
        Get all mutual receptions in the chart.

        Args:
            system: "traditional" or "modern"

        Returns:
            List of mutual reception dictionaries
        """
        dignity_data = self.metadata.get("dignities", {})
        receptions = dignity_data.get("mutual_receptions", {})
        return receptions.get(system, [])

    def get_all_accidental_dignities(self) -> dict[str, Any]:
        """Get all accidental dignities (entire object)."""
        return self.metadata.get("accidental_dignities", {})

    def get_accidental_dignities(self, system: str | None = None) -> dict[str, Any]:
        """
        Get accidental dignity calculations.

        Args:
            system: Specific house system ("Placidus"). If None returns all systems.

        Returns:
            Dictionary of planetary accidental dignities
        """
        all_accidentals = self.metadata.get("accidental_dignities", {})

        if system is None:
            # Use the first house system in the chart
            system = self.default_house_system

        # Return for specific system
        result = {}
        for planet_name, data in all_accidentals.items():
            by_system = data.get("by_system", {})
            universal = data.get("universal", {})

            if system in by_system:
                # Combine system-specific and universal
                system_data = by_system[system].copy()

                # Add universal conditions to this system's conditions
                combined_conditions = system_data.get("conditions", []).copy()
                combined_conditions.extend(universal.get("conditions", []))

                result[planet_name] = {
                    "planet": planet_name,
                    "score": system_data.get("score", 0) + universal.get("score", 0),
                    "house": system_data.get("house"),
                    "conditions": combined_conditions,
                    "system": system,
                }

        return result

    def get_planet_accidental(
        self, planet_name: str, system: str | None = None
    ) -> dict[str, Any] | None:
        """
        Get accidental dignity for a specific planet.

        Args:
            planet_name: Name of the planet
            system: House system (defaults to default house system if None)

        Returns:
            Accidental dignity data, or None if not found
        """
        accidentals = self.get_accidental_dignities(system)
        return accidentals.get(planet_name)

    def get_strongest_planet(
        self, system: str = "traditional"
    ) -> tuple[str, int] | None:
        """
        Find the planet with the highest dignity score (Almuten).

        Args:
            system: "traditional" or "modern"

        Returns:
            Tuple of (planet_name, score) or None if no dignities calculated
        """
        dignities = self.get_dignities(system)

        if not dignities:
            return None

        strongest = max(dignities.items(), key=lambda x: x[1].get("score", 0))

        return strongest[0], strongest[1].get("score", 0)

    def get_planet_total_score(
        self,
        planet_name: str,
        essential_system: str = "traditional",
        accidental_system: str | None = None,
    ) -> dict[str, Any]:
        """
        Get combined essential + accidental dignity score.

        Args:
            planet_name: Name of the planet
            essential_system: "traditional" or "modern"
            accidental_system: House system name (defaults to default system)

        Returns:
            Dict with essential, accidental, and total scores
        """
        essential = self.get_planet_dignity(planet_name, essential_system)
        accidental = self.get_planet_accidental(planet_name, accidental_system)

        essential_score = essential.get("score", 0) if essential else 0
        accidental_score = accidental.get("score", 0) if accidental else 0

        return {
            "planet": planet_name,
            "essential_score": essential_score,
            "essential_system": essential_system,
            "accidental_score": accidental_score,
            "accidental_system": accidental_system or self.default_house_system,
            "total_score": essential_score + accidental_score,
            "interpretation": self._interpret_total_score(
                essential_score + accidental_score
            ),
        }

    def _interpret_total_score(self, total_score: int) -> str:
        """Interpret combined dignity score."""
        if total_score >= 15:
            return "Exceptionally strong - excellent condition"
        elif total_score >= 10:
            return "Very strong - favorable condition"
        elif total_score >= 5:
            return "Strong - good condition"
        elif total_score >= 0:
            return "Moderate - neutral to favorable"
        elif total_score >= -5:
            return "Challenged - some difficulties"
        elif total_score >= -10:
            return "Significantly challenged - considerable difficulties"
        else:
            return "Severely challenged - very difficult condition"

    def sect(self) -> bool | None:
        """
        Check which sect this chart is (day or night) (Sun above the horizon).

        Returns:
            "day" or "night"
        """
        dignity_data = self.metadata.get("dignities", {})
        return dignity_data.get("sect")

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to dictionary for JSON export.

        This enables web API integration, storage, etc.
        """
        base_dict = {
            "datetime": {
                "utc": self.datetime.utc_datetime.isoformat(),
                "julian_date": self.datetime.julian_day,
            },
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "name": self.location.name,
            },
            "house_systems": {
                system_name: list(house_cusps.cusps)
                for system_name, house_cusps in self.house_systems.items()
            },
            "default_house_system": self.default_house_system,
            "house_placements": self.house_placements,
            "positions": [
                {
                    "name": p.name,
                    "type": p.object_type.value,
                    "longitude": p.longitude,
                    "latitude": p.latitude,
                    "sign": p.sign,
                    "sign_degree": p.sign_degree,
                    "is_retrograde": p.is_retrograde,
                }
                for p in self.positions
            ],
            "aspects": [
                {
                    "object1": a.object1.name,
                    "object2": a.object2.name,
                    "aspect": a.aspect_name,
                    "orb": a.orb,
                }
                for a in self.aspects
            ],
        }

        # add metadata (including dignities)
        if self.metadata:
            base_dict["metadata"] = self.metadata

        return base_dict
