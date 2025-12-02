"""
Stage 4: Wealth & Assets Analysis (D2 Hora + D4 Chaturthamsha)

D2 (Hora): Indicates wealth potential and accumulation ability
D4 (Chaturthamsha): Shows property, vehicles, fixed assets, fortune

Output: WealthAnalysis with indices for financial potential
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .varga_utils import (
    parse_varga_chart, VargaChartData, VargaPlanetData,
    get_sign_lord, is_benefic, is_malefic, get_dignity_in_sign,
    is_kendra, is_trikona, is_dusthana
)
from ..models.types import Planet, Zodiac, Dignity


class WealthType(Enum):
    """Types of wealth indicated by chart"""
    EARNED = "earned"              # Through personal effort
    INHERITED = "inherited"        # From family/legacy
    SPECULATIVE = "speculative"    # Through risk-taking
    PASSIVE = "passive"            # Investments, rentals
    PROFESSIONAL = "professional"  # From career
    CREATIVE = "creative"          # From artistic work


class AssetType(Enum):
    """Types of assets indicated by D4"""
    REAL_ESTATE = "real_estate"
    VEHICLES = "vehicles"
    LAND = "land"
    LUXURY_ITEMS = "luxury_items"
    INVESTMENTS = "investments"


@dataclass
class HoraAnalysis:
    """D2 Hora chart analysis"""
    hora_ascendant: Zodiac
    sun_hora: str          # "Sun" or "Moon" hora
    moon_hora: str
    benefics_in_sun_hora: List[str]
    benefics_in_moon_hora: List[str]
    malefics_in_sun_hora: List[str]
    malefics_in_moon_hora: List[str]
    wealth_planet_strength: Dict[str, float]  # Jupiter, Venus strength
    accumulation_potential: float  # 0-100 score


@dataclass
class ChaturthamshaAnalysis:
    """D4 Chaturthamsha chart analysis"""
    d4_ascendant: Zodiac
    fourth_lord_position: Dict[str, Any]
    venus_position: Dict[str, Any]
    property_indicators: List[str]
    vehicle_indicators: List[str]
    asset_potential: float  # 0-100 score
    recommended_assets: List[AssetType]


@dataclass
class Stage4Result:
    """Complete Stage 4 analysis output"""
    hora: HoraAnalysis
    chaturthamsha: ChaturthamshaAnalysis

    # Combined indices
    wealth_accumulation_index: float      # 0-100
    fixed_assets_index: float             # 0-100
    financial_stability_index: float      # 0-100

    # Wealth types
    primary_wealth_types: List[WealthType]

    # House score adjustments for 2nd and 4th houses
    house_score_adjustments: Dict[str, float]

    # Interpretations
    wealth_strengths: List[str]
    wealth_challenges: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hora": {
                "ascendant": self.hora.hora_ascendant.name,
                "sun_hora": self.hora.sun_hora,
                "moon_hora": self.hora.moon_hora,
                "benefics_sun_hora": self.hora.benefics_in_sun_hora,
                "benefics_moon_hora": self.hora.benefics_in_moon_hora,
                "wealth_planet_strength": self.hora.wealth_planet_strength,
                "accumulation_potential": round(self.hora.accumulation_potential, 1)
            },
            "chaturthamsha": {
                "ascendant": self.chaturthamsha.d4_ascendant.name,
                "fourth_lord": self.chaturthamsha.fourth_lord_position,
                "venus": self.chaturthamsha.venus_position,
                "property_indicators": self.chaturthamsha.property_indicators,
                "vehicle_indicators": self.chaturthamsha.vehicle_indicators,
                "asset_potential": round(self.chaturthamsha.asset_potential, 1),
                "recommended_assets": [a.value for a in self.chaturthamsha.recommended_assets]
            },
            "indices": {
                "wealth_accumulation": round(self.wealth_accumulation_index, 1),
                "fixed_assets": round(self.fixed_assets_index, 1),
                "financial_stability": round(self.financial_stability_index, 1)
            },
            "wealth_types": [w.value for w in self.primary_wealth_types],
            "house_adjustments": self.house_score_adjustments,
            "strengths": self.wealth_strengths,
            "challenges": self.wealth_challenges
        }


class Stage04WealthAnalysis:
    """
    Stage 4: Analyze D2 (Hora) and D4 (Chaturthamsha) for wealth potential.

    Input: digital_twin, D1 basic data
    Output: Stage4Result with wealth indices
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

        # Parse varga charts
        self.d2 = parse_varga_chart(digital_twin, "D2")
        self.d4 = parse_varga_chart(digital_twin, "D4")
        self.d1 = parse_varga_chart(digital_twin, "D1")

    def analyze(self) -> Stage4Result:
        """Run complete Stage 4 analysis"""
        hora = self._analyze_hora()
        chaturthamsha = self._analyze_chaturthamsha()

        # Calculate combined indices
        wealth_index = self._calculate_wealth_accumulation_index(hora, chaturthamsha)
        assets_index = self._calculate_fixed_assets_index(chaturthamsha)
        stability_index = self._calculate_financial_stability_index(hora, chaturthamsha)

        # Determine wealth types
        wealth_types = self._determine_wealth_types(hora, chaturthamsha)

        # Calculate house adjustments
        adjustments = self._calculate_house_adjustments(hora, chaturthamsha)

        # Generate interpretations
        strengths, challenges = self._generate_interpretations(hora, chaturthamsha)

        return Stage4Result(
            hora=hora,
            chaturthamsha=chaturthamsha,
            wealth_accumulation_index=wealth_index,
            fixed_assets_index=assets_index,
            financial_stability_index=stability_index,
            primary_wealth_types=wealth_types,
            house_score_adjustments=adjustments,
            wealth_strengths=strengths,
            wealth_challenges=challenges
        )

    def _analyze_hora(self) -> HoraAnalysis:
        """Analyze D2 Hora chart for wealth indicators"""
        if not self.d2:
            return self._default_hora_analysis()

        hora_asc = self.d2.ascendant_sign

        # In Hora, odd signs = Sun hora, even signs = Moon hora
        benefics_sun = []
        benefics_moon = []
        malefics_sun = []
        malefics_moon = []

        for planet, data in self.d2.planets.items():
            hora_type = "Sun" if data.sign.value % 2 == 1 else "Moon"

            if is_benefic(planet):
                if hora_type == "Sun":
                    benefics_sun.append(planet.value)
                else:
                    benefics_moon.append(planet.value)
            elif is_malefic(planet):
                if hora_type == "Sun":
                    malefics_sun.append(planet.value)
                else:
                    malefics_moon.append(planet.value)

        # Calculate wealth planet strength
        jupiter_data = self.d2.planets.get(Planet.JUPITER)
        venus_data = self.d2.planets.get(Planet.VENUS)

        wealth_strength = {}

        if jupiter_data:
            jup_score = 50.0
            if jupiter_data.dignity == Dignity.EXALTED:
                jup_score = 90
            elif jupiter_data.dignity == Dignity.OWN_SIGN:
                jup_score = 80
            elif jupiter_data.dignity == Dignity.DEBILITATED:
                jup_score = 30
            elif is_kendra(jupiter_data.house) or is_trikona(jupiter_data.house):
                jup_score = 70
            wealth_strength["Jupiter"] = jup_score

        if venus_data:
            ven_score = 50.0
            if venus_data.dignity == Dignity.EXALTED:
                ven_score = 90
            elif venus_data.dignity == Dignity.OWN_SIGN:
                ven_score = 80
            elif venus_data.dignity == Dignity.DEBILITATED:
                ven_score = 30
            elif is_kendra(venus_data.house) or is_trikona(venus_data.house):
                ven_score = 70
            wealth_strength["Venus"] = ven_score

        # Calculate accumulation potential
        accumulation = 50.0

        # More benefics = better accumulation
        accumulation += len(benefics_sun) * 5 + len(benefics_moon) * 5
        accumulation -= len(malefics_sun) * 3 + len(malefics_moon) * 3

        # Jupiter and Venus strength matters
        if wealth_strength.get("Jupiter", 50) > 70:
            accumulation += 10
        if wealth_strength.get("Venus", 50) > 70:
            accumulation += 10

        accumulation = max(0, min(100, accumulation))

        # Determine hora types for Sun and Moon
        sun_data = self.d2.planets.get(Planet.SUN)
        moon_data = self.d2.planets.get(Planet.MOON)

        sun_hora = "Sun" if sun_data and sun_data.sign.value % 2 == 1 else "Moon"
        moon_hora = "Moon" if moon_data and moon_data.sign.value % 2 == 0 else "Sun"

        return HoraAnalysis(
            hora_ascendant=hora_asc,
            sun_hora=sun_hora,
            moon_hora=moon_hora,
            benefics_in_sun_hora=benefics_sun,
            benefics_in_moon_hora=benefics_moon,
            malefics_in_sun_hora=malefics_sun,
            malefics_in_moon_hora=malefics_moon,
            wealth_planet_strength=wealth_strength,
            accumulation_potential=accumulation
        )

    def _analyze_chaturthamsha(self) -> ChaturthamshaAnalysis:
        """Analyze D4 Chaturthamsha for fixed assets"""
        if not self.d4:
            return self._default_chaturthamsha_analysis()

        d4_asc = self.d4.ascendant_sign

        # Fourth lord analysis
        fourth_sign = self.d4.houses.get(4, Zodiac.CANCER)
        fourth_lord = get_sign_lord(fourth_sign)
        fourth_lord_data = self.d4.planets.get(fourth_lord)

        fourth_lord_position = {
            "planet": fourth_lord.value,
            "sign": fourth_lord_data.sign.name if fourth_lord_data else "Unknown",
            "house": fourth_lord_data.house if fourth_lord_data else 0
        }

        # Venus analysis (karaka for vehicles and luxury)
        venus_data = self.d4.planets.get(Planet.VENUS)
        venus_position = {
            "sign": venus_data.sign.name if venus_data else "Unknown",
            "house": venus_data.house if venus_data else 0,
            "dignity": venus_data.dignity.value if venus_data and venus_data.dignity else "neutral"
        }

        # Property indicators
        property_indicators = []
        if fourth_lord_data:
            if is_kendra(fourth_lord_data.house):
                property_indicators.append("4th lord in kendra - strong property potential")
            if fourth_lord_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                property_indicators.append("4th lord well-dignified - quality properties")

        # Check 4th house occupants
        planets_in_4th = self.d4.get_planets_in_house(4)
        if Planet.JUPITER in planets_in_4th:
            property_indicators.append("Jupiter in 4th - expansive property holdings")
        if Planet.VENUS in planets_in_4th:
            property_indicators.append("Venus in 4th - luxurious properties")
        if Planet.SATURN in planets_in_4th:
            property_indicators.append("Saturn in 4th - older/inherited properties")

        # Vehicle indicators
        vehicle_indicators = []
        if venus_data:
            if is_kendra(venus_data.house) or is_trikona(venus_data.house):
                vehicle_indicators.append("Venus well-placed - quality vehicles")
            if venus_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                vehicle_indicators.append("Strong Venus - luxury vehicles")

        # Mars for vehicles
        mars_data = self.d4.planets.get(Planet.MARS)
        if mars_data and is_kendra(mars_data.house):
            vehicle_indicators.append("Mars in kendra - powerful/sporty vehicles")

        # Calculate asset potential
        asset_potential = 50.0

        if fourth_lord_data:
            if is_kendra(fourth_lord_data.house):
                asset_potential += 15
            if fourth_lord_data.dignity == Dignity.EXALTED:
                asset_potential += 20
            elif fourth_lord_data.dignity == Dignity.OWN_SIGN:
                asset_potential += 15
            elif fourth_lord_data.dignity == Dignity.DEBILITATED:
                asset_potential -= 15

        if venus_data:
            if is_kendra(venus_data.house) or is_trikona(venus_data.house):
                asset_potential += 10

        asset_potential = max(0, min(100, asset_potential))

        # Recommended asset types based on chart
        recommended = []
        if property_indicators:
            recommended.append(AssetType.REAL_ESTATE)
        if vehicle_indicators:
            recommended.append(AssetType.VEHICLES)
        if Planet.SATURN in planets_in_4th or (fourth_lord == Planet.SATURN):
            recommended.append(AssetType.LAND)
        if venus_data and venus_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
            recommended.append(AssetType.LUXURY_ITEMS)

        if not recommended:
            recommended = [AssetType.INVESTMENTS]

        return ChaturthamshaAnalysis(
            d4_ascendant=d4_asc,
            fourth_lord_position=fourth_lord_position,
            venus_position=venus_position,
            property_indicators=property_indicators,
            vehicle_indicators=vehicle_indicators,
            asset_potential=asset_potential,
            recommended_assets=recommended
        )

    def _calculate_wealth_accumulation_index(
        self, hora: HoraAnalysis, chaturthamsha: ChaturthamshaAnalysis
    ) -> float:
        """Calculate overall wealth accumulation potential"""
        # D2 weight: 60%, D4 weight: 40%
        d2_score = hora.accumulation_potential
        d4_score = chaturthamsha.asset_potential

        combined = (d2_score * 0.6) + (d4_score * 0.4)

        # Adjust based on 2nd house lord in D1
        second_lord_info = self.house_lords.get(2, {})
        second_lord_house = second_lord_info.get("in_house", 0)

        if second_lord_house in [1, 2, 5, 9, 11]:  # Favorable houses
            combined += 5
        elif second_lord_house in [6, 8, 12]:  # Challenging houses
            combined -= 5

        return max(0, min(100, combined))

    def _calculate_fixed_assets_index(self, chaturthamsha: ChaturthamshaAnalysis) -> float:
        """Calculate fixed assets potential from D4"""
        base = chaturthamsha.asset_potential

        # Adjust based on property and vehicle indicators
        base += len(chaturthamsha.property_indicators) * 5
        base += len(chaturthamsha.vehicle_indicators) * 3

        return max(0, min(100, base))

    def _calculate_financial_stability_index(
        self, hora: HoraAnalysis, chaturthamsha: ChaturthamshaAnalysis
    ) -> float:
        """Calculate financial stability index"""
        # Stability comes from both accumulation ability and fixed assets
        stability = (hora.accumulation_potential + chaturthamsha.asset_potential) / 2

        # Jupiter strength adds stability
        jup_strength = hora.wealth_planet_strength.get("Jupiter", 50)
        if jup_strength > 70:
            stability += 10

        # More malefics reduce stability
        malefic_count = len(hora.malefics_in_sun_hora) + len(hora.malefics_in_moon_hora)
        stability -= malefic_count * 2

        return max(0, min(100, stability))

    def _determine_wealth_types(
        self, hora: HoraAnalysis, chaturthamsha: ChaturthamshaAnalysis
    ) -> List[WealthType]:
        """Determine primary wealth types from chart"""
        types = []

        # Check for earned wealth (Sun hora strength)
        if len(hora.benefics_in_sun_hora) >= 2:
            types.append(WealthType.EARNED)

        # Check for passive/investment wealth (Moon hora)
        if len(hora.benefics_in_moon_hora) >= 2:
            types.append(WealthType.PASSIVE)

        # Check for inherited wealth (4th house indicators)
        if any("inherited" in ind.lower() for ind in chaturthamsha.property_indicators):
            types.append(WealthType.INHERITED)

        # Venus strength indicates creative wealth
        venus_strength = hora.wealth_planet_strength.get("Venus", 50)
        if venus_strength > 70:
            types.append(WealthType.CREATIVE)

        # Jupiter strength indicates professional wealth
        jupiter_strength = hora.wealth_planet_strength.get("Jupiter", 50)
        if jupiter_strength > 70:
            types.append(WealthType.PROFESSIONAL)

        if not types:
            types = [WealthType.EARNED]

        return types[:3]  # Return top 3

    def _calculate_house_adjustments(
        self, hora: HoraAnalysis, chaturthamsha: ChaturthamshaAnalysis
    ) -> Dict[str, float]:
        """Calculate house score adjustments based on wealth analysis"""
        adjustments = {}

        # 2nd house (wealth) adjustment based on D2
        h2_adj = (hora.accumulation_potential - 50) / 10
        adjustments["house_2"] = round(h2_adj, 2)

        # 4th house (property) adjustment based on D4
        h4_adj = (chaturthamsha.asset_potential - 50) / 10
        adjustments["house_4"] = round(h4_adj, 2)

        # 11th house (gains) adjustment
        combined_score = (hora.accumulation_potential + chaturthamsha.asset_potential) / 2
        h11_adj = (combined_score - 50) / 15
        adjustments["house_11"] = round(h11_adj, 2)

        return adjustments

    def _generate_interpretations(
        self, hora: HoraAnalysis, chaturthamsha: ChaturthamshaAnalysis
    ) -> tuple[List[str], List[str]]:
        """Generate strength and challenge interpretations"""
        strengths = []
        challenges = []

        # Hora interpretations
        if hora.accumulation_potential > 70:
            strengths.append("Strong wealth accumulation potential in D2")
        elif hora.accumulation_potential < 40:
            challenges.append("Wealth accumulation requires extra effort")

        jup = hora.wealth_planet_strength.get("Jupiter", 50)
        ven = hora.wealth_planet_strength.get("Venus", 50)

        if jup > 70:
            strengths.append("Jupiter strong in D2 - natural abundance")
        if ven > 70:
            strengths.append("Venus strong in D2 - luxury and comfort")

        if jup < 40:
            challenges.append("Jupiter weak in D2 - growth may be slow")
        if ven < 40:
            challenges.append("Venus weak in D2 - material comforts delayed")

        # Chaturthamsha interpretations
        if chaturthamsha.asset_potential > 70:
            strengths.append("Excellent fixed asset potential in D4")
        elif chaturthamsha.asset_potential < 40:
            challenges.append("Fixed asset accumulation challenging")

        if chaturthamsha.property_indicators:
            strengths.append(f"Property potential: {chaturthamsha.property_indicators[0]}")

        if chaturthamsha.vehicle_indicators:
            strengths.append(f"Vehicle potential: {chaturthamsha.vehicle_indicators[0]}")

        return strengths, challenges

    def _default_hora_analysis(self) -> HoraAnalysis:
        """Return default analysis when D2 not available"""
        return HoraAnalysis(
            hora_ascendant=Zodiac.ARIES,
            sun_hora="Unknown",
            moon_hora="Unknown",
            benefics_in_sun_hora=[],
            benefics_in_moon_hora=[],
            malefics_in_sun_hora=[],
            malefics_in_moon_hora=[],
            wealth_planet_strength={},
            accumulation_potential=50.0
        )

    def _default_chaturthamsha_analysis(self) -> ChaturthamshaAnalysis:
        """Return default analysis when D4 not available"""
        return ChaturthamshaAnalysis(
            d4_ascendant=Zodiac.ARIES,
            fourth_lord_position={},
            venus_position={},
            property_indicators=[],
            vehicle_indicators=[],
            asset_potential=50.0,
            recommended_assets=[AssetType.INVESTMENTS]
        )
