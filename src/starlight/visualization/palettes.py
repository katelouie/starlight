"""
Zodiac Color Palettes (starlight.visualization.palettes)

Defines color schemes for the zodiac wheel visualization.
"""

from enum import Enum


class ZodiacPalette(str, Enum):
    """Available color palettes for the zodiac wheel."""

    # Base palettes
    GREY = "grey"
    RAINBOW = "rainbow"
    ELEMENTAL = "elemental"
    CARDINALITY = "cardinality"

    # Theme-coordinated rainbow variants
    RAINBOW_DARK = "rainbow_dark"
    RAINBOW_MIDNIGHT = "rainbow_midnight"
    RAINBOW_NEON = "rainbow_neon"
    RAINBOW_SEPIA = "rainbow_sepia"
    RAINBOW_CELESTIAL = "rainbow_celestial"

    # Theme-coordinated elemental variants
    ELEMENTAL_DARK = "elemental_dark"
    ELEMENTAL_MIDNIGHT = "elemental_midnight"
    ELEMENTAL_NEON = "elemental_neon"
    ELEMENTAL_SEPIA = "elemental_sepia"


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

    # ========================================================================
    # Theme-coordinated rainbow variants
    # ========================================================================

    elif palette == ZodiacPalette.RAINBOW_DARK:
        # Dark theme: Muted, darker rainbow colors
        return [
            "#B88B8F",  # Aries - muted red
            "#B89B8F",  # Taurus - muted orange
            "#B8AB8F",  # Gemini - muted yellow-orange
            "#B8B88F",  # Cancer - muted yellow
            "#ABB88F",  # Leo - muted yellow-green
            "#9BB88F",  # Virgo - muted green
            "#8FB89B",  # Libra - muted cyan-green
            "#8FB8AB",  # Scorpio - muted cyan
            "#8FABB8",  # Sagittarius - muted blue
            "#8F9BB8",  # Capricorn - muted indigo
            "#9B8FB8",  # Aquarius - muted violet
            "#AB8FB8",  # Pisces - muted magenta
        ]

    elif palette == ZodiacPalette.RAINBOW_MIDNIGHT:
        # Midnight theme: Cool, deep blues and purples
        return [
            "#4A5A7C",  # Aries - deep blue-grey
            "#3A6A8C",  # Taurus - deep cyan-blue
            "#3A7A9C",  # Gemini - deep cyan
            "#3A8AAC",  # Cancer - deep sky blue
            "#3A8A9C",  # Leo - deep teal
            "#3A9A8C",  # Virgo - deep blue-green
            "#3A9A7C",  # Libra - deep sea green
            "#3A8A6C",  # Scorpio - deep forest green
            "#4A6A7C",  # Sagittarius - deep blue
            "#5A5A8C",  # Capricorn - deep indigo
            "#6A4A8C",  # Aquarius - deep purple
            "#7A3A8C",  # Pisces - deep magenta
        ]

    elif palette == ZodiacPalette.RAINBOW_NEON:
        # Neon theme: Super bright, saturated neon colors
        return [
            "#FF00AA",  # Aries - hot pink
            "#FF3300",  # Taurus - neon orange-red
            "#FF6600",  # Gemini - neon orange
            "#FFFF00",  # Cancer - electric yellow
            "#AAFF00",  # Leo - neon lime
            "#00FF00",  # Virgo - electric green
            "#00FFAA",  # Libra - neon cyan-green
            "#00FFFF",  # Scorpio - electric cyan
            "#0088FF",  # Sagittarius - neon blue
            "#0000FF",  # Capricorn - electric blue
            "#AA00FF",  # Aquarius - neon violet
            "#FF00FF",  # Pisces - electric magenta
        ]

    elif palette == ZodiacPalette.RAINBOW_SEPIA:
        # Sepia theme: Warm browns, oranges, and earth tones
        return [
            "#C4A090",  # Aries - terracotta
            "#C4AA90",  # Taurus - warm tan
            "#C4B490",  # Gemini - sandy brown
            "#C4BE90",  # Cancer - wheat
            "#B4C490",  # Leo - sage
            "#AAC490",  # Virgo - olive
            "#90C4AA",  # Libra - sea foam brown
            "#90C4B4",  # Scorpio - sage blue
            "#90B4C4",  # Sagittarius - dusty blue
            "#90AAC4",  # Capricorn - slate blue
            "#A090C4",  # Aquarius - dusty purple
            "#AA90C4",  # Pisces - mauve
        ]

    elif palette == ZodiacPalette.RAINBOW_CELESTIAL:
        # Celestial theme: Deep cosmic purples, blues, and golds
        return [
            "#9B4FA3",  # Aries - cosmic purple
            "#8B5FAF",  # Taurus - deep lavender
            "#7B6FAF",  # Gemini - periwinkle
            "#6B7FAF",  # Cancer - cosmic blue
            "#5B8FAF",  # Leo - stellar blue
            "#4B9FAF",  # Virgo - galaxy cyan
            "#4BAFAF",  # Libra - nebula teal
            "#4BAFAF",  # Scorpio - deep teal
            "#5B9FAF",  # Sagittarius - space blue
            "#6B8FAF",  # Capricorn - cosmic indigo
            "#7B7FAF",  # Aquarius - deep violet
            "#8B6FAF",  # Pisces - stellar purple
        ]

    # ========================================================================
    # Theme-coordinated elemental variants
    # ========================================================================

    elif palette == ZodiacPalette.ELEMENTAL_DARK:
        # Dark theme: Darker, muted elemental colors
        element_colors = {
            "fire": "#B88080",  # Darker warm red
            "earth": "#80A880",  # Darker green
            "air": "#8080B8",  # Darker blue
            "water": "#A880B8",  # Darker purple
        }
        return [element_colors[SIGN_ELEMENTS[i]] for i in range(12)]

    elif palette == ZodiacPalette.ELEMENTAL_MIDNIGHT:
        # Midnight theme: Cool-toned elements
        element_colors = {
            "fire": "#5A6A8C",  # Cool blue-grey (fire as starlight)
            "earth": "#4A7A7C",  # Deep teal (earth as ocean)
            "air": "#6A7AAC",  # Deep sky blue
            "water": "#5A5A8C",  # Deep indigo
        }
        return [element_colors[SIGN_ELEMENTS[i]] for i in range(12)]

    elif palette == ZodiacPalette.ELEMENTAL_NEON:
        # Neon theme: Electric bright elements
        element_colors = {
            "fire": "#FF0066",  # Electric magenta
            "earth": "#00FF66",  # Neon green
            "air": "#00CCFF",  # Electric cyan
            "water": "#CC00FF",  # Neon purple
        }
        return [element_colors[SIGN_ELEMENTS[i]] for i in range(12)]

    elif palette == ZodiacPalette.ELEMENTAL_SEPIA:
        # Sepia theme: Warm-toned elements
        element_colors = {
            "fire": "#C49080",  # Terracotta
            "earth": "#A0B490",  # Olive
            "air": "#90A8C4",  # Dusty blue
            "water": "#A490B4",  # Dusty purple
        }
        return [element_colors[SIGN_ELEMENTS[i]] for i in range(12)]

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
        # Base palettes
        ZodiacPalette.GREY: "Classic grey wheel (no color)",
        ZodiacPalette.RAINBOW: "Rainbow spectrum (12 soft colors)",
        ZodiacPalette.ELEMENTAL: "4-color elemental (Fire/Earth/Air/Water)",
        ZodiacPalette.CARDINALITY: "3-color modality (Cardinal/Fixed/Mutable)",
        # Rainbow variants
        ZodiacPalette.RAINBOW_DARK: "Dark rainbow (muted, darker spectrum)",
        ZodiacPalette.RAINBOW_MIDNIGHT: "Midnight rainbow (cool blues and purples)",
        ZodiacPalette.RAINBOW_NEON: "Neon rainbow (super bright electric colors)",
        ZodiacPalette.RAINBOW_SEPIA: "Sepia rainbow (warm browns and earth tones)",
        ZodiacPalette.RAINBOW_CELESTIAL: "Celestial rainbow (cosmic purples and blues)",
        # Elemental variants
        ZodiacPalette.ELEMENTAL_DARK: "Dark elemental (muted element colors)",
        ZodiacPalette.ELEMENTAL_MIDNIGHT: "Midnight elemental (cool-toned elements)",
        ZodiacPalette.ELEMENTAL_NEON: "Neon elemental (electric element colors)",
        ZodiacPalette.ELEMENTAL_SEPIA: "Sepia elemental (warm-toned elements)",
    }
    return descriptions.get(palette, "Unknown palette")
