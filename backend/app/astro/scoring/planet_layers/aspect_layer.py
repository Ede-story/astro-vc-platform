"""
Aspect Layer - Planet Scoring Phase 9

Evaluates planetary strength based on aspects:
- Graha Drishti (planetary aspects) received
- Benefic vs malefic aspects
- Aspect strength (full vs partial)
- Hemming (Kartari Yoga) - planets on both sides

Score range: -10 to +10 points
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..neecha_bhanga import get_sign_number


# Natural benefics and malefics
NATURAL_BENEFICS = ["Jupiter", "Venus", "Mercury", "Moon"]
NATURAL_MALEFICS = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]

# Planetary aspect patterns (houses aspected from planet's position)
# All planets aspect 7th, special planets have additional aspects
ASPECT_PATTERNS = {
    "Sun": [7],
    "Moon": [7],
    "Mercury": [7],
    "Venus": [7],
    "Jupiter": [5, 7, 9],      # Special trine aspects
    "Saturn": [3, 7, 10],      # Special 3rd and 10th aspects
    "Mars": [4, 7, 8],         # Special 4th and 8th aspects
    "Rahu": [5, 7, 9],         # Like Jupiter
    "Ketu": [5, 7, 9],         # Like Jupiter
}


@dataclass
class AspectResult:
    """Result of aspect analysis for a planet"""
    planet: str
    house: int
    aspects_received: List[Dict[str, Any]]  # List of {planet, type, strength}
    benefic_count: int
    malefic_count: int
    is_hemmed: bool
    hemmed_type: str  # "benefic", "malefic", "mixed", "none"
    score: float
    details: List[str]


class AspectLayer:
    """
    Calculates aspect-based scores for each planet

    Scoring:
    - Each benefic aspect: +2
    - Each malefic aspect: -2
    - Jupiter aspect (special): +3
    - Saturn aspect (special): -2.5
    - Shubha Kartari (hemmed by benefics): +4
    - Papa Kartari (hemmed by malefics): -4
    """

    WEIGHT = 0.10  # 10% of total planet score

    def __init__(self, d1_data: Dict[str, Any]):
        """
        Initialize aspect layer

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

    def calculate(self) -> Dict[str, AspectResult]:
        """
        Calculate aspect-based scores for all planets

        Returns:
            Dict mapping planet name to AspectResult
        """
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if planet in self.planet_data:
                results[planet] = self._analyze_planet(planet)
        return results

    def _analyze_planet(self, planet: str) -> AspectResult:
        """Analyze aspects for a single planet"""
        data = self.planet_data.get(planet, {})
        house = data.get("house", 1)

        details = []
        score = 0.0
        aspects_received = []
        benefic_count = 0
        malefic_count = 0

        # Check which planets aspect this planet
        for other_planet, other_data in self.planet_data.items():
            if other_planet == planet:
                continue

            other_house = other_data.get("house", 1)
            aspect_houses = ASPECT_PATTERNS.get(other_planet, [7])

            # Calculate if other_planet aspects this planet's house
            for aspect_distance in aspect_houses:
                aspected_house = ((other_house + aspect_distance - 1) % 12) + 1
                if aspected_house == house:
                    # This planet is aspected by other_planet
                    is_benefic = other_planet in NATURAL_BENEFICS
                    is_special = aspect_distance != 7  # Special aspect

                    aspect_info = {
                        "planet": other_planet,
                        "type": "benefic" if is_benefic else "malefic",
                        "special": is_special,
                        "distance": aspect_distance
                    }
                    aspects_received.append(aspect_info)

                    # Calculate score contribution
                    if is_benefic:
                        benefic_count += 1
                        if other_planet == "Jupiter":
                            bonus = 3.0 if is_special else 2.5
                            score += bonus
                            details.append(f"Jupiter aspect ({aspect_distance}th): +{bonus}")
                        else:
                            score += 2.0
                            details.append(f"{other_planet} aspect (benefic): +2")
                    else:
                        malefic_count += 1
                        if other_planet == "Saturn":
                            penalty = -2.5 if is_special else -2.0
                            score += penalty
                            details.append(f"Saturn aspect ({aspect_distance}th): {penalty}")
                        elif other_planet in ["Rahu", "Ketu"]:
                            score -= 1.5
                            details.append(f"{other_planet} aspect: -1.5")
                        else:
                            score -= 2.0
                            details.append(f"{other_planet} aspect (malefic): -2")

        # Check for hemming (Kartari Yoga)
        is_hemmed, hemmed_type = self._check_hemming(house)
        if is_hemmed:
            if hemmed_type == "benefic":
                score += 4.0
                details.append("Shubha Kartari (hemmed by benefics): +4")
            elif hemmed_type == "malefic":
                score -= 4.0
                details.append("Papa Kartari (hemmed by malefics): -4")
            # Mixed hemming has no score impact

        if not aspects_received and not is_hemmed:
            details.append(f"{planet} receives no aspects")

        return AspectResult(
            planet=planet,
            house=house,
            aspects_received=aspects_received,
            benefic_count=benefic_count,
            malefic_count=malefic_count,
            is_hemmed=is_hemmed,
            hemmed_type=hemmed_type,
            score=score,
            details=details
        )

    def _check_hemming(self, house: int) -> tuple:
        """
        Check if a house is hemmed by planets (Kartari Yoga)

        Returns:
            (is_hemmed, hemmed_type) where hemmed_type is "benefic", "malefic", "mixed", or "none"
        """
        prev_house = ((house - 2) % 12) + 1  # House before
        next_house = (house % 12) + 1        # House after

        prev_planets = []
        next_planets = []

        for planet, data in self.planet_data.items():
            p_house = data.get("house", 0)
            if p_house == prev_house:
                prev_planets.append(planet)
            elif p_house == next_house:
                next_planets.append(planet)

        # Must have planets on both sides for hemming
        if not prev_planets or not next_planets:
            return False, "none"

        # Determine nature of hemming planets
        prev_benefic = any(p in NATURAL_BENEFICS for p in prev_planets)
        prev_malefic = any(p in NATURAL_MALEFICS for p in prev_planets)
        next_benefic = any(p in NATURAL_BENEFICS for p in next_planets)
        next_malefic = any(p in NATURAL_MALEFICS for p in next_planets)

        if prev_benefic and next_benefic and not prev_malefic and not next_malefic:
            return True, "benefic"
        elif prev_malefic and next_malefic and not prev_benefic and not next_benefic:
            return True, "malefic"
        else:
            return True, "mixed"

    def get_score(self, planet: str) -> float:
        """Get the aspect score for a specific planet"""
        results = self.calculate()
        if planet in results:
            return results[planet].score
        return 0.0

    def get_all_scores(self) -> Dict[str, float]:
        """Get aspect scores for all planets"""
        results = self.calculate()
        return {planet: result.score for planet, result in results.items()}
