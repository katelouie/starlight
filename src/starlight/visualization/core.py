"""
Core Chart Drawing Engine (starlight.visualization.core)

This module provides the core, refactored drawing system.
It is based on a "Layer" strategy pattern.

- ChartRenderer: The main "canvas" and coordinate system.
- IRenderLayer: The protocol (interface) that all drawable layers must follow.
"""

import math
from typing import Any, Protocol

import svgwrite

from starlight.core.models import CalculatedChart
from starlight.core.registry import get_object_info

# Legacy glyph dictionaries - kept for backwards compatibility
# Prefer using the registry via get_glyph() helper function
PLANET_GLYPHS = {
    # === Traditional Planets (The Septenary) ===
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    # === Modern Planets ===
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    # === Chart Points & Nodes ===
    "Earth": "♁",
    "True Node": "☊",  # Also called the North Node
    "South Node": "☋",
    "Black Moon Lilith": "⚸",
    "Part of Fortune": "⊗",  # A common glyph, U+2297
    # === Asteroids (The "Big Four") ===
    "Ceres": "⚳",
    "Pallas": "⚴",
    "Juno": "⚵",
    "Vesta": "⚶",
    # === Centaurs ===
    "Chiron": "⚷",
    "Pholus": "⬰",  # (U+2B30) This is the correct glyph
    # === Uranian / Witte School Planets ===
    # These are very niche, but have standard glyphs
    "Cupido": "Cup",  # (U+2BD3)
    "Hades": "Had",  # (U+2BD4)
    "Zeus": "Zeu",  # (U+2BD5)
    "Kronos": "Kro",  # (U+2BD6)
    "Apollon": "Apo",  # (U+2BD7)
    "Admetos": "Adm",  # (U+2BD8)
    "Vulcanus": "Vul",  # (U+2BD9)
    "Poseidon": "Pos",  # (U+2BDA)
}

ZODIAC_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

ANGLE_GLYPHS = {
    "ASC": "Asc",
    "MC": "MC",
    "DSC": "Dsc",
    "IC": "IC",
    "Vertex": "Vx",
}

ASPECT_GLYPHS = {
    # === Major Aspects (Ptolemaic) ===
    "Conjunction": "☌",  # 0°
    "Sextile": "⚹",  # 60°
    "Square": "□",  # 90°
    "Trine": "△",  # 120°
    "Opposition": "☍",  # 180°
    # === Minor Aspects ===
    "Quincunx": "⚻",  # 150° (Also known as Inconjunct)
    "Semi-Sextile": "⚺",  # 30°
    "Semi-Square": "∠",  # 45°
    "Sesquiquadrate": "⚼",  # 135° (Also known as Sesquisquare)
}


def get_glyph(object_name: str) -> str:
    """
    Get the glyph for a celestial object, with registry lookup and fallback.

    Args:
        object_name: Name of the object (e.g., "Sun", "Mean Apogee", "ASC")

    Returns:
        Unicode glyph string, or abbreviated name if not found
    """
    # Try registry first
    obj_info = get_object_info(object_name)
    if obj_info:
        return obj_info.glyph

    # Fall back to legacy dictionaries
    if object_name in PLANET_GLYPHS:
        return PLANET_GLYPHS[object_name]
    if object_name in ANGLE_GLYPHS:
        return ANGLE_GLYPHS[object_name]

    # Final fallback: use first 2-3 characters
    return object_name[:3]


def get_display_name(object_name: str) -> str:
    """
    Get the display name for a celestial object.

    Args:
        object_name: Technical name (e.g., "Mean Apogee")

    Returns:
        Display name (e.g., "Black Moon Lilith") or original name if not in registry
    """
    obj_info = get_object_info(object_name)
    if obj_info:
        return obj_info.display_name
    return object_name


class ChartRenderer:
    """
    The core chart drawing canvas and coordinate system.

    This class holds the SVG drawing object and provides the geometric
    utilities for layers to draw themselves. It acts as the "Context"
    in the strategy pattern.
    """

    def __init__(
        self,
        size: int = 600,
        rotation: float = 0.0,
        style_config: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the chart renderer.

        Args:
            size: The canvas size in pixels.
            rotation: The astrological longitude (in degrees) to fix
                      at the 9 o'clock position. Defaults to 0 (Aries).
            style_config: Optional style overrides.
        """
        self.size = size
        self.center = size // 2
        self.rotation = rotation

        # Define the radial structure of the chart
        # These are proportional to canvas size for scalability
        self.radii = {
            "outer_border": size * 0.48,
            "zodiac_ring_outer": size * 0.47,
            "zodiac_glyph": size * 0.42,
            "zodiac_ring_inner": size * 0.37,
            "planet_ring": size * 0.30,
            "house_number_ring": size * 0.22,
            "aspect_ring_inner": size * 0.18,
            "synastry_planet_ring_inner": size * 0.13,
        }

        self.style = self._get_default_style()
        if style_config:
            # Deep merge dictionaries
            for key, value in style_config.items():
                if isinstance(value, dict):
                    self.style[key].update(value)
                else:
                    self.style[key] = value

    def _get_default_style(self) -> dict[str, Any]:
        """Provides the base styling configuration."""
        return {
            "background_color": "#FFFFFF",
            "border_color": "#999999",
            "border_width": 1,
            "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
            "font_family_text": '"Arial", "Helvetica", sans-serif',
            "zodiac": {
                "ring_color": "#EEEEEE",
                "line_color": "#BBBBBB",
                "glyph_color": "#555555",
                "glyph_size": "20px",
            },
            "houses": {
                "line_color": "#CCCCCC",
                "line_width": 0.8,
                "number_color": "#AAAAAA",
                "number_size": "11px",
                "fill_alternate": True,
                "fill_color_1": "#F5F5F5",
                "fill_color_2": "#FFFFFF",
            },
            "angles": {
                "line_color": "#555555",
                "line_width": 2.5,
                "glyph_color": "#333333",
                "glyph_size": "12px",
            },
            "planets": {
                "glyph_color": "#222222",
                "glyph_size": "32px",
                "info_color": "#444444",
                "info_size": "10px",
                "retro_color": "#E74C3C",
            },
            "aspects": {
                "Conjunct": {"color": "#34495E", "width": 2.0, "dash": "1,0"},
                "Opposition": {"color": "#E74C3C", "width": 2.0, "dash": "1,0"},
                "Square": {"color": "#F39C12", "width": 1.5, "dash": "4,2"},
                "Trine": {"color": "#3498DB", "width": 2.0, "dash": "1,0"},
                "Sextile": {"color": "#27AE60", "width": 1.5, "dash": "6,2"},
                "Quincunx": {"color": "#9B59B6", "width": 1.0, "dash": "2,2"},
                "default": {"color": "#BDC3C7", "width": 0.5, "dash": "2,2"},
                "line_color": "#BBBBBB",
                "background_color": "#FFFFFF",
            },
        }

    def astrological_to_svg_angle(self, astro_deg: float) -> float:
        """
        Converts astrological degrees (0° = Aries) to SVG degrees
        (0° = 3 o'clock), appling the chart's rotation.

        Our system: 0° Aries is at 9 o'clock (180° SVG).
        Rotation is COUNTER-CLOCKWISE.
        """
        # Get the degree relative to the rotation point
        # if Sun is 15 Leo (135) and Asc (rotation) is 15 Cancer (105)
        # then relative degree is 30
        relative_deg = (astro_deg - self.rotation + 360) % 360

        # Apply the standard formula to the relative degree
        # (180 - relative degree) places 0 deg at 9 o clock (180)
        # and makes the chart rotate counter-clockwise
        svg_angle = (180 + relative_deg - 360) % 360

        return svg_angle

    def polar_to_cartesian(
        self, astro_deg: float, radius: float
    ) -> tuple[float, float]:
        """
        Converts an astrological degree (0 degrees Aries) and radius to an (x,y) coordinate.
        """
        svg_angle_rad = math.radians(self.astrological_to_svg_angle(astro_deg))

        # SVG Y is inverted (positive is down)
        x = self.center + radius * math.cos(svg_angle_rad)
        y = self.center - radius * math.sin(svg_angle_rad)

        return x, y

    def create_svg_drawing(self, filename: str) -> svgwrite.Drawing:
        """Creates the main SVG object and draws the background."""
        dwg = svgwrite.Drawing(
            filename=filename,
            size=(f"{self.size}px", f"{self.size}px"),
            viewBox=f"0 0 {self.size} {self.size}",
            profile="full",
        )

        # Add square background instead of circle
        dwg.add(
            dwg.rect(
                insert=(0, 0),
                size=(f"{self.size}px", f"{self.size}px"),
                fill=self.style["background_color"],
            )
        )

        # Add outer circle border
        dwg.add(
            dwg.circle(
                center=(self.center, self.center),
                r=self.radii["outer_border"],
                fill="none",
                stroke=self.style["border_color"],
                stroke_width=self.style["border_width"],
            )
        )

        # Add border circle at aspect ring inner radius
        dwg.add(
            dwg.circle(
                center=(self.center, self.center),
                r=self.radii["aspect_ring_inner"],
                fill="none",
                stroke=self.style["border_color"],
                stroke_width=self.style["border_width"],
            )
        )

        return dwg


class IRenderLayer(Protocol):
    """
    Protocol (interface) for all drawable chart layers.

    Each layer is a self-contained drawing strategy.
    """

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        """
        The main drawing method for the layer.

        Args:
            renderer: ChartRenderer instance, used to access coordinate methods
            (.polar_to_cartesian) and style/radius definitions.
            dwg: The svgwrite.Drawing object to add elements to.
            chart: The full CalculatedChart data object.
        """
        ...
