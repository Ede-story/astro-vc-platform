"""
Navamsha Layer - Planet Scoring Phase 9

Evaluates planetary strength based on D9 (Navamsha) chart:
- Vargottama (same sign in D1 and D9)
- Pushkara Navamsha (auspicious D9 positions)
- D9 dignity (exalted/own/debilitated in D9)
- D9 aspects

Score range: -10 to +10 points
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..neecha_bhanga import (
    get_sign_number,
    EXALTATION_SIGNS,
    DEBILITATION_SIGNS,
    OWN_SIGNS,
)


# Pushkara Navamshas - most auspicious D9 positions
# These are specific degrees that fall in benefic navamshas
# Represented as navamsha sign numbers for each sign
PUSHKARA_NAVAMSHAS = {
    "Aries": [7, 9],      # Libra, Sagittarius navamshas
    "Taurus": [3, 5],     # Gemini, Leo navamshas
    "Gemini": [6, 8],     # Virgo, Scorpio navamshas
    "Cancer": [1, 3],     # Aries, Gemini navamshas
    "Leo": [5, 7],        # Leo, Libra navamshas
    "Virgo": [2, 4],      # Taurus, Cancer navamshas
    "Libra": [7, 9],      # Libra, Sagittarius navamshas
    "Scorpio": [3, 5],    # Gemini, Leo navamshas
    "Sagittarius": [6, 8], # Virgo, Scorpio navamshas
    "Capricorn": [1, 3],  # Aries, Gemini navamshas
    "Aquarius": [5, 7],   # Leo, Libra navamshas
    "Pisces": [2, 4],     # Taurus, Cancer navamshas
}

# Map navamsha number (1-9) to sign name
def get_navamsha_sign(d1_sign: str, navamsha_num: int) -> str:
    """Get the navamsha sign for a given D1 sign and navamsha number (1-9)"""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    # Starting navamsha depends on element of D1 sign
    # Fire (1,5,9): Start from Aries (0)
    # Earth (2,6,10): Start from Capricorn (9)
    # Air (3,7,11): Start from Libra (6)
    # Water (4,8,12): Start from Cancer (3)
    d1_num = get_sign_number(d1_sign)
    if d1_num in [1, 5, 9]:
        start = 0
    elif d1_num in [2, 6, 10]:
        start = 9
    elif d1_num in [3, 7, 11]:
        start = 6
    else:  # 4, 8, 12
        start = 3

    navamsha_sign_index = (start + navamsha_num - 1) % 12
    return signs[navamsha_sign_index]


@dataclass
class NavamshaResult:
    """Result of Navamsha analysis for a planet"""
    planet: str
    d1_sign: str
    d9_sign: str
    is_vargottama: bool
    is_pushkara: bool
    d9_dignity: str  # exalted, own, friend, neutral, enemy, debilitated
    score: float
    details: List[str]


class NavamshaLayer:
    """
    Calculates Navamsha-based scores for each planet

    Scoring:
    - Vargottama: +6
    - Pushkara Navamsha: +4
    - D9 Exalted: +4
    - D9 Own sign: +2
    - D9 Debilitated: -4
    """

    WEIGHT = 0.10  # 10% of total planet score

    def __init__(self, d1_data: Dict[str, Any], d9_data: Optional[Dict[str, Any]] = None):
        """
        Initialize Navamsha layer

        Args:
            d1_data: D1 chart data with planets
            d9_data: D9 chart data (if not provided, will calculate from D1)
        """
        self.d1 = d1_data
        self.d9 = d9_data
        self.planets_d1 = d1_data.get("planets", [])

        # Build D1 planet lookup
        self.d1_planet_data = {}
        for p in self.planets_d1:
            name = p.get("name", "")
            sign = p.get("sign_name") or p.get("sign", "")
            degree = p.get("degree_in_sign", 0) or p.get("longitude", 0) % 30
            self.d1_planet_data[name] = {"sign": sign, "degree": degree}

        # Build D9 planet lookup if D9 data is provided
        self.d9_planet_data = {}
        if d9_data:
            for p in d9_data.get("planets", []):
                name = p.get("name", "")
                sign = p.get("sign_name") or p.get("sign", "")
                self.d9_planet_data[name] = {"sign": sign}
        else:
            # Calculate D9 signs from D1 degrees
            for name, data in self.d1_planet_data.items():
                d1_sign = data.get("sign", "")
                degree = data.get("degree", 0)
                # Each navamsha is 3°20' = 3.333...°
                navamsha_num = int(degree / 3.333333) + 1
                if navamsha_num > 9:
                    navamsha_num = 9
                d9_sign = get_navamsha_sign(d1_sign, navamsha_num)
                self.d9_planet_data[name] = {"sign": d9_sign}

    def calculate(self) -> Dict[str, NavamshaResult]:
        """
        Calculate Navamsha-based scores for all planets

        Returns:
            Dict mapping planet name to NavamshaResult
        """
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if planet in self.d1_planet_data:
                results[planet] = self._analyze_planet(planet)
        return results

    def _analyze_planet(self, planet: str) -> NavamshaResult:
        """Analyze Navamsha for a single planet"""
        d1_data = self.d1_planet_data.get(planet, {})
        d9_data = self.d9_planet_data.get(planet, {})

        d1_sign = d1_data.get("sign", "")
        d9_sign = d9_data.get("sign", "")
        degree = d1_data.get("degree", 0)

        details = []
        score = 0.0

        # Check Vargottama (same sign in D1 and D9)
        is_vargottama = d1_sign == d9_sign
        if is_vargottama:
            score += 6.0
            details.append(f"VARGOTTAMA: {planet} in {d1_sign} in both D1 and D9: +6")

        # Check Pushkara Navamsha
        navamsha_num = int(degree / 3.333333) + 1
        if navamsha_num > 9:
            navamsha_num = 9
        pushkara_navamshas = PUSHKARA_NAVAMSHAS.get(d1_sign, [])
        is_pushkara = navamsha_num in pushkara_navamshas
        if is_pushkara:
            score += 4.0
            details.append(f"Pushkara Navamsha ({navamsha_num} of {d1_sign}): +4")

        # Check D9 dignity
        d9_dignity = self._get_d9_dignity(planet, d9_sign)
        if d9_dignity == "exalted":
            score += 4.0
            details.append(f"Exalted in D9 ({d9_sign}): +4")
        elif d9_dignity == "own":
            score += 2.0
            details.append(f"Own sign in D9 ({d9_sign}): +2")
        elif d9_dignity == "debilitated":
            score -= 4.0
            details.append(f"Debilitated in D9 ({d9_sign}): -4")

        if not details:
            details.append(f"{planet} in {d9_sign} (D9): neutral")

        return NavamshaResult(
            planet=planet,
            d1_sign=d1_sign,
            d9_sign=d9_sign,
            is_vargottama=is_vargottama,
            is_pushkara=is_pushkara,
            d9_dignity=d9_dignity,
            score=score,
            details=details
        )

    def _get_d9_dignity(self, planet: str, d9_sign: str) -> str:
        """Determine dignity of planet in D9"""
        if d9_sign == EXALTATION_SIGNS.get(planet):
            return "exalted"
        if d9_sign == DEBILITATION_SIGNS.get(planet):
            return "debilitated"
        if d9_sign in OWN_SIGNS.get(planet, []):
            return "own"
        return "neutral"

    def get_score(self, planet: str) -> float:
        """Get the Navamsha score for a specific planet"""
        results = self.calculate()
        if planet in results:
            return results[planet].score
        return 0.0

    def get_all_scores(self) -> Dict[str, float]:
        """Get Navamsha scores for all planets"""
        results = self.calculate()
        return {planet: result.score for planet, result in results.items()}
