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
    OuterHouseCuspLayer,
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
    moon_phase_position: str | None = None,  # None = auto (bottom-right if aspects, center if not)
    moon_phase_label: bool = True,
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
    house_systems: str | list[str] | None = None,  # Single name, list of names, or "all"
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
        house_systems: House system(s) to overlay on the chart. Options:
            - None (default): Use chart's default house system only
            - Single system name (e.g., "Whole Sign"): Overlay that system
            - List of names (e.g., ["Placidus", "Whole Sign"]): Overlay multiple systems
            - "all": Display all available house systems from the chart

    Note:
        Zodiac wheel glyphs are automatically adapted for contrast against their
        sign backgrounds for accessibility (WCAG AA compliance). No configuration needed.
        When multiple house systems are specified, the first is drawn with default style,
        and additional systems are drawn with distinct styles (dashed lines, different colors).

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
        # If no zodiac palette specified, use theme's default
        if zodiac_palette is None:
            zodiac_palette = get_theme_default_palette(theme_enum)
        # If no aspect palette specified, use theme's default
        if aspect_palette is None:
            from .themes import get_theme_default_aspect_palette
            aspect_palette = get_theme_default_aspect_palette(theme_enum).value
        # If no planet glyph palette specified, use theme's default
        if planet_glyph_palette is None:
            from .themes import get_theme_default_planet_palette
            planet_glyph_palette = get_theme_default_planet_palette(theme_enum).value
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

    # Count corner layers early to determine if padding is needed
    # This must happen BEFORE creating SVG so borders are drawn with correct radii
    corner_layers_count = 0
    if chart_info:
        corner_layers_count += 1
    if aspect_counts:
        corner_layers_count += 1
    if element_modality_table:
        corner_layers_count += 1
    if chart_shape:
        corner_layers_count += 1

    # Apply padding if auto_padding is enabled and >2 corners are occupied
    # Must be done before creating SVG so borders use adjusted radii
    if auto_padding and corner_layers_count > 2:
        # Add subtle padding by slightly reducing radii (keeps chart centered)
        padding_factor = 0.95  # Reduce by 5%
        for key in renderer.radii:
            renderer.radii[key] *= padding_factor

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

    # Determine which house systems to render
    house_system_names = []
    if house_systems is None:
        # Default: use chart's default house system
        house_system_names = [chart.default_house_system]
    elif house_systems == "all":
        # Use all available house systems from chart
        house_system_names = list(chart.house_systems.keys())
    elif isinstance(house_systems, str):
        # Single house system specified
        house_system_names = [house_systems]
    else:
        # List of house systems
        house_system_names = house_systems

    # Assemble the layers in draw order (background to foreground)
    layers: list[IRenderLayer] = [
        ZodiacLayer(palette=zodiac_palette),
    ]

    # Add house cusp layers (first with default style, rest with distinct styles)
    for i, system_name in enumerate(house_system_names):
        if i == 0:
            # First system uses default style
            layers.append(HouseCuspLayer(house_system_name=system_name))
        else:
            # Additional systems use distinct styles
            # Cycle through colors for multiple overlays
            overlay_colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6"]
            color = overlay_colors[(i - 1) % len(overlay_colors)]

            layers.append(
                HouseCuspLayer(
                    house_system_name=system_name,
                    style_override={
                        "line_color": color,
                        "line_width": 0.5,
                        "line_dash": "5,5",
                        "number_color": color,
                        "fill_alternate": False,  # Don't fill for overlay systems
                    },
                )
            )

    # Add remaining layers
    layers.extend([
        AspectLayer(),
        PlanetLayer(planet_set=planets_to_draw, radius_key="planet_ring"),
        AngleLayer(),
    ])

    # Add moon phase layer if requested
    if moon_phase:
        moon_layer = MoonPhaseLayer(
            position=moon_phase_position,
            show_label=moon_phase_label,
        )
        layers.insert(3, moon_layer)  # Insert before PlanetLayer

    # Add corner layers (auto_padding already applied earlier if needed)
    corner_positions = set()

    # Add chart info layer if requested
    if chart_info:
        info_layer = ChartInfoLayer(
            position=chart_info_position,
            fields=chart_info_fields,
            house_systems=house_system_names,  # Pass actual systems being rendered
        )
        layers.append(info_layer)
        corner_positions.add(chart_info_position)

    # Add aspect counts layer if requested
    if aspect_counts:
        counts_layer = AspectCountsLayer(
            position=aspect_counts_position,
        )
        layers.append(counts_layer)
        corner_positions.add(aspect_counts_position)

    # Add element/modality table layer if requested
    if element_modality_table:
        table_layer = ElementModalityTableLayer(
            position=element_modality_position,
        )
        layers.append(table_layer)
        corner_positions.add(element_modality_position)

    # Add chart shape layer if requested (with collision detection)
    if chart_shape:
        # Check for collision with auto-positioned moon phase
        # Skip chart shape if moon phase will be in same corner (bottom-right when aspects present)
        moon_will_be_in_bottom_right = (
            moon_phase
            and moon_phase_position is None  # Auto-detect enabled
            and chart.aspects and len(chart.aspects) > 0  # Has aspects = moon goes to bottom-right
            and chart_shape_position == "bottom-right"  # Chart shape also in bottom-right
        )

        if not moon_will_be_in_bottom_right:
            shape_layer = ChartShapeLayer(
                position=chart_shape_position,
            )
            layers.append(shape_layer)
            corner_positions.add(chart_shape_position)

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
        # If no zodiac palette specified, use theme's default
        if zodiac_palette is None:
            zodiac_palette = get_theme_default_palette(theme_enum)
        # If no aspect palette specified, use theme's default
        if aspect_palette is None:
            from .themes import get_theme_default_aspect_palette
            aspect_palette = get_theme_default_aspect_palette(theme_enum).value
        # If no planet glyph palette specified, use theme's default
        if planet_glyph_palette is None:
            from .themes import get_theme_default_planet_palette
            planet_glyph_palette = get_theme_default_planet_palette(theme_enum).value
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


def draw_comparison_chart(
    comparison,  # Comparison object from ComparisonBuilder
    filename: str = "comparison.svg",
    size: int = 700,  # Larger default for bi-wheel
    moon_phase: bool | str = "chart1",  # True/"both", False, or "chart1"
    moon_phase_position: str | None = None,
    moon_phase_label: bool = True,
    chart_info: bool = True,
    chart_info_position: str = "top-left",
    chart_info_fields: list[str] | None = None,
    aspect_counts: bool = False,
    aspect_counts_position: str = "top-right",
    auto_padding: bool = True,
    extended_canvas: str | None = "right",  # Default to right for comparisons
    show_position_table: bool = True,
    show_aspectarian: bool = True,
    aspectarian_mode: str = "cross_chart",  # "cross_chart", "all", "chart1", "chart2"
    theme: ChartTheme | str | None = None,
    zodiac_palette: ZodiacPalette | str | None = None,
    aspect_palette: str | None = None,
    planet_glyph_palette: str | None = None,
    color_sign_info: bool = False,
    style_config: dict | None = None,
) -> str:
    """
    Draws a bi-wheel comparison chart (synastry, transits, progressions).

    This function creates a bi-wheel layout where:
    - Inner wheel: chart1 (native/person1) planets
    - Outer wheel: chart2 (transit/person2/progressed) planets
    - Cross-chart aspects drawn in the central aspect ring

    Args:
        comparison: Comparison object from ComparisonBuilder.calculate()
        filename: Output filename (e.g., "synastry.svg")
        size: Pixel dimensions (chart will be larger to accommodate outer wheel)
        moon_phase: Moon phase display:
            - "chart1": Show only chart1's moon phase (default)
            - "both" or True: Show both moons (small rendering)
            - False: Don't show moon phase
        moon_phase_position: Position of moon phase symbol
        moon_phase_label: Whether to show the phase name
        chart_info: Whether to show chart metadata
        chart_info_position: Position of chart info block
        chart_info_fields: List of fields to display
        aspect_counts: Whether to show aspect counts summary
        aspect_counts_position: Position of aspect counts
        auto_padding: Auto-pad when >2 corners occupied
        extended_canvas: Extended canvas mode ("right", "left", "below", or None)
        show_position_table: Show position table in extended canvas
        show_aspectarian: Show aspectarian in extended canvas
        aspectarian_mode: Which aspects to show in aspectarian:
            - "cross_chart": Only cross-chart aspects (default)
            - "all": All three grids (chart1 internal, chart2 internal, cross-chart)
            - "chart1": Only chart1 internal aspects
            - "chart2": Only chart2 internal aspects
        theme: Visual theme
        zodiac_palette: Color palette for zodiac wheel
        aspect_palette: Color palette for aspect lines
        planet_glyph_palette: Color palette for planet glyphs
        color_sign_info: Color sign glyphs adaptively
        style_config: Optional style overrides

    Returns:
        The filename of the saved chart
    """
    from starlight.core.comparison import Comparison

    # Import here to avoid circular dependency
    if not isinstance(comparison, Comparison):
        raise TypeError("comparison must be a Comparison object")

    # Find rotation angle from chart1's ASC
    asc_object = comparison.chart1.get_object("ASC")
    rotation_angle = asc_object.longitude if asc_object else 0.0

    # Determine theme and palette
    if theme:
        theme_enum = ChartTheme(theme) if isinstance(theme, str) else theme
        if zodiac_palette is None:
            zodiac_palette = get_theme_default_palette(theme_enum)
        if aspect_palette is None:
            from .themes import get_theme_default_aspect_palette

            aspect_palette = get_theme_default_aspect_palette(theme_enum).value
        if planet_glyph_palette is None:
            from .themes import get_theme_default_planet_palette

            planet_glyph_palette = get_theme_default_planet_palette(theme_enum).value
    else:
        if zodiac_palette is None:
            zodiac_palette = ZodiacPalette.GREY

    # Convert zodiac_palette to string if it's an enum
    if hasattr(zodiac_palette, "value"):
        zodiac_palette_str = zodiac_palette.value
    else:
        zodiac_palette_str = zodiac_palette

    # Calculate canvas dimensions for extended canvas
    canvas_width = size
    canvas_height = size
    chart_x_offset = 0
    chart_y_offset = 0

    if extended_canvas:
        if extended_canvas == "right":
            canvas_width = size + 500  # More space for interleaved tables
        elif extended_canvas == "left":
            canvas_width = size + 500
            chart_x_offset = 500
        elif extended_canvas == "below":
            canvas_height = size + 500
        else:
            raise ValueError(
                f"Invalid extended_canvas: {extended_canvas}. Must be 'right', 'left', or 'below'"
            )

    # Create renderer with bi-wheel radii adjustments
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

    # Adjust radii for bi-wheel layout
    # Inner planets: slightly smaller radius
    # Outer planets: outside the zodiac ring
    inner_planet_radius = renderer.radii["planet_ring"] - 15
    outer_planet_radius = renderer.radii["zodiac_ring_outer"] + 50

    # Add custom radii to renderer
    renderer.radii["inner_planet_ring"] = inner_planet_radius
    renderer.radii["outer_planet_ring"] = outer_planet_radius

    # Count corner layers for auto-padding
    corner_layers_count = 0
    if chart_info:
        corner_layers_count += 1
    if aspect_counts:
        corner_layers_count += 1

    # Apply padding if needed
    if auto_padding and corner_layers_count > 2:
        padding_factor = 0.95
        for key in renderer.radii:
            renderer.radii[key] *= padding_factor

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
                center=(
                    chart_x_offset + renderer.center,
                    chart_y_offset + renderer.center,
                ),
                r=renderer.radii["outer_border"],
                fill="none",
                stroke=renderer.style["border_color"],
                stroke_width=renderer.style["border_width"],
            )
        )
        dwg.add(
            dwg.circle(
                center=(
                    chart_x_offset + renderer.center,
                    chart_y_offset + renderer.center,
                ),
                r=renderer.radii["aspect_ring_inner"],
                fill="none",
                stroke=renderer.style["border_color"],
                stroke_width=renderer.style["border_width"],
            )
        )

        # Store offset
        renderer.x_offset = chart_x_offset
        renderer.y_offset = chart_y_offset
    else:
        dwg = renderer.create_svg_drawing(filename)
        renderer.x_offset = 0
        renderer.y_offset = 0

    # Get planets to draw from both charts
    chart1_planets = [
        p
        for p in comparison.chart1.positions
        if p.object_type
        in (ObjectType.PLANET, ObjectType.ASTEROID, ObjectType.NODE, ObjectType.POINT)
    ]
    chart2_planets = [
        p
        for p in comparison.chart2.positions
        if p.object_type
        in (ObjectType.PLANET, ObjectType.ASTEROID, ObjectType.NODE, ObjectType.POINT)
    ]

    # Assemble layers for bi-wheel
    layers: list[IRenderLayer] = [
        ZodiacLayer(palette=zodiac_palette),
        # Chart1 (inner) house cusps - more prominent
        HouseCuspLayer(house_system_name=comparison.chart1.default_house_system),
        # Chart2 (outer) house cusps - dashed, outside zodiac
        OuterHouseCuspLayer(
            house_system_name=comparison.chart2.default_house_system,
            style_override={
                "line_color": renderer.style.get("planets", {}).get(
                    "outer_wheel_planet_color", "#4A90E2"
                ),
                "line_dash": "3,3",
                "number_color": renderer.style.get("planets", {}).get(
                    "outer_wheel_planet_color", "#4A90E2"
                ),
            },
        ),
        # Cross-chart aspects only (in central ring)
        AspectLayer(),  # Will draw comparison.cross_aspects
        # Inner wheel planets (chart1)
        PlanetLayer(
            planet_set=chart1_planets,
            radius_key="inner_planet_ring",
            use_outer_wheel_color=False,
        ),
        # Outer wheel planets (chart2) - with outer wheel color
        PlanetLayer(
            planet_set=chart2_planets,
            radius_key="outer_planet_ring",
            use_outer_wheel_color=True,
        ),
        # Angles from chart1
        AngleLayer(),
    ]

    # Add moon phase layer(s)
    if moon_phase:
        if moon_phase == "both" or moon_phase is True:
            # TODO: Implement dual moon phase rendering
            # For now, just show chart1's moon
            moon_layer = MoonPhaseLayer(
                position=moon_phase_position,
                show_label=moon_phase_label,
            )
            layers.insert(3, moon_layer)
        else:  # "chart1" or any other truthy value
            moon_layer = MoonPhaseLayer(
                position=moon_phase_position,
                show_label=moon_phase_label,
            )
            layers.insert(3, moon_layer)

    # Add corner layers
    if chart_info:
        # Custom fields for comparison charts
        if chart_info_fields is None:
            chart_info_fields = ["name", "location", "datetime", "timezone"]

        info_layer = ChartInfoLayer(
            position=chart_info_position,
            fields=chart_info_fields,
        )
        layers.append(info_layer)

    if aspect_counts:
        counts_layer = AspectCountsLayer(position=aspect_counts_position)
        layers.append(counts_layer)

    # Render all layers
    # Note: AspectLayer will need to be modified to handle Comparison objects
    # For now, we'll render using comparison.chart1 but with cross_aspects
    for layer in layers:
        if isinstance(layer, AspectLayer):
            # Create a temporary chart-like object with cross_aspects
            # This is a workaround - ideally AspectLayer should handle Comparison
            from dataclasses import replace

            temp_chart = replace(comparison.chart1, aspects=comparison.cross_aspects)
            layer.render(renderer, dwg, temp_chart)
        else:
            # Most layers use chart1 as reference
            layer.render(renderer, dwg, comparison.chart1)

    # Add extended canvas layers if requested
    if extended_canvas and (show_position_table or show_aspectarian):
        # Calculate positions for extended layers
        if extended_canvas == "right":
            table_x = size + 30
            table_y = 30
            aspectarian_x = size + 30
            aspectarian_y = 350  # Below position table
        elif extended_canvas == "left":
            table_x = 30
            table_y = 30
            aspectarian_x = 30
            aspectarian_y = 350
        elif extended_canvas == "below":
            table_x = 30
            table_y = size + 30
            aspectarian_x = 400
            aspectarian_y = size + 30
        else:
            table_x = table_y = aspectarian_x = aspectarian_y = 0

        # Adapt colors to theme
        extended_style = {
            "text_color": renderer.style.get("planets", {}).get("info_color", "#333333"),
            "header_color": renderer.style.get("planets", {}).get(
                "glyph_color", "#222222"
            ),
            "grid_color": renderer.style.get("zodiac", {}).get("line_color", "#CCCCCC"),
        }

        # Position table - will need to be modified for Comparison objects
        if show_position_table:
            position_table = PositionTableLayer(
                x_offset=table_x,
                y_offset=table_y,
                style_override=extended_style,
            )
            # TODO: Modify PositionTableLayer to handle Comparison objects
            position_table.render(renderer, dwg, comparison)  # Pass comparison directly

        # Aspectarian - will need to be modified for Comparison objects
        if show_aspectarian:
            aspectarian = AspectarianLayer(
                x_offset=aspectarian_x,
                y_offset=aspectarian_y,
                style_override=extended_style,
            )
            # TODO: Modify AspectarianLayer to handle Comparison objects
            aspectarian.render(renderer, dwg, comparison)  # Pass comparison directly

    dwg.save()
    return filename
