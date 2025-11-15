"""
Concrete Render Layers (starlight.visualization.layers)

These are the concrete implementations of the IRenderLayer protocol.
Each class knows how to draw one specific part of a chart,
reading its data from the CalculatedChart object.
"""

import math
from typing import Any

import svgwrite

from starlight.core.models import CalculatedChart, CelestialPosition, HouseCusps

from .core import (
    ANGLE_GLYPHS,
    PLANET_GLYPHS,
    ZODIAC_GLYPHS,
    ChartRenderer,
    get_glyph,
    get_display_name,
)


class ZodiacLayer:
    """Renders the outer Zodiac ring, including glyphs and tick marks."""

    def __init__(self, style_override: dict[str, Any] | None = None) -> None:
        self.style = style_override or {}

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        style = renderer.style["zodiac"]
        style.update(self.style)

        # Draw the main zodiac ring background
        dwg.add(
            dwg.circle(
                center=(renderer.center, renderer.center),
                r=renderer.radii["zodiac_ring_outer"],
                fill=style["ring_color"],
                stroke="none",
            )
        )
        dwg.add(
            dwg.circle(
                center=(renderer.center, renderer.center),
                r=renderer.radii["zodiac_ring_inner"],
                fill=renderer.style["background_color"],  # Punch a hole
                stroke="none",
            )
        )

        # Draw 12 sign boundaries and glyphs
        for i in range(12):
            deg = i * 30.0

            # Line
            x1, y1 = renderer.polar_to_cartesian(
                deg, renderer.radii["zodiac_ring_outer"]
            )
            x2, y2 = renderer.polar_to_cartesian(
                deg, renderer.radii["zodiac_ring_inner"]
            )
            dwg.add(
                dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=style["line_color"],
                    stroke_width=0.5,
                )
            )

            # Glyph
            glyph_deg = (i * 30.0) + 15.0
            x_glyph, y_glyph = renderer.polar_to_cartesian(
                glyph_deg, renderer.radii["zodiac_glyph"]
            )
            dwg.add(
                dwg.text(
                    ZODIAC_GLYPHS[i],
                    insert=(x_glyph, y_glyph),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["glyph_size"],
                    fill=style["glyph_color"],
                    font_family=renderer.style["font_family_glyphs"],
                )
            )


class HouseCuspLayer:
    """
    Renders a *single* set of house cusps and numbers.

    To draw multiple systems, add multiple layers.
    """

    def __init__(
        self, house_system_name: str, style_override: dict[str, Any] | None = None
    ) -> None:
        """
        Args:
            house_system_name: The name of the system to pull from the CalculatedChart (eg "Pladicus")
            style_override: Optional style changes for this specific layer (eg. {"line_color": "red})
        """
        self.system_name = house_system_name
        self.style = style_override or {}

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        style = renderer.style["houses"].copy()
        style.update(self.style)

        try:
            house_cusps: HouseCusps = chart.get_houses(self.system_name)
        except (ValueError, KeyError):
            print(
                f"Warning: House system '{self.system_name}' not found in chart data."
            )
            return

        # Draw alternating fill wedges FIRST (if enabled)
        if style.get("fill_alternate", False):
            for i in range(12):
                cusp_deg = house_cusps.cusps[i]
                next_cusp_deg = house_cusps.cusps[(i + 1) % 12]

                # Handle 0-degree wrap
                if next_cusp_deg < cusp_deg:
                    next_cusp_deg += 360

                # Alternate between two fill colors
                fill_color = (
                    style["fill_color_1"] if i % 2 == 0 else style["fill_color_2"]
                )

                # Create a pie wedge path
                # Start at center, go to inner radius at cusp_deg, arc to next_cusp, back to center
                x_start, y_start = renderer.polar_to_cartesian(
                    cusp_deg, renderer.radii["aspect_ring_inner"]
                )
                x_end, y_end = renderer.polar_to_cartesian(
                    next_cusp_deg, renderer.radii["aspect_ring_inner"]
                )
                x_outer_start, y_outer_start = renderer.polar_to_cartesian(
                    cusp_deg, renderer.radii["zodiac_ring_inner"]
                )
                x_outer_end, y_outer_end = renderer.polar_to_cartesian(
                    next_cusp_deg, renderer.radii["zodiac_ring_inner"]
                )

                # Determine if we need the large arc flag (for arcs > 180 degrees)
                angle_diff = next_cusp_deg - cusp_deg
                large_arc = 1 if angle_diff > 180 else 0

                # Create path: outer arc + line + inner arc + line back
                path_data = f"M {x_outer_start},{y_outer_start} "
                path_data += f"A {renderer.radii['zodiac_ring_inner']},{renderer.radii['zodiac_ring_inner']} 0 {large_arc},0 {x_outer_end},{y_outer_end} "
                path_data += f"L {x_end},{y_end} "
                path_data += f"A {renderer.radii['aspect_ring_inner']},{renderer.radii['aspect_ring_inner']} 0 {large_arc},1 {x_start},{y_start} "
                path_data += "Z"

                dwg.add(
                    dwg.path(
                        d=path_data,
                        fill=fill_color,
                        stroke="none",
                    )
                )

        for i, cusp_deg in enumerate(house_cusps.cusps):
            house_num = i + 1

            # Draw cusp line
            x1, y1 = renderer.polar_to_cartesian(
                cusp_deg, renderer.radii["zodiac_ring_inner"]
            )
            x2, y2 = renderer.polar_to_cartesian(
                cusp_deg, renderer.radii["aspect_ring_inner"]
            )

            dwg.add(
                dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=style["line_color"],
                    stroke_width=style["line_width"],
                    stroke_dasharray=style.get("line_dash", "1.0"),
                )
            )

            # Draw house number
            # find the midpoint angle of the house
            next_cusp_deg = house_cusps.cusps[(i + 1) % 12]
            if next_cusp_deg < cusp_deg:
                next_cusp_deg += 360  # Handle 0-degree wrap

            mid_deg = (cusp_deg + next_cusp_deg) / 2.0

            x_num, y_num = renderer.polar_to_cartesian(
                mid_deg, renderer.radii["house_number_ring"]
            )

            dwg.add(
                dwg.text(
                    str(house_num),
                    insert=(x_num, y_num),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["number_size"],
                    fill=style["number_color"],
                    font_family=renderer.style["font_family_text"],
                )
            )


class AngleLayer:
    """Renders the primary chart angles (ASC, MC, DSC, IC)"""

    def __init__(self, style_override: dict[str, Any] | None = None) -> None:
        self.style = style_override or {}

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        style = renderer.style["angles"].copy()
        style.update(self.style)

        angles = chart.get_angles()

        for angle in angles:
            if angle.name not in ANGLE_GLYPHS:
                continue

            # Draw angle line (ASC/MC axis is the strongest)
            is_axis = angle.name in ("ASC", "MC")
            line_width = style["line_width"] if is_axis else style["line_width"] * 0.7
            line_color = (
                style["line_color"]
                if is_axis
                else renderer.style["houses"]["line_color"]
            )

            if angle.name in ("ASC", "MC", "DSC", "IC"):
                x1, y1 = renderer.polar_to_cartesian(
                    angle.longitude, renderer.radii["zodiac_ring_outer"]
                )
                x2, y2 = renderer.polar_to_cartesian(
                    angle.longitude, renderer.radii["aspect_ring_inner"]
                )
                dwg.add(
                    dwg.line(
                        start=(x1, y1),
                        end=(x2, y2),
                        stroke=line_color,
                        stroke_width=line_width,
                    )
                )

            # Draw angle glyph - positioned just inside the border with directional offset
            base_radius = renderer.radii["zodiac_ring_inner"] + 10
            x_glyph, y_glyph = renderer.polar_to_cartesian(angle.longitude, base_radius)

            # Apply directional offset based on angle name
            offset = 8  # pixels to nudge
            if angle.name == "ASC":  # 9 o'clock - nudge up
                y_glyph -= offset
            elif angle.name == "MC":  # 12 o'clock - nudge right
                x_glyph += offset
            elif angle.name == "DSC":  # 3 o'clock - nudge down
                y_glyph += offset
            elif angle.name == "IC":  # 6 o'clock - nudge left
                x_glyph -= offset

            dwg.add(
                dwg.text(
                    ANGLE_GLYPHS[angle.name],
                    insert=(x_glyph, y_glyph),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["glyph_size"],
                    fill=style["glyph_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight="bold",
                )
            )


class PlanetLayer:
    """Renders a set of planets at a specific radius."""

    def __init__(
        self,
        planet_set: list[CelestialPosition],
        radius_key: str = "planet_ring",
        style_override: dict[str, Any] | None = None,
    ) -> None:
        """
        Args:
            planet_set: The list of CelestialPosition objects to draw.
            radius_key: The key from renderer.radii to use (e.g., "planet_ring").
            style_override: Style overrides for this layer.
        """
        self.planets = planet_set
        self.radius_key = radius_key
        self.style = style_override or {}

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        style = renderer.style["planets"].copy()
        style.update(self.style)

        base_radius = renderer.radii[self.radius_key]

        # Calculate adjusted positions with collision detection
        adjusted_positions = self._calculate_adjusted_positions(
            self.planets, base_radius
        )

        # Draw all planets with their info columns
        for planet in self.planets:
            original_long = planet.longitude
            adjusted_long = adjusted_positions[planet]["longitude"]
            is_adjusted = adjusted_positions[planet]["adjusted"]

            # Draw connector line if position was adjusted
            if is_adjusted:
                x_original, y_original = renderer.polar_to_cartesian(
                    original_long, base_radius
                )
                x_adjusted, y_adjusted = renderer.polar_to_cartesian(
                    adjusted_long, base_radius
                )
                dwg.add(
                    dwg.line(
                        start=(x_original, y_original),
                        end=(x_adjusted, y_adjusted),
                        stroke="#999999",
                        stroke_width=0.5,
                        stroke_dasharray="2,2",
                        opacity=0.6,
                    )
                )

            # Draw planet glyph at adjusted position
            glyph = get_glyph(planet.name)
            x, y = renderer.polar_to_cartesian(adjusted_long, base_radius)

            color = (
                style["retro_color"] if planet.is_retrograde else style["glyph_color"]
            )
            dwg.add(
                dwg.text(
                    glyph,
                    insert=(x, y),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["glyph_size"],
                    fill=color,
                    font_family=renderer.style["font_family_glyphs"],
                )
            )

            # Draw Planet Info (Degrees, Sign, Minutes) - all at ADJUSTED longitude
            # This creates a "column" of info that moves together with the glyph
            glyph_size_px = float(style["glyph_size"][:-2])

            # Calculate radii for info rings (inward from planet glyph)
            degrees_radius = base_radius - (glyph_size_px * 0.8)
            sign_radius = base_radius - (glyph_size_px * 1.2)
            minutes_radius = base_radius - (glyph_size_px * 1.6)

            # Degrees
            deg_str = f"{int(planet.sign_degree)}°"
            x_deg, y_deg = renderer.polar_to_cartesian(adjusted_long, degrees_radius)
            dwg.add(
                dwg.text(
                    deg_str,
                    insert=(x_deg, y_deg),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["info_size"],
                    fill=style["info_color"],
                    font_family=renderer.style["font_family_text"],
                )
            )

            # Sign glyph
            sign_glyph = ZODIAC_GLYPHS[int(planet.longitude // 30)]
            x_sign, y_sign = renderer.polar_to_cartesian(adjusted_long, sign_radius)
            dwg.add(
                dwg.text(
                    sign_glyph,
                    insert=(x_sign, y_sign),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["info_size"],
                    fill=style["info_color"],
                    font_family=renderer.style["font_family_glyphs"],
                )
            )

            # Minutes
            min_str = f"{int((planet.sign_degree % 1) * 60):02d}'"
            x_min, y_min = renderer.polar_to_cartesian(adjusted_long, minutes_radius)
            dwg.add(
                dwg.text(
                    min_str,
                    insert=(x_min, y_min),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["info_size"],
                    fill=style["info_color"],
                    font_family=renderer.style["font_family_text"],
                )
            )

    def _calculate_adjusted_positions(
        self, planets: list[CelestialPosition], base_radius: float
    ) -> dict[CelestialPosition, dict[str, Any]]:
        """
        Calculate adjusted positions for planets with collision detection.

        Groups colliding planets and spreads them evenly while maintaining
        their original order.

        Args:
            planets: List of planets to position
            base_radius: The radius at which to place planet glyphs

        Returns:
            Dictionary mapping each planet to its position info:
            {
                planet: {
                    "longitude": adjusted_longitude,
                    "adjusted": bool (True if position was changed)
                }
            }
        """
        # Minimum angular separation in degrees
        min_separation = 6.0

        # Sort planets by longitude to maintain order
        sorted_planets = sorted(planets, key=lambda p: p.longitude)

        # Find collision groups
        collision_groups = self._find_collision_groups(sorted_planets, min_separation)

        # Adjust positions for each group
        adjusted_positions = {}

        for group in collision_groups:
            if len(group) == 1:
                # No collision - use original position
                planet = group[0]
                adjusted_positions[planet] = {
                    "longitude": planet.longitude,
                    "adjusted": False,
                }
            else:
                # Collision detected - spread the group evenly
                self._spread_group(group, min_separation, adjusted_positions)

        return adjusted_positions

    def _find_collision_groups(
        self, sorted_planets: list[CelestialPosition], min_separation: float
    ) -> list[list[CelestialPosition]]:
        """
        Find groups of planets that are too close together.

        Args:
            sorted_planets: Planets sorted by longitude
            min_separation: Minimum angular separation required

        Returns:
            List of groups, where each group is a list of colliding planets
        """
        if not sorted_planets:
            return []

        groups = []
        current_group = [sorted_planets[0]]

        for i in range(1, len(sorted_planets)):
            prev_planet = sorted_planets[i - 1]
            curr_planet = sorted_planets[i]

            # Calculate angular distance
            distance = curr_planet.longitude - prev_planet.longitude
            # Handle wrap-around at 0°/360°
            if distance < 0:
                distance += 360

            if distance < min_separation:
                # Add to current group
                current_group.append(curr_planet)
            else:
                # Start new group
                groups.append(current_group)
                current_group = [curr_planet]

        # Don't forget the last group
        groups.append(current_group)

        return groups

    def _spread_group(
        self,
        group: list[CelestialPosition],
        min_separation: float,
        adjusted_positions: dict[CelestialPosition, dict[str, Any]],
    ) -> None:
        """
        Spread a group of colliding planets evenly while maintaining order.

        Args:
            group: List of planets in collision (already sorted by longitude)
            min_separation: Minimum angular separation required
            adjusted_positions: Dictionary to populate with adjusted positions
        """
        # Calculate the center point of the group
        group_start = group[0].longitude
        group_end = group[-1].longitude

        # Handle wrap-around
        if group_end < group_start:
            group_end += 360

        group_center = (group_start + group_end) / 2

        # Calculate total span needed for the group
        num_planets = len(group)
        total_span = (num_planets - 1) * min_separation

        # Calculate start position (centered around group center)
        spread_start = group_center - (total_span / 2)

        # Assign positions evenly across the span
        for i, planet in enumerate(group):
            adjusted_long = (spread_start + (i * min_separation)) % 360

            # Check if position was actually changed
            original_long = planet.longitude
            angle_diff = abs(adjusted_long - original_long)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            is_adjusted = angle_diff > 0.5  # More than 0.5° difference counts as adjusted

            adjusted_positions[planet] = {
                "longitude": adjusted_long,
                "adjusted": is_adjusted,
            }


class AspectLayer:
    """Renders the aspect lines within the chart."""

    def __init__(self, style_override: dict[str, Any] | None = None):
        self.style = style_override or {}

    def render(
        self,
        renderer: ChartRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        style = renderer.style["aspects"].copy()
        style.update(self.style)

        radius = renderer.radii["aspect_ring_inner"]

        dwg.add(
            dwg.circle(
                center=(renderer.center, renderer.center),
                r=radius,
                fill=style["background_color"],
                stroke=style["line_color"],
            )
        )

        for aspect in chart.aspects:
            # Get style, falling back to default
            aspect_style = style.get(aspect.aspect_name, style["default"])

            # Get positions on the inner aspect ring
            x1, y1 = renderer.polar_to_cartesian(aspect.object1.longitude, radius)
            x2, y2 = renderer.polar_to_cartesian(aspect.object2.longitude, radius)

            dwg.add(
                dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=aspect_style["color"],
                    stroke_width=aspect_style["width"],
                    stroke_dasharray=aspect_style["dash"],
                )
            )
