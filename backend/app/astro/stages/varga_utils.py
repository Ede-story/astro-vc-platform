"""
Varga Utilities Module

Common helper functions for parsing and analyzing divisional charts (vargas).
Used by Stages 4-8 for consistent varga data extraction.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..models.types import Planet, Zodiac, House, Dignity
from ..models.planets import PlanetPosition, PlanetSummary


class VargaType(Enum):
    """Divisional chart types"""
    D1 = "D1"    # Rashi - Main chart
    D2 = "D2"    # Hora - Wealth
    D3 = "D3"    # Drekkana - Siblings/Courage
    D4 = "D4"    # Chaturthamsha - Fortune/Property
    D5 = "D5"    # Panchamsha - Creativity/Children
    D7 = "D7"    # Saptamsha - Children/Progeny
    D9 = "D9"    # Navamsha - Soul/Marriage
    D10 = "D10"  # Dashamsha - Career
    D11 = "D11"  # Rudramsha - Death/Destruction/Gains
    D12 = "D12"  # Dwadashamsha - Parents/Ancestry
    D16 = "D16"  # Shodashamsha - Vehicles/Luxury
    D20 = "D20"  # Vimshamsha - Spirituality
    D24 = "D24"  # Chaturvimshamsha - Education
    D27 = "D27"  # Bhamsha - Strength
    D30 = "D30"  # Trimshamsha - Misfortune
    D60 = "D60"  # Shashtiamsha - General


@dataclass
class VargaPlanetData:
    """Planet data extracted from a varga chart"""
    planet: Planet
    sign: Zodiac
    house: int
    degree: float
    is_retrograde: bool = False
    dignity: Optional[Dignity] = None

    @property
    def sign_id(self) -> int:
        return self.sign.value


@dataclass
class VargaChartData:
    """Complete data for a divisional chart"""
    varga_type: VargaType
    ascendant_sign: Zodiac
    ascendant_degree: float
    planets: Dict[Planet, VargaPlanetData]
    houses: Dict[int, Zodiac]  # house_num -> sign

    def get_planet(self, planet: Planet) -> Optional[VargaPlanetData]:
        """Get planet data by Planet enum"""
        return self.planets.get(planet)

    def get_planets_in_house(self, house: int) -> List[Planet]:
        """Get all planets in a specific house"""
        return [p for p, data in self.planets.items() if data.house == house]

    def get_planets_in_sign(self, sign: Zodiac) -> List[Planet]:
        """Get all planets in a specific sign"""
        return [p for p, data in self.planets.items() if data.sign == sign]


def parse_varga_chart(digital_twin: Dict[str, Any], varga_name: str) -> Optional[VargaChartData]:
    """
    Parse a divisional chart from digital_twin JSON.

    Args:
        digital_twin: The full digital_twin dict
        varga_name: Varga name like "D1", "D2", "D9", etc.

    Returns:
        VargaChartData or None if varga not found
    """
    vargas = digital_twin.get("vargas", {})
    varga_data = vargas.get(varga_name, {})

    if not varga_data:
        return None

    # Parse ascendant
    asc_data = varga_data.get("ascendant", {})
    asc_sign_id = asc_data.get("sign_id", 1)
    asc_degree = float(asc_data.get("degrees", 0))

    try:
        asc_sign = Zodiac(asc_sign_id)
    except ValueError:
        asc_sign = Zodiac.ARIES

    # Parse planets
    planets_dict: Dict[Planet, VargaPlanetData] = {}
    planets_list = varga_data.get("planets", [])

    for planet_data in planets_list:
        try:
            planet_name = planet_data.get("name", "")
            planet = Planet.from_string(planet_name)

            sign_id = planet_data.get("sign_id", 1)
            sign = Zodiac(sign_id)

            house = int(planet_data.get("house", 1))
            degree = float(planet_data.get("degree", 0))
            is_retro = planet_data.get("is_retrograde", False)

            # Get dignity if available
            dignity_str = planet_data.get("dignity", "")
            dignity = None
            if dignity_str:
                try:
                    dignity = Dignity[dignity_str.upper()]
                except (KeyError, AttributeError):
                    pass

            planets_dict[planet] = VargaPlanetData(
                planet=planet,
                sign=sign,
                house=house,
                degree=degree,
                is_retrograde=is_retro,
                dignity=dignity
            )
        except (ValueError, KeyError) as e:
            continue

    # Parse houses
    houses_dict: Dict[int, Zodiac] = {}
    houses_list = varga_data.get("houses", [])

    for house_data in houses_list:
        try:
            house_num = int(house_data.get("house", 0))
            sign_id = house_data.get("sign_id", 1)
            houses_dict[house_num] = Zodiac(sign_id)
        except (ValueError, KeyError):
            continue

    # If houses not provided, calculate from ascendant
    if not houses_dict:
        for i in range(1, 13):
            sign_num = ((asc_sign.value - 1 + i - 1) % 12) + 1
            houses_dict[i] = Zodiac(sign_num)

    try:
        varga_type = VargaType(varga_name)
    except ValueError:
        varga_type = VargaType.D1

    return VargaChartData(
        varga_type=varga_type,
        ascendant_sign=asc_sign,
        ascendant_degree=asc_degree,
        planets=planets_dict,
        houses=houses_dict
    )


def get_house_from_ascendant(planet_sign: Zodiac, ascendant_sign: Zodiac) -> int:
    """
    Calculate house number from planet sign relative to ascendant.

    Args:
        planet_sign: Sign where planet is placed
        ascendant_sign: Ascendant sign

    Returns:
        House number (1-12)
    """
    diff = planet_sign.value - ascendant_sign.value
    house = (diff % 12) + 1
    return house


def get_sign_lord(sign: Zodiac) -> Planet:
    """
    Get the ruling planet of a sign.

    Args:
        sign: Zodiac sign

    Returns:
        Ruling planet
    """
    lords = {
        Zodiac.ARIES: Planet.MARS,
        Zodiac.TAURUS: Planet.VENUS,
        Zodiac.GEMINI: Planet.MERCURY,
        Zodiac.CANCER: Planet.MOON,
        Zodiac.LEO: Planet.SUN,
        Zodiac.VIRGO: Planet.MERCURY,
        Zodiac.LIBRA: Planet.VENUS,
        Zodiac.SCORPIO: Planet.MARS,
        Zodiac.SAGITTARIUS: Planet.JUPITER,
        Zodiac.CAPRICORN: Planet.SATURN,
        Zodiac.AQUARIUS: Planet.SATURN,
        Zodiac.PISCES: Planet.JUPITER,
    }
    return lords.get(sign, Planet.SUN)


def is_benefic(planet: Planet) -> bool:
    """Check if planet is naturally benefic"""
    return planet in [Planet.JUPITER, Planet.VENUS, Planet.MERCURY, Planet.MOON]


def is_malefic(planet: Planet) -> bool:
    """Check if planet is naturally malefic"""
    return planet in [Planet.SATURN, Planet.MARS, Planet.SUN, Planet.RAHU, Planet.KETU]


def get_dignity_in_sign(planet: Planet, sign: Zodiac) -> Dignity:
    """
    Determine planet's dignity in a sign.

    Args:
        planet: The planet
        sign: The sign planet is in

    Returns:
        Dignity enum value
    """
    # Exaltation signs
    exaltation = {
        Planet.SUN: Zodiac.ARIES,
        Planet.MOON: Zodiac.TAURUS,
        Planet.MARS: Zodiac.CAPRICORN,
        Planet.MERCURY: Zodiac.VIRGO,
        Planet.JUPITER: Zodiac.CANCER,
        Planet.VENUS: Zodiac.PISCES,
        Planet.SATURN: Zodiac.LIBRA,
    }

    # Debilitation signs
    debilitation = {
        Planet.SUN: Zodiac.LIBRA,
        Planet.MOON: Zodiac.SCORPIO,
        Planet.MARS: Zodiac.CANCER,
        Planet.MERCURY: Zodiac.PISCES,
        Planet.JUPITER: Zodiac.CAPRICORN,
        Planet.VENUS: Zodiac.VIRGO,
        Planet.SATURN: Zodiac.ARIES,
    }

    # Own signs
    own_signs = {
        Planet.SUN: [Zodiac.LEO],
        Planet.MOON: [Zodiac.CANCER],
        Planet.MARS: [Zodiac.ARIES, Zodiac.SCORPIO],
        Planet.MERCURY: [Zodiac.GEMINI, Zodiac.VIRGO],
        Planet.JUPITER: [Zodiac.SAGITTARIUS, Zodiac.PISCES],
        Planet.VENUS: [Zodiac.TAURUS, Zodiac.LIBRA],
        Planet.SATURN: [Zodiac.CAPRICORN, Zodiac.AQUARIUS],
    }

    if planet in exaltation and exaltation[planet] == sign:
        return Dignity.EXALTED

    if planet in debilitation and debilitation[planet] == sign:
        return Dignity.DEBILITATED

    if planet in own_signs and sign in own_signs[planet]:
        return Dignity.OWN_SIGN

    # Check for friendly/enemy signs (simplified)
    lord = get_sign_lord(sign)
    if lord == planet:
        return Dignity.OWN_SIGN

    return Dignity.NEUTRAL


def compare_d1_varga_position(
    d1_planet: VargaPlanetData,
    varga_planet: VargaPlanetData
) -> Dict[str, Any]:
    """
    Compare planet position between D1 and another varga.

    Args:
        d1_planet: Planet data from D1
        varga_planet: Planet data from another varga

    Returns:
        Dict with comparison results
    """
    same_sign = d1_planet.sign == varga_planet.sign

    # Calculate sign distance
    sign_diff = abs(d1_planet.sign.value - varga_planet.sign.value)
    if sign_diff > 6:
        sign_diff = 12 - sign_diff

    # Determine relationship
    if same_sign:
        relationship = "vargottama"
        strength_modifier = 1.25
    elif sign_diff <= 2:
        relationship = "supportive"
        strength_modifier = 1.1
    elif sign_diff >= 5:
        relationship = "challenging"
        strength_modifier = 0.9
    else:
        relationship = "neutral"
        strength_modifier = 1.0

    return {
        "same_sign": same_sign,
        "sign_distance": sign_diff,
        "relationship": relationship,
        "strength_modifier": strength_modifier,
        "d1_sign": d1_planet.sign.name,
        "varga_sign": varga_planet.sign.name
    }


def get_karaka_for_house(house: int) -> List[Planet]:
    """
    Get natural significators (karakas) for a house.

    Args:
        house: House number (1-12)

    Returns:
        List of karaka planets
    """
    karakas = {
        1: [Planet.SUN],                          # Self, personality
        2: [Planet.JUPITER, Planet.VENUS],        # Wealth, speech
        3: [Planet.MARS, Planet.MERCURY],         # Courage, siblings
        4: [Planet.MOON, Planet.VENUS],           # Mother, property
        5: [Planet.JUPITER],                      # Children, creativity
        6: [Planet.MARS, Planet.SATURN],          # Enemies, disease
        7: [Planet.VENUS],                        # Marriage, partnerships
        8: [Planet.SATURN],                       # Longevity, transformation
        9: [Planet.JUPITER, Planet.SUN],          # Father, dharma
        10: [Planet.SUN, Planet.SATURN, Planet.MERCURY],  # Career
        11: [Planet.JUPITER],                     # Gains, desires
        12: [Planet.SATURN, Planet.KETU],         # Losses, moksha
    }
    return karakas.get(house, [])


def calculate_varga_strength(
    planet: Planet,
    varga_positions: Dict[str, VargaPlanetData]
) -> float:
    """
    Calculate planet strength across multiple vargas.

    Args:
        planet: Planet to analyze
        varga_positions: Dict of varga_name -> VargaPlanetData

    Returns:
        Strength score (0-100)
    """
    if not varga_positions:
        return 50.0

    score = 50.0
    varga_weights = {
        "D1": 1.0,
        "D9": 0.5,
        "D10": 0.3,
        "D2": 0.2,
        "D3": 0.2,
        "D4": 0.2,
        "D7": 0.2,
    }

    for varga_name, position in varga_positions.items():
        weight = varga_weights.get(varga_name, 0.1)

        if position.dignity:
            if position.dignity == Dignity.EXALTED:
                score += 10 * weight
            elif position.dignity == Dignity.OWN_SIGN:
                score += 7 * weight
            elif position.dignity == Dignity.DEBILITATED:
                score -= 10 * weight

    return max(0, min(100, score))


def get_element(sign: Zodiac) -> str:
    """Get element of a zodiac sign"""
    fire = [Zodiac.ARIES, Zodiac.LEO, Zodiac.SAGITTARIUS]
    earth = [Zodiac.TAURUS, Zodiac.VIRGO, Zodiac.CAPRICORN]
    air = [Zodiac.GEMINI, Zodiac.LIBRA, Zodiac.AQUARIUS]
    water = [Zodiac.CANCER, Zodiac.SCORPIO, Zodiac.PISCES]

    if sign in fire:
        return "fire"
    elif sign in earth:
        return "earth"
    elif sign in air:
        return "air"
    elif sign in water:
        return "water"
    return "unknown"


def get_modality(sign: Zodiac) -> str:
    """Get modality of a zodiac sign"""
    cardinal = [Zodiac.ARIES, Zodiac.CANCER, Zodiac.LIBRA, Zodiac.CAPRICORN]
    fixed = [Zodiac.TAURUS, Zodiac.LEO, Zodiac.SCORPIO, Zodiac.AQUARIUS]
    mutable = [Zodiac.GEMINI, Zodiac.VIRGO, Zodiac.SAGITTARIUS, Zodiac.PISCES]

    if sign in cardinal:
        return "cardinal"
    elif sign in fixed:
        return "fixed"
    elif sign in mutable:
        return "mutable"
    return "unknown"


def planets_in_mutual_aspect(
    planet1: VargaPlanetData,
    planet2: VargaPlanetData
) -> bool:
    """
    Check if two planets are in mutual aspect.

    In Vedic astrology, all planets aspect 7th from them.
    Mars also aspects 4th and 8th.
    Jupiter also aspects 5th and 9th.
    Saturn also aspects 3rd and 10th.

    Args:
        planet1: First planet data
        planet2: Second planet data

    Returns:
        True if planets aspect each other
    """
    def get_aspects(planet: Planet) -> List[int]:
        """Get houses aspected from current position (1-indexed offset)"""
        base = [7]  # All planets aspect 7th
        if planet == Planet.MARS:
            base.extend([4, 8])
        elif planet == Planet.JUPITER:
            base.extend([5, 9])
        elif planet == Planet.SATURN:
            base.extend([3, 10])
        return base

    house1 = planet1.house
    house2 = planet2.house

    aspects1 = get_aspects(planet1.planet)
    aspects2 = get_aspects(planet2.planet)

    # Check if planet1 aspects planet2
    for asp in aspects1:
        target = ((house1 - 1 + asp) % 12) + 1
        if target == house2:
            # Now check if planet2 aspects planet1
            for asp2 in aspects2:
                target2 = ((house2 - 1 + asp2) % 12) + 1
                if target2 == house1:
                    return True

    return False


def is_kendra(house: int) -> bool:
    """Check if house is a kendra (1, 4, 7, 10)"""
    return house in [1, 4, 7, 10]


def is_trikona(house: int) -> bool:
    """Check if house is a trikona (1, 5, 9)"""
    return house in [1, 5, 9]


def is_dusthana(house: int) -> bool:
    """Check if house is a dusthana (6, 8, 12)"""
    return house in [6, 8, 12]


def is_upachaya(house: int) -> bool:
    """Check if house is an upachaya (3, 6, 10, 11)"""
    return house in [3, 6, 10, 11]
