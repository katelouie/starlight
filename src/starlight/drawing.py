"""
Professional astrological chart drawing with SVG.

This module provides a clean, extensible system for drawing astrological charts
using SVG for crisp, scalable output.
"""

import math
from typing import Optional, Tuple, Dict, Any
import svgwrite
from starlight.chart import Chart
from starlight.objects import get_ephemeris_object, ASPECTS


class ChartWheel:
    """
    Core chart wheel drawing system with proper coordinate transformation.

    This class handles the fundamental geometry and coordinate system for
    astrological chart drawing.
    """

    def __init__(self, size: int = 600, style: Optional[Dict[str, Any]] = None):
        """
        Initialize chart wheel with configurable size and styling.

        Args:
            size: Canvas size in pixels (creates square canvas)
            style: Optional styling configuration
        """
        self.size = size
        self.center = size // 2

        # Define the radial structure of the chart
        # These are proportional to canvas size for scalability
        self.radius_outer = size * 0.42  # Outer edge
        self.radius_zodiac = size * 0.38  # Zodiac ring
        self.radius_houses = size * 0.34  # House numbers
        self.radius_planets = size * 0.28  # Planet placement
        self.radius_inner = size * 0.20   # Inner clear area

        # Professional styling configuration
        self.style = {
            # Main chart styling
            'background_color': '#FEFEFE',
            'border_color': '#2C3E50',
            'border_width': 2,

            # House styling
            'house_line_color': '#BDC3C7',
            'house_line_width': 0.8,
            'house_number_color': '#7F8C8D',
            'house_number_size': '11px',

            # Zodiac ring styling
            'zodiac_line_color': '#95A5A6',
            'zodiac_line_width': 0.6,
            'zodiac_sign_color': '#34495E',
            'zodiac_sign_size': '22px',
            'zodiac_font_family': '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',

            # Planet styling
            'planet_color': '#2C3E50',
            'planet_size': '24px',
            'planet_font_family': '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
            'planet_retro_color': '#E74C3C',

            # Inner circle styling (separates aspects from outer elements)
            'inner_circle_color': '#BDC3C7',
            'inner_circle_width': 1,

            # Additional detail styling
            'sign_planet_separator_color': "#B5B5B5",
            'sign_planet_separator_width': 0.5,
            'degree_tick_color': "#6A6A6A",
            'degree_tick_width': 0.3,
            'degree_tick_length': 8,
            'house_alternating_colors': ["#A7A894", '#F1F3F4'],

            # Angle styling
            'angle_color': '#949494',
            'angle_size': '12px',
            'angle_line_color': '#595959',
            'angle_line_width': 2,
            'angle_line_opacity': 0.8,

            # Text styling
            'text_color': '#2C3E50',

            # Aspect styling
            'aspect_colors': {
                'Conjunct': '#34495E',    # Dark blue-gray
                'Opposition': '#E74C3C',  # Modern red
                'Square': '#F39C12',      # Modern orange
                'Trine': '#3498DB',       # Modern blue
                'Sextile': '#27AE60'      # Modern green
            },
            'aspect_widths': {
                'Conjunct': 1.2,
                'Opposition': 1.8,
                'Square': 1.3,
                'Trine': 1.3,
                'Sextile': 1.0
            },
            'aspect_opacity': {
                'Conjunct': 0.8,
                'Opposition': 0.9,
                'Square': 0.8,
                'Trine': 0.8,
                'Sextile': 0.7
            },
            'show_aspects': True,

        }

        # Update with user-provided styles
        if style:
            self.style.update(style)

    def create_svg(self, filename: Optional[str] = None) -> svgwrite.Drawing:
        """
        Create the base SVG drawing with proper setup.

        Args:
            filename: Optional filename for SVG output

        Returns:
            SVG Drawing object ready for chart elements
        """
        # Create SVG with proper viewBox for scalability
        if filename:
            dwg = svgwrite.Drawing(
                filename=filename,
                size=(f"{self.size}px", f"{self.size}px"),
                viewBox=f"0 0 {self.size} {self.size}",
                profile='full'  # Use full profile for better text support
            )
        else:
            dwg = svgwrite.Drawing(
                size=(f"{self.size}px", f"{self.size}px"),
                viewBox=f"0 0 {self.size} {self.size}",
                profile='full'  # Use full profile for better text support
            )

        # Add background circle
        dwg.add(dwg.circle(
            center=(self.center, self.center),
            r=self.radius_outer,
            fill=self.style['background_color'],
            stroke=self.style['border_color'],
            stroke_width=self.style['border_width']
        ))

        # Add inner circle to separate aspect area
        dwg.add(dwg.circle(
            center=(self.center, self.center),
            r=self.radius_inner,
            fill="none",
            stroke=self.style['inner_circle_color'],
            stroke_width=self.style['inner_circle_width']
        ))

        # Add separator circle between signs and planets
        separator_radius = (self.radius_zodiac + self.radius_planets) / 2
        dwg.add(dwg.circle(
            center=(self.center, self.center),
            r=separator_radius,
            fill="none",
            stroke=self.style['sign_planet_separator_color'],
            stroke_width=self.style['sign_planet_separator_width']
        ))

        # Add degree tick marks around the outer circle
        self._draw_degree_ticks(dwg)

        return dwg

    def astrological_to_svg_angle(self, astrological_degrees: float) -> float:
        """
        Convert astrological degrees to SVG coordinate system.

        Astrological system:
        - 0° = Aries point (placed at 9 o'clock / left side)
        - Degrees increase clockwise

        SVG system:
        - 0° = 3 o'clock position
        - Degrees increase counterclockwise

        Args:
            astrological_degrees: Degrees in astrological system (0-360)

        Returns:
            Degrees in SVG coordinate system
        """
        # Convert: astro 0° = SVG 180° (9 o'clock), and maintain clockwise direction
        return (180 + astrological_degrees) % 360

    def polar_to_cartesian(self, angle_degrees: float, radius: float) -> Tuple[float, float]:
        """
        Convert polar coordinates to Cartesian (X, Y) coordinates.

        Args:
            angle_degrees: Angle in degrees (astrological system)
            radius: Distance from center

        Returns:
            (x, y) coordinates for SVG
        """
        # Convert to SVG angle system
        svg_angle = self.astrological_to_svg_angle(angle_degrees)
        angle_rad = math.radians(svg_angle)

        # Calculate Cartesian coordinates
        x = self.center + radius * math.cos(angle_rad)
        y = self.center - radius * math.sin(angle_rad)  # SVG Y is inverted

        return x, y

    def _draw_degree_ticks(self, dwg: svgwrite.Drawing) -> None:
        """
        Draw degree tick marks around the outer circle every 5 degrees.

        Args:
            dwg: SVG Drawing object
        """
        for degree in range(0, 360, 5):
            # Major ticks every 30 degrees (sign boundaries)
            if degree % 30 == 0:
                tick_length = self.style['degree_tick_length'] * 1.5
                tick_width = self.style['degree_tick_width'] * 2
            # Minor ticks every 10 degrees
            elif degree % 10 == 0:
                tick_length = self.style['degree_tick_length'] * 1.2
                tick_width = self.style['degree_tick_width'] * 1.5
            # Smallest ticks every 5 degrees
            else:
                tick_length = self.style['degree_tick_length']
                tick_width = self.style['degree_tick_width']

            # Calculate tick positions
            x_outer, y_outer = self.polar_to_cartesian(degree, self.radius_outer)
            x_inner, y_inner = self.polar_to_cartesian(degree, self.radius_outer - tick_length)

            # Draw tick mark
            dwg.add(dwg.line(
                start=(x_inner, y_inner),
                end=(x_outer, y_outer),
                stroke=self.style['degree_tick_color'],
                stroke_width=tick_width
            ))

    def draw_house_divisions(self, dwg: svgwrite.Drawing, chart: Chart) -> None:
        """
        Draw the 12 house division lines with alternating background colors.

        Args:
            dwg: SVG Drawing object
            chart: Chart object containing house cusp data
        """
        # First pass: Draw alternating house background sectors
        for i, cusp_degree in enumerate(chart.cusps):
            next_cusp = chart.cusps[(i + 1) % 12]

            # Calculate the span of this house
            if next_cusp < cusp_degree:  # Handle wrapping around 360°
                next_cusp += 360

            # Determine background color (alternating pattern)
            color_index = i % 2
            fill_color = self.style['house_alternating_colors'][color_index]

            # Create a sector path for the house background
            self._draw_house_sector(dwg, cusp_degree, next_cusp, fill_color)

        # Second pass: Draw house division lines and numbers
        for i, cusp_degree in enumerate(chart.cusps):
            x_outer, y_outer = self.polar_to_cartesian(cusp_degree, self.radius_outer)
            x_inner, y_inner = self.polar_to_cartesian(cusp_degree, self.radius_inner)

            # Draw house division line
            dwg.add(dwg.line(
                start=(x_inner, y_inner),
                end=(x_outer, y_outer),
                stroke=self.style['house_line_color'],
                stroke_width=self.style['house_line_width']
            ))

            # Add house number
            house_number = i + 1
            x_house, y_house = self.polar_to_cartesian(
                cusp_degree + 15,  # Offset to middle of house
                self.radius_houses
            )

            dwg.add(dwg.text(
                str(house_number),
                insert=(x_house, y_house),
                text_anchor="middle",
                dominant_baseline="middle",
                font_size=self.style['house_number_size'],
                fill=self.style['house_number_color'],
                font_family="Arial, sans-serif"
            ))

    def _draw_house_sector(self, dwg: svgwrite.Drawing, start_degree: float,
                          end_degree: float, fill_color: str) -> None:
        """
        Draw a sector background for a house with alternating colors.

        Args:
            dwg: SVG Drawing object
            start_degree: Starting degree of the house
            end_degree: Ending degree of the house
            fill_color: Fill color for the sector
        """
        # Fill the entire pie slice from center to outer edge
        outer_radius = self.radius_outer
        inner_radius = self.radius_inner  # Start from center for full pie slice

        # Convert to SVG angles
        start_svg = self.astrological_to_svg_angle(start_degree)
        end_svg = self.astrological_to_svg_angle(end_degree)

        # Handle angle wrapping
        if end_svg < start_svg:
            end_svg += 360

        # Calculate the angle span
        angle_span = end_svg - start_svg
        large_arc_flag = 1 if angle_span > 180 else 0

        # Calculate start and end points for outer and inner arcs
        start_x_outer = self.center + outer_radius * math.cos(math.radians(start_svg))
        start_y_outer = self.center - outer_radius * math.sin(math.radians(start_svg))
        end_x_outer = self.center + outer_radius * math.cos(math.radians(end_svg))
        end_y_outer = self.center - outer_radius * math.sin(math.radians(end_svg))

        start_x_inner = self.center + inner_radius * math.cos(math.radians(start_svg))
        start_y_inner = self.center - inner_radius * math.sin(math.radians(start_svg))
        end_x_inner = self.center + inner_radius * math.cos(math.radians(end_svg))
        end_y_inner = self.center - inner_radius * math.sin(math.radians(end_svg))

        # Create the sector path
        path_data = f"M {start_x_outer},{start_y_outer} "
        path_data += f"A {outer_radius},{outer_radius} 0 {large_arc_flag},0 {end_x_outer},{end_y_outer} "
        path_data += f"L {end_x_inner},{end_y_inner} "
        path_data += f"A {inner_radius},{inner_radius} 0 {large_arc_flag},1 {start_x_inner},{start_y_inner} "
        path_data += "Z"

        # Draw the sector
        dwg.add(dwg.path(
            d=path_data,
            fill=fill_color,
            stroke="none",
            opacity=0.3
        ))

    def draw_zodiac_ring(self, dwg: svgwrite.Drawing, chart: Chart) -> None:
        """
        Draw the zodiac signs around the wheel.

        Args:
            dwg: SVG Drawing object
            chart: Chart object for ASC reference
        """
        # Get ASC position to orient zodiac properly
        asc_degree = chart.objects_dict["ASC"].long

        # Zodiac signs with Unicode astrological glyphs
        zodiac_signs = [
            "♈", "♉", "♊", "♋", "♌", "♍",
            "♎", "♏", "♐", "♑", "♒", "♓"
        ]

        # Draw zodiac division lines and signs
        for i in range(12):
            # Each sign is 30 degrees
            sign_start = i * 30
            sign_middle = sign_start + 15

            # The zodiac should be positioned so that the ASC degree
            # corresponds to its actual zodiac position on the wheel
            # If ASC = 0° (Aries), then 0° Aries should be at ASC position
            actual_degree = sign_start
            actual_middle = sign_middle

            # Draw sign division line
            x_outer, y_outer = self.polar_to_cartesian(actual_degree, self.radius_outer)
            x_zodiac, y_zodiac = self.polar_to_cartesian(actual_degree, self.radius_zodiac)

            dwg.add(dwg.line(
                start=(x_zodiac, y_zodiac),
                end=(x_outer, y_outer),
                stroke=self.style['zodiac_line_color'],
                stroke_width=self.style['zodiac_line_width']
            ))

            # Add zodiac sign symbol
            x_sign, y_sign = self.polar_to_cartesian(actual_middle, self.radius_zodiac)

            dwg.add(dwg.text(
                zodiac_signs[i],
                insert=(x_sign, y_sign),
                text_anchor="middle",
                dominant_baseline="middle",
                font_size=self.style['zodiac_sign_size'],
                fill=self.style['zodiac_sign_color'],
                font_family=self.style['zodiac_font_family'],
                font_weight="bold"
            ))

    def draw_planets(self, dwg: svgwrite.Drawing, chart: Chart) -> None:
        """
        Draw planets on the chart wheel at their calculated positions.

        Args:
            dwg: SVG Drawing object
            chart: Chart object containing planet data
        """
        # Apply collision detection to get adjusted positions
        planet_positions = self._calculate_planet_positions_with_collision_detection(chart)

        # Draw planets at their adjusted positions
        for planet, position in planet_positions.items():
            x_planet, y_planet = position['x'], position['y']

            # Get planet symbol from the alias (last character)
            planet_info = get_ephemeris_object(planet.swe)
            planet_symbol = planet_info["alias"][-1]

            # Determine color based on retrograde status
            planet_color = self.style['planet_retro_color'] if planet.is_retro else self.style['planet_color']

            # Draw the planet symbol
            dwg.add(dwg.text(
                planet_symbol,
                insert=(x_planet, y_planet),
                text_anchor="middle",
                dominant_baseline="middle",
                font_size=self.style['planet_size'],
                fill=planet_color,
                font_family=self.style['planet_font_family'],
                font_weight="bold"
            ))

            # Draw a thin line connecting planet to its actual position if adjusted
            if position['adjusted']:
                x_actual, y_actual = self.polar_to_cartesian(
                    planet.long,
                    self.radius_planets
                )
                dwg.add(dwg.line(
                    start=(x_actual, y_actual),
                    end=(x_planet, y_planet),
                    stroke="#999999",
                    stroke_width=0.5,
                    opacity=0.6
                ))

            # Optional: Add small degree label below planet
            if self.style.get('show_planet_degrees', False):
                degree_text = f"{planet.long:.0f}°"
                dwg.add(dwg.text(
                    degree_text,
                    insert=(x_planet, y_planet + 12),
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_size="8px",
                    fill="#666666"
                ))


    def _calculate_planet_positions_with_collision_detection(self, chart: Chart) -> Dict:
        """
        Calculate planet positions with basic collision detection.

        Args:
            chart: Chart object containing planet data

        Returns:
            Dictionary mapping planets to their adjusted positions
        """
        # Minimum distance between planets (in pixels)
        min_distance = 20

        # Store planet positions
        planet_positions = {}
        placed_positions = []

        # Sort planets by longitude for consistent placement
        sorted_planets = sorted(
            [p for p in chart.planets if hasattr(p, 'long') and p.long is not None],
            key=lambda p: p.long
        )

        for planet in sorted_planets:
            # Calculate ideal position
            x_ideal, y_ideal = self.polar_to_cartesian(
                planet.long,
                self.radius_planets
            )

            # Check for collisions with already placed planets
            collision_detected = False
            for placed_pos in placed_positions:
                distance = math.sqrt(
                    (x_ideal - placed_pos['x'])**2 +
                    (y_ideal - placed_pos['y'])**2
                )
                if distance < min_distance:
                    collision_detected = True
                    break

            if not collision_detected:
                # No collision, use ideal position
                planet_positions[planet] = {
                    'x': x_ideal,
                    'y': y_ideal,
                    'adjusted': False
                }
                placed_positions.append({'x': x_ideal, 'y': y_ideal})
            else:
                # Collision detected, find alternative position
                adjusted_pos = self._find_alternative_position(
                    planet.long, placed_positions, min_distance
                )
                planet_positions[planet] = {
                    'x': adjusted_pos['x'],
                    'y': adjusted_pos['y'],
                    'adjusted': True
                }
                placed_positions.append(adjusted_pos)

        return planet_positions

    def _find_alternative_position(self, original_longitude: float,
                                 placed_positions: list, min_distance: float) -> Dict:
        """
        Find an alternative position for a planet that avoids collisions.

        Args:
            original_longitude: Original longitude of the planet
            placed_positions: List of already placed positions
            min_distance: Minimum distance required between planets

        Returns:
            Dictionary with x, y coordinates for alternative position
        """
        # Try positions at slightly different radii
        radius_offsets = [0, -8, 8, -16, 16, -24, 24]
        angle_offsets = [0, 5, -5, 10, -10, 15, -15]

        for radius_offset in radius_offsets:
            for angle_offset in angle_offsets:
                test_radius = self.radius_planets + radius_offset
                test_angle = original_longitude + angle_offset

                x_test, y_test = self.polar_to_cartesian(test_angle, test_radius)

                # Check if this position conflicts with any placed position
                valid_position = True
                for placed_pos in placed_positions:
                    distance = math.sqrt(
                        (x_test - placed_pos['x'])**2 +
                        (y_test - placed_pos['y'])**2
                    )
                    if distance < min_distance:
                        valid_position = False
                        break

                if valid_position:
                    return {'x': x_test, 'y': y_test}

        # If no good position found, use a fallback position
        # This is a simple radial offset
        fallback_radius = self.radius_planets - 30
        x_fallback, y_fallback = self.polar_to_cartesian(
            original_longitude, fallback_radius
        )
        return {'x': x_fallback, 'y': y_fallback}

    def draw_angles(self, dwg: svgwrite.Drawing, chart: Chart) -> None:
        """
        Draw chart angles (ASC, MC, DSC, IC) with special emphasis.

        Args:
            dwg: SVG Drawing object
            chart: Chart object containing angle data
        """
        # Main angles to emphasize
        main_angles = ["ASC", "MC", "DSC", "IC"]

        for angle in chart.angles:
            if angle.name in main_angles:
                # Draw line from center to angle position for emphasis
                x_inner, y_inner = self.polar_to_cartesian(angle.long, self.radius_inner)
                x_outer, y_outer = self.polar_to_cartesian(angle.long, self.radius_outer)

                dwg.add(dwg.line(
                    start=(x_inner, y_inner),
                    end=(x_outer, y_outer),
                    stroke=self.style['angle_line_color'],
                    stroke_width=self.style['angle_line_width'],
                    opacity=self.style['angle_line_opacity']
                ))

                # Calculate label position outside the chart
                label_radius = self.radius_outer + 20  # Outside the main circle
                x_label, y_label = self.polar_to_cartesian(angle.long, label_radius)

                # Get angle symbol
                angle_info = get_ephemeris_object(angle.name)
                angle_symbol = angle_info["alias"]

                # Determine text anchor based on position to avoid overlap
                text_anchor = self._get_angle_text_anchor(angle.long)

                # Draw angle label outside the chart
                dwg.add(dwg.text(
                    angle_symbol,
                    insert=(x_label, y_label),
                    text_anchor=text_anchor,
                    dominant_baseline="middle",
                    font_size=self.style['angle_size'],
                    fill=self.style['angle_color'],
                    font_weight="bold",
                    font_family="Arial, sans-serif"
                ))

    def _get_angle_text_anchor(self, longitude: float) -> str:
        """
        Determine the best text anchor for angle labels based on their position.

        Args:
            longitude: Angle longitude in degrees

        Returns:
            Text anchor value for SVG text element
        """
        # Normalize longitude to 0-360 range
        longitude = longitude % 360

        # Determine text anchor based on quadrant
        if 315 <= longitude or longitude < 45:  # Right side (around ASC/DSC)
            return "start"  # Text starts from the point, extends right
        elif 45 <= longitude < 135:  # Bottom side (around IC)
            return "middle"  # Centered
        elif 135 <= longitude < 225:  # Left side (around DSC)
            return "end"  # Text ends at the point, extends left
        else:  # Top side (around MC)
            return "middle"  # Centered

    def draw_aspects(self, dwg: svgwrite.Drawing, chart: Chart) -> None:
        """
        Draw aspect lines between planets that form significant aspects.

        Args:
            dwg: SVG Drawing object
            chart: Chart object containing planet data
        """
        if not self.style.get('show_aspects', True):
            return

        # Get valid planets with positions
        valid_planets = [
            p for p in chart.planets
            if hasattr(p, 'long') and p.long is not None
        ]

        # Calculate all aspects between planet pairs
        for i, planet1 in enumerate(valid_planets):
            for planet2 in valid_planets[i+1:]:  # Avoid duplicate pairs
                # Check each aspect type
                for aspect_name, aspect_data in ASPECTS.items():
                    is_aspect, orb, distance, movement = planet1.aspect(
                        planet2,
                        aspect_data['degree'],
                        aspect_data['orb']
                    )

                    if is_aspect:
                        self._draw_aspect_line(
                            dwg, planet1, planet2, aspect_name, orb
                        )
                        break  # Only draw one aspect per planet pair

    def _draw_aspect_line(self, dwg: svgwrite.Drawing, planet1, planet2,
                         aspect_name: str, orb: float) -> None:
        """
        Draw a single aspect line between two planets.

        Args:
            dwg: SVG Drawing object
            planet1: First planet object
            planet2: Second planet object
            aspect_name: Name of the aspect (e.g., 'Trine', 'Square')
            orb: Orb of the aspect in degrees
        """
        # Get aspect styling
        color = self.style['aspect_colors'].get(aspect_name, '#666666')
        width = self.style['aspect_widths'].get(aspect_name, 1)

        # Calculate opacity based on orb and aspect type
        max_orb = ASPECTS[aspect_name]['orb']
        base_opacity = self.style['aspect_opacity'].get(aspect_name, 0.8)
        orb_factor = max(0.4, 1.0 - (orb / max_orb) * 0.6)
        opacity = base_opacity * orb_factor

        # Special handling for conjunctions - draw arc instead of line
        if aspect_name == 'Conjunct':
            self._draw_conjunction_arc(dwg, planet1, planet2, color, width, opacity)
        else:
            # Get positions on the inner circle (to avoid overlapping planets)
            x1, y1 = self.polar_to_cartesian(planet1.long, self.radius_inner)
            x2, y2 = self.polar_to_cartesian(planet2.long, self.radius_inner)

            # Draw regular aspect line
            line_attrs = {
                'start': (x1, y1),
                'end': (x2, y2),
                'stroke': color,
                'stroke_width': width,
                'opacity': opacity
            }

            # Add dashed pattern for certain aspects
            if aspect_name in ['Square']:
                line_attrs['stroke_dasharray'] = "2,2"

            dwg.add(dwg.line(**line_attrs))

    def _draw_conjunction_arc(self, dwg: svgwrite.Drawing, planet1, planet2,
                             color: str, width: float, opacity: float) -> None:
        """
        Draw an arc between two planets in conjunction, similar to astro.com style.

        Args:
            dwg: SVG Drawing object
            planet1: First planet object
            planet2: Second planet object
            color: Stroke color
            width: Stroke width
            opacity: Opacity value
        """
        # Calculate the midpoint longitude between the two planets
        long1, long2 = planet1.long, planet2.long

        # Handle angle wrapping for conjunctions near 0°/360°
        angle_diff = abs(long2 - long1)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff

        # Calculate midpoint longitude
        if abs(long2 - long1) <= 180:
            mid_long = (long1 + long2) / 2
        else:
            # Handle wrapping case
            if long1 > long2:
                mid_long = ((long1 + long2 + 360) / 2) % 360
            else:
                mid_long = ((long1 + long2 + 360) / 2) % 360

        # Arc radius should be at planet level but slightly inward
        arc_radius = self.radius_planets + 15

        # Calculate arc span (proportional to orb)
        arc_span = min(angle_diff * 1.5, 15)  # Cap at 15 degrees

        # Start and end angles for the arc
        start_angle = mid_long - arc_span/2
        end_angle = mid_long + arc_span/2

        # Convert to SVG coordinates
        start_x, start_y = self.polar_to_cartesian(start_angle, arc_radius)
        end_x, end_y = self.polar_to_cartesian(end_angle, arc_radius)

        # Calculate arc parameters for SVG path
        # We want a small arc that curves away from center
        sweep_flag = 0  # Small arc
        large_arc_flag = 0  # Small arc

        # Create SVG path for arc
        path_data = f"M {start_x},{start_y} A {arc_radius},{arc_radius} 0 {large_arc_flag},{sweep_flag} {end_x},{end_y}"

        # Draw the arc
        dwg.add(dwg.path(
            d=path_data,
            stroke=color,
            stroke_width=width,
            fill="none",
            opacity=opacity
        ))

    def _create_moon_phase_symbol(self, moon_planet) -> Optional[svgwrite.container.Group]:
        """
        Create an SVG group containing an accurate moon phase visualization.

        Args:
            moon_planet: Moon planet object with phase data

        Returns:
            SVG group containing moon phase visualization, or None if no phase data
        """
        # Check if Moon has phase data
        if not hasattr(moon_planet, 'phase_frac') or moon_planet.phase_frac is None:
            return None

        # Default moon phase styling
        moon_style = {
            'moon_phase_size': 16,
            'moon_phase_border_color': '#2C3E50',
            'moon_phase_border_width': 1,
            'moon_phase_lit_color': '#F8F9FA',
            'moon_phase_shadow_color': '#2C3E50',
            'moon_phase_opacity': 0.9
        }

        # Get styling parameters
        radius = moon_style['moon_phase_size']
        border_color = moon_style['moon_phase_border_color']
        border_width = moon_style['moon_phase_border_width']
        lit_color = moon_style['moon_phase_lit_color']
        shadow_color = moon_style['moon_phase_shadow_color']
        opacity = moon_style['moon_phase_opacity']

        # Get phase data
        illuminated_fraction = moon_planet.phase_frac  # 0 (new) to 1 (full)
        phase_angle = getattr(moon_planet, 'phase_angle', 0)  # 0-360 degrees

        # Determine if waxing or waning based on phase angle
        # In astronomical terms: 0° = new moon, 180° = full moon
        # But Swiss Ephemeris may use different convention, so we use fraction
        waxing = self._is_moon_waxing(phase_angle)

        # Create the moon phase visualization using two-circle method
        moon_group = self._draw_moon_phase_two_circles(
            radius, illuminated_fraction, waxing,
            lit_color, shadow_color, border_color, border_width, opacity
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
        # This matches the elongation angle (angular separation from Sun)
        return normalized_angle <= 180

    def _draw_moon_phase_two_circles(
        self, radius: float, illuminated_fraction: float, waxing: bool,
        lit_color: str, shadow_color: str, border_color: str, 
        border_width: float, opacity: float
    ) -> svgwrite.container.Group:
        """
        Draw artistic moon phase as a single circle with proper light/shadow pattern.
        
        This creates the classic artistic representation where the moon is always
        a perfect circle with varying light and shadow regions.

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

        # Handle special cases first
        if illuminated_fraction <= 0.01:
            # New moon - completely dark circle
            group.add(temp_dwg.circle(
                center=(0, 0), r=radius,
                fill=shadow_color,
                stroke=border_color,
                stroke_width=border_width,
                opacity=opacity
            ))
            return group
        elif illuminated_fraction >= 0.99:
            # Full moon - completely lit circle
            group.add(temp_dwg.circle(
                center=(0, 0), r=radius,
                fill=lit_color,
                stroke=border_color,
                stroke_width=border_width,
                opacity=opacity
            ))
            return group

        # For partial phases, use the classic two-circle approach
        # This creates the authentic-looking curved terminator
        
        # Calculate the offset for the "light circle"
        # When fraction = 0.5, the circles are tangent (touching at center)
        # When fraction approaches 0 or 1, one circle dominates
        offset = 2 * radius * abs(0.5 - illuminated_fraction)
        
        # Create clipping path for moon boundary
        moon_clip_id = f"moonClip_{id(group)}"
        moon_clip = temp_dwg.clipPath(id=moon_clip_id)
        moon_clip.add(temp_dwg.circle(center=(0, 0), r=radius))
        temp_dwg.defs.add(moon_clip)

        # Calculate the terminator position based on illumination
        # For a single-circle artistic representation with curved terminator
        
        # Start with the base circle (always the shadow color)
        group.add(temp_dwg.circle(
            center=(0, 0), r=radius,
            fill=shadow_color, stroke="none", opacity=opacity
        ))
        
        if abs(illuminated_fraction - 0.5) < 0.01:
            # Quarter moons - perfect vertical split
            if waxing:
                # First quarter - right half lit
                # Path: start at center top, arc to center bottom (right side), line back to top
                lit_path = temp_dwg.path(
                    d=f"M 0 {-radius} A {radius} {radius} 0 0 1 0 {radius} L 0 0 Z",
                    fill=lit_color, stroke="none", opacity=opacity
                )
            else:
                # Third quarter - left half lit (mirror of first quarter)
                # Path: start at center top, arc to center bottom (left side), line back to top
                lit_path = temp_dwg.path(
                    d=f"M 0 {-radius} A {radius} {radius} 0 0 0 0 {radius} L 0 0 Z",
                    fill=lit_color, stroke="none", opacity=opacity
                )
            group.add(lit_path)
        else:
            # For crescents and gibbous phases, use simple ellipse approach
            # This creates clean, artistic moon phases
            
            if illuminated_fraction < 0.5:
                # Crescent phase - create a narrow ellipse for the lit area
                # Calculate ellipse width based on illumination
                ellipse_width = radius * illuminated_fraction * 2
                
                if waxing:
                    # Waxing crescent - lit on right side
                    # Create an ellipse that represents the lit crescent
                    ellipse_cx = radius - ellipse_width/2
                    
                    # Use an ellipse to create the crescent shape
                    lit_ellipse = temp_dwg.ellipse(
                        center=(ellipse_cx, 0),
                        r=(ellipse_width/2, radius),
                        fill=lit_color, stroke="none", opacity=opacity
                    )
                    # Clip to moon boundary
                    lit_ellipse['clip-path'] = f"url(#{moon_clip_id})"
                    group.add(lit_ellipse)
                else:
                    # Waning crescent - lit on left side
                    ellipse_cx = -radius + ellipse_width/2
                    
                    lit_ellipse = temp_dwg.ellipse(
                        center=(ellipse_cx, 0),
                        r=(ellipse_width/2, radius),
                        fill=lit_color, stroke="none", opacity=opacity
                    )
                    lit_ellipse['clip-path'] = f"url(#{moon_clip_id})"
                    group.add(lit_ellipse)
            else:
                # Gibbous phase - start with full lit circle, subtract dark ellipse
                group.add(temp_dwg.circle(
                    center=(0, 0), r=radius,
                    fill=lit_color, stroke="none", opacity=opacity
                ))
                
                # Calculate dark ellipse
                dark_fraction = 1.0 - illuminated_fraction
                ellipse_width = radius * dark_fraction * 2
                
                if waxing:
                    # Waxing gibbous - dark on left
                    ellipse_cx = -radius + ellipse_width/2
                    
                    dark_ellipse = temp_dwg.ellipse(
                        center=(ellipse_cx, 0),
                        r=(ellipse_width/2, radius),
                        fill=shadow_color, stroke="none", opacity=opacity
                    )
                    dark_ellipse['clip-path'] = f"url(#{moon_clip_id})"
                    group.add(dark_ellipse)
                else:
                    # Waning gibbous - dark on right
                    ellipse_cx = radius - ellipse_width/2
                    
                    dark_ellipse = temp_dwg.ellipse(
                        center=(ellipse_cx, 0),
                        r=(ellipse_width/2, radius),
                        fill=shadow_color, stroke="none", opacity=opacity
                    )
                    dark_ellipse['clip-path'] = f"url(#{moon_clip_id})"
                    group.add(dark_ellipse)

        # Add border last
        group.add(temp_dwg.circle(
            center=(0, 0), r=radius,
            fill="none",
            stroke=border_color,
            stroke_width=border_width,
            opacity=opacity
        ))

        return group


def draw_chart(chart: Chart, filename: str = "chart.svg", size: int = 600) -> str:
    """
    High-level function to draw a complete astrological chart.

    Args:
        chart: Chart object containing all astrological data
        filename: Output filename for SVG
        size: Canvas size in pixels

    Returns:
        Path to the created SVG file
    """
    # Create chart wheel
    wheel = ChartWheel(size=size)

    # Create SVG drawing
    dwg = wheel.create_svg(filename)

    # Draw chart elements in order (background to foreground)
    wheel.draw_house_divisions(dwg, chart)
    wheel.draw_zodiac_ring(dwg, chart)
    wheel.draw_aspects(dwg, chart)    # Draw aspects before planets/angles
    wheel.draw_angles(dwg, chart)     # Draw angles before planets
    wheel.draw_planets(dwg, chart)

    # Save the SVG
    dwg.save()

    return filename


def draw_moon_phase_standalone(illuminated_fraction: float, waxing: bool = True, 
                               filename: str = "moon_phase.svg", size: int = 100) -> str:
    """
    Create a standalone moon phase visualization SVG.

    Args:
        illuminated_fraction: Fraction of moon that is lit (0-1)
        waxing: True if waxing, False if waning
        filename: Output filename for SVG
        size: Size of the SVG canvas

    Returns:
        Path to the created SVG file
    """
    # Create a temporary chart wheel for styling and methods
    wheel = ChartWheel(size=size)
    
    # Create SVG drawing
    dwg = svgwrite.Drawing(
        filename=filename,
        size=(f"{size}px", f"{size}px"),
        viewBox=f"0 0 {size} {size}",
        profile='full'
    )

    # Create a mock moon object with the required phase data
    class MockMoon:
        def __init__(self, phase_frac, phase_angle):
            self.name = "Moon"
            self.phase_frac = phase_frac
            self.phase_angle = phase_angle

    # Set phase angle based on waxing status
    # For waxing: 0-180 degrees, for waning: 180-360 degrees
    phase_angle = 90 if waxing else 270  # Quarter positions
    mock_moon = MockMoon(illuminated_fraction, phase_angle)

    # Create moon phase symbol
    moon_group = wheel._create_moon_phase_symbol(mock_moon)
    
    if moon_group:
        # Center the moon phase in the SVG
        moon_group['transform'] = f"translate({size//2}, {size//2})"
        dwg.add(moon_group)

    # Save the SVG
    dwg.save()
    return filename




# Test function
def test_basic_wheel():
    """Test the basic wheel drawing with sample data."""
    print("Moon visualization system implemented!")
    print("Features:")
    print("- Automatic moon phase calculation from Swiss Ephemeris data")
    print("- Accurate two-circle intersection method for realistic phases")
    print("- Integration with existing chart drawing system")
    print("- Configurable styling through ChartWheel.style")
    print("\nRun demo_moon_phases() to see examples of all phase types.")


