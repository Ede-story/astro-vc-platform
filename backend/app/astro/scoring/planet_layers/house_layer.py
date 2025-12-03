"""
House Layer - Planet Scoring Phase 9

Evaluates planetary strength based on house placement:
- Dig Bala (directional strength)
- Functional benefic/malefic status based on ascendant
- Yogakaraka status
- Badhaka (obstructing) planet status
- House type (kendra, trikona, dusthana, upachaya)

Score range: -10 to +10 points
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..neecha_bhanga import get_sign_number, SIGN_LORDS


# Dig Bala - Directional Strength
# Planets gain strength in specific houses (quadrants)
DIG_BALA = {
    "Sun": 10,      # 10th house (Zenith)
    "Mars": 10,     # 10th house (Zenith)
    "Jupiter": 1,   # 1st house (East)
    "Mercury": 1,   # 1st house (East)
    "Moon": 4,      # 4th house (Nadir)
    "Venus": 4,     # 4th house (Nadir)
    "Saturn": 7,    # 7th house (West)
    "Rahu": 7,      # 7th house (West)
    "Ketu": 4,      # 4th house (Nadir) - some traditions say 1st
}

# Opposite houses where planets are weakest (low Dig Bala)
LOW_DIG_BALA = {
    "Sun": 4,       # 4th house
    "Mars": 4,      # 4th house
    "Jupiter": 7,   # 7th house
    "Mercury": 7,   # 7th house
    "Moon": 10,     # 10th house
    "Venus": 10,    # 10th house
    "Saturn": 1,    # 1st house
    "Rahu": 1,      # 1st house
    "Ketu": 10,     # 10th house
}

# Yogakaraka planets by ascendant (lords of both kendra AND trikona)
YOGAKARAKA = {
    "Aries": ["Saturn"],          # Lord of 10 and 11 (some dispute this)
    "Taurus": ["Saturn"],         # Lord of 9 and 10
    "Gemini": [],                 # No single yogakaraka
    "Cancer": ["Mars"],           # Lord of 5 and 10
    "Leo": ["Mars"],              # Lord of 4 and 9
    "Virgo": [],                  # No single yogakaraka
    "Libra": ["Saturn"],          # Lord of 4 and 5
    "Scorpio": [],                # Jupiter rules 2,5 / Moon rules 9
    "Sagittarius": [],            # No single yogakaraka
    "Capricorn": ["Venus"],       # Lord of 5 and 10
    "Aquarius": ["Venus"],        # Lord of 4 and 9
    "Pisces": [],                 # No single yogakaraka
}

# Functional benefics by ascendant (lords of trikonas 1,5,9 and kendras 1,4,7,10)
# Some planets are always functional benefics for certain ascendants
FUNCTIONAL_BENEFICS = {
    "Aries": ["Sun", "Moon", "Mars", "Jupiter"],
    "Taurus": ["Sun", "Mercury", "Saturn"],
    "Gemini": ["Venus", "Saturn"],
    "Cancer": ["Moon", "Mars", "Jupiter"],
    "Leo": ["Sun", "Mars", "Jupiter"],
    "Virgo": ["Mercury", "Venus"],
    "Libra": ["Mercury", "Venus", "Saturn"],
    "Scorpio": ["Moon", "Sun", "Jupiter"],
    "Sagittarius": ["Sun", "Mars", "Jupiter"],
    "Capricorn": ["Venus", "Mercury", "Saturn"],
    "Aquarius": ["Venus", "Saturn"],
    "Pisces": ["Moon", "Mars", "Jupiter"],
}

# Functional malefics by ascendant (lords of dusthanas 6,8,12)
FUNCTIONAL_MALEFICS = {
    "Aries": ["Mercury", "Saturn"],
    "Taurus": ["Mars", "Jupiter", "Venus"],
    "Gemini": ["Mars"],
    "Cancer": ["Saturn", "Venus"],
    "Leo": ["Moon", "Saturn"],
    "Virgo": ["Sun", "Mars"],
    "Libra": ["Sun", "Jupiter", "Mars"],
    "Scorpio": ["Mercury", "Venus"],
    "Sagittarius": ["Venus", "Saturn"],
    "Capricorn": ["Sun", "Moon"],
    "Aquarius": ["Moon", "Mars", "Jupiter"],
    "Pisces": ["Sun", "Saturn", "Venus", "Mercury"],
}

# Badhaka (obstructing) houses and their lords
# For movable (cardinal) signs: 11th house
# For fixed signs: 9th house
# For dual (mutable) signs: 7th house
BADHAKA_HOUSES = {
    "Aries": 11, "Cancer": 11, "Libra": 11, "Capricorn": 11,  # Movable
    "Taurus": 9, "Leo": 9, "Scorpio": 9, "Aquarius": 9,        # Fixed
    "Gemini": 7, "Virgo": 7, "Sagittarius": 7, "Pisces": 7,    # Dual
}

# House types
KENDRA_HOUSES = [1, 4, 7, 10]      # Angular houses (strongest)
TRIKONA_HOUSES = [1, 5, 9]         # Trinal houses (most auspicious)
UPACHAYA_HOUSES = [3, 6, 10, 11]   # Growth houses (improve with time)
DUSTHANA_HOUSES = [6, 8, 12]       # Difficult houses


@dataclass
class HouseResult:
    """Result of house-based analysis for a planet"""
    planet: str
    house: int
    house_type: str
    dig_bala: str  # strong, neutral, weak
    functional_status: str  # benefic, malefic, neutral, yogakaraka
    score: float
    details: List[str]


class HouseLayer:
    """
    Calculates house-based scores for each planet

    Scoring:
    - Dig Bala strong: +5
    - Dig Bala weak: -3
    - Kendra placement: +2
    - Trikona placement: +3
    - Dusthana placement: -3
    - Upachaya placement: +1
    - Yogakaraka: +5
    - Functional benefic: +2
    - Functional malefic: -2
    - Badhaka lord: -2
    """

    WEIGHT = 0.10  # 10% of total planet score

    def __init__(self, d1_data: Dict[str, Any]):
        """
        Initialize house layer

        Args:
            d1_data: D1 chart data with planets and ascendant
        """
        self.d1 = d1_data
        self.planets = d1_data.get("planets", [])
        self.ascendant = d1_data.get("ascendant", {})
        self.asc_sign = self.ascendant.get("sign_name") or self.ascendant.get("sign", "Aries")
        self.asc_num = get_sign_number(self.asc_sign)

        # Build planet lookup
        self.planet_data = {}
        for p in self.planets:
            name = p.get("name", "")
            sign = p.get("sign_name") or p.get("sign", "")

            # Calculate house
            house = p.get("house_occupied") or p.get("house")
            if not house and sign:
                sign_num = get_sign_number(sign)
                house = ((sign_num - self.asc_num) % 12) + 1

            self.planet_data[name] = {
                "sign": sign,
                "house": house or 1,
            }

        # Calculate badhaka lord
        badhaka_house = BADHAKA_HOUSES.get(self.asc_sign, 11)
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        badhaka_sign = signs[(self.asc_num + badhaka_house - 2) % 12]
        self.badhaka_lord = SIGN_LORDS.get(badhaka_sign)

    def calculate(self) -> Dict[str, HouseResult]:
        """
        Calculate house-based scores for all planets

        Returns:
            Dict mapping planet name to HouseResult
        """
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if planet in self.planet_data:
                results[planet] = self._analyze_planet(planet)
        return results

    def _analyze_planet(self, planet: str) -> HouseResult:
        """Analyze house placement for a single planet"""
        data = self.planet_data.get(planet, {})
        house = data.get("house", 1)

        details = []
        score = 0.0

        # Determine house type
        house_type = self._get_house_type(house)
        details.append(f"{planet} in house {house} ({house_type})")

        # House type scoring
        if house in KENDRA_HOUSES:
            score += 2.0
            if house != 1:  # Don't double count for trikona
                details.append(f"Kendra placement (house {house}): +2")
        if house in TRIKONA_HOUSES:
            score += 3.0
            details.append(f"Trikona placement (house {house}): +3")
        if house in DUSTHANA_HOUSES:
            score -= 3.0
            details.append(f"Dusthana placement (house {house}): -3")
        elif house in UPACHAYA_HOUSES and house not in KENDRA_HOUSES:
            score += 1.0
            details.append(f"Upachaya placement (house {house}): +1")

        # Dig Bala
        dig_bala_house = DIG_BALA.get(planet)
        low_dig_bala_house = LOW_DIG_BALA.get(planet)
        dig_bala_status = "neutral"

        if house == dig_bala_house:
            score += 5.0
            dig_bala_status = "strong"
            details.append(f"DIG BALA: {planet} gains directional strength in house {house}: +5")
        elif house == low_dig_bala_house:
            score -= 3.0
            dig_bala_status = "weak"
            details.append(f"Low Dig Bala: {planet} weak in house {house}: -3")

        # Functional status
        functional_status = self._get_functional_status(planet)

        if functional_status == "yogakaraka":
            score += 5.0
            details.append(f"YOGAKARAKA for {self.asc_sign} ascendant: +5")
        elif functional_status == "benefic":
            score += 2.0
            details.append(f"Functional benefic for {self.asc_sign}: +2")
        elif functional_status == "malefic":
            score -= 2.0
            details.append(f"Functional malefic for {self.asc_sign}: -2")

        # Badhaka lord penalty
        if planet == self.badhaka_lord:
            score -= 2.0
            details.append(f"Badhaka lord for {self.asc_sign}: -2")

        return HouseResult(
            planet=planet,
            house=house,
            house_type=house_type,
            dig_bala=dig_bala_status,
            functional_status=functional_status,
            score=score,
            details=details
        )

    def _get_house_type(self, house: int) -> str:
        """Determine the type of house"""
        types = []
        if house in KENDRA_HOUSES:
            types.append("kendra")
        if house in TRIKONA_HOUSES:
            types.append("trikona")
        if house in DUSTHANA_HOUSES:
            types.append("dusthana")
        if house in UPACHAYA_HOUSES:
            types.append("upachaya")

        if types:
            return "/".join(types)
        return "neutral"

    def _get_functional_status(self, planet: str) -> str:
        """Determine the functional status of a planet based on ascendant"""

        # Check Yogakaraka first (highest)
        yogakarakas = YOGAKARAKA.get(self.asc_sign, [])
        if planet in yogakarakas:
            return "yogakaraka"

        # Check functional benefic
        benefics = FUNCTIONAL_BENEFICS.get(self.asc_sign, [])
        if planet in benefics:
            return "benefic"

        # Check functional malefic
        malefics = FUNCTIONAL_MALEFICS.get(self.asc_sign, [])
        if planet in malefics:
            return "malefic"

        return "neutral"

    def get_score(self, planet: str) -> float:
        """Get the house score for a specific planet"""
        results = self.calculate()
        if planet in results:
            return results[planet].score
        return 0.0

    def get_all_scores(self) -> Dict[str, float]:
        """Get house scores for all planets"""
        results = self.calculate()
        return {planet: result.score for planet, result in results.items()}
