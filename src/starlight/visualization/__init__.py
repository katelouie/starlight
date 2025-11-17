"""Visualization system for Starlight charts."""

from .core import ChartRenderer
from .drawing import draw_chart
from .layers import (
    AngleLayer,
    AspectLayer,
    HouseCuspLayer,
    PlanetLayer,
    ZodiacLayer,
)
from .moon_phase import MoonPhaseLayer
from .palettes import (
    AspectPalette,
    PlanetGlyphPalette,
    ZodiacPalette,
    get_aspect_palette_colors,
    get_aspect_palette_description,
    get_palette_colors,
    get_palette_description,
    get_planet_glyph_color,
    get_planet_glyph_palette_description,
)
from .themes import (
    ChartTheme,
    get_theme_default_aspect_palette,
    get_theme_default_palette,
    get_theme_default_planet_palette,
    get_theme_description,
    get_theme_style,
)
from .reference_sheet import (
    generate_html_reference,
    generate_zodiac_palette_reference,
    generate_aspect_palette_reference,
    generate_theme_reference,
)
from .grid import (
    draw_chart_grid,
    draw_theme_comparison,
    draw_palette_comparison,
)

__all__ = [
    # Core rendering
    "ChartRenderer",
    "draw_chart",
    # Layers
    "ZodiacLayer",
    "HouseCuspLayer",
    "AngleLayer",
    "PlanetLayer",
    "AspectLayer",
    "MoonPhaseLayer",
    # Palettes
    "ZodiacPalette",
    "AspectPalette",
    "PlanetGlyphPalette",
    "get_palette_colors",
    "get_palette_description",
    "get_aspect_palette_colors",
    "get_aspect_palette_description",
    "get_planet_glyph_color",
    "get_planet_glyph_palette_description",
    # Themes
    "ChartTheme",
    "get_theme_style",
    "get_theme_default_palette",
    "get_theme_default_aspect_palette",
    "get_theme_default_planet_palette",
    "get_theme_description",
    # Reference sheets
    "generate_html_reference",
    "generate_zodiac_palette_reference",
    "generate_aspect_palette_reference",
    "generate_theme_reference",
    # Grid layouts
    "draw_chart_grid",
    "draw_theme_comparison",
    "draw_palette_comparison",
]
