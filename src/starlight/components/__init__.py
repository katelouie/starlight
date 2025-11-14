"""
Component system for optional chart calculations.

Components calculate additional objects based on:
- Chart datetime/location
- Already-calculated planetary positions
- House cusps

They return CelestialPosition (or metadata) objects that integrate seamlessly
with the rest of the chart.
"""

from starlight.core.protocols import ChartComponent

__all__ = ["ChartComponent"]
