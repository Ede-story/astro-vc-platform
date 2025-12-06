"""
Phase 8.5 House Layers - Deep House Scoring Enhancement

These layers provide comprehensive house analysis using advanced Vedic astrology techniques:

1. BhavaBalaLayer (±15 points) - 7-component classical Bhava Bala
2. SudarshanaLayer (±5 points) - Triple perspective (Lagna/Moon/Sun) analysis
3. UpagrahaLayer (±3 points) - 5 shadow planet influences
4. SahamaLayer (±3 points) - 7 Arabic Parts/Sensitive Points
5. TaraBalLayer (±3 points) - Nakshatra-based Tara cycle analysis

Total potential contribution: ±29 points to house scores
"""

from .bhava_bala_layer import (
    BhavaBalaLayer,
    BhavaBalaResult,
)

from .sudarshana_layer import (
    SudarshanaLayer,
    SudarshanaResult,
)

from .upagraha_layer import (
    UpagrahaLayer,
    UpagrahaResult,
    UpagrahaData,
)

from .sahama_layer import (
    SahamaLayer,
    SahamaResult,
    SahamaData,
)

from .tara_bala_layer import (
    TaraBalLayer,
    TaraResult,
    TaraInfo,
    TARAS,
    NAKSHATRAS,
)


__all__ = [
    # Bhava Bala (±15 points)
    "BhavaBalaLayer",
    "BhavaBalaResult",
    # Sudarshana Chakra (±5 points)
    "SudarshanaLayer",
    "SudarshanaResult",
    # Upagrahas (±3 points)
    "UpagrahaLayer",
    "UpagrahaResult",
    "UpagrahaData",
    # Sahamas (±3 points)
    "SahamaLayer",
    "SahamaResult",
    "SahamaData",
    # Tara Bala (±3 points)
    "TaraBalLayer",
    "TaraResult",
    "TaraInfo",
    "TARAS",
    "NAKSHATRAS",
]
