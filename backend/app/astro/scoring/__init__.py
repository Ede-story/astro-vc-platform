"""
Deep Scoring System - Phase 8 & Phase 9
Comprehensive house and planet scoring based on 110+ Vedic astrology techniques

Phase 8 - House Scoring Architecture:
- Layer 1 (D1): Base scores from planetary positions, lords, aspects (40%)
- Layer 2 (D9): Navamsha modifications and Vargottama bonuses (20%)
- Layer 3 (Varga): Multi-divisional strength from 16 vargas (15%)
- Layer 4 (Yoga): Yoga impact per house (15%)
- Layer 5 (Jaimini): Chara karaka influences (10%)

Phase 9 - Planet Scoring Architecture:
- Dignity Layer (20%): Sign placement, Neecha Bhanga
- House Layer (10%): Dig Bala, functional status
- Aspect Layer (10%): Graha Drishti, Kartari
- Shadbala Layer (15%): Six-fold strength
- Navamsha Layer (10%): D9 dignity, Vargottama
- Varga Layer (10%): Multi-divisional charts
- Yoga Layer (15%): Yoga participation
- Special Layer (10%): Combustion, Gandanta, etc.

Target calibration:
- Trump's 10th house: 85-95 (billionaire real estate mogul, president)
- Trump's Sun: 85-90
- Vadim's Mars (with Neecha Bhanga): 75-80
- Average: 45-55
"""

from .calculator import HouseScoreCalculator, calculate_house_scores, get_house_score_details
from .layers import D1Layer, D9Layer, VargaLayer, YogaLayer, JaiminiLayer
from .neecha_bhanga import (
    NeechaBhangaAnalyzer,
    NeechaBhangaResult,
    analyze_all_neecha_bhanga,
    get_house_neecha_bhanga_modifier,
    get_neecha_bhanga_details,
)
from .planet_scorer import (
    PlanetScorer,
    PlanetScoreResult,
    LayerScore,
    calculate_planet_scores,
    get_planet_score_report,
)
from .planet_layers import (
    DignityLayer,
    HouseLayer,
    AspectLayer,
    ShadbalaLayer,
    NavamshaLayer as PlanetNavamshaLayer,
    VargaLayer as PlanetVargaLayer,
    YogaPlanetLayer,
    SpecialLayer,
)

__all__ = [
    # Phase 8 - House Scoring
    "HouseScoreCalculator",
    "calculate_house_scores",
    "get_house_score_details",
    "D1Layer",
    "D9Layer",
    "VargaLayer",
    "YogaLayer",
    "JaiminiLayer",
    # Neecha Bhanga
    "NeechaBhangaAnalyzer",
    "NeechaBhangaResult",
    "analyze_all_neecha_bhanga",
    "get_house_neecha_bhanga_modifier",
    "get_neecha_bhanga_details",
    # Phase 9 - Planet Scoring
    "PlanetScorer",
    "PlanetScoreResult",
    "LayerScore",
    "calculate_planet_scores",
    "get_planet_score_report",
    # Planet Layers
    "DignityLayer",
    "HouseLayer",
    "AspectLayer",
    "ShadbalaLayer",
    "PlanetNavamshaLayer",
    "PlanetVargaLayer",
    "YogaPlanetLayer",
    "SpecialLayer",
]
