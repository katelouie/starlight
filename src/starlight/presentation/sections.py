"""
Report section implementations.

Each section extracts specific data from a CalculatedChart and formats it
into a standardized structure that renderers can consume.
"""

import datetime as dt
from typing import Any

from starlight.core.models import CalculatedChart, ObjectType


class ChartOverviewSection:
    """
    Overview section with basic chart information.

    Shows:
    - Native name (if available)
    - Birth date/time
    - Location
    - Chart type (day/night)
    - House system
    """

    @property
    def section_name(self) -> str:
        return "Chart Overview"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate chart overview data.

        Why key-value format?
        - Simple label: value pairs
        - Easy to render as a list or small table
        - Human-readable structure
        """
        data = {}

        # Date and time
        birth: dt.datetime = chart.datetime.local_datetime
        data["Date"] = birth.strftime("%B %d, %Y")
        data["Time"] = birth.strftime("%I:%M %p")
        data["Timezone"] = str(chart.location.timezone)

        # Location
        loc = chart.location
        data["Location"] = f"{loc.name}" if loc.name else "Unknown"
        data["Coordinates"] = f"{loc.latitude:.4f}°, {loc.longitude:.4f}°"

        # Chart metadata
        house_systems = ", ".join(chart.house_systems.keys())
        data["House System"] = house_systems

        # Sect (if available in metadata)
        if "dignities" in chart.metadata:
            sect = chart.metadata["dignities"].get("sect", "unknown")
            data["Chart Sect"] = f"{sect.title()} Chart"

        return {
            "type": "key_value",
            "data": data,
        }


class PlanetPositionSection:
    """Table of planet positions.

    Shows:
    - Planet name
    - Sign + degree
    - House (optional)
    - Speed (optional, shows retrograde status)
    """

    def __init__(
        self,
        include_speed: bool = False,
        include_house: bool = True,
        house_system: str | None = None,
    ) -> None:
        """
        Initialize section with display options.

        Args:
            include_speed: Show speed column (for retrograde detection)
            include_house: Show house placement column
            house_system: Which system to use for houses (None = chart default)
        """
        self.include_speed = include_speed
        self.include_house = include_house
        self.house_system = house_system

    @property
    def section_name(self) -> str:
        return "Planet Positions"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate planet positions table.
        """
        # Build headers based on options
        headers = ["Planet", "Position"]

        if self.include_house:
            headers.append("House")

        if self.include_speed:
            headers.append("Speed")
            headers.append("Motion")

        # Filter to planets, asteroids, nodes and points
        positions = [
            p
            for p in chart.positions
            if p.object_type
            in (
                ObjectType.PLANET,
                ObjectType.ASTEROID,
                ObjectType.NODE,
                ObjectType.POINT,
            )
        ]

        # Build rows
        rows = []
        for pos in positions:
            row = []
            # Planet name
            row.append(pos.name)

            # Position (e.g., "15° ♌ 32'")
            degree = int(pos.sign_degree)
            minute = int((pos.sign_degree % 1) * 60)
            row.append(f"{degree}° {pos.sign} {minute:02d}'")

            # House (if requested)
            if self.include_house:
                system = self.house_system or chart.default_house_system
                try:
                    house_placements = chart.house_placements[system]
                    house = house_placements.get(pos.name, "—")
                    row.append(str(house) if house else "—")
                except KeyError:
                    row.append("—")

            # Speed and motion (if requested)
            if self.include_speed:
                row.append(f"{pos.speed_longitude:.4f}°/day")
                row.append("Retrograde" if pos.is_retrograde else "Direct")

            rows.append(row)

        return {"type": "table", "headers": headers, "rows": rows}


class AspectSection:
    """
    Table of aspects between planets.

    Shows:
    - Planet 1
    - Aspect type
    - Planet 2
    - Orb (optional)
    - Applying/Separating (optional)
    """

    def __init__(
        self, mode: str = "all", orbs: bool = True, sort_by: str = "orb"
    ) -> None:
        """
        Initialize aspect section.

        Args:
            mode: "all", "major", "minor", or "harmonic"
        """
