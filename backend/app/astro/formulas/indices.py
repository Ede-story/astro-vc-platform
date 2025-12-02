"""
Indices Formulas Module

Consolidates all index calculations from Stages 4-8 into composite indices.
Provides final life area scores and overall life quality indices.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass
class LifeAreaIndex:
    """Score for a specific life area"""
    name: str
    score: float           # 0-100
    confidence: float      # 0-1 (based on data availability)
    contributing_factors: List[str]
    interpretation: str


@dataclass
class CompositeIndices:
    """All composite indices from Stage 4-8 analysis"""
    # Wealth & Material (from Stage 4)
    wealth_index: float
    material_security_index: float

    # Skills & Action (from Stage 5)
    initiative_index: float
    communication_index: float

    # Career & Status (from Stage 6)
    career_index: float
    authority_index: float

    # Creativity & Legacy (from Stage 7)
    creativity_index: float
    legacy_index: float

    # Profit & Karma (from Stage 8)
    gains_index: float
    karmic_index: float

    # Master indices (combined)
    overall_prosperity_index: float
    life_success_index: float
    spiritual_evolution_index: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "wealth": round(self.wealth_index, 1),
            "material_security": round(self.material_security_index, 1),
            "initiative": round(self.initiative_index, 1),
            "communication": round(self.communication_index, 1),
            "career": round(self.career_index, 1),
            "authority": round(self.authority_index, 1),
            "creativity": round(self.creativity_index, 1),
            "legacy": round(self.legacy_index, 1),
            "gains": round(self.gains_index, 1),
            "karmic": round(self.karmic_index, 1),
            "master_indices": {
                "prosperity": round(self.overall_prosperity_index, 1),
                "life_success": round(self.life_success_index, 1),
                "spiritual_evolution": round(self.spiritual_evolution_index, 1)
            }
        }


def calculate_wealth_index(
    hora_accumulation: float,
    d4_asset_potential: float,
    d1_second_house_score: float = 50.0
) -> float:
    """
    Calculate composite wealth index from D2 and D4 analysis.

    Formula: 40% D2 + 35% D4 + 25% D1 2nd house

    Args:
        hora_accumulation: Accumulation potential from D2 (0-100)
        d4_asset_potential: Asset potential from D4 (0-100)
        d1_second_house_score: D1 2nd house base score (0-100)

    Returns:
        Composite wealth index (0-100)
    """
    weighted = (
        hora_accumulation * 0.40 +
        d4_asset_potential * 0.35 +
        d1_second_house_score * 0.25
    )
    return max(0, min(100, weighted))


def calculate_material_security_index(
    wealth_index: float,
    fixed_assets_index: float,
    stability_index: float
) -> float:
    """
    Calculate material security index.

    Formula: Average of wealth, fixed assets, and stability

    Args:
        wealth_index: Composite wealth index
        fixed_assets_index: D4 fixed assets index
        stability_index: Financial stability index

    Returns:
        Material security index (0-100)
    """
    return (wealth_index + fixed_assets_index + stability_index) / 3


def calculate_career_composite_index(
    d10_career_strength: float,
    d10_professional_success: float,
    d10_authority: float,
    d1_tenth_house_score: float = 50.0
) -> float:
    """
    Calculate composite career index from D10 analysis.

    Formula: 35% strength + 30% success + 20% authority + 15% D1 10th

    Args:
        d10_career_strength: Career strength from D10
        d10_professional_success: Professional success from D10
        d10_authority: Authority index from D10
        d1_tenth_house_score: D1 10th house base score

    Returns:
        Composite career index (0-100)
    """
    weighted = (
        d10_career_strength * 0.35 +
        d10_professional_success * 0.30 +
        d10_authority * 0.20 +
        d1_tenth_house_score * 0.15
    )
    return max(0, min(100, weighted))


def calculate_creativity_composite_index(
    d5_creativity: float,
    d5_intellectual: float,
    d7_progeny: float,
    d5_spiritual: float
) -> float:
    """
    Calculate composite creativity index from D5 and D7.

    Formula: 35% creativity + 25% intellectual + 25% progeny + 15% spiritual

    Args:
        d5_creativity: Creativity index from D5
        d5_intellectual: Intellectual index from D5
        d7_progeny: Progeny index from D7
        d5_spiritual: Spiritual creativity from D5

    Returns:
        Composite creativity index (0-100)
    """
    weighted = (
        d5_creativity * 0.35 +
        d5_intellectual * 0.25 +
        d7_progeny * 0.25 +
        d5_spiritual * 0.15
    )
    return max(0, min(100, weighted))


def calculate_gains_composite_index(
    d11_gains: float,
    d11_network: float,
    d11_desire_fulfillment: float
) -> float:
    """
    Calculate composite gains index from D11.

    Formula: 40% gains + 30% network + 30% desire fulfillment

    Args:
        d11_gains: Gains potential from D11
        d11_network: Network index from D11
        d11_desire_fulfillment: Desire fulfillment from D11

    Returns:
        Composite gains index (0-100)
    """
    weighted = (
        d11_gains * 0.40 +
        d11_network * 0.30 +
        d11_desire_fulfillment * 0.30
    )
    return max(0, min(100, weighted))


def calculate_overall_prosperity_index(
    wealth_index: float,
    career_index: float,
    gains_index: float,
    material_security: float
) -> float:
    """
    Calculate overall prosperity (material success) index.

    Formula: 30% wealth + 30% career + 25% gains + 15% security

    Args:
        wealth_index: Composite wealth index
        career_index: Composite career index
        gains_index: Composite gains index
        material_security: Material security index

    Returns:
        Overall prosperity index (0-100)
    """
    weighted = (
        wealth_index * 0.30 +
        career_index * 0.30 +
        gains_index * 0.25 +
        material_security * 0.15
    )
    return max(0, min(100, weighted))


def calculate_life_success_index(
    prosperity_index: float,
    creativity_index: float,
    initiative_index: float,
    communication_index: float
) -> float:
    """
    Calculate overall life success index.

    Formula: 35% prosperity + 25% creativity + 25% initiative + 15% communication

    Args:
        prosperity_index: Overall prosperity index
        creativity_index: Composite creativity index
        initiative_index: Initiative index from D3
        communication_index: Communication index from D3

    Returns:
        Life success index (0-100)
    """
    weighted = (
        prosperity_index * 0.35 +
        creativity_index * 0.25 +
        initiative_index * 0.25 +
        communication_index * 0.15
    )
    return max(0, min(100, weighted))


def calculate_spiritual_evolution_index(
    karmic_balance: float,
    spiritual_creativity: float,
    d9_synergy: float = 50.0,
    legacy_index: float = 50.0
) -> float:
    """
    Calculate spiritual evolution index.

    Formula: 35% karmic + 30% spiritual creativity + 20% D9 synergy + 15% legacy

    Args:
        karmic_balance: Karmic balance from D12
        spiritual_creativity: Spiritual creativity from D5
        d9_synergy: D1-D9 synergy score from Stage 2
        legacy_index: Legacy index from D7

    Returns:
        Spiritual evolution index (0-100)
    """
    weighted = (
        karmic_balance * 0.35 +
        spiritual_creativity * 0.30 +
        d9_synergy * 0.20 +
        legacy_index * 0.15
    )
    return max(0, min(100, weighted))


def calculate_composite_indices(
    stage4_result: Optional[Dict[str, Any]] = None,
    stage5_result: Optional[Dict[str, Any]] = None,
    stage6_result: Optional[Dict[str, Any]] = None,
    stage7_result: Optional[Dict[str, Any]] = None,
    stage8_result: Optional[Dict[str, Any]] = None,
    d9_synergy: float = 50.0
) -> CompositeIndices:
    """
    Calculate all composite indices from Stage 4-8 results.

    Args:
        stage4_result: Stage 4 result dict
        stage5_result: Stage 5 result dict
        stage6_result: Stage 6 result dict
        stage7_result: Stage 7 result dict
        stage8_result: Stage 8 result dict
        d9_synergy: D1-D9 synergy from Stage 2

    Returns:
        CompositeIndices with all calculated indices
    """
    # Extract values with defaults
    # Stage 4 - Wealth
    s4 = stage4_result or {}
    s4_indices = s4.get("indices", {})
    wealth_accum = s4_indices.get("wealth_accumulation", 50.0)
    fixed_assets = s4_indices.get("fixed_assets", 50.0)
    financial_stability = s4_indices.get("financial_stability", 50.0)

    # Stage 5 - Skills
    s5 = stage5_result or {}
    s5_indices = s5.get("indices", {})
    initiative = s5_indices.get("initiative", 50.0)
    communication = s5_indices.get("communication", 50.0)

    # Stage 6 - Career
    s6 = stage6_result or {}
    s6_indices = s6.get("indices", {})
    career_strength = s6_indices.get("career_strength", 50.0)
    professional_success = s6_indices.get("professional_success", 50.0)
    authority = s6_indices.get("authority", 50.0)

    # Stage 7 - Creativity
    s7 = stage7_result or {}
    s7_indices = s7.get("indices", {})
    creativity = s7_indices.get("creativity", 50.0)
    intellectual = s7_indices.get("intellectual", 50.0)
    progeny = s7_indices.get("progeny", 50.0)
    spiritual_creativity = s7_indices.get("spiritual_creativity", 50.0)

    # Stage 8 - Profit/Karma
    s8 = stage8_result or {}
    s8_indices = s8.get("indices", {})
    gains = s8_indices.get("gains", 50.0)
    network = s8_indices.get("network", 50.0)
    desire_fulfillment = s8_indices.get("desire_fulfillment", 50.0)
    karmic_balance = s8_indices.get("karmic_balance", 50.0)

    # Calculate composite indices
    wealth_composite = calculate_wealth_index(wealth_accum, fixed_assets)
    material_security = calculate_material_security_index(
        wealth_composite, fixed_assets, financial_stability
    )
    career_composite = calculate_career_composite_index(
        career_strength, professional_success, authority
    )
    creativity_composite = calculate_creativity_composite_index(
        creativity, intellectual, progeny, spiritual_creativity
    )
    gains_composite = calculate_gains_composite_index(
        gains, network, desire_fulfillment
    )

    # Master indices
    prosperity = calculate_overall_prosperity_index(
        wealth_composite, career_composite, gains_composite, material_security
    )
    life_success = calculate_life_success_index(
        prosperity, creativity_composite, initiative, communication
    )
    spiritual_evolution = calculate_spiritual_evolution_index(
        karmic_balance, spiritual_creativity, d9_synergy, progeny
    )

    return CompositeIndices(
        wealth_index=wealth_composite,
        material_security_index=material_security,
        initiative_index=initiative,
        communication_index=communication,
        career_index=career_composite,
        authority_index=authority,
        creativity_index=creativity_composite,
        legacy_index=progeny,  # Using progeny as legacy proxy
        gains_index=gains_composite,
        karmic_index=karmic_balance,
        overall_prosperity_index=prosperity,
        life_success_index=life_success,
        spiritual_evolution_index=spiritual_evolution
    )


def get_life_area_interpretations(indices: CompositeIndices) -> Dict[str, LifeAreaIndex]:
    """
    Generate interpretations for each life area based on indices.

    Args:
        indices: Calculated composite indices

    Returns:
        Dict mapping life area to LifeAreaIndex with interpretations
    """
    def get_interpretation(score: float, area: str) -> str:
        if score >= 75:
            return f"Excellent potential in {area}. Natural strengths support success."
        elif score >= 60:
            return f"Good potential in {area}. Favorable conditions with some effort required."
        elif score >= 45:
            return f"Moderate potential in {area}. Balanced approach recommended."
        elif score >= 30:
            return f"Challenging area requiring extra attention and effort in {area}."
        else:
            return f"Significant growth opportunity in {area}. Focused work needed."

    return {
        "wealth": LifeAreaIndex(
            name="Wealth & Finances",
            score=indices.wealth_index,
            confidence=0.85,
            contributing_factors=["D2 Hora", "D4 Chaturthamsha", "2nd House"],
            interpretation=get_interpretation(indices.wealth_index, "wealth and finances")
        ),
        "career": LifeAreaIndex(
            name="Career & Status",
            score=indices.career_index,
            confidence=0.90,
            contributing_factors=["D10 Dashamsha", "10th House", "Saturn"],
            interpretation=get_interpretation(indices.career_index, "career and public status")
        ),
        "creativity": LifeAreaIndex(
            name="Creativity & Legacy",
            score=indices.creativity_index,
            confidence=0.80,
            contributing_factors=["D5 Panchamsha", "D7 Saptamsha", "5th House"],
            interpretation=get_interpretation(indices.creativity_index, "creative expression")
        ),
        "initiative": LifeAreaIndex(
            name="Initiative & Skills",
            score=indices.initiative_index,
            confidence=0.85,
            contributing_factors=["D3 Drekkana", "Mars", "3rd House"],
            interpretation=get_interpretation(indices.initiative_index, "initiative and action")
        ),
        "gains": LifeAreaIndex(
            name="Gains & Expansion",
            score=indices.gains_index,
            confidence=0.80,
            contributing_factors=["D11 Rudramsha", "Jupiter", "11th House"],
            interpretation=get_interpretation(indices.gains_index, "gains and networking")
        ),
        "spiritual": LifeAreaIndex(
            name="Spiritual Evolution",
            score=indices.spiritual_evolution_index,
            confidence=0.75,
            contributing_factors=["D12 Dwadashamsha", "D9 Navamsha", "12th House"],
            interpretation=get_interpretation(indices.spiritual_evolution_index, "spiritual growth")
        )
    }


def calculate_house_score_adjustments(
    stage4_adj: Dict[str, float],
    stage5_adj: Dict[str, float],
    stage6_adj: Dict[str, float],
    stage7_adj: Dict[str, float],
    stage8_adj: Dict[str, float]
) -> Dict[str, float]:
    """
    Combine house score adjustments from all stages.

    Args:
        stage4_adj: Adjustments from Stage 4
        stage5_adj: Adjustments from Stage 5
        stage6_adj: Adjustments from Stage 6
        stage7_adj: Adjustments from Stage 7
        stage8_adj: Adjustments from Stage 8

    Returns:
        Combined house score adjustments
    """
    combined = {}

    all_adjustments = [stage4_adj, stage5_adj, stage6_adj, stage7_adj, stage8_adj]

    # Collect all house keys
    all_houses = set()
    for adj in all_adjustments:
        all_houses.update(adj.keys())

    # Sum adjustments for each house
    for house in all_houses:
        total = 0.0
        count = 0
        for adj in all_adjustments:
            if house in adj:
                total += adj[house]
                count += 1

        if count > 0:
            combined[house] = round(total / count, 2)  # Average adjustment

    return combined
