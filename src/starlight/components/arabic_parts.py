"""
Arabic Parts calculator component.

Arabic Parts (also called Lots) are calculated points based on
the distances between three chart objects. They represent themes
or areas of life.

Formula: Lot = Asc + Point2 - Point1

Many lots are "sect-aware" - they flip the formula for day vs night charts:
- Day Chart: Asc + Point2 - Point1
- Night Chart: Asc + Point1 - Point2
"""

from starlight.components.dignity import determine_sect
from starlight.core.models import (
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
    ObjectType,
)

# Arabic parts catalog
# Each entry defines: which points to use, whether to flip for sect
ARABIC_PARTS_CATALOG = {
    "Part of Fortune": {
        "points": ["ASC", "Moon", "Sun"],
        "sect_flip": True,
        "description": "Material wellbeing, body, health",
    },
    "Part of Spirit": {
        "points": ["ASC", "Sun", "Moon"],
        "sect_flip": True,
        "description": "Spiritual purpose, inner life",
    },
    "Part of Love": {
        "points": ["ASC", "Venus", "Sun"],
        "sect_flip": False,
        "description": "Romantic love, desire",
    },
    "Part of Marriage": {
        "points": ["ASC", "Venus", "Jupiter"],
        "sect_flip": False,
        "description": "Partnership, committed relationships",
    },
    "Part of Eros": {
        "points": ["ASC", "Venus", "Mars"],
        "sect_flip": False,
        "description": "Passion, sexual attraction",
    },
    "Part of Children": {
        "points": ["ASC", "Jupiter", "Moon"],
        "sect_flip": False,
        "description": "Fertility, relationship with children",
    },
    "Part of Father": {
        "points": ["ASC", "Sun", "Saturn"],
        "sect_flip": False,
        "description": "Relationship with father figure",
    },
    "Part of Mother": {
        "points": ["ASC", "Venus", "Moon"],
        "sect_flip": False,
        "description": "Relationship with mother figure",
    },
    "Part of Profession": {
        "points": ["ASC", "MC", "Sun"],
        "sect_flip": False,
        "description": "Career, vocation, public standing",
    },
    "Part of Death": {
        "points": ["ASC", "Saturn", "Moon"],
        "sect_flip": False,
        "description": "Transformation, endings, legacy",
    },
}


class ArabicPartsCalculator:
    """
    Calculate Arabic Parts (Lots) for a chart.

    Arabic Parts are senstitive points calculated from the distances between three
    chart objects. They represent specific life themes.
    """

    def __init__(
        self,
        parts_to_calculate: list[str] | None = None,
        custom_parts: dict | None = None,
    ) -> None:
        """
        Initialize Arabic Parts calculator.

        Args:
            parts_to_calculate: Which parts to calculate (None=all)
            custom_parts: Additional custom parts definitions
        """
        self._catalog = ARABIC_PARTS_CATALOG.copy()
        if custom_parts:
            self._catalog.update(custom_parts)

        self._parts_to_calculate = parts_to_calculate

    @property
    def component_name(self) -> str:
        return "Arabic Parts"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]],
    ) -> list[CelestialPosition]:
        """
        Calculate Arabic Parts.

        Args:
            datetime: Chart datetime (unused, required by protocol)
            location: Chart location (unused, required by protocol)
            positions: Already-calculated positions
            house_systems_map: House systems and House cusps
            house_placements_map: Object placement by house system

        Returns:
            List of CelestialPosition objects for each part
        """
        # Build position lookup
        pos_dict = {p.name: p for p in positions}

        # Determine chart sect
        sect = determine_sect(positions)

        # Calculate each part
        parts = []

        if self._parts_to_calculate:
            catalog_to_use = {
                k: v for k, v in self._catalog.items() if k in self._parts_to_calculate
            }
        else:
            catalog_to_use = self._catalog

        for part_name, part_config in catalog_to_use.items():
            try:
                part_position = self._calculate_single_part(
                    part_name, part_config, pos_dict, sect
                )
                parts.append(part_position)
            except KeyError as e:
                # Missing required position
                print(f"Warning: Could not calculate {part_name}: missing ({e})")
                continue

        return parts

    def _calculate_single_part(
        self,
        part_name: str,
        part_config: dict,
        positions: dict[str, CelestialPosition],
        sect: str,
    ) -> CelestialPosition:
        """
        Calculate a single Arabic Part.

        Args:
            part_name: Name of the part
            part_config: Configuration (points, sect_flip)
            positions: Position lookup
            sect: Chart sect ("day" or "night")

        Returns:
            CelestialPosition for the calculated part
        """
        point_names = part_config["points"]
        sect_flip = part_config["sect_flip"]

        # Get the three points
        asc = positions[point_names[0]]
        point2 = positions[point_names[1]]
        point3 = positions[point_names[2]]

        # Calculate longitude based on formula and sect
        if sect == "day" or not sect_flip:
            # Day formula: ASC + Point2 - Point3
            longitude = (asc.longitude + point2.longitude - point3.longitude) % 360
        else:
            # Night formula (flipped): ASC + Point3 - Point2
            longitude = (asc.longitude + point3.longitude - point2.longitude) % 360

        # Create CelestialPosition for this part
        return CelestialPosition(
            name=part_name,
            object_type=ObjectType.ARABIC_PART,
            longitude=longitude,
        )


class PartOfFortuneCalculator:
    """
    Simplified calculator for just Part of Fortune.

    This is useful for when you only need Fortune and don't want to calculate all
    Arabic Parts.
    """

    @property
    def component_name(self) -> str:
        return "Part of Fortune"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]],
    ) -> list[CelestialPosition]:
        """Calculate only Part of Fortune."""
        calculator = ArabicPartsCalculator(parts_to_calculate=["Part of Fortune"])
        return calculator.calculate(
            datetime, location, positions, house_systems_map, house_placements_map
        )
