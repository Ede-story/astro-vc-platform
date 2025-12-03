"""
Varga Layer - Planet Scoring Phase 9

Evaluates planetary strength across multiple divisional charts:
- D2 (Hora): Wealth
- D3 (Drekkana): Siblings, courage
- D7 (Saptamsha): Children
- D10 (Dasamsha): Career
- D12 (Dwadashamsha): Parents
- D30 (Trimsamsha): Misfortunes

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


# Key vargas and their significance
VARGA_WEIGHTS = {
    "D2": 0.1,    # Hora - wealth
    "D3": 0.1,    # Drekkana - siblings
    "D7": 0.15,   # Saptamsha - children
    "D9": 0.25,   # Navamsha - spouse, dharma (handled by NavamshaLayer)
    "D10": 0.25,  # Dasamsha - career (most important for planets)
    "D12": 0.1,   # Dwadashamsha - parents
    "D30": 0.05,  # Trimsamsha - misfortune
}


@dataclass
class VargaResult:
    """Result of Varga analysis for a planet"""
    planet: str
    varga_positions: Dict[str, str]  # varga -> sign
    varga_dignities: Dict[str, str]  # varga -> dignity
    good_placements: int
    bad_placements: int
    score: float
    details: List[str]


class VargaLayer:
    """
    Calculates Varga-based scores for each planet

    Analyzes planet's dignity across multiple divisional charts.

    Scoring per varga:
    - Exalted: +2 * weight
    - Own sign: +1.5 * weight
    - Debilitated: -2 * weight
    """

    WEIGHT = 0.10  # 10% of total planet score

    def __init__(self, vargas: Dict[str, Dict[str, Any]]):
        """
        Initialize Varga layer

        Args:
            vargas: Dict of varga charts {D1: {...}, D9: {...}, D10: {...}, etc.}
        """
        self.vargas = vargas

        # Build planet positions for each varga
        self.planet_vargas = {}  # planet -> {varga: sign}
        for varga_name, varga_data in vargas.items():
            if varga_name in ["D2", "D3", "D7", "D10", "D12", "D30"]:
                planets = varga_data.get("planets", [])
                for p in planets:
                    name = p.get("name", "")
                    sign = p.get("sign_name") or p.get("sign", "")
                    if name not in self.planet_vargas:
                        self.planet_vargas[name] = {}
                    self.planet_vargas[name][varga_name] = sign

    def calculate(self) -> Dict[str, VargaResult]:
        """
        Calculate Varga-based scores for all planets

        Returns:
            Dict mapping planet name to VargaResult
        """
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if planet in self.planet_vargas:
                results[planet] = self._analyze_planet(planet)
        return results

    def _analyze_planet(self, planet: str) -> VargaResult:
        """Analyze varga positions for a single planet"""
        varga_positions = self.planet_vargas.get(planet, {})

        details = []
        score = 0.0
        varga_dignities = {}
        good_placements = 0
        bad_placements = 0

        for varga_name, sign in varga_positions.items():
            weight = VARGA_WEIGHTS.get(varga_name, 0.1)
            dignity = self._get_dignity(planet, sign)
            varga_dignities[varga_name] = dignity

            if dignity == "exalted":
                contribution = 2.0 * weight * 10  # Scale to score range
                score += contribution
                good_placements += 1
                details.append(f"{varga_name}: Exalted in {sign} (+{contribution:.1f})")
            elif dignity == "own":
                contribution = 1.5 * weight * 10
                score += contribution
                good_placements += 1
                details.append(f"{varga_name}: Own sign {sign} (+{contribution:.1f})")
            elif dignity == "debilitated":
                contribution = -2.0 * weight * 10
                score += contribution
                bad_placements += 1
                details.append(f"{varga_name}: Debilitated in {sign} ({contribution:.1f})")

        if not details:
            details.append(f"{planet}: No significant varga placements")

        return VargaResult(
            planet=planet,
            varga_positions=varga_positions,
            varga_dignities=varga_dignities,
            good_placements=good_placements,
            bad_placements=bad_placements,
            score=round(score, 2),
            details=details
        )

    def _get_dignity(self, planet: str, sign: str) -> str:
        """Determine dignity of planet in a sign"""
        if sign == EXALTATION_SIGNS.get(planet):
            return "exalted"
        if sign == DEBILITATION_SIGNS.get(planet):
            return "debilitated"
        if sign in OWN_SIGNS.get(planet, []):
            return "own"
        return "neutral"

    def get_score(self, planet: str) -> float:
        """Get the Varga score for a specific planet"""
        results = self.calculate()
        if planet in results:
            return results[planet].score
        return 0.0

    def get_all_scores(self) -> Dict[str, float]:
        """Get Varga scores for all planets"""
        results = self.calculate()
        return {planet: result.score for planet, result in results.items()}
