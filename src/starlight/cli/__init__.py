"""Starlight command-line interface."""

import click

from starlight import __version__

# Import and register command groups
from starlight.cli.cache import cache_group
from starlight.cli.chart import chart_group
from starlight.cli.ephemeris import ephemeris_group


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    Starlight - Professional Astrology Library

    A comprehensive toolkit for astrological calculations,
    chart generation, and visualization.
    """
    pass


cli.add_command(cache_group)
cli.add_command(ephemeris_group)
cli.add_command(chart_group)

if __name__ == "__main__":
    cli()
