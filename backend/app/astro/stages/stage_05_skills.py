"""
Stage 5: Skills & Initiative Analysis (D3 Drekkana)

D3 (Drekkana): Shows courage, initiative, siblings, communication skills,
               hands-on abilities, and short journeys.

Output: SkillsAnalysis with initiative and communication indices
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


class SkillType(Enum):
    """Types of skills indicated by D3"""
    COMMUNICATION = "communication"     # Writing, speaking, media
    TECHNICAL = "technical"             # Hands-on, engineering
    ARTISTIC = "artistic"               # Creative expression
    ANALYTICAL = "analytical"           # Research, analysis
    PHYSICAL = "physical"               # Sports, martial arts
    ENTREPRENEURIAL = "entrepreneurial" # Business initiative
    TEACHING = "teaching"               # Education, mentoring


class InitiativeStyle(Enum):
    """How person takes initiative"""
    BOLD = "bold"               # Direct, immediate action
    STRATEGIC = "strategic"     # Planned, calculated
    COLLABORATIVE = "collaborative"  # Team-oriented
    CAUTIOUS = "cautious"       # Risk-averse, careful
    OPPORTUNISTIC = "opportunistic"  # Waits for right moment


@dataclass
class DrekkanaAnalysis:
    """D3 Drekkana chart analysis"""
    d3_ascendant: Zodiac
    d3_ascendant_element: str
    mars_position: Dict[str, Any]     # Mars is karaka for courage
    mercury_position: Dict[str, Any]  # Mercury for communication
    third_lord_position: Dict[str, Any]
    planets_in_third: List[str]
    courage_indicators: List[str]
    skill_indicators: List[str]
    sibling_indicators: List[str]


@dataclass
class Stage5Result:
    """Complete Stage 5 analysis output"""
    drekkana: DrekkanaAnalysis

    # Core indices
    initiative_index: float         # 0-100 courage/action taking
    communication_index: float      # 0-100 communication ability
    skill_diversity_index: float    # 0-100 range of abilities

    # Derived attributes
    primary_skills: List[SkillType]
    initiative_style: InitiativeStyle
    risk_tolerance: str  # "high", "moderate", "low"

    # House score adjustments
    house_score_adjustments: Dict[str, float]

    # Interpretations
    strengths: List[str]
    challenges: List[str]
    recommended_skill_development: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "drekkana": {
                "ascendant": self.drekkana.d3_ascendant.name,
                "ascendant_element": self.drekkana.d3_ascendant_element,
                "mars": self.drekkana.mars_position,
                "mercury": self.drekkana.mercury_position,
                "third_lord": self.drekkana.third_lord_position,
                "planets_in_third": self.drekkana.planets_in_third,
                "courage_indicators": self.drekkana.courage_indicators,
                "skill_indicators": self.drekkana.skill_indicators,
                "sibling_indicators": self.drekkana.sibling_indicators
            },
            "indices": {
                "initiative": round(self.initiative_index, 1),
                "communication": round(self.communication_index, 1),
                "skill_diversity": round(self.skill_diversity_index, 1)
            },
            "primary_skills": [s.value for s in self.primary_skills],
            "initiative_style": self.initiative_style.value,
            "risk_tolerance": self.risk_tolerance,
            "house_adjustments": self.house_score_adjustments,
            "strengths": self.strengths,
            "challenges": self.challenges,
            "skill_development": self.recommended_skill_development
        }


class Stage05SkillsAnalysis:
    """
    Stage 5: Analyze D3 (Drekkana) for skills and initiative.

    Input: digital_twin, D1 basic data
    Output: Stage5Result with skill indices
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

        # Parse D3 chart
        self.d3 = parse_varga_chart(digital_twin, "D3")
        self.d1 = parse_varga_chart(digital_twin, "D1")

    def analyze(self) -> Stage5Result:
        """Run complete Stage 5 analysis"""
        drekkana = self._analyze_drekkana()

        # Calculate indices
        initiative_index = self._calculate_initiative_index(drekkana)
        communication_index = self._calculate_communication_index(drekkana)
        skill_diversity = self._calculate_skill_diversity_index(drekkana)

        # Determine attributes
        primary_skills = self._determine_primary_skills(drekkana)
        initiative_style = self._determine_initiative_style(drekkana)
        risk_tolerance = self._determine_risk_tolerance(drekkana, initiative_index)

        # House adjustments
        adjustments = self._calculate_house_adjustments(drekkana, initiative_index, communication_index)

        # Interpretations
        strengths, challenges = self._generate_interpretations(drekkana, initiative_index, communication_index)
        recommendations = self._generate_skill_recommendations(drekkana, primary_skills)

        return Stage5Result(
            drekkana=drekkana,
            initiative_index=initiative_index,
            communication_index=communication_index,
            skill_diversity_index=skill_diversity,
            primary_skills=primary_skills,
            initiative_style=initiative_style,
            risk_tolerance=risk_tolerance,
            house_score_adjustments=adjustments,
            strengths=strengths,
            challenges=challenges,
            recommended_skill_development=recommendations
        )

    def _analyze_drekkana(self) -> DrekkanaAnalysis:
        """Analyze D3 Drekkana chart"""
        if not self.d3:
            return self._default_drekkana_analysis()

        d3_asc = self.d3.ascendant_sign
        d3_element = get_element(d3_asc)

        # Mars position (karaka for courage)
        mars_data = self.d3.planets.get(Planet.MARS)
        mars_position = {}
        if mars_data:
            mars_dignity = mars_data.dignity or get_dignity_in_sign(Planet.MARS, mars_data.sign)
            mars_position = {
                "sign": mars_data.sign.name,
                "house": mars_data.house,
                "dignity": mars_dignity.value if mars_dignity else "neutral",
                "is_retrograde": mars_data.is_retrograde
            }

        # Mercury position (karaka for communication)
        mercury_data = self.d3.planets.get(Planet.MERCURY)
        mercury_position = {}
        if mercury_data:
            merc_dignity = mercury_data.dignity or get_dignity_in_sign(Planet.MERCURY, mercury_data.sign)
            mercury_position = {
                "sign": mercury_data.sign.name,
                "house": mercury_data.house,
                "dignity": merc_dignity.value if merc_dignity else "neutral",
                "is_retrograde": mercury_data.is_retrograde
            }

        # Third lord position
        third_sign = self.d3.houses.get(3, Zodiac.GEMINI)
        third_lord = get_sign_lord(third_sign)
        third_lord_data = self.d3.planets.get(third_lord)
        third_lord_position = {
            "planet": third_lord.value,
            "sign": third_lord_data.sign.name if third_lord_data else "Unknown",
            "house": third_lord_data.house if third_lord_data else 0
        }

        # Planets in 3rd house
        planets_in_third = [p.value for p in self.d3.get_planets_in_house(3)]

        # Courage indicators
        courage_indicators = []
        if mars_data:
            if is_kendra(mars_data.house):
                courage_indicators.append("Mars in kendra - strong initiative")
            if mars_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                courage_indicators.append("Mars well-dignified - natural courage")
            if mars_data.house == 3:
                courage_indicators.append("Mars in 3rd - bold communicator")

        if Planet.SUN in self.d3.get_planets_in_house(3):
            courage_indicators.append("Sun in 3rd - confident self-expression")

        # Skill indicators
        skill_indicators = []
        if mercury_data:
            if is_kendra(mercury_data.house) or is_trikona(mercury_data.house):
                skill_indicators.append("Mercury well-placed - strong intellectual skills")
            if mercury_data.dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                skill_indicators.append("Mercury dignified - excellent communication")

        # Venus for artistic skills
        venus_data = self.d3.planets.get(Planet.VENUS)
        if venus_data:
            if is_kendra(venus_data.house) or is_trikona(venus_data.house):
                skill_indicators.append("Venus well-placed - artistic abilities")

        # Jupiter for teaching/wisdom
        jupiter_data = self.d3.planets.get(Planet.JUPITER)
        if jupiter_data:
            if is_kendra(jupiter_data.house) or is_trikona(jupiter_data.house):
                skill_indicators.append("Jupiter well-placed - teaching ability")

        # Sibling indicators
        sibling_indicators = []
        if third_lord_data:
            if is_kendra(third_lord_data.house) or is_trikona(third_lord_data.house):
                sibling_indicators.append("3rd lord well-placed - supportive siblings")
            if is_dusthana(third_lord_data.house):
                sibling_indicators.append("3rd lord in dusthana - sibling challenges")

        if planets_in_third:
            benefics_in_3 = [p for p in planets_in_third if Planet.from_string(p) in [Planet.JUPITER, Planet.VENUS, Planet.MERCURY]]
            if benefics_in_3:
                sibling_indicators.append(f"Benefics in 3rd ({', '.join(benefics_in_3)}) - harmonious sibling relations")

        return DrekkanaAnalysis(
            d3_ascendant=d3_asc,
            d3_ascendant_element=d3_element,
            mars_position=mars_position,
            mercury_position=mercury_position,
            third_lord_position=third_lord_position,
            planets_in_third=planets_in_third,
            courage_indicators=courage_indicators,
            skill_indicators=skill_indicators,
            sibling_indicators=sibling_indicators
        )

    def _calculate_initiative_index(self, drekkana: DrekkanaAnalysis) -> float:
        """Calculate initiative/courage index"""
        score = 50.0

        # Mars position is primary factor
        mars = drekkana.mars_position
        if mars:
            dignity = mars.get("dignity", "neutral")
            house = mars.get("house", 6)

            if dignity == "exalted":
                score += 25
            elif dignity == "own_sign":
                score += 20
            elif dignity == "debilitated":
                score -= 15

            if is_kendra(house):
                score += 15
            elif is_trikona(house):
                score += 10
            elif is_dusthana(house):
                score -= 10

            if mars.get("is_retrograde"):
                score -= 5  # Internalized energy

        # Courage indicators add bonus
        score += len(drekkana.courage_indicators) * 5

        # Fire element ascendant adds initiative
        if drekkana.d3_ascendant_element == "fire":
            score += 10
        elif drekkana.d3_ascendant_element == "earth":
            score += 5  # Practical initiative

        return max(0, min(100, score))

    def _calculate_communication_index(self, drekkana: DrekkanaAnalysis) -> float:
        """Calculate communication ability index"""
        score = 50.0

        # Mercury position is primary factor
        mercury = drekkana.mercury_position
        if mercury:
            dignity = mercury.get("dignity", "neutral")
            house = mercury.get("house", 6)

            if dignity == "exalted":
                score += 25
            elif dignity == "own_sign":
                score += 20
            elif dignity == "debilitated":
                score -= 15

            if is_kendra(house):
                score += 15
            elif is_trikona(house):
                score += 10
            elif is_dusthana(house):
                score -= 10

        # Skill indicators
        comm_skills = [s for s in drekkana.skill_indicators if "communication" in s.lower() or "intellectual" in s.lower()]
        score += len(comm_skills) * 8

        # Air element ascendant boosts communication
        if drekkana.d3_ascendant_element == "air":
            score += 12

        # Planets in 3rd house boost communication
        score += len(drekkana.planets_in_third) * 3

        return max(0, min(100, score))

    def _calculate_skill_diversity_index(self, drekkana: DrekkanaAnalysis) -> float:
        """Calculate skill diversity index"""
        score = 50.0

        # More skill indicators = more diversity
        score += len(drekkana.skill_indicators) * 8

        # Planets in 3rd add diversity
        score += len(drekkana.planets_in_third) * 5

        # Check for varied dignities
        mars = drekkana.mars_position
        mercury = drekkana.mercury_position

        if mars and mars.get("dignity") in ["exalted", "own_sign"]:
            score += 10
        if mercury and mercury.get("dignity") in ["exalted", "own_sign"]:
            score += 10

        return max(0, min(100, score))

    def _determine_primary_skills(self, drekkana: DrekkanaAnalysis) -> List[SkillType]:
        """Determine primary skill types from chart"""
        skills = []

        mercury = drekkana.mercury_position
        mars = drekkana.mars_position

        # Communication skills
        if mercury and mercury.get("dignity") in ["exalted", "own_sign"]:
            skills.append(SkillType.COMMUNICATION)

        # Technical/Physical skills from Mars
        if mars and mars.get("dignity") in ["exalted", "own_sign"]:
            if drekkana.d3_ascendant_element in ["fire", "earth"]:
                skills.append(SkillType.TECHNICAL)
            else:
                skills.append(SkillType.PHYSICAL)

        # Artistic from Venus indicators
        if any("artistic" in s.lower() for s in drekkana.skill_indicators):
            skills.append(SkillType.ARTISTIC)

        # Teaching from Jupiter indicators
        if any("teaching" in s.lower() for s in drekkana.skill_indicators):
            skills.append(SkillType.TEACHING)

        # Analytical from Mercury in earth/air signs
        if mercury and drekkana.d3_ascendant_element in ["earth", "air"]:
            skills.append(SkillType.ANALYTICAL)

        # Entrepreneurial from strong Mars + Mercury
        if mars and mercury:
            mars_strong = mars.get("dignity") in ["exalted", "own_sign"]
            merc_strong = mercury.get("dignity") in ["exalted", "own_sign"]
            if mars_strong and merc_strong:
                skills.append(SkillType.ENTREPRENEURIAL)

        if not skills:
            skills = [SkillType.COMMUNICATION]

        return list(set(skills))[:4]  # Return unique, max 4

    def _determine_initiative_style(self, drekkana: DrekkanaAnalysis) -> InitiativeStyle:
        """Determine how person takes initiative"""
        mars = drekkana.mars_position
        element = drekkana.d3_ascendant_element

        # Fire + strong Mars = bold
        if element == "fire" and mars and mars.get("dignity") in ["exalted", "own_sign"]:
            return InitiativeStyle.BOLD

        # Earth element = strategic
        if element == "earth":
            return InitiativeStyle.STRATEGIC

        # Air element = collaborative
        if element == "air":
            return InitiativeStyle.COLLABORATIVE

        # Water element = cautious
        if element == "water":
            return InitiativeStyle.CAUTIOUS

        # Mars retrograde = opportunistic
        if mars and mars.get("is_retrograde"):
            return InitiativeStyle.OPPORTUNISTIC

        return InitiativeStyle.STRATEGIC

    def _determine_risk_tolerance(self, drekkana: DrekkanaAnalysis, initiative_index: float) -> str:
        """Determine risk tolerance level"""
        if initiative_index > 70:
            return "high"
        elif initiative_index > 45:
            return "moderate"
        else:
            return "low"

    def _calculate_house_adjustments(
        self,
        drekkana: DrekkanaAnalysis,
        initiative_index: float,
        communication_index: float
    ) -> Dict[str, float]:
        """Calculate house score adjustments"""
        adjustments = {}

        # 3rd house adjustment based on overall D3 analysis
        h3_adj = ((initiative_index + communication_index) / 2 - 50) / 10
        adjustments["house_3"] = round(h3_adj, 2)

        # 6th house (effort, daily work) from initiative
        h6_adj = (initiative_index - 50) / 15
        adjustments["house_6"] = round(h6_adj, 2)

        return adjustments

    def _generate_interpretations(
        self,
        drekkana: DrekkanaAnalysis,
        initiative_index: float,
        communication_index: float
    ) -> tuple[List[str], List[str]]:
        """Generate strength and challenge interpretations"""
        strengths = []
        challenges = []

        if initiative_index > 70:
            strengths.append("Strong initiative and courage in D3")
        elif initiative_index < 40:
            challenges.append("Initiative may need conscious development")

        if communication_index > 70:
            strengths.append("Excellent communication abilities")
        elif communication_index < 40:
            challenges.append("Communication skills need strengthening")

        # Mars-specific
        mars = drekkana.mars_position
        if mars:
            if mars.get("dignity") in ["exalted", "own_sign"]:
                strengths.append("Mars strong - natural leadership and courage")
            elif mars.get("dignity") == "debilitated":
                challenges.append("Mars weak - may struggle with assertiveness")

        # Mercury-specific
        mercury = drekkana.mercury_position
        if mercury:
            if mercury.get("dignity") in ["exalted", "own_sign"]:
                strengths.append("Mercury strong - quick thinking and learning")
            elif mercury.get("dignity") == "debilitated":
                challenges.append("Mercury weak - may need extra focus on communication")

        # Add existing indicators
        if drekkana.courage_indicators:
            strengths.append(drekkana.courage_indicators[0])
        if drekkana.skill_indicators:
            strengths.append(drekkana.skill_indicators[0])

        return strengths, challenges

    def _generate_skill_recommendations(
        self,
        drekkana: DrekkanaAnalysis,
        primary_skills: List[SkillType]
    ) -> List[str]:
        """Generate skill development recommendations"""
        recommendations = []

        element = drekkana.d3_ascendant_element

        if SkillType.COMMUNICATION in primary_skills:
            recommendations.append("Develop writing, public speaking, or media skills")

        if SkillType.TECHNICAL in primary_skills:
            recommendations.append("Pursue technical certifications or engineering skills")

        if SkillType.ARTISTIC in primary_skills:
            recommendations.append("Explore creative arts, design, or music")

        if SkillType.ENTREPRENEURIAL in primary_skills:
            recommendations.append("Consider business ventures or leadership roles")

        # Element-based recommendations
        if element == "fire" and SkillType.PHYSICAL not in primary_skills:
            recommendations.append("Physical activities can boost energy and focus")
        if element == "air" and SkillType.ANALYTICAL not in primary_skills:
            recommendations.append("Analytical thinking could complement natural abilities")

        if not recommendations:
            recommendations = ["Focus on developing hands-on practical skills"]

        return recommendations[:4]

    def _default_drekkana_analysis(self) -> DrekkanaAnalysis:
        """Return default analysis when D3 not available"""
        return DrekkanaAnalysis(
            d3_ascendant=Zodiac.ARIES,
            d3_ascendant_element="fire",
            mars_position={},
            mercury_position={},
            third_lord_position={},
            planets_in_third=[],
            courage_indicators=[],
            skill_indicators=[],
            sibling_indicators=[]
        )
