"""
Reference Data for Astro Brain

Static astrological reference data including:
- Planetary dignities (exaltation, debilitation, own signs, moolatrikona)
- Natural friendships and enmities
- Sign lordships
- Nakshatra lords
- Yoga definitions
"""

from .dignities import (
    EXALTATION,
    EXALTATION_DEGREES,
    DEBILITATION,
    DEBILITATION_DEGREES,
    MOOLATRIKONA,
    OWN_SIGNS,
    SIGN_LORDS,
    get_dignity,
    is_in_own_sign,
    is_exalted,
    is_debilitated,
    is_in_moolatrikona,
)

from .friendships import (
    NATURAL_FRIENDS,
    NATURAL_ENEMIES,
    NATURAL_NEUTRALS,
    get_natural_relationship,
    get_temporal_relationship,
    get_compound_relationship,
)

__all__ = [
    # Dignities
    "EXALTATION",
    "EXALTATION_DEGREES",
    "DEBILITATION",
    "DEBILITATION_DEGREES",
    "MOOLATRIKONA",
    "OWN_SIGNS",
    "SIGN_LORDS",
    "get_dignity",
    "is_in_own_sign",
    "is_exalted",
    "is_debilitated",
    "is_in_moolatrikona",
    # Friendships
    "NATURAL_FRIENDS",
    "NATURAL_ENEMIES",
    "NATURAL_NEUTRALS",
    "get_natural_relationship",
    "get_temporal_relationship",
    "get_compound_relationship",
]
