"""
Protocol definitions for Starlight components.

Protocols define INTERFACES - what methods a component must implement.
They don't provide implementation - that's in the engine classes.

Think of these as contracts: "If you want to be an EphemerisEngine,
you must implement these methods with these signatures."
"""

from typing import Any, Protocol

from starlight.core.models import (
    Aspect,
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
)


class EphemerisEngine(Protocol):
    """
    Protocol for planetary position calculation engines.

    Different implementations might use:
    - Swiss Ephemeris
    - JPL Ephemeris
    - Custom calculation algorithms
    - Mock data for testing
    """

    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: list[str] | None = None,
    ) -> list[CelestialPosition]:
        """
        Calculate positions for celestial objects.

        Args:
            datetime: When to calculate positions
            location: Where to calculate from (for topocentric)
            objects: Which objects to calculate (None = all standard objects)

        Returns:
            List of CelestialPosition objects
        """
        ...


class HouseSystemEngine(Protocol):
    """
    Protocol for house system calculation engines.

    Different implementations for different house systems:
    - Whole Sign
    - Placidus
    - Koch
    - Equal House
    - etc
    """

    @property
    def system_name(self) -> str:
        """Name of this house system (e.g. Placidus)"""
        ...

    def calculate_house_data(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> tuple[HouseCusps, list[CelestialPosition]]:
        """
        Calculate house cusps for this system.

        Args:
            datetime: Chart datetime
            location: Chart location

        Returns:
            Tuple containing:
            1. HouseCusps object with 12 cusp positions (For this specific system)
            2. A List of CelestialPosition objects for the primary angles
               (ASC, MC, DSC, IC, Vertex)
        """
        ...

    def assign_houses(
        self, positions: list[CelestialPosition], cusps: HouseCusps
    ) -> dict[str, int]:
        """
        Assign house numbers to celestial positions.

        Args:
            positions: Celestial objects to assign houses
            cusps: House cusps to use for assignment

        Returns:
            A dictionary of {object_name: house_number}
        """
        ...


class AspectEngine(Protocol):
    """
    Protocol for aspect calculation engines.

    Different implementations might use:
    - Traditional aspects (Ptolemaic)
    - Modern aspects (including minor aspects)
    - Harmonic aspects
    - Vedic aspects (completely different system)
    """

    def calculate_aspects(
        self,
        positions: list[CelestialPosition],
        orb_config: OrbEngine,
    ) -> list[Aspect]:
        """
        Calculate aspects between celestial objects.

        Args:
            positions: Objects to find aspects between
            orb_config: Optional custom orb settings

        Returns:
            List of Aspect objects
        """
        ...


class OrbEngine(Protocol):
    """
    Protocol for orb calculation.

    Encapsulates logic for determining orb allowance, which can be simple (by aspect)
    or complex (by planet, by planet pair, by day/night, etc.).
    """

    def get_orb_allowance(
        self, obj1: CelestialPosition, obj2: CelestialPosition, aspect_name: str
    ) -> float:
        """
        Get the allowed orb for a specific aspect between two objects.

        Args:
            obj1: The first celestial object
            obj2: The second celestial object
            aspect_name: The name of the aspect (e.g. Square)

        Returns:
            The maximum allowed orb in degrees
        """
        ...


class DignityCalculator(Protocol):
    """
    Protocol for dignity/debility calculation.

    Different implementations:
    - Traditional essential dignities
    - Modern rulerships
    - Vedic dignity system
    """

    def calculate_dignities(self, position: CelestialPosition) -> dict[str, Any]:
        """
        Calculate dignities for a celestial position.

        Args:
            position: Position to calculate dignities for

        Returns:
            Dictionary with dignity information
        """


class ChartComponent(Protocol):
    """
    Base protocol for chart calculation components.

    Components can be:
    - Arabic part calculators
    - Midpoint finders
    - Pattern detectors (grand trine, T-square, etc.)
    - Fixed star calculators
    - Harmonic charts
    """

    @property
    def component_name(self) -> str:
        """Name of this component."""
        ...

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        houses: HouseCusps,
    ) -> list[CelestialPosition]:
        """
        Calculate additional chart objects.

        Args:
            datetime: Chart datetime
            location: Chart location
            positions: Already calculated positions
            houses: House cusps

        Returns:
            List of additional CelestialPosition objects
        """
        ...
