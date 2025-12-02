"""
Stage 6: Career & Status Analysis (D10 Dashamsha)

D10 (Dashamsha): The most important varga for career, profession,
                 public reputation, and worldly achievements.

Output: CareerAnalysis with professional indices and career archetypes
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .varga_utils import (
    parse_varga_chart, VargaChartData, VargaPlanetData,
    get_sign_lord, is_benefic, is_malefic, get_dignity_in_sign,
    is_kendra, is_trikona, is_dusthana, get_element, get_modality
)
from ..models.types import Planet, Zodiac, Dignity


class CareerArchetype(Enum):
    """Career archetypes based on planetary influences"""
    LEADER = "leader"               # Sun dominant - authority, government
    NURTURER = "nurturer"           # Moon dominant - caregiving, hospitality
    WARRIOR = "warrior"             # Mars dominant - military, sports, surgery
    COMMUNICATOR = "communicator"   # Mercury dominant - writing, commerce, tech
    ADVISOR = "advisor"             # Jupiter dominant - teaching, law, consulting
    ARTIST = "artist"               # Venus dominant - arts, entertainment, luxury
    BUILDER = "builder"             # Saturn dominant - construction, agriculture
    INNOVATOR = "innovator"         # Rahu dominant - technology, unconventional
    HEALER = "healer"               # Ketu dominant - alternative medicine, spiritual


class WorkStyle(Enum):
    """Preferred work style"""
    INDEPENDENT = "independent"       # Self-employed, entrepreneurial
    COLLABORATIVE = "collaborative"   # Team-oriented
    STRUCTURED = "structured"         # Corporate, hierarchical
    FLEXIBLE = "flexible"             # Variable, project-based
    SERVICE = "service"               # Helping others


@dataclass
class DashamshaAnalysis:
    """D10 Dashamsha chart analysis"""
    d10_ascendant: Zodiac
    d10_ascendant_element: str
    d10_ascendant_modality: str
    tenth_lord_d10: Dict[str, Any]      # 10th lord position in D10
    tenth_lord_d1: Dict[str, Any]       # 10th lord position in D1
    sun_position: Dict[str, Any]        # Sun (karaka for career)
    saturn_position: Dict[str, Any]     # Saturn (karaka for profession)
    mercury_position: Dict[str, Any]    # Mercury (karaka for skills)
    planets_in_tenth: List[str]
    strong_planets: List[str]           # Well-dignified in D10
    weak_planets: List[str]             # Poorly dignified in D10


@dataclass
class Stage6Result:
    """Complete Stage 6 analysis output"""
    dashamsha: DashamshaAnalysis

    # Core indices
    career_strength_index: float        # 0-100 overall career potential
    professional_success_index: float   # 0-100 achievement potential
    public_recognition_index: float     # 0-100 fame/reputation potential
    authority_index: float              # 0-100 leadership potential

    # Derived attributes
    primary_archetypes: List[CareerArchetype]
    work_style: WorkStyle
    career_sectors: List[str]           # Recommended industries

    # House score adjustments
    house_score_adjustments: Dict[str, float]

    # Interpretations
    career_strengths: List[str]
    career_challenges: List[str]
    career_timing_hints: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dashamsha": {
                "ascendant": self.dashamsha.d10_ascendant.name,
                "ascendant_element": self.dashamsha.d10_ascendant_element,
                "ascendant_modality": self.dashamsha.d10_ascendant_modality,
                "tenth_lord_d10": self.dashamsha.tenth_lord_d10,
                "tenth_lord_d1": self.dashamsha.tenth_lord_d1,
                "sun": self.dashamsha.sun_position,
                "saturn": self.dashamsha.saturn_position,
                "mercury": self.dashamsha.mercury_position,
                "planets_in_tenth": self.dashamsha.planets_in_tenth,
                "strong_planets": self.dashamsha.strong_planets,
                "weak_planets": self.dashamsha.weak_planets
            },
            "indices": {
                "career_strength": round(self.career_strength_index, 1),
                "professional_success": round(self.professional_success_index, 1),
                "public_recognition": round(self.public_recognition_index, 1),
                "authority": round(self.authority_index, 1)
            },
            "archetypes": [a.value for a in self.primary_archetypes],
            "work_style": self.work_style.value,
            "career_sectors": self.career_sectors,
            "house_adjustments": self.house_score_adjustments,
            "strengths": self.career_strengths,
            "challenges": self.career_challenges,
            "timing_hints": self.career_timing_hints
        }


class Stage06CareerAnalysis:
    """
    Stage 6: Analyze D10 (Dashamsha) for career potential.

    Input: digital_twin, D1 basic data
    Output: Stage6Result with career indices
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
        self.d10 = parse_varga_chart(digital_twin, "D10")
        self.d1 = parse_varga_chart(digital_twin, "D1")

    def analyze(self) -> Stage6Result:
        """Run complete Stage 6 analysis"""
        dashamsha = self._analyze_dashamsha()

        # Calculate indices
        career_index = self._calculate_career_strength_index(dashamsha)
        success_index = self._calculate_professional_success_index(dashamsha)
        recognition_index = self._calculate_public_recognition_index(dashamsha)
        authority_index = self._calculate_authority_index(dashamsha)

        # Determine attributes
        archetypes = self._determine_career_archetypes(dashamsha)
        work_style = self._determine_work_style(dashamsha)
        sectors = self._determine_career_sectors(dashamsha, archetypes)

        # House adjustments
        adjustments = self._calculate_house_adjustments(career_index, success_index)

        # Interpretations
        strengths, challenges = self._generate_interpretations(dashamsha, career_index)
        timing = self._generate_timing_hints(dashamsha)

        return Stage6Result(
            dashamsha=dashamsha,
            career_strength_index=career_index,
            professional_success_index=success_index,
            public_recognition_index=recognition_index,
            authority_index=authority_index,
            primary_archetypes=archetypes,
            work_style=work_style,
            career_sectors=sectors,
            house_score_adjustments=adjustments,
            career_strengths=strengths,
            career_challenges=challenges,
            career_timing_hints=timing
        )

    def _analyze_dashamsha(self) -> DashamshaAnalysis:
        """Analyze D10 Dashamsha chart"""
        if not self.d10:
            return self._default_dashamsha_analysis()

        d10_asc = self.d10.ascendant_sign
        d10_element = get_element(d10_asc)
        d10_modality = get_modality(d10_asc)

        # 10th lord in D10
        tenth_sign_d10 = self.d10.houses.get(10, Zodiac.CAPRICORN)
        tenth_lord = get_sign_lord(tenth_sign_d10)
        tenth_lord_data_d10 = self.d10.planets.get(tenth_lord)

        tenth_lord_d10_pos = {}
        if tenth_lord_data_d10:
            dignity = tenth_lord_data_d10.dignity or get_dignity_in_sign(tenth_lord, tenth_lord_data_d10.sign)
            tenth_lord_d10_pos = {
                "planet": tenth_lord.value,
                "sign": tenth_lord_data_d10.sign.name,
                "house": tenth_lord_data_d10.house,
                "dignity": dignity.value if dignity else "neutral"
            }

        # 10th lord from D1 house_lords
        tenth_lord_d1_info = self.house_lords.get(10, {})
        tenth_lord_d1_pos = {
            "planet": tenth_lord_d1_info.get("lord", "Unknown"),
            "in_house": tenth_lord_d1_info.get("in_house", 0)
        }

        # Sun position (karaka for authority)
        sun_data = self.d10.planets.get(Planet.SUN)
        sun_position = {}
        if sun_data:
            sun_dignity = sun_data.dignity or get_dignity_in_sign(Planet.SUN, sun_data.sign)
            sun_position = {
                "sign": sun_data.sign.name,
                "house": sun_data.house,
                "dignity": sun_dignity.value if sun_dignity else "neutral"
            }

        # Saturn position (karaka for profession/hard work)
        saturn_data = self.d10.planets.get(Planet.SATURN)
        saturn_position = {}
        if saturn_data:
            sat_dignity = saturn_data.dignity or get_dignity_in_sign(Planet.SATURN, saturn_data.sign)
            saturn_position = {
                "sign": saturn_data.sign.name,
                "house": saturn_data.house,
                "dignity": sat_dignity.value if sat_dignity else "neutral"
            }

        # Mercury position (karaka for skills)
        mercury_data = self.d10.planets.get(Planet.MERCURY)
        mercury_position = {}
        if mercury_data:
            merc_dignity = mercury_data.dignity or get_dignity_in_sign(Planet.MERCURY, mercury_data.sign)
            mercury_position = {
                "sign": mercury_data.sign.name,
                "house": mercury_data.house,
                "dignity": merc_dignity.value if merc_dignity else "neutral"
            }

        # Planets in 10th house
        planets_in_tenth = [p.value for p in self.d10.get_planets_in_house(10)]

        # Strong and weak planets
        strong_planets = []
        weak_planets = []

        for planet, data in self.d10.planets.items():
            dignity = data.dignity or get_dignity_in_sign(planet, data.sign)
            if dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                strong_planets.append(planet.value)
            elif dignity == Dignity.DEBILITATED:
                weak_planets.append(planet.value)

        return DashamshaAnalysis(
            d10_ascendant=d10_asc,
            d10_ascendant_element=d10_element,
            d10_ascendant_modality=d10_modality,
            tenth_lord_d10=tenth_lord_d10_pos,
            tenth_lord_d1=tenth_lord_d1_pos,
            sun_position=sun_position,
            saturn_position=saturn_position,
            mercury_position=mercury_position,
            planets_in_tenth=planets_in_tenth,
            strong_planets=strong_planets,
            weak_planets=weak_planets
        )

    def _calculate_career_strength_index(self, dashamsha: DashamshaAnalysis) -> float:
        """Calculate overall career strength"""
        score = 50.0

        # 10th lord dignity in D10
        tenth_lord = dashamsha.tenth_lord_d10
        if tenth_lord:
            dignity = tenth_lord.get("dignity", "neutral")
            house = tenth_lord.get("house", 6)

            if dignity == "exalted":
                score += 25
            elif dignity == "own_sign":
                score += 20
            elif dignity == "debilitated":
                score -= 15

            if is_kendra(house):
                score += 10
            elif is_trikona(house):
                score += 8

        # 10th lord in D1 placement
        tenth_d1 = dashamsha.tenth_lord_d1
        if tenth_d1:
            d1_house = tenth_d1.get("in_house", 0)
            if d1_house in [1, 4, 5, 7, 9, 10, 11]:
                score += 8
            elif d1_house in [6, 8, 12]:
                score -= 5

        # Strong planets bonus
        score += len(dashamsha.strong_planets) * 3
        score -= len(dashamsha.weak_planets) * 2

        return max(0, min(100, score))

    def _calculate_professional_success_index(self, dashamsha: DashamshaAnalysis) -> float:
        """Calculate professional achievement potential"""
        score = 50.0

        # Saturn strength (karaka for profession)
        saturn = dashamsha.saturn_position
        if saturn:
            dignity = saturn.get("dignity", "neutral")
            if dignity == "exalted":
                score += 20
            elif dignity == "own_sign":
                score += 15
            elif dignity == "debilitated":
                score -= 10

            house = saturn.get("house", 6)
            if is_kendra(house):
                score += 10
            elif is_trikona(house):
                score += 8

        # Mercury strength (skills)
        mercury = dashamsha.mercury_position
        if mercury:
            dignity = mercury.get("dignity", "neutral")
            if dignity in ["exalted", "own_sign"]:
                score += 10

        # Planets in 10th add potential
        score += len(dashamsha.planets_in_tenth) * 5

        return max(0, min(100, score))

    def _calculate_public_recognition_index(self, dashamsha: DashamshaAnalysis) -> float:
        """Calculate fame/recognition potential"""
        score = 50.0

        # Sun strength (karaka for fame)
        sun = dashamsha.sun_position
        if sun:
            dignity = sun.get("dignity", "neutral")
            if dignity == "exalted":
                score += 25
            elif dignity == "own_sign":
                score += 20
            elif dignity == "debilitated":
                score -= 15

            house = sun.get("house", 6)
            if house in [1, 10]:  # Angular positions
                score += 15
            elif is_kendra(house):
                score += 10

        # Fire ascendant in D10 adds visibility
        if dashamsha.d10_ascendant_element == "fire":
            score += 8

        # Jupiter and Venus in kendras add recognition
        if "Jupiter" in dashamsha.strong_planets:
            score += 8
        if "Venus" in dashamsha.strong_planets:
            score += 5

        return max(0, min(100, score))

    def _calculate_authority_index(self, dashamsha: DashamshaAnalysis) -> float:
        """Calculate leadership/authority potential"""
        score = 50.0

        # Sun is primary indicator
        sun = dashamsha.sun_position
        if sun:
            dignity = sun.get("dignity", "neutral")
            if dignity == "exalted":
                score += 25
            elif dignity == "own_sign":
                score += 20

            house = sun.get("house", 6)
            if house == 10:
                score += 15
            elif house == 1:
                score += 12

        # Mars adds authority/command
        mars_data = self.d10.planets.get(Planet.MARS) if self.d10 else None
        if mars_data:
            mars_dignity = mars_data.dignity or get_dignity_in_sign(Planet.MARS, mars_data.sign)
            if mars_dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                score += 10
            if is_kendra(mars_data.house):
                score += 8

        # Cardinal modality indicates leadership
        if dashamsha.d10_ascendant_modality == "cardinal":
            score += 8

        return max(0, min(100, score))

    def _determine_career_archetypes(self, dashamsha: DashamshaAnalysis) -> List[CareerArchetype]:
        """Determine primary career archetypes"""
        archetypes = []
        archetype_scores: Dict[CareerArchetype, float] = {}

        # Sun strength -> Leader
        sun = dashamsha.sun_position
        if sun and sun.get("dignity") in ["exalted", "own_sign"]:
            archetype_scores[CareerArchetype.LEADER] = 80
        elif sun and is_kendra(sun.get("house", 6)):
            archetype_scores[CareerArchetype.LEADER] = 60

        # Saturn strength -> Builder
        saturn = dashamsha.saturn_position
        if saturn and saturn.get("dignity") in ["exalted", "own_sign"]:
            archetype_scores[CareerArchetype.BUILDER] = 80
        elif saturn and is_kendra(saturn.get("house", 6)):
            archetype_scores[CareerArchetype.BUILDER] = 60

        # Mercury strength -> Communicator
        mercury = dashamsha.mercury_position
        if mercury and mercury.get("dignity") in ["exalted", "own_sign"]:
            archetype_scores[CareerArchetype.COMMUNICATOR] = 80
        elif mercury and is_kendra(mercury.get("house", 6)):
            archetype_scores[CareerArchetype.COMMUNICATOR] = 60

        # Check for other planets
        if self.d10:
            jupiter_data = self.d10.planets.get(Planet.JUPITER)
            if jupiter_data:
                jup_dignity = jupiter_data.dignity or get_dignity_in_sign(Planet.JUPITER, jupiter_data.sign)
                if jup_dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                    archetype_scores[CareerArchetype.ADVISOR] = 80

            venus_data = self.d10.planets.get(Planet.VENUS)
            if venus_data:
                ven_dignity = venus_data.dignity or get_dignity_in_sign(Planet.VENUS, venus_data.sign)
                if ven_dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                    archetype_scores[CareerArchetype.ARTIST] = 80

            mars_data = self.d10.planets.get(Planet.MARS)
            if mars_data:
                mars_dignity = mars_data.dignity or get_dignity_in_sign(Planet.MARS, mars_data.sign)
                if mars_dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                    archetype_scores[CareerArchetype.WARRIOR] = 80

            moon_data = self.d10.planets.get(Planet.MOON)
            if moon_data:
                moon_dignity = moon_data.dignity or get_dignity_in_sign(Planet.MOON, moon_data.sign)
                if moon_dignity in [Dignity.EXALTED, Dignity.OWN_SIGN]:
                    archetype_scores[CareerArchetype.NURTURER] = 70

            rahu_data = self.d10.planets.get(Planet.RAHU)
            if rahu_data and is_kendra(rahu_data.house):
                archetype_scores[CareerArchetype.INNOVATOR] = 65

            ketu_data = self.d10.planets.get(Planet.KETU)
            if ketu_data and is_kendra(ketu_data.house):
                archetype_scores[CareerArchetype.HEALER] = 60

        # Sort by score and take top 3
        sorted_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
        archetypes = [a[0] for a in sorted_archetypes[:3]]

        if not archetypes:
            archetypes = [CareerArchetype.BUILDER]

        return archetypes

    def _determine_work_style(self, dashamsha: DashamshaAnalysis) -> WorkStyle:
        """Determine preferred work style"""
        sun = dashamsha.sun_position
        saturn = dashamsha.saturn_position
        element = dashamsha.d10_ascendant_element

        # Strong Sun = independent/leadership
        if sun and sun.get("dignity") in ["exalted", "own_sign"]:
            return WorkStyle.INDEPENDENT

        # Strong Saturn = structured
        if saturn and saturn.get("dignity") in ["exalted", "own_sign"]:
            return WorkStyle.STRUCTURED

        # Water element = service oriented
        if element == "water":
            return WorkStyle.SERVICE

        # Air element = collaborative
        if element == "air":
            return WorkStyle.COLLABORATIVE

        # Mutable modality = flexible
        if dashamsha.d10_ascendant_modality == "mutable":
            return WorkStyle.FLEXIBLE

        return WorkStyle.STRUCTURED

    def _determine_career_sectors(
        self,
        dashamsha: DashamshaAnalysis,
        archetypes: List[CareerArchetype]
    ) -> List[str]:
        """Determine recommended career sectors"""
        sectors = []

        archetype_sectors = {
            CareerArchetype.LEADER: ["Government", "Executive Management", "Politics"],
            CareerArchetype.NURTURER: ["Healthcare", "Hospitality", "Human Resources"],
            CareerArchetype.WARRIOR: ["Military", "Sports", "Surgery", "Engineering"],
            CareerArchetype.COMMUNICATOR: ["Media", "Technology", "Commerce", "Writing"],
            CareerArchetype.ADVISOR: ["Law", "Education", "Consulting", "Finance"],
            CareerArchetype.ARTIST: ["Entertainment", "Design", "Luxury Goods", "Beauty"],
            CareerArchetype.BUILDER: ["Construction", "Agriculture", "Manufacturing"],
            CareerArchetype.INNOVATOR: ["Technology", "Research", "Startups"],
            CareerArchetype.HEALER: ["Alternative Medicine", "Spirituality", "Psychology"]
        }

        for archetype in archetypes:
            sectors.extend(archetype_sectors.get(archetype, []))

        # Add element-based sectors
        element = dashamsha.d10_ascendant_element
        element_sectors = {
            "fire": ["Leadership", "Sports", "Entrepreneurship"],
            "earth": ["Real Estate", "Banking", "Agriculture"],
            "air": ["IT", "Networking", "Communication"],
            "water": ["Arts", "Counseling", "Maritime"]
        }
        sectors.extend(element_sectors.get(element, []))

        # Remove duplicates and limit
        return list(dict.fromkeys(sectors))[:8]

    def _calculate_house_adjustments(
        self,
        career_index: float,
        success_index: float
    ) -> Dict[str, float]:
        """Calculate house score adjustments"""
        adjustments = {}

        # 10th house based on career analysis
        h10_adj = (career_index - 50) / 10
        adjustments["house_10"] = round(h10_adj, 2)

        # 6th house (daily work) correlates with success
        h6_adj = (success_index - 50) / 15
        adjustments["house_6"] = round(h6_adj, 2)

        # 1st house (self-projection) affected by career strength
        h1_adj = (career_index - 50) / 20
        adjustments["house_1"] = round(h1_adj, 2)

        return adjustments

    def _generate_interpretations(
        self,
        dashamsha: DashamshaAnalysis,
        career_index: float
    ) -> tuple[List[str], List[str]]:
        """Generate strength and challenge interpretations"""
        strengths = []
        challenges = []

        if career_index > 70:
            strengths.append("Strong D10 indicates excellent career potential")
        elif career_index < 40:
            challenges.append("Career may require extra effort and patience")

        # 10th lord analysis
        tenth_lord = dashamsha.tenth_lord_d10
        if tenth_lord:
            dignity = tenth_lord.get("dignity", "neutral")
            if dignity in ["exalted", "own_sign"]:
                strengths.append(f"10th lord ({tenth_lord.get('planet')}) strongly placed")
            elif dignity == "debilitated":
                challenges.append(f"10th lord ({tenth_lord.get('planet')}) needs support")

        # Sun analysis
        sun = dashamsha.sun_position
        if sun:
            if sun.get("dignity") in ["exalted", "own_sign"]:
                strengths.append("Sun strong - natural authority and recognition")
            elif sun.get("dignity") == "debilitated":
                challenges.append("Sun weak - authority may come through service")

        # Strong planets bonus
        if len(dashamsha.strong_planets) >= 3:
            strengths.append(f"Multiple strong planets: {', '.join(dashamsha.strong_planets[:3])}")

        if len(dashamsha.weak_planets) >= 2:
            challenges.append(f"Planets needing attention: {', '.join(dashamsha.weak_planets[:2])}")

        return strengths, challenges

    def _generate_timing_hints(self, dashamsha: DashamshaAnalysis) -> List[str]:
        """Generate timing hints for career activation"""
        hints = []

        tenth_lord = dashamsha.tenth_lord_d10
        if tenth_lord:
            planet = tenth_lord.get("planet", "")
            hints.append(f"Career activates during {planet} dasha/antardasha periods")

        sun = dashamsha.sun_position
        if sun and sun.get("dignity") in ["exalted", "own_sign"]:
            hints.append("Sun periods bring recognition and authority")

        saturn = dashamsha.saturn_position
        if saturn and saturn.get("dignity") in ["exalted", "own_sign"]:
            hints.append("Saturn periods solidify professional foundation")

        if dashamsha.strong_planets:
            hints.append(f"Strong planets ({', '.join(dashamsha.strong_planets[:2])}) periods are favorable")

        return hints[:4]

    def _default_dashamsha_analysis(self) -> DashamshaAnalysis:
        """Return default analysis when D10 not available"""
        return DashamshaAnalysis(
            d10_ascendant=Zodiac.ARIES,
            d10_ascendant_element="fire",
            d10_ascendant_modality="cardinal",
            tenth_lord_d10={},
            tenth_lord_d1={},
            sun_position={},
            saturn_position={},
            mercury_position={},
            planets_in_tenth=[],
            strong_planets=[],
            weak_planets=[]
        )
