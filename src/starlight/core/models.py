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
    house: int | None = None
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
    houses: HouseCusps
    aspects: tuple[Aspect, ...] = ()

    # Metadata
    calculation_timestamp: dt.datetime = field(
        default_factory=lambda: dt.datetime.now(dt.UTC)
    )

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

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to dictionary for JSON export.

        This enables web API integration, storage, etc.
        """
        return {
            "datetime": {
                "utc": self.datetime.utc_datetime.isoformat(),
                "julian_date": self.datetime.julian_day,
            },
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "name": self.location.name,
            },
            "houses": {"system": self.houses.system, "cusps": list(self.houses.cusps)},
            "positions": [
                {
                    "name": p.name,
                    "type": p.object_type.value,
                    "longitude": p.longitude,
                    "latitude": p.latitude,
                    "sign": p.sign,
                    "sign_degree": p.sign_degree,
                    "house": p.house,
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
