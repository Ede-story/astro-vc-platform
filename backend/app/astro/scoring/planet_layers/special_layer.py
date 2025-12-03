"""
Special Layer - Planet Scoring Phase 9

Evaluates special planetary conditions:
- Nakshatra quality (friendly/unfriendly)
- Combustion (too close to Sun)
- Gandanta (junction points)
- Planetary War (Graha Yuddha)
- Avastha (planetary states)
- Pushkara Bhaga (auspicious degrees)

Score range: -10 to +10 points
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..neecha_bhanga import get_sign_number


# Combustion orbs (degrees from Sun where planet is combust)
COMBUSTION_ORBS = {
    "Moon": 12,
    "Mars": 17,
    "Mercury": 14,  # 12 if retrograde
    "Jupiter": 11,
    "Venus": 10,    # 8 if retrograde
    "Saturn": 15,
}

# Gandanta degrees (junction between water and fire signs)
# These are the last 3°20' of Cancer, Scorpio, Pisces
# and first 3°20' of Leo, Sagittarius, Aries
GANDANTA_SIGNS_END = ["Cancer", "Scorpio", "Pisces"]
GANDANTA_SIGNS_START = ["Leo", "Sagittarius", "Aries"]
GANDANTA_DEGREE_THRESHOLD = 3.333  # 3°20'

# Pushkara Bhagas (most auspicious degrees in each sign)
PUSHKARA_BHAGAS = {
    "Aries": [21],
    "Taurus": [14],
    "Gemini": [18],
    "Cancer": [8],
    "Leo": [19],
    "Virgo": [9],
    "Libra": [24],
    "Scorpio": [14],
    "Sagittarius": [13],
    "Capricorn": [9],
    "Aquarius": [14],
    "Pisces": [9],
}

# Nakshatra lords and their general favorability
NAKSHATRA_LORDS = {
    "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun",
    "Rohini": "Moon", "Mrigashira": "Mars", "Ardra": "Rahu",
    "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
    "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
    "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
    "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshtha": "Mercury",
    "Mula": "Ketu", "Purva Ashadha": "Venus", "Uttara Ashadha": "Sun",
    "Shravana": "Moon", "Dhanishtha": "Mars", "Shatabhisha": "Rahu",
    "Purva Bhadrapada": "Jupiter", "Uttara Bhadrapada": "Saturn", "Revati": "Mercury",
}


@dataclass
class SpecialResult:
    """Result of special conditions analysis for a planet"""
    planet: str
    is_combust: bool
    is_gandanta: bool
    is_pushkara_bhaga: bool
    in_planetary_war: bool
    special_conditions: List[str]
    score: float
    details: List[str]


class SpecialLayer:
    """
    Calculates special condition scores for each planet

    Scoring:
    - Combustion: -4 to -6
    - Gandanta: -4
    - Pushkara Bhaga: +4
    - Planetary War winner: +2
    - Planetary War loser: -3
    - Friendly nakshatra lord: +2
    """

    WEIGHT = 0.10  # 10% of total planet score

    def __init__(self, d1_data: Dict[str, Any]):
        """
        Initialize Special layer

        Args:
            d1_data: D1 chart data with planets
        """
        self.d1 = d1_data
        self.planets = d1_data.get("planets", [])

        # Build planet lookup with detailed data
        self.planet_data = {}
        for p in self.planets:
            name = p.get("name", "")
            sign = p.get("sign_name") or p.get("sign", "")
            degree = p.get("degree_in_sign", 0) or p.get("longitude", 0) % 30
            longitude = p.get("longitude", 0)
            nakshatra = p.get("nakshatra", "")

            self.planet_data[name] = {
                "sign": sign,
                "degree": degree,
                "longitude": longitude,
                "nakshatra": nakshatra,
            }

    def calculate(self) -> Dict[str, SpecialResult]:
        """
        Calculate special condition scores for all planets

        Returns:
            Dict mapping planet name to SpecialResult
        """
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if planet in self.planet_data:
                results[planet] = self._analyze_planet(planet)
        return results

    def _analyze_planet(self, planet: str) -> SpecialResult:
        """Analyze special conditions for a single planet"""
        data = self.planet_data.get(planet, {})
        sign = data.get("sign", "")
        degree = data.get("degree", 0)
        longitude = data.get("longitude", 0)
        nakshatra = data.get("nakshatra", "")

        details = []
        score = 0.0
        special_conditions = []

        # Check combustion (not applicable to Sun)
        is_combust = False
        if planet != "Sun":
            is_combust = self._check_combustion(planet)
            if is_combust:
                penalty = -5.0 if planet in ["Mercury", "Venus"] else -4.0
                score += penalty
                special_conditions.append("combust")
                details.append(f"COMBUST (too close to Sun): {penalty}")

        # Check Gandanta
        is_gandanta = self._check_gandanta(sign, degree)
        if is_gandanta:
            score -= 4.0
            special_conditions.append("gandanta")
            details.append(f"GANDANTA (junction point): -4")

        # Check Pushkara Bhaga
        is_pushkara = self._check_pushkara_bhaga(sign, degree)
        if is_pushkara:
            score += 4.0
            special_conditions.append("pushkara_bhaga")
            details.append(f"Pushkara Bhaga ({int(degree)}° of {sign}): +4")

        # Check planetary war (for real planets only, not nodes)
        in_war = False
        if planet not in ["Sun", "Moon", "Rahu", "Ketu"]:
            war_result = self._check_planetary_war(planet, longitude)
            if war_result:
                in_war = True
                if war_result == "winner":
                    score += 2.0
                    special_conditions.append("war_winner")
                    details.append("Wins planetary war: +2")
                else:
                    score -= 3.0
                    special_conditions.append("war_loser")
                    details.append("Loses planetary war: -3")

        # Check nakshatra lord relationship
        if nakshatra:
            nakshatra_lord = NAKSHATRA_LORDS.get(nakshatra)
            if nakshatra_lord:
                # If in own nakshatra lord's sign, bonus
                if nakshatra_lord == planet:
                    score += 2.0
                    details.append(f"In own nakshatra ({nakshatra}): +2")

        if not special_conditions and not details:
            details.append(f"{planet}: No special conditions")

        return SpecialResult(
            planet=planet,
            is_combust=is_combust,
            is_gandanta=is_gandanta,
            is_pushkara_bhaga=is_pushkara,
            in_planetary_war=in_war,
            special_conditions=special_conditions,
            score=score,
            details=details
        )

    def _check_combustion(self, planet: str) -> bool:
        """Check if planet is combust (too close to Sun)"""
        if planet not in COMBUSTION_ORBS:
            return False

        sun_data = self.planet_data.get("Sun", {})
        planet_data = self.planet_data.get(planet, {})

        sun_long = sun_data.get("longitude", 0)
        planet_long = planet_data.get("longitude", 0)

        # Calculate angular distance
        diff = abs(sun_long - planet_long)
        if diff > 180:
            diff = 360 - diff

        return diff < COMBUSTION_ORBS[planet]

    def _check_gandanta(self, sign: str, degree: float) -> bool:
        """Check if planet is in Gandanta (junction between water and fire)"""
        # End of water signs
        if sign in GANDANTA_SIGNS_END and degree > (30 - GANDANTA_DEGREE_THRESHOLD):
            return True
        # Beginning of fire signs
        if sign in GANDANTA_SIGNS_START and degree < GANDANTA_DEGREE_THRESHOLD:
            return True
        return False

    def _check_pushkara_bhaga(self, sign: str, degree: float) -> bool:
        """Check if planet is at Pushkara Bhaga degree"""
        pushkara_degrees = PUSHKARA_BHAGAS.get(sign, [])
        # Check within 1 degree of Pushkara Bhaga
        for pb_deg in pushkara_degrees:
            if abs(degree - pb_deg) < 1.0:
                return True
        return False

    def _check_planetary_war(self, planet: str, longitude: float) -> Optional[str]:
        """
        Check if planet is in planetary war (within 1 degree of another planet)

        Returns: "winner", "loser", or None
        """
        # Planetary war only between Mars, Mercury, Jupiter, Venus, Saturn
        war_planets = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        if planet not in war_planets:
            return None

        for other in war_planets:
            if other == planet:
                continue

            other_data = self.planet_data.get(other, {})
            other_long = other_data.get("longitude", 0)

            diff = abs(longitude - other_long)
            if diff > 180:
                diff = 360 - diff

            # Within 1 degree = war
            if diff < 1.0:
                # Brighter (lower longitude in battle) wins
                # Simplified: use natural brightness order
                brightness = {
                    "Venus": 1, "Jupiter": 2, "Mars": 3, "Mercury": 4, "Saturn": 5
                }
                if brightness.get(planet, 5) < brightness.get(other, 5):
                    return "winner"
                else:
                    return "loser"

        return None

    def get_score(self, planet: str) -> float:
        """Get the special conditions score for a specific planet"""
        results = self.calculate()
        if planet in results:
            return results[planet].score
        return 0.0

    def get_all_scores(self) -> Dict[str, float]:
        """Get special condition scores for all planets"""
        results = self.calculate()
        return {planet: result.score for planet, result in results.items()}
