"""
Component system for optional chart calculations.

Components calculate additional objects based on:
- Chart datetime/location
- Already-calculated planetary positions
- House cusps

They return CelestialPosition (or metadata) objects that integrate seamlessly
with the rest of the chart.
"""

from starlight.components.arabic_parts import ArabicPartsCalculator
from starlight.components.dignity import (
    AccidentalDignityComponent,
    DignityComponent,
)
from starlight.components.midpoints import MidpointCalculator
from starlight.core.protocols import ChartComponent

__all__ = [
    # Protocol
    "ChartComponent",
    # Components
    "ArabicPartsCalculator",
    "MidpointCalculator",
    "DignityComponent",
    "AccidentalDignityComponent",
]
