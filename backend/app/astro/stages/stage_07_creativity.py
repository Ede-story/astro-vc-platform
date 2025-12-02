"""
Stage 7: Creativity & Legacy Analysis (D5 Panchamsha + D7 Saptamsha)

D5 (Panchamsha): Shows creativity, intellect, merit, and spiritual practices
D7 (Saptamsha): Shows progeny, creative legacy, and continuation through children

Output: CreativityAnalysis with indices for creative potential and legacy
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .varga_utils import (
    parse_varga_chart, VargaChartData, VargaPlanetData,
    get_sign_lord, is_benefic, is_malefic, get_dignity_in_sign,
    is_kendra, is_trikona, is_dusthana, get_element
)
from ..models.types import Planet, Zodiac, Dignity


class CreativeType(Enum):
    """Types of creative expression"""
    ARTISTIC = "artistic"           # Visual arts, music, dance
    INTELLECTUAL = "intellectual"   # Writing, research, philosophy
    PERFORMATIVE = "performative"   # Acting, entertainment
    ENTREPRENEURIAL = "entrepreneurial"  # Business creativity
    TECHNICAL = "technical"         # Engineering, innovation
    SPIRITUAL = "spiritual"         # Religious, mystical


class LegacyType(Enum):
    """Types of legacy one may leave"""
    CHILDREN = "children"           # Through biological progeny
    CREATIVE_WORKS = "creative_works"  # Art, books, inventions
    INSTITUTIONS = "institutions"   # Organizations, foundations
    TEACHINGS = "teachings"         # Knowledge, philosophy
    WEALTH = "wealth"               # Financial legacy


@dataclass
class PanchamshaAnalysis:
    """D5 Panchamsha chart analysis"""
    d5_ascendant: Zodiac
    d5_element: str
    fifth_lord_position: Dict[str, Any]
    jupiter_position: Dict[str, Any]  # Karaka for wisdom/creativity
    sun_position: Dict[str, Any]      # Karaka for creative self-expression
    mercury_position: Dict[str, Any]  # Karaka for intellect
    creative_indicators: List[str]
    spiritual_indicators: List[str]


@dataclass
class SaptamshaAnalysis:
    """D7 Saptamsha chart analysis"""
    d7_ascendant: Zodiac
    d7_element: str
    fifth_lord_position: Dict[str, Any]  # 5th lord shows children
    jupiter_position: Dict[str, Any]     # Putrakaraka
    planets_in_fifth: List[str]
    progeny_indicators: List[str]
    legacy_indicators: List[str]


@dataclass
class Stage7Result:
    """Complete Stage 7 analysis output"""
    panchamsha: PanchamshaAnalysis
    saptamsha: SaptamshaAnalysis

    # Core indices
    creativity_index: float          # 0-100 creative potential
    intellectual_index: float        # 0-100 intellectual abilities
    progeny_index: float             # 0-100 children/legacy potential
    spiritual_creativity_index: float  # 0-100 spiritual creative expression

    # Derived attributes
    primary_creative_types: List[CreativeType]
    legacy_types: List[LegacyType]
    creative_peak_periods: List[str]  # Timing hints

    # House score adjustments
    house_score_adjustments: Dict[str, float]

    # Interpretations
    creative_strengths: List[str]
    creative_challenges: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "panchamsha": {
                "ascendant": self.panchamsha.d5_ascendant.name,
                "element": self.panchamsha.d5_element,
                "fifth_lord": self.panchamsha.fifth_lord_position,
                "jupiter": self.panchamsha.jupiter_position,
                "sun": self.panchamsha.sun_position,
                "mercury": self.panchamsha.mercury_position,
                "creative_indicators": self.panchamsha.creative_indicators,
                "spiritual_indicators": self.panchamsha.spiritual_indicators
            },
            "saptamsha": {
                "ascendant": self.saptamsha.d7_ascendant.name,
                "element": self.saptamsha.d7_element,
                "fifth_lord": self.saptamsha.fifth_lord_position,
                "jupiter": self.saptamsha.jupiter_position,
                "planets_in_fifth": self.saptamsha.planets_in_fifth,
                "progeny_indicators": self.saptamsha.progeny_indicators,
                "legacy_indicators": self.saptamsha.legacy_indicators
            },
            "indices": {
                "creativity": round(self.creativity_index, 1),
                "intellectual": round(self.intellectual_index, 1),
                "progeny": round(self.progeny_index, 1),
                "spiritual_creativity": round(self.spiritual_creativity_index, 1)
            },
            "creative_types": [c.value for c in self.primary_creative_types],
            "legacy_types": [l.value for l in self.legacy_types],
            "peak_periods": self.creative_peak_periods,
            "house_adjustments": self.house_score_adjustments,
            "strengths": self.creative_strengths,
            "challenges": self.creative_challenges,
            "recommendations": self.recommendations
        }


class Stage07CreativityAnalysis:
    """
    Stage 7: Analyze D5 (Panchamsha) and D7 (Saptamsha) for creativity and legacy.

    Input: digital_twin, D1 basic data
    Output: Stage7Result with creativity indices
    """

    def __init__(
        self,
        digital_twin: Dict[str, Any],
        d1_planets: List[Any],
        house_lords: Dict[int, Dict[str, Any]]
    ):
        self.digital_twin = digital_twin
        self.d1_planets = d1_planets
        self.house_lords = house_lords

        # Parse charts
        self.d5 = parse_varga_chart(digital_twin, "D5")
        self.d7 = parse_varga_chart(digital_twin, "D7")
        self.d1 = parse_varga_chart(digital_twin, "D1")

    def analyze(self) -> Stage7Result:
        """Run complete Stage 7 analysis"""
        panchamsha = self._analyze_panchamsha()
        saptamsha = self._analyze_saptamsha()

        # Calculate indices
        creativity_index = self._calculate_creativity_index(panchamsha, saptamsha)
        intellectual_index = self._calculate_intellectual_index(panchamsha)
        progeny_index = self._calculate_progeny_index(saptamsha)
        spiritual_index = self._calculate_spiritual_creativity_index(panchamsha)

        # Determine attributes
        creative_types = self._determine_creative_types(panchamsha, saptamsha)
        legacy_types = self._determine_legacy_types(saptamsha, progeny_index)
        peak_periods = self._determine_peak_periods(panchamsha, saptamsha)

        # House adjustments
        adjustments = self._calculate_house_adjustments(creativity_index, progeny_index)

        # Interpretations
        strengths, challenges = self._generate_interpretations(
            panchamsha, saptamsha, creativity_index
        )
        recommendations = self._generate_recommendations(
            panchamsha, creative_types, creativity_index
        )

        return Stage7Result(
            panchamsha=panchamsha,
            saptamsha=saptamsha,
            creativity_index=creativity_index,
            intellectual_index=intellectual_index,
            progeny_index=progeny_index,
            spiritual_creativity_index=spiritual_index,
            primary_creative_types=creative_types,
            legacy_types=legacy_types,
            creative_peak_periods=peak_periods,
            house_score_adjustments=adjustments,
            creative_strengths=strengths,
            creative_challenges=challenges,
            recommendations=recommendations
        )

    def _analyze_panchamsha(self) -> PanchamshaAnalysis:
        """Analyze D5 Panchamsha chart"""
        if not self.d5:
            return self._default_panchamsha_analysis()

        d5_asc = self.d5.ascendant_sign
        d5_element = get_element(d5_asc)

        # Fifth lord position
        fifth_sign = self.d5.houses.get(5, Zodiac.LEO)
        fifth_lord = get_sign_lord(fifth_sign)
        fifth_lord_data = self.d5.planets.get(fifth_lord)

        fifth_lord_position = {}
        if fifth_lord_data:
            dignity = fifth_lord_data.dignity or get_dignity_in_sign(fifth_lord, fifth_lord_data.sign)
            fifth_lord_position = {
                "planet": fifth_lord.value,
                "sign": fifth_lord_data.sign.name,
                "house": fifth_lord_data.house,
                "dignity": dignity.value if dignity else "neutral"
            }

        # Jupiter position (karaka for creativity/wisdom)
        jupiter_data = self.d5.planets.get(Planet.JUPITER)
        jupiter_position = {}
        if jupiter_data:
            jup_dignity = jupiter_data.dignity or get_dignity_in_sign(Planet.JUPITER, jupiter_data.sign)
            jupiter_position = {
                "sign": jupiter_data.sign.name,
                "house": jupiter_data.house,
                "dignity": jup_dignity.value if jup_dignity else "neutral"
            }

        # Sun position (karaka for creative self-expression)
        sun_data = self.d5.planets.get(Planet.SUN)
        sun_position = {}
        if sun_data:
            sun_dignity = sun_data.dignity or get_dignity_in_sign(Planet.SUN, sun_data.sign)
            sun_position = {
                "sign": sun_data.sign.name,
                "house": sun_data.house,
                "dignity": sun_dignity.value if sun_dignity else "neutral"
            }

        # Mercury position (karaka for intellect)
        mercury_data = self.d5.planets.get(Planet.MERCURY)
        mercury_position = {}
        if mercury_data:
            merc_dignity = mercury_data.dignity or get_dignity_in_sign(Planet.MERCURY, mercury_data.sign)
            mercury_position = {
                "sign": mercury_data.sign.name,
                "house": mercury_data.house,
                "dignity": merc_dignity.value if merc_dignity else "neutral"
            }

        # Creative indicators
        creative_indicators = []

        if jupiter_data and is_kendra(jupiter_data.house):
            creative_indicators.append("Jupiter in kendra - expansive creativity")
        if jupiter_data and jupiter_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
            creative_indicators.append("Jupiter dignified - natural wisdom and creativity")

        if sun_data and is_kendra(sun_data.house):
            creative_indicators.append("Sun in kendra - strong creative self-expression")

        # Venus for artistic creativity
        venus_data = self.d5.planets.get(Planet.VENUS)
        if venus_data and is_kendra(venus_data.house):
            creative_indicators.append("Venus well-placed - artistic talent")
        if venus_data and venus_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
            creative_indicators.append("Venus dignified - refined aesthetic sense")

        if mercury_data and mercury_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
            creative_indicators.append("Mercury strong - intellectual creativity")

        # Spiritual indicators
        spiritual_indicators = []

        # Ketu for spiritual insight
        ketu_data = self.d5.planets.get(Planet.KETU)
        if ketu_data:
            if is_trikona(ketu_data.house):
                spiritual_indicators.append("Ketu in trikona - spiritual inclination")
            if ketu_data.house == 12:
                spiritual_indicators.append("Ketu in 12th - moksha-oriented creativity")

        # Jupiter in spiritual houses
        if jupiter_data and jupiter_data.house in [5, 9, 12]:
            spiritual_indicators.append("Jupiter in spiritual house - dharmic creativity")

        # Water element ascendant adds intuition
        if d5_element == "water":
            spiritual_indicators.append("Water ascendant - intuitive creative flow")

        return PanchamshaAnalysis(
            d5_ascendant=d5_asc,
            d5_element=d5_element,
            fifth_lord_position=fifth_lord_position,
            jupiter_position=jupiter_position,
            sun_position=sun_position,
            mercury_position=mercury_position,
            creative_indicators=creative_indicators,
            spiritual_indicators=spiritual_indicators
        )

    def _analyze_saptamsha(self) -> SaptamshaAnalysis:
        """Analyze D7 Saptamsha chart"""
        if not self.d7:
            return self._default_saptamsha_analysis()

        d7_asc = self.d7.ascendant_sign
        d7_element = get_element(d7_asc)

        # Fifth lord position (shows children)
        fifth_sign = self.d7.houses.get(5, Zodiac.LEO)
        fifth_lord = get_sign_lord(fifth_sign)
        fifth_lord_data = self.d7.planets.get(fifth_lord)

        fifth_lord_position = {}
        if fifth_lord_data:
            dignity = fifth_lord_data.dignity or get_dignity_in_sign(fifth_lord, fifth_lord_data.sign)
            fifth_lord_position = {
                "planet": fifth_lord.value,
                "sign": fifth_lord_data.sign.name,
                "house": fifth_lord_data.house,
                "dignity": dignity.value if dignity else "neutral"
            }

        # Jupiter position (Putrakaraka - significator of children)
        jupiter_data = self.d7.planets.get(Planet.JUPITER)
        jupiter_position = {}
        if jupiter_data:
            jup_dignity = jupiter_data.dignity or get_dignity_in_sign(Planet.JUPITER, jupiter_data.sign)
            jupiter_position = {
                "sign": jupiter_data.sign.name,
                "house": jupiter_data.house,
                "dignity": jup_dignity.value if jup_dignity else "neutral"
            }

        # Planets in 5th house
        planets_in_fifth = [p.value for p in self.d7.get_planets_in_house(5)]

        # Progeny indicators
        progeny_indicators = []

        if jupiter_data:
            if is_kendra(jupiter_data.house) or is_trikona(jupiter_data.house):
                progeny_indicators.append("Jupiter well-placed - favorable for children")
            if jupiter_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                progeny_indicators.append("Jupiter dignified - strong progeny indications")

        if fifth_lord_data:
            if is_kendra(fifth_lord_data.house):
                progeny_indicators.append("5th lord in kendra - good for children")
            if fifth_lord_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                progeny_indicators.append("5th lord dignified - supportive for progeny")

        # Benefics in 5th
        benefics_in_5 = [p for p in planets_in_fifth if p in ["Jupiter", "Venus", "Mercury", "Moon"]]
        if benefics_in_5:
            progeny_indicators.append(f"Benefics in 5th ({', '.join(benefics_in_5)}) - auspicious")

        # Legacy indicators
        legacy_indicators = []

        # 9th house for legacy through dharma
        ninth_lord = get_sign_lord(self.d7.houses.get(9, Zodiac.SAGITTARIUS))
        ninth_lord_data = self.d7.planets.get(ninth_lord)
        if ninth_lord_data and is_kendra(ninth_lord_data.house):
            legacy_indicators.append("9th lord well-placed - dharmic legacy")

        # Saturn for lasting legacy
        saturn_data = self.d7.planets.get(Planet.SATURN)
        if saturn_data and saturn_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
            legacy_indicators.append("Saturn dignified - enduring legacy")

        # Sun for recognition legacy
        sun_data = self.d7.planets.get(Planet.SUN)
        if sun_data and is_kendra(sun_data.house):
            legacy_indicators.append("Sun in kendra - recognized legacy")

        return SaptamshaAnalysis(
            d7_ascendant=d7_asc,
            d7_element=d7_element,
            fifth_lord_position=fifth_lord_position,
            jupiter_position=jupiter_position,
            planets_in_fifth=planets_in_fifth,
            progeny_indicators=progeny_indicators,
            legacy_indicators=legacy_indicators
        )

    def _calculate_creativity_index(
        self, panchamsha: PanchamshaAnalysis, saptamsha: SaptamshaAnalysis
    ) -> float:
        """Calculate overall creativity index"""
        score = 50.0

        # D5 factors (60% weight)
        jupiter = panchamsha.jupiter_position
        if jupiter:
            dignity = jupiter.get("dignity", "neutral")
            if dignity == "exalted":
                score += 15
            elif dignity == "own_sign":
                score += 12
            elif dignity == "debilitated":
                score -= 8

            if is_kendra(jupiter.get("house", 6)):
                score += 8

        # Sun creativity
        sun = panchamsha.sun_position
        if sun:
            dignity = sun.get("dignity", "neutral")
            if dignity in ["exalted", "own_sign"]:
                score += 10

        # Creative indicators bonus
        score += len(panchamsha.creative_indicators) * 4

        # D7 factors (40% weight for creative legacy)
        score += len(saptamsha.legacy_indicators) * 3

        return max(0, min(100, score))

    def _calculate_intellectual_index(self, panchamsha: PanchamshaAnalysis) -> float:
        """Calculate intellectual potential index"""
        score = 50.0

        # Mercury is primary indicator
        mercury = panchamsha.mercury_position
        if mercury:
            dignity = mercury.get("dignity", "neutral")
            if dignity == "exalted":
                score += 25
            elif dignity == "own_sign":
                score += 20
            elif dignity == "debilitated":
                score -= 12

            if is_kendra(mercury.get("house", 6)):
                score += 10

        # Jupiter adds wisdom
        jupiter = panchamsha.jupiter_position
        if jupiter:
            dignity = jupiter.get("dignity", "neutral")
            if dignity in ["exalted", "own_sign"]:
                score += 10

        # Air element boosts intellect
        if panchamsha.d5_element == "air":
            score += 8

        return max(0, min(100, score))

    def _calculate_progeny_index(self, saptamsha: SaptamshaAnalysis) -> float:
        """Calculate progeny/children potential index"""
        score = 50.0

        # Jupiter (Putrakaraka) is primary
        jupiter = saptamsha.jupiter_position
        if jupiter:
            dignity = jupiter.get("dignity", "neutral")
            if dignity == "exalted":
                score += 25
            elif dignity == "own_sign":
                score += 20
            elif dignity == "debilitated":
                score -= 15

            house = jupiter.get("house", 6)
            if is_kendra(house) or is_trikona(house):
                score += 12

        # 5th lord position
        fifth_lord = saptamsha.fifth_lord_position
        if fifth_lord:
            dignity = fifth_lord.get("dignity", "neutral")
            if dignity in ["exalted", "own_sign"]:
                score += 10
            if is_kendra(fifth_lord.get("house", 6)):
                score += 8

        # Progeny indicators
        score += len(saptamsha.progeny_indicators) * 4

        return max(0, min(100, score))

    def _calculate_spiritual_creativity_index(self, panchamsha: PanchamshaAnalysis) -> float:
        """Calculate spiritual creative expression index"""
        score = 50.0

        # Spiritual indicators are primary
        score += len(panchamsha.spiritual_indicators) * 8

        # Jupiter in spiritual houses
        jupiter = panchamsha.jupiter_position
        if jupiter:
            house = jupiter.get("house", 6)
            if house in [5, 9, 12]:
                score += 15
            if jupiter.get("dignity") in ["exalted", "own_sign"]:
                score += 10

        # Water element adds intuition
        if panchamsha.d5_element == "water":
            score += 10

        return max(0, min(100, score))

    def _determine_creative_types(
        self, panchamsha: PanchamshaAnalysis, saptamsha: SaptamshaAnalysis
    ) -> List[CreativeType]:
        """Determine primary creative expression types"""
        types = []

        # Venus for artistic
        if self.d5:
            venus_data = self.d5.planets.get(Planet.VENUS)
            if venus_data and venus_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                types.append(CreativeType.ARTISTIC)

        # Mercury for intellectual
        mercury = panchamsha.mercury_position
        if mercury and mercury.get("dignity") in ["exalted", "own_sign"]:
            types.append(CreativeType.INTELLECTUAL)

        # Sun for performative
        sun = panchamsha.sun_position
        if sun and sun.get("dignity") in ["exalted", "own_sign"]:
            types.append(CreativeType.PERFORMATIVE)

        # Mars for technical
        if self.d5:
            mars_data = self.d5.planets.get(Planet.MARS)
            if mars_data and mars_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                types.append(CreativeType.TECHNICAL)

        # Spiritual indicators
        if panchamsha.spiritual_indicators:
            types.append(CreativeType.SPIRITUAL)

        # Saturn for entrepreneurial
        if self.d5:
            saturn_data = self.d5.planets.get(Planet.SATURN)
            if saturn_data and is_kendra(saturn_data.house):
                types.append(CreativeType.ENTREPRENEURIAL)

        if not types:
            types = [CreativeType.INTELLECTUAL]

        return list(set(types))[:4]

    def _determine_legacy_types(
        self, saptamsha: SaptamshaAnalysis, progeny_index: float
    ) -> List[LegacyType]:
        """Determine types of legacy indicated"""
        types = []

        # Children legacy if progeny index is strong
        if progeny_index > 60:
            types.append(LegacyType.CHILDREN)

        # Creative works from 5th house strength
        if saptamsha.fifth_lord_position:
            if saptamsha.fifth_lord_position.get("dignity") in ["exalted", "own_sign"]:
                types.append(LegacyType.CREATIVE_WORKS)

        # Teachings from Jupiter
        jupiter = saptamsha.jupiter_position
        if jupiter and jupiter.get("dignity") in ["exalted", "own_sign"]:
            types.append(LegacyType.TEACHINGS)

        # Institutions from Saturn
        if self.d7:
            saturn_data = self.d7.planets.get(Planet.SATURN)
            if saturn_data and is_kendra(saturn_data.house):
                types.append(LegacyType.INSTITUTIONS)

        # Wealth legacy from 2nd/11th houses
        if self.d7:
            second_lord = get_sign_lord(self.d7.houses.get(2, Zodiac.TAURUS))
            second_data = self.d7.planets.get(second_lord)
            if second_data and is_kendra(second_data.house):
                types.append(LegacyType.WEALTH)

        if not types:
            types = [LegacyType.CREATIVE_WORKS]

        return list(set(types))[:4]

    def _determine_peak_periods(
        self, panchamsha: PanchamshaAnalysis, saptamsha: SaptamshaAnalysis
    ) -> List[str]:
        """Determine creative peak periods"""
        periods = []

        # Jupiter periods for creativity
        jupiter_d5 = panchamsha.jupiter_position
        if jupiter_d5 and jupiter_d5.get("dignity") in ["exalted", "own_sign"]:
            periods.append("Jupiter dasha/antardasha - peak creative period")

        # 5th lord periods
        fifth_lord_d5 = panchamsha.fifth_lord_position
        if fifth_lord_d5:
            lord = fifth_lord_d5.get("planet", "")
            if lord:
                periods.append(f"{lord} periods activate creativity")

        # Venus periods for artistic expression
        if self.d5:
            venus_data = self.d5.planets.get(Planet.VENUS)
            if venus_data and venus_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                periods.append("Venus periods enhance artistic expression")

        return periods[:4]

    def _calculate_house_adjustments(
        self, creativity_index: float, progeny_index: float
    ) -> Dict[str, float]:
        """Calculate house score adjustments"""
        adjustments = {}

        # 5th house based on creativity and progeny
        h5_adj = ((creativity_index + progeny_index) / 2 - 50) / 10
        adjustments["house_5"] = round(h5_adj, 2)

        # 9th house (dharma/higher learning) from spiritual creativity
        h9_adj = (creativity_index - 50) / 15
        adjustments["house_9"] = round(h9_adj, 2)

        return adjustments

    def _generate_interpretations(
        self,
        panchamsha: PanchamshaAnalysis,
        saptamsha: SaptamshaAnalysis,
        creativity_index: float
    ) -> tuple[List[str], List[str]]:
        """Generate strength and challenge interpretations"""
        strengths = []
        challenges = []

        if creativity_index > 70:
            strengths.append("Strong creative potential in D5/D7")
        elif creativity_index < 40:
            challenges.append("Creative expression may need cultivation")

        # D5 interpretations
        if panchamsha.creative_indicators:
            strengths.append(panchamsha.creative_indicators[0])

        jupiter = panchamsha.jupiter_position
        if jupiter:
            if jupiter.get("dignity") in ["exalted", "own_sign"]:
                strengths.append("Jupiter strong - natural wisdom and creativity")
            elif jupiter.get("dignity") == "debilitated":
                challenges.append("Jupiter weak - creativity may need conscious effort")

        # D7 interpretations
        if saptamsha.progeny_indicators:
            strengths.append(saptamsha.progeny_indicators[0])
        if saptamsha.legacy_indicators:
            strengths.append(saptamsha.legacy_indicators[0])

        return strengths, challenges

    def _generate_recommendations(
        self,
        panchamsha: PanchamshaAnalysis,
        creative_types: List[CreativeType],
        creativity_index: float
    ) -> List[str]:
        """Generate creative development recommendations"""
        recommendations = []

        if CreativeType.ARTISTIC in creative_types:
            recommendations.append("Pursue visual arts, music, or design")

        if CreativeType.INTELLECTUAL in creative_types:
            recommendations.append("Writing, research, or philosophical study")

        if CreativeType.PERFORMATIVE in creative_types:
            recommendations.append("Theater, public speaking, or entertainment")

        if CreativeType.SPIRITUAL in creative_types:
            recommendations.append("Meditation, spiritual practices enhance creativity")

        if creativity_index < 50:
            recommendations.append("Regular creative practice strengthens expression")

        # Element-based
        if panchamsha.d5_element == "fire":
            recommendations.append("Bold, pioneering creative projects suit you")
        elif panchamsha.d5_element == "water":
            recommendations.append("Intuitive, emotionally-driven creativity flows best")

        return recommendations[:4]

    def _default_panchamsha_analysis(self) -> PanchamshaAnalysis:
        """Return default analysis when D5 not available"""
        return PanchamshaAnalysis(
            d5_ascendant=Zodiac.ARIES,
            d5_element="fire",
            fifth_lord_position={},
            jupiter_position={},
            sun_position={},
            mercury_position={},
            creative_indicators=[],
            spiritual_indicators=[]
        )

    def _default_saptamsha_analysis(self) -> SaptamshaAnalysis:
        """Return default analysis when D7 not available"""
        return SaptamshaAnalysis(
            d7_ascendant=Zodiac.ARIES,
            d7_element="fire",
            fifth_lord_position={},
            jupiter_position={},
            planets_in_fifth=[],
            progeny_indicators=[],
            legacy_indicators=[]
        )
