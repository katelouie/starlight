#!/usr/bin/env python3
"""
Moon Phase SVG Tester
Tests and demonstrates the moon phase SVG generation functions
"""

import svgwrite
from typing import Optional
import os
from dataclasses import dataclass


@dataclass
class MockMoonPlanet:
    """Mock moon planet object for testing"""

    phase_frac: float  # 0.0 to 1.0
    phase_angle: float  # 0 to 360 degrees


class MoonPhaseRenderer:
    """Moon phase SVG renderer class"""

    def _create_moon_phase_symbol(
        self, moon_planet
    ) -> Optional[svgwrite.container.Group]:
        """
        Create an SVG group containing an accurate moon phase visualization.

        Args:
            moon_planet: Moon planet object with phase data

        Returns:
            SVG group containing moon phase visualization, or None if no phase data
        """
        # Check if Moon has phase data
        if not hasattr(moon_planet, "phase_frac") or moon_planet.phase_frac is None:
            return None

        # Default moon phase styling
        moon_style = {
            "moon_phase_size": 16,
            "moon_phase_border_color": "#2C3E50",
            "moon_phase_border_width": 1,
            "moon_phase_lit_color": "#F8F9FA",
            "moon_phase_shadow_color": "#2C3E50",
            "moon_phase_opacity": 0.9,
        }

        # Get styling parameters
        radius = moon_style["moon_phase_size"]
        border_color = moon_style["moon_phase_border_color"]
        border_width = moon_style["moon_phase_border_width"]
        lit_color = moon_style["moon_phase_lit_color"]
        shadow_color = moon_style["moon_phase_shadow_color"]
        opacity = moon_style["moon_phase_opacity"]

        # Get phase data
        illuminated_fraction = moon_planet.phase_frac  # 0 (new) to 1 (full)
        phase_angle = getattr(moon_planet, "phase_angle", 0)  # 0-360 degrees

        # Determine if waxing or waning based on phase angle
        waxing = self._is_moon_waxing(phase_angle)

        # Create the moon phase visualization
        moon_group = self._draw_moon_phase_accurate(
            radius,
            illuminated_fraction,
            waxing,
            lit_color,
            shadow_color,
            border_color,
            border_width,
            opacity,
        )

        return moon_group

    def _is_moon_waxing(self, phase_angle: float) -> bool:
        """
        Determine if the moon is waxing based on phase angle.

        Args:
            phase_angle: Phase angle in degrees

        Returns:
            True if waxing, False if waning
        """
        # Normalize angle to 0-360 range
        normalized_angle = phase_angle % 360

        # Convention: 0-180 = waxing, 180-360 = waning
        return normalized_angle <= 180

    def _draw_moon_phase_accurate(
        self,
        radius: float,
        illuminated_fraction: float,
        waxing: bool,
        lit_color: str,
        shadow_color: str,
        border_color: str,
        border_width: float,
        opacity: float,
    ) -> svgwrite.container.Group:
        """
        Draw accurate moon phase using path-based approach.

        This creates the correct curved terminator line that accurately represents
        how the moon appears from Earth.

        Args:
            radius: Radius of the moon circle
            illuminated_fraction: Fraction of moon that is lit (0-1)
            waxing: True if waxing, False if waning
            lit_color: Color for illuminated portion
            shadow_color: Color for shadowed portion
            border_color: Color for border
            border_width: Width of border
            opacity: Overall opacity

        Returns:
            SVG group containing the moon phase
        """
        # Create SVG drawing instance for group creation
        temp_dwg = svgwrite.Drawing()
        group = temp_dwg.g()

        # Handle special cases
        if illuminated_fraction <= 0.01:
            # New moon - completely dark
            group.add(
                temp_dwg.circle(
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
                temp_dwg.circle(
                    center=(0, 0),
                    r=radius,
                    fill=lit_color,
                    stroke=border_color,
                    stroke_width=border_width,
                    opacity=opacity,
                )
            )
            return group

        # For partial phases, we need to create the correct curved terminator
        # The terminator is an ellipse that appears as we see the moon from an angle

        # Start with base circle (shadow)
        group.add(
            temp_dwg.circle(
                center=(0, 0),
                r=radius,
                fill=shadow_color,
                stroke="none",
                opacity=opacity,
            )
        )

        # Calculate the terminator ellipse parameters
        # The key insight: the terminator appears as an ellipse with width that varies
        # based on the phase. At quarter moon (0.5), it's a straight line (width=0)

        if abs(illuminated_fraction - 0.5) < 0.001:
            # Quarter moon - exactly half lit
            if waxing:
                # First quarter - right half lit
                path_d = f"M 0 {-radius} A {radius} {radius} 0 0 1 0 {radius} Z"
            else:
                # Last quarter - left half lit
                path_d = f"M 0 {-radius} A {radius} {radius} 0 0 0 0 {radius} Z"

            lit_path = temp_dwg.path(
                d=path_d, fill=lit_color, stroke="none", opacity=opacity
            )
            group.add(lit_path)
        else:
            # For other phases, create the curved terminator
            # The terminator ellipse width is based on how far we are from quarter phase
            terminator_width = abs(2 * (illuminated_fraction - 0.5)) * radius

            if illuminated_fraction < 0.5:
                # Crescent phase - less than half lit
                if waxing:
                    # Waxing crescent - lit on right
                    # Create path for the lit crescent
                    # Arc along right edge, then curve back along terminator
                    path_d = self._create_crescent_path(radius, terminator_width, True)
                else:
                    # Waning crescent - lit on left
                    path_d = self._create_crescent_path(radius, terminator_width, False)

                lit_path = temp_dwg.path(
                    d=path_d, fill=lit_color, stroke="none", opacity=opacity
                )
                group.add(lit_path)
            else:
                # Gibbous phase - more than half lit
                # Fill with lit color first
                group.add(
                    temp_dwg.circle(
                        center=(0, 0),
                        r=radius,
                        fill=lit_color,
                        stroke="none",
                        opacity=opacity,
                    )
                )

                # Add shadow crescent
                if waxing:
                    # Waxing gibbous - shadow on left
                    path_d = self._create_crescent_path(radius, terminator_width, False)
                else:
                    # Waning gibbous - shadow on right
                    path_d = self._create_crescent_path(radius, terminator_width, True)

                shadow_path = temp_dwg.path(
                    d=path_d, fill=shadow_color, stroke="none", opacity=opacity
                )
                group.add(shadow_path)

        # Add border
        group.add(
            temp_dwg.circle(
                center=(0, 0),
                r=radius,
                fill="none",
                stroke=border_color,
                stroke_width=border_width,
                opacity=opacity,
            )
        )

        return group

    def _create_crescent_path(
        self, radius: float, terminator_width: float, on_right: bool
    ) -> str:
        """
        Create a path for a crescent shape using accurate elliptical terminator.

        Args:
            radius: Moon radius
            terminator_width: Width of the terminator ellipse
            on_right: True if crescent is on right side, False if on left

        Returns:
            SVG path string
        """
        # The crescent is formed by the intersection of the moon circle
        # and an ellipse representing the terminator

        # For the elliptical terminator, we need to use the correct curve
        # The terminator is an ellipse with semi-major axis = radius
        # and semi-minor axis = terminator_width

        if on_right:
            # Crescent on right side
            # Start at top, arc along right edge, curve back along terminator to bottom
            path = f"M 0 {-radius} "  # Start at top center
            path += f"A {radius} {radius} 0 0 1 0 {radius} "  # Arc to bottom along right edge
            path += f"A {terminator_width} {radius} 0 0 0 0 {-radius} "  # Elliptical arc back to top
            path += "Z"  # Close path
        else:
            # Crescent on left side
            # Start at top, arc along left edge, curve back along terminator to bottom
            path = f"M 0 {-radius} "  # Start at top center
            path += f"A {radius} {radius} 0 0 0 0 {radius} "  # Arc to bottom along left edge
            path += f"A {terminator_width} {radius} 0 0 1 0 {-radius} "  # Elliptical arc back to top
            path += "Z"  # Close path

        return path


def create_moon_phase_test_grid():
    """Create a test grid showing various moon phases"""

    # Create output directory
    output_dir = "moon_phase_tests"
    os.makedirs(output_dir, exist_ok=True)

    # Initialize renderer
    renderer = MoonPhaseRenderer()

    # Define test cases with phase names
    test_cases = [
        # Waxing phases (0-180 degrees)
        ("new_moon", 0.0, 0),
        ("waxing_crescent_early", 0.1, 36),
        ("waxing_crescent", 0.25, 90),
        ("waxing_crescent_late", 0.4, 144),
        ("first_quarter", 0.5, 90),
        ("waxing_gibbous_early", 0.6, 108),
        ("waxing_gibbous", 0.75, 135),
        ("waxing_gibbous_late", 0.9, 162),
        ("full_moon", 1.0, 180),
        # Waning phases (180-360 degrees)
        ("waning_gibbous_early", 0.9, 198),
        ("waning_gibbous", 0.75, 225),
        ("waning_gibbous_late", 0.6, 252),
        ("last_quarter", 0.5, 270),
        ("waning_crescent_early", 0.4, 288),
        ("waning_crescent", 0.25, 315),
        ("waning_crescent_late", 0.1, 324),
    ]

    # Create individual SVG files for each phase
    for name, phase_frac, phase_angle in test_cases:
        # Create mock moon object
        moon = MockMoonPlanet(phase_frac=phase_frac, phase_angle=phase_angle)

        # Create SVG drawing
        dwg = svgwrite.Drawing(
            filename=os.path.join(output_dir, f"{name}.svg"),
            size=("100px", "100px"),
            viewBox="-50 -50 100 100",
        )

        # Add background
        dwg.add(dwg.rect(insert=(-50, -50), size=(100, 100), fill="#1a1a1a"))

        # Create moon phase
        moon_group = renderer._create_moon_phase_symbol(moon)
        if moon_group:
            # Scale up for better visibility
            main_group = dwg.g(transform="scale(2.5)")
            for element in moon_group.elements:
                main_group.add(element)
            dwg.add(main_group)

        # Add label
        dwg.add(
            dwg.text(
                name.replace("_", " ").title(),
                insert=(0, 40),
                text_anchor="middle",
                fill="white",
                font_size="8px",
                font_family="Arial",
            )
        )

        # Add phase info
        dwg.add(
            dwg.text(
                f"{phase_frac:.1%} / {phase_angle}°",
                insert=(0, 48),
                text_anchor="middle",
                fill="#888",
                font_size="6px",
                font_family="Arial",
            )
        )

        dwg.save()

    # Create a composite grid view
    grid_dwg = svgwrite.Drawing(
        filename=os.path.join(output_dir, "moon_phases_grid.svg"),
        size=("800px", "600px"),
    )

    # Add title
    grid_dwg.add(
        grid_dwg.text(
            "Moon Phase Test Grid",
            insert=(400, 30),
            text_anchor="middle",
            fill="black",
            font_size="24px",
            font_weight="bold",
            font_family="Arial",
        )
    )

    # Arrange phases in grid
    cols = 4
    cell_size = 150
    start_x = 100
    start_y = 80

    for i, (name, phase_frac, phase_angle) in enumerate(test_cases):
        row = i // cols
        col = i % cols
        x = start_x + col * cell_size
        y = start_y + row * cell_size

        # Create group for this phase
        phase_group = grid_dwg.g(transform=f"translate({x}, {y})")

        # Add background
        phase_group.add(
            grid_dwg.rect(
                insert=(-40, -40),
                size=(80, 80),
                fill="#f0f0f0",
                stroke="#ccc",
                stroke_width=1,
            )
        )

        # Create moon
        moon = MockMoonPlanet(phase_frac=phase_frac, phase_angle=phase_angle)
        moon_group = renderer._create_moon_phase_symbol(moon)

        if moon_group:
            scaled_group = grid_dwg.g(transform="scale(2)")
            for element in moon_group.elements:
                scaled_group.add(element)
            phase_group.add(scaled_group)

        # Add label
        phase_group.add(
            grid_dwg.text(
                name.replace("_", " ").title(),
                insert=(0, 50),
                text_anchor="middle",
                fill="black",
                font_size="10px",
                font_family="Arial",
            )
        )

        # Add phase info
        phase_group.add(
            grid_dwg.text(
                f"{phase_frac:.0%}",
                insert=(0, 62),
                text_anchor="middle",
                fill="#666",
                font_size="8px",
                font_family="Arial",
            )
        )

        grid_dwg.add(phase_group)

    grid_dwg.save()

    print(f"Moon phase test files created in '{output_dir}' directory:")
    print(f"- Individual phase files: {len(test_cases)} SVG files")
    print(f"- Grid view: moon_phases_grid.svg")

    # Create an HTML viewer
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Moon Phase SVG Tests</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .phase-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .phase-card img {
            width: 100%;
            height: auto;
        }
        .phase-name {
            font-weight: bold;
            margin-top: 10px;
        }
        .phase-info {
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>Moon Phase SVG Test Results</h1>
    <p>This page displays the generated moon phase SVGs. Each phase shows the illuminated fraction and phase angle.</p>

    <h2>Complete Grid View</h2>
    <img src="moon_phases_grid.svg" style="max-width: 100%; height: auto; border: 1px solid #ddd;">

    <h2>Individual Phases</h2>
    <div class="grid">
"""

    for name, phase_frac, phase_angle in test_cases:
        waxing_text = "Waxing" if phase_angle <= 180 else "Waning"
        html_content += f"""
        <div class="phase-card">
            <img src="{name}.svg" alt="{name}">
            <div class="phase-name">{name.replace("_", " ").title()}</div>
            <div class="phase-info">{phase_frac:.1%} illuminated</div>
            <div class="phase-info">{phase_angle}° ({waxing_text})</div>
        </div>
"""

    html_content += """
    </div>
</body>
</html>
"""

    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(html_content)

    print(f"- HTML viewer: index.html")
    print(f"\nOpen '{output_dir}/index.html' in a web browser to view all phases.")


if __name__ == "__main__":
    create_moon_phase_test_grid()
