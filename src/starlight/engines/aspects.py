"""
Aspect calculation engines.

These engines are responsible for finding angular relationships (aspects)
between celestial objects. They follow the `AspectEngine` protocol.
"""

from itertools import combinations

from starlight.core.config import AspectConfig
from starlight.core.models import Aspect, CelestialPosition, ObjectType
from starlight.core.protocols import OrbEngine
from starlight.core.registry import get_aspect_by_alias, get_aspect_info

# --- Helper Functions (Shared Logic) ---


def _angular_distance(long1: float, long2: float) -> float:
    """Calculate shortest angular distance between two longitudes."""
    diff = abs(long1 - long2)
    if diff > 180:
        diff = 360 - diff
    return diff


def _is_applying(
    obj1: CelestialPosition,
    obj2: CelestialPosition,
    aspect_angle: float,
    current_distance: float,
) -> bool | None:
    """
    Determine if aspect is applying or separating.
    An aspect is "applying" if the planets are moving *toward*
    the exact aspect angle.

    Returns:
        True if applying, False if separating, None if speed is unknown.
    """
    # Need speed data for both objects
    if obj1.speed_longitude == 0 or obj2.speed_longitude == 0:
        return None

    # Use a 1-minute interval.
    # This is (1 day / 24 hours / 60 minutes)
    interval_fraction = 1.0 / (24.0 * 60.0)

    # Calculate where they'll be in one minute
    future_long1 = (obj1.longitude + (obj1.speed_longitude * interval_fraction)) % 360
    future_long2 = (obj2.longitude + (obj2.speed_longitude * interval_fraction)) % 360
    future_distance = _angular_distance(future_long1, future_long2)

    # Calculate the orb (distance from exactness) now and in one minute
    current_orb = abs(current_distance - aspect_angle)
    future_orb = abs(future_distance - aspect_angle)

    # Applying = the future orb is smaller than the current orb
    # This check is now safe from the "crossover" bug because
    # the interval is too small to cross and return an equal
    # absolute value.
    return future_orb < current_orb


class ModernAspectEngine:
    """
    Calculates standard aspects (conjunction, square, trine, etc.)
    based on a provided AspectConfig.
    """

    def __init__(self, config: AspectConfig | None = None):
        """
        Initialize the engine.

        Args:
            config: An AspectConfig object defining which aspect angles
                    and object types to use. If None, a default
                    AspectConfig is created.
        """
        self._config = config or AspectConfig()

    def calculate_aspects(
        self, positions: list[CelestialPosition], orb_engine: OrbEngine
    ) -> list[Aspect]:
        """
        Calculate aspects based on the engine's config and the provided orb engine.

        Args:
            positions: The list of CelestialPosition objects to check.
            orb_engine: The OrbEngine that will provide the orb allowance
                        for each potential aspect.

        Returns:
            A list of found Aspect objects.
        """
        aspects = []

        # 1. Filter the list of positions based on our config
        valid_types = {ObjectType.PLANET, ObjectType.NODE, ObjectType.POINT}
        if self._config.include_angles:
            valid_types.add(ObjectType.ANGLE)
        if self._config.include_asteroids:
            valid_types.add(ObjectType.ASTEROID)

        valid_objects = [p for p in positions if p.object_type in valid_types]

        # 2. Iterate over every unique pair of objects
        for obj1, obj2 in combinations(valid_objects, 2):
            distance = _angular_distance(obj1.longitude, obj2.longitude)

            # 3. Check against each aspect in our config
            for aspect_name in self._config.aspects:
                # Look up the aspect angle from the registry
                aspect_info = get_aspect_info(aspect_name)
                if not aspect_info:
                    # Try as alias
                    aspect_info = get_aspect_by_alias(aspect_name)

                if not aspect_info:
                    # Skip unknown aspects
                    continue

                aspect_angle = aspect_info.angle
                actual_orb = abs(distance - aspect_angle)

                # 4. Ask the OrbEngine for the allowance
                orb_allowance = orb_engine.get_orb_allowance(obj1, obj2, aspect_name)

                # 5. If it's a match, create the Aspect object
                if actual_orb <= orb_allowance:
                    is_applying = _is_applying(obj1, obj2, aspect_angle, distance)

                    aspect = Aspect(
                        object1=obj1,
                        object2=obj2,
                        aspect_name=aspect_name,
                        aspect_degree=aspect_angle,
                        orb=actual_orb,
                        is_applying=is_applying,
                    )
                    aspects.append(aspect)

                    # Only one aspect per pair
                    break

        return aspects


class HarmonicAspectEngine:
    """
    Calculates harmonic aspects (eg H5, H7, H9).
    This engine does *not* use AspectConfig, as it defines its own angles.
    It *does* use the OrbEngine, which can be configured to give different orbs
    for different harmonics.
    """

    def __init__(self, harmonic: int) -> None:
        """
        Initialize the harmonic engine.

        Args:
            harmonic: The harmonic number (eg. 7 for septiles)
        """
        if harmonic <= 1:
            raise ValueError("Harmonic must be greater than 1.")

        self.harmonic = harmonic
        self.aspect_name = f"H{harmonic}"

        # Generate the aspect angles for this harmonic
        # e.g., H7 = [51.42, 102.85, 154.28]
        # We skip the 0/360 conjunction
        base_angle = 360.0 / harmonic
        self.aspect_angles = [(i * base_angle) for i in range(1, harmonic // 2 + 1)]

    def calculate_aspects(
        self, positions: list[CelestialPosition], orb_engine: OrbEngine
    ) -> list[Aspect]:
        """
        Calculate harmonic aspects for the configured harmonic number.

        Currently only calculates between ObjectType=Planet objects.

        Args:
            positions: The list of CelestialPositions objects to check.
            orb_engine: The OrbEngine that will provide the orb allowance.

        Returns:
            A list of found Aspect objects.
        """
        aspects = []

        # Harmonics are typically only calculated between planets
        valid_objects = [p for p in positions if p.object_type == ObjectType.PLANET]

        for obj1, obj2 in combinations(valid_objects, 2):
            distance = _angular_distance(obj1.longitude, obj2.longitude)

            # Check against each harmonic angle (e.g., 51.4, 102.8 for H7)
            for aspect_angle in self.aspect_angles:
                actual_orb = abs(distance - aspect_angle)

                # Ask the OrbEngine for allowance for "H7", etc.
                orb_allowance = orb_engine.get_orb_allowance(
                    obj1, obj2, self.aspect_name
                )

                if actual_orb <= orb_allowance:
                    is_applying = _is_applying(obj1, obj2, aspect_angle, distance)

                    aspect = Aspect(
                        object1=obj1,
                        object2=obj2,
                        aspect_name=self.aspect_name,
                        aspect_degree=round(aspect_angle),
                        orb=actual_orb,
                        is_applying=is_applying,
                    )
                    aspects.append(aspect)

                    # Only use one harmonic aspect per pair
                    break

        return aspects
