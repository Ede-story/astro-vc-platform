"""
Planetary Dignities Reference Data

Complete reference for planetary states including:
- Exaltation signs and exact degrees
- Debilitation signs and exact degrees
- Moolatrikona ranges
- Own signs (rulerships)
- Sign lords
"""

from typing import Dict, List, Tuple, Optional
from ..models.types import Planet, Zodiac, Dignity


# =============================================================================
# EXALTATION - Signs where planets are at maximum strength
# =============================================================================

EXALTATION: Dict[Planet, Zodiac] = {
    Planet.SUN: Zodiac.ARIES,
    Planet.MOON: Zodiac.TAURUS,
    Planet.MARS: Zodiac.CAPRICORN,
    Planet.MERCURY: Zodiac.VIRGO,
    Planet.JUPITER: Zodiac.CANCER,
    Planet.VENUS: Zodiac.PISCES,
    Planet.SATURN: Zodiac.LIBRA,
    Planet.RAHU: Zodiac.GEMINI,       # Some texts: Taurus
    Planet.KETU: Zodiac.SAGITTARIUS,  # Some texts: Scorpio
}

# Exact degrees of exaltation (deep exaltation point)
EXALTATION_DEGREES: Dict[Planet, float] = {
    Planet.SUN: 10.0,      # Sun exalted at 10° Aries
    Planet.MOON: 3.0,      # Moon exalted at 3° Taurus
    Planet.MARS: 28.0,     # Mars exalted at 28° Capricorn
    Planet.MERCURY: 15.0,  # Mercury exalted at 15° Virgo
    Planet.JUPITER: 5.0,   # Jupiter exalted at 5° Cancer
    Planet.VENUS: 27.0,    # Venus exalted at 27° Pisces
    Planet.SATURN: 20.0,   # Saturn exalted at 20° Libra
    Planet.RAHU: 15.0,     # Rahu - approximate
    Planet.KETU: 15.0,     # Ketu - approximate
}


# =============================================================================
# DEBILITATION - Signs where planets are at minimum strength
# =============================================================================

DEBILITATION: Dict[Planet, Zodiac] = {
    Planet.SUN: Zodiac.LIBRA,
    Planet.MOON: Zodiac.SCORPIO,
    Planet.MARS: Zodiac.CANCER,
    Planet.MERCURY: Zodiac.PISCES,
    Planet.JUPITER: Zodiac.CAPRICORN,
    Planet.VENUS: Zodiac.VIRGO,
    Planet.SATURN: Zodiac.ARIES,
    Planet.RAHU: Zodiac.SAGITTARIUS,
    Planet.KETU: Zodiac.GEMINI,
}

# Exact degrees of debilitation (deep debilitation point)
DEBILITATION_DEGREES: Dict[Planet, float] = {
    Planet.SUN: 10.0,      # Sun debilitated at 10° Libra
    Planet.MOON: 3.0,      # Moon debilitated at 3° Scorpio
    Planet.MARS: 28.0,     # Mars debilitated at 28° Cancer
    Planet.MERCURY: 15.0,  # Mercury debilitated at 15° Pisces
    Planet.JUPITER: 5.0,   # Jupiter debilitated at 5° Capricorn
    Planet.VENUS: 27.0,    # Venus debilitated at 27° Virgo
    Planet.SATURN: 20.0,   # Saturn debilitated at 20° Aries
    Planet.RAHU: 15.0,
    Planet.KETU: 15.0,
}


# =============================================================================
# MOOLATRIKONA - Special powerful zones within own signs
# Format: (sign, start_degree, end_degree)
# =============================================================================

MOOLATRIKONA: Dict[Planet, Tuple[Zodiac, float, float]] = {
    Planet.SUN: (Zodiac.LEO, 0.0, 20.0),           # Leo 0-20°
    Planet.MOON: (Zodiac.TAURUS, 3.0, 30.0),       # Taurus 3-30°
    Planet.MARS: (Zodiac.ARIES, 0.0, 12.0),        # Aries 0-12°
    Planet.MERCURY: (Zodiac.VIRGO, 15.0, 20.0),    # Virgo 15-20°
    Planet.JUPITER: (Zodiac.SAGITTARIUS, 0.0, 10.0),  # Sagittarius 0-10°
    Planet.VENUS: (Zodiac.LIBRA, 0.0, 15.0),       # Libra 0-15°
    Planet.SATURN: (Zodiac.AQUARIUS, 0.0, 20.0),   # Aquarius 0-20°
    # Rahu/Ketu don't have traditional moolatrikona
}


# =============================================================================
# OWN SIGNS - Signs ruled by each planet
# =============================================================================

OWN_SIGNS: Dict[Planet, List[Zodiac]] = {
    Planet.SUN: [Zodiac.LEO],
    Planet.MOON: [Zodiac.CANCER],
    Planet.MARS: [Zodiac.ARIES, Zodiac.SCORPIO],
    Planet.MERCURY: [Zodiac.GEMINI, Zodiac.VIRGO],
    Planet.JUPITER: [Zodiac.SAGITTARIUS, Zodiac.PISCES],
    Planet.VENUS: [Zodiac.TAURUS, Zodiac.LIBRA],
    Planet.SATURN: [Zodiac.CAPRICORN, Zodiac.AQUARIUS],
    Planet.RAHU: [Zodiac.AQUARIUS],   # Co-ruler of Aquarius
    Planet.KETU: [Zodiac.SCORPIO],    # Co-ruler of Scorpio
}


# =============================================================================
# SIGN LORDS - Lord (ruler) of each sign
# =============================================================================

SIGN_LORDS: Dict[Zodiac, Planet] = {
    Zodiac.ARIES: Planet.MARS,
    Zodiac.TAURUS: Planet.VENUS,
    Zodiac.GEMINI: Planet.MERCURY,
    Zodiac.CANCER: Planet.MOON,
    Zodiac.LEO: Planet.SUN,
    Zodiac.VIRGO: Planet.MERCURY,
    Zodiac.LIBRA: Planet.VENUS,
    Zodiac.SCORPIO: Planet.MARS,      # Traditional; Ketu as co-ruler
    Zodiac.SAGITTARIUS: Planet.JUPITER,
    Zodiac.CAPRICORN: Planet.SATURN,
    Zodiac.AQUARIUS: Planet.SATURN,   # Traditional; Rahu as co-ruler
    Zodiac.PISCES: Planet.JUPITER,
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def is_exalted(planet: Planet, sign: Zodiac) -> bool:
    """Check if planet is in its exaltation sign"""
    return EXALTATION.get(planet) == sign


def is_debilitated(planet: Planet, sign: Zodiac) -> bool:
    """Check if planet is in its debilitation sign"""
    return DEBILITATION.get(planet) == sign


def is_in_own_sign(planet: Planet, sign: Zodiac) -> bool:
    """Check if planet is in one of its own signs"""
    return sign in OWN_SIGNS.get(planet, [])


def is_in_moolatrikona(planet: Planet, sign: Zodiac, degree: float) -> bool:
    """Check if planet is in moolatrikona zone"""
    mt_data = MOOLATRIKONA.get(planet)
    if mt_data is None:
        return False
    mt_sign, start_deg, end_deg = mt_data
    return sign == mt_sign and start_deg <= degree < end_deg


def get_sign_lord(sign: Zodiac) -> Planet:
    """Get the ruling planet of a sign"""
    return SIGN_LORDS[sign]


def get_dignity(
    planet: Planet,
    sign: Zodiac,
    degree: float,
    sign_lord_relationship: Optional[str] = None
) -> Dignity:
    """
    Determine the dignity state of a planet in a given sign.

    Priority order:
    1. Exaltation (highest)
    2. Moolatrikona
    3. Own Sign
    4. Based on relationship with sign lord (friend/neutral/enemy)
    5. Debilitation (lowest)

    Args:
        planet: The planet to check
        sign: The zodiac sign
        degree: Degree within sign (0-30)
        sign_lord_relationship: Optional pre-calculated relationship

    Returns:
        Dignity enum value
    """
    # Check debilitation first (can be cancelled by other factors)
    if is_debilitated(planet, sign):
        return Dignity.DEBILITATED

    # Check exaltation
    if is_exalted(planet, sign):
        return Dignity.EXALTED

    # Check moolatrikona (before own sign, as it's stronger)
    if is_in_moolatrikona(planet, sign, degree):
        return Dignity.MOOLATRIKONA

    # Check own sign
    if is_in_own_sign(planet, sign):
        return Dignity.OWN_SIGN

    # If relationship with sign lord is provided, use it
    if sign_lord_relationship:
        relationship_map = {
            "great_friend": Dignity.GREAT_FRIEND,
            "friend": Dignity.FRIEND,
            "neutral": Dignity.NEUTRAL,
            "enemy": Dignity.ENEMY,
            "great_enemy": Dignity.GREAT_ENEMY,
        }
        return relationship_map.get(sign_lord_relationship, Dignity.NEUTRAL)

    # Default to neutral if no other condition met
    return Dignity.NEUTRAL


def get_dignity_from_string(dignity_str: str) -> Dignity:
    """Convert string dignity to enum (handles various formats)"""
    mapping = {
        "exalted": Dignity.EXALTED,
        "moolatrikona": Dignity.MOOLATRIKONA,
        "own sign": Dignity.OWN_SIGN,
        "own": Dignity.OWN_SIGN,
        "great friend": Dignity.GREAT_FRIEND,
        "friend": Dignity.FRIEND,
        "neutral": Dignity.NEUTRAL,
        "enemy": Dignity.ENEMY,
        "great enemy": Dignity.GREAT_ENEMY,
        "debilitated": Dignity.DEBILITATED,
    }
    return mapping.get(dignity_str.lower(), Dignity.NEUTRAL)


def calculate_dignity_strength(dignity: Dignity) -> float:
    """
    Calculate strength multiplier based on dignity.

    Returns a value between 0.0 and 1.0 for use in strength calculations.
    """
    strength_map = {
        Dignity.EXALTED: 1.0,
        Dignity.MOOLATRIKONA: 0.875,
        Dignity.OWN_SIGN: 0.75,
        Dignity.GREAT_FRIEND: 0.625,
        Dignity.FRIEND: 0.5,
        Dignity.NEUTRAL: 0.375,
        Dignity.ENEMY: 0.25,
        Dignity.GREAT_ENEMY: 0.125,
        Dignity.DEBILITATED: 0.0,
    }
    return strength_map.get(dignity, 0.375)
