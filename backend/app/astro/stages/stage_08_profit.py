"""
Stage 8: Profit & Expansion Analysis (D11 Rudramsha + D12 Dwadashamsha)

D11 (Rudramsha/Ekadamsha): Shows gains, fulfillment of desires, networking
D12 (Dwadashamsha): Shows parents, ancestry, past life karmas, and spiritual journey

Output: ProfitAnalysis with indices for gains and karmic patterns
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


class GainType(Enum):
    """Types of gains indicated by D11"""
    FINANCIAL = "financial"         # Monetary gains
    SOCIAL = "social"               # Network, connections
    KNOWLEDGE = "knowledge"         # Learning, wisdom
    RECOGNITION = "recognition"     # Awards, honors
    MATERIAL = "material"           # Physical assets
    SPIRITUAL = "spiritual"         # Inner growth


class KarmicPattern(Enum):
    """Karmic patterns from D12"""
    LEADERSHIP = "leadership"       # Karmic duty to lead
    SERVICE = "service"             # Karmic duty to serve
    TEACHING = "teaching"           # Karmic duty to share knowledge
    HEALING = "healing"             # Karmic duty to heal
    CREATING = "creating"           # Karmic duty to create
    TRANSFORMING = "transforming"   # Karmic duty to transform


@dataclass
class RudramshaAnalysis:
    """D11 Rudramsha/Ekadamsha chart analysis"""
    d11_ascendant: Zodiac
    d11_element: str
    eleventh_lord_position: Dict[str, Any]
    jupiter_position: Dict[str, Any]   # Karaka for gains
    moon_position: Dict[str, Any]      # Karaka for desires
    planets_in_eleventh: List[str]
    gain_indicators: List[str]
    network_indicators: List[str]


@dataclass
class DwadasamshaAnalysis:
    """D12 Dwadashamsha chart analysis"""
    d12_ascendant: Zodiac
    d12_element: str
    ninth_lord_position: Dict[str, Any]   # Father/dharma
    fourth_lord_position: Dict[str, Any]  # Mother
    sun_position: Dict[str, Any]          # Father karaka
    moon_position: Dict[str, Any]         # Mother karaka
    karmic_indicators: List[str]
    ancestral_indicators: List[str]


@dataclass
class Stage8Result:
    """Complete Stage 8 analysis output"""
    rudramsha: RudramshaAnalysis
    dwadasamsha: DwadasamshaAnalysis

    # Core indices
    gains_index: float               # 0-100 overall gains potential
    network_index: float             # 0-100 social/professional network
    desire_fulfillment_index: float  # 0-100 ability to achieve desires
    karmic_balance_index: float      # 0-100 karmic clarity/resolution

    # Derived attributes
    primary_gain_types: List[GainType]
    karmic_patterns: List[KarmicPattern]
    ancestral_strengths: List[str]

    # House score adjustments
    house_score_adjustments: Dict[str, float]

    # Interpretations
    profit_strengths: List[str]
    profit_challenges: List[str]
    karmic_recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rudramsha": {
                "ascendant": self.rudramsha.d11_ascendant.name,
                "element": self.rudramsha.d11_element,
                "eleventh_lord": self.rudramsha.eleventh_lord_position,
                "jupiter": self.rudramsha.jupiter_position,
                "moon": self.rudramsha.moon_position,
                "planets_in_eleventh": self.rudramsha.planets_in_eleventh,
                "gain_indicators": self.rudramsha.gain_indicators,
                "network_indicators": self.rudramsha.network_indicators
            },
            "dwadasamsha": {
                "ascendant": self.dwadasamsha.d12_ascendant.name,
                "element": self.dwadasamsha.d12_element,
                "ninth_lord": self.dwadasamsha.ninth_lord_position,
                "fourth_lord": self.dwadasamsha.fourth_lord_position,
                "sun": self.dwadasamsha.sun_position,
                "moon": self.dwadasamsha.moon_position,
                "karmic_indicators": self.dwadasamsha.karmic_indicators,
                "ancestral_indicators": self.dwadasamsha.ancestral_indicators
            },
            "indices": {
                "gains": round(self.gains_index, 1),
                "network": round(self.network_index, 1),
                "desire_fulfillment": round(self.desire_fulfillment_index, 1),
                "karmic_balance": round(self.karmic_balance_index, 1)
            },
            "gain_types": [g.value for g in self.primary_gain_types],
            "karmic_patterns": [k.value for k in self.karmic_patterns],
            "ancestral_strengths": self.ancestral_strengths,
            "house_adjustments": self.house_score_adjustments,
            "strengths": self.profit_strengths,
            "challenges": self.profit_challenges,
            "karmic_recommendations": self.karmic_recommendations
        }


class Stage08ProfitAnalysis:
    """
    Stage 8: Analyze D11 (Rudramsha) and D12 (Dwadashamsha) for gains and karma.

    Input: digital_twin, D1 basic data
    Output: Stage8Result with profit and karmic indices
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
        self.d11 = parse_varga_chart(digital_twin, "D11")
        self.d12 = parse_varga_chart(digital_twin, "D12")
        self.d1 = parse_varga_chart(digital_twin, "D1")

    def analyze(self) -> Stage8Result:
        """Run complete Stage 8 analysis"""
        rudramsha = self._analyze_rudramsha()
        dwadasamsha = self._analyze_dwadasamsha()

        # Calculate indices
        gains_index = self._calculate_gains_index(rudramsha)
        network_index = self._calculate_network_index(rudramsha)
        desire_index = self._calculate_desire_fulfillment_index(rudramsha)
        karmic_index = self._calculate_karmic_balance_index(dwadasamsha)

        # Determine attributes
        gain_types = self._determine_gain_types(rudramsha)
        karmic_patterns = self._determine_karmic_patterns(dwadasamsha)
        ancestral = self._determine_ancestral_strengths(dwadasamsha)

        # House adjustments
        adjustments = self._calculate_house_adjustments(gains_index, karmic_index)

        # Interpretations
        strengths, challenges = self._generate_interpretations(
            rudramsha, dwadasamsha, gains_index
        )
        recommendations = self._generate_karmic_recommendations(
            dwadasamsha, karmic_patterns
        )

        return Stage8Result(
            rudramsha=rudramsha,
            dwadasamsha=dwadasamsha,
            gains_index=gains_index,
            network_index=network_index,
            desire_fulfillment_index=desire_index,
            karmic_balance_index=karmic_index,
            primary_gain_types=gain_types,
            karmic_patterns=karmic_patterns,
            ancestral_strengths=ancestral,
            house_score_adjustments=adjustments,
            profit_strengths=strengths,
            profit_challenges=challenges,
            karmic_recommendations=recommendations
        )

    def _analyze_rudramsha(self) -> RudramshaAnalysis:
        """Analyze D11 Rudramsha chart"""
        if not self.d11:
            return self._default_rudramsha_analysis()

        d11_asc = self.d11.ascendant_sign
        d11_element = get_element(d11_asc)

        # 11th lord position
        eleventh_sign = self.d11.houses.get(11, Zodiac.AQUARIUS)
        eleventh_lord = get_sign_lord(eleventh_sign)
        eleventh_lord_data = self.d11.planets.get(eleventh_lord)

        eleventh_lord_position = {}
        if eleventh_lord_data:
            dignity = eleventh_lord_data.dignity or get_dignity_in_sign(eleventh_lord, eleventh_lord_data.sign)
            eleventh_lord_position = {
                "planet": eleventh_lord.value,
                "sign": eleventh_lord_data.sign.name,
                "house": eleventh_lord_data.house,
                "dignity": dignity.value if dignity else "neutral"
            }

        # Jupiter position (karaka for gains and expansion)
        jupiter_data = self.d11.planets.get(Planet.JUPITER)
        jupiter_position = {}
        if jupiter_data:
            jup_dignity = jupiter_data.dignity or get_dignity_in_sign(Planet.JUPITER, jupiter_data.sign)
            jupiter_position = {
                "sign": jupiter_data.sign.name,
                "house": jupiter_data.house,
                "dignity": jup_dignity.value if jup_dignity else "neutral"
            }

        # Moon position (karaka for desires)
        moon_data = self.d11.planets.get(Planet.MOON)
        moon_position = {}
        if moon_data:
            moon_dignity = moon_data.dignity or get_dignity_in_sign(Planet.MOON, moon_data.sign)
            moon_position = {
                "sign": moon_data.sign.name,
                "house": moon_data.house,
                "dignity": moon_dignity.value if moon_dignity else "neutral"
            }

        # Planets in 11th house
        planets_in_eleventh = [p.value for p in self.d11.get_planets_in_house(11)]

        # Gain indicators
        gain_indicators = []

        if jupiter_data:
            if is_kendra(jupiter_data.house) or is_trikona(jupiter_data.house):
                gain_indicators.append("Jupiter well-placed - abundant gains potential")
            if jupiter_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                gain_indicators.append("Jupiter dignified - natural expansion and growth")

        if eleventh_lord_data:
            if is_kendra(eleventh_lord_data.house):
                gain_indicators.append("11th lord in kendra - strong gain realization")
            if eleventh_lord_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                gain_indicators.append("11th lord dignified - consistent gains")

        # Benefics in 11th
        benefics_in_11 = [p for p in planets_in_eleventh if p in ["Jupiter", "Venus", "Mercury", "Moon"]]
        if benefics_in_11:
            gain_indicators.append(f"Benefics in 11th ({', '.join(benefics_in_11)}) - auspicious")

        # Network indicators
        network_indicators = []

        # Mercury for networking/communication
        mercury_data = self.d11.planets.get(Planet.MERCURY)
        if mercury_data:
            if is_kendra(mercury_data.house):
                network_indicators.append("Mercury in kendra - strong networking ability")
            if mercury_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                network_indicators.append("Mercury dignified - excellent connections")

        # Venus for social connections
        venus_data = self.d11.planets.get(Planet.VENUS)
        if venus_data:
            if is_kendra(venus_data.house) or is_trikona(venus_data.house):
                network_indicators.append("Venus well-placed - harmonious relationships")

        # Air element for networking
        if d11_element == "air":
            network_indicators.append("Air ascendant - natural networker")

        return RudramshaAnalysis(
            d11_ascendant=d11_asc,
            d11_element=d11_element,
            eleventh_lord_position=eleventh_lord_position,
            jupiter_position=jupiter_position,
            moon_position=moon_position,
            planets_in_eleventh=planets_in_eleventh,
            gain_indicators=gain_indicators,
            network_indicators=network_indicators
        )

    def _analyze_dwadasamsha(self) -> DwadasamshaAnalysis:
        """Analyze D12 Dwadashamsha chart"""
        if not self.d12:
            return self._default_dwadasamsha_analysis()

        d12_asc = self.d12.ascendant_sign
        d12_element = get_element(d12_asc)

        # 9th lord (father/dharma)
        ninth_sign = self.d12.houses.get(9, Zodiac.SAGITTARIUS)
        ninth_lord = get_sign_lord(ninth_sign)
        ninth_lord_data = self.d12.planets.get(ninth_lord)

        ninth_lord_position = {}
        if ninth_lord_data:
            dignity = ninth_lord_data.dignity or get_dignity_in_sign(ninth_lord, ninth_lord_data.sign)
            ninth_lord_position = {
                "planet": ninth_lord.value,
                "sign": ninth_lord_data.sign.name,
                "house": ninth_lord_data.house,
                "dignity": dignity.value if dignity else "neutral"
            }

        # 4th lord (mother)
        fourth_sign = self.d12.houses.get(4, Zodiac.CANCER)
        fourth_lord = get_sign_lord(fourth_sign)
        fourth_lord_data = self.d12.planets.get(fourth_lord)

        fourth_lord_position = {}
        if fourth_lord_data:
            dignity = fourth_lord_data.dignity or get_dignity_in_sign(fourth_lord, fourth_lord_data.sign)
            fourth_lord_position = {
                "planet": fourth_lord.value,
                "sign": fourth_lord_data.sign.name,
                "house": fourth_lord_data.house,
                "dignity": dignity.value if dignity else "neutral"
            }

        # Sun position (father karaka)
        sun_data = self.d12.planets.get(Planet.SUN)
        sun_position = {}
        if sun_data:
            sun_dignity = sun_data.dignity or get_dignity_in_sign(Planet.SUN, sun_data.sign)
            sun_position = {
                "sign": sun_data.sign.name,
                "house": sun_data.house,
                "dignity": sun_dignity.value if sun_dignity else "neutral"
            }

        # Moon position (mother karaka)
        moon_data = self.d12.planets.get(Planet.MOON)
        moon_position = {}
        if moon_data:
            moon_dignity = moon_data.dignity or get_dignity_in_sign(Planet.MOON, moon_data.sign)
            moon_position = {
                "sign": moon_data.sign.name,
                "house": moon_data.house,
                "dignity": moon_dignity.value if moon_dignity else "neutral"
            }

        # Karmic indicators
        karmic_indicators = []

        # Ketu for past life karma
        ketu_data = self.d12.planets.get(Planet.KETU)
        if ketu_data:
            if is_trikona(ketu_data.house):
                karmic_indicators.append("Ketu in trikona - strong past life connection")
            if ketu_data.house == 1:
                karmic_indicators.append("Ketu in 1st - past life identity carried forward")
            if ketu_data.house == 12:
                karmic_indicators.append("Ketu in 12th - spiritual completion karma")

        # Saturn for karmic lessons
        saturn_data = self.d12.planets.get(Planet.SATURN)
        if saturn_data:
            if saturn_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                karmic_indicators.append("Saturn dignified - karmic duties well-understood")
            if is_kendra(saturn_data.house):
                karmic_indicators.append("Saturn in kendra - structured karmic work")

        # Ancestral indicators
        ancestral_indicators = []

        # Sun for paternal lineage
        if sun_data:
            if sun_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                ancestral_indicators.append("Sun strong - strong paternal blessings")
            if is_dusthana(sun_data.house):
                ancestral_indicators.append("Sun in dusthana - paternal karmic debts")

        # Moon for maternal lineage
        if moon_data:
            if moon_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                ancestral_indicators.append("Moon strong - strong maternal blessings")
            if is_dusthana(moon_data.house):
                ancestral_indicators.append("Moon in dusthana - maternal karmic debts")

        # Jupiter for ancestors' blessings
        jupiter_data = self.d12.planets.get(Planet.JUPITER)
        if jupiter_data and jupiter_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
            ancestral_indicators.append("Jupiter dignified - ancestral blessings active")

        return DwadasamshaAnalysis(
            d12_ascendant=d12_asc,
            d12_element=d12_element,
            ninth_lord_position=ninth_lord_position,
            fourth_lord_position=fourth_lord_position,
            sun_position=sun_position,
            moon_position=moon_position,
            karmic_indicators=karmic_indicators,
            ancestral_indicators=ancestral_indicators
        )

    def _calculate_gains_index(self, rudramsha: RudramshaAnalysis) -> float:
        """Calculate overall gains potential"""
        score = 50.0

        # Jupiter is primary factor
        jupiter = rudramsha.jupiter_position
        if jupiter:
            dignity = jupiter.get("dignity", "neutral")
            if dignity == "exalted":
                score += 25
            elif dignity == "own_sign":
                score += 20
            elif dignity == "debilitated":
                score -= 12

            if is_kendra(jupiter.get("house", 6)):
                score += 10
            elif is_trikona(jupiter.get("house", 6)):
                score += 8

        # 11th lord position
        eleventh = rudramsha.eleventh_lord_position
        if eleventh:
            dignity = eleventh.get("dignity", "neutral")
            if dignity in ["exalted", "own_sign"]:
                score += 12
            if is_kendra(eleventh.get("house", 6)):
                score += 8

        # Gain indicators bonus
        score += len(rudramsha.gain_indicators) * 4

        return max(0, min(100, score))

    def _calculate_network_index(self, rudramsha: RudramshaAnalysis) -> float:
        """Calculate networking/social ability index"""
        score = 50.0

        # Network indicators
        score += len(rudramsha.network_indicators) * 8

        # Air element boosts networking
        if rudramsha.d11_element == "air":
            score += 12

        # Planets in 11th add connections
        score += len(rudramsha.planets_in_eleventh) * 5

        # Moon for emotional connections
        moon = rudramsha.moon_position
        if moon:
            dignity = moon.get("dignity", "neutral")
            if dignity in ["exalted", "own_sign"]:
                score += 10

        return max(0, min(100, score))

    def _calculate_desire_fulfillment_index(self, rudramsha: RudramshaAnalysis) -> float:
        """Calculate desire fulfillment potential"""
        score = 50.0

        # Moon is karaka for desires
        moon = rudramsha.moon_position
        if moon:
            dignity = moon.get("dignity", "neutral")
            if dignity == "exalted":
                score += 20
            elif dignity == "own_sign":
                score += 15
            elif dignity == "debilitated":
                score -= 10

            if is_kendra(moon.get("house", 6)):
                score += 10

        # Jupiter for fulfillment
        jupiter = rudramsha.jupiter_position
        if jupiter:
            dignity = jupiter.get("dignity", "neutral")
            if dignity in ["exalted", "own_sign"]:
                score += 12

        # 11th house strength
        score += len(rudramsha.planets_in_eleventh) * 4

        return max(0, min(100, score))

    def _calculate_karmic_balance_index(self, dwadasamsha: DwadasamshaAnalysis) -> float:
        """Calculate karmic balance/clarity index"""
        score = 50.0

        # Karmic indicators
        positive_karma = [k for k in dwadasamsha.karmic_indicators if "debt" not in k.lower()]
        negative_karma = [k for k in dwadasamsha.karmic_indicators if "debt" in k.lower()]

        score += len(positive_karma) * 8
        score -= len(negative_karma) * 5

        # Ancestral blessings
        blessings = [a for a in dwadasamsha.ancestral_indicators if "blessing" in a.lower()]
        debts = [a for a in dwadasamsha.ancestral_indicators if "debt" in a.lower()]

        score += len(blessings) * 6
        score -= len(debts) * 4

        # Sun and Moon strength
        sun = dwadasamsha.sun_position
        if sun and sun.get("dignity") in ["exalted", "own_sign"]:
            score += 8

        moon = dwadasamsha.moon_position
        if moon and moon.get("dignity") in ["exalted", "own_sign"]:
            score += 8

        return max(0, min(100, score))

    def _determine_gain_types(self, rudramsha: RudramshaAnalysis) -> List[GainType]:
        """Determine primary types of gains"""
        types = []

        # Jupiter for financial/material
        jupiter = rudramsha.jupiter_position
        if jupiter and jupiter.get("dignity") in ["exalted", "own_sign"]:
            types.append(GainType.FINANCIAL)

        # Mercury for knowledge/networking
        if self.d11:
            mercury_data = self.d11.planets.get(Planet.MERCURY)
            if mercury_data and mercury_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                types.append(GainType.KNOWLEDGE)

        # Network indicators = social gains
        if rudramsha.network_indicators:
            types.append(GainType.SOCIAL)

        # Sun for recognition
        if self.d11:
            sun_data = self.d11.planets.get(Planet.SUN)
            if sun_data and is_kendra(sun_data.house):
                types.append(GainType.RECOGNITION)

        # Ketu for spiritual gains
        if self.d11:
            ketu_data = self.d11.planets.get(Planet.KETU)
            if ketu_data and is_trikona(ketu_data.house):
                types.append(GainType.SPIRITUAL)

        # Default
        if not types:
            types = [GainType.MATERIAL]

        return list(set(types))[:4]

    def _determine_karmic_patterns(self, dwadasamsha: DwadasamshaAnalysis) -> List[KarmicPattern]:
        """Determine karmic duty patterns"""
        patterns = []

        # Sun for leadership karma
        sun = dwadasamsha.sun_position
        if sun and sun.get("dignity") in ["exalted", "own_sign"]:
            patterns.append(KarmicPattern.LEADERSHIP)

        # Moon for nurturing/service
        moon = dwadasamsha.moon_position
        if moon and moon.get("dignity") in ["exalted", "own_sign"]:
            patterns.append(KarmicPattern.SERVICE)

        # Jupiter for teaching
        if self.d12:
            jupiter_data = self.d12.planets.get(Planet.JUPITER)
            if jupiter_data and jupiter_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                patterns.append(KarmicPattern.TEACHING)

        # Ketu for healing/transformation
        if self.d12:
            ketu_data = self.d12.planets.get(Planet.KETU)
            if ketu_data:
                if is_trikona(ketu_data.house):
                    patterns.append(KarmicPattern.HEALING)
                if ketu_data.house == 8:
                    patterns.append(KarmicPattern.TRANSFORMING)

        # Venus for creating
        if self.d12:
            venus_data = self.d12.planets.get(Planet.VENUS)
            if venus_data and venus_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                patterns.append(KarmicPattern.CREATING)

        if not patterns:
            patterns = [KarmicPattern.SERVICE]

        return list(set(patterns))[:4]

    def _determine_ancestral_strengths(self, dwadasamsha: DwadasamshaAnalysis) -> List[str]:
        """Determine ancestral strengths and blessings"""
        strengths = []

        # Filter for positive indicators
        for indicator in dwadasamsha.ancestral_indicators:
            if "blessing" in indicator.lower() or "strong" in indicator.lower():
                strengths.append(indicator)

        # Add from karmic indicators
        for indicator in dwadasamsha.karmic_indicators:
            if "well" in indicator.lower() or "dignified" in indicator.lower():
                strengths.append(indicator)

        return strengths[:4]

    def _calculate_house_adjustments(
        self, gains_index: float, karmic_index: float
    ) -> Dict[str, float]:
        """Calculate house score adjustments"""
        adjustments = {}

        # 11th house based on gains
        h11_adj = (gains_index - 50) / 10
        adjustments["house_11"] = round(h11_adj, 2)

        # 12th house based on karmic balance
        h12_adj = (karmic_index - 50) / 12
        adjustments["house_12"] = round(h12_adj, 2)

        # 9th house (dharma) from karmic patterns
        h9_adj = (karmic_index - 50) / 15
        adjustments["house_9"] = round(h9_adj, 2)

        return adjustments

    def _generate_interpretations(
        self,
        rudramsha: RudramshaAnalysis,
        dwadasamsha: DwadasamshaAnalysis,
        gains_index: float
    ) -> tuple[List[str], List[str]]:
        """Generate strength and challenge interpretations"""
        strengths = []
        challenges = []

        if gains_index > 70:
            strengths.append("Strong D11 indicates excellent gains potential")
        elif gains_index < 40:
            challenges.append("Gains may require persistent effort")

        # D11 interpretations
        if rudramsha.gain_indicators:
            strengths.append(rudramsha.gain_indicators[0])

        jupiter = rudramsha.jupiter_position
        if jupiter:
            if jupiter.get("dignity") in ["exalted", "own_sign"]:
                strengths.append("Jupiter strong - natural abundance and expansion")
            elif jupiter.get("dignity") == "debilitated":
                challenges.append("Jupiter weak - growth may need nurturing")

        # D12 interpretations
        if dwadasamsha.karmic_indicators:
            for ind in dwadasamsha.karmic_indicators:
                if "debt" not in ind.lower():
                    strengths.append(ind)
                    break

        if dwadasamsha.ancestral_indicators:
            strengths.append(dwadasamsha.ancestral_indicators[0])

        return strengths, challenges

    def _generate_karmic_recommendations(
        self,
        dwadasamsha: DwadasamshaAnalysis,
        patterns: List[KarmicPattern]
    ) -> List[str]:
        """Generate karmic recommendations"""
        recommendations = []

        pattern_recs = {
            KarmicPattern.LEADERSHIP: "Embrace leadership roles with responsibility",
            KarmicPattern.SERVICE: "Service to others fulfills karmic purpose",
            KarmicPattern.TEACHING: "Sharing knowledge is your dharmic duty",
            KarmicPattern.HEALING: "Healing work aligns with soul purpose",
            KarmicPattern.CREATING: "Creative expression balances karma",
            KarmicPattern.TRANSFORMING: "Embrace transformation and help others transform"
        }

        for pattern in patterns:
            if pattern in pattern_recs:
                recommendations.append(pattern_recs[pattern])

        # Add ancestral recommendations
        debts = [a for a in dwadasamsha.ancestral_indicators if "debt" in a.lower()]
        if debts:
            recommendations.append("Honor ancestors through prayers and remembrance")

        blessings = [a for a in dwadasamsha.ancestral_indicators if "blessing" in a.lower()]
        if blessings:
            recommendations.append("Ancestral blessings support your journey")

        return recommendations[:4]

    def _default_rudramsha_analysis(self) -> RudramshaAnalysis:
        """Return default analysis when D11 not available"""
        return RudramshaAnalysis(
            d11_ascendant=Zodiac.ARIES,
            d11_element="fire",
            eleventh_lord_position={},
            jupiter_position={},
            moon_position={},
            planets_in_eleventh=[],
            gain_indicators=[],
            network_indicators=[]
        )

    def _default_dwadasamsha_analysis(self) -> DwadasamshaAnalysis:
        """Return default analysis when D12 not available"""
        return DwadasamshaAnalysis(
            d12_ascendant=Zodiac.ARIES,
            d12_element="fire",
            ninth_lord_position={},
            fourth_lord_position={},
            sun_position={},
            moon_position={},
            karmic_indicators=[],
            ancestral_indicators=[]
        )
