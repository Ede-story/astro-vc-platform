"""
Bhava Bala Layer - Traditional House Strength Calculation (±15 points)

7 components of Bhava Bala (House Strength):
1. Bhavadhipati Bala - House lord strength (25%)
2. Bhava Digbala - Directional strength (15%)
3. Bhava Drishti Bala - Aspect strength (20%)
4. Bhava Madhya Bala - Mid-cusp proximity (10%)
5. Bhava Argala Bala - Intervention strength (10%)
6. Bhava Ashtakavarga - House bindu count (15%)
7. Bhava Yoga Bala - Yoga influence on house (5%)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class BhavaBalaResult:
    """Result from Bhava Bala layer for one house"""
    house: int
    total_score: float
    components: Dict[str, float]
    details: List[str]


# Alias for backwards compatibility
BhavaResult = BhavaBalaResult


# Sign number mapping
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# House lords by ascendant
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

# Digbala (Directional strength) - planets strong in specific houses
DIGBALA = {
    "Sun": 10,      # Strong in 10th
    "Moon": 4,      # Strong in 4th
    "Mars": 10,     # Strong in 10th
    "Mercury": 1,   # Strong in 1st
    "Jupiter": 1,   # Strong in 1st
    "Venus": 4,     # Strong in 4th
    "Saturn": 7,    # Strong in 7th
}

# Exaltation signs
EXALTATION_SIGNS = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio"
}

# Own signs
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

# Benefics
NATURAL_BENEFICS = ["Jupiter", "Venus", "Mercury", "Moon"]


def get_sign_number(sign: str) -> int:
    """Convert sign name to number (1-12)"""
    try:
        return SIGNS.index(sign) + 1
    except ValueError:
        return 1


class BhavaBalaLayer:
    """
    Phase 8.5 Layer: Bhava Bala House Strength (±15 points)

    Traditional Vedic calculation of house strength using 7 components.
    """

    WEIGHT = 0.10  # 10% weight in final calculation
    MAX_POINTS = 15.0  # Maximum contribution ±15 points

    # Component weights (total = 100%)
    COMPONENT_WEIGHTS = {
        "bhavadhipati": 0.25,   # House lord strength
        "digbala": 0.15,        # Directional strength
        "drishti": 0.20,        # Aspect strength
        "madhya": 0.10,         # Mid-cusp proximity
        "argala": 0.10,         # Intervention
        "ashtakavarga": 0.15,   # Bindu count
        "yoga": 0.05,           # Yoga influence
    }

    def __init__(
        self,
        chart_data: Dict[str, Any],
        ashtakavarga_data: Optional[Dict] = None,
        yogas: Optional[List[Dict]] = None
    ):
        # Handle both direct D1 data and wrapper format with vargas/D1 keys
        if 'vargas' in chart_data:
            self.d1 = chart_data.get('vargas', {}).get('D1', {})
        elif 'D1' in chart_data:
            self.d1 = chart_data.get('D1', {})
        else:
            # Assume it's D1 data directly
            self.d1 = chart_data

        self.planets = self.d1.get("planets", [])
        self.ascendant = self.d1.get("ascendant", {})
        self.asc_sign = self.ascendant.get("sign_name") or self.ascendant.get("sign", "Aries")
        self.ashtakavarga = ashtakavarga_data or {}
        self.yogas = yogas or []

        # Build planet position map
        self.planet_houses = self._build_planet_houses()
        self.planet_signs = self._build_planet_signs()

    def _build_planet_houses(self) -> Dict[str, int]:
        """Build mapping of planet -> house number"""
        result = {}
        asc_num = get_sign_number(self.asc_sign)

        for p in self.planets:
            name = p.get("name", "")
            house = p.get("house_occupied")
            if not house:
                sign = p.get("sign_name") or p.get("sign", "")
                if sign:
                    sign_num = get_sign_number(sign)
                    house = ((sign_num - asc_num) % 12) + 1
            if house and 1 <= house <= 12:
                result[name] = house

        return result

    def _build_planet_signs(self) -> Dict[str, str]:
        """Build mapping of planet -> sign"""
        result = {}
        for p in self.planets:
            name = p.get("name", "")
            sign = p.get("sign_name") or p.get("sign", "")
            if sign:
                result[name] = sign
        return result

    def calculate(self) -> Dict[int, BhavaBalaResult]:
        """
        Calculate Bhava Bala for all 12 houses.

        Returns:
            Dict mapping house number to BhavaResult
        """
        results = {}

        for house in range(1, 13):
            components = {
                "bhavadhipati": self._calc_bhavadhipati_bala(house),
                "digbala": self._calc_bhava_digbala(house),
                "drishti": self._calc_bhava_drishti_bala(house),
                "madhya": self._calc_bhava_madhya_bala(house),
                "argala": self._calc_bhava_argala_bala(house),
                "ashtakavarga": self._calc_bhava_ashtakavarga(house),
                "yoga": self._calc_bhava_yoga_bala(house),
            }

            # Calculate weighted total
            total = sum(
                score * self.COMPONENT_WEIGHTS[comp]
                for comp, score in components.items()
            )

            # Normalize to ±15 range
            # Raw total is 0-100, map to -15 to +15
            normalized = (total - 50) * (self.MAX_POINTS / 50)
            normalized = max(-self.MAX_POINTS, min(self.MAX_POINTS, normalized))

            # Build details
            details = []
            if components["bhavadhipati"] > 60:
                details.append(f"Strong house lord (+{components['bhavadhipati']:.0f}%)")
            if components["digbala"] > 70:
                details.append(f"Good directional strength (+{components['digbala']:.0f}%)")
            if components["drishti"] > 60:
                details.append(f"Beneficial aspects (+{components['drishti']:.0f}%)")
            if components["argala"] > 60:
                details.append(f"Strong argala support (+{components['argala']:.0f}%)")

            results[house] = BhavaBalaResult(
                house=house,
                total_score=round(normalized, 2),
                components=components,
                details=details
            )

        return results

    def _calc_bhavadhipati_bala(self, house: int) -> float:
        """
        Calculate Bhavadhipati Bala - strength of house lord.

        Factors:
        - Lord's dignity (exalted, own sign, friend, etc.)
        - Lord's house placement
        - Lord's aspects

        Returns:
            Score 0-100
        """
        lords = HOUSE_LORDS.get(self.asc_sign, HOUSE_LORDS["Aries"])
        lord = lords[house - 1]

        score = 50.0  # Base

        # Lord's sign dignity
        lord_sign = self.planet_signs.get(lord, "")
        if EXALTATION_SIGNS.get(lord) == lord_sign:
            score += 30
        elif lord_sign in OWN_SIGNS.get(lord, []):
            score += 25

        # Lord's house placement
        lord_house = self.planet_houses.get(lord, 0)
        if lord_house == house:
            score += 15  # Lord in own house
        elif lord_house in [1, 4, 7, 10]:  # Kendras
            score += 10
        elif lord_house in [5, 9]:  # Trikonas
            score += 8
        elif lord_house in [6, 8, 12]:  # Dusthanas
            score -= 15

        return max(0, min(100, score))

    def _calc_bhava_digbala(self, house: int) -> float:
        """
        Calculate Bhava Digbala - directional strength from planets.

        Planets in houses where they have digbala strengthen those houses.

        Returns:
            Score 0-100
        """
        score = 50.0  # Base

        # Check planets in this house
        for planet, p_house in self.planet_houses.items():
            if p_house == house:
                # Planet is in this house
                digbala_house = DIGBALA.get(planet, 0)
                if digbala_house == house:
                    score += 25  # Planet has digbala here
                elif planet in NATURAL_BENEFICS:
                    score += 10  # Benefic occupies
                else:
                    score += 3  # Any planet occupying

        # Check if this house IS a digbala house for any planet occupying it
        for planet, strong_house in DIGBALA.items():
            if strong_house == house and planet in self.planet_houses:
                if self.planet_houses[planet] == house:
                    score += 15  # This planet has maximum digbala here

        return max(0, min(100, score))

    def _calc_bhava_drishti_bala(self, house: int) -> float:
        """
        Calculate Bhava Drishti Bala - aspect strength.

        Beneficial aspects increase score, malefic decrease.

        Returns:
            Score 0-100
        """
        score = 50.0  # Base

        # Aspect rules (houses aspected from planet's position)
        aspect_rules = {
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

        for planet, p_house in self.planet_houses.items():
            aspects = aspect_rules.get(planet, [7])

            for asp in aspects:
                aspected_house = ((p_house + asp - 1) % 12) + 1
                if aspected_house == house:
                    # This planet aspects our house
                    planet_sign = self.planet_signs.get(planet, "")

                    if planet in NATURAL_BENEFICS:
                        # Benefic aspect
                        if EXALTATION_SIGNS.get(planet) == planet_sign:
                            score += 15
                        elif planet_sign in OWN_SIGNS.get(planet, []):
                            score += 12
                        else:
                            score += 8
                    else:
                        # Malefic aspect
                        if EXALTATION_SIGNS.get(planet) == planet_sign:
                            score += 3  # Dignified malefic is less harmful
                        else:
                            score -= 5

        return max(0, min(100, score))

    def _calc_bhava_madhya_bala(self, house: int) -> float:
        """
        Calculate Bhava Madhya Bala - mid-cusp proximity strength.

        Planets closer to bhava madhya (mid-point) are stronger.

        Returns:
            Score 0-100
        """
        score = 50.0  # Base

        # Check planets in this house and their degree proximity to mid-cusp
        for p in self.planets:
            p_house = p.get("house_occupied")
            if not p_house:
                sign = p.get("sign_name") or p.get("sign", "")
                if sign:
                    asc_num = get_sign_number(self.asc_sign)
                    sign_num = get_sign_number(sign)
                    p_house = ((sign_num - asc_num) % 12) + 1

            if p_house == house:
                degree = p.get("relative_degree") or p.get("degree", 15)
                # Mid-cusp is at 15 degrees
                proximity = 15 - abs(degree - 15)
                # 0-15 proximity maps to 0-20 bonus
                score += (proximity / 15) * 20

        return max(0, min(100, score))

    def _calc_bhava_argala_bala(self, house: int) -> float:
        """
        Calculate Bhava Argala Bala - intervention strength.

        Argala: Planets in 2nd, 4th, 11th from a house intervene (support).
        Virodha argala: Planets in 12th, 10th, 3rd obstruct.

        Returns:
            Score 0-100
        """
        score = 50.0  # Base

        # Argala houses (support)
        argala_offsets = [2, 4, 11]  # 2nd, 4th, 11th from house

        # Virodha argala (obstruction)
        virodha_offsets = [12, 10, 3]  # 12th, 10th, 3rd from house

        argala_count = 0
        virodha_count = 0

        for offset in argala_offsets:
            argala_house = ((house + offset - 1) % 12) + 1
            for planet, p_house in self.planet_houses.items():
                if p_house == argala_house:
                    if planet in NATURAL_BENEFICS:
                        argala_count += 2
                    else:
                        argala_count += 1

        for offset in virodha_offsets:
            virodha_house = ((house + offset - 1) % 12) + 1
            for planet, p_house in self.planet_houses.items():
                if p_house == virodha_house:
                    if planet in NATURAL_BENEFICS:
                        virodha_count += 1
                    else:
                        virodha_count += 2

        # Net argala effect
        net = argala_count - virodha_count
        score += net * 8  # Each net argala point adds/subtracts 8

        return max(0, min(100, score))

    def _calc_bhava_ashtakavarga(self, house: int) -> float:
        """
        Calculate Bhava Ashtakavarga - house bindu count.

        Higher bindu count in SAV (Sarvashtakavarga) = stronger house.
        Average SAV is ~25-30 bindus per house.

        Returns:
            Score 0-100
        """
        score = 50.0  # Base

        sav = self.ashtakavarga.get("sarvashtakavarga", {})
        if not sav:
            return score

        # Get house bindu count
        # SAV data might be indexed by sign or house
        house_bindus = sav.get(house, sav.get(str(house), 0))

        # Average is ~28, range typically 18-38
        # Map to score: 18->30, 28->50, 38->70
        if house_bindus > 0:
            score = 30 + (house_bindus - 18) * 2

        return max(0, min(100, score))

    def _calc_bhava_yoga_bala(self, house: int) -> float:
        """
        Calculate Bhava Yoga Bala - yoga influence on house.

        If yogas involve this house or its lord, score increases.

        Returns:
            Score 0-100
        """
        score = 50.0  # Base

        lords = HOUSE_LORDS.get(self.asc_sign, HOUSE_LORDS["Aries"])
        lord = lords[house - 1]

        for yoga in self.yogas:
            if not yoga.get("is_formed", False) and not yoga.get("formed", False):
                continue

            # Check if yoga involves this house
            description = str(yoga.get("description", "")).lower()
            planets_involved = yoga.get("planets", [])

            # Check for house mention in description
            if f"{house}th house" in description or f"house {house}" in description:
                score += 15

            # Check if house lord is involved
            if lord in planets_involved or lord.lower() in description:
                score += 10

            # Check yoga name for house relevance
            yoga_name = yoga.get("name", "").lower()
            if house == 1 and any(x in yoga_name for x in ["raja", "mahapurusha"]):
                score += 10
            elif house == 10 and any(x in yoga_name for x in ["raja", "career", "karma"]):
                score += 10
            elif house == 2 and "dhana" in yoga_name:
                score += 10

        return max(0, min(100, score))

    def calculate_for_houses(self) -> Dict[int, float]:
        """
        Return simplified scores for integration.

        Returns:
            Dict mapping house number to score (±15 range)
        """
        results = self.calculate()
        return {h: r.total_score for h, r in results.items()}
