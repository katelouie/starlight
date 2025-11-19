"""
Extended canvas layers for position tables and aspectarian grids.

These layers render tabular data outside the main chart wheel,
requiring an extended canvas with additional space.
"""

from typing import Any

import svgwrite

from starlight.core.models import CalculatedChart, ObjectType
from starlight.core.registry import get_aspect_info

from .core import ChartRenderer, get_glyph


def _is_comparison(obj):
    """Check if object is a Comparison (avoid circular import)."""
    return hasattr(obj, "comparison_type") and hasattr(obj, "chart1") and hasattr(obj, "chart2")


def _filter_objects_for_tables(positions, object_types=None):
    """
    Filter positions to include in position tables and aspectarian.

    Default includes:
    - All PLANET objects (except Earth)
    - All ASTEROID objects
    - All POINT objects
    - North Node only (exclude South Node)
    - ASC/AC and MC only (exclude DSC/DC and IC)

    Default excludes:
    - MIDPOINT, ARABIC_PART, FIXED_STAR

    Args:
        positions: List of CelestialPosition objects
        object_types: Optional list of ObjectType enum values or strings to include.
                     If None, uses default filter (planet, asteroid, point, node, angle).
                     Examples: ["planet", "asteroid", "midpoint"]
                              [ObjectType.PLANET, ObjectType.ASTEROID]

    Returns:
        Filtered list of CelestialPosition objects
    """
    # Convert object_types to a set of ObjectType enums for fast lookup
    if object_types is None:
        # Default: include planet, asteroid, point, node, angle
        included_types = {
            ObjectType.PLANET,
            ObjectType.ASTEROID,
            ObjectType.POINT,
            ObjectType.NODE,
            ObjectType.ANGLE,
        }
    else:
        # Convert strings to ObjectType enums
        included_types = set()
        for obj_type in object_types:
            if isinstance(obj_type, str):
                # Convert string to ObjectType enum
                try:
                    included_types.add(ObjectType(obj_type.lower()))
                except ValueError:
                    # Skip invalid type names
                    pass
            elif isinstance(obj_type, ObjectType):
                included_types.add(obj_type)

    filtered = []
    for p in positions:
        # Skip Earth
        if p.name == "Earth":
            continue

        # Check if object type is in included types
        if p.object_type not in included_types:
            continue

        # For planets: include all except Earth (already checked)
        if p.object_type == ObjectType.PLANET:
            filtered.append(p)
            continue

        # For asteroids: include all
        if p.object_type == ObjectType.ASTEROID:
            filtered.append(p)
            continue

        # For nodes: include North Node only (exclude South Node)
        if p.object_type == ObjectType.NODE:
            if p.name in ("North Node", "True Node", "Mean Node"):
                filtered.append(p)
            continue

        # For points: include all
        if p.object_type == ObjectType.POINT:
            filtered.append(p)
            continue

        # For angles: include only ASC/AC and MC (exclude DSC/DC and IC)
        if p.object_type == ObjectType.ANGLE:
            if p.name in ("ASC", "AC", "Ascendant", "MC", "Midheaven"):
                filtered.append(p)
            continue

        # For midpoints and arabic parts: include all if type is in included_types
        if p.object_type in (ObjectType.MIDPOINT, ObjectType.ARABIC_PART, ObjectType.FIXED_STAR):
            filtered.append(p)
            continue

    return filtered


class PositionTableLayer:
    """
    Renders a table of planetary positions.

    Shows planet name, sign, degree, house, and speed in a tabular format.
    Respects chart theme colors.
    """

    DEFAULT_STYLE = {
        "text_color": "#333333",
        "header_color": "#222222",
        "text_size": "10px",
        "header_size": "11px",
        "line_height": 16,
        "col_spacing": 55,  # Pixels between columns (reduced from 70 for tighter spacing)
        "font_weight": "normal",
        "header_weight": "bold",
        "show_speed": True,
        "show_house": True,
    }

    def __init__(
        self,
        x_offset: float = 0,
        y_offset: float = 0,
        style_override: dict[str, Any] | None = None,
        object_types: list[str | ObjectType] | None = None,
    ) -> None:
        """
        Initialize position table layer.

        Args:
            x_offset: X position offset from canvas origin
            y_offset: Y position offset from canvas origin
            style_override: Optional style overrides
            object_types: Optional list of object types to include.
                         If None, uses default (planet, asteroid, point, node, angle).
                         Examples: ["planet", "asteroid", "midpoint"]
        """
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.style = {**self.DEFAULT_STYLE, **(style_override or {})}
        self.object_types = object_types

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart
    ) -> None:
        """Render position table.

        Handles both CalculatedChart and Comparison objects.
        For Comparison, displays interleaved positions from both charts.
        """
        # Check if this is a Comparison object
        is_comparison = _is_comparison(chart)

        if is_comparison:
            # Get positions from both charts using filter function
            chart1_positions = _filter_objects_for_tables(chart.chart1.positions, self.object_types)
            chart2_positions = _filter_objects_for_tables(chart.chart2.positions, self.object_types)

            # Sort both lists
            type_priority = {
                ObjectType.PLANET: 0,
                ObjectType.ASTEROID: 1,
                ObjectType.NODE: 2,
                ObjectType.POINT: 3,
                ObjectType.ANGLE: 4,
                ObjectType.MIDPOINT: 5,
                ObjectType.ARABIC_PART: 6,
                ObjectType.FIXED_STAR: 7,
            }
            chart1_positions.sort(key=lambda p: (type_priority.get(p.object_type, 99), p.name))
            chart2_positions.sort(key=lambda p: (type_priority.get(p.object_type, 99), p.name))

            # Interleave the positions
            positions = []
            max_len = max(len(chart1_positions), len(chart2_positions))
            for i in range(max_len):
                if i < len(chart1_positions):
                    positions.append(("chart1", chart1_positions[i]))
                if i < len(chart2_positions):
                    positions.append(("chart2", chart2_positions[i]))
        else:
            # Standard CalculatedChart - use filter function to include angles
            chart_positions = _filter_objects_for_tables(chart.positions, self.object_types)

            # Sort by object type priority, then name
            type_priority = {
                ObjectType.PLANET: 0,
                ObjectType.ASTEROID: 1,
                ObjectType.NODE: 2,
                ObjectType.POINT: 3,
                ObjectType.ANGLE: 4,
                ObjectType.MIDPOINT: 5,
                ObjectType.ARABIC_PART: 6,
                ObjectType.FIXED_STAR: 7,
            }
            chart_positions.sort(key=lambda p: (type_priority.get(p.object_type, 99), p.name))
            positions = [(None, p) for p in chart_positions]  # Wrap in tuples for consistency

        # Build table
        x_start = self.x_offset
        y_start = self.y_offset

        # Header row
        headers = ["Planet", "Sign", "Degree"]
        if self.style["show_house"]:
            headers.append("House")
        if self.style["show_speed"]:
            headers.append("Speed")

        # Render headers
        for i, header in enumerate(headers):
            x = x_start + (i * self.style["col_spacing"])
            dwg.add(
                dwg.text(
                    header,
                    insert=(x, y_start),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["header_size"],
                    fill=self.style["header_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["header_weight"],
                )
            )

        # Render data rows
        for row_idx, (owner, pos) in enumerate(positions):
            y = y_start + ((row_idx + 1) * self.style["line_height"])

            # Column 0: Planet name + glyph (with chart indicator for comparisons)
            glyph_info = get_glyph(pos.name)
            if glyph_info["type"] == "unicode":
                planet_text = f"{glyph_info['value']} {pos.name}"
            else:
                planet_text = pos.name

            # Add chart indicator for comparisons
            if owner == "chart1":
                planet_text += " ①"
            elif owner == "chart2":
                planet_text += " ②"

            # Add retrograde symbol if applicable
            if pos.is_retrograde:
                planet_text += " ℞"

            dwg.add(
                dwg.text(
                    planet_text,
                    insert=(x_start, y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=self.style["text_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 1: Sign
            x_sign = x_start + self.style["col_spacing"]
            dwg.add(
                dwg.text(
                    pos.sign,
                    insert=(x_sign, y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=self.style["text_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 2: Degree
            degrees = int(pos.sign_degree)
            minutes = int((pos.sign_degree % 1) * 60)
            degree_text = f"{degrees}°{minutes:02d}'"
            x_degree = x_start + (2 * self.style["col_spacing"])
            dwg.add(
                dwg.text(
                    degree_text,
                    insert=(x_degree, y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=self.style["text_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 3: House (if enabled)
            col_offset = 3
            if self.style["show_house"]:
                if is_comparison:
                    # For comparisons, show house in respective chart
                    if owner == "chart1":
                        house = self._get_house_placement(chart.chart1, pos)
                    elif owner == "chart2":
                        house = self._get_house_placement(chart.chart2, pos)
                    else:
                        house = None
                else:
                    house = self._get_house_placement(chart, pos)

                x_house = x_start + (col_offset * self.style["col_spacing"])
                dwg.add(
                    dwg.text(
                        str(house) if house else "-",
                        insert=(x_house, y),
                        text_anchor="start",
                        dominant_baseline="hanging",
                        font_size=self.style["text_size"],
                        fill=self.style["text_color"],
                        font_family=renderer.style["font_family_text"],
                        font_weight=self.style["font_weight"],
                    )
                )
                col_offset += 1

            # Column 4: Speed (if enabled)
            if self.style["show_speed"]:
                speed_text = f"{pos.speed_longitude:.2f}"
                x_speed = x_start + (col_offset * self.style["col_spacing"])
                dwg.add(
                    dwg.text(
                        speed_text,
                        insert=(x_speed, y),
                        text_anchor="start",
                        dominant_baseline="hanging",
                        font_size=self.style["text_size"],
                        fill=self.style["text_color"],
                        font_family=renderer.style["font_family_text"],
                        font_weight=self.style["font_weight"],
                    )
                )

    def _get_house_placement(self, chart: CalculatedChart, position) -> int | None:
        """Get house placement for a position."""
        if not chart.default_house_system or not chart.house_placements:
            return None

        placements = chart.house_placements.get(chart.default_house_system, {})
        return placements.get(position.name)


class HouseCuspTableLayer:
    """
    Renders a table of house cusps with sign placements.

    Shows house number, cusp longitude, sign, and degree in sign.
    Respects chart theme colors.
    """

    DEFAULT_STYLE = {
        "text_color": "#333333",
        "header_color": "#222222",
        "text_size": "10px",
        "header_size": "11px",
        "line_height": 16,
        "col_spacing": 55,  # Pixels between columns (reduced from 70 for tighter spacing)
        "font_weight": "normal",
        "header_weight": "bold",
    }

    def __init__(
        self,
        x_offset: float = 0,
        y_offset: float = 0,
        style_override: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize house cusp table layer.

        Args:
            x_offset: X position offset from canvas origin
            y_offset: Y position offset from canvas origin
            style_override: Optional style overrides
        """
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.style = {**self.DEFAULT_STYLE, **(style_override or {})}

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        """Render house cusp table.

        Only works for CalculatedChart objects (not Comparison).
        """
        # Skip if this is a Comparison object
        if _is_comparison(chart):
            return

        # Get house cusps from default house system
        if not chart.default_house_system:
            return

        houses = chart.get_houses(chart.default_house_system)
        if not houses:
            return

        # Build table
        x_start = self.x_offset
        y_start = self.y_offset

        # Header row
        headers = ["House", "Sign", "Degree"]

        # Render headers
        for i, header in enumerate(headers):
            x = x_start + (i * self.style["col_spacing"])
            dwg.add(
                dwg.text(
                    header,
                    insert=(x, y_start),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["header_size"],
                    fill=self.style["header_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["header_weight"],
                )
            )

        # Render data rows for all 12 houses
        for house_num in range(1, 13):
            y = y_start + (house_num * self.style["line_height"])

            # Get cusp longitude
            cusp_longitude = houses.cusps[house_num - 1]

            # Calculate sign and degree
            sign_index = int(cusp_longitude / 30)
            sign_names = [
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
            sign_name = sign_names[sign_index % 12]
            degree_in_sign = cusp_longitude % 30

            # Column 0: House number
            house_text = f"{house_num}"
            dwg.add(
                dwg.text(
                    house_text,
                    insert=(x_start, y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=self.style["text_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 1: Sign
            x_sign = x_start + self.style["col_spacing"]
            dwg.add(
                dwg.text(
                    sign_name,
                    insert=(x_sign, y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=self.style["text_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 2: Degree
            degrees = int(degree_in_sign)
            minutes = int((degree_in_sign % 1) * 60)
            degree_text = f"{degrees}°{minutes:02d}'"
            x_degree = x_start + (2 * self.style["col_spacing"])
            dwg.add(
                dwg.text(
                    degree_text,
                    insert=(x_degree, y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=self.style["text_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )


class AspectarianLayer:
    """
    Renders an aspectarian grid (triangle aspect table).

    Shows aspects between all planets in a classic triangle grid format.
    Respects chart theme colors.
    """

    DEFAULT_STYLE = {
        "text_color": "#333333",
        "header_color": "#222222",
        "grid_color": "#CCCCCC",
        "text_size": "10px",
        "header_size": "10px",
        "cell_size": 24,  # Size of each grid cell
        "font_weight": "normal",
        "header_weight": "bold",
        "show_grid": True,
    }

    def __init__(
        self,
        x_offset: float = 0,
        y_offset: float = 0,
        style_override: dict[str, Any] | None = None,
        object_types: list[str | ObjectType] | None = None,
    ) -> None:
        """
        Initialize aspectarian layer.

        Args:
            x_offset: X position offset from canvas origin
            y_offset: Y position offset from canvas origin
            style_override: Optional style overrides
            object_types: Optional list of object types to include.
                         If None, uses default (planet, asteroid, point, node, angle).
                         Examples: ["planet", "asteroid", "midpoint"]
        """
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.style = {**self.DEFAULT_STYLE, **(style_override or {})}
        self.object_types = object_types

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart
    ) -> None:
        """Render aspectarian grid.

        Handles both CalculatedChart and Comparison objects.
        For Comparison, displays cross-chart aspects including Asc and MC from both charts.
        """
        # Check if this is a Comparison object
        is_comparison = _is_comparison(chart)

        if is_comparison:
            # For comparisons: get all celestial objects using filter function
            # Chart1 objects (rows - inner wheel)
            chart1_objects = _filter_objects_for_tables(chart.chart1.positions, self.object_types)

            # Chart2 objects (columns - outer wheel)
            chart2_objects = _filter_objects_for_tables(chart.chart2.positions, self.object_types)

            # Sort by traditional order (planets first, nodes, points, then angles)
            object_order = [
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
                "North Node",
                "True Node",
                "Mean Node",
                "ASC",
                "AC",
                "Ascendant",
                "MC",
                "Midheaven",
            ]

            chart1_objects.sort(
                key=lambda p: object_order.index(p.name)
                if p.name in object_order
                else 99
            )
            chart2_objects.sort(
                key=lambda p: object_order.index(p.name)
                if p.name in object_order
                else 99
            )

            # Build aspect lookup from cross_aspects
            aspect_lookup = {}
            for aspect in chart.cross_aspects:
                # Key format: (chart1_obj_name, chart2_obj_name)
                key = (aspect.object1.name, aspect.object2.name)
                aspect_lookup[key] = aspect

            # Use chart1_objects for rows, chart2_objects for columns
            row_objects = chart1_objects
            col_objects = chart2_objects

        else:
            # Standard CalculatedChart - use filter function to include angles and nodes
            planets = _filter_objects_for_tables(chart.positions, self.object_types)

            # Sort by traditional order (planets, nodes, points, angles)
            planet_order = [
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
                "North Node",
                "True Node",
                "Mean Node",
                "ASC",
                "AC",
                "Ascendant",
                "MC",
                "Midheaven",
            ]
            planets.sort(
                key=lambda p: planet_order.index(p.name)
                if p.name in planet_order
                else 99
            )

            # Build aspect lookup
            aspect_lookup = {}
            for aspect in chart.aspects:
                key1 = (aspect.object1.name, aspect.object2.name)
                key2 = (aspect.object2.name, aspect.object1.name)
                aspect_lookup[key1] = aspect
                aspect_lookup[key2] = aspect

            # Use planets for both rows and columns (traditional triangle grid)
            row_objects = planets
            col_objects = planets

        # Render grid
        cell_size = self.style["cell_size"]
        x_start = self.x_offset
        y_start = self.y_offset

        if is_comparison:
            # For comparisons: full rectangular grid (chart1 rows × chart2 columns)
            # Column headers (chart2 objects - outer wheel) - aligned at left edge of column
            for col_idx, obj in enumerate(col_objects):
                glyph_info = get_glyph(obj.name)
                glyph = glyph_info["value"] if glyph_info["type"] == "unicode" else obj.name[:2]

                # Add ② indicator for chart2
                glyph = f"{glyph}②"

                x = x_start + ((col_idx + 1) * cell_size)  # Left edge of column
                y = y_start

                dwg.add(
                    dwg.text(
                        glyph,
                        insert=(x, y),
                        text_anchor="start",  # Align at left edge
                        dominant_baseline="hanging",
                        font_size=self.style["header_size"],
                        fill=self.style["header_color"],
                        font_family=renderer.style["font_family_glyphs"],
                        font_weight=self.style["header_weight"],
                    )
                )

            # Row headers (chart1 objects - inner wheel) and grid cells
            for row_idx, obj_row in enumerate(row_objects):
                glyph_info = get_glyph(obj_row.name)
                glyph = glyph_info["value"] if glyph_info["type"] == "unicode" else obj_row.name[:2]

                # Add ① indicator for chart1
                glyph = f"{glyph}①"

                y_row = y_start + ((row_idx + 1) * cell_size) + (cell_size / 2)

                # Row header
                dwg.add(
                    dwg.text(
                        glyph,
                        insert=(x_start, y_row),
                        text_anchor="start",
                        dominant_baseline="middle",
                        font_size=self.style["header_size"],
                        fill=self.style["header_color"],
                        font_family=renderer.style["font_family_glyphs"],
                        font_weight=self.style["header_weight"],
                    )
                )

                # Grid cells (all columns for rectangular grid)
                for col_idx, obj_col in enumerate(col_objects):
                    x_cell = x_start + ((col_idx + 1) * cell_size) + (cell_size / 2)
                    y_cell = y_row

                    # Draw grid lines if enabled
                    if self.style["show_grid"]:
                        cell_x = x_start + ((col_idx + 1) * cell_size)
                        cell_y = y_start + ((row_idx + 1) * cell_size)

                        dwg.add(
                            dwg.rect(
                                insert=(cell_x, cell_y),
                                size=(cell_size, cell_size),
                                fill="none",
                                stroke=self.style["grid_color"],
                                stroke_width=0.5,
                            )
                        )

                    # Check for cross-chart aspect (chart1_obj → chart2_obj)
                    aspect_key = (obj_row.name, obj_col.name)
                    if aspect_key in aspect_lookup:
                        aspect = aspect_lookup[aspect_key]
                        aspect_info = get_aspect_info(aspect.aspect_name)

                        if aspect_info and aspect_info.glyph:
                            aspect_glyph = aspect_info.glyph
                        else:
                            aspect_glyph = aspect.aspect_name[:1]

                        # Use aspect color if available
                        if aspect_info and aspect_info.color:
                            text_color = aspect_info.color
                        else:
                            text_color = self.style["text_color"]

                        dwg.add(
                            dwg.text(
                                aspect_glyph,
                                insert=(x_cell, y_cell),
                                text_anchor="middle",
                                dominant_baseline="middle",
                                font_size=self.style["text_size"],
                                fill=text_color,
                                font_family=renderer.style["font_family_glyphs"],
                                font_weight=self.style["font_weight"],
                            )
                        )

        else:
            # Standard CalculatedChart: triangle grid
            # Column headers (top) - aligned at left edge of column
            for col_idx in range(len(row_objects) - 1):
                obj = row_objects[col_idx]
                glyph_info = get_glyph(obj.name)
                glyph = glyph_info["value"] if glyph_info["type"] == "unicode" else obj.name[:2]

                x = x_start + ((col_idx + 1) * cell_size)  # Left edge of column
                y = y_start

                dwg.add(
                    dwg.text(
                        glyph,
                        insert=(x, y),
                        text_anchor="start",  # Align at left edge
                        dominant_baseline="hanging",
                        font_size=self.style["header_size"],
                        fill=self.style["header_color"],
                        font_family=renderer.style["font_family_glyphs"],
                        font_weight=self.style["header_weight"],
                    )
                )

            # Row headers (left) and grid cells (lower triangle only)
            for row_idx in range(1, len(row_objects)):
                obj_row = row_objects[row_idx]
                glyph_info = get_glyph(obj_row.name)
                glyph = glyph_info["value"] if glyph_info["type"] == "unicode" else obj_row.name[:2]

                y_row = y_start + (row_idx * cell_size) + (cell_size / 2)

                # Row header
                dwg.add(
                    dwg.text(
                        glyph,
                        insert=(x_start, y_row),
                        text_anchor="start",
                        dominant_baseline="middle",
                        font_size=self.style["header_size"],
                        fill=self.style["header_color"],
                        font_family=renderer.style["font_family_glyphs"],
                        font_weight=self.style["header_weight"],
                    )
                )

                # Grid cells (only lower triangle)
                for col_idx in range(row_idx):
                    obj_col = row_objects[col_idx]

                    x_cell = x_start + ((col_idx + 1) * cell_size) + (cell_size / 2)
                    y_cell = y_row

                    # Draw grid lines if enabled
                    if self.style["show_grid"]:
                        # Cell border
                        cell_x = x_start + ((col_idx + 1) * cell_size)
                        cell_y = y_start + (row_idx * cell_size)

                        dwg.add(
                            dwg.rect(
                                insert=(cell_x, cell_y),
                                size=(cell_size, cell_size),
                                fill="none",
                                stroke=self.style["grid_color"],
                                stroke_width=0.5,
                            )
                        )

                    # Check for aspect
                    aspect_key = (obj_row.name, obj_col.name)
                    if aspect_key in aspect_lookup:
                        aspect = aspect_lookup[aspect_key]
                        aspect_info = get_aspect_info(aspect.aspect_name)

                        if aspect_info and aspect_info.glyph:
                            aspect_glyph = aspect_info.glyph
                        else:
                            aspect_glyph = aspect.aspect_name[:1]

                        # Use aspect color if available
                        if aspect_info and aspect_info.color:
                            text_color = aspect_info.color
                        else:
                            text_color = self.style["text_color"]

                        dwg.add(
                            dwg.text(
                                aspect_glyph,
                                insert=(x_cell, y_cell),
                                text_anchor="middle",
                                dominant_baseline="middle",
                                font_size=self.style["text_size"],
                                fill=text_color,
                                font_family=renderer.style["font_family_glyphs"],
                                font_weight=self.style["font_weight"],
                            )
                        )
