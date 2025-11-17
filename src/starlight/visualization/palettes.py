"""
Zodiac Color Palettes (starlight.visualization.palettes)

Defines color schemes for the zodiac wheel visualization.
"""

from enum import Enum


class ZodiacPalette(str, Enum):
    """Available color palettes for the zodiac wheel."""

    GREY = "grey"
    RAINBOW = "rainbow"
    ELEMENTAL = "elemental"
    CARDINALITY = "cardinality"


# Zodiac sign properties for palette mapping
SIGN_ELEMENTS = {
    0: "fire",  # Aries
    1: "earth",  # Taurus
    2: "air",  # Gemini
    3: "water",  # Cancer
    4: "fire",  # Leo
    5: "earth",  # Virgo
    6: "air",  # Libra
    7: "water",  # Scorpio
    8: "fire",  # Sagittarius
    9: "earth",  # Capricorn
    10: "air",  # Aquarius
    11: "water",  # Pisces
}

SIGN_MODALITIES = {
    0: "cardinal",  # Aries
    1: "fixed",  # Taurus
    2: "mutable",  # Gemini
    3: "cardinal",  # Cancer
    4: "fixed",  # Leo
    5: "mutable",  # Virgo
    6: "cardinal",  # Libra
    7: "fixed",  # Scorpio
    8: "mutable",  # Sagittarius
    9: "cardinal",  # Capricorn
    10: "fixed",  # Aquarius
    11: "mutable",  # Pisces
}


def get_palette_colors(palette: ZodiacPalette) -> list[str]:
    """
    Get the color list for a zodiac wheel palette.

    Returns a list of 12 colors (one per sign, starting with Aries).

    Args:
        palette: The palette to use

    Returns:
        List of 12 hex color strings
    """
    if palette == ZodiacPalette.GREY:
        # All signs same color (classic grey)
        return ["#EEEEEE"] * 12

    elif palette == ZodiacPalette.RAINBOW:
        # Tasteful rainbow: soft, desaturated colors progressing through hue wheel
        # Starting with Aries (red) and progressing through the spectrum
        return [
            "#E8B4B8",  # Aries - soft red
            "#E8C4B8",  # Taurus - soft orange
            "#E8D8B8",  # Gemini - soft yellow-orange
            "#E8E8B8",  # Cancer - soft yellow
            "#D8E8B8",  # Leo - soft yellow-green
            "#C4E8B8",  # Virgo - soft green
            "#B8E8C4",  # Libra - soft cyan-green
            "#B8E8D8",  # Scorpio - soft cyan
            "#B8D8E8",  # Sagittarius - soft blue
            "#B8C4E8",  # Capricorn - soft indigo
            "#C4B8E8",  # Aquarius - soft violet
            "#D8B8E8",  # Pisces - soft magenta
        ]

    elif palette == ZodiacPalette.ELEMENTAL:
        # 4-color elemental palette
        element_colors = {
            "fire": "#F4D4D4",  # Soft warm red
            "earth": "#D4E4D4",  # Soft green
            "air": "#D4E4F4",  # Soft blue
            "water": "#E4D4F4",  # Soft purple
        }
        return [element_colors[SIGN_ELEMENTS[i]] for i in range(12)]

    elif palette == ZodiacPalette.CARDINALITY:
        # 3-color cardinality/modality palette
        modality_colors = {
            "cardinal": "#F4E4D4",  # Soft peach (initiating)
            "fixed": "#D4E4E4",  # Soft teal (sustaining)
            "mutable": "#E4D4E4",  # Soft lavender (adapting)
        }
        return [modality_colors[SIGN_MODALITIES[i]] for i in range(12)]

    else:
        # Fallback to grey
        return ["#EEEEEE"] * 12


def get_palette_description(palette: ZodiacPalette) -> str:
    """
    Get a human-readable description of a palette.

    Args:
        palette: The palette to describe

    Returns:
        Description string
    """
    descriptions = {
        ZodiacPalette.GREY: "Classic grey wheel (no color)",
        ZodiacPalette.RAINBOW: "Rainbow spectrum (12 colors progressing through hue wheel)",
        ZodiacPalette.ELEMENTAL: "4-color elemental (Fire: red, Earth: green, Air: blue, Water: purple)",
        ZodiacPalette.CARDINALITY: "3-color modality (Cardinal: peach, Fixed: teal, Mutable: lavender)",
    }
    return descriptions.get(palette, "Unknown palette")
