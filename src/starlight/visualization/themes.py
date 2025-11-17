"""
Chart Themes (starlight.visualization.themes)

Defines complete visual themes for chart rendering, including colors,
line styles, and default zodiac palettes.
"""

from enum import Enum
from typing import Any

from starlight.core.registry import ASPECT_REGISTRY

from .palettes import ZodiacPalette


class ChartTheme(str, Enum):
    """Available visual themes for chart rendering."""

    CLASSIC = "classic"
    DARK = "dark"
    MIDNIGHT = "midnight"
    NEON = "neon"
    SEPIA = "sepia"
    PASTEL = "pastel"
    CELESTIAL = "celestial"


# Default zodiac palette for each theme
THEME_DEFAULT_PALETTES = {
    ChartTheme.CLASSIC: ZodiacPalette.GREY,
    ChartTheme.DARK: ZodiacPalette.GREY,
    ChartTheme.MIDNIGHT: ZodiacPalette.GREY,
    ChartTheme.NEON: ZodiacPalette.RAINBOW,
    ChartTheme.SEPIA: ZodiacPalette.GREY,
    ChartTheme.PASTEL: ZodiacPalette.RAINBOW,
    ChartTheme.CELESTIAL: ZodiacPalette.GREY,
}


def get_theme_style(theme: ChartTheme) -> dict[str, Any]:
    """
    Get the complete style configuration for a theme.

    Args:
        theme: The theme to use

    Returns:
        Complete style dictionary for ChartRenderer
    """
    if theme == ChartTheme.CLASSIC:
        return _get_classic_theme()
    elif theme == ChartTheme.DARK:
        return _get_dark_theme()
    elif theme == ChartTheme.MIDNIGHT:
        return _get_midnight_theme()
    elif theme == ChartTheme.NEON:
        return _get_neon_theme()
    elif theme == ChartTheme.SEPIA:
        return _get_sepia_theme()
    elif theme == ChartTheme.PASTEL:
        return _get_pastel_theme()
    elif theme == ChartTheme.CELESTIAL:
        return _get_celestial_theme()
    else:
        return _get_classic_theme()


def get_theme_default_palette(theme: ChartTheme) -> ZodiacPalette:
    """
    Get the default zodiac palette for a theme.

    Args:
        theme: The theme

    Returns:
        Default ZodiacPalette for this theme
    """
    return THEME_DEFAULT_PALETTES.get(theme, ZodiacPalette.GREY)


# ============================================================================
# Theme Definitions
# ============================================================================


def _get_classic_theme() -> dict[str, Any]:
    """Classic theme - current default styling (grey, professional)."""
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
            **{
                aspect_info.name: {
                    "color": aspect_info.color,
                    "width": aspect_info.metadata.get("line_width", 1.5),
                    "dash": aspect_info.metadata.get("dash_pattern", "1,0"),
                }
                for aspect_info in ASPECT_REGISTRY.values()
                if aspect_info.category in ["Major", "Minor"]
            },
            "default": {"color": "#BDC3C7", "width": 0.5, "dash": "2,2"},
            "line_color": "#BBBBBB",
            "background_color": "#FFFFFF",
        },
    }


def _get_dark_theme() -> dict[str, Any]:
    """Dark theme - dark grey background with light text."""
    return {
        "background_color": "#1E1E1E",
        "border_color": "#555555",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#2D2D2D",
            "line_color": "#666666",
            "glyph_color": "#CCCCCC",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#555555",
            "line_width": 0.8,
            "number_color": "#888888",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#252525",
            "fill_color_2": "#1E1E1E",
        },
        "angles": {
            "line_color": "#AAAAAA",
            "line_width": 2.5,
            "glyph_color": "#DDDDDD",
            "glyph_size": "12px",
        },
        "planets": {
            "glyph_color": "#EEEEEE",
            "glyph_size": "32px",
            "info_color": "#BBBBBB",
            "info_size": "10px",
            "retro_color": "#FF6B6B",
        },
        "aspects": {
            "Conjunction": {"color": "#FFD700", "width": 2.0, "dash": "1,0"},
            "Opposition": {"color": "#FF6B6B", "width": 1.5, "dash": "1,0"},
            "Trine": {"color": "#4ECDC4", "width": 1.5, "dash": "1,0"},
            "Square": {"color": "#FF6B9D", "width": 1.5, "dash": "1,0"},
            "Sextile": {"color": "#95E1D3", "width": 1.2, "dash": "1,0"},
            "default": {"color": "#666666", "width": 0.5, "dash": "2,2"},
            "line_color": "#555555",
            "background_color": "#1E1E1E",
        },
    }


def _get_midnight_theme() -> dict[str, Any]:
    """Midnight theme - elegant night sky with deep navy and white/gold accents."""
    return {
        "background_color": "#0A1628",
        "border_color": "#3A5A7C",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#0D1F3C",
            "line_color": "#4A6FA5",
            "glyph_color": "#E8E8E8",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#4A6FA5",
            "line_width": 0.8,
            "number_color": "#A8C5E8",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#0E223D",
            "fill_color_2": "#0A1628",
        },
        "angles": {
            "line_color": "#E8E8E8",
            "line_width": 2.5,
            "glyph_color": "#FFFFFF",
            "glyph_size": "12px",
        },
        "planets": {
            "glyph_color": "#FFD700",
            "glyph_size": "32px",
            "info_color": "#E8E8E8",
            "info_size": "10px",
            "retro_color": "#FFA07A",
        },
        "aspects": {
            "Conjunction": {"color": "#FFD700", "width": 2.0, "dash": "1,0"},
            "Opposition": {"color": "#87CEEB", "width": 1.5, "dash": "1,0"},
            "Trine": {"color": "#98D8E8", "width": 1.5, "dash": "1,0"},
            "Square": {"color": "#B0C4DE", "width": 1.5, "dash": "1,0"},
            "Sextile": {"color": "#ADD8E6", "width": 1.2, "dash": "1,0"},
            "default": {"color": "#4A6FA5", "width": 0.5, "dash": "2,2"},
            "line_color": "#3A5A7C",
            "background_color": "#0A1628",
        },
    }


def _get_neon_theme() -> dict[str, Any]:
    """Neon theme - cyberpunk aesthetic with black background and bright neon colors."""
    return {
        "background_color": "#0D0D0D",
        "border_color": "#00FFFF",
        "border_width": 1.5,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#1A1A1A",
            "line_color": "#00FFFF",
            "glyph_color": "#FF00FF",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#00FFFF",
            "line_width": 1.0,
            "number_color": "#39FF14",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#1A0A1A",
            "fill_color_2": "#0D0D0D",
        },
        "angles": {
            "line_color": "#FF00FF",
            "line_width": 3.0,
            "glyph_color": "#FFFF00",
            "glyph_size": "12px",
        },
        "planets": {
            "glyph_color": "#00FFFF",
            "glyph_size": "32px",
            "info_color": "#FF00FF",
            "info_size": "10px",
            "retro_color": "#FF1493",
        },
        "aspects": {
            "Conjunction": {"color": "#FFFF00", "width": 2.5, "dash": "1,0"},
            "Opposition": {"color": "#FF00FF", "width": 2.0, "dash": "1,0"},
            "Trine": {"color": "#00FFFF", "width": 2.0, "dash": "1,0"},
            "Square": {"color": "#FF1493", "width": 2.0, "dash": "1,0"},
            "Sextile": {"color": "#39FF14", "width": 1.5, "dash": "1,0"},
            "default": {"color": "#00FF88", "width": 0.8, "dash": "2,2"},
            "line_color": "#00FFFF",
            "background_color": "#0D0D0D",
        },
    }


def _get_sepia_theme() -> dict[str, Any]:
    """Sepia theme - vintage/aged paper aesthetic with warm browns."""
    return {
        "background_color": "#F4ECD8",
        "border_color": "#8B7355",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Georgia", "Times New Roman", serif',
        "zodiac": {
            "ring_color": "#E8DCC4",
            "line_color": "#A68B6B",
            "glyph_color": "#5D4E37",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#A68B6B",
            "line_width": 0.8,
            "number_color": "#8B7355",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#EDE4D0",
            "fill_color_2": "#F4ECD8",
        },
        "angles": {
            "line_color": "#5D4E37",
            "line_width": 2.5,
            "glyph_color": "#3E2F1F",
            "glyph_size": "12px",
        },
        "planets": {
            "glyph_color": "#4A3728",
            "glyph_size": "32px",
            "info_color": "#6B5744",
            "info_size": "10px",
            "retro_color": "#A0522D",
        },
        "aspects": {
            "Conjunction": {"color": "#8B4513", "width": 2.0, "dash": "1,0"},
            "Opposition": {"color": "#A0522D", "width": 1.5, "dash": "1,0"},
            "Trine": {"color": "#9B7653", "width": 1.5, "dash": "1,0"},
            "Square": {"color": "#8B7355", "width": 1.5, "dash": "1,0"},
            "Sextile": {"color": "#A68B6B", "width": 1.2, "dash": "1,0"},
            "default": {"color": "#C4A582", "width": 0.5, "dash": "2,2"},
            "line_color": "#A68B6B",
            "background_color": "#F4ECD8",
        },
    }


def _get_pastel_theme() -> dict[str, Any]:
    """Pastel theme - soft, gentle colors with light and airy feel."""
    return {
        "background_color": "#FAFAFA",
        "border_color": "#C4C4C4",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#F0F0F0",
            "line_color": "#D4D4D4",
            "glyph_color": "#888888",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#D4D4D4",
            "line_width": 0.8,
            "number_color": "#A0A0A0",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#F5F5F5",
            "fill_color_2": "#FAFAFA",
        },
        "angles": {
            "line_color": "#888888",
            "line_width": 2.5,
            "glyph_color": "#666666",
            "glyph_size": "12px",
        },
        "planets": {
            "glyph_color": "#555555",
            "glyph_size": "32px",
            "info_color": "#777777",
            "info_size": "10px",
            "retro_color": "#FF9999",
        },
        "aspects": {
            "Conjunction": {"color": "#FFD4A3", "width": 2.0, "dash": "1,0"},
            "Opposition": {"color": "#FFB3BA", "width": 1.5, "dash": "1,0"},
            "Trine": {"color": "#BAE1FF", "width": 1.5, "dash": "1,0"},
            "Square": {"color": "#FFDFBA", "width": 1.5, "dash": "1,0"},
            "Sextile": {"color": "#BAFFC9", "width": 1.2, "dash": "1,0"},
            "default": {"color": "#E0E0E0", "width": 0.5, "dash": "2,2"},
            "line_color": "#D4D4D4",
            "background_color": "#FAFAFA",
        },
    }


def _get_celestial_theme() -> dict[str, Any]:
    """Celestial theme - cosmic/galaxy aesthetic with deep purples and gold stars."""
    return {
        "background_color": "#1A0F2E",
        "border_color": "#6B4FA3",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#2A1A4A",
            "line_color": "#7B5FAF",
            "glyph_color": "#E8D4FF",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#7B5FAF",
            "line_width": 0.8,
            "number_color": "#C4A4E8",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#241540",
            "fill_color_2": "#1A0F2E",
        },
        "angles": {
            "line_color": "#FFD700",
            "line_width": 2.5,
            "glyph_color": "#FFF4D4",
            "glyph_size": "12px",
        },
        "planets": {
            "glyph_color": "#FFD700",
            "glyph_size": "32px",
            "info_color": "#E8D4FF",
            "info_size": "10px",
            "retro_color": "#FF69B4",
        },
        "aspects": {
            "Conjunction": {"color": "#FFD700", "width": 2.0, "dash": "1,0"},
            "Opposition": {"color": "#DA70D6", "width": 1.5, "dash": "1,0"},
            "Trine": {"color": "#9370DB", "width": 1.5, "dash": "1,0"},
            "Square": {"color": "#BA55D3", "width": 1.5, "dash": "1,0"},
            "Sextile": {"color": "#DDA0DD", "width": 1.2, "dash": "1,0"},
            "default": {"color": "#7B5FAF", "width": 0.5, "dash": "2,2"},
            "line_color": "#6B4FA3",
            "background_color": "#1A0F2E",
        },
    }


def get_theme_description(theme: ChartTheme) -> str:
    """
    Get a human-readable description of a theme.

    Args:
        theme: The theme to describe

    Returns:
        Description string
    """
    descriptions = {
        ChartTheme.CLASSIC: "Classic - Professional grey/neutral (default)",
        ChartTheme.DARK: "Dark - Dark grey background with light text",
        ChartTheme.MIDNIGHT: "Midnight - Elegant night sky with deep navy and white/gold",
        ChartTheme.NEON: "Neon - Cyberpunk aesthetic with bright neon colors",
        ChartTheme.SEPIA: "Sepia - Vintage aged paper with warm browns",
        ChartTheme.PASTEL: "Pastel - Soft gentle colors, light and airy",
        ChartTheme.CELESTIAL: "Celestial - Cosmic galaxy with deep purples and gold",
    }
    return descriptions.get(theme, "Unknown theme")
