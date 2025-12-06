"""
Planet Scoring Layers - Phase 9 & Phase 9.5

Each layer analyzes specific aspects of planetary strength and combines
to produce a final 0-100 score for each planet.

Phase 9 Original Layer weights:
- Dignity: 20%
- House: 10%
- Aspect: 10%
- Shadbala: 15%
- Navamsha: 10%
- Varga: 10%
- Yoga: 15%
- Special: 10%

Phase 9.5 Enhanced Layers:
- Shadbala: Enhanced with full 6-component calculation (±25)
- Ashtakavarga: NEW - Bindu point system (±12)
- Jaimini: NEW - Chara Karaka based strength (±10)
- Yoga: Enhanced to 50+ yogas (±18)
"""

from .dignity_layer import DignityLayer
from .house_layer import HouseLayer
from .aspect_layer import AspectLayer
from .shadbala_layer import ShadbalaLayer
from .navamsha_layer import NavamshaLayer
from .varga_layer import VargaLayer
from .yoga_layer import YogaPlanetLayer
from .special_layer import SpecialLayer

# Phase 9.5 new layers
from .ashtakavarga_layer import AshtakavargaLayer
from .jaimini_layer import JaiminiPlanetLayer

__all__ = [
    # Phase 9 Original layers
    "DignityLayer",
    "HouseLayer",
    "AspectLayer",
    "ShadbalaLayer",
    "NavamshaLayer",
    "VargaLayer",
    "YogaPlanetLayer",
    "SpecialLayer",
    # Phase 9.5 New layers
    "AshtakavargaLayer",
    "JaiminiPlanetLayer",
]
