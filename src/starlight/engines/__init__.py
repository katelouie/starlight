"""
Calculation engines for ephemeris, houses, aspects, orbs, and dignities.

Common engines:
    >>> from starlight.engines import PlacidusHouses, WholeSignHouses
    >>> from starlight.engines import ModernAspectEngine, TraditionalAspectEngine
    >>> from starlight.engines import SimpleOrbEngine, LuminariesOrbEngine
"""

# Ephemeris
# Aspects
from starlight.engines.aspects import (
    HarmonicAspectEngine,
    ModernAspectEngine,
)

# Dignities
from starlight.engines.dignities import (
    ModernDignityCalculator,
    TraditionalDignityCalculator,
)
from starlight.engines.ephemeris import SwissEphemerisEngine

# House Systems
from starlight.engines.houses import (
    EqualHouses,
    KochHouses,
    PlacidusHouses,
    WholeSignHouses,
)

# Orbs
from starlight.engines.orbs import (
    ComplexOrbEngine,
    LuminariesOrbEngine,
    SimpleOrbEngine,
)

__all__ = [
    # Ephemeris
    "SwissEphemerisEngine",
    # Houses
    "PlacidusHouses",
    "WholeSignHouses",
    "KochHouses",
    "EqualHouses",
    # Aspects
    "ModernAspectEngine",
    "HarmonicAspectEngine",
    # Orbs
    "SimpleOrbEngine",
    "LuminariesOrbEngine",
    "ComplexOrbEngine",
    # Dignities
    "TraditionalDignityCalculator",
    "ModernDignityCalculator",
]
