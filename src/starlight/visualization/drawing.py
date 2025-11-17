"""
High-Level Drawing Functions (starlight.visualization.drawing)

This is the main, user-facing module for creating chart images.
It uses the ChartRenderer and Layer classes from .core and .layers
to assemble and render chart drawings.
"""

from starlight.core.models import CalculatedChart, ObjectType

from .core import ChartRenderer, IRenderLayer
from .layers import (
    AngleLayer,
    AspectLayer,
    ChartInfoLayer,
    HouseCuspLayer,
    PlanetLayer,
    ZodiacLayer,
)
from .moon_phase import MoonPhaseLayer
from .palettes import ZodiacPalette
from .themes import ChartTheme, get_theme_default_palette


def draw_chart(
    chart: CalculatedChart,
    filename: str = "chart.svg",
    size: int = 600,
    moon_phase: bool = True,
    moon_phase_position: str = "center",
    moon_phase_label: bool = False,
    chart_info: bool = False,
    chart_info_position: str = "top-left",
    chart_info_fields: list[str] | None = None,
    theme: ChartTheme | str | None = None,
    zodiac_palette: ZodiacPalette | str | None = None,
    aspect_palette: str | None = None,
    planet_glyph_palette: str | None = None,
    color_sign_info: bool = False,
    style_config: dict | None = None,
) -> str:
    """
    Draws a standard natal chart.

    This function assembles the standard layers for a natal chart
    and renders them to an SVG file.

    Args:
        chart: The CalculatedChart object from the ChartBuilder.
        filename: The output filename (e.g., "natal_chart.svg").
        size: The pixel dimensions of the (square) chart.
        moon_phase: Whether to show moon phase.
        moon_phase_position: Position of moon phase symbol.
            Options: "center", "top-left", "top-right", "bottom-left", "bottom-right"
        moon_phase_label: Whether to show the phase name below the moon symbol.
        chart_info: Whether to show chart metadata (name, location, date/time, etc.).
        chart_info_position: Position of chart info block.
            Options: "top-left", "top-right", "bottom-left", "bottom-right"
        chart_info_fields: List of fields to display in chart info.
            Options: "name", "location", "datetime", "timezone", "coordinates", "house_system"
            If None, displays all except house_system.
        theme: Visual theme (classic, dark, midnight, neon, sepia, pastel, celestial,
               viridis, plasma, inferno, magma, cividis, turbo).
               If not specified, uses classic theme.
        zodiac_palette: Color palette for zodiac wheel (grey, rainbow, elemental, cardinality,
                        viridis, plasma, inferno, etc.).
                        If not specified, uses the theme's default palette.
        aspect_palette: Color palette for aspect lines (classic, dark, viridis, plasma, etc.).
                        If not specified, uses the theme's default palette.
        planet_glyph_palette: Color palette for planet glyphs (default, element, sign_ruler,
                              planet_type, luminaries, rainbow, chakra, viridis, etc.).
                              If not specified, uses the theme's default palette.
        color_sign_info: If True, color sign glyphs in info stack based on zodiac palette
                         with adaptive contrast. Default False.
        style_config: Optional style overrides for fine-tuning.

    Returns:
        The filename of the saved chart.
    """
    # Find the rotation angle
    # We'll use the Asc angle as the default for rotation
    asc_object = chart.get_object("ASC")
    rotation_angle = asc_object.longitude if asc_object else 0.0

    # Determine theme and palette
    if theme:
        theme_enum = ChartTheme(theme) if isinstance(theme, str) else theme
        # If no palette specified, use theme's default
        if zodiac_palette is None:
            zodiac_palette = get_theme_default_palette(theme_enum)
    else:
        # No theme specified, use classic defaults
        if zodiac_palette is None:
            zodiac_palette = ZodiacPalette.GREY

    # Convert zodiac_palette to string if it's an enum
    if hasattr(zodiac_palette, "value"):
        zodiac_palette_str = zodiac_palette.value
    else:
        zodiac_palette_str = zodiac_palette

    # Create main renderer "canvas" with the rotation
    renderer = ChartRenderer(
        size=size,
        rotation=rotation_angle,
        theme=theme,
        style_config=style_config,
        zodiac_palette=zodiac_palette_str,
        aspect_palette=aspect_palette,
        planet_glyph_palette=planet_glyph_palette,
        color_sign_info=color_sign_info,
    )

    # Get the SVG drawing object
    dwg = renderer.create_svg_drawing(filename)

    # Get the list of planets to draw (includes nodes and points)
    planets_to_draw = [
        p
        for p in chart.positions
        if p.object_type
        in (ObjectType.PLANET, ObjectType.ASTEROID, ObjectType.NODE, ObjectType.POINT)
    ]

    # Assemble the layers in draw order (background to foreground)
    layers: list[IRenderLayer] = [
        ZodiacLayer(palette=zodiac_palette),
        HouseCuspLayer(house_system_name=chart.default_house_system),
        AspectLayer(),
        PlanetLayer(planet_set=planets_to_draw, radius_key="planet_ring"),
        AngleLayer(),
    ]

    # Add moon phase layer if requested
    if moon_phase:
        moon_layer = MoonPhaseLayer(
            position=moon_phase_position,
            show_label=moon_phase_label,
        )
        layers.insert(3, moon_layer)  # Insert before PlanetLayer

    # Add chart info layer if requested
    if chart_info:
        info_layer = ChartInfoLayer(
            position=chart_info_position,
            fields=chart_info_fields,
        )
        # Add chart info as the last layer (on top of everything)
        layers.append(info_layer)

    # Tell each layer to render itself
    for layer in layers:
        layer.render(renderer, dwg, chart)

    # Save the final SVG
    dwg.save()

    return filename


def draw_chart_with_multiple_houses(
    chart: CalculatedChart,
    filename: str = "multi_house_chart.svg",
    size: int = 600,
    theme: ChartTheme | str | None = None,
    zodiac_palette: ZodiacPalette | str | None = None,
    style_config: dict | None = None,
) -> str:
    """
    Example of the new system's flexibility:
    Draws a natal chart with two house systems overlaid.

    Args:
        chart: The CalculatedChart object from the ChartBuilder.
        filename: The output filename.
        size: The pixel dimensions of the (square) chart.
        theme: Visual theme (classic, dark, midnight, neon, sepia, pastel, celestial).
        zodiac_palette: Color palette for zodiac wheel (grey, rainbow, elemental, cardinality).
        style_config: Optional style overrides for fine-tuning.

    Returns:
        The filename of the saved chart.
    """
    asc_object = chart.get_object("ASC")
    rotation_angle = asc_object.longitude if asc_object else 0.0

    # Determine theme and palette
    if theme:
        theme_enum = ChartTheme(theme) if isinstance(theme, str) else theme
        # If no palette specified, use theme's default
        if zodiac_palette is None:
            zodiac_palette = get_theme_default_palette(theme_enum)
    else:
        # No theme specified, use classic defaults
        if zodiac_palette is None:
            zodiac_palette = ZodiacPalette.GREY

    renderer = ChartRenderer(
        size=size, rotation=rotation_angle, theme=theme, style_config=style_config
    )
    dwg = renderer.create_svg_drawing(filename)

    # Get the list of planets to draw (includes nodes and points)
    planets_to_draw = [
        p
        for p in chart.positions
        if p.object_type
        in (ObjectType.PLANET, ObjectType.ASTEROID, ObjectType.NODE, ObjectType.POINT)
    ]

    # Get the names of the first two house systems
    system_names = list(chart.house_systems.keys())
    if not system_names:
        raise ValueError("Chart has no house systems to draw.")

    system1_name = system_names[0]
    system2_name = system_names[1] if len(system_names) > 1 else system_names[0]

    layers: list[IRenderLayer] = [
        ZodiacLayer(palette=zodiac_palette),
        # --- The only change is here ---
        # Add the first house system (default style)
        HouseCuspLayer(house_system_name=system1_name),
        # Add the second house system with a custom style
        HouseCuspLayer(
            house_system_name=system2_name,
            style_override={
                "line_color": "red",
                "line_width": 0.5,
                "line_dash": "5,5",
                "number_color": "red",
                "fill_alternate": False,  # Don't draw fills for second system
            },
        ),
        # --- End change ---
        AspectLayer(),
        PlanetLayer(planet_set=planets_to_draw, radius_key="planet_ring"),
        AngleLayer(),
    ]

    for layer in layers:
        layer.render(renderer, dwg, chart)

    dwg.save()
    return filename
