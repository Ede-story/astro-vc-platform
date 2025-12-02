"""
Dosha (affliction) definitions and detection rules.

Doshas are planetary afflictions that create challenges.
Critical for risk assessment in investment decisions.
"""
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

from ..models.types import Planet, Zodiac


class DoshaType(str, Enum):
    """Types of doshas."""
    MANGAL = "MangalDosha"           # Mars in 1,4,7,8,12 from Lagna/Moon/Venus
    KALA_SARPA = "KalaSarpaDosha"    # All planets between Rahu-Ketu
    GURU_CHANDAL = "GuruChandalDosha" # Jupiter conjunct Rahu
    PITRU = "PitruDosha"             # Sun afflicted by Saturn/Rahu/Ketu
    GRAHAN = "GrahanDosha"           # Sun/Moon conjunct Rahu/Ketu
    SHRAPIT = "ShrapitDosha"         # Saturn conjunct Rahu
    KEMADRUM = "KemadrumDosha"       # No planets 2nd/12th from Moon
    DARIDRA = "DaridraDosha"         # 11th lord in dusthana


class DoshaSeverity(str, Enum):
    """Severity level of dosha."""
    CRITICAL = "Critical"     # 9-10 severity
    HIGH = "High"             # 7-8
    MODERATE = "Moderate"     # 5-6
    LOW = "Low"               # 3-4
    MINIMAL = "Minimal"       # 1-2
    CANCELLED = "Cancelled"   # Dosha cancelled by other factors


@dataclass
class DoshaDefinition:
    """Definition of a dosha."""
    name: str
    dosha_type: DoshaType
    description: str
    affected_areas: List[str]
    base_severity: float  # 1-10
    cancellation_rules: List[str]
    remedies: List[str]


# Dosha catalog
DOSHA_CATALOG: Dict[DoshaType, DoshaDefinition] = {
    DoshaType.MANGAL: DoshaDefinition(
        name="Mangal Dosha (Kuja Dosha)",
        dosha_type=DoshaType.MANGAL,
        description="Mars in houses 1,2,4,7,8,12 from Lagna, Moon, or Venus creates aggressive energy affecting relationships and partnerships.",
        affected_areas=["marriage", "partnerships", "business_partners", "co-founders", "health"],
        base_severity=7.0,
        cancellation_rules=[
            "Mars in own sign (Aries, Scorpio)",
            "Mars in exaltation (Capricorn)",
            "Jupiter aspects Mars",
            "Both partners have Mangal Dosha",
            "Mars in 2nd house in Gemini/Virgo",
            "Mars in 4th in Aries/Scorpio",
            "Mars in 7th in Cancer/Capricorn",
            "Mars in 8th in Sagittarius/Pisces",
            "Mars in 12th in Taurus/Libra",
            "Person is born on Tuesday"
        ],
        remedies=["Kumbh Vivah", "Mangal mantra", "Red coral gemstone", "Hanuman worship"]
    ),

    DoshaType.KALA_SARPA: DoshaDefinition(
        name="Kala Sarpa Dosha",
        dosha_type=DoshaType.KALA_SARPA,
        description="All planets hemmed between Rahu and Ketu axis creates karmic restrictions and sudden ups/downs.",
        affected_areas=["sudden_changes", "career_instability", "mental_peace", "obstacles", "delays"],
        base_severity=8.0,
        cancellation_rules=[
            "Any planet conjunct Rahu or Ketu",
            "Jupiter aspects Rahu or Ketu",
            "Moon is waxing (Shukla Paksha)",
            "Benefic in Kendra from Rahu",
            "Partial Kala Sarpa (one planet outside)"
        ],
        remedies=["Rahu-Ketu puja", "Naag panchami worship", "Donation of black items"]
    ),

    DoshaType.GURU_CHANDAL: DoshaDefinition(
        name="Guru Chandal Dosha",
        dosha_type=DoshaType.GURU_CHANDAL,
        description="Jupiter conjunct Rahu corrupts wisdom and judgment, leads to unethical shortcuts.",
        affected_areas=["judgment", "ethics", "education", "children", "mentorship", "investments"],
        base_severity=6.5,
        cancellation_rules=[
            "Jupiter in own sign (Sagittarius, Pisces)",
            "Jupiter in exaltation (Cancer)",
            "Jupiter aspects from benefic house",
            "Saturn aspects the conjunction",
            "Moon is strong and aspects"
        ],
        remedies=["Jupiter mantra", "Yellow sapphire", "Guru puja on Thursday", "Feeding Brahmins"]
    ),

    DoshaType.PITRU: DoshaDefinition(
        name="Pitru Dosha",
        dosha_type=DoshaType.PITRU,
        description="Sun afflicted by Saturn, Rahu, or Ketu indicates ancestral karmic debt affecting authority and recognition.",
        affected_areas=["father", "authority", "government", "recognition", "career_blocks", "leadership"],
        base_severity=6.0,
        cancellation_rules=[
            "Sun in exaltation (Aries)",
            "Sun in own sign (Leo)",
            "Jupiter aspects Sun",
            "Sun in Kendra from strong Moon"
        ],
        remedies=["Surya mantra", "Ruby gemstone", "Pinda daan", "Shraddha rituals"]
    ),

    DoshaType.GRAHAN: DoshaDefinition(
        name="Grahan Dosha",
        dosha_type=DoshaType.GRAHAN,
        description="Sun or Moon conjunct Rahu/Ketu (eclipse points) creates confusion, identity issues, and health problems.",
        affected_areas=["identity", "health", "mental_clarity", "mother_father", "confidence"],
        base_severity=7.5,
        cancellation_rules=[
            "Jupiter aspects the conjunction",
            "Luminaries in own/exalted sign",
            "Nodes in benefic signs",
            "Born after actual eclipse"
        ],
        remedies=["Chandra/Surya mantra", "Pearl/Ruby gemstone", "Fasting on eclipse days"]
    ),

    DoshaType.SHRAPIT: DoshaDefinition(
        name="Shrapit Dosha",
        dosha_type=DoshaType.SHRAPIT,
        description="Saturn conjunct Rahu indicates past-life curses, chronic delays and suffering.",
        affected_areas=["delays", "chronic_issues", "karma", "obstacles", "depression"],
        base_severity=8.5,
        cancellation_rules=[
            "Jupiter aspects the conjunction",
            "In benefic house (5, 9, 11)",
            "Saturn in own/exalted sign",
            "Moon strong and aspecting"
        ],
        remedies=["Saturn-Rahu shanti", "Hanuman worship", "Saturday fasting", "Black sesame donation"]
    ),

    DoshaType.KEMADRUM: DoshaDefinition(
        name="Kemadrum Dosha",
        dosha_type=DoshaType.KEMADRUM,
        description="No planets in 2nd or 12th from Moon creates emotional isolation and poverty despite potential.",
        affected_areas=["wealth", "emotional_support", "loneliness", "instability"],
        base_severity=5.0,
        cancellation_rules=[
            "Jupiter aspects Moon",
            "Venus aspects Moon",
            "Moon in Kendra from Lagna",
            "Moon in own/exalted sign",
            "Planets in Kendra from Moon",
            "Full Moon (Purnima)"
        ],
        remedies=["Moon mantra", "Pearl gemstone", "White offerings on Monday"]
    ),

    DoshaType.DARIDRA: DoshaDefinition(
        name="Daridra Dosha",
        dosha_type=DoshaType.DARIDRA,
        description="11th lord in 6th, 8th, or 12th house blocks income realization despite earning potential.",
        affected_areas=["income", "profit_realization", "gains", "networks"],
        base_severity=6.0,
        cancellation_rules=[
            "11th lord in own/exalted sign",
            "Jupiter aspects 11th lord",
            "Strong 11th house in D11",
            "Benefics in 11th house"
        ],
        remedies=["Lakshmi mantra", "Yellow sapphire", "Donation on Thursday"]
    ),
}


# Mangal Dosha specific houses from different references
MANGAL_DOSHA_HOUSES = {
    "from_lagna": [1, 2, 4, 7, 8, 12],
    "from_moon": [1, 2, 4, 7, 8, 12],
    "from_venus": [1, 2, 4, 7, 8, 12],
}

# Cancellation signs for Mars in specific houses
MANGAL_CANCELLATION_SIGNS: Dict[int, List[Zodiac]] = {
    1: [Zodiac.ARIES, Zodiac.LEO, Zodiac.SCORPIO, Zodiac.CAPRICORN, Zodiac.AQUARIUS],
    2: [Zodiac.GEMINI, Zodiac.VIRGO],
    4: [Zodiac.ARIES, Zodiac.SCORPIO],
    7: [Zodiac.CANCER, Zodiac.CAPRICORN],
    8: [Zodiac.SAGITTARIUS, Zodiac.PISCES, Zodiac.AQUARIUS],
    12: [Zodiac.TAURUS, Zodiac.LIBRA],
}
