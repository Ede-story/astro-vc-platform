"""
Ashtakavarga Layer - Point System for Planetary Strength (±12 points)

Ashtakavarga is an ancient Vedic astrology technique that assigns benefic points (bindus)
to each planet based on their position relative to other planets and the ascendant.

Components:
1. Bhinna Ashtakavarga (BAV): Individual planet's bindu count in sign (0-8)
   - Each planet gets contributions from 7 planets + Lagna
   - More bindus = stronger planet in that sign

2. Sarvashtakavarga (SAV): Total bindus in sign from all 7 planets (0-56)
   - High SAV (>30) = auspicious sign placement
   - Low SAV (<25) = challenging sign placement

3. Kakshya Analysis: Sub-portions of signs
   - Each sign is divided into 8 kakshyas (3°45' each)
   - Ruler of kakshya affects planet's results

Score Contribution: -12 to +12 points
- Exceptional BAV (7-8): +8 to +12
- Strong BAV (5-6): +3 to +6
- Average BAV (4): 0
- Weak BAV (2-3): -3 to -6
- Very Weak BAV (0-1): -8 to -12
- SAV modifiers: ±3 points
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AshtakavargaScore:
    """Result from Ashtakavarga analysis"""
    planet: str
    raw_score: float
    bav_score: float  # From Bhinna Ashtakavarga
    sav_modifier: float  # From Sarvashtakavarga
    kakshya_modifier: float  # From Kakshya analysis
    details: List[str] = field(default_factory=list)


class AshtakavargaLayer:
    """
    Calculates planet strength based on Ashtakavarga system

    Weight: 12% of total planet score
    Range: -12 to +12 points
    """

    WEIGHT = 0.12  # 12% of total score
    MAX_CONTRIBUTION = 12.0
    MIN_CONTRIBUTION = -12.0

    # Standard Ashtakavarga contribution points
    # Each planet gets bindus from these contributors in specific positions
    # Format: {contributor: [houses from contributor where planet gets bindu]}

    # Sun's Ashtakavarga (Surya-Ashtakavarga)
    SUN_CONTRIBUTIONS = {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Ascendant": [3, 4, 6, 10, 11, 12],
    }

    # Moon's Ashtakavarga (Chandra-Ashtakavarga)
    MOON_CONTRIBUTIONS = {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Ascendant": [3, 6, 10, 11],
    }

    # Mars's Ashtakavarga (Mangala-Ashtakavarga)
    MARS_CONTRIBUTIONS = {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Ascendant": [1, 3, 6, 10, 11],
    }

    # Mercury's Ashtakavarga (Budha-Ashtakavarga)
    MERCURY_CONTRIBUTIONS = {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Ascendant": [1, 2, 4, 6, 8, 10, 11],
    }

    # Jupiter's Ashtakavarga (Guru-Ashtakavarga)
    JUPITER_CONTRIBUTIONS = {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    }

    # Venus's Ashtakavarga (Shukra-Ashtakavarga)
    VENUS_CONTRIBUTIONS = {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11],
    }

    # Saturn's Ashtakavarga (Shani-Ashtakavarga)
    SATURN_CONTRIBUTIONS = {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Ascendant": [1, 3, 4, 6, 10, 11],
    }

    # Mapping planet to its contribution table
    PLANET_CONTRIBUTIONS = {
        "Sun": SUN_CONTRIBUTIONS,
        "Moon": MOON_CONTRIBUTIONS,
        "Mars": MARS_CONTRIBUTIONS,
        "Mercury": MERCURY_CONTRIBUTIONS,
        "Jupiter": JUPITER_CONTRIBUTIONS,
        "Venus": VENUS_CONTRIBUTIONS,
        "Saturn": SATURN_CONTRIBUTIONS,
    }

    # Zodiac signs
    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    # Sign lords for Kakshya analysis
    SIGN_LORDS = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
        "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
        "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
        "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
    }

    # Kakshya rulers (for each 3°45' portion of a sign)
    # Order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna
    KAKSHYA_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Ascendant"]

    def __init__(self, d1_chart: Dict[str, Any]):
        """
        Initialize with D1 chart data

        Args:
            d1_chart: D1 chart containing planets and ascendant
        """
        self.d1 = d1_chart
        self.planets = self._extract_planets()
        self.asc_sign = self._get_ascendant_sign()

    def _extract_planets(self) -> Dict[str, Dict[str, Any]]:
        """Extract planet positions from D1 chart"""
        planets = {}
        for planet_data in self.d1.get("planets", []):
            name = planet_data.get("name", "")
            # Normalize name
            if name in ["Rahu", "Ketu"]:
                continue  # Rahu/Ketu not used in traditional Ashtakavarga

            eng_name = self._to_english(name)
            if eng_name:
                planets[eng_name] = {
                    "sign": planet_data.get("sign", ""),
                    "degree": planet_data.get("longitude", 0) % 30,
                    "house": planet_data.get("house", 1),
                }
        return planets

    def _to_english(self, name: str) -> Optional[str]:
        """Convert planet name to English"""
        mapping = {
            "Солнце": "Sun", "Sun": "Sun",
            "Луна": "Moon", "Moon": "Moon",
            "Марс": "Mars", "Mars": "Mars",
            "Меркурий": "Mercury", "Mercury": "Mercury",
            "Юпитер": "Jupiter", "Jupiter": "Jupiter",
            "Венера": "Venus", "Venus": "Venus",
            "Сатурн": "Saturn", "Saturn": "Saturn",
        }
        return mapping.get(name)

    def _get_ascendant_sign(self) -> str:
        """Get ascendant sign"""
        asc_data = self.d1.get("ascendant", {})
        return asc_data.get("sign", "Aries")

    def _get_sign_index(self, sign: str) -> int:
        """Get 0-based index of sign"""
        try:
            return self.SIGNS.index(sign)
        except ValueError:
            return 0

    def _house_from_sign(self, from_sign: str, to_sign: str) -> int:
        """
        Calculate house number from one sign to another
        Returns 1-12 (1 = same sign)
        """
        from_idx = self._get_sign_index(from_sign)
        to_idx = self._get_sign_index(to_sign)
        return ((to_idx - from_idx) % 12) + 1

    def calculate_bav(self, planet: str) -> tuple:
        """
        Calculate Bhinna Ashtakavarga (individual bindu count) for a planet

        Returns:
            (bindu_count, contributors)
        """
        if planet not in self.planets:
            return 0, []

        planet_sign = self.planets[planet]["sign"]
        contributions = self.PLANET_CONTRIBUTIONS.get(planet, {})

        bindus = 0
        contributors = []

        for contributor, houses in contributions.items():
            if contributor == "Ascendant":
                # From ascendant
                contributor_sign = self.asc_sign
            elif contributor in self.planets:
                contributor_sign = self.planets[contributor]["sign"]
            else:
                continue

            # Calculate house from contributor to planet
            house = self._house_from_sign(contributor_sign, planet_sign)

            if house in houses:
                bindus += 1
                contributors.append(contributor)

        return bindus, contributors

    def calculate_sav(self, sign: str) -> int:
        """
        Calculate Sarvashtakavarga (total bindus) for a sign

        Returns total bindus from all 7 planets in that sign
        """
        total = 0

        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            # Count how many bindus this planet gives to this sign
            contributions = self.PLANET_CONTRIBUTIONS.get(planet, {})

            for contributor, houses in contributions.items():
                if contributor == "Ascendant":
                    contributor_sign = self.asc_sign
                elif contributor in self.planets:
                    contributor_sign = self.planets[contributor]["sign"]
                else:
                    continue

                house = self._house_from_sign(contributor_sign, sign)
                if house in houses:
                    total += 1

        return total

    def get_kakshya_lord(self, planet: str) -> Optional[str]:
        """
        Get the lord of the kakshya where planet is placed

        Each sign is divided into 8 kakshyas of 3°45' each
        """
        if planet not in self.planets:
            return None

        degree = self.planets[planet]["degree"]
        kakshya_num = int(degree / 3.75)  # 0-7

        if 0 <= kakshya_num <= 7:
            return self.KAKSHYA_ORDER[kakshya_num]
        return None

    def calculate(self, planet: str) -> AshtakavargaScore:
        """
        Calculate complete Ashtakavarga score for a planet

        Score breakdown:
        - BAV (0-8 bindus) -> -12 to +12 base
        - SAV modifier -> -3 to +3
        - Kakshya modifier -> -2 to +2
        """
        details = []

        if planet not in self.planets:
            return AshtakavargaScore(
                planet=planet,
                raw_score=0,
                bav_score=0,
                sav_modifier=0,
                kakshya_modifier=0,
                details=["Planet not found in chart"]
            )

        planet_sign = self.planets[planet]["sign"]

        # 1. Calculate BAV (main score)
        bindus, contributors = self.calculate_bav(planet)

        # BAV score mapping (0-8 bindus -> score)
        # 4 bindus = neutral (0 points)
        # Each bindu above/below 4 = ~2.5 points
        bav_score = (bindus - 4) * 2.5

        # Enhanced bonuses for extreme values
        if bindus >= 7:
            bav_score += 2  # Extra bonus for very high
            details.append(f"Exceptional BAV: {bindus}/8 bindus in {planet_sign}")
        elif bindus >= 5:
            details.append(f"Strong BAV: {bindus}/8 bindus in {planet_sign}")
        elif bindus == 4:
            details.append(f"Average BAV: {bindus}/8 bindus in {planet_sign}")
        elif bindus >= 2:
            details.append(f"Weak BAV: {bindus}/8 bindus in {planet_sign}")
        else:
            bav_score -= 2  # Extra penalty for very low
            details.append(f"Very weak BAV: {bindus}/8 bindus in {planet_sign}")

        if contributors:
            details.append(f"Bindu from: {', '.join(contributors)}")

        # 2. Calculate SAV modifier
        sav = self.calculate_sav(planet_sign)

        # SAV scoring: 28 is average
        if sav >= 35:
            sav_modifier = 3.0
            details.append(f"Very strong SAV: {sav}/56 in {planet_sign}")
        elif sav >= 30:
            sav_modifier = 1.5
            details.append(f"Strong SAV: {sav}/56 in {planet_sign}")
        elif sav >= 25:
            sav_modifier = 0.0
            details.append(f"Average SAV: {sav}/56 in {planet_sign}")
        elif sav >= 20:
            sav_modifier = -1.5
            details.append(f"Weak SAV: {sav}/56 in {planet_sign}")
        else:
            sav_modifier = -3.0
            details.append(f"Very weak SAV: {sav}/56 in {planet_sign}")

        # 3. Kakshya analysis
        kakshya_lord = self.get_kakshya_lord(planet)
        kakshya_modifier = 0.0

        if kakshya_lord:
            # Benefit if kakshya lord is natural friend or same planet
            natural_friends = self._get_natural_friends(planet)

            if kakshya_lord == planet:
                kakshya_modifier = 2.0
                details.append(f"Own kakshya: {planet} in own sub-portion")
            elif kakshya_lord in natural_friends:
                kakshya_modifier = 1.0
                details.append(f"Friendly kakshya: {kakshya_lord}'s portion")
            elif kakshya_lord in self._get_natural_enemies(planet):
                kakshya_modifier = -1.5
                details.append(f"Enemy kakshya: {kakshya_lord}'s portion")
            else:
                details.append(f"Neutral kakshya: {kakshya_lord}'s portion")

        # Total score
        raw_score = bav_score + sav_modifier + kakshya_modifier

        # Clamp to range
        raw_score = max(self.MIN_CONTRIBUTION, min(self.MAX_CONTRIBUTION, raw_score))

        return AshtakavargaScore(
            planet=planet,
            raw_score=raw_score,
            bav_score=bav_score,
            sav_modifier=sav_modifier,
            kakshya_modifier=kakshya_modifier,
            details=details
        )

    def _get_natural_friends(self, planet: str) -> List[str]:
        """Get natural friends of a planet"""
        friends = {
            "Sun": ["Moon", "Mars", "Jupiter"],
            "Moon": ["Sun", "Mercury"],
            "Mars": ["Sun", "Moon", "Jupiter"],
            "Mercury": ["Sun", "Venus"],
            "Jupiter": ["Sun", "Moon", "Mars"],
            "Venus": ["Mercury", "Saturn"],
            "Saturn": ["Mercury", "Venus"],
        }
        return friends.get(planet, [])

    def _get_natural_enemies(self, planet: str) -> List[str]:
        """Get natural enemies of a planet"""
        enemies = {
            "Sun": ["Saturn", "Venus"],
            "Moon": [],  # Moon has no enemies
            "Mars": ["Mercury"],
            "Mercury": ["Moon"],
            "Jupiter": ["Mercury", "Venus"],
            "Venus": ["Sun", "Moon"],
            "Saturn": ["Sun", "Moon", "Mars"],
        }
        return enemies.get(planet, [])

    def calculate_all(self) -> Dict[str, AshtakavargaScore]:
        """Calculate Ashtakavarga scores for all planets"""
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            results[planet] = self.calculate(planet)
        return results


def calculate_ashtakavarga_score(d1_chart: Dict[str, Any], planet: str) -> float:
    """
    Convenience function to calculate Ashtakavarga score for a planet

    Returns score in range -12 to +12
    """
    layer = AshtakavargaLayer(d1_chart)
    result = layer.calculate(planet)
    return result.raw_score


def get_ashtakavarga_details(d1_chart: Dict[str, Any], planet: str) -> Dict[str, Any]:
    """
    Get detailed Ashtakavarga analysis for a planet
    """
    layer = AshtakavargaLayer(d1_chart)
    result = layer.calculate(planet)

    return {
        "planet": result.planet,
        "score": result.raw_score,
        "bav_score": result.bav_score,
        "sav_modifier": result.sav_modifier,
        "kakshya_modifier": result.kakshya_modifier,
        "details": result.details,
    }
