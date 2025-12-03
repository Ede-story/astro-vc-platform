"""
Shadbala Layer - Planet Scoring Phase 9

Evaluates planetary strength based on the 6 components of Shadbala:
1. Sthana Bala (Positional Strength) - sign placement
2. Dig Bala (Directional Strength) - house position
3. Kala Bala (Temporal Strength) - day/night, hora, etc.
4. Chesta Bala (Motional Strength) - speed and retrograde
5. Naisargika Bala (Natural Strength) - inherent brightness
6. Drik Bala (Aspectual Strength) - aspects received

Simplified implementation focusing on key factors.
Score range: -15 to +15 points
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import math

from ..neecha_bhanga import (
    get_sign_number,
    EXALTATION_SIGNS,
    DEBILITATION_SIGNS,
    OWN_SIGNS,
)


# Natural strength order (Naisargika Bala)
# Sun is strongest, Saturn is weakest among the 7 planets
NATURAL_STRENGTH = {
    "Sun": 60,
    "Moon": 51.43,
    "Mars": 17.14,
    "Mercury": 25.71,
    "Jupiter": 34.29,
    "Venus": 42.86,
    "Saturn": 8.57,
    "Rahu": 20,    # Approximate
    "Ketu": 20,    # Approximate
}

# Day/night rulership for Kala Bala
# Sun, Jupiter, Saturn are strong during day
# Moon, Venus, Mars are strong during night
DAY_PLANETS = ["Sun", "Jupiter", "Saturn"]
NIGHT_PLANETS = ["Moon", "Venus", "Mars"]


@dataclass
class ShadbalaResult:
    """Result of Shadbala analysis for a planet"""
    planet: str
    components: Dict[str, float]  # Each component's contribution
    total_shadbala: float
    is_strong: bool  # Above required minimum
    score: float
    details: List[str]


class ShadbalaLayer:
    """
    Calculates Shadbala-based scores for each planet

    Simplified Shadbala calculation focusing on:
    - Natural strength ranking
    - Positional strength from dignity
    - Retrograde bonus (Chesta Bala)
    - Basic directional strength

    Full Shadbala requires precise birth time calculations
    which are beyond this simplified implementation.
    """

    WEIGHT = 0.15  # 15% of total planet score

    def __init__(self, d1_data: Dict[str, Any], is_day_birth: bool = True):
        """
        Initialize Shadbala layer

        Args:
            d1_data: D1 chart data with planets and ascendant
            is_day_birth: True if born during day (Sun above horizon)
        """
        self.d1 = d1_data
        self.planets = d1_data.get("planets", [])
        self.is_day_birth = is_day_birth
        self.ascendant = d1_data.get("ascendant", {})
        self.asc_sign = self.ascendant.get("sign_name") or self.ascendant.get("sign", "Aries")
        self.asc_num = get_sign_number(self.asc_sign)

        # Build planet lookup
        self.planet_data = {}
        for p in self.planets:
            name = p.get("name", "")
            sign = p.get("sign_name") or p.get("sign", "")
            house = p.get("house_occupied") or p.get("house")
            if not house and sign:
                sign_num = get_sign_number(sign)
                house = ((sign_num - self.asc_num) % 12) + 1

            self.planet_data[name] = {
                "sign": sign,
                "house": house or 1,
                "degree": p.get("degree_in_sign", 0) or p.get("longitude", 0) % 30,
                "is_retrograde": p.get("is_retrograde", False),
                "speed": p.get("speed", 1.0),
            }

    def calculate(self) -> Dict[str, ShadbalaResult]:
        """
        Calculate Shadbala-based scores for all planets

        Returns:
            Dict mapping planet name to ShadbalaResult
        """
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if planet in self.planet_data:
                results[planet] = self._analyze_planet(planet)
        return results

    def _analyze_planet(self, planet: str) -> ShadbalaResult:
        """Analyze Shadbala for a single planet"""
        data = self.planet_data.get(planet, {})
        sign = data.get("sign", "")
        house = data.get("house", 1)
        is_retrograde = data.get("is_retrograde", False)

        components = {}
        details = []
        total = 0.0

        # 1. Naisargika Bala (Natural Strength)
        natural = NATURAL_STRENGTH.get(planet, 30)
        # Normalize to -2 to +2 scale
        natural_score = (natural - 30) / 15
        components["naisargika"] = natural_score
        if abs(natural_score) > 0.5:
            details.append(f"Natural strength: {'+' if natural_score > 0 else ''}{natural_score:.1f}")
        total += natural_score

        # 2. Sthana Bala (Positional Strength) - simplified
        sthana = self._calculate_sthana_bala(planet, sign)
        components["sthana"] = sthana
        if abs(sthana) >= 1.0:
            details.append(f"Positional strength: {'+' if sthana > 0 else ''}{sthana:.1f}")
        total += sthana

        # 3. Kala Bala (Temporal Strength) - day/night only
        kala = self._calculate_kala_bala(planet)
        components["kala"] = kala
        if abs(kala) >= 0.5:
            details.append(f"Temporal strength: {'+' if kala > 0 else ''}{kala:.1f}")
        total += kala

        # 4. Chesta Bala (Motional Strength)
        chesta = self._calculate_chesta_bala(planet, is_retrograde)
        components["chesta"] = chesta
        if abs(chesta) >= 1.0:
            details.append(f"Motional strength: {'+' if chesta > 0 else ''}{chesta:.1f}")
        total += chesta

        # 5. Dig Bala (Directional Strength) - calculated in HouseLayer, skip here

        # Scale total to -15 to +15 range
        # Current range is approximately -6 to +6
        score = total * 2.5

        # Determine if planet is "strong" (positive score)
        is_strong = score > 0

        if not details:
            details.append(f"{planet} has average Shadbala")

        return ShadbalaResult(
            planet=planet,
            components=components,
            total_shadbala=total,
            is_strong=is_strong,
            score=round(score, 2),
            details=details
        )

    def _calculate_sthana_bala(self, planet: str, sign: str) -> float:
        """Calculate positional strength based on dignity"""
        # Exalted: +3, Own: +2, Debilitated: -3
        if sign == EXALTATION_SIGNS.get(planet):
            return 3.0
        if sign == DEBILITATION_SIGNS.get(planet):
            return -3.0
        if sign in OWN_SIGNS.get(planet, []):
            return 2.0
        return 0.0

    def _calculate_kala_bala(self, planet: str) -> float:
        """Calculate temporal strength based on day/night birth"""
        if planet in ["Rahu", "Ketu"]:
            return 0.0  # Nodes don't have day/night preference

        if self.is_day_birth:
            if planet in DAY_PLANETS:
                return 1.0
            elif planet in NIGHT_PLANETS:
                return -0.5
        else:
            if planet in NIGHT_PLANETS:
                return 1.0
            elif planet in DAY_PLANETS:
                return -0.5

        return 0.0

    def _calculate_chesta_bala(self, planet: str, is_retrograde: bool) -> float:
        """Calculate motional strength"""
        # Sun and Moon are never retrograde
        if planet in ["Sun", "Moon", "Rahu", "Ketu"]:
            return 0.0

        # Retrograde planets have increased Chesta Bala
        if is_retrograde:
            return 2.0

        return 0.0

    def get_score(self, planet: str) -> float:
        """Get the Shadbala score for a specific planet"""
        results = self.calculate()
        if planet in results:
            return results[planet].score
        return 0.0

    def get_all_scores(self) -> Dict[str, float]:
        """Get Shadbala scores for all planets"""
        results = self.calculate()
        return {planet: result.score for planet, result in results.items()}
