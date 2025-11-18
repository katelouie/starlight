"""
High-Level Drawing Functions (starlight.visualization.drawing)

This is the main, user-facing module for creating chart images.
It uses the ChartRenderer and Layer classes from .core and .layers
to assemble and render chart drawings.
"""

from starlight.core.models import CalculatedChart, ObjectType

from .core import ChartRenderer, IRenderLayer
from .extended_canvas import AspectarianLayer, PositionTableLayer
from .layers import (
    AngleLayer,
    AspectCountsLayer,
    AspectLayer,
    ChartInfoLayer,
    ChartShapeLayer,
    ElementModalityTableLayer,
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
    aspect_counts: bool = False,
    aspect_counts_position: str = "top-right",
    element_modality_table: bool = False,
    element_modality_position: str = "bottom-left",
    chart_shape: bool = False,
    chart_shape_position: str = "bottom-right",
    auto_padding: bool = True,
    extended_canvas: str | None = None,
    show_position_table: bool = True,
    show_aspectarian: bool = True,
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
        aspect_counts: Whether to show aspect counts summary.
        aspect_counts_position: Position of aspect counts.
            Options: "top-left", "top-right", "bottom-left", "bottom-right"
        element_modality_table: Whether to show element/modality cross-table.
        element_modality_position: Position of element/modality table.
            Options: "top-left", "top-right", "bottom-left", "bottom-right"
        chart_shape: Whether to show chart shape detection.
        chart_shape_position: Position of chart shape info.
            Options: "top-left", "top-right", "bottom-left", "bottom-right"
        auto_padding: If True, automatically add padding when >2 corners are occupied.
        extended_canvas: Extended canvas mode for position tables and aspectarian.
            Options: None (disabled), "right", "left", "below"
            When enabled, expands canvas to include tabular data alongside chart.
        show_position_table: Whether to show position table in extended canvas.
        show_aspectarian: Whether to show aspectarian grid in extended canvas.
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

    Note:
        Zodiac wheel glyphs are automatically adapted for contrast against their
        sign backgrounds for accessibility (WCAG AA compliance). No configuration needed.

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

    # Calculate canvas dimensions and chart offset for extended canvas
    canvas_width = size
    canvas_height = size
    chart_x_offset = 0
    chart_y_offset = 0

    if extended_canvas:
        if extended_canvas == "right":
            canvas_width = size + 450  # Add space on right
            chart_x_offset = 0
        elif extended_canvas == "left":
            canvas_width = size + 450  # Add space on left
            chart_x_offset = 450  # Shift chart to right
        elif extended_canvas == "below":
            canvas_height = size + 400  # Add space below
            chart_y_offset = 0
        else:
            raise ValueError(
                f"Invalid extended_canvas: {extended_canvas}. Must be 'right', 'left', or 'below'"
            )

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

    # Create SVG drawing
    if extended_canvas:
        import svgwrite

        dwg = svgwrite.Drawing(
            filename=filename,
            size=(f"{canvas_width}px", f"{canvas_height}px"),
            viewBox=f"0 0 {canvas_width} {canvas_height}",
            profile="full",
        )

        # Add background
        dwg.add(
            dwg.rect(
                insert=(0, 0),
                size=(f"{canvas_width}px", f"{canvas_height}px"),
                fill=renderer.style["background_color"],
            )
        )

        # Add chart borders at offset position
        dwg.add(
            dwg.circle(
                center=(chart_x_offset + renderer.center, chart_y_offset + renderer.center),
                r=renderer.radii["outer_border"],
                fill="none",
                stroke=renderer.style["border_color"],
                stroke_width=renderer.style["border_width"],
            )
        )
        dwg.add(
            dwg.circle(
                center=(chart_x_offset + renderer.center, chart_y_offset + renderer.center),
                r=renderer.radii["aspect_ring_inner"],
                fill="none",
                stroke=renderer.style["border_color"],
                stroke_width=renderer.style["border_width"],
            )
        )

        # Store offset in renderer for layers to use
        renderer.x_offset = chart_x_offset
        renderer.y_offset = chart_y_offset
    else:
        # Standard canvas - use renderer's method
        dwg = renderer.create_svg_drawing(filename)
        renderer.x_offset = 0
        renderer.y_offset = 0

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

    # Count corner layers to determine if padding is needed
    corner_layers_count = 0
    corner_positions = set()

    # Add chart info layer if requested
    if chart_info:
        info_layer = ChartInfoLayer(
            position=chart_info_position,
            fields=chart_info_fields,
        )
        layers.append(info_layer)
        corner_layers_count += 1
        corner_positions.add(chart_info_position)

    # Add aspect counts layer if requested
    if aspect_counts:
        counts_layer = AspectCountsLayer(
            position=aspect_counts_position,
        )
        layers.append(counts_layer)
        corner_layers_count += 1
        corner_positions.add(aspect_counts_position)

    # Add element/modality table layer if requested
    if element_modality_table:
        table_layer = ElementModalityTableLayer(
            position=element_modality_position,
        )
        layers.append(table_layer)
        corner_layers_count += 1
        corner_positions.add(element_modality_position)

    # Add chart shape layer if requested
    if chart_shape:
        shape_layer = ChartShapeLayer(
            position=chart_shape_position,
        )
        layers.append(shape_layer)
        corner_layers_count += 1
        corner_positions.add(chart_shape_position)

    # Apply padding if auto_padding is enabled and >2 corners are occupied
    # This is a simple approach - we just scale up the radii proportionally
    # A more sophisticated approach would expand the canvas size
    # For now, this keeps the chart centered with more breathing room
    if auto_padding and corner_layers_count > 2:
        # Add subtle padding by slightly reducing radii (keeps chart centered)
        padding_factor = 0.95  # Reduce by 5%
        for key in renderer.radii:
            renderer.radii[key] *= padding_factor

    # Tell each layer to render itself
    for layer in layers:
        layer.render(renderer, dwg, chart)

    # Add extended canvas layers if requested
    if extended_canvas and (show_position_table or show_aspectarian):
        # Calculate positions for extended layers based on mode
        if extended_canvas == "right":
            table_x = size + 30  # 30px margin from chart
            table_y = 30
            aspectarian_x = size + 30
            aspectarian_y = 300  # Below position table
        elif extended_canvas == "left":
            table_x = 30
            table_y = 30
            aspectarian_x = 30
            aspectarian_y = 300
        elif extended_canvas == "below":
            table_x = 30
            table_y = size + 30
            aspectarian_x = 350  # To the right of position table
            aspectarian_y = size + 30
        else:
            table_x = table_y = aspectarian_x = aspectarian_y = 0

        # Adapt extended layer colors to theme
        extended_style = {
            "text_color": renderer.style.get("planets", {}).get("info_color", "#333333"),
            "header_color": renderer.style.get("planets", {}).get("glyph_color", "#222222"),
            "grid_color": renderer.style.get("zodiac", {}).get("line_color", "#CCCCCC"),
        }

        # Add position table
        if show_position_table:
            position_table = PositionTableLayer(
                x_offset=table_x,
                y_offset=table_y,
                style_override=extended_style,
            )
            position_table.render(renderer, dwg, chart)

        # Add aspectarian
        if show_aspectarian:
            aspectarian = AspectarianLayer(
                x_offset=aspectarian_x,
                y_offset=aspectarian_y,
                style_override=extended_style,
            )
            aspectarian.render(renderer, dwg, chart)

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
