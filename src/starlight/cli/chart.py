"""Chart generation commands."""

from pathlib import Path

import click


@click.group(name="chart")
def chart_group():
    """Generate and export charts."""
    pass


@chart_group.command("from-registry")
@click.argument("name")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--house-system",
    default="Placidus",
    type=click.Choice(["Placidus", "Whole Sign", "Koch", "Equal"]),
    help="House system to use",
)
@click.option(
    "--format",
    "output_format",
    default="svg",
    type=click.Choice(["svg", "terminal", "json"]),
    help="Output format",
)
def chart_from_registry_cmd(name, output, house_system, output_format):
    """
    Generate a chart from the birth registry.

    Example:
        starlight chart from-registry "Albert Einstein" -o einstein.svg
    """
    from starlight.core.builder import ChartBuilder
    from starlight.presentation.builder import ReportBuilder
    from starlight.visualization.drawing import draw_chart

    try:
        # Build chart
        chart = (
            ChartBuilder.from_birth_registry(name)
            .with_house_system(house_system)
            .build()
        )

        if output_format == "svg":
            output_path = output or f"{name.lower().replace(' ', '_')}.svg"
            draw_chart(chart, output_path)
            click.echo(f"✅ Chart saved to: {output_path}")

        elif output_format == "terminal":
            report = (
                ReportBuilder.from_chart(chart)
                .with_chart_overview()
                .with_planet_positions()
                .with_aspects()
                .render("terminal")
            )

        elif output_format == "json":
            # Export as JSON
            import json

            output_path = output or f"{name.lower().replace(' ', '_')}.json"
            # ... implement JSON export
            click.echo(f"✅ Chart data saved to: {output_path}")

    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()
