"""
Stage 3: Yoga Analysis

Detects all active yogas in the chart and calculates:
- Which yogas are present
- Strength of each yoga (with modifiers)
- Neecha Bhanga Raja Yoga (8 rules)
- Overall yoga score
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from ..models.types import (
    Planet, Zodiac, Dignity, ZODIAC_ORDER,
    KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES
)
from ..reference.dignities import (
    get_dignity, SIGN_LORDS, EXALTATION, DEBILITATION, OWN_SIGNS
)
from ..reference.yogas_catalog import (
    YogaDefinition, YogaCategory, ALL_YOGAS,
    YOGA_BY_NAME, get_yoga_definition
)


class CancellationLevel(str, Enum):
    """Level of Neecha Bhanga (debilitation cancellation)."""
    NONE = "None"
    WEAK = "Weak"
    MODERATE = "Moderate"
    STRONG = "Strong"
    RAJA_YOGA = "RajaYoga"


@dataclass
class YogaResult:
    """Result of yoga detection."""
    name: str
    sanskrit_name: str
    category: YogaCategory
    is_active: bool
    strength: float
    base_strength: float
    modifiers: List[Dict[str, Any]]
    participating_planets: List[Planet]
    affected_houses: List[int]
    interpretation_key: str
    timing_activation: Optional[str] = None


@dataclass
class NeechaBhangaResult:
    """Result of Neecha Bhanga analysis."""
    planet: Planet
    debilitation_sign: Zodiac
    house: int
    degree: float
    rules_satisfied: List[int]
    rule_details: List[Dict[str, Any]]
    total_restoration_score: float
    cancellation_level: CancellationLevel
    house_score_modifier: float
    effective_dignity: str


@dataclass
class YogaSummary:
    """Summary of all yogas in the chart."""
    total_count: int
    positive_count: int
    negative_count: int
    total_strength: float
    positive_strength: float
    negative_strength: float
    raja_yoga_count: int
    raja_yoga_strength: float
    dhana_yoga_count: int
    dhana_yoga_strength: float
    mahapurusha_yogas: List[str]
    key_yogas: List[str]
    overall_yoga_score: float


@dataclass
class Stage3Result:
    """Complete Stage 3 analysis result."""
    yogas: List[YogaResult]
    neecha_bhanga: Dict[str, NeechaBhangaResult]
    yoga_summary: YogaSummary
    house_yoga_bonuses: Dict[str, float]


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_planet_enum(p) -> Planet:
    """Get Planet enum from either PlanetSummary or object with planet attribute."""
    if hasattr(p, 'planet'):
        result = p.planet
        if isinstance(result, Planet):
            return result
        return Planet.from_string(str(result))
    elif hasattr(p, 'name'):
        return Planet.from_string(p.name)
    return Planet.SUN


def get_sign_enum(p) -> Zodiac:
    """Get Zodiac enum from either PlanetSummary or object with sign attribute."""
    if hasattr(p, 'sign_zodiac'):
        return p.sign_zodiac
    elif hasattr(p, 'sign'):
        result = p.sign
        if isinstance(result, Zodiac):
            return result
        return Zodiac.from_string(str(result))
    return Zodiac.ARIES


def get_dignity_enum(p) -> Dignity:
    """Get Dignity enum from object."""
    from ..reference.dignities import get_dignity_from_string
    if hasattr(p, 'dignity_enum'):
        return p.dignity_enum
    elif hasattr(p, 'dignity'):
        result = p.dignity
        if isinstance(result, Dignity):
            return result
        return get_dignity_from_string(str(result))
    return Dignity.NEUTRAL


def get_house_from_sign(planet_sign: Zodiac, ascendant_sign: Zodiac) -> int:
    """Calculate house number from sign relative to ascendant."""
    asc_index = ZODIAC_ORDER.index(ascendant_sign)
    planet_index = ZODIAC_ORDER.index(planet_sign)
    house = ((planet_index - asc_index) % 12) + 1
    return house


def planets_in_kendra_from(
    reference_sign: Zodiac,
    planets: List[Any]
) -> List[Any]:
    """Get planets in Kendra (1,4,7,10) from a reference sign."""
    result = []
    ref_index = ZODIAC_ORDER.index(reference_sign)

    for planet in planets:
        sign = get_sign_enum(planet)
        planet_index = ZODIAC_ORDER.index(sign)
        distance = (planet_index - ref_index) % 12
        if distance in [0, 3, 6, 9]:
            result.append(planet)

    return result


def has_conjunction(
    planet1: Planet,
    planet2: Planet,
    planets: List[Any]
) -> bool:
    """Check if two planets are in conjunction (same sign)."""
    p1 = next((p for p in planets if get_planet_enum(p) == planet1), None)
    p2 = next((p for p in planets if get_planet_enum(p) == planet2), None)

    if p1 and p2:
        return get_sign_enum(p1) == get_sign_enum(p2)
    return False


def get_planet_position(planet: Planet, planets: List[Any]) -> Optional[Any]:
    """Get position of a specific planet."""
    return next((p for p in planets if get_planet_enum(p) == planet), None)


def get_house(p) -> int:
    """Get house number from planet object."""
    return getattr(p, 'house', 1)


def get_degree(p) -> float:
    """Get degree from planet object."""
    return getattr(p, 'degree', 15.0)


def get_house_lord(house: int, ascendant: Zodiac) -> Planet:
    """Get the lord of a house based on ascendant."""
    asc_index = ZODIAC_ORDER.index(ascendant)
    house_sign_index = (asc_index + house - 1) % 12
    house_sign = ZODIAC_ORDER[house_sign_index]
    return SIGN_LORDS[house_sign]


# ============================================
# YOGA DETECTION FUNCTIONS
# ============================================

def check_gaja_kesari(
    planets: List[Any],
    ascendant: Zodiac
) -> Optional[YogaResult]:
    """Gaja Kesari Yoga: Jupiter in Kendra from Moon."""
    moon = get_planet_position(Planet.MOON, planets)
    jupiter = get_planet_position(Planet.JUPITER, planets)

    if not moon or not jupiter:
        return None

    moon_sign = get_sign_enum(moon)
    moon_kendras = planets_in_kendra_from(moon_sign, planets)
    jupiter_in_kendra = jupiter in moon_kendras

    if not jupiter_in_kendra:
        return None

    yoga_def = get_yoga_definition("Gaja Kesari Yoga")
    strength = yoga_def.base_strength
    modifiers = []

    jupiter_dignity = get_dignity_enum(jupiter)
    if jupiter_dignity == Dignity.EXALTED:
        strength += 1.5
        modifiers.append({"description": "Jupiter exalted", "effect": 1.5})
    elif jupiter_dignity == Dignity.OWN_SIGN:
        strength += 1.0
        modifiers.append({"description": "Jupiter in own sign", "effect": 1.0})
    elif jupiter_dignity == Dignity.DEBILITATED:
        strength -= 1.5
        modifiers.append({"description": "Jupiter debilitated", "effect": -1.5})

    if hasattr(jupiter, 'is_combust') and jupiter.is_combust:
        strength -= 1.0
        modifiers.append({"description": "Jupiter combust", "effect": -1.0})

    strength = max(1.0, min(10.0, strength))

    return YogaResult(
        name=yoga_def.name,
        sanskrit_name=yoga_def.sanskrit_name,
        category=yoga_def.category,
        is_active=True,
        strength=strength,
        base_strength=yoga_def.base_strength,
        modifiers=modifiers,
        participating_planets=[Planet.JUPITER, Planet.MOON],
        affected_houses=yoga_def.affected_houses,
        interpretation_key=yoga_def.interpretation_key,
        timing_activation="Jupiter or Moon dasha"
    )


def check_mahapurusha_yoga(
    planet: Planet,
    planets: List[Any],
    ascendant: Zodiac,
    yoga_name: str
) -> Optional[YogaResult]:
    """Check Mahapurusha yoga for a planet."""
    planet_pos = get_planet_position(planet, planets)
    if not planet_pos:
        return None

    planet_dignity = get_dignity_enum(planet_pos)
    planet_house = get_house(planet_pos)

    if planet_dignity not in [Dignity.EXALTED, Dignity.OWN_SIGN, Dignity.MOOLATRIKONA]:
        return None

    if planet_house not in KENDRA_HOUSES:
        return None

    yoga_def = get_yoga_definition(yoga_name)
    if not yoga_def:
        return None

    strength = yoga_def.base_strength
    modifiers = []

    if planet_dignity == Dignity.EXALTED:
        strength += 1.0
        modifiers.append({"description": f"{planet.value} exalted", "effect": 1.0})

    if planet_house == 1:
        strength += 0.5
        modifiers.append({"description": "In 1st house", "effect": 0.5})
    elif planet_house == 10:
        strength += 0.5
        modifiers.append({"description": "In 10th house", "effect": 0.5})

    if hasattr(planet_pos, 'is_retrograde') and planet_pos.is_retrograde:
        strength += 0.25
        modifiers.append({"description": "Retrograde", "effect": 0.25})

    strength = max(1.0, min(10.0, strength))

    return YogaResult(
        name=yoga_def.name,
        sanskrit_name=yoga_def.sanskrit_name,
        category=yoga_def.category,
        is_active=True,
        strength=strength,
        base_strength=yoga_def.base_strength,
        modifiers=modifiers,
        participating_planets=[planet],
        affected_houses=yoga_def.affected_houses,
        interpretation_key=yoga_def.interpretation_key,
        timing_activation=f"{planet.value} dasha"
    )


def check_budhaditya(
    planets: List[Any],
    ascendant: Zodiac
) -> Optional[YogaResult]:
    """Budhaditya Yoga: Sun-Mercury conjunction."""
    if not has_conjunction(Planet.SUN, Planet.MERCURY, planets):
        return None

    sun = get_planet_position(Planet.SUN, planets)
    mercury = get_planet_position(Planet.MERCURY, planets)

    yoga_def = get_yoga_definition("Budhaditya Yoga")
    strength = yoga_def.base_strength
    modifiers = []

    if sun and mercury:
        degree_diff = abs(get_degree(sun) - get_degree(mercury))
        if degree_diff < 3:
            strength -= 1.0
            modifiers.append({"description": "Mercury too close to Sun", "effect": -1.0})

        if get_house(sun) in KENDRA_HOUSES:
            strength += 0.5
            modifiers.append({"description": "In Kendra", "effect": 0.5})

        mercury_dignity = get_dignity_enum(mercury)
        if mercury_dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
            strength += 0.75
            modifiers.append({"description": "Mercury strong", "effect": 0.75})

    strength = max(1.0, min(10.0, strength))

    return YogaResult(
        name=yoga_def.name,
        sanskrit_name=yoga_def.sanskrit_name,
        category=yoga_def.category,
        is_active=True,
        strength=strength,
        base_strength=yoga_def.base_strength,
        modifiers=modifiers,
        participating_planets=[Planet.SUN, Planet.MERCURY],
        affected_houses=yoga_def.affected_houses,
        interpretation_key=yoga_def.interpretation_key,
        timing_activation="Sun or Mercury dasha"
    )


def check_chandra_mangal(
    planets: List[Any],
    ascendant: Zodiac
) -> Optional[YogaResult]:
    """Chandra-Mangal Yoga: Moon-Mars conjunction."""
    if not has_conjunction(Planet.MOON, Planet.MARS, planets):
        return None

    yoga_def = get_yoga_definition("Chandra-Mangal Yoga")
    strength = yoga_def.base_strength
    modifiers = []

    moon = get_planet_position(Planet.MOON, planets)
    mars = get_planet_position(Planet.MARS, planets)

    if moon and mars:
        if get_house(moon) in [2, 4, 10, 11]:
            strength += 0.5
            modifiers.append({"description": "In wealth house", "effect": 0.5})

    return YogaResult(
        name=yoga_def.name,
        sanskrit_name=yoga_def.sanskrit_name,
        category=yoga_def.category,
        is_active=True,
        strength=strength,
        base_strength=yoga_def.base_strength,
        modifiers=modifiers,
        participating_planets=[Planet.MOON, Planet.MARS],
        affected_houses=yoga_def.affected_houses,
        interpretation_key=yoga_def.interpretation_key,
        timing_activation="Moon or Mars dasha"
    )


def check_kemadruma(
    planets: List[Any],
    ascendant: Zodiac
) -> Optional[YogaResult]:
    """Kemadruma Yoga (Negative): No planets in 2nd or 12th from Moon."""
    moon = get_planet_position(Planet.MOON, planets)
    if not moon:
        return None

    moon_sign = get_sign_enum(moon)
    moon_index = ZODIAC_ORDER.index(moon_sign)
    second_sign = ZODIAC_ORDER[(moon_index + 1) % 12]
    twelfth_sign = ZODIAC_ORDER[(moon_index - 1) % 12]

    planets_nearby = False
    for planet in planets:
        planet_enum = get_planet_enum(planet)
        if planet_enum in [Planet.MOON, Planet.SUN, Planet.RAHU, Planet.KETU]:
            continue
        planet_sign = get_sign_enum(planet)
        if planet_sign in [second_sign, twelfth_sign]:
            planets_nearby = True
            break

    if planets_nearby:
        return None

    yoga_def = get_yoga_definition("Kemadruma Yoga")
    strength = yoga_def.base_strength
    modifiers = []

    jupiter = get_planet_position(Planet.JUPITER, planets)
    if jupiter:
        jup_kendras = planets_in_kendra_from(moon_sign, planets)
        if jupiter in jup_kendras:
            strength += 3.0
            modifiers.append({"description": "Jupiter aspects Moon", "effect": 3.0})

    if get_house(moon) in KENDRA_HOUSES:
        strength += 2.0
        modifiers.append({"description": "Moon in Kendra", "effect": 2.0})

    moon_dignity = get_dignity_enum(moon)
    if moon_dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
        strength += 2.0
        modifiers.append({"description": "Moon strong", "effect": 2.0})

    if strength >= 0:
        return None

    return YogaResult(
        name=yoga_def.name,
        sanskrit_name=yoga_def.sanskrit_name,
        category=yoga_def.category,
        is_active=True,
        strength=strength,
        base_strength=yoga_def.base_strength,
        modifiers=modifiers,
        participating_planets=[Planet.MOON],
        affected_houses=yoga_def.affected_houses,
        interpretation_key=yoga_def.interpretation_key,
        timing_activation="Moon dasha"
    )


def check_guru_chandala(
    planets: List[Any],
    ascendant: Zodiac
) -> Optional[YogaResult]:
    """Guru Chandala Yoga (Negative): Jupiter-Rahu conjunction."""
    if not has_conjunction(Planet.JUPITER, Planet.RAHU, planets):
        return None

    jupiter = get_planet_position(Planet.JUPITER, planets)

    yoga_def = get_yoga_definition("Guru Chandala Yoga")
    strength = yoga_def.base_strength
    modifiers = []

    if jupiter:
        jupiter_dignity = get_dignity_enum(jupiter)
        jupiter_house = get_house(jupiter)
        if jupiter_dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
            strength += 2.0
            modifiers.append({"description": "Jupiter strong", "effect": 2.0})

        if jupiter_house in [5, 9]:
            strength += 1.0
            modifiers.append({"description": "In dharma house", "effect": 1.0})

    return YogaResult(
        name=yoga_def.name,
        sanskrit_name=yoga_def.sanskrit_name,
        category=yoga_def.category,
        is_active=True,
        strength=strength,
        base_strength=yoga_def.base_strength,
        modifiers=modifiers,
        participating_planets=[Planet.JUPITER, Planet.RAHU],
        affected_houses=yoga_def.affected_houses,
        interpretation_key=yoga_def.interpretation_key,
        timing_activation="Jupiter or Rahu dasha"
    )


def check_grahan(
    planets: List[Any],
    ascendant: Zodiac
) -> Optional[YogaResult]:
    """Grahan Yoga: Sun/Moon with Rahu/Ketu."""
    sun = get_planet_position(Planet.SUN, planets)
    moon = get_planet_position(Planet.MOON, planets)
    rahu = get_planet_position(Planet.RAHU, planets)
    ketu = get_planet_position(Planet.KETU, planets)

    eclipsed = []
    if sun and rahu and get_sign_enum(sun) == get_sign_enum(rahu):
        eclipsed.append(Planet.SUN)
    if sun and ketu and get_sign_enum(sun) == get_sign_enum(ketu):
        eclipsed.append(Planet.SUN)
    if moon and rahu and get_sign_enum(moon) == get_sign_enum(rahu):
        eclipsed.append(Planet.MOON)
    if moon and ketu and get_sign_enum(moon) == get_sign_enum(ketu):
        eclipsed.append(Planet.MOON)

    if not eclipsed:
        return None

    yoga_def = get_yoga_definition("Grahan Yoga")
    strength = yoga_def.base_strength
    modifiers = []

    if len(eclipsed) == 2:
        strength -= 1.0
        modifiers.append({"description": "Both luminaries eclipsed", "effect": -1.0})

    return YogaResult(
        name=yoga_def.name,
        sanskrit_name=yoga_def.sanskrit_name,
        category=yoga_def.category,
        is_active=True,
        strength=strength,
        base_strength=yoga_def.base_strength,
        modifiers=modifiers,
        participating_planets=eclipsed + [Planet.RAHU, Planet.KETU],
        affected_houses=yoga_def.affected_houses,
        interpretation_key=yoga_def.interpretation_key,
        timing_activation="Rahu/Ketu dasha"
    )


# ============================================
# NEECHA BHANGA RAJA YOGA
# ============================================

def check_neecha_bhanga(
    planet_pos: Any,
    planets: List[Any],
    ascendant: Zodiac
) -> Optional[NeechaBhangaResult]:
    """
    Check Neecha Bhanga (debilitation cancellation) for a planet.

    8 Rules of Neecha Bhanga:
    1. Lord of debilitation sign in Kendra from Lagna or Moon
    2. Lord of exaltation sign in Kendra from Lagna or Moon
    3. Planet that exalts in debilitation sign aspects debilitated planet
    4. Debilitated planet in Kendra
    5. Sign lord conjunct debilitated planet
    6. Navamsha cancellation (planet exalted in D9)
    7. Sign lord exalted
    8. Debilitated planet receives aspect from exaltation sign lord
    """
    pos_dignity = get_dignity_enum(planet_pos)
    if pos_dignity != Dignity.DEBILITATED:
        return None

    planet = get_planet_enum(planet_pos)
    pos_house = get_house(planet_pos)
    pos_sign = get_sign_enum(planet_pos)
    pos_degree = get_degree(planet_pos)

    deb_sign = DEBILITATION.get(planet)
    if not deb_sign:
        return None

    rules_satisfied = []
    rule_details = []
    restoration_score = 0.0

    # Rule 1: Lord of debilitation sign in Kendra
    deb_lord = SIGN_LORDS.get(deb_sign)
    if deb_lord:
        deb_lord_pos = get_planet_position(deb_lord, planets)
        if deb_lord_pos and get_house(deb_lord_pos) in KENDRA_HOUSES:
            rules_satisfied.append(1)
            rule_details.append({
                "rule": 1,
                "description": f"{deb_lord.value} (deb sign lord) in Kendra",
                "strength": 0.15
            })
            restoration_score += 0.15

    # Rule 2: Lord of exaltation sign in Kendra
    exalt_sign = EXALTATION.get(planet)
    if exalt_sign:
        exalt_lord = SIGN_LORDS.get(exalt_sign)
        if exalt_lord:
            exalt_lord_pos = get_planet_position(exalt_lord, planets)
            if exalt_lord_pos and get_house(exalt_lord_pos) in KENDRA_HOUSES:
                rules_satisfied.append(2)
                rule_details.append({
                    "rule": 2,
                    "description": f"{exalt_lord.value} (exalt sign lord) in Kendra",
                    "strength": 0.15
                })
                restoration_score += 0.15

    # Rule 3: Planet exalted in deb sign aspects debilitated planet
    for p in planets:
        p_planet = get_planet_enum(p)
        if EXALTATION.get(p_planet) == deb_sign:
            if get_house(p) in KENDRA_HOUSES:
                rules_satisfied.append(3)
                rule_details.append({
                    "rule": 3,
                    "description": f"{p_planet.value} exalts in {deb_sign.name} and aspects",
                    "strength": 0.2
                })
                restoration_score += 0.2
                break

    # Rule 4: Debilitated planet in Kendra
    if pos_house in KENDRA_HOUSES:
        rules_satisfied.append(4)
        rule_details.append({
            "rule": 4,
            "description": "Debilitated planet in Kendra house",
            "strength": 0.2
        })
        restoration_score += 0.2

    # Rule 5: Sign lord conjunct
    if deb_lord:
        deb_lord_pos = get_planet_position(deb_lord, planets)
        if deb_lord_pos and get_sign_enum(deb_lord_pos) == pos_sign:
            rules_satisfied.append(5)
            rule_details.append({
                "rule": 5,
                "description": f"Sign lord {deb_lord.value} conjunct",
                "strength": 0.15
            })
            restoration_score += 0.15

    # Rule 7: Sign lord exalted
    if deb_lord:
        deb_lord_pos = get_planet_position(deb_lord, planets)
        if deb_lord_pos and get_dignity_enum(deb_lord_pos) == Dignity.EXALTED:
            rules_satisfied.append(7)
            rule_details.append({
                "rule": 7,
                "description": f"Sign lord {deb_lord.value} exalted",
                "strength": 0.25
            })
            restoration_score += 0.25

    if not rules_satisfied:
        return None

    # Determine cancellation level
    if restoration_score >= 0.6:
        cancellation_level = CancellationLevel.RAJA_YOGA
        effective_dignity = "Raja Yoga Karaka"
        house_modifier = 2.0
    elif restoration_score >= 0.4:
        cancellation_level = CancellationLevel.STRONG
        effective_dignity = "Neutral-Strong"
        house_modifier = 1.5
    elif restoration_score >= 0.25:
        cancellation_level = CancellationLevel.MODERATE
        effective_dignity = "Neutral"
        house_modifier = 1.0
    elif restoration_score >= 0.1:
        cancellation_level = CancellationLevel.WEAK
        effective_dignity = "Weak-Neutral"
        house_modifier = 0.5
    else:
        cancellation_level = CancellationLevel.NONE
        effective_dignity = "Debilitated"
        house_modifier = 0.0

    return NeechaBhangaResult(
        planet=planet,
        debilitation_sign=deb_sign,
        house=pos_house,
        degree=pos_degree,
        rules_satisfied=rules_satisfied,
        rule_details=rule_details,
        total_restoration_score=restoration_score,
        cancellation_level=cancellation_level,
        house_score_modifier=house_modifier,
        effective_dignity=effective_dignity
    )


# ============================================
# MAIN DETECTION ENGINE
# ============================================

def detect_all_yogas(
    planets: List[Any],
    ascendant: Zodiac
) -> Tuple[List[YogaResult], Dict[str, NeechaBhangaResult]]:
    """Detect all yogas in the chart."""
    yogas = []
    neecha_bhanga = {}

    # Check Gaja Kesari
    result = check_gaja_kesari(planets, ascendant)
    if result:
        yogas.append(result)

    # Check Mahapurusha yogas
    mahapurusha_checks = [
        (Planet.JUPITER, "Hamsa Yoga"),
        (Planet.VENUS, "Malavya Yoga"),
        (Planet.MARS, "Ruchaka Yoga"),
        (Planet.MERCURY, "Bhadra Yoga"),
        (Planet.SATURN, "Sasha Yoga"),
    ]
    for planet, yoga_name in mahapurusha_checks:
        result = check_mahapurusha_yoga(planet, planets, ascendant, yoga_name)
        if result:
            yogas.append(result)

    # Check Budhaditya
    result = check_budhaditya(planets, ascendant)
    if result:
        yogas.append(result)

    # Check Chandra-Mangal
    result = check_chandra_mangal(planets, ascendant)
    if result:
        yogas.append(result)

    # Check negative yogas
    result = check_kemadruma(planets, ascendant)
    if result:
        yogas.append(result)

    result = check_guru_chandala(planets, ascendant)
    if result:
        yogas.append(result)

    result = check_grahan(planets, ascendant)
    if result:
        yogas.append(result)

    # Check Neecha Bhanga for debilitated planets
    for planet_pos in planets:
        pos_dignity = get_dignity_enum(planet_pos)
        if pos_dignity == Dignity.DEBILITATED:
            nb_result = check_neecha_bhanga(planet_pos, planets, ascendant)
            if nb_result:
                pos_planet = get_planet_enum(planet_pos)
                pos_house = get_house(planet_pos)
                neecha_bhanga[pos_planet.value] = nb_result
                # Add as yoga if strong enough
                if nb_result.cancellation_level == CancellationLevel.RAJA_YOGA:
                    yoga_def = get_yoga_definition("Neecha Bhanga Raja Yoga")
                    yogas.append(YogaResult(
                        name=yoga_def.name,
                        sanskrit_name=yoga_def.sanskrit_name,
                        category=yoga_def.category,
                        is_active=True,
                        strength=yoga_def.base_strength,
                        base_strength=yoga_def.base_strength,
                        modifiers=[{
                            "description": f"{pos_planet.value} debilitation cancelled",
                            "effect": nb_result.total_restoration_score
                        }],
                        participating_planets=[pos_planet],
                        affected_houses=[pos_house],
                        interpretation_key=yoga_def.interpretation_key,
                        timing_activation=f"{pos_planet.value} dasha"
                    ))

    return yogas, neecha_bhanga


def calculate_yoga_summary(yogas: List[YogaResult]) -> YogaSummary:
    """Calculate summary statistics for all yogas."""
    positive_yogas = [y for y in yogas if y.strength > 0]
    negative_yogas = [y for y in yogas if y.strength < 0]

    raja_yogas = [y for y in yogas if y.category in [YogaCategory.RAJA, YogaCategory.MAHAPURUSHA]]
    dhana_yogas = [y for y in yogas if y.category == YogaCategory.DHANA]

    mahapurusha_names = [y.name for y in yogas if y.category == YogaCategory.MAHAPURUSHA]

    key_yogas = sorted(yogas, key=lambda y: abs(y.strength), reverse=True)[:5]
    key_yoga_names = [y.name for y in key_yogas]

    positive_strength = sum(y.strength for y in positive_yogas)
    negative_strength = sum(y.strength for y in negative_yogas)
    total_strength = positive_strength + negative_strength

    # Calculate overall score (0-10)
    overall_score = 5.0 + (total_strength / max(len(yogas), 1))
    overall_score = max(1.0, min(10.0, overall_score))

    return YogaSummary(
        total_count=len(yogas),
        positive_count=len(positive_yogas),
        negative_count=len(negative_yogas),
        total_strength=total_strength,
        positive_strength=positive_strength,
        negative_strength=negative_strength,
        raja_yoga_count=len(raja_yogas),
        raja_yoga_strength=sum(y.strength for y in raja_yogas),
        dhana_yoga_count=len(dhana_yogas),
        dhana_yoga_strength=sum(y.strength for y in dhana_yogas),
        mahapurusha_yogas=mahapurusha_names,
        key_yogas=key_yoga_names,
        overall_yoga_score=overall_score
    )


def calculate_house_yoga_bonuses(
    yogas: List[YogaResult],
    neecha_bhanga: Dict[str, NeechaBhangaResult]
) -> Dict[str, float]:
    """Calculate house score bonuses from yogas."""
    bonuses = {f"house_{i}": 0.0 for i in range(1, 13)}

    for yoga in yogas:
        bonus = yoga.strength / 10.0
        for house in yoga.affected_houses:
            key = f"house_{house}"
            if key in bonuses:
                bonuses[key] += bonus

    for nb in neecha_bhanga.values():
        key = f"house_{nb.house}"
        if key in bonuses:
            bonuses[key] += nb.house_score_modifier

    for key in bonuses:
        bonuses[key] = round(max(-3.0, min(3.0, bonuses[key])), 2)

    return bonuses


class Stage03YogaAnalysis:
    """Stage 3: Yoga Analysis engine."""

    def __init__(self, planets: List[Any], ascendant: Zodiac):
        self.planets = planets
        self.ascendant = ascendant

    def analyze(self) -> Stage3Result:
        """Run Stage 3 analysis."""
        yogas, neecha_bhanga = detect_all_yogas(self.planets, self.ascendant)
        yoga_summary = calculate_yoga_summary(yogas)
        house_bonuses = calculate_house_yoga_bonuses(yogas, neecha_bhanga)

        return Stage3Result(
            yogas=yogas,
            neecha_bhanga=neecha_bhanga,
            yoga_summary=yoga_summary,
            house_yoga_bonuses=house_bonuses
        )
