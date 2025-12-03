"""
Yoga Layer - Planet Scoring Phase 9

Evaluates planetary strength based on yoga participation:
- Raja Yogas (power/authority)
- Dhana Yogas (wealth)
- Parivartana Yogas (exchange)
- Neecha Bhanga (cancellation of debilitation)
- Other auspicious yogas

Score range: -15 to +15 points
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..neecha_bhanga import SIGN_LORDS, OWN_SIGNS, get_sign_number


# Yoga types and their point values
YOGA_POINTS = {
    # Major Raja Yogas
    "raja_yoga": 5.0,
    "maha_raja_yoga": 8.0,

    # Dhana Yogas
    "dhana_yoga": 4.0,
    "maha_dhana_yoga": 6.0,

    # Parivartana (exchange)
    "parivartana_yoga": 4.0,

    # Special combinations
    "hamsa_yoga": 6.0,      # Jupiter in kendra in own/exaltation
    "malavya_yoga": 6.0,    # Venus in kendra in own/exaltation
    "bhadra_yoga": 6.0,     # Mercury in kendra in own/exaltation
    "ruchaka_yoga": 6.0,    # Mars in kendra in own/exaltation
    "sasa_yoga": 6.0,       # Saturn in kendra in own/exaltation

    # Gajakesari (Jupiter-Moon)
    "gajakesari_yoga": 5.0,

    # Budhaditya (Sun-Mercury conjunction)
    "budhaditya_yoga": 3.0,

    # Neecha Bhanga
    "neecha_bhanga": 4.0,
    "neecha_bhanga_raja_yoga": 7.0,

    # Generic beneficial
    "auspicious_yoga": 2.0,
    "minor_yoga": 1.0,
}


@dataclass
class YogaLayerResult:
    """Result of yoga analysis for a planet"""
    planet: str
    yogas_participated: List[str]
    yoga_count: int
    total_yoga_points: float
    score: float
    details: List[str]


class YogaPlanetLayer:
    """
    Calculates yoga-based scores for each planet

    Analyzes which yogas each planet participates in
    and assigns points accordingly.
    """

    WEIGHT = 0.15  # 15% of total planet score

    def __init__(self, d1_data: Dict[str, Any], yogas: List[Dict[str, Any]] = None):
        """
        Initialize Yoga layer

        Args:
            d1_data: D1 chart data with planets
            yogas: List of found yogas (from yoga detection)
        """
        self.d1 = d1_data
        self.yogas = yogas or []
        self.planets = d1_data.get("planets", [])
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
            }

        # Pre-detect some key yogas
        self._detect_basic_yogas()

    def _detect_basic_yogas(self):
        """Detect basic yogas from chart data"""
        # This supplements any yogas passed in from external detection
        detected = []

        # Check for Pancha Mahapurusha Yogas
        for planet in ["Jupiter", "Venus", "Mercury", "Mars", "Saturn"]:
            data = self.planet_data.get(planet, {})
            house = data.get("house", 0)
            sign = data.get("sign", "")

            if house in [1, 4, 7, 10]:  # Kendra
                if sign in OWN_SIGNS.get(planet, []):
                    yoga_name = self._get_mahapurusha_name(planet)
                    if yoga_name:
                        detected.append({
                            "name": yoga_name,
                            "type": yoga_name.lower().replace(" ", "_"),
                            "planets": [planet],
                            "strength": "strong"
                        })

        # Check for Gajakesari (Jupiter-Moon in kendra from each other)
        jupiter_house = self.planet_data.get("Jupiter", {}).get("house", 0)
        moon_house = self.planet_data.get("Moon", {}).get("house", 0)
        if jupiter_house and moon_house:
            diff = abs(jupiter_house - moon_house)
            if diff in [0, 3, 6, 9] or (12 - diff) in [3, 6, 9]:
                detected.append({
                    "name": "Gajakesari Yoga",
                    "type": "gajakesari_yoga",
                    "planets": ["Jupiter", "Moon"],
                    "strength": "strong"
                })

        # Check for Budhaditya (Sun-Mercury conjunction)
        sun_house = self.planet_data.get("Sun", {}).get("house", 0)
        mercury_house = self.planet_data.get("Mercury", {}).get("house", 0)
        if sun_house == mercury_house and sun_house > 0:
            detected.append({
                "name": "Budhaditya Yoga",
                "type": "budhaditya_yoga",
                "planets": ["Sun", "Mercury"],
                "strength": "moderate"
            })

        # Add detected yogas to the list
        self.yogas.extend(detected)

    def _get_mahapurusha_name(self, planet: str) -> Optional[str]:
        """Get Pancha Mahapurusha yoga name for a planet"""
        names = {
            "Jupiter": "Hamsa Yoga",
            "Venus": "Malavya Yoga",
            "Mercury": "Bhadra Yoga",
            "Mars": "Ruchaka Yoga",
            "Saturn": "Sasa Yoga",
        }
        return names.get(planet)

    def calculate(self) -> Dict[str, YogaLayerResult]:
        """
        Calculate yoga-based scores for all planets

        Returns:
            Dict mapping planet name to YogaLayerResult
        """
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if planet in self.planet_data:
                results[planet] = self._analyze_planet(planet)
        return results

    def _analyze_planet(self, planet: str) -> YogaLayerResult:
        """Analyze yoga participation for a single planet"""
        details = []
        yogas_participated = []
        total_points = 0.0

        # Find all yogas this planet participates in
        for yoga in self.yogas:
            yoga_planets = yoga.get("planets", [])
            if planet in yoga_planets:
                yoga_name = yoga.get("name", "Unknown Yoga")
                yoga_type = yoga.get("type", "minor_yoga")
                strength = yoga.get("strength", "moderate")

                yogas_participated.append(yoga_name)

                # Get base points for this yoga type
                base_points = YOGA_POINTS.get(yoga_type, 1.0)

                # Apply strength modifier
                if strength == "strong":
                    modifier = 1.2
                elif strength == "weak":
                    modifier = 0.7
                else:
                    modifier = 1.0

                points = base_points * modifier
                total_points += points

                details.append(f"{yoga_name}: +{points:.1f}")

        # Cap total points at reasonable range
        score = min(15.0, max(-15.0, total_points))

        if not yogas_participated:
            details.append(f"{planet} does not participate in any detected yogas")

        return YogaLayerResult(
            planet=planet,
            yogas_participated=yogas_participated,
            yoga_count=len(yogas_participated),
            total_yoga_points=total_points,
            score=score,
            details=details
        )

    def get_score(self, planet: str) -> float:
        """Get the yoga score for a specific planet"""
        results = self.calculate()
        if planet in results:
            return results[planet].score
        return 0.0

    def get_all_scores(self) -> Dict[str, float]:
        """Get yoga scores for all planets"""
        results = self.calculate()
        return {planet: result.score for planet, result in results.items()}
