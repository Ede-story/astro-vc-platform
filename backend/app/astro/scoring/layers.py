"""
House Scoring Layers - Each layer contributes to the final house score

Layer 1 (D1): Base scores from D1 chart (40%)
Layer 2 (D9): Navamsha modifications (20%)
Layer 3 (Varga): Multi-varga strength (15%)
Layer 4 (Yoga): Yoga impact per house (15%)
Layer 5 (Jaimini): Chara karaka influences (10%)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .neecha_bhanga import NeechaBhangaAnalyzer, DEBILITATION_SIGNS


# Planetary dignities and strengths
EXALTATION_SIGNS = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio"
}

DEBILITATION_SIGNS = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries", "Rahu": "Scorpio", "Ketu": "Taurus"
}

OWN_SIGNS = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"],
    "Rahu": ["Aquarius"],
    "Ketu": ["Scorpio"]
}

MOOLATRIKONA_SIGNS = {
    "Sun": ("Leo", 0, 20),  # (sign, start_degree, end_degree)
    "Moon": ("Taurus", 3, 30),
    "Mars": ("Aries", 0, 12),
    "Mercury": ("Virgo", 15, 20),
    "Jupiter": ("Sagittarius", 0, 10),
    "Venus": ("Libra", 0, 15),
    "Saturn": ("Aquarius", 0, 20),
}

# Benefic/Malefic classification
NATURAL_BENEFICS = ["Jupiter", "Venus", "Mercury", "Moon"]
NATURAL_MALEFICS = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]

# House lords by ascending sign
HOUSE_LORDS = {
    "Aries": ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"],
    "Taurus": ["Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter", "Mars"],
    "Gemini": ["Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter", "Mars", "Venus"],
    "Cancer": ["Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter", "Mars", "Venus", "Mercury"],
    "Leo": ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter", "Mars", "Venus", "Mercury", "Moon"],
    "Virgo": ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter", "Mars", "Venus", "Mercury", "Moon", "Sun"],
    "Libra": ["Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter", "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury"],
    "Scorpio": ["Mars", "Jupiter", "Saturn", "Saturn", "Jupiter", "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus"],
    "Sagittarius": ["Jupiter", "Saturn", "Saturn", "Jupiter", "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars"],
    "Capricorn": ["Saturn", "Saturn", "Jupiter", "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter"],
    "Aquarius": ["Saturn", "Jupiter", "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"],
    "Pisces": ["Jupiter", "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn"],
}

# Aspect rules (degrees where planets cast aspect)
ASPECT_RULES = {
    "Sun": [7],
    "Moon": [7],
    "Mercury": [7],
    "Venus": [7],
    "Mars": [4, 7, 8],
    "Jupiter": [5, 7, 9],
    "Saturn": [3, 7, 10],
    "Rahu": [5, 7, 9],
    "Ketu": [5, 7, 9],
}


def get_sign_number(sign: str) -> int:
    """Convert sign name to number (1-12)"""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    try:
        return signs.index(sign) + 1
    except ValueError:
        return 1


def get_sign_name(num: int) -> str:
    """Convert sign number (1-12) to name"""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return signs[(num - 1) % 12]


@dataclass
class LayerResult:
    """Result from a scoring layer"""
    scores: Dict[int, float]  # house_num -> score contribution
    details: Dict[int, List[str]]  # house_num -> list of reasons


class D1Layer:
    """
    Layer 1: D1 (Rashi) Base Scores (40% weight)

    Scoring factors:
    - Planetary occupancy (+3-10 based on benefic/malefic and dignity)
    - House lord placement and dignity (+5-15)
    - Aspects received (+2-8)
    - Kendras/Trikonas have base bonus (+5)
    - Neecha Bhanga Raja Yoga (cancellation of debilitation)
    """

    WEIGHT = 0.40

    def __init__(self, d1_data: Dict[str, Any], d9_data: Optional[Dict[str, Any]] = None):
        self.d1 = d1_data
        self.d9 = d9_data
        self.planets = d1_data.get("planets", [])
        self.ascendant = d1_data.get("ascendant", {})
        # Support both 'sign' and 'sign_name' field names
        self.asc_sign = self.ascendant.get("sign_name") or self.ascendant.get("sign", "Aries")

        # Initialize Neecha Bhanga analyzer
        self.neecha_bhanga_analyzer = NeechaBhangaAnalyzer(d1_data, d9_data)
        self.neecha_bhanga_results = {r.planet: r for r in self.neecha_bhanga_analyzer.analyze_all()}

    def calculate(self) -> LayerResult:
        scores = {h: 0.0 for h in range(1, 13)}
        details = {h: [] for h in range(1, 13)}

        # 1. Base bonuses for Kendras (1,4,7,10) and Trikonas (1,5,9)
        for h in [1, 4, 7, 10]:
            scores[h] += 5.0  # Increased from 3.0
            details[h].append("Kendra house (+5)")
        for h in [5, 9]:
            scores[h] += 4.0  # Increased from 2.0
            details[h].append("Trikona house (+4)")

        # 2. Penalty for Dusthanas (6, 8, 12) - reduced penalty
        for h in [6, 8, 12]:
            scores[h] -= 1.0  # Reduced from -2.0
            details[h].append("Dusthana house (-1)")

        # 3. Analyze each planet and track house occupancy for conjunction bonus
        planet_houses = self._get_planet_houses()
        house_planet_count = {h: [] for h in range(1, 13)}

        for planet_name, house_num in planet_houses.items():
            if house_num < 1 or house_num > 12:
                continue

            planet_data = self._get_planet_data(planet_name)
            if not planet_data:
                continue

            # Track planets per house for conjunction bonus
            house_planet_count[house_num].append(planet_name)

            # Use sign_name or sign field
            sign = planet_data.get("sign_name") or planet_data.get("sign", "")
            degree = planet_data.get("relative_degree") or planet_data.get("degree", 0)
            dignity = planet_data.get("dignity_state", "")

            # Occupancy bonus/penalty - use pre-computed dignity when available
            occ_score = self._calculate_occupancy_score(planet_name, sign, degree, dignity)
            scores[house_num] += occ_score

            # Add Neecha Bhanga detail if applicable
            nb_result = self.neecha_bhanga_results.get(planet_name)
            if nb_result:
                if nb_result.is_raja_yoga:
                    details[house_num].append(f"{planet_name} Neecha Bhanga Raja Yoga! ({nb_result.count} rules, {occ_score:+.1f})")
                elif nb_result.count > 0:
                    details[house_num].append(f"{planet_name} Neecha Bhanga ({nb_result.count} rules, {occ_score:+.1f})")
                else:
                    details[house_num].append(f"{planet_name} debilitated ({occ_score:+.1f})")
            else:
                details[house_num].append(f"{planet_name} occupies ({occ_score:+.1f})")

            # Aspects from this planet
            for aspect_house in self._get_aspect_houses(house_num, planet_name):
                if 1 <= aspect_house <= 12:
                    asp_score = self._calculate_aspect_score(planet_name, sign)
                    scores[aspect_house] += asp_score
                    details[aspect_house].append(f"{planet_name} aspects from H{house_num} ({asp_score:+.1f})")

        # 4. House lord analysis
        lord_scores = self._calculate_lord_scores()
        for h, (score, reason) in lord_scores.items():
            scores[h] += score
            if reason:
                details[h].append(reason)

        # 5. Conjunction bonus - multiple planets in same house creates power concentration
        for house_num, planets in house_planet_count.items():
            if len(planets) >= 2:
                # More planets = more power (Sun+Rahu in 10th = very powerful)
                conj_bonus = (len(planets) - 1) * 5.0
                # Extra bonus if conjunction includes exalted/own sign planet
                has_strong_planet = False
                for p in planets:
                    pd = self._get_planet_data(p)
                    if pd:
                        dignity = pd.get("dignity_state", "").lower()
                        if "exalt" in dignity or "own" in dignity:
                            has_strong_planet = True
                            break
                if has_strong_planet:
                    conj_bonus += 5.0
                    details[house_num].append(f"Strong conjunction: {', '.join(planets)} (+{conj_bonus:.0f})")
                else:
                    details[house_num].append(f"Conjunction: {', '.join(planets)} (+{conj_bonus:.0f})")
                scores[house_num] += conj_bonus

        return LayerResult(scores=scores, details=details)

    def _get_planet_houses(self) -> Dict[str, int]:
        """Get house number for each planet"""
        result = {}

        for p in self.planets:
            name = p.get("name", "")
            # Use pre-calculated house_occupied if available, otherwise calculate
            house = p.get("house_occupied") or p.get("house")
            if not house:
                # Fallback: calculate from sign
                sign = p.get("sign_name") or p.get("sign", "")
                if sign:
                    asc_num = get_sign_number(self.asc_sign)
                    sign_num = get_sign_number(sign)
                    house = ((sign_num - asc_num) % 12) + 1
            if house and 1 <= house <= 12:
                result[name] = house

        return result

    def _get_planet_data(self, name: str) -> Optional[Dict]:
        for p in self.planets:
            if p.get("name") == name:
                return p
        return None

    def _calculate_occupancy_score(self, planet: str, sign: str, degree: float = 0, dignity: str = "") -> float:
        """Score for planet occupying a house based on dignity - enhanced for exceptional charts"""
        # Higher base for benefics, less penalty for malefics
        base = 3.0 if planet in NATURAL_BENEFICS else 0.0

        # Check for Neecha Bhanga first - this replaces the simple debilitation penalty
        nb_result = self.neecha_bhanga_results.get(planet)
        if nb_result:
            # Planet is debilitated - use Neecha Bhanga score instead of fixed penalty
            return base + nb_result.score_modifier

        # Use pre-computed dignity state if available
        dignity_lower = dignity.lower() if dignity else ""
        if "exalt" in dignity_lower:
            # Exaltation is very powerful - big boost
            return base + 12.0
        if "debilit" in dignity_lower or "fall" in dignity_lower:
            # Double-check with Neecha Bhanga (should have been caught above)
            if planet in self.neecha_bhanga_results:
                return base + self.neecha_bhanga_results[planet].score_modifier
            return base - 4.0  # Reduced penalty
        if "own" in dignity_lower:
            return base + 10.0  # Increased from 5.0
        if "moolatrikona" in dignity_lower:
            return base + 11.0  # Increased from 6.0
        if "friend" in dignity_lower:
            return base + 6.0  # Increased from 3.0
        if "enemy" in dignity_lower:
            return base - 1.0  # Reduced penalty from -2.0
        if "neutral" in dignity_lower:
            return base + 2.0

        # Fallback: calculate from sign if no dignity provided
        # Exaltation
        if EXALTATION_SIGNS.get(planet) == sign:
            return base + 12.0

        # Debilitation - check Neecha Bhanga
        if DEBILITATION_SIGNS.get(planet) == sign:
            if planet in self.neecha_bhanga_results:
                return base + self.neecha_bhanga_results[planet].score_modifier
            return base - 4.0

        # Own sign
        if sign in OWN_SIGNS.get(planet, []):
            return base + 10.0

        # Moolatrikona
        mt = MOOLATRIKONA_SIGNS.get(planet)
        if mt and mt[0] == sign and mt[1] <= degree <= mt[2]:
            return base + 11.0

        return base

    def _get_aspect_houses(self, from_house: int, planet: str) -> List[int]:
        """Get houses aspected by planet from given house"""
        aspects = ASPECT_RULES.get(planet, [7])
        return [(from_house + asp - 1) % 12 + 1 for asp in aspects]

    def _calculate_aspect_score(self, planet: str, sign: str) -> float:
        """Score for aspect - benefics give positive, malefics negative unless dignified"""
        if planet in NATURAL_BENEFICS:
            return 3.0
        else:
            if EXALTATION_SIGNS.get(planet) == sign or sign in OWN_SIGNS.get(planet, []):
                return 1.5  # Dignified malefic aspects are less harmful
            return -1.5

    def _calculate_lord_scores(self) -> Dict[int, tuple]:
        """Calculate scores based on house lord placements"""
        result = {}
        lords = HOUSE_LORDS.get(self.asc_sign, HOUSE_LORDS["Aries"])
        planet_houses = self._get_planet_houses()

        for house_num in range(1, 13):
            lord = lords[house_num - 1]
            lord_house = planet_houses.get(lord, 0)

            if lord_house == 0:
                result[house_num] = (0, "")
                continue

            lord_data = self._get_planet_data(lord)
            lord_sign = lord_data.get("sign", "") if lord_data else ""

            # Lord in own house
            if lord_house == house_num:
                result[house_num] = (8.0, f"Lord {lord} in own house (+8)")
                continue

            # Lord in kendra from house
            kendras_from = [(house_num + k - 1) % 12 + 1 for k in [1, 4, 7, 10]]
            if lord_house in kendras_from:
                score = 5.0
                if EXALTATION_SIGNS.get(lord) == lord_sign:
                    score += 3.0
                result[house_num] = (score, f"Lord {lord} in kendra H{lord_house} (+{score:.0f})")
                continue

            # Lord in trikona from house
            trikonas_from = [(house_num + k - 1) % 12 + 1 for k in [1, 5, 9]]
            if lord_house in trikonas_from:
                score = 4.0
                result[house_num] = (score, f"Lord {lord} in trikona H{lord_house} (+4)")
                continue

            # Lord in dusthana (6, 8, 12 from house)
            dusthanas_from = [(house_num + k - 1) % 12 + 1 for k in [6, 8, 12]]
            if lord_house in dusthanas_from:
                score = -4.0
                # Check for Viparita Raja Yoga (dusthana lord in dusthana)
                if house_num in [6, 8, 12]:
                    score = 2.0  # Viparita - dusthana lord in dusthana is good
                result[house_num] = (score, f"Lord {lord} in H{lord_house} ({score:+.0f})")
                continue

            result[house_num] = (0, "")

        return result


class D9Layer:
    """
    Layer 2: D9 (Navamsha) Modifications (20% weight)

    Scoring factors:
    - Vargottama planets (+10 to house they occupy)
    - D9 lord placement
    - Pushkara navamsha (+5)
    - D9 planet dignity
    """

    WEIGHT = 0.20

    def __init__(self, d1_data: Dict, d9_data: Dict):
        self.d1 = d1_data
        self.d9 = d9_data
        self.d1_planets = d1_data.get("planets", [])
        self.d9_planets = d9_data.get("planets", [])
        self.d1_asc = d1_data.get("ascendant", {}).get("sign", "Aries")

    def calculate(self) -> LayerResult:
        scores = {h: 0.0 for h in range(1, 13)}
        details = {h: [] for h in range(1, 13)}

        asc_num = get_sign_number(self.d1_asc)

        # Check each planet
        for d1_planet in self.d1_planets:
            name = d1_planet.get("name", "")
            d1_sign = d1_planet.get("sign", "")

            # Find corresponding D9 planet
            d9_planet = None
            for p in self.d9_planets:
                if p.get("name") == name:
                    d9_planet = p
                    break

            if not d9_planet:
                continue

            d9_sign = d9_planet.get("sign", "")

            # Calculate house in D1
            sign_num = get_sign_number(d1_sign)
            house = ((sign_num - asc_num) % 12) + 1

            # Vargottama check
            if d1_sign == d9_sign:
                scores[house] += 8.0
                details[house].append(f"{name} Vargottama (+8)")

            # D9 dignity bonus
            if EXALTATION_SIGNS.get(name) == d9_sign:
                scores[house] += 5.0
                details[house].append(f"{name} exalted in D9 (+5)")
            elif d9_sign in OWN_SIGNS.get(name, []):
                scores[house] += 3.0
                details[house].append(f"{name} own sign in D9 (+3)")
            elif DEBILITATION_SIGNS.get(name) == d9_sign:
                scores[house] -= 3.0
                details[house].append(f"{name} debilitated in D9 (-3)")

        # Check Pushkara navamshas (specific degrees that are auspicious)
        pushkara_degrees = self._get_pushkara_planets()
        for planet, house in pushkara_degrees.items():
            if house:
                scores[house] += 4.0
                details[house].append(f"{planet} in Pushkara navamsha (+4)")

        return LayerResult(scores=scores, details=details)

    def _get_pushkara_planets(self) -> Dict[str, Optional[int]]:
        """Check which planets are in Pushkara navamsha"""
        result = {}
        asc_num = get_sign_number(self.d1_asc)

        # Pushkara navamsha degrees per sign
        pushkara = {
            "Aries": [21, 24], "Taurus": [14, 18], "Gemini": [18, 22],
            "Cancer": [8, 11], "Leo": [21, 24], "Virgo": [14, 18],
            "Libra": [18, 22], "Scorpio": [8, 11], "Sagittarius": [21, 24],
            "Capricorn": [14, 18], "Aquarius": [18, 22], "Pisces": [8, 11]
        }

        for p in self.d1_planets:
            name = p.get("name", "")
            sign = p.get("sign", "")
            degree = p.get("degree", 0)

            if sign in pushkara:
                if any(abs(degree - pd) < 2 for pd in pushkara[sign]):
                    sign_num = get_sign_number(sign)
                    house = ((sign_num - asc_num) % 12) + 1
                    result[name] = house
                else:
                    result[name] = None
            else:
                result[name] = None

        return result


class VargaLayer:
    """
    Layer 3: Multi-Varga Strength (15% weight)

    Uses Shad Varga or Sapta Varga strength:
    - Check planet dignity across D1, D2, D3, D9, D12, D30
    - Count how many vargas planet is strong in
    """

    WEIGHT = 0.15

    def __init__(self, vargas: Dict[str, Dict]):
        self.vargas = vargas
        self.d1 = vargas.get("D1", {})

    def calculate(self) -> LayerResult:
        scores = {h: 0.0 for h in range(1, 13)}
        details = {h: [] for h in range(1, 13)}

        d1_asc = self.d1.get("ascendant", {}).get("sign", "Aries")
        asc_num = get_sign_number(d1_asc)

        # Key vargas to check
        varga_keys = ["D1", "D2", "D3", "D9", "D10", "D12"]

        # Get planets from D1
        d1_planets = self.d1.get("planets", [])

        for planet_d1 in d1_planets:
            name = planet_d1.get("name", "")
            d1_sign = planet_d1.get("sign", "")

            if not d1_sign:
                continue

            # Calculate D1 house
            sign_num = get_sign_number(d1_sign)
            house = ((sign_num - asc_num) % 12) + 1

            # Count strong placements across vargas
            strong_count = 0
            for varga_key in varga_keys:
                varga = self.vargas.get(varga_key, {})
                varga_planets = varga.get("planets", [])

                for vp in varga_planets:
                    if vp.get("name") == name:
                        vp_sign = vp.get("sign", "")
                        if self._is_strong(name, vp_sign):
                            strong_count += 1
                        break

            # Score based on varga strength count
            if strong_count >= 5:
                scores[house] += 8.0
                details[house].append(f"{name} strong in {strong_count} vargas (+8)")
            elif strong_count >= 4:
                scores[house] += 5.0
                details[house].append(f"{name} strong in {strong_count} vargas (+5)")
            elif strong_count >= 3:
                scores[house] += 3.0
                details[house].append(f"{name} strong in {strong_count} vargas (+3)")

        return LayerResult(scores=scores, details=details)

    def _is_strong(self, planet: str, sign: str) -> bool:
        """Check if planet is strong in given sign"""
        if EXALTATION_SIGNS.get(planet) == sign:
            return True
        if sign in OWN_SIGNS.get(planet, []):
            return True
        return False


class YogaLayer:
    """
    Layer 4: Yoga Impact on Houses (15% weight)

    Analyzes yogas and their impact on specific houses
    """

    WEIGHT = 0.15

    # Yoga to house mapping
    YOGA_HOUSE_IMPACT = {
        # Wealth yogas -> 2nd, 11th houses
        "Dhana Yoga": [2, 11],
        "Lakshmi Yoga": [2, 9],

        # Power yogas -> 1st, 10th houses
        "Raja Yoga": [1, 10],
        "Pancha Mahapurusha": [1, 10],
        "Hamsa Yoga": [1, 10],
        "Malavya Yoga": [1, 7],
        "Bhadra Yoga": [1, 3],
        "Ruchaka Yoga": [1, 10],
        "Shasha Yoga": [1, 10],

        # Knowledge yogas -> 5th, 9th houses
        "Saraswati Yoga": [5, 9],
        "Budhaditya Yoga": [5, 3],

        # Marriage/relationship yogas -> 7th house
        "Shubha Kartari": [7],

        # General auspicious
        "Gajakesari Yoga": [1, 4, 7, 10],
        "Chandra-Mangala Yoga": [2, 11],
        "Neecha Bhanga Raja Yoga": [1, 10],

        # Spiritual yogas
        "Kemadruma Yoga": [12],  # Usually negative
        "Pravrajya Yoga": [12, 9],
    }

    def __init__(self, yogas: List[Dict]):
        self.yogas = yogas

    def calculate(self) -> LayerResult:
        scores = {h: 0.0 for h in range(1, 13)}
        details = {h: [] for h in range(1, 13)}

        for yoga in self.yogas:
            yoga_name = yoga.get("name", "")
            strength = yoga.get("strength", 50) / 100.0  # Normalize to 0-1
            is_formed = yoga.get("is_formed", False) or yoga.get("formed", False)

            if not is_formed:
                continue

            # Find which houses this yoga impacts
            impacted_houses = []
            for key, houses in self.YOGA_HOUSE_IMPACT.items():
                if key.lower() in yoga_name.lower():
                    impacted_houses = houses
                    break

            # If no specific mapping, check yoga description for house mentions
            if not impacted_houses:
                description = yoga.get("description", "").lower()
                for h in range(1, 13):
                    if f"{h}th house" in description or f"house {h}" in description:
                        impacted_houses.append(h)

                # Default to 1st and 10th if still no houses found
                if not impacted_houses:
                    impacted_houses = [1]

            # Apply yoga score to houses
            base_score = 5.0 * strength
            for house in impacted_houses:
                if 1 <= house <= 12:
                    scores[house] += base_score
                    details[house].append(f"{yoga_name} ({base_score:.1f})")

        return LayerResult(scores=scores, details=details)


class JaiminiLayer:
    """
    Layer 5: Jaimini Chara Karaka Influences (10% weight)

    Analyzes impact of Atmakaraka, Amatyakaraka, etc on houses
    Enhanced: AK in 10th = massive career boost (billionaire indicator)
    """

    WEIGHT = 0.10

    # Karaka significance for houses
    KARAKA_HOUSE_SIGNIFICANCE = {
        "AK": [1, 12],      # Atmakaraka - self, moksha
        "AmK": [10, 2],     # Amatyakaraka - career, wealth
        "BK": [3, 11],      # Bhratrikaraka - siblings, gains
        "MK": [4],          # Matrikaraka - mother, property
        "PK": [5, 9],       # Putrakaraka - children, fortune
        "GK": [6, 8],       # Gnatikaraka - enemies, obstacles
        "DK": [7],          # Darakaraka - spouse
    }

    def __init__(self, jaimini_data: Dict, d1_data: Dict):
        self.jaimini = jaimini_data
        self.d1 = d1_data

    def calculate(self) -> LayerResult:
        scores = {h: 0.0 for h in range(1, 13)}
        details = {h: [] for h in range(1, 13)}

        karakas = self.jaimini.get("karakas", [])
        d1_asc = self.d1.get("ascendant", {}).get("sign_name") or self.d1.get("ascendant", {}).get("sign", "Aries")
        asc_num = get_sign_number(d1_asc)

        # Create planet -> house mapping from D1
        planet_houses = {}
        for p in self.d1.get("planets", []):
            name = p.get("name", "")
            # Use house_occupied if available
            house = p.get("house_occupied")
            if not house:
                sign = p.get("sign_name") or p.get("sign", "")
                if sign:
                    sign_num = get_sign_number(sign)
                    house = ((sign_num - asc_num) % 12) + 1
            if house:
                planet_houses[name] = house

        for karaka in karakas:
            code = karaka.get("karaka_code", "")
            planet = karaka.get("planet", "")
            degrees = karaka.get("degrees_in_sign", 0)

            # Get house where this karaka planet sits
            house = planet_houses.get(planet, 0)
            if house == 0:
                continue

            # Houses this karaka is significant for
            significant_houses = self.KARAKA_HOUSE_SIGNIFICANCE.get(code, [])

            # Score based on karaka strength (higher degrees = stronger)
            strength_factor = degrees / 30.0  # Normalize to 0-1

            # Enhanced: AK placement is VERY significant
            if code == "AK":
                # AK in kendra (1,4,7,10) is extremely powerful
                if house in [1, 4, 7, 10]:
                    ak_bonus = 15.0 * strength_factor
                    scores[house] += ak_bonus
                    details[house].append(f"AK ({planet}) in kendra - very powerful (+{ak_bonus:.1f})")
                    # Extra bonus for 10th - career house with soul planet
                    if house == 10:
                        extra = 10.0 * strength_factor
                        scores[house] += extra
                        details[house].append(f"AK in 10th = destined for public prominence (+{extra:.1f})")
                else:
                    base_score = 8.0 * strength_factor
                    scores[house] += base_score
                    details[house].append(f"AK ({planet}) placed here ({base_score:.1f})")
            # AmK (career karaka) also gets boost in 10th
            elif code == "AmK":
                if house == 10:
                    amk_bonus = 12.0 * strength_factor
                    scores[house] += amk_bonus
                    details[house].append(f"AmK ({planet}) in 10th - strong career (+{amk_bonus:.1f})")
                else:
                    base_score = 6.0 * strength_factor
                    scores[house] += base_score
                    details[house].append(f"AmK ({planet}) placed here ({base_score:.1f})")
            else:
                # Other karakas
                base_score = 5.0 * strength_factor
                scores[house] += base_score
                details[house].append(f"{code} ({planet}) placed here ({base_score:.1f})")

            # Bonus to houses karaka signifies
            for sig_house in significant_houses:
                if sig_house != house:  # Don't double count
                    sig_score = 4.0 * strength_factor
                    scores[sig_house] += sig_score
                    details[sig_house].append(f"{code} signifies this house ({sig_score:.1f})")

        return LayerResult(scores=scores, details=details)
