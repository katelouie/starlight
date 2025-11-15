"""
Celestial Objects Registry

A comprehensive catalog of all celestial objects used in astrological calculations.
This centralizes metadata like names, glyphs, types, and descriptions for planets,
asteroids, nodes, points, fixed stars, and other celestial bodies.
"""

from dataclasses import dataclass, field
from typing import Any

from starlight.core.models import ObjectType


@dataclass(frozen=True)
class CelestialObjectInfo:
    """
    Complete metadata for a celestial object.

    This represents everything we know about an object - from its technical
    name and ephemeris ID to its glyph and human-readable description.
    """

    # Core Identity
    name: str  # Technical/internal name (e.g., "Mean Apogee", "True Node")
    display_name: str  # What users see (e.g., "Black Moon Lilith", "North Node")
    object_type: ObjectType  # PLANET, NODE, POINT, ASTEROID, etc.

    # Visual Representation
    glyph: str  # Unicode astrological glyph (e.g., "☽", "☊", "⚸")

    # Ephemeris/Calculation Data
    swiss_ephemeris_id: int | None = None  # Swiss Ephemeris object ID (if applicable)

    # Classification & Organization
    category: str | None = None  # "Traditional Planet", "Asteroid", "Centaur", "TNO", "Fixed Star", etc.
    aliases: list[str] = field(default_factory=list)  # Alternative names (e.g., ["Lilith", "BML"])

    # Documentation
    description: str = ""  # Brief explanation of what this object represents

    # Advanced/Optional Metadata
    metadata: dict[str, Any] = field(default_factory=dict)  # Extensible for future needs

    def __str__(self) -> str:
        return f"{self.display_name} ({self.name})"


# ============================================================================
# CELESTIAL OBJECTS REGISTRY
# ============================================================================

CELESTIAL_REGISTRY: dict[str, CelestialObjectInfo] = {
    # ========================================================================
    # TRADITIONAL PLANETS (The Septenary)
    # ========================================================================
    "Sun": CelestialObjectInfo(
        name="Sun",
        display_name="Sun",
        object_type=ObjectType.PLANET,
        glyph="☉",
        swiss_ephemeris_id=0,
        category="Traditional Planet",
        aliases=["Sol"],
        description="The luminary representing life force, vitality, ego, and conscious will.",
    ),
    "Moon": CelestialObjectInfo(
        name="Moon",
        display_name="Moon",
        object_type=ObjectType.PLANET,
        glyph="☽",
        swiss_ephemeris_id=1,
        category="Traditional Planet",
        aliases=["Luna"],
        description="The luminary representing emotions, instincts, habits, and the subconscious.",
    ),
    "Mercury": CelestialObjectInfo(
        name="Mercury",
        display_name="Mercury",
        object_type=ObjectType.PLANET,
        glyph="☿",
        swiss_ephemeris_id=2,
        category="Traditional Planet",
        description="The planet of communication, intellect, learning, and exchange.",
    ),
    "Venus": CelestialObjectInfo(
        name="Venus",
        display_name="Venus",
        object_type=ObjectType.PLANET,
        glyph="♀",
        swiss_ephemeris_id=3,
        category="Traditional Planet",
        description="The planet of love, beauty, harmony, values, and relationships.",
    ),
    "Mars": CelestialObjectInfo(
        name="Mars",
        display_name="Mars",
        object_type=ObjectType.PLANET,
        glyph="♂",
        swiss_ephemeris_id=4,
        category="Traditional Planet",
        description="The planet of action, desire, courage, assertion, and conflict.",
    ),
    "Jupiter": CelestialObjectInfo(
        name="Jupiter",
        display_name="Jupiter",
        object_type=ObjectType.PLANET,
        glyph="♃",
        swiss_ephemeris_id=5,
        category="Traditional Planet",
        description="The planet of expansion, growth, wisdom, fortune, and philosophy.",
    ),
    "Saturn": CelestialObjectInfo(
        name="Saturn",
        display_name="Saturn",
        object_type=ObjectType.PLANET,
        glyph="♄",
        swiss_ephemeris_id=6,
        category="Traditional Planet",
        description="The planet of structure, discipline, boundaries, responsibility, and time.",
    ),

    # ========================================================================
    # MODERN PLANETS (Outer Planets)
    # ========================================================================
    "Uranus": CelestialObjectInfo(
        name="Uranus",
        display_name="Uranus",
        object_type=ObjectType.PLANET,
        glyph="♅",
        swiss_ephemeris_id=7,
        category="Modern Planet",
        description="The planet of revolution, innovation, awakening, and sudden change.",
    ),
    "Neptune": CelestialObjectInfo(
        name="Neptune",
        display_name="Neptune",
        object_type=ObjectType.PLANET,
        glyph="♆",
        swiss_ephemeris_id=8,
        category="Modern Planet",
        description="The planet of dreams, illusion, spirituality, dissolution, and the unconscious.",
    ),
    "Pluto": CelestialObjectInfo(
        name="Pluto",
        display_name="Pluto",
        object_type=ObjectType.PLANET,
        glyph="♇",
        swiss_ephemeris_id=9,
        category="Modern Planet",
        description="The planet of transformation, power, death/rebirth, and the underworld.",
    ),

    # ========================================================================
    # LUNAR NODES
    # ========================================================================
    "True Node": CelestialObjectInfo(
        name="True Node",
        display_name="North Node",
        object_type=ObjectType.NODE,
        glyph="☊",
        swiss_ephemeris_id=11,
        category="Lunar Node",
        aliases=["North Node", "Dragon's Head", "Rahu"],
        description="The true (osculating) lunar north node - the Moon's ascending node, representing karmic direction and soul growth.",
    ),
    "Mean Node": CelestialObjectInfo(
        name="Mean Node",
        display_name="Mean North Node",
        object_type=ObjectType.NODE,
        glyph="☊",
        swiss_ephemeris_id=10,
        category="Lunar Node",
        aliases=["Mean North Node"],
        description="The mean lunar north node - averaged position of the Moon's ascending node.",
    ),
    "South Node": CelestialObjectInfo(
        name="South Node",
        display_name="South Node",
        object_type=ObjectType.NODE,
        glyph="☋",
        swiss_ephemeris_id=None,  # Calculated as opposite of North Node
        category="Lunar Node",
        aliases=["Dragon's Tail", "Ketu"],
        description="The lunar south node - opposite the North Node, representing past patterns and karmic release.",
    ),

    # ========================================================================
    # CALCULATED POINTS
    # ========================================================================
    "Mean Apogee": CelestialObjectInfo(
        name="Mean Apogee",
        display_name="Black Moon Lilith",
        object_type=ObjectType.POINT,
        glyph="⚸",
        swiss_ephemeris_id=12,
        category="Lunar Apogee",
        aliases=["Lilith", "BML", "Black Moon", "Mean Lilith"],
        description="The mean lunar apogee - the point where the Moon is farthest from Earth. Represents the wild, untamed feminine, shadow work, and rejection of patriarchal norms.",
    ),
    "True Apogee": CelestialObjectInfo(
        name="True Apogee",
        display_name="True Black Moon Lilith",
        object_type=ObjectType.POINT,
        glyph="⚸",
        swiss_ephemeris_id=13,
        category="Lunar Apogee",
        aliases=["True Lilith", "Osculating Lilith"],
        description="The true (osculating) lunar apogee - the actual, instantaneous farthest point of the Moon's orbit.",
    ),
    "Vertex": CelestialObjectInfo(
        name="Vertex",
        display_name="Vertex",
        object_type=ObjectType.POINT,
        glyph="Vx",
        swiss_ephemeris_id=-5,  # Calculated by swe.houses()
        category="Calculated Point",
        aliases=["Electric Ascendant"],
        description="A sensitive point on the western horizon, often associated with fated encounters and destined events.",
    ),

    # ========================================================================
    # ASTEROIDS (The "Big Four")
    # ========================================================================
    "Ceres": CelestialObjectInfo(
        name="Ceres",
        display_name="Ceres",
        object_type=ObjectType.ASTEROID,
        glyph="⚳",
        swiss_ephemeris_id=17,
        category="Main Belt Asteroid",
        description="The largest asteroid, representing nurturing, motherhood, agriculture, and sustenance.",
    ),
    "Pallas": CelestialObjectInfo(
        name="Pallas",
        display_name="Pallas Athena",
        object_type=ObjectType.ASTEROID,
        glyph="⚴",
        swiss_ephemeris_id=18,
        category="Main Belt Asteroid",
        aliases=["Pallas Athene"],
        description="The warrior asteroid representing wisdom, creative intelligence, and strategic thinking.",
    ),
    "Juno": CelestialObjectInfo(
        name="Juno",
        display_name="Juno",
        object_type=ObjectType.ASTEROID,
        glyph="⚵",
        swiss_ephemeris_id=19,
        category="Main Belt Asteroid",
        description="The asteroid of partnership, marriage, commitment, and power dynamics in relationships.",
    ),
    "Vesta": CelestialObjectInfo(
        name="Vesta",
        display_name="Vesta",
        object_type=ObjectType.ASTEROID,
        glyph="⚶",
        swiss_ephemeris_id=20,
        category="Main Belt Asteroid",
        description="The asteroid of the sacred flame, devotion, focus, and sexual integrity.",
    ),

    # ========================================================================
    # CENTAURS
    # ========================================================================
    "Chiron": CelestialObjectInfo(
        name="Chiron",
        display_name="Chiron",
        object_type=ObjectType.ASTEROID,  # Note: Often treated as honorary planet
        glyph="⚷",
        swiss_ephemeris_id=15,
        category="Centaur",
        aliases=["The Wounded Healer"],
        description="The wounded healer - represents deep wounds, healing journey, mentorship, and bridging worlds.",
    ),
    "Pholus": CelestialObjectInfo(
        name="Pholus",
        display_name="Pholus",
        object_type=ObjectType.ASTEROID,
        glyph="⬰",
        swiss_ephemeris_id=16,
        category="Centaur",
        description="Small cause, big effect - represents multigenerational patterns and catalyst events.",
    ),
    "Nessus": CelestialObjectInfo(
        name="Nessus",
        display_name="Nessus",
        object_type=ObjectType.ASTEROID,
        glyph="Nes",
        swiss_ephemeris_id=7066,
        category="Centaur",
        description="Represents abuse, boundaries violated, karmic consequences, and the poison that becomes medicine.",
    ),
    "Chariklo": CelestialObjectInfo(
        name="Chariklo",
        display_name="Chariklo",
        object_type=ObjectType.ASTEROID,
        glyph="Cha",
        swiss_ephemeris_id=10199,
        category="Centaur",
        description="Chiron's wife - represents compassionate healing, devotion, and grounding spiritual wisdom.",
    ),

    # ========================================================================
    # TRANS-NEPTUNIAN OBJECTS (TNOs)
    # ========================================================================
    "Eris": CelestialObjectInfo(
        name="Eris",
        display_name="Eris",
        object_type=ObjectType.ASTEROID,
        glyph="⯰",
        swiss_ephemeris_id=136199,
        category="Dwarf Planet (TNO)",
        aliases=["Xena"],
        description="The dwarf planet of discord, rivalry, and fierce feminine power. Larger than Pluto.",
    ),
    "Sedna": CelestialObjectInfo(
        name="Sedna",
        display_name="Sedna",
        object_type=ObjectType.ASTEROID,
        glyph="Sed",
        swiss_ephemeris_id=90377,
        category="Trans-Neptunian Object",
        description="Represents deep cold, isolation, victim consciousness, and the slow thaw of healing.",
    ),
    "Makemake": CelestialObjectInfo(
        name="Makemake",
        display_name="Makemake",
        object_type=ObjectType.ASTEROID,
        glyph="🝼",
        swiss_ephemeris_id=136472,
        category="Dwarf Planet (TNO)",
        description="Represents environmental awareness, resourcefulness, and manifestation.",
    ),
    "Haumea": CelestialObjectInfo(
        name="Haumea",
        display_name="Haumea",
        object_type=ObjectType.ASTEROID,
        glyph="🝻",
        swiss_ephemeris_id=136108,
        category="Dwarf Planet (TNO)",
        description="Represents rebirth, fertility, connection to nature, and rapid transformation.",
    ),
    "Orcus": CelestialObjectInfo(
        name="Orcus",
        display_name="Orcus",
        object_type=ObjectType.ASTEROID,
        glyph="Orc",
        swiss_ephemeris_id=90482,
        category="Trans-Neptunian Object",
        aliases=["Anti-Pluto"],
        description="The anti-Pluto - represents oaths, consequences, and the afterlife.",
    ),
    "Quaoar": CelestialObjectInfo(
        name="Quaoar",
        display_name="Quaoar",
        object_type=ObjectType.ASTEROID,
        glyph="Qua",
        swiss_ephemeris_id=50000,
        category="Trans-Neptunian Object",
        description="Represents creation myths, harmony, and finding order in chaos.",
    ),

    # ========================================================================
    # URANIAN / HAMBURG SCHOOL PLANETS
    # ========================================================================
    "Cupido": CelestialObjectInfo(
        name="Cupido",
        display_name="Cupido",
        object_type=ObjectType.ASTEROID,
        glyph="Cup",
        swiss_ephemeris_id=40,
        category="Uranian Planet",
        description="Hypothetical planet representing family, groups, art, and community.",
    ),
    "Hades": CelestialObjectInfo(
        name="Hades",
        display_name="Hades",
        object_type=ObjectType.ASTEROID,
        glyph="Had",
        swiss_ephemeris_id=41,
        category="Uranian Planet",
        description="Hypothetical planet representing decay, the past, poverty, and what's hidden.",
    ),
    "Zeus": CelestialObjectInfo(
        name="Zeus",
        display_name="Zeus",
        object_type=ObjectType.ASTEROID,
        glyph="Zeu",
        swiss_ephemeris_id=42,
        category="Uranian Planet",
        description="Hypothetical planet representing leadership, fire, machines, and directed energy.",
    ),
    "Kronos": CelestialObjectInfo(
        name="Kronos",
        display_name="Kronos",
        object_type=ObjectType.ASTEROID,
        glyph="Kro",
        swiss_ephemeris_id=43,
        category="Uranian Planet",
        description="Hypothetical planet representing authority, expertise, and high position.",
    ),
    "Apollon": CelestialObjectInfo(
        name="Apollon",
        display_name="Apollon",
        object_type=ObjectType.ASTEROID,
        glyph="Apo",
        swiss_ephemeris_id=44,
        category="Uranian Planet",
        description="Hypothetical planet representing expansion, science, commerce, and success.",
    ),
    "Admetos": CelestialObjectInfo(
        name="Admetos",
        display_name="Admetos",
        object_type=ObjectType.ASTEROID,
        glyph="Adm",
        swiss_ephemeris_id=45,
        category="Uranian Planet",
        description="Hypothetical planet representing depth, stagnation, raw materials, and the earth.",
    ),
    "Vulkanus": CelestialObjectInfo(
        name="Vulkanus",
        display_name="Vulkanus",
        object_type=ObjectType.ASTEROID,
        glyph="Vul",
        swiss_ephemeris_id=46,
        category="Uranian Planet",
        aliases=["Vulcanus"],
        description="Hypothetical planet representing immense power, force, and intensity.",
    ),
    "Poseidon": CelestialObjectInfo(
        name="Poseidon",
        display_name="Poseidon",
        object_type=ObjectType.ASTEROID,
        glyph="Pos",
        swiss_ephemeris_id=47,
        category="Uranian Planet",
        description="Hypothetical planet representing spirituality, enlightenment, and clarity.",
    ),

    # ========================================================================
    # FIXED STARS (Selected Notable Stars)
    # ========================================================================
    "Algol": CelestialObjectInfo(
        name="Algol",
        display_name="Algol",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,  # Fixed stars calculated differently
        category="Fixed Star",
        aliases=["Beta Persei", "The Demon Star"],
        description="The most infamous fixed star - represents the Medusa's head, transformation through crisis, and facing the shadow.",
        metadata={"constellation": "Perseus", "magnitude": 2.1, "approx_longitude_2000": 26.0},  # ~26° Taurus
    ),
    "Regulus": CelestialObjectInfo(
        name="Regulus",
        display_name="Regulus",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Leonis", "The Heart of the Lion"],
        description="Royal star representing glory, success, nobility, and leadership. One of the four Royal Stars of Persia.",
        metadata={"constellation": "Leo", "magnitude": 1.4, "approx_longitude_2000": 29.5},  # ~29° Leo
    ),
    "Spica": CelestialObjectInfo(
        name="Spica",
        display_name="Spica",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Virginis"],
        description="The gift of the harvest - represents talent, brilliance, protection, and divine favor. One of the four Royal Stars.",
        metadata={"constellation": "Virgo", "magnitude": 1.0, "approx_longitude_2000": 23.5},  # ~23° Libra
    ),
    "Antares": CelestialObjectInfo(
        name="Antares",
        display_name="Antares",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Scorpii", "The Rival of Mars"],
        description="The heart of the Scorpion - represents courage, obsession, confrontation, and intensity. One of the four Royal Stars.",
        metadata={"constellation": "Scorpius", "magnitude": 1.0, "approx_longitude_2000": 9.5},  # ~9° Sagittarius
    ),
    "Aldebaran": CelestialObjectInfo(
        name="Aldebaran",
        display_name="Aldebaran",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Tauri", "The Eye of the Bull"],
        description="The follower of the Pleiades - represents integrity, eloquence, courage, and the warrior spirit. One of the four Royal Stars.",
        metadata={"constellation": "Taurus", "magnitude": 0.9, "approx_longitude_2000": 9.5},  # ~9° Gemini
    ),
    "Fomalhaut": CelestialObjectInfo(
        name="Fomalhaut",
        display_name="Fomalhaut",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Piscis Austrini"],
        description="The mouth of the fish - represents idealism, utopianism, and the fall from grace. One of the four Royal Stars.",
        metadata={"constellation": "Piscis Austrinus", "magnitude": 1.2, "approx_longitude_2000": 3.5},  # ~3° Pisces
    ),
    "Sirius": CelestialObjectInfo(
        name="Sirius",
        display_name="Sirius",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Canis Majoris", "The Dog Star"],
        description="The brightest star in the sky - represents fame, honor, devotion, passion, and the guardianship of the sacred.",
        metadata={"constellation": "Canis Major", "magnitude": -1.5, "approx_longitude_2000": 14.0},  # ~14° Cancer
    ),
    "Pleiades": CelestialObjectInfo(
        name="Pleiades",
        display_name="Pleiades",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["The Seven Sisters", "M45"],
        description="The weeping sisters - represents ambition, brilliance, love of learning, but also sorrow and loss.",
        metadata={"constellation": "Taurus", "magnitude": 1.6, "approx_longitude_2000": 0.0},  # ~0° Gemini
    ),

    # ========================================================================
    # OTHER NOTABLE POINTS/BODIES
    # ========================================================================
    "Earth": CelestialObjectInfo(
        name="Earth",
        display_name="Earth",
        object_type=ObjectType.PLANET,
        glyph="♁",
        swiss_ephemeris_id=14,
        category="Planet",
        description="Our home planet. Rarely used in geocentric charts but relevant in heliocentric calculations.",
    ),
}


# ============================================================================
# REGISTRY HELPER FUNCTIONS
# ============================================================================

def get_object_info(name: str) -> CelestialObjectInfo | None:
    """
    Get celestial object info by name.

    Args:
        name: The technical name of the object (e.g., "Mean Apogee", "Sun")

    Returns:
        CelestialObjectInfo if found, None otherwise
    """
    return CELESTIAL_REGISTRY.get(name)


def get_by_alias(alias: str) -> CelestialObjectInfo | None:
    """
    Get celestial object info by any of its aliases.

    Args:
        alias: An alias for the object (e.g., "Lilith", "BML", "North Node")

    Returns:
        CelestialObjectInfo if found, None otherwise
    """
    alias_lower = alias.lower()

    for obj_info in CELESTIAL_REGISTRY.values():
        # Check if alias matches any of the object's aliases
        if any(a.lower() == alias_lower for a in obj_info.aliases):
            return obj_info
        # Also check display name
        if obj_info.display_name.lower() == alias_lower:
            return obj_info

    return None


def get_all_by_type(object_type: ObjectType) -> list[CelestialObjectInfo]:
    """
    Get all celestial objects of a specific type.

    Args:
        object_type: The ObjectType to filter by

    Returns:
        List of CelestialObjectInfo matching the type
    """
    return [
        obj_info
        for obj_info in CELESTIAL_REGISTRY.values()
        if obj_info.object_type == object_type
    ]


def get_all_by_category(category: str) -> list[CelestialObjectInfo]:
    """
    Get all celestial objects in a specific category.

    Args:
        category: The category to filter by (e.g., "Centaur", "Fixed Star")

    Returns:
        List of CelestialObjectInfo matching the category
    """
    return [
        obj_info
        for obj_info in CELESTIAL_REGISTRY.values()
        if obj_info.category == category
    ]


def search_objects(query: str) -> list[CelestialObjectInfo]:
    """
    Search for objects by name, display name, alias, or description.

    Args:
        query: Search string (case-insensitive)

    Returns:
        List of matching CelestialObjectInfo objects
    """
    query_lower = query.lower()
    results = []

    for obj_info in CELESTIAL_REGISTRY.values():
        # Check name, display name
        if query_lower in obj_info.name.lower() or query_lower in obj_info.display_name.lower():
            results.append(obj_info)
            continue

        # Check aliases
        if any(query_lower in alias.lower() for alias in obj_info.aliases):
            results.append(obj_info)
            continue

        # Check description
        if query_lower in obj_info.description.lower():
            results.append(obj_info)

    return results
