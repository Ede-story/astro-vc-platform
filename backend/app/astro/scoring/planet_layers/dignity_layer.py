"""
Dignity Layer - Planet Scoring Phase 9

Evaluates planetary dignity including:
- Sign placement (exalted, own, friend, neutral, enemy, debilitated)
- Neecha Bhanga Raja Yoga (cancellation of debilitation)
- Moolatrikona positions
- Deep exaltation/debilitation degrees

Score range: -20 to +20 points
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..neecha_bhanga import (
    NeechaBhangaAnalyzer,
    DEBILITATION_SIGNS,
    EXALTATION_SIGNS,
    SIGN_LORDS,
    OWN_SIGNS,
    get_sign_number,
)


# Moolatrikona data - degrees where planet has special strength
MOOLATRIKONA = {
    "Sun": {"sign": "Leo", "start": 0, "end": 20},
    "Moon": {"sign": "Taurus", "start": 3, "end": 30},
    "Mars": {"sign": "Aries", "start": 0, "end": 12},
    "Mercury": {"sign": "Virgo", "start": 15, "end": 20},
    "Jupiter": {"sign": "Sagittarius", "start": 0, "end": 10},
    "Venus": {"sign": "Libra", "start": 0, "end": 15},
    "Saturn": {"sign": "Aquarius", "start": 0, "end": 20},
}

# Deep exaltation degrees (maximum strength in exaltation sign)
DEEP_EXALTATION_DEGREES = {
    "Sun": 10,      # Aries 10
    "Moon": 3,      # Taurus 3
    "Mars": 28,     # Capricorn 28
    "Mercury": 15,  # Virgo 15
    "Jupiter": 5,   # Cancer 5
    "Venus": 27,    # Pisces 27
    "Saturn": 20,   # Libra 20
    "Rahu": 20,     # Taurus 20 (Gemini in some traditions)
    "Ketu": 20,     # Scorpio 20 (Sagittarius in some traditions)
}

# Deep debilitation degrees (maximum weakness in debilitation sign)
DEEP_DEBILITATION_DEGREES = {
    "Sun": 10,      # Libra 10
    "Moon": 3,      # Scorpio 3
    "Mars": 28,     # Cancer 28
    "Mercury": 15,  # Pisces 15
    "Jupiter": 5,   # Capricorn 5
    "Venus": 27,    # Virgo 27
    "Saturn": 20,   # Aries 20
    "Rahu": 20,     # Scorpio 20
    "Ketu": 20,     # Taurus 20
}

# Planetary friendships for calculating friend/enemy signs
NATURAL_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"],
    "Rahu": ["Mercury", "Venus", "Saturn"],
    "Ketu": ["Mars", "Venus", "Saturn"],
}

NATURAL_ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],  # Moon has no enemies
    "Mars": ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon", "Mars"],
    "Rahu": ["Sun", "Moon", "Mars"],
    "Ketu": ["Sun", "Moon"],
}

# All remaining relationships are neutral


@dataclass
class DignityResult:
    """Result of dignity analysis for a planet"""
    planet: str
    sign: str
    dignity_type: str  # exalted, moolatrikona, own, friend, neutral, enemy, debilitated
    base_score: float
    modifiers: Dict[str, float]
    total_score: float
    details: List[str]


class DignityLayer:
    """
    Calculates dignity-based scores for each planet

    Scoring:
    - Exalted: +15 to +20 (deep exaltation = +20)
    - Moolatrikona: +12
    - Own sign: +10
    - Friend sign: +5
    - Neutral sign: 0
    - Enemy sign: -5
    - Debilitated: -15 to -20 (deep debilitation = -20)

    Neecha Bhanga modifiers:
    - 1 rule: cancels debilitation penalty (-15 -> 0)
    - 2 rules: mild boost (-15 -> +5)
    - 3+ rules: Raja Yoga! (-15 -> +15)
    """

    WEIGHT = 0.20  # 20% of total planet score

    # Base scores for dignity types
    DIGNITY_SCORES = {
        "exalted": 15.0,
        "moolatrikona": 12.0,
        "own": 10.0,
        "friend": 5.0,
        "neutral": 0.0,
        "enemy": -5.0,
        "debilitated": -15.0,
    }

    def __init__(self, d1_data: Dict[str, Any], d9_data: Optional[Dict[str, Any]] = None):
        """
        Initialize dignity layer

        Args:
            d1_data: D1 chart data with planets and ascendant
            d9_data: Optional D9 data for Neecha Bhanga rule 8
        """
        self.d1 = d1_data
        self.d9 = d9_data
        self.planets = d1_data.get("planets", [])

        # Build planet lookup
        self.planet_data = {}
        for p in self.planets:
            name = p.get("name", "")
            self.planet_data[name] = {
                "sign": p.get("sign_name") or p.get("sign", ""),
                "degree": p.get("degree_in_sign", 0) or p.get("longitude", 0) % 30,
                "is_retrograde": p.get("is_retrograde", False),
            }

        # Initialize Neecha Bhanga analyzer
        self.neecha_bhanga = NeechaBhangaAnalyzer(d1_data, d9_data)
        self.neecha_bhanga_results = {
            r.planet: r for r in self.neecha_bhanga.analyze_all()
        }

    def calculate(self) -> Dict[str, DignityResult]:
        """
        Calculate dignity scores for all planets

        Returns:
            Dict mapping planet name to DignityResult
        """
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if planet in self.planet_data:
                results[planet] = self._analyze_planet(planet)
        return results

    def _analyze_planet(self, planet: str) -> DignityResult:
        """Analyze dignity for a single planet"""
        data = self.planet_data.get(planet, {})
        sign = data.get("sign", "")
        degree = data.get("degree", 0)

        details = []
        modifiers = {}

        # Determine base dignity type
        dignity_type = self._get_dignity_type(planet, sign)
        base_score = self.DIGNITY_SCORES.get(dignity_type, 0)
        details.append(f"{planet} in {sign}: {dignity_type} ({base_score:+.1f})")

        # Check for deep exaltation/debilitation
        if dignity_type == "exalted":
            deep_deg = DEEP_EXALTATION_DEGREES.get(planet, 15)
            distance = abs(degree - deep_deg)
            if distance <= 3:
                modifiers["deep_exaltation"] = 5.0
                details.append(f"Near deep exaltation degree ({deep_deg}): +5")
            elif distance <= 10:
                bonus = 2.0 * (1 - distance / 10)
                modifiers["near_exaltation"] = round(bonus, 1)
                details.append(f"Near exaltation peak: +{bonus:.1f}")

        elif dignity_type == "debilitated":
            deep_deg = DEEP_DEBILITATION_DEGREES.get(planet, 15)
            distance = abs(degree - deep_deg)
            if distance <= 3:
                modifiers["deep_debilitation"] = -5.0
                details.append(f"Near deep debilitation degree ({deep_deg}): -5")
            elif distance <= 10:
                penalty = -2.0 * (1 - distance / 10)
                modifiers["near_debilitation"] = round(penalty, 1)
                details.append(f"Near debilitation nadir: {penalty:.1f}")

            # Check for Neecha Bhanga
            nb_result = self.neecha_bhanga_results.get(planet)
            if nb_result:
                if nb_result.count >= 3:
                    # Raja Yoga! Convert penalty to major bonus
                    modifiers["neecha_bhanga_raja_yoga"] = 30.0  # -15 base + 30 = +15
                    details.append(f"NEECHA BHANGA RAJA YOGA ({nb_result.count} rules): +30")
                    for rule in nb_result.rules_satisfied[:3]:
                        details.append(f"  - {rule}")
                elif nb_result.count == 2:
                    # Good cancellation with mild boost
                    modifiers["neecha_bhanga"] = 20.0  # -15 base + 20 = +5
                    details.append(f"Neecha Bhanga (2 rules): +20")
                    for rule in nb_result.rules_satisfied:
                        details.append(f"  - {rule}")
                elif nb_result.count == 1:
                    # Simple cancellation
                    modifiers["neecha_bhanga"] = 15.0  # -15 base + 15 = 0
                    details.append(f"Neecha Bhanga (1 rule): +15 (cancels debilitation)")
                    details.append(f"  - {nb_result.rules_satisfied[0]}")

        # Check for Moolatrikona (special own sign position)
        mt_data = MOOLATRIKONA.get(planet)
        if mt_data and sign == mt_data["sign"]:
            if mt_data["start"] <= degree <= mt_data["end"]:
                if dignity_type != "moolatrikona":
                    # Upgrade to moolatrikona
                    bonus = self.DIGNITY_SCORES["moolatrikona"] - base_score
                    modifiers["moolatrikona_upgrade"] = bonus
                    details.append(f"In Moolatrikona degrees ({mt_data['start']}-{mt_data['end']}): +{bonus:.1f}")

        # Check for retrograde bonus (stronger in some contexts)
        if data.get("is_retrograde") and dignity_type not in ["exalted", "own", "moolatrikona"]:
            modifiers["retrograde_strength"] = 2.0
            details.append("Retrograde (increased strength): +2")

        # Calculate total score
        total_score = base_score + sum(modifiers.values())

        return DignityResult(
            planet=planet,
            sign=sign,
            dignity_type=dignity_type,
            base_score=base_score,
            modifiers=modifiers,
            total_score=total_score,
            details=details
        )

    def _get_dignity_type(self, planet: str, sign: str) -> str:
        """Determine the dignity type for a planet in a sign"""

        # Check exaltation
        if EXALTATION_SIGNS.get(planet) == sign:
            return "exalted"

        # Check debilitation
        if DEBILITATION_SIGNS.get(planet) == sign:
            return "debilitated"

        # Check own sign
        if sign in OWN_SIGNS.get(planet, []):
            # Check if in Moolatrikona portion
            mt = MOOLATRIKONA.get(planet)
            degree = self.planet_data.get(planet, {}).get("degree", 15)
            if mt and sign == mt["sign"] and mt["start"] <= degree <= mt["end"]:
                return "moolatrikona"
            return "own"

        # Check friendship with sign lord
        sign_lord = SIGN_LORDS.get(sign)
        if not sign_lord:
            return "neutral"

        if sign_lord in NATURAL_FRIENDS.get(planet, []):
            return "friend"

        if sign_lord in NATURAL_ENEMIES.get(planet, []):
            return "enemy"

        return "neutral"

    def get_score(self, planet: str) -> float:
        """Get the dignity score for a specific planet"""
        results = self.calculate()
        if planet in results:
            return results[planet].total_score
        return 0.0

    def get_all_scores(self) -> Dict[str, float]:
        """Get dignity scores for all planets"""
        results = self.calculate()
        return {planet: result.total_score for planet, result in results.items()}
