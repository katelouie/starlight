"""
ChartBuilder: The main API for creating charts.

This is the fluent interface that users interact with. It orchestrates all the engines
and components to build a complete chart.
"""

import datetime as dt

import pytz
import swisseph as swe

from starlight.cache import cached
from starlight.core.config import CalculationConfig
from starlight.core.models import (
    CalculatedChart,
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
)
from starlight.core.native import Native

# --- Engine Protocols (for Type Hinting) ---
from starlight.core.protocols import (
    AspectEngine,
    ChartComponent,
    EphemerisEngine,
    HouseSystemEngine,
    OrbEngine,
)

# --- Default Engine Implementations ---
from starlight.engines.ephemeris import SwissEphemerisEngine
from starlight.engines.houses import PlacidusHouses
from starlight.engines.orbs import SimpleOrbEngine  # PIVOT: New default orb engine


class ChartBuilder:
    """
    Fluent builder for creating astrological charts.

    Usage:
        chart = (
            ChartBuilder.from_native(dt, location)
            .with_ephemeris(SwissEphemeris())
            .with_house_systems([PlacidusHouses(), WholeSignHouses()])
            .with_aspects(ModernAspectEngine())
            .with_orbs(SimpleOrbEngine())
            .calculate()
        )
    """

    def __init__(self, datetime: ChartDateTime, location: ChartLocation) -> None:
        """
        Initialize builder with required data.

        Args:
            datetime: Chart datetime
            location: Chart location
        """
        self._datetime = datetime
        self._location = location

        # Default engines (can be overridden)
        self._ephemeris: EphemerisEngine = SwissEphemerisEngine()
        self._house_engines: list[HouseSystemEngine] = [PlacidusHouses()]
        self._aspect_engine: AspectEngine | None = None  # optional
        self._orb_engine: OrbEngine = SimpleOrbEngine()

        # Configuration
        self._config = CalculationConfig()

        # Additional components
        self._components = []

    @classmethod
    def from_native(cls, native: Native) -> "ChartBuilder":
        """Create a new ChartBuilder from a Native object.

        This is the primary factory method.
        """
        # The Native object has already done all the processing.
        # We just pass its clean attributes to our "pro chef" __init__.
        return cls(native.datetime, native.location)

    # ---- Fluent configuration methods ---
    def with_ephemeris(self, engine: EphemerisEngine) -> "ChartBuilder":
        """Set the ephemeris engine."""
        self._ephemeris = engine
        return self

    def with_house_systems(self, engines: list[HouseSystemEngine]) -> "ChartBuilder":
        """
        Replaces the entire list of house engines (eg - to calculate *only* Whole Sign)
        """
        if not engines:
            raise ValueError("House engine list cannot be empty")
        self._house_engines = engines
        return self

    def add_house_system(self, engine: HouseSystemEngine) -> "ChartBuilder":
        """
        Adds an additional house engine to the calculation list.
        (e.g., to calculate Placidus *and* Whole Sign)
        """
        self._house_engines.append(engine)
        return self

    def with_aspects(self, engine: AspectEngine | None) -> "ChartBuilder":
        """Set the aspect calculation engine. (Set to None to disable)"""
        self._aspect_engine = engine
        return self

    def with_orbs(self, engine: OrbEngine) -> "ChartBuilder":
        """Set the orb calculation engine."""
        self._orb_engine = engine
        return self

    def with_config(self, config: CalculationConfig) -> "ChartBuilder":
        """Set the calculation configuration (which objects to find)."""
        self._config = config
        return self

    def add_component(self, component: ChartComponent) -> "ChartBuilder":
        """Add an additional calculation component (e.g. ArabicParts)."""
        self._components.append(component)
        return self

    # --- Calculation ---

    def _get_objects_list(self) -> list[str]:
        """Get list of objects to calculate based on config."""
        objects = self._config.include_planets.copy()

        if self._config.include_nodes:
            objects.append("True Node")

        if self._config.include_chiron:
            objects.append("Chiron")

        objects.extend(self._config.include_asteroids)

        # Ensure all names are unique
        return list(set(objects))

    def calculate(self) -> CalculatedChart:
        """
        Execute all calculations and return the final chart.

        Returns:
            CalculatedChart with all calculated data
        """
        # Step 1: Calculate planetary positions
        objects_to_calculate = self._get_objects_list()
        positions = self._ephemeris.calculate_positions(
            self._datetime, self._location, objects_to_calculate
        )

        # Step 2: Calculate all house systems AND angles
        house_systems_map: dict[str, HouseCusps] = {}
        calculated_angles: list[CelestialPosition] = []

        for engine in self._house_engines:
            system_name = engine.system_name
            if system_name in house_systems_map:
                continue  # Avoid duplicate calculations

            # Call the efficient protocol method
            cusps, angles = engine.calculate_house_data(self._datetime, self._location)

            house_systems_map[system_name] = cusps

            # Angles are universal, only save them once
            if not calculated_angles:
                calculated_angles = angles

        # Step 3: Add angles to the main position list
        positions.extend(calculated_angles)

        # Step 4: Run additional components (Arabic parts, etc)
        # (Components can now see angles in the position list)
        for component in self._components:
            additional = component.calculate(
                self._datetime,
                self._location,
                positions,
                house_systems_map,  # Pass the full map of cusps
            )
            positions.extend(additional)

        # Step 5: Assign house placements for all systems
        house_placements_map: dict[str, dict[str, int]] = {}
        for engine in self._house_engines:
            system_name = engine.system_name
            cusps = house_systems_map[system_name]

            # Get the {object_name: house_num} dict
            placements = engine.assign_houses(positions, cusps)
            house_placements_map[system_name] = placements

        # Step 6: Calculate aspects (if engine provided)
        aspects = []
        if self._aspect_engine:
            aspects = self._aspect_engine.calculate_aspects(
                positions,
                self._orb_engine,  # Pass the configured orb engine
            )

        # Step 7: Build final chart
        return CalculatedChart(
            datetime=self._datetime,
            location=self._location,
            positions=tuple(positions),
            house_systems=house_systems_map,
            house_placements=house_placements_map,
            aspects=tuple(aspects),
        )
