"""
House Score Calculator - Combines all scoring layers

Phase 8.5 Enhanced: Added 5 new house layers for deep analysis
- BhavaBalaLayer: 7-component classical Bhava Bala (±15 points)
- SudarshanaLayer: Triple perspective Lagna/Moon/Sun analysis (±5 points)
- UpagrahaLayer: 5 shadow planet influences (±3 points)
- SahamaLayer: 7 Arabic Parts/Sensitive Points (±3 points)
- TaraBalLayer: Nakshatra-based Tara cycle analysis (±3 points)

Produces normalized scores 0-100 for each house with detailed breakdown
Target distribution:
- Average person: 45-55 per house
- Exceptional (Trump 10th): 85-95
- Weak house: 20-35
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .layers import D1Layer, D9Layer, VargaLayer, YogaLayer, JaiminiLayer, LayerResult

# Phase 8.5: Import new house layers
try:
    from .house_layers import (
        BhavaBalaLayer,
        SudarshanaLayer,
        UpagrahaLayer,
        SahamaLayer,
        TaraBalLayer,
    )
    PHASE_8_5_AVAILABLE = True
except ImportError:
    PHASE_8_5_AVAILABLE = False


@dataclass
class HouseScoreResult:
    """Complete result for a single house"""
    house_number: int
    raw_score: float
    normalized_score: float  # 0-100
    layer_contributions: Dict[str, float]
    details: List[str]


@dataclass
class ScoringResult:
    """Complete scoring result for all houses"""
    house_scores: Dict[int, float]  # house_num -> normalized score (0-100)
    house_details: Dict[int, HouseScoreResult]
    layer_breakdown: Dict[str, Dict[int, float]]  # layer_name -> {house: score}


class HouseScoreCalculator:
    """
    Main calculator that combines all scoring layers

    Layer weights:
    - D1 Layer: 40%
    - D9 Layer: 20%
    - Varga Layer: 15%
    - Yoga Layer: 15%
    - Jaimini Layer: 10%

    Normalization:
    - Raw scores are normalized to 0-100 range
    - Base score is 50 (average)
    - Each layer contribution shifts from base
    """

    # Normalization parameters
    BASE_SCORE = 50.0
    MIN_SCORE = 0.0
    MAX_SCORE = 100.0

    # Scaling factor: raw score of ~15 -> +35 normalized points (to reach ~85)
    # Increased from 2.5 to 2.8 to reach target for exceptional charts like Trump
    SCALE_FACTOR = 2.8

    def __init__(self, digital_twin: Dict[str, Any], yogas: List[Dict] = None):
        """
        Initialize calculator with digital twin data

        Args:
            digital_twin: Full digital twin from AstroBrain including vargas, chara_karakas, etc.
            yogas: List of found yogas (optional, can extract from stages)
        """
        self.digital_twin = digital_twin
        self.vargas = digital_twin.get("vargas", {})
        self.d1 = self.vargas.get("D1", {})
        self.d9 = self.vargas.get("D9", {})
        self.jaimini = digital_twin.get("chara_karakas", {})
        self.yogas = yogas or []

    def calculate(self) -> ScoringResult:
        """
        Calculate house scores using all layers

        Returns:
            ScoringResult with normalized scores and detailed breakdown
        """
        layer_results: Dict[str, LayerResult] = {}

        # Layer 1: D1 Base Scores (with D9 for Neecha Bhanga analysis)
        if self.d1:
            d1_layer = D1Layer(self.d1, self.d9)
            layer_results["D1"] = d1_layer.calculate()

        # Layer 2: D9 Modifications
        if self.d1 and self.d9:
            d9_layer = D9Layer(self.d1, self.d9)
            layer_results["D9"] = d9_layer.calculate()

        # Layer 3: Varga Strength
        if self.vargas:
            varga_layer = VargaLayer(self.vargas)
            layer_results["Varga"] = varga_layer.calculate()

        # Layer 4: Yoga Impact
        if self.yogas:
            yoga_layer = YogaLayer(self.yogas)
            layer_results["Yoga"] = yoga_layer.calculate()

        # Layer 5: Jaimini Influences
        if self.jaimini and self.d1:
            jaimini_layer = JaiminiLayer(self.jaimini, self.d1)
            layer_results["Jaimini"] = jaimini_layer.calculate()

        # Phase 8.5: Add new house layers
        if PHASE_8_5_AVAILABLE and self.d1:
            phase_8_5_scores = self._calculate_phase_8_5_layers()
            layer_results.update(phase_8_5_scores)

        # Combine all layers with weights
        return self._combine_layers(layer_results)

    def _calculate_phase_8_5_layers(self) -> Dict[str, LayerResult]:
        """
        Calculate Phase 8.5 house layers.

        Returns dictionary of LayerResult for each new layer:
        - BhavaBala (±15 points)
        - Sudarshana (±5 points)
        - Upagraha (±3 points)
        - Sahama (±3 points)
        - TaraBal (±3 points)
        """
        results = {}

        # Prepare chart data in the format layers expect
        chart_data = {
            'vargas': self.vargas,
            'D1': self.d1,
            'D9': self.d9,
        }

        try:
            # 1. Bhava Bala Layer (±15 points)
            bhava_layer = BhavaBalaLayer(chart_data)
            bhava_scores = bhava_layer.calculate_for_houses()
            results["BhavaBala"] = LayerResult(
                scores=bhava_scores,
                details={h: [f"Bhava Bala score: {s:.2f}"] for h, s in bhava_scores.items()}
            )
        except Exception:
            pass

        try:
            # 2. Sudarshana Chakra Layer (±5 points)
            sudarshana_layer = SudarshanaLayer(chart_data)
            sudarshana_scores = sudarshana_layer.calculate_for_houses()
            results["Sudarshana"] = LayerResult(
                scores=sudarshana_scores,
                details={h: [f"Sudarshana score: {s:.2f}"] for h, s in sudarshana_scores.items()}
            )
        except Exception:
            pass

        try:
            # 3. Upagraha Layer (±3 points)
            upagraha_layer = UpagrahaLayer(chart_data)
            upagraha_scores = upagraha_layer.calculate_for_houses()
            results["Upagraha"] = LayerResult(
                scores=upagraha_scores,
                details={h: [f"Upagraha score: {s:.2f}"] for h, s in upagraha_scores.items()}
            )
        except Exception:
            pass

        try:
            # 4. Sahama Layer (±3 points)
            sahama_layer = SahamaLayer(chart_data)
            sahama_scores = sahama_layer.calculate_for_houses()
            results["Sahama"] = LayerResult(
                scores=sahama_scores,
                details={h: [f"Sahama score: {s:.2f}"] for h, s in sahama_scores.items()}
            )
        except Exception:
            pass

        try:
            # 5. Tara Bala Layer (±3 points)
            tara_layer = TaraBalLayer(chart_data)
            tara_scores = tara_layer.calculate_for_houses()
            results["TaraBal"] = LayerResult(
                scores=tara_scores,
                details={h: [f"Tara Bala score: {s:.2f}"] for h, s in tara_scores.items()}
            )
        except Exception:
            pass

        return results

    def _combine_layers(self, layer_results: Dict[str, LayerResult]) -> ScoringResult:
        """Combine all layer results into final scores"""

        # Layer weights (original + Phase 8.5)
        weights = {
            "D1": D1Layer.WEIGHT,
            "D9": D9Layer.WEIGHT,
            "Varga": VargaLayer.WEIGHT,
            "Yoga": YogaLayer.WEIGHT,
            "Jaimini": JaiminiLayer.WEIGHT,
        }

        # Add Phase 8.5 layer weights if available
        if PHASE_8_5_AVAILABLE:
            weights.update({
                "BhavaBala": BhavaBalaLayer.WEIGHT,
                "Sudarshana": SudarshanaLayer.WEIGHT,
                "Upagraha": UpagrahaLayer.WEIGHT,
                "Sahama": SahamaLayer.WEIGHT,
                "TaraBal": TaraBalLayer.WEIGHT,
            })

        # Initialize combined scores
        raw_scores = {h: 0.0 for h in range(1, 13)}
        layer_breakdown = {name: {h: 0.0 for h in range(1, 13)} for name in weights}
        all_details = {h: [] for h in range(1, 13)}

        # Aggregate weighted scores
        for layer_name, result in layer_results.items():
            weight = weights.get(layer_name, 0.1)

            for house in range(1, 13):
                layer_score = result.scores.get(house, 0)
                weighted_score = layer_score * weight
                raw_scores[house] += weighted_score
                layer_breakdown[layer_name][house] = layer_score

                # Add details
                for detail in result.details.get(house, []):
                    all_details[house].append(f"[{layer_name}] {detail}")

        # Normalize to 0-100 range
        house_scores = {}
        house_details = {}

        for house in range(1, 13):
            raw = raw_scores[house]

            # Apply scaling and add to base
            normalized = self.BASE_SCORE + (raw * self.SCALE_FACTOR)

            # Clamp to valid range
            normalized = max(self.MIN_SCORE, min(self.MAX_SCORE, normalized))

            house_scores[house] = round(normalized, 1)

            # Create detailed result
            layer_contribs = {
                name: layer_breakdown[name][house]
                for name in layer_breakdown
            }

            house_details[house] = HouseScoreResult(
                house_number=house,
                raw_score=raw,
                normalized_score=normalized,
                layer_contributions=layer_contribs,
                details=all_details[house]
            )

        return ScoringResult(
            house_scores=house_scores,
            house_details=house_details,
            layer_breakdown=layer_breakdown
        )


def calculate_house_scores(
    digital_twin: Dict[str, Any],
    yogas: List[Dict] = None
) -> Dict[str, float]:
    """
    Convenience function to calculate house scores

    Args:
        digital_twin: Full digital twin data
        yogas: Optional list of yogas

    Returns:
        Dict mapping "house_1" -> score (0-100)
    """
    calculator = HouseScoreCalculator(digital_twin, yogas)
    result = calculator.calculate()

    # Convert to expected format
    return {f"house_{h}": score for h, score in result.house_scores.items()}


def get_house_score_details(
    digital_twin: Dict[str, Any],
    yogas: List[Dict] = None
) -> Dict[str, Any]:
    """
    Get detailed house score breakdown

    Returns complete scoring data including layer contributions
    """
    calculator = HouseScoreCalculator(digital_twin, yogas)
    result = calculator.calculate()

    details = {}
    for house, detail in result.house_details.items():
        details[f"house_{house}"] = {
            "score": detail.normalized_score,
            "raw": detail.raw_score,
            "layers": detail.layer_contributions,
            "reasons": detail.details[:10]  # Limit to top 10 reasons
        }

    return details
