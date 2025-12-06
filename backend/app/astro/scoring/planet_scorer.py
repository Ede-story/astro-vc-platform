"""
Planet Scorer - Phase 9 & Phase 9.5: Deep Planet Scoring System

Phase 9 Original (8 layers):
1. Dignity (20%) - Sign placement, Neecha Bhanga
2. House (10%) - Dig Bala, functional status
3. Aspect (10%) - Graha Drishti, Kartari
4. Shadbala (15%) - Six-fold strength
5. Navamsha (10%) - D9 dignity, Vargottama
6. Varga (10%) - Multi-divisional charts
7. Yoga (15%) - Yoga participation
8. Special (10%) - Combustion, Gandanta, etc.

Phase 9.5 Enhanced (10 layers):
- Shadbala: Enhanced with full 6-component calculation (±25)
- Ashtakavarga: NEW - Bindu point system (±12)
- Jaimini: NEW - Chara Karaka based strength (±10)
- Yoga: Enhanced to 50+ yogas (±18)

New weights (Phase 9.5):
- Dignity: 0.18
- House: 0.08
- Aspect: 0.08
- Shadbala: 0.14 (enhanced)
- Navamsha: 0.08
- Varga: 0.08
- Yoga: 0.14 (enhanced)
- Special: 0.08
- Ashtakavarga: 0.08 (NEW)
- Jaimini: 0.06 (NEW)

Target calibration:
- Trump's Sun: 85-90
- Vadim's Mars (with Neecha Bhanga): 75-80
- Average planet: 45-55
- Weak planet: 20-35
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .planet_layers import (
    DignityLayer,
    HouseLayer,
    AspectLayer,
    ShadbalaLayer,
    NavamshaLayer,
    VargaLayer,
    YogaPlanetLayer,
    SpecialLayer,
    # Phase 9.5 new layers
    AshtakavargaLayer,
    JaiminiPlanetLayer,
)


@dataclass
class LayerScore:
    """Score from a single layer"""
    layer_name: str
    raw_score: float
    weight: float
    weighted_score: float
    details: List[str] = field(default_factory=list)


@dataclass
class PlanetScoreResult:
    """Comprehensive planet score result"""
    planet: str
    total_score: float  # 0-100 normalized score
    raw_total: float  # Sum of weighted layer scores before normalization
    grade: str  # S, A, B, C, D, F
    layer_scores: Dict[str, LayerScore]
    strengths: List[str]  # Key positive factors
    weaknesses: List[str]  # Key negative factors
    summary: str  # One-line summary


class PlanetScorer:
    """
    Master class for calculating comprehensive planet scores.

    Architecture:
    - Each layer calculates raw scores in its own range
    - Raw scores are normalized and weighted
    - Final score is normalized to 0-100

    Layer weights (total = 1.0):
    - Dignity: 0.20 (most fundamental)
    - House: 0.10
    - Aspect: 0.10
    - Shadbala: 0.15
    - Navamsha: 0.10
    - Varga: 0.10
    - Yoga: 0.15
    - Special: 0.10
    """

    # Layer weights (must sum to 1.0)
    # Phase 9.5: Redistributed weights to accommodate new layers
    LAYER_WEIGHTS = {
        # Original Phase 9 layers (adjusted)
        "dignity": 0.18,      # Reduced from 0.20
        "house": 0.08,        # Reduced from 0.10
        "aspect": 0.08,       # Reduced from 0.10
        "shadbala": 0.14,     # Reduced from 0.15 (but enhanced calculation)
        "navamsha": 0.08,     # Reduced from 0.10
        "varga": 0.08,        # Reduced from 0.10
        "yoga": 0.14,         # Reduced from 0.15 (but enhanced to 50+ yogas)
        "special": 0.08,      # Reduced from 0.10
        # Phase 9.5 new layers
        "ashtakavarga": 0.08, # NEW - Bindu point system
        "jaimini": 0.06,      # NEW - Chara Karaka based strength
    }

    # Raw score ranges for each layer (min, max) for normalization
    # These define the expected range of raw scores from each layer
    RAW_SCORE_RANGES = {
        # Phase 9 original layers
        "dignity": (-20, 20),    # Debilitated deep to Exalted deep + NBRY
        "house": (-10, 15),      # Dusthana to Kendra + Dig Bala + Yogakaraka
        "aspect": (-10, 10),     # Papa Kartari to Shubha Kartari + benefic aspects
        "shadbala": (-25, 25),   # Phase 9.5: Enhanced range for 6-component calculation
        "navamsha": (-4, 14),    # Debilitated D9 to Vargottama + Pushkara + Exalted
        "varga": (-10, 10),      # Multiple debilitations to multiple exaltations
        "yoga": (-5, 18),        # Phase 9.5: Enhanced range for 50+ yogas
        "special": (-10, 10),    # Combust + Gandanta to Pushkara Bhaga + friendly nakshatra
        # Phase 9.5 new layers
        "ashtakavarga": (-12, 12),  # NEW - BAV/SAV/Kakshya analysis
        "jaimini": (-10, 10),       # NEW - Chara Karaka + Argala
    }

    # Calibration parameters
    # Based on observed data:
    # - Trump's Sun raw_total: 33.6 (should score 85-90)
    # - Average planets: 25-40 (should score 45-55)
    # - Weak planets: 15-25 (should score 20-35)
    # Using linear mapping from raw_total (0-100 scale) to final score
    RAW_WEAK = 15.0      # Raw total for very weak planets
    RAW_AVERAGE = 35.0   # Raw total for average planets
    RAW_STRONG = 55.0    # Raw total for strong planets
    SCORE_WEAK = 25.0    # Output score for weak
    SCORE_AVERAGE = 50.0 # Output score for average
    SCORE_STRONG = 90.0  # Output score for strong

    def __init__(
        self,
        d1_data: Dict[str, Any],
        d9_data: Optional[Dict[str, Any]] = None,
        vargas: Optional[Dict[str, Dict[str, Any]]] = None,
        yogas: Optional[List[Dict[str, Any]]] = None,
        birth_time_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Planet Scorer with chart data.

        Args:
            d1_data: D1 (Rashi) chart data with planets, houses, ascendant
            d9_data: D9 (Navamsha) chart data (optional, calculated if not provided)
            vargas: Dict of all varga charts {D2: {...}, D3: {...}, etc.}
            yogas: List of detected yogas from yoga detection module
            birth_time_data: Birth time info for Shadbala (sunrise/sunset, day/night)
        """
        self.d1 = d1_data
        self.d9 = d9_data
        self.vargas = vargas or {}
        self.yogas = yogas or []
        self.birth_time_data = birth_time_data or {}

        # Initialize all layers
        self._init_layers()

    def _init_layers(self):
        """Initialize all scoring layers"""
        # Phase 9 Original Layers
        # Dignity Layer (with Neecha Bhanga)
        self.dignity_layer = DignityLayer(self.d1, self.d9)

        # House Layer (Dig Bala, functional status)
        self.house_layer = HouseLayer(self.d1)

        # Aspect Layer (Graha Drishti, Kartari)
        self.aspect_layer = AspectLayer(self.d1)

        # Shadbala Layer (Phase 9.5: enhanced 6-component calculation)
        self.shadbala_layer = ShadbalaLayer(self.d1, self.birth_time_data)

        # Navamsha Layer (D9 analysis)
        self.navamsha_layer = NavamshaLayer(self.d1, self.d9)

        # Varga Layer (multi-divisional)
        self.varga_layer = VargaLayer(self.vargas)

        # Yoga Layer (Phase 9.5: enhanced to 50+ yogas)
        self.yoga_layer = YogaPlanetLayer(self.d1, self.yogas)

        # Special Layer (combustion, gandanta, etc.)
        self.special_layer = SpecialLayer(self.d1)

        # Phase 9.5 New Layers
        # Ashtakavarga Layer (Bindu point system)
        self.ashtakavarga_layer = AshtakavargaLayer(self.d1)

        # Jaimini Layer (Chara Karaka based strength)
        self.jaimini_layer = JaiminiPlanetLayer(self.d1, self.d9)

    def calculate_all(self) -> Dict[str, PlanetScoreResult]:
        """
        Calculate scores for all planets.

        Returns:
            Dict mapping planet name to PlanetScoreResult
        """
        results = {}
        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

        # Get all layer results once (efficiency)
        # Phase 9 Original Layers
        dignity_results = self.dignity_layer.calculate()
        house_results = self.house_layer.calculate()
        aspect_results = self.aspect_layer.calculate()
        shadbala_results = self.shadbala_layer.calculate()
        navamsha_results = self.navamsha_layer.calculate()
        varga_results = self.varga_layer.calculate()
        yoga_results = self.yoga_layer.calculate()
        special_results = self.special_layer.calculate()
        # Phase 9.5 New Layers
        ashtakavarga_results = self.ashtakavarga_layer.calculate_all()
        jaimini_results = self.jaimini_layer.calculate_all()

        for planet in planets:
            # Collect raw scores from each layer
            layer_raw_scores = {
                # Phase 9 Original Layers
                "dignity": dignity_results.get(planet),
                "house": house_results.get(planet),
                "aspect": aspect_results.get(planet),
                "shadbala": shadbala_results.get(planet),
                "navamsha": navamsha_results.get(planet),
                "varga": varga_results.get(planet),
                "yoga": yoga_results.get(planet),
                "special": special_results.get(planet),
                # Phase 9.5 New Layers
                "ashtakavarga": ashtakavarga_results.get(planet),
                "jaimini": jaimini_results.get(planet),
            }

            results[planet] = self._calculate_planet_score(planet, layer_raw_scores)

        return results

    def calculate_planet(self, planet: str) -> PlanetScoreResult:
        """Calculate score for a single planet"""
        all_results = self.calculate_all()
        return all_results.get(planet, self._empty_result(planet))

    def _calculate_planet_score(
        self,
        planet: str,
        layer_results: Dict[str, Any]
    ) -> PlanetScoreResult:
        """
        Calculate final score for a planet from all layer results.
        """
        layer_scores = {}
        weighted_sum = 0.0
        strengths = []
        weaknesses = []

        for layer_name, result in layer_results.items():
            if result is None:
                # No data for this layer
                layer_scores[layer_name] = LayerScore(
                    layer_name=layer_name,
                    raw_score=0.0,
                    weight=self.LAYER_WEIGHTS[layer_name],
                    weighted_score=0.0,
                    details=["No data available"]
                )
                continue

            # Extract raw score from result
            raw_score = self._get_raw_score(result)

            # Normalize to 0-1 range
            min_score, max_score = self.RAW_SCORE_RANGES[layer_name]
            normalized = (raw_score - min_score) / (max_score - min_score)
            normalized = max(0.0, min(1.0, normalized))  # Clamp to [0, 1]

            # Apply weight
            weight = self.LAYER_WEIGHTS[layer_name]
            weighted_score = normalized * weight
            weighted_sum += weighted_score

            # Get details from result
            details = self._get_details(result)

            layer_scores[layer_name] = LayerScore(
                layer_name=layer_name,
                raw_score=raw_score,
                weight=weight,
                weighted_score=weighted_score,
                details=details
            )

            # Identify strengths and weaknesses
            if raw_score > (max_score * 0.5):
                for detail in details[:2]:  # Top 2 positive details
                    if "+" in detail or any(word in detail.lower() for word in
                        ["exalted", "own", "vargottama", "raja", "yoga", "dig bala", "benefic"]):
                        strengths.append(f"{layer_name}: {detail}")
            elif raw_score < (min_score * 0.5):
                for detail in details[:2]:  # Top 2 negative details
                    if "-" in detail or any(word in detail.lower() for word in
                        ["debilitated", "combust", "enemy", "dusthana", "malefic", "gandanta"]):
                        weaknesses.append(f"{layer_name}: {detail}")

        # Final normalization to 0-100
        # raw_total is weighted_sum * 100, typically ranging from 15-55
        raw_total = weighted_sum * 100

        # Piecewise linear mapping based on calibration targets:
        # raw_total 15 -> score 25 (weak)
        # raw_total 35 -> score 50 (average)
        # raw_total 55 -> score 90 (strong)
        if raw_total <= self.RAW_AVERAGE:
            # Map RAW_WEAK..RAW_AVERAGE to SCORE_WEAK..SCORE_AVERAGE
            t = (raw_total - self.RAW_WEAK) / (self.RAW_AVERAGE - self.RAW_WEAK)
            t = max(0.0, min(1.0, t))
            calibrated_score = self.SCORE_WEAK + t * (self.SCORE_AVERAGE - self.SCORE_WEAK)
        else:
            # Map RAW_AVERAGE..RAW_STRONG to SCORE_AVERAGE..SCORE_STRONG
            t = (raw_total - self.RAW_AVERAGE) / (self.RAW_STRONG - self.RAW_AVERAGE)
            t = max(0.0, t)  # Allow extension above 1.0 for very strong planets
            calibrated_score = self.SCORE_AVERAGE + t * (self.SCORE_STRONG - self.SCORE_AVERAGE)

        # Soft clamp to [5, 98] to avoid extreme values
        final_score = max(5.0, min(98.0, calibrated_score))

        # Determine grade
        grade = self._get_grade(final_score)

        # Generate summary
        summary = self._generate_summary(planet, final_score, grade, strengths, weaknesses)

        return PlanetScoreResult(
            planet=planet,
            total_score=round(final_score, 1),
            raw_total=round(raw_total, 2),
            grade=grade,
            layer_scores=layer_scores,
            strengths=strengths[:5],  # Top 5
            weaknesses=weaknesses[:5],  # Top 5
            summary=summary
        )

    def _get_raw_score(self, result: Any) -> float:
        """Extract raw score from a layer result object"""
        # All our result dataclasses have either 'score' or 'total_score' attribute
        if hasattr(result, 'total_score'):
            return result.total_score
        if hasattr(result, 'score'):
            return result.score
        return 0.0

    def _get_details(self, result: Any) -> List[str]:
        """Extract details from a layer result object"""
        if hasattr(result, 'details'):
            return result.details
        return []

    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "S"  # Exceptional
        elif score >= 80:
            return "A"
        elif score >= 65:
            return "B"
        elif score >= 50:
            return "C"
        elif score >= 35:
            return "D"
        else:
            return "F"

    def _generate_summary(
        self,
        planet: str,
        score: float,
        grade: str,
        strengths: List[str],
        weaknesses: List[str]
    ) -> str:
        """Generate one-line summary for planet"""
        if grade == "S":
            return f"{planet} is exceptionally strong ({score:.0f}/100)"
        elif grade == "A":
            return f"{planet} is very strong with excellent placements ({score:.0f}/100)"
        elif grade == "B":
            return f"{planet} is above average with good strength ({score:.0f}/100)"
        elif grade == "C":
            return f"{planet} is average with balanced influences ({score:.0f}/100)"
        elif grade == "D":
            return f"{planet} is below average, may face challenges ({score:.0f}/100)"
        else:
            return f"{planet} is weak and may struggle to express positively ({score:.0f}/100)"

    def _empty_result(self, planet: str) -> PlanetScoreResult:
        """Return empty result for unknown planet"""
        return PlanetScoreResult(
            planet=planet,
            total_score=50.0,
            raw_total=50.0,
            grade="C",
            layer_scores={},
            strengths=[],
            weaknesses=[],
            summary=f"{planet}: No data available"
        )

    def get_scores_dict(self) -> Dict[str, float]:
        """Get simple dict of planet -> score for API response"""
        results = self.calculate_all()
        return {planet: result.total_score for planet, result in results.items()}

    def get_detailed_report(self) -> Dict[str, Any]:
        """Get detailed report for admin/debug purposes"""
        results = self.calculate_all()
        report = {}

        for planet, result in results.items():
            report[planet] = {
                "score": result.total_score,
                "grade": result.grade,
                "raw_total": result.raw_total,
                "summary": result.summary,
                "strengths": result.strengths,
                "weaknesses": result.weaknesses,
                "layers": {
                    name: {
                        "raw": layer.raw_score,
                        "weighted": round(layer.weighted_score * 100, 2),
                        "details": layer.details
                    }
                    for name, layer in result.layer_scores.items()
                }
            }

        return report


def calculate_planet_scores(
    digital_twin: Dict[str, Any],
    yogas: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, float]:
    """
    Convenience function to calculate planet scores from digital_twin.

    Args:
        digital_twin: Full digital twin data containing vargas, yogas, birth_time, etc.
        yogas: Optional list of yogas (if not in digital_twin)

    Returns:
        Dict mapping planet name to score (0-100)
    """
    # Extract data from digital_twin
    vargas = digital_twin.get("vargas", {})
    d1_data = vargas.get("D1", {})
    d9_data = vargas.get("D9", {})
    birth_time_data = digital_twin.get("birth_time", {})

    # Get yogas from digital_twin if not provided
    if yogas is None:
        yogas = digital_twin.get("yogas", [])

    scorer = PlanetScorer(d1_data, d9_data, vargas, yogas, birth_time_data)
    return scorer.get_scores_dict()


def get_planet_score_report(
    d1_data: Dict[str, Any],
    d9_data: Optional[Dict[str, Any]] = None,
    vargas: Optional[Dict[str, Dict[str, Any]]] = None,
    yogas: Optional[List[Dict[str, Any]]] = None,
    birth_time_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Get detailed planet score report for admin purposes.

    Returns:
        Detailed report with layer breakdowns
    """
    scorer = PlanetScorer(d1_data, d9_data, vargas, yogas, birth_time_data)
    return scorer.get_detailed_report()
