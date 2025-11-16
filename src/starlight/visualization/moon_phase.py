"""
Moon phase visualization layer.

Renders accurate moon phase symbols showing the illuminated portion
with curved terminator lines.
"""

from typing import Any

import svgwrite

from starlight.core.models import (
    CalculatedChart,
    CelestialPosition,
    ObjectType,
    PhaseData,
)

from .core import ChartRenderer


class MoonPhaseLayer:
    """
    Renders the moon phase in the center of the chart.

    This layer draws an accurate representation of the moon's current phase
    using curved terminator lines to show the illuminated portion.
    """

    DEFAULT_STYLE = {
        "size": 40,  # Radius in pixels
        "border_color": "#2C3E50",
        "border_width": 2,
        "lit_color": "#F8F9FA",
        "shadow_color": "#2C3E50",
        "opacity": 0.95,
    }

    def __init__(self, style_override: dict[str, Any] | None = None) -> None:
        """
        Initialize moon phase layer.

        Args:
            style_override: Optional style overrides
        """
        self.style = {**self.DEFAULT_STYLE, **(style_override or {})}

    def render(
        self,
        renderer: ChartRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """
        Render the moon phase.

        Args:
            renderer: ChartRenderer instance
            dwg: SVG drawing object
            chart: Calculated chart
        """
        # Find the Moon
        moon = chart.get_object("Moon")
        if not moon or not moon.phase:
            return

        # Access the phase data cleanly
        phase_data = moon.phase

        # Create moon phase symbol
        moon_group = self._create_moon_phase_symbol(
            dwg,
            phase_data.phase_angle,
            phase_data.illuminated_fraction,
            self.style["size"],
            self.style["border_color"],
            self.style["border_width"],
            self.style["lit_color"],
            self.style["shadow_color"],
            self.style["opacity"],
        )

        if moon_group:
            # Position at chart center
            centered_group = dwg.g(
                transform=f"translate({renderer.center}, {renderer.center})"
            )
            for element in moon_group.elements:
                centered_group.add(element)
            dwg.add(centered_group)

    def _create_moon_phase_symbol(
        self,
        dwg: svgwrite.Drawing,
        phase_angle: float,
        illuminated_fraction: float,
        radius: float,
        border_color: str,
        border_width: float,
        lit_color: str,
        shadow_color: str,
        opacity: float,
    ) -> svgwrite.container.Group:
        """
        Create an SVG group containing accurate moon phase visualization.

        Args:
            dwg: SVG drawing object
            moon: Moon position with phase data
            radius: Moon radius
            border_color: Border color
            border_width: Border width
            lit_color: Color for illuminated portion
            shadow_color: Color for shadowed portion
            opacity: Overall opacity

        Returns:
            SVG group containing moon phase
        """
        # Determine if waxing or waning
        waxing = self._is_moon_waxing(phase_angle)

        # Create group
        group = dwg.g()

        # Handle special cases
        if illuminated_fraction <= 0.01:
            # New moon - completely dark
            group.add(
                dwg.circle(
                    center=(0, 0),
                    r=radius,
                    fill=shadow_color,
                    stroke=border_color,
                    stroke_width=border_width,
                    opacity=opacity,
                )
            )
            return group
        elif illuminated_fraction >= 0.99:
            # Full moon - completely lit
            group.add(
                dwg.circle(
                    center=(0, 0),
                    r=radius,
                    fill=lit_color,
                    stroke=border_color,
                    stroke_width=border_width,
                    opacity=opacity,
                )
            )
            return group

        # Start with base circle (shadow)
        group.add(
            dwg.circle(
                center=(0, 0),
                r=radius,
                fill=shadow_color,
                stroke="none",
                opacity=opacity,
            )
        )

        # Calculate and draw the terminator
        if abs(illuminated_fraction - 0.5) < 0.001:
            # Quarter moon - exactly half lit
            if waxing:
                # First quarter - right half lit
                path_d = f"M 0 {-radius} A {radius} {radius} 0 0 1 0 {radius} Z"
            else:
                # Last quarter - left half lit
                path_d = f"M 0 {-radius} A {radius} {radius} 0 0 0 0 {radius} Z"

            group.add(
                dwg.path(d=path_d, fill=lit_color, stroke="none", opacity=opacity)
            )
        else:
            # Crescent or gibbous - curved terminator
            terminator_width = abs(2 * (illuminated_fraction - 0.5)) * radius

            if illuminated_fraction < 0.5:
                # Crescent phase
                if waxing:
                    path_d = self._create_crescent_path(radius, terminator_width, True)
                else:
                    path_d = self._create_crescent_path(radius, terminator_width, False)

                group.add(
                    dwg.path(d=path_d, fill=lit_color, stroke="none", opacity=opacity)
                )
            else:
                # Gibbous phase - fill with lit, add shadow crescent
                group.add(
                    dwg.circle(
                        center=(0, 0),
                        r=radius,
                        fill=lit_color,
                        stroke="none",
                        opacity=opacity,
                    )
                )

                if waxing:
                    path_d = self._create_crescent_path(radius, terminator_width, False)
                else:
                    path_d = self._create_crescent_path(radius, terminator_width, True)

                group.add(
                    dwg.path(
                        d=path_d, fill=shadow_color, stroke="none", opacity=opacity
                    )
                )

        # Add border
        group.add(
            dwg.circle(
                center=(0, 0),
                r=radius,
                fill="none",
                stroke=border_color,
                stroke_width=border_width,
                opacity=opacity,
            )
        )

        return group

    def _is_moon_waxing(self, phase_angle: float) -> bool:
        """
        Determine if moon is waxing based on phase angle.

        Args:
            phase_angle: Phase angle in degrees

        Returns:
            True if waxing, False if waning
        """
        normalized_angle = phase_angle % 360
        return normalized_angle <= 180

    def _create_crescent_path(
        self, radius: float, terminator_width: float, on_right: bool
    ) -> str:
        """
        Create SVG path for crescent shape with elliptical terminator.

        Args:
            radius: Moon radius
            terminator_width: Width of terminator ellipse
            on_right: True if crescent on right, False if on left

        Returns:
            SVG path string
        """
        if on_right:
            # Crescent on right side
            path = f"M 0 {-radius} "
            path += f"A {radius} {radius} 0 0 1 0 {radius} "
            path += f"A {terminator_width} {radius} 0 0 0 0 {-radius} "
            path += "Z"
        else:
            # Crescent on left side
            path = f"M 0 {-radius} "
            path += f"A {radius} {radius} 0 0 0 0 {radius} "
            path += f"A {terminator_width} {radius} 0 0 1 0 {-radius} "
            path += "Z"

        return path


def draw_moon_phase_standalone(
    phase_frac: float,
    phase_angle: float,
    filename: str = "moon_phase.svg",
    size: int = 200,
    style: dict[str, Any] | None = None,
) -> str:
    """
    Draw a standalone moon phase SVG.

    Useful for testing or standalone moon phase displays.

    Args:
        phase_frac: Illuminated fraction (0-1)
        phase_angle: Phase angle in degrees (0-360)
        filename: Output filename
        size: SVG size in pixels
        style: Style overrides

    Returns:
        Filename of saved SVG

    Example:
        # Draw a waxing crescent
        draw_moon_phase_standalone(0.25, 90, "waxing_crescent.svg")

        # Draw a full moon
        draw_moon_phase_standalone(1.0, 180, "full_moon.svg")
    """
    moon = CelestialPosition(
        name="Moon",
        object_type=ObjectType.PLANET,
        longitude=0.0,
    )
    moon_phase_data = PhaseData(
        phase_angle=phase_angle,
        illuminated_fraction=phase_frac,
        elongation=0.0,
        apparent_diameter=0.0,
        apparent_magnitude=0.0,
    )
    object.__setattr__(moon, "phase", moon_phase_data)

    # Create SVG
    dwg = svgwrite.Drawing(
        filename=filename,
        size=(f"{size}px", f"{size}px"),
        viewBox=f"0 0 {size} {size}",
    )

    # Add background
    dwg.add(dwg.rect(insert=(0, 0), size=(size, size), fill="#1a1a1a"))

    # Create moon phase layer
    layer = MoonPhaseLayer(style_override=style)

    # Render (need a mock renderer/chart for the interface)
    from unittest.mock import Mock

    mock_renderer = Mock()
    mock_renderer.center = size // 2
    mock_chart = Mock()
    mock_chart.get_object = lambda name: moon if name == "Moon" else None

    layer.render(mock_renderer, dwg, mock_chart)

    dwg.save()
    return filename
