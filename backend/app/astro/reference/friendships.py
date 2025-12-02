"""
Planetary Friendships Reference Data

Natural (Naisargika) and Temporal (Tatkalika) planetary relationships.
Used for calculating compound relationships and dignity states.
"""

from typing import Dict, List, Set, Optional
from ..models.types import Planet, Zodiac, House


# =============================================================================
# NATURAL FRIENDSHIPS (Naisargika Mitra)
# These are permanent, based on inherent planetary nature
# =============================================================================

NATURAL_FRIENDS: Dict[Planet, List[Planet]] = {
    Planet.SUN: [Planet.MOON, Planet.MARS, Planet.JUPITER],
    Planet.MOON: [Planet.SUN, Planet.MERCURY],
    Planet.MARS: [Planet.SUN, Planet.MOON, Planet.JUPITER],
    Planet.MERCURY: [Planet.SUN, Planet.VENUS],
    Planet.JUPITER: [Planet.SUN, Planet.MOON, Planet.MARS],
    Planet.VENUS: [Planet.MERCURY, Planet.SATURN],
    Planet.SATURN: [Planet.MERCURY, Planet.VENUS],
    # Nodes follow their depositor's relationships (simplified)
    Planet.RAHU: [Planet.MERCURY, Planet.VENUS, Planet.SATURN],
    Planet.KETU: [Planet.SUN, Planet.MOON, Planet.MARS, Planet.JUPITER],
}

NATURAL_ENEMIES: Dict[Planet, List[Planet]] = {
    Planet.SUN: [Planet.SATURN, Planet.VENUS],
    Planet.MOON: [],  # Moon has no natural enemies
    Planet.MARS: [Planet.MERCURY],
    Planet.MERCURY: [Planet.MOON],
    Planet.JUPITER: [Planet.MERCURY, Planet.VENUS],
    Planet.VENUS: [Planet.SUN, Planet.MOON],
    Planet.SATURN: [Planet.SUN, Planet.MOON, Planet.MARS],
    # Nodes
    Planet.RAHU: [Planet.SUN, Planet.MOON, Planet.MARS],
    Planet.KETU: [Planet.MERCURY, Planet.VENUS],
}

# Neutral = planets that are neither friends nor enemies
NATURAL_NEUTRALS: Dict[Planet, List[Planet]] = {
    Planet.SUN: [Planet.MERCURY],
    Planet.MOON: [Planet.MARS, Planet.JUPITER, Planet.VENUS, Planet.SATURN],
    Planet.MARS: [Planet.VENUS, Planet.SATURN],
    Planet.MERCURY: [Planet.MARS, Planet.JUPITER, Planet.SATURN],
    Planet.JUPITER: [Planet.SATURN],
    Planet.VENUS: [Planet.MARS, Planet.JUPITER],
    Planet.SATURN: [Planet.JUPITER],
    Planet.RAHU: [Planet.JUPITER],
    Planet.KETU: [Planet.SATURN],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_natural_relationship(planet1: Planet, planet2: Planet) -> str:
    """
    Get the natural (permanent) relationship between two planets.

    Returns:
        "friend", "enemy", or "neutral"
    """
    if planet2 in NATURAL_FRIENDS.get(planet1, []):
        return "friend"
    elif planet2 in NATURAL_ENEMIES.get(planet1, []):
        return "enemy"
    else:
        return "neutral"


def get_temporal_relationship(
    planet: Planet,
    planet_house: int,
    other_planet: Planet,
    other_planet_house: int
) -> str:
    """
    Get the temporal (chart-specific) relationship between two planets.

    Based on house positions:
    - If other planet is in 2, 3, 4, 10, 11, or 12 from planet = temporal friend
    - If other planet is in 1, 5, 6, 7, 8, or 9 from planet = temporal enemy

    Args:
        planet: The planet whose perspective we're taking
        planet_house: House number (1-12) where planet is placed
        other_planet: The other planet
        other_planet_house: House number where other planet is placed

    Returns:
        "friend" or "enemy"
    """
    # Calculate house distance (1-12)
    distance = ((other_planet_house - planet_house) % 12) + 1

    # Houses 2, 3, 4, 10, 11, 12 = temporal friend
    if distance in [2, 3, 4, 10, 11, 12]:
        return "friend"
    else:
        return "enemy"


def get_compound_relationship(
    natural_rel: str,
    temporal_rel: str
) -> str:
    """
    Calculate compound (Panchadha) relationship from natural + temporal.

    Combination rules:
    - Friend + Friend = Great Friend (Adhi Mitra)
    - Friend + Enemy = Neutral (Sama)
    - Neutral + Friend = Friend (Mitra)
    - Neutral + Enemy = Enemy (Shatru)
    - Enemy + Friend = Neutral (Sama)
    - Enemy + Enemy = Great Enemy (Adhi Shatru)

    Returns:
        "great_friend", "friend", "neutral", "enemy", or "great_enemy"
    """
    compound_matrix = {
        ("friend", "friend"): "great_friend",
        ("friend", "enemy"): "neutral",
        ("neutral", "friend"): "friend",
        ("neutral", "enemy"): "enemy",
        ("enemy", "friend"): "neutral",
        ("enemy", "enemy"): "great_enemy",
    }

    return compound_matrix.get((natural_rel, temporal_rel), "neutral")


def calculate_all_temporal_relationships(
    planet_houses: Dict[Planet, int]
) -> Dict[Planet, Dict[Planet, str]]:
    """
    Calculate all temporal relationships for a chart.

    Args:
        planet_houses: Dictionary mapping planets to their house positions (1-12)

    Returns:
        Nested dict: {planet1: {planet2: "friend"/"enemy", ...}, ...}
    """
    relationships: Dict[Planet, Dict[Planet, str]] = {}

    for planet in Planet:
        if planet not in planet_houses:
            continue

        relationships[planet] = {}
        for other_planet in Planet:
            if other_planet not in planet_houses or planet == other_planet:
                continue

            rel = get_temporal_relationship(
                planet,
                planet_houses[planet],
                other_planet,
                planet_houses[other_planet]
            )
            relationships[planet][other_planet] = rel

    return relationships


def calculate_all_compound_relationships(
    planet_houses: Dict[Planet, int]
) -> Dict[Planet, Dict[Planet, str]]:
    """
    Calculate all compound relationships for a chart.

    Args:
        planet_houses: Dictionary mapping planets to their house positions (1-12)

    Returns:
        Nested dict: {planet1: {planet2: "great_friend"/"friend"/etc, ...}, ...}
    """
    temporal = calculate_all_temporal_relationships(planet_houses)
    compound: Dict[Planet, Dict[Planet, str]] = {}

    for planet in Planet:
        if planet not in planet_houses:
            continue

        compound[planet] = {}
        for other_planet in Planet:
            if other_planet not in planet_houses or planet == other_planet:
                continue

            natural_rel = get_natural_relationship(planet, other_planet)
            temporal_rel = temporal.get(planet, {}).get(other_planet, "neutral")
            compound[planet][other_planet] = get_compound_relationship(
                natural_rel, temporal_rel
            )

    return compound


def get_relationship_with_sign_lord(
    planet: Planet,
    sign: Zodiac,
    planet_houses: Optional[Dict[Planet, int]] = None
) -> str:
    """
    Get the relationship between a planet and the lord of a sign.

    If planet_houses is provided, uses compound relationship.
    Otherwise, uses natural relationship only.

    Args:
        planet: The planet
        sign: The sign where planet is placed
        planet_houses: Optional dict of all planet positions

    Returns:
        Relationship string
    """
    from .dignities import SIGN_LORDS

    sign_lord = SIGN_LORDS[sign]

    # Planet in its own sign
    if planet == sign_lord:
        return "own"

    if planet_houses:
        # Use compound relationship
        temporal = calculate_all_temporal_relationships(planet_houses)
        natural_rel = get_natural_relationship(planet, sign_lord)
        temporal_rel = temporal.get(planet, {}).get(sign_lord, "neutral")
        return get_compound_relationship(natural_rel, temporal_rel)
    else:
        # Use natural relationship only
        return get_natural_relationship(planet, sign_lord)
