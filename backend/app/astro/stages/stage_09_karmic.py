"""
Stage 9: Karmic Depth (D30 Trimshamsha + D60 Shashtiamsha)

D30 Trimshamsha Chart:
- 30 divisions per sign (1° each)
- Shows: misfortunes, diseases, past-life karma, challenges
- THE risk indicator chart
- Malefics here = specific life challenges

D60 Shashtiamsha Chart:
- 60 divisions per sign (0.5° each)
- THE most subtle varga - shows past life
- Karmic ceiling indicator
- Overall auspiciousness of the chart
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from ..models.types import Planet, Zodiac, Dignity
from ..reference.doshas import (
    DoshaType, DoshaSeverity, DOSHA_CATALOG,
    MANGAL_DOSHA_HOUSES, MANGAL_CANCELLATION_SIGNS
)
from .varga_utils import (
    parse_varga_chart, VargaChartData, VargaPlanetData,
    get_sign_lord, is_benefic, is_malefic
)


class KarmicCeilingTier(str, Enum):
    """Karmic ceiling potential tiers."""
    UNLIMITED = "Unlimited"           # 27-30: $10B+ potential
    VERY_HIGH = "VeryHigh"            # 23-26: $1-10B potential
    HIGH = "High"                     # 19-22: $100M-1B potential
    MODERATE = "Moderate"             # 15-18: $10-100M potential
    LIMITED = "Limited"               # 11-14: $1-10M potential
    CONSTRAINED = "Constrained"       # 7-10: <$1M potential
    BLOCKED = "Blocked"               # 0-6: Severe karmic blocks


class RiskCategory(str, Enum):
    """Risk categories for investment."""
    VERY_LOW = "VeryLow"              # 0-2 risk severity
    LOW = "Low"                       # 2-4
    MODERATE = "Moderate"             # 4-6
    HIGH = "High"                     # 6-8
    CRITICAL = "Critical"             # 8-10


@dataclass
class DoshaResult:
    """Result of dosha detection."""
    dosha_type: DoshaType
    is_present: bool
    severity: float  # 1-10
    severity_level: DoshaSeverity
    cancellation_score: float  # 0-1 (how much cancelled)
    effective_severity: float  # After cancellation
    affected_areas: List[str]
    cancellation_factors: List[str]
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.dosha_type.value,
            "is_present": self.is_present,
            "severity": self.severity,
            "severity_level": self.severity_level.value,
            "cancellation_score": self.cancellation_score,
            "effective_severity": self.effective_severity,
            "affected_areas": self.affected_areas,
            "cancellation_factors": self.cancellation_factors,
            "description": self.description
        }


@dataclass
class D30Analysis:
    """D30 Trimshamsha analysis for risks."""
    malefics_strength: Dict[str, float]
    afflicted_houses: List[int]
    risk_areas: List[str]
    challenge_score: float  # 1-10 (higher = more challenges)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "malefics_strength": self.malefics_strength,
            "afflicted_houses": self.afflicted_houses,
            "risk_areas": self.risk_areas,
            "challenge_score": self.challenge_score
        }


@dataclass
class D60Analysis:
    """D60 Shashtiamsha analysis for karmic ceiling."""
    benefic_count: int
    malefic_count: int
    auspicious_divisions: int
    karmic_clarity: float  # 1-10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benefic_count": self.benefic_count,
            "malefic_count": self.malefic_count,
            "auspicious_divisions": self.auspicious_divisions,
            "karmic_clarity": self.karmic_clarity
        }


@dataclass
class Stage9Result:
    """Complete Stage 9 analysis result."""
    d30_analysis: D30Analysis
    d60_analysis: D60Analysis

    # Doshas
    doshas_detected: List[DoshaResult]
    total_dosha_count: int
    active_dosha_count: int  # After cancellations
    dosha_summary: Dict[str, Any]

    # Risk assessment
    risk_severity_index: float  # 1-10
    risk_category: RiskCategory
    red_flags: List[str]
    yellow_flags: List[str]
    green_flags: List[str]

    # Karmic assessment
    karmic_ceiling_score: int  # 0-30
    karmic_ceiling_tier: KarmicCeilingTier
    potential_tier: str  # "$1-10B", "$100M-1B", etc.

    # Indices
    indices: Dict[str, float] = field(default_factory=dict)

    # For house scoring
    house_adjustments: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "d30_analysis": self.d30_analysis.to_dict(),
            "d60_analysis": self.d60_analysis.to_dict(),
            "doshas": [d.to_dict() for d in self.doshas_detected],
            "total_dosha_count": self.total_dosha_count,
            "active_dosha_count": self.active_dosha_count,
            "dosha_summary": self.dosha_summary,
            "risk_severity_index": self.risk_severity_index,
            "risk_category": self.risk_category.value,
            "red_flags": self.red_flags,
            "yellow_flags": self.yellow_flags,
            "green_flags": self.green_flags,
            "karmic_ceiling_score": self.karmic_ceiling_score,
            "karmic_ceiling_tier": self.karmic_ceiling_tier.value,
            "potential_tier": self.potential_tier,
            "indices": self.indices,
            "house_adjustments": self.house_adjustments
        }


# D60 auspicious divisions (simplified)
AUSPICIOUS_D60_RANGES = [
    (0, 0.5), (1, 1.5), (2, 2.5), (3, 3.5), (4, 4.5),
    (10, 10.5), (11, 11.5), (12, 12.5),
    (20, 20.5), (21, 21.5), (22, 22.5), (23, 23.5),
]


def _get_planet_attr(planet: Any, key: str, default: Any = None) -> Any:
    """Get attribute from planet dict or dataclass object."""
    if hasattr(planet, 'get'):
        return planet.get(key, default)
    return getattr(planet, key, default)


def _get_house_from_signs(planet_sign: Zodiac, reference_sign: Zodiac) -> int:
    """Get house number of planet from reference sign."""
    planet_idx = list(Zodiac).index(planet_sign)
    ref_idx = list(Zodiac).index(reference_sign)
    house = ((planet_idx - ref_idx) % 12) + 1
    return house


def _get_jupiter_aspects(jupiter_house: int) -> List[int]:
    """Get houses Jupiter aspects (5th, 7th, 9th from itself)."""
    return [
        ((jupiter_house - 1 + 4) % 12) + 1,  # 5th
        ((jupiter_house - 1 + 6) % 12) + 1,  # 7th
        ((jupiter_house - 1 + 8) % 12) + 1,  # 9th
    ]


def _get_saturn_aspects(saturn_house: int) -> List[int]:
    """Get houses Saturn aspects (3rd, 7th, 10th from itself)."""
    return [
        ((saturn_house - 1 + 2) % 12) + 1,   # 3rd
        ((saturn_house - 1 + 6) % 12) + 1,   # 7th
        ((saturn_house - 1 + 9) % 12) + 1,   # 10th
    ]


def check_mangal_dosha(
    d1_planets: List[Dict[str, Any]],
    ascendant_sign: Zodiac
) -> DoshaResult:
    """
    Check for Mangal (Kuja) Dosha.

    Mars in houses 1,2,4,7,8,12 from Lagna, Moon, or Venus.
    """
    # Find Mars
    mars = None
    moon = None
    venus = None
    jupiter = None

    for p in d1_planets:
        name = _get_planet_attr(p, "name", "").upper()
        if name == "MARS":
            mars = p
        elif name == "MOON":
            moon = p
        elif name == "VENUS":
            venus = p
        elif name == "JUPITER":
            jupiter = p

    if not mars:
        return DoshaResult(
            dosha_type=DoshaType.MANGAL,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["Mars not found"],
            description="No Mangal Dosha"
        )

    mars_house = _get_planet_attr(mars, "house", _get_planet_attr(mars, "house", 1))
    mars_sign_name = _get_planet_attr(mars, "sign", _get_planet_attr(mars, "sign", "Aries"))
    mars_sign = Zodiac[mars_sign_name.upper()]

    # Get reference signs
    moon_sign_name = _get_planet_attr(moon, "sign", _get_planet_attr(moon, "sign", "Aries")) if moon else "Aries"
    venus_sign_name = _get_planet_attr(venus, "sign", _get_planet_attr(venus, "sign", "Aries")) if venus else "Aries"
    moon_sign = Zodiac[moon_sign_name.upper()]
    venus_sign = Zodiac[venus_sign_name.upper()]

    # Check from all three reference points
    mars_from_lagna = mars_house
    mars_from_moon = _get_house_from_signs(mars_sign, moon_sign)
    mars_from_venus = _get_house_from_signs(mars_sign, venus_sign)

    dosha_from_lagna = mars_from_lagna in MANGAL_DOSHA_HOUSES["from_lagna"]
    dosha_from_moon = mars_from_moon in MANGAL_DOSHA_HOUSES["from_moon"]
    dosha_from_venus = mars_from_venus in MANGAL_DOSHA_HOUSES["from_venus"]

    is_present = dosha_from_lagna or dosha_from_moon or dosha_from_venus

    if not is_present:
        return DoshaResult(
            dosha_type=DoshaType.MANGAL,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["Mars not in dosha houses"],
            description="No Mangal Dosha"
        )

    # Calculate severity
    count = sum([dosha_from_lagna, dosha_from_moon, dosha_from_venus])
    base_severity = DOSHA_CATALOG[DoshaType.MANGAL].base_severity
    severity = base_severity + (count - 1) * 0.5

    # Check cancellations
    cancellation_factors = []
    cancellation_score = 0.0

    # Mars in own sign
    if mars_sign in [Zodiac.ARIES, Zodiac.SCORPIO]:
        cancellation_score += 0.4
        cancellation_factors.append("Mars in own sign")

    # Mars exalted
    dignity = _get_planet_attr(mars, "dignity", "").lower()
    if "exalt" in dignity:
        cancellation_score += 0.5
        cancellation_factors.append("Mars exalted in Capricorn")

    # Sign-specific cancellations
    house_to_check = mars_from_lagna if dosha_from_lagna else mars_from_moon
    if house_to_check in MANGAL_CANCELLATION_SIGNS:
        if mars_sign in MANGAL_CANCELLATION_SIGNS[house_to_check]:
            cancellation_score += 0.3
            cancellation_factors.append(f"Mars in {mars_sign.value} cancels in house {house_to_check}")

    # Jupiter aspect
    if jupiter:
        jupiter_house = _get_planet_attr(jupiter, "house", 1)
        jupiter_aspects = _get_jupiter_aspects(jupiter_house)
        if mars_house in jupiter_aspects:
            cancellation_score += 0.4
            cancellation_factors.append("Jupiter aspects Mars")

    cancellation_score = min(1.0, cancellation_score)
    effective_severity = severity * (1 - cancellation_score)

    # Determine severity level
    if effective_severity <= 1:
        level = DoshaSeverity.CANCELLED
    elif effective_severity <= 3:
        level = DoshaSeverity.MINIMAL
    elif effective_severity <= 5:
        level = DoshaSeverity.LOW
    elif effective_severity <= 7:
        level = DoshaSeverity.MODERATE
    elif effective_severity <= 8.5:
        level = DoshaSeverity.HIGH
    else:
        level = DoshaSeverity.CRITICAL

    sources = []
    if dosha_from_lagna:
        sources.append("Lagna")
    if dosha_from_moon:
        sources.append("Moon")
    if dosha_from_venus:
        sources.append("Venus")

    return DoshaResult(
        dosha_type=DoshaType.MANGAL,
        is_present=True,
        severity=round(severity, 1),
        severity_level=level,
        cancellation_score=round(cancellation_score, 2),
        effective_severity=round(effective_severity, 1),
        affected_areas=DOSHA_CATALOG[DoshaType.MANGAL].affected_areas,
        cancellation_factors=cancellation_factors if cancellation_factors else ["No cancellations"],
        description=f"Mangal Dosha from {', '.join(sources)}"
    )


def check_kala_sarpa_dosha(d1_planets: List[Dict[str, Any]]) -> DoshaResult:
    """
    Check for Kala Sarpa Dosha.

    All 7 planets (excluding Rahu-Ketu) between Rahu and Ketu axis.
    """
    rahu = None
    ketu = None
    other_planets = []
    jupiter = None

    for p in d1_planets:
        name = _get_planet_attr(p, "name", "").upper()
        if name == "RAHU":
            rahu = p
        elif name == "KETU":
            ketu = p
        elif name == "JUPITER":
            jupiter = p
            other_planets.append(p)
        elif name not in ["RAHU", "KETU"]:
            other_planets.append(p)

    if not rahu or not ketu:
        return DoshaResult(
            dosha_type=DoshaType.KALA_SARPA,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["Nodes not found"],
            description="No Kala Sarpa Dosha"
        )

    rahu_house = _get_planet_attr(rahu, "house", 1)
    ketu_house = _get_planet_attr(ketu, "house", 7)

    def is_between_clockwise(house: int, start: int, end: int) -> bool:
        """Check if house is between start and end going clockwise."""
        if start <= end:
            return start < house < end
        else:
            return house > start or house < end

    planets_between_rahu_ketu = 0
    planets_between_ketu_rahu = 0

    for planet in other_planets:
        house = _get_planet_attr(planet, "house", 1)
        if is_between_clockwise(house, rahu_house, ketu_house):
            planets_between_rahu_ketu += 1
        else:
            planets_between_ketu_rahu += 1

    all_one_side = (planets_between_rahu_ketu == 0 or planets_between_ketu_rahu == 0)
    partial = (min(planets_between_rahu_ketu, planets_between_ketu_rahu) == 1)

    if not all_one_side and not partial:
        return DoshaResult(
            dosha_type=DoshaType.KALA_SARPA,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["Planets on both sides of axis"],
            description="No Kala Sarpa Dosha"
        )

    base_severity = DOSHA_CATALOG[DoshaType.KALA_SARPA].base_severity
    if partial:
        base_severity -= 2.0

    cancellation_factors = []
    cancellation_score = 0.0

    # Planet conjunct nodes
    for planet in other_planets:
        house = _get_planet_attr(planet, "house", 1)
        if house == rahu_house or house == ketu_house:
            cancellation_score += 0.3
            cancellation_factors.append(f"{_get_planet_attr(planet, 'name', None)} conjunct node")

    # Jupiter aspect
    if jupiter:
        jupiter_house = _get_planet_attr(jupiter, "house", 1)
        jupiter_aspects = _get_jupiter_aspects(jupiter_house)
        if rahu_house in jupiter_aspects or ketu_house in jupiter_aspects:
            cancellation_score += 0.3
            cancellation_factors.append("Jupiter aspects nodes")

    cancellation_score = min(1.0, cancellation_score)
    effective_severity = base_severity * (1 - cancellation_score)

    if effective_severity <= 1:
        level = DoshaSeverity.CANCELLED
    elif effective_severity <= 3:
        level = DoshaSeverity.LOW
    elif effective_severity <= 5:
        level = DoshaSeverity.MODERATE
    elif effective_severity <= 7:
        level = DoshaSeverity.HIGH
    else:
        level = DoshaSeverity.CRITICAL

    return DoshaResult(
        dosha_type=DoshaType.KALA_SARPA,
        is_present=True,
        severity=round(base_severity, 1),
        severity_level=level,
        cancellation_score=round(cancellation_score, 2),
        effective_severity=round(effective_severity, 1),
        affected_areas=DOSHA_CATALOG[DoshaType.KALA_SARPA].affected_areas,
        cancellation_factors=cancellation_factors if cancellation_factors else ["No cancellations"],
        description="Full Kala Sarpa" if all_one_side else "Partial Kala Sarpa"
    )


def check_guru_chandal_dosha(d1_planets: List[Dict[str, Any]]) -> DoshaResult:
    """
    Check for Guru Chandal Dosha.

    Jupiter conjunct Rahu (within same sign/house).
    """
    jupiter = None
    rahu = None
    saturn = None

    for p in d1_planets:
        name = _get_planet_attr(p, "name", "").upper()
        if name == "JUPITER":
            jupiter = p
        elif name == "RAHU":
            rahu = p
        elif name == "SATURN":
            saturn = p

    if not jupiter or not rahu:
        return DoshaResult(
            dosha_type=DoshaType.GURU_CHANDAL,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["Jupiter or Rahu not found"],
            description="No Guru Chandal Dosha"
        )

    jupiter_house = _get_planet_attr(jupiter, "house", 1)
    rahu_house = _get_planet_attr(rahu, "house", 1)
    jupiter_sign = _get_planet_attr(jupiter, "sign", "Aries")
    rahu_sign = _get_planet_attr(rahu, "sign", "Aries")

    is_conjunct = jupiter_house == rahu_house or jupiter_sign == rahu_sign

    if not is_conjunct:
        return DoshaResult(
            dosha_type=DoshaType.GURU_CHANDAL,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["Jupiter not conjunct Rahu"],
            description="No Guru Chandal Dosha"
        )

    base_severity = DOSHA_CATALOG[DoshaType.GURU_CHANDAL].base_severity

    cancellation_factors = []
    cancellation_score = 0.0

    # Jupiter in own/exalted sign
    dignity = _get_planet_attr(jupiter, "dignity", "").lower()
    if "own" in dignity or "exalt" in dignity:
        cancellation_score += 0.5
        cancellation_factors.append(f"Jupiter in {dignity}")

    # Saturn aspect
    if saturn:
        saturn_house = _get_planet_attr(saturn, "house", 1)
        saturn_aspects = _get_saturn_aspects(saturn_house)
        if jupiter_house in saturn_aspects:
            cancellation_score += 0.3
            cancellation_factors.append("Saturn aspects conjunction")

    cancellation_score = min(1.0, cancellation_score)
    effective_severity = base_severity * (1 - cancellation_score)

    if effective_severity <= 2:
        level = DoshaSeverity.MINIMAL
    elif effective_severity <= 4:
        level = DoshaSeverity.LOW
    elif effective_severity <= 5.5:
        level = DoshaSeverity.MODERATE
    else:
        level = DoshaSeverity.HIGH

    return DoshaResult(
        dosha_type=DoshaType.GURU_CHANDAL,
        is_present=True,
        severity=round(base_severity, 1),
        severity_level=level,
        cancellation_score=round(cancellation_score, 2),
        effective_severity=round(effective_severity, 1),
        affected_areas=DOSHA_CATALOG[DoshaType.GURU_CHANDAL].affected_areas,
        cancellation_factors=cancellation_factors if cancellation_factors else ["No cancellations"],
        description="Jupiter conjunct Rahu - corrupted wisdom"
    )


def check_pitru_dosha(d1_planets: List[Dict[str, Any]]) -> DoshaResult:
    """
    Check for Pitru Dosha.

    Sun afflicted by Saturn, Rahu, or Ketu (conjunction or aspect).
    """
    sun = None
    saturn = None
    rahu = None
    ketu = None
    jupiter = None

    for p in d1_planets:
        name = _get_planet_attr(p, "name", "").upper()
        if name == "SUN":
            sun = p
        elif name == "SATURN":
            saturn = p
        elif name == "RAHU":
            rahu = p
        elif name == "KETU":
            ketu = p
        elif name == "JUPITER":
            jupiter = p

    if not sun:
        return DoshaResult(
            dosha_type=DoshaType.PITRU,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["Sun not found"],
            description="No Pitru Dosha"
        )

    sun_house = _get_planet_attr(sun, "house", 1)
    afflictions = []

    # Check conjunctions
    if saturn and _get_planet_attr(saturn, "house", None) == sun_house:
        afflictions.append("Saturn conjunct Sun")
    if rahu and _get_planet_attr(rahu, "house", None) == sun_house:
        afflictions.append("Rahu conjunct Sun")
    if ketu and _get_planet_attr(ketu, "house", None) == sun_house:
        afflictions.append("Ketu conjunct Sun")

    # Check Saturn's aspects
    if saturn:
        saturn_house = _get_planet_attr(saturn, "house", 1)
        saturn_aspects = _get_saturn_aspects(saturn_house)
        if sun_house in saturn_aspects:
            afflictions.append("Saturn aspects Sun")

    if not afflictions:
        return DoshaResult(
            dosha_type=DoshaType.PITRU,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["Sun not afflicted"],
            description="No Pitru Dosha"
        )

    base_severity = DOSHA_CATALOG[DoshaType.PITRU].base_severity
    severity = base_severity + len(afflictions) * 0.5

    cancellation_factors = []
    cancellation_score = 0.0

    dignity = _get_planet_attr(sun, "dignity", "").lower()
    if "exalt" in dignity or "own" in dignity:
        cancellation_score += 0.5
        cancellation_factors.append(f"Sun in {dignity}")

    if jupiter:
        jupiter_house = _get_planet_attr(jupiter, "house", 1)
        jupiter_aspects = _get_jupiter_aspects(jupiter_house)
        if sun_house in jupiter_aspects:
            cancellation_score += 0.4
            cancellation_factors.append("Jupiter aspects Sun")

    cancellation_score = min(1.0, cancellation_score)
    effective_severity = severity * (1 - cancellation_score)

    if effective_severity <= 2:
        level = DoshaSeverity.MINIMAL
    elif effective_severity <= 4:
        level = DoshaSeverity.LOW
    elif effective_severity <= 6:
        level = DoshaSeverity.MODERATE
    else:
        level = DoshaSeverity.HIGH

    return DoshaResult(
        dosha_type=DoshaType.PITRU,
        is_present=True,
        severity=round(severity, 1),
        severity_level=level,
        cancellation_score=round(cancellation_score, 2),
        effective_severity=round(effective_severity, 1),
        affected_areas=DOSHA_CATALOG[DoshaType.PITRU].affected_areas,
        cancellation_factors=cancellation_factors if cancellation_factors else ["No cancellations"],
        description="; ".join(afflictions)
    )


def check_grahan_dosha(d1_planets: List[Dict[str, Any]]) -> DoshaResult:
    """
    Check for Grahan Dosha.

    Sun or Moon conjunct Rahu or Ketu.
    """
    sun = None
    moon = None
    rahu = None
    ketu = None
    jupiter = None

    for p in d1_planets:
        name = _get_planet_attr(p, "name", "").upper()
        if name == "SUN":
            sun = p
        elif name == "MOON":
            moon = p
        elif name == "RAHU":
            rahu = p
        elif name == "KETU":
            ketu = p
        elif name == "JUPITER":
            jupiter = p

    afflictions = []

    if sun and rahu:
        if _get_planet_attr(sun, "house", None) == _get_planet_attr(rahu, "house", None):
            afflictions.append("Sun-Rahu conjunction (Surya Grahan)")
    if sun and ketu:
        if _get_planet_attr(sun, "house", None) == _get_planet_attr(ketu, "house", None):
            afflictions.append("Sun-Ketu conjunction")
    if moon and rahu:
        if _get_planet_attr(moon, "house", None) == _get_planet_attr(rahu, "house", None):
            afflictions.append("Moon-Rahu conjunction (Chandra Grahan)")
    if moon and ketu:
        if _get_planet_attr(moon, "house", None) == _get_planet_attr(ketu, "house", None):
            afflictions.append("Moon-Ketu conjunction")

    if not afflictions:
        return DoshaResult(
            dosha_type=DoshaType.GRAHAN,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["No luminary-node conjunctions"],
            description="No Grahan Dosha"
        )

    base_severity = DOSHA_CATALOG[DoshaType.GRAHAN].base_severity
    severity = base_severity + (len(afflictions) - 1) * 1.0

    cancellation_factors = []
    cancellation_score = 0.0

    if jupiter:
        jupiter_house = _get_planet_attr(jupiter, "house", 1)
        jupiter_aspects = _get_jupiter_aspects(jupiter_house)

        afflicted_houses = set()
        if sun and rahu and _get_planet_attr(sun, "house", None) == _get_planet_attr(rahu, "house", None):
            afflicted_houses.add(_get_planet_attr(sun, "house", None))
        if moon and rahu and _get_planet_attr(moon, "house", None) == _get_planet_attr(rahu, "house", None):
            afflicted_houses.add(_get_planet_attr(moon, "house", None))

        for house in afflicted_houses:
            if house in jupiter_aspects or house == jupiter_house:
                cancellation_score += 0.4
                cancellation_factors.append("Jupiter aspects/conjuncts Grahan")
                break

    cancellation_score = min(1.0, cancellation_score)
    effective_severity = severity * (1 - cancellation_score)

    if effective_severity <= 2:
        level = DoshaSeverity.LOW
    elif effective_severity <= 5:
        level = DoshaSeverity.MODERATE
    elif effective_severity <= 7:
        level = DoshaSeverity.HIGH
    else:
        level = DoshaSeverity.CRITICAL

    return DoshaResult(
        dosha_type=DoshaType.GRAHAN,
        is_present=True,
        severity=round(severity, 1),
        severity_level=level,
        cancellation_score=round(cancellation_score, 2),
        effective_severity=round(effective_severity, 1),
        affected_areas=DOSHA_CATALOG[DoshaType.GRAHAN].affected_areas,
        cancellation_factors=cancellation_factors if cancellation_factors else ["No cancellations"],
        description="; ".join(afflictions)
    )


def check_shrapit_dosha(d1_planets: List[Dict[str, Any]]) -> DoshaResult:
    """
    Check for Shrapit Dosha.

    Saturn conjunct Rahu.
    """
    saturn = None
    rahu = None
    jupiter = None
    moon = None

    for p in d1_planets:
        name = _get_planet_attr(p, "name", "").upper()
        if name == "SATURN":
            saturn = p
        elif name == "RAHU":
            rahu = p
        elif name == "JUPITER":
            jupiter = p
        elif name == "MOON":
            moon = p

    if not saturn or not rahu:
        return DoshaResult(
            dosha_type=DoshaType.SHRAPIT,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["Saturn or Rahu not found"],
            description="No Shrapit Dosha"
        )

    saturn_house = _get_planet_attr(saturn, "house", 1)
    rahu_house = _get_planet_attr(rahu, "house", 1)

    if saturn_house != rahu_house:
        return DoshaResult(
            dosha_type=DoshaType.SHRAPIT,
            is_present=False,
            severity=0,
            severity_level=DoshaSeverity.CANCELLED,
            cancellation_score=1.0,
            effective_severity=0,
            affected_areas=[],
            cancellation_factors=["Saturn not conjunct Rahu"],
            description="No Shrapit Dosha"
        )

    base_severity = DOSHA_CATALOG[DoshaType.SHRAPIT].base_severity

    cancellation_factors = []
    cancellation_score = 0.0

    # Jupiter aspect
    if jupiter:
        jupiter_house = _get_planet_attr(jupiter, "house", 1)
        jupiter_aspects = _get_jupiter_aspects(jupiter_house)
        if saturn_house in jupiter_aspects:
            cancellation_score += 0.4
            cancellation_factors.append("Jupiter aspects conjunction")

    # In benefic house
    if saturn_house in [5, 9, 11]:
        cancellation_score += 0.2
        cancellation_factors.append(f"Conjunction in benefic house {saturn_house}")

    # Saturn in own/exalted
    dignity = _get_planet_attr(saturn, "dignity", "").lower()
    if "own" in dignity or "exalt" in dignity:
        cancellation_score += 0.3
        cancellation_factors.append(f"Saturn in {dignity}")

    cancellation_score = min(1.0, cancellation_score)
    effective_severity = base_severity * (1 - cancellation_score)

    if effective_severity <= 2:
        level = DoshaSeverity.LOW
    elif effective_severity <= 5:
        level = DoshaSeverity.MODERATE
    elif effective_severity <= 7:
        level = DoshaSeverity.HIGH
    else:
        level = DoshaSeverity.CRITICAL

    return DoshaResult(
        dosha_type=DoshaType.SHRAPIT,
        is_present=True,
        severity=round(base_severity, 1),
        severity_level=level,
        cancellation_score=round(cancellation_score, 2),
        effective_severity=round(effective_severity, 1),
        affected_areas=DOSHA_CATALOG[DoshaType.SHRAPIT].affected_areas,
        cancellation_factors=cancellation_factors if cancellation_factors else ["No cancellations"],
        description="Saturn conjunct Rahu - past-life curse"
    )


def analyze_d30(digital_twin: Dict[str, Any]) -> D30Analysis:
    """
    Analyze D30 Trimshamsha for risks and challenges.
    """
    d30 = parse_varga_chart(digital_twin, "D30")

    if d30 is None:
        return D30Analysis(
            malefics_strength={},
            afflicted_houses=[],
            risk_areas=[],
            challenge_score=5.0
        )

    malefic_planets = [Planet.MARS, Planet.SATURN, Planet.RAHU, Planet.KETU, Planet.SUN]
    malefic_strength: Dict[str, float] = {}

    for planet_data in d30.planets.values():
        if planet_data.planet in malefic_planets:
            strength = 5.0
            if planet_data.dignity == Dignity.DEBILITATED:
                strength += 2.0
            elif planet_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN, Dignity.MOOLATRIKONA]:
                strength -= 2.0
            if planet_data.house in [6, 8, 12]:
                strength += 1.0
            malefic_strength[planet_data.planet.value] = max(1.0, min(10.0, strength))

    afflicted = []
    for house in range(1, 13):
        occupants = d30.get_planets_in_house(house)
        if any(p in malefic_planets for p in occupants):
            afflicted.append(house)

    risk_areas = []
    house_meanings = {
        1: "health", 2: "wealth", 3: "courage", 4: "property",
        5: "children", 6: "enemies", 7: "partnership", 8: "longevity",
        9: "fortune", 10: "career", 11: "gains", 12: "losses"
    }
    for house in afflicted:
        risk_areas.append(house_meanings.get(house, f"house_{house}"))

    challenge = sum(malefic_strength.values()) / max(1, len(malefic_strength)) if malefic_strength else 5.0

    return D30Analysis(
        malefics_strength=malefic_strength,
        afflicted_houses=afflicted,
        risk_areas=risk_areas,
        challenge_score=round(challenge, 1)
    )


def analyze_d60(digital_twin: Dict[str, Any]) -> D60Analysis:
    """
    Analyze D60 Shashtiamsha for karmic ceiling.
    """
    d60 = parse_varga_chart(digital_twin, "D60")

    if d60 is None:
        return D60Analysis(
            benefic_count=0,
            malefic_count=0,
            auspicious_divisions=0,
            karmic_clarity=5.0
        )

    benefic_planets = [Planet.JUPITER, Planet.VENUS, Planet.MERCURY, Planet.MOON]
    malefic_planets = [Planet.MARS, Planet.SATURN, Planet.RAHU, Planet.KETU]

    benefic_count = len([p for p in d60.planets.values() if p.planet in benefic_planets and
                        p.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN, Dignity.FRIEND]])
    malefic_count = len([p for p in d60.planets.values() if p.planet in malefic_planets and
                        p.dignity in [Dignity.DEBILITATED, Dignity.ENEMY]])

    auspicious = 0
    for planet_data in d60.planets.values():
        degree_in_sign = planet_data.degree % 30
        for start, end in AUSPICIOUS_D60_RANGES:
            if start <= degree_in_sign <= end:
                auspicious += 1
                break

    clarity = 5.0 + benefic_count * 1.0 - malefic_count * 0.5 + auspicious * 0.3
    clarity = max(1.0, min(10.0, clarity))

    return D60Analysis(
        benefic_count=benefic_count,
        malefic_count=malefic_count,
        auspicious_divisions=auspicious,
        karmic_clarity=round(clarity, 1)
    )


def calculate_karmic_ceiling(
    d60_analysis: D60Analysis,
    d30_analysis: D30Analysis,
    doshas: List[DoshaResult],
    yoga_strength: float
) -> Tuple[int, KarmicCeilingTier, str]:
    """
    Calculate karmic ceiling score (0-30).
    """
    d60_score = d60_analysis.karmic_clarity
    yoga_score = min(10.0, yoga_strength)

    total_dosha_severity = sum(d.effective_severity for d in doshas if d.is_present)
    dosha_penalty = min(5.0, total_dosha_severity / 3)

    d30_adj = (5.0 - d30_analysis.challenge_score) * 0.4

    ceiling = d60_score + yoga_score - dosha_penalty + d30_adj
    ceiling = max(0, min(30, int(ceiling)))

    if ceiling >= 27:
        tier = KarmicCeilingTier.UNLIMITED
        potential = "$10B+"
    elif ceiling >= 23:
        tier = KarmicCeilingTier.VERY_HIGH
        potential = "$1-10B"
    elif ceiling >= 19:
        tier = KarmicCeilingTier.HIGH
        potential = "$100M-1B"
    elif ceiling >= 15:
        tier = KarmicCeilingTier.MODERATE
        potential = "$10-100M"
    elif ceiling >= 11:
        tier = KarmicCeilingTier.LIMITED
        potential = "$1-10M"
    elif ceiling >= 7:
        tier = KarmicCeilingTier.CONSTRAINED
        potential = "<$1M"
    else:
        tier = KarmicCeilingTier.BLOCKED
        potential = "Blocked"

    return ceiling, tier, potential


class Stage09KarmicAnalysis:
    """Stage 9: Karmic Depth analysis class."""

    def __init__(
        self,
        digital_twin: Dict[str, Any],
        d1_planets: List[Dict[str, Any]],
        house_lords: Dict[int, Dict[str, Any]],
        yoga_strength: float = 5.0
    ):
        self.digital_twin = digital_twin
        self.d1_planets = d1_planets
        self.house_lords = house_lords
        self.yoga_strength = yoga_strength

        vargas = digital_twin.get("vargas", {})
        d1 = vargas.get("D1", {})
        asc = d1.get("ascendant", {})
        self.ascendant_sign = Zodiac[asc.get("sign", "Aries").upper()]

    def analyze(self) -> Stage9Result:
        """Run complete Stage 9 analysis."""
        # Check all doshas
        doshas = [
            check_mangal_dosha(self.d1_planets, self.ascendant_sign),
            check_kala_sarpa_dosha(self.d1_planets),
            check_guru_chandal_dosha(self.d1_planets),
            check_pitru_dosha(self.d1_planets),
            check_grahan_dosha(self.d1_planets),
            check_shrapit_dosha(self.d1_planets),
        ]

        # Analyze D30 and D60
        d30 = analyze_d30(self.digital_twin)
        d60 = analyze_d60(self.digital_twin)

        # Count doshas
        total_count = len([d for d in doshas if d.is_present])
        active_count = len([d for d in doshas if d.is_present and d.effective_severity > 2])

        # Risk severity index
        total_severity = sum(d.effective_severity for d in doshas if d.is_present)
        risk_severity = total_severity / max(1, total_count) if total_count > 0 else 0
        risk_severity = min(10.0, risk_severity + d30.challenge_score * 0.2)

        # Risk category
        if risk_severity <= 2:
            risk_category = RiskCategory.VERY_LOW
        elif risk_severity <= 4:
            risk_category = RiskCategory.LOW
        elif risk_severity <= 6:
            risk_category = RiskCategory.MODERATE
        elif risk_severity <= 8:
            risk_category = RiskCategory.HIGH
        else:
            risk_category = RiskCategory.CRITICAL

        # Flags
        red_flags = []
        yellow_flags = []
        green_flags = []

        for dosha in doshas:
            if dosha.is_present:
                if dosha.effective_severity >= 7:
                    red_flags.append(f"{dosha.dosha_type.value}: {dosha.description}")
                elif dosha.effective_severity >= 4:
                    yellow_flags.append(f"{dosha.dosha_type.value}: {dosha.description}")
            if dosha.cancellation_score >= 0.7:
                green_flags.append(f"{dosha.dosha_type.value} largely cancelled")

        if d60.karmic_clarity >= 7:
            green_flags.append("High karmic clarity in D60")
        if d30.challenge_score <= 4:
            green_flags.append("Low challenge score in D30")

        # Karmic ceiling
        ceiling, tier, potential = calculate_karmic_ceiling(d60, d30, doshas, self.yoga_strength)

        # Dosha summary
        dosha_summary = {
            "mangal_present": any(d.dosha_type == DoshaType.MANGAL and d.is_present for d in doshas),
            "kala_sarpa_present": any(d.dosha_type == DoshaType.KALA_SARPA and d.is_present for d in doshas),
            "guru_chandal_present": any(d.dosha_type == DoshaType.GURU_CHANDAL and d.is_present for d in doshas),
            "pitru_present": any(d.dosha_type == DoshaType.PITRU and d.is_present for d in doshas),
            "grahan_present": any(d.dosha_type == DoshaType.GRAHAN and d.is_present for d in doshas),
            "shrapit_present": any(d.dosha_type == DoshaType.SHRAPIT and d.is_present for d in doshas),
            "total_active": active_count,
            "average_severity": round(risk_severity, 1),
        }

        # House adjustments
        house_adj = {}
        for house in d30.afflicted_houses:
            house_adj[f"house_{house}"] = -0.3 * (d30.challenge_score / 10)

        # Indices
        indices = {
            "risk_severity": round(risk_severity, 1),
            "karmic_clarity": d60.karmic_clarity,
            "challenge_score": d30.challenge_score,
            "karmic_ceiling": ceiling
        }

        return Stage9Result(
            d30_analysis=d30,
            d60_analysis=d60,
            doshas_detected=doshas,
            total_dosha_count=total_count,
            active_dosha_count=active_count,
            dosha_summary=dosha_summary,
            risk_severity_index=round(risk_severity, 1),
            risk_category=risk_category,
            red_flags=red_flags,
            yellow_flags=yellow_flags,
            green_flags=green_flags,
            karmic_ceiling_score=ceiling,
            karmic_ceiling_tier=tier,
            potential_tier=potential,
            indices=indices,
            house_adjustments=house_adj
        )
