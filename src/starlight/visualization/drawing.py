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
    HouseCuspLayer,
    PlanetLayer,
    ZodiacLayer,
)
from .moon_phase import MoonPhaseLayer


def draw_chart(
    chart: CalculatedChart,
    filename: str = "chart.svg",
    size: int = 600,
    moon_phase: bool = True,
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

    Returns:
        The filename of the saved chart.
    """
    # Find the rotation angle
    # We'll use the Asc angle as the default for rotation
    asc_object = chart.get_object("ASC")
    rotation_angle = asc_object.longitude if asc_object else 0.0

    # Create main renderer "canvas" with the rotation
    renderer = ChartRenderer(size=size, rotation=rotation_angle)

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
        ZodiacLayer(),
        HouseCuspLayer(house_system_name=chart.default_house_system),
        AspectLayer(),
        PlanetLayer(planet_set=planets_to_draw, radius_key="planet_ring"),
        AngleLayer(),
    ]

    if moon_phase:
        layers.insert(3, MoonPhaseLayer())  # Insert before PlanetLayer

    # Tell each layer to render itself
    for layer in layers:
        layer.render(renderer, dwg, chart)

    # Save the final SVG
    dwg.save()

    return filename


def draw_chart_with_multiple_houses(
    chart: CalculatedChart, filename: str = "multi_house_chart.svg", size: int = 600
) -> str:
    """
    Example of the new system's flexibility:
    Draws a natal chart with two house systems overlaid.
    """
    asc_object = chart.get_object("ASC")
    rotation_angle = asc_object.longitude if asc_object else 0.0

    renderer = ChartRenderer(size=size, rotation=rotation_angle)
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
        ZodiacLayer(),
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
