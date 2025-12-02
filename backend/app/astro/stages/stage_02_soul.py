"""
Stage 2: Soul Blueprint (D9 Navamsha)

The Navamsha (D9) chart reveals:
- True soul nature (manifests after age 30-35)
- Marriage and partnerships
- Spiritual path
- Dharmic purpose

Key analyses:
- Planet positions in D9
- Vargottama planets (same sign in D1 and D9)
- Pushkara Navamsha positions
- D1-D9 synergy score
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from ..models.types import Planet, Zodiac, Dignity, ZODIAC_ORDER
from ..reference.dignities import get_dignity, get_dignity_from_string, SIGN_LORDS


class SynergyLevel(str, Enum):
    """D1-D9 synergy classification."""
    EXCELLENT = "Excellent"      # 8-10
    GOOD = "Good"                # 6-8
    MODERATE = "Moderate"        # 4-6
    CHALLENGING = "Challenging"  # 2-4
    DIFFICULT = "Difficult"      # 0-2


@dataclass
class VargottamaInfo:
    """Planet in same sign in D1 and D9."""
    planet: Planet
    sign: Zodiac
    strength_bonus: float = 1.5


@dataclass
class PushkaraInfo:
    """Planet in Pushkara Navamsha."""
    planet: Planet
    navamsha_sign: Zodiac
    is_pushkara_navamsha: bool
    is_pushkara_bhaga: bool


@dataclass
class D1D9Comparison:
    """Comparison of planet between D1 and D9."""
    planet: Planet
    d1_sign: Zodiac
    d1_dignity: Dignity
    d9_sign: Zodiac
    d9_dignity: Dignity
    is_vargottama: bool
    improvement: str  # "improved", "weakened", "stable"
    synergy_contribution: float


@dataclass
class D9PlanetData:
    """Planet data from D9 chart."""
    planet: Planet
    sign: Zodiac
    house: int
    degree: float
    dignity: Dignity
    nakshatra: str = ""
    is_retrograde: bool = False


@dataclass
class Stage2Result:
    """Complete Stage 2 analysis result."""
    d9_ascendant: Zodiac
    d9_ascendant_degree: float
    d9_planets: List[D9PlanetData]

    vargottama_planets: List[VargottamaInfo]
    pushkara_positions: List[PushkaraInfo]

    planet_comparisons: List[D1D9Comparison]
    synergy_score: float
    synergy_level: SynergyLevel

    house_scores_adjusted: Dict[str, float]

    confirmations: List[str]
    contradictions: List[str]

    atmakaraka: Optional[Planet] = None
    atmakaraka_d9_sign: Optional[Zodiac] = None


# Pushkara Navamsha signs
PUSHKARA_NAVAMSHAS = {
    Zodiac.ARIES: [Zodiac.SAGITTARIUS],
    Zodiac.TAURUS: [Zodiac.AQUARIUS],
    Zodiac.GEMINI: [Zodiac.CANCER],
    Zodiac.CANCER: [Zodiac.SAGITTARIUS],
    Zodiac.LEO: [Zodiac.AQUARIUS],
    Zodiac.VIRGO: [Zodiac.CANCER],
    Zodiac.LIBRA: [Zodiac.SAGITTARIUS],
    Zodiac.SCORPIO: [Zodiac.AQUARIUS],
    Zodiac.SAGITTARIUS: [Zodiac.CANCER],
    Zodiac.CAPRICORN: [Zodiac.SAGITTARIUS],
    Zodiac.AQUARIUS: [Zodiac.AQUARIUS],
    Zodiac.PISCES: [Zodiac.CANCER],
}


def normalize_planet_name(name: str) -> Planet:
    """Convert planet name string to enum."""
    name_map = {
        "sun": Planet.SUN, "Sun": Planet.SUN, "SUN": Planet.SUN,
        "moon": Planet.MOON, "Moon": Planet.MOON, "MOON": Planet.MOON,
        "mars": Planet.MARS, "Mars": Planet.MARS, "MARS": Planet.MARS,
        "mercury": Planet.MERCURY, "Mercury": Planet.MERCURY,
        "jupiter": Planet.JUPITER, "Jupiter": Planet.JUPITER,
        "venus": Planet.VENUS, "Venus": Planet.VENUS,
        "saturn": Planet.SATURN, "Saturn": Planet.SATURN,
        "rahu": Planet.RAHU, "Rahu": Planet.RAHU,
        "ketu": Planet.KETU, "Ketu": Planet.KETU,
    }
    return name_map.get(name, Planet.SUN)


def normalize_sign_name(name: str) -> Zodiac:
    """Convert sign name string to enum."""
    if not name:
        return Zodiac.ARIES
    name_map = {
        "aries": Zodiac.ARIES, "taurus": Zodiac.TAURUS,
        "gemini": Zodiac.GEMINI, "cancer": Zodiac.CANCER,
        "leo": Zodiac.LEO, "virgo": Zodiac.VIRGO,
        "libra": Zodiac.LIBRA, "scorpio": Zodiac.SCORPIO,
        "sagittarius": Zodiac.SAGITTARIUS, "capricorn": Zodiac.CAPRICORN,
        "aquarius": Zodiac.AQUARIUS, "pisces": Zodiac.PISCES,
    }
    return name_map.get(name.lower(), Zodiac.ARIES)


def get_house_from_sign(planet_sign: Zodiac, ascendant_sign: Zodiac) -> int:
    """Calculate house number from sign relative to ascendant."""
    asc_index = ZODIAC_ORDER.index(ascendant_sign)
    planet_index = ZODIAC_ORDER.index(planet_sign)
    house = ((planet_index - asc_index) % 12) + 1
    return house


def parse_d9_chart(digital_twin: Dict[str, Any]) -> Tuple[Dict, List[Dict]]:
    """Extract D9 chart from digital_twin."""
    d9 = digital_twin.get("vargas", {}).get("D9", {})
    ascendant_data = d9.get("ascendant", {})
    planets_data = d9.get("planets", [])
    return ascendant_data, planets_data


def get_planet_enum(p) -> Planet:
    """Get Planet enum from either PlanetSummary or object with planet attribute."""
    if hasattr(p, 'planet'):
        result = p.planet
        if isinstance(result, Planet):
            return result
        return normalize_planet_name(str(result))
    elif hasattr(p, 'name'):
        return normalize_planet_name(p.name)
    return Planet.SUN


def get_sign_enum(p) -> Zodiac:
    """Get Zodiac enum from either PlanetSummary or object with sign attribute."""
    if hasattr(p, 'sign_zodiac'):
        return p.sign_zodiac
    elif hasattr(p, 'sign'):
        result = p.sign
        if isinstance(result, Zodiac):
            return result
        return normalize_sign_name(str(result))
    return Zodiac.ARIES


def get_dignity_enum(p) -> Dignity:
    """Get Dignity enum from object."""
    if hasattr(p, 'dignity_enum'):
        return p.dignity_enum
    elif hasattr(p, 'dignity'):
        result = p.dignity
        if isinstance(result, Dignity):
            return result
        return get_dignity_from_string(str(result))
    return Dignity.NEUTRAL


def detect_vargottama(
    d1_planets: List[Any],
    d9_planets: List[Dict]
) -> List[VargottamaInfo]:
    """Detect Vargottama planets (same sign in D1 and D9)."""
    vargottama = []

    d9_signs = {}
    for p_data in d9_planets:
        planet = normalize_planet_name(p_data.get("name", ""))
        sign = normalize_sign_name(p_data.get("sign_name", ""))
        d9_signs[planet] = sign

    for d1_planet in d1_planets:
        planet_enum = get_planet_enum(d1_planet)
        sign_enum = get_sign_enum(d1_planet)
        if planet_enum in d9_signs:
            d9_sign = d9_signs[planet_enum]
            if sign_enum == d9_sign:
                vargottama.append(VargottamaInfo(
                    planet=planet_enum,
                    sign=sign_enum,
                    strength_bonus=1.5
                ))

    return vargottama


def detect_pushkara(
    d9_planets: List[Dict],
    d1_signs: Dict[Planet, Zodiac]
) -> List[PushkaraInfo]:
    """Detect planets in Pushkara Navamsha."""
    pushkara_list = []

    for p_data in d9_planets:
        planet = normalize_planet_name(p_data.get("name", ""))
        d9_sign = normalize_sign_name(p_data.get("sign_name", ""))
        d1_sign = d1_signs.get(planet, Zodiac.ARIES)

        pushkara_signs = PUSHKARA_NAVAMSHAS.get(d1_sign, [])
        is_pushkara = d9_sign in pushkara_signs

        if is_pushkara:
            pushkara_list.append(PushkaraInfo(
                planet=planet,
                navamsha_sign=d9_sign,
                is_pushkara_navamsha=True,
                is_pushkara_bhaga=False
            ))

    return pushkara_list


def compare_d1_d9(
    d1_planets: List[Any],
    d9_planets_data: List[Dict]
) -> Tuple[List[D1D9Comparison], float]:
    """Compare each planet's position in D1 vs D9."""
    comparisons = []
    synergy_total = 0.0
    planet_count = 0

    d9_info = {}
    for p_data in d9_planets_data:
        planet = normalize_planet_name(p_data.get("name", ""))
        sign = normalize_sign_name(p_data.get("sign_name", ""))
        degree = p_data.get("relative_degree", p_data.get("degree", 15.0))
        d9_info[planet] = (sign, degree)

    dignity_rank = {
        Dignity.EXALTED: 7,
        Dignity.MOOLATRIKONA: 6,
        Dignity.OWN_SIGN: 5,
        Dignity.GREAT_FRIEND: 4,
        Dignity.FRIEND: 4,
        Dignity.NEUTRAL: 3,
        Dignity.ENEMY: 2,
        Dignity.GREAT_ENEMY: 2,
        Dignity.DEBILITATED: 1,
    }

    for d1_planet in d1_planets:
        planet = get_planet_enum(d1_planet)
        d1_sign = get_sign_enum(d1_planet)
        d1_dignity = get_dignity_enum(d1_planet)

        if planet not in d9_info:
            continue

        d9_sign, d9_degree = d9_info[planet]
        d9_dignity = get_dignity(planet, d9_sign, d9_degree)

        d1_rank = dignity_rank.get(d1_dignity, 3)
        d9_rank = dignity_rank.get(d9_dignity, 3)

        rank_diff = d9_rank - d1_rank
        if rank_diff >= 2:
            improvement = "improved"
            synergy_contrib = 1.5
        elif rank_diff >= 1:
            improvement = "slightly_improved"
            synergy_contrib = 0.75
        elif rank_diff <= -2:
            improvement = "weakened"
            synergy_contrib = -1.0
        elif rank_diff <= -1:
            improvement = "slightly_weakened"
            synergy_contrib = -0.5
        else:
            improvement = "stable"
            synergy_contrib = 0.5 if d1_rank >= 4 else 0.0

        is_vargottama = d1_sign == d9_sign
        if is_vargottama:
            synergy_contrib += 1.0

        comparisons.append(D1D9Comparison(
            planet=planet,
            d1_sign=d1_sign,
            d1_dignity=d1_dignity,
            d9_sign=d9_sign,
            d9_dignity=d9_dignity,
            is_vargottama=is_vargottama,
            improvement=improvement,
            synergy_contribution=synergy_contrib
        ))

        synergy_total += synergy_contrib
        planet_count += 1

    if planet_count > 0:
        raw_synergy = synergy_total
        synergy_score = ((raw_synergy + 13.5) / 36.0) * 10.0
        synergy_score = max(0.0, min(10.0, synergy_score))
    else:
        synergy_score = 5.0

    return comparisons, round(synergy_score, 1)


def get_synergy_level(score: float) -> SynergyLevel:
    """Convert synergy score to level."""
    if score >= 8:
        return SynergyLevel.EXCELLENT
    elif score >= 6:
        return SynergyLevel.GOOD
    elif score >= 4:
        return SynergyLevel.MODERATE
    elif score >= 2:
        return SynergyLevel.CHALLENGING
    else:
        return SynergyLevel.DIFFICULT


def calculate_adjusted_house_scores(
    d1_house_scores: Dict[str, float],
    d9_planets: List[Dict],
    d9_ascendant: Zodiac,
    synergy_score: float
) -> Dict[str, float]:
    """Calculate adjusted house scores (D1+D9 blend)."""
    adjusted = {}

    d9_planets_by_house: Dict[int, List[Planet]] = {i: [] for i in range(1, 13)}
    for p_data in d9_planets:
        planet = normalize_planet_name(p_data.get("name", ""))
        sign = normalize_sign_name(p_data.get("sign_name", ""))
        house = get_house_from_sign(sign, d9_ascendant)
        d9_planets_by_house[house].append(planet)

    benefics = [Planet.JUPITER, Planet.VENUS, Planet.MERCURY, Planet.MOON]
    malefics = [Planet.SATURN, Planet.MARS, Planet.RAHU, Planet.KETU, Planet.SUN]

    for house_num in range(1, 13):
        key = f"house_{house_num}"
        d1_score = d1_house_scores.get(key, 5.0)

        d9_score = 5.0
        d9_occupants = d9_planets_by_house.get(house_num, [])
        for planet in d9_occupants:
            if planet in benefics:
                d9_score += 0.8
            elif planet in malefics:
                d9_score -= 0.4
        d9_score = max(1.0, min(10.0, d9_score))

        synergy_component = synergy_score / 10.0 * 2.0
        final_score = (d1_score * 0.4) + (d9_score * 0.4) + (synergy_component * 0.5 + 4.0) * 0.2
        adjusted[key] = round(max(1.0, min(10.0, final_score)), 1)

    return adjusted


def find_atmakaraka(d1_planets: List[Any]) -> Tuple[Optional[Planet], float]:
    """Find Atmakaraka (planet with highest degree)."""
    max_degree = -1.0
    atmakaraka = None

    for planet_obj in d1_planets:
        planet_enum = get_planet_enum(planet_obj)
        if planet_enum in [Planet.RAHU, Planet.KETU]:
            continue

        degree = getattr(planet_obj, 'degree', 15.0)
        if degree > max_degree:
            max_degree = degree
            atmakaraka = planet_enum

    return atmakaraka, max_degree


def generate_insights(
    comparisons: List[D1D9Comparison],
    vargottama: List[VargottamaInfo]
) -> Tuple[List[str], List[str]]:
    """Generate confirmations and contradictions."""
    confirmations = []
    contradictions = []

    for comp in comparisons:
        planet_name = comp.planet.value

        if comp.is_vargottama:
            confirmations.append(
                f"{planet_name} is Vargottama in {comp.d1_sign.name} - very stable expression"
            )

        if comp.improvement == "improved":
            confirmations.append(
                f"{planet_name} gains strength in D9 ({comp.d1_dignity.value} -> {comp.d9_dignity.value})"
            )
        elif comp.improvement == "weakened":
            contradictions.append(
                f"{planet_name} weakens in D9 ({comp.d1_dignity.value} -> {comp.d9_dignity.value})"
            )

    if len(vargottama) >= 3:
        confirmations.append(f"{len(vargottama)} Vargottama planets indicate stable destiny")

    return confirmations, contradictions


class Stage02SoulBlueprint:
    """Stage 2: Soul Blueprint analyzer."""

    def __init__(
        self,
        digital_twin: Dict[str, Any],
        d1_planets: List[Any],
        d1_house_scores: Dict[str, float]
    ):
        self.digital_twin = digital_twin
        self.d1_planets = d1_planets
        self.d1_house_scores = d1_house_scores

    def analyze(self) -> Stage2Result:
        """Run Stage 2 analysis."""
        d9_asc_data, d9_planets_data = parse_d9_chart(self.digital_twin)
        d9_ascendant = normalize_sign_name(d9_asc_data.get("sign_name", "Aries"))
        d9_asc_degree = d9_asc_data.get("degrees", d9_asc_data.get("degree", 0.0))

        d9_planets = []
        for p_data in d9_planets_data:
            planet = normalize_planet_name(p_data.get("name", ""))
            sign = normalize_sign_name(p_data.get("sign_name", ""))
            degree = p_data.get("relative_degree", p_data.get("degree", 0.0))
            house = get_house_from_sign(sign, d9_ascendant)
            dignity = get_dignity(planet, sign, degree)

            d9_planets.append(D9PlanetData(
                planet=planet,
                sign=sign,
                house=house,
                degree=degree,
                dignity=dignity,
                nakshatra=p_data.get("nakshatra", ""),
                is_retrograde=p_data.get("is_retrograde", False)
            ))

        vargottama = detect_vargottama(self.d1_planets, d9_planets_data)

        d1_signs = {p.planet: p.sign for p in self.d1_planets}
        pushkara = detect_pushkara(d9_planets_data, d1_signs)

        comparisons, synergy_score = compare_d1_d9(self.d1_planets, d9_planets_data)
        synergy_level = get_synergy_level(synergy_score)

        adjusted_scores = calculate_adjusted_house_scores(
            self.d1_house_scores, d9_planets_data, d9_ascendant, synergy_score
        )

        atmakaraka, ak_degree = find_atmakaraka(self.d1_planets)
        ak_d9_sign = None
        if atmakaraka:
            for p_data in d9_planets_data:
                if normalize_planet_name(p_data.get("name", "")) == atmakaraka:
                    ak_d9_sign = normalize_sign_name(p_data.get("sign_name", ""))
                    break

        confirmations, contradictions = generate_insights(comparisons, vargottama)

        return Stage2Result(
            d9_ascendant=d9_ascendant,
            d9_ascendant_degree=d9_asc_degree,
            d9_planets=d9_planets,
            vargottama_planets=vargottama,
            pushkara_positions=pushkara,
            planet_comparisons=comparisons,
            synergy_score=synergy_score,
            synergy_level=synergy_level,
            house_scores_adjusted=adjusted_scores,
            confirmations=confirmations,
            contradictions=contradictions,
            atmakaraka=atmakaraka,
            atmakaraka_d9_sign=ak_d9_sign
        )
