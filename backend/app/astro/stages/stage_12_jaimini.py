"""
Stage 12: Jaimini Synthesis

Analyzes the chart using Jaimini astrology system:
- Chara Karakas (7-planet system)
- Atmakaraka (soul significator) meaning
- Karakamsha (AK in D9) interpretation
- Arudha Lagna calculation
- Badhaka (obstruction) house
- Composite Jaimini score

Key concepts:
- Atmakaraka: Planet with highest degree in sign (soul lesson)
- Amatyakaraka: 2nd highest (career/status)
- Karakamsha: AK's position in Navamsha (life purpose)
- Arudha Lagna: Public image point
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from ..models.types import Planet, Zodiac, House, Karaka
from ..reference.jaimini import (
    ATMAKARAKA_MEANINGS,
    KARAKAMSHA_MEANINGS,
    SIGN_MODALITY,
    get_badhaka_house,
    get_atmakaraka_meaning,
    get_karakamsha_meaning,
    AtmakarakaMeaning,
    KarakamshaMeaning,
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_planet_attr(planet: Any, key: str, default: Any = None) -> Any:
    """Helper to get attribute from dict or object"""
    if hasattr(planet, 'get'):
        return planet.get(key, default)
    return getattr(planet, key, default)


# =============================================================================
# OUTPUT DATACLASSES
# =============================================================================

@dataclass
class CharaKarakaInfo:
    """Individual Chara Karaka information"""
    karaka_code: str           # AK, AmK, BK, MK, PK, GK, DK
    karaka_name: str           # Full name (Atmakaraka, etc.)
    planet: str                # Planet name
    degrees_in_sign: float     # Degree (0-30)
    sign: str                  # Sign name
    significance: str          # What this karaka signifies


@dataclass
class AtmakarakaAnalysis:
    """Detailed Atmakaraka analysis"""
    planet: str
    degrees_in_sign: float
    sign_d1: str
    sign_d9: str               # Karakamsha
    soul_lesson: str
    karmic_trap: str
    spiritual_path: str
    life_theme: str
    strengths: List[str]
    challenges: List[str]


@dataclass
class KarakamshaAnalysis:
    """Karakamsha (AK in D9) analysis"""
    sign: str
    life_purpose: str
    career_direction: str
    spiritual_path: str
    key_themes: List[str]


@dataclass
class ArudhaLagnaAnalysis:
    """Arudha Lagna (public image) analysis"""
    sign: str
    house_from_lagna: int
    interpretation: str


@dataclass
class BadhakaAnalysis:
    """Badhaka (obstruction) house analysis"""
    badhaka_house: int
    badhaka_sign: str
    badhaka_lord: str
    obstruction_themes: List[str]


@dataclass
class JaiminiAnalysis:
    """
    Stage 12 Output: Complete Jaimini System Analysis

    Contains:
    - All 7 Chara Karakas with meanings
    - Detailed Atmakaraka analysis
    - Karakamsha interpretation
    - Arudha Lagna analysis
    - Badhaka house analysis
    - Composite Jaimini scores
    """
    # Chara Karakas (7-planet system)
    chara_karakas: List[CharaKarakaInfo]

    # Atmakaraka deep dive
    atmakaraka: AtmakarakaAnalysis

    # Karakamsha analysis
    karakamsha: KarakamshaAnalysis

    # Arudha Lagna
    arudha_lagna: ArudhaLagnaAnalysis

    # Badhaka house
    badhaka: BadhakaAnalysis

    # Composite scores (0-100)
    soul_clarity_score: float       # How clear is the soul's path
    career_alignment_score: float   # AK-AmK alignment
    public_image_strength: float    # Arudha strength
    obstruction_level: float        # Badhaka impact

    # Investment-relevant summary
    jaimini_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "chara_karakas": [
                {
                    "karaka_code": k.karaka_code,
                    "karaka_name": k.karaka_name,
                    "planet": k.planet,
                    "degrees_in_sign": round(k.degrees_in_sign, 2),
                    "sign": k.sign,
                    "significance": k.significance,
                }
                for k in self.chara_karakas
            ],
            "atmakaraka": {
                "planet": self.atmakaraka.planet,
                "degrees_in_sign": round(self.atmakaraka.degrees_in_sign, 2),
                "sign_d1": self.atmakaraka.sign_d1,
                "karakamsha_sign": self.atmakaraka.sign_d9,
                "soul_lesson": self.atmakaraka.soul_lesson,
                "karmic_trap": self.atmakaraka.karmic_trap,
                "spiritual_path": self.atmakaraka.spiritual_path,
                "life_theme": self.atmakaraka.life_theme,
                "strengths": self.atmakaraka.strengths,
                "challenges": self.atmakaraka.challenges,
            },
            "karakamsha": {
                "sign": self.karakamsha.sign,
                "life_purpose": self.karakamsha.life_purpose,
                "career_direction": self.karakamsha.career_direction,
                "spiritual_path": self.karakamsha.spiritual_path,
                "key_themes": self.karakamsha.key_themes,
            },
            "arudha_lagna": {
                "sign": self.arudha_lagna.sign,
                "house_from_lagna": self.arudha_lagna.house_from_lagna,
                "interpretation": self.arudha_lagna.interpretation,
            },
            "badhaka": {
                "badhaka_house": self.badhaka.badhaka_house,
                "badhaka_sign": self.badhaka.badhaka_sign,
                "badhaka_lord": self.badhaka.badhaka_lord,
                "obstruction_themes": self.badhaka.obstruction_themes,
            },
            "scores": {
                "soul_clarity": round(self.soul_clarity_score, 1),
                "career_alignment": round(self.career_alignment_score, 1),
                "public_image_strength": round(self.public_image_strength, 1),
                "obstruction_level": round(self.obstruction_level, 1),
            },
            "summary": self.jaimini_summary,
        }


# =============================================================================
# KARAKA SIGNIFICANCE DESCRIPTIONS
# =============================================================================

KARAKA_SIGNIFICANCE = {
    "AK": "Soul significator - soul's deepest lesson and desire",
    "AmK": "Minister/Career - profession, status, mental focus",
    "BK": "Siblings - brothers/sisters, courage, initiative",
    "MK": "Mother - mother, mind, education, property",
    "PK": "Father - father, children, fortune, guru",
    "GK": "Enemies - obstacles, enemies, diseases",
    "DK": "Spouse - marriage partner, partnerships",
}


# =============================================================================
# ARUDHA INTERPRETATION
# =============================================================================

ARUDHA_INTERPRETATIONS = {
    1: "Public image aligned with true self. What you see is what you get.",
    2: "Public image tied to wealth, speech, and family values.",
    3: "Public image through communication, courage, and skills.",
    4: "Public image through home, emotional security, motherly qualities.",
    5: "Public image through creativity, children, romance, speculation.",
    6: "Public image through service, health, competition, overcoming enemies.",
    7: "Public image through partnerships, business, spouse, public dealings.",
    8: "Public image through transformation, occult, research, hidden matters.",
    9: "Public image through wisdom, teaching, dharma, higher learning.",
    10: "Public image through career, status, authority, public action.",
    11: "Public image through gains, networks, large organizations, aspirations.",
    12: "Public image through spirituality, foreign lands, losses, liberation.",
}


# =============================================================================
# BADHAKA OBSTRUCTION THEMES
# =============================================================================

BADHAKA_THEMES = {
    Planet.SUN: ["Authority conflicts", "Ego clashes", "Father-related obstacles"],
    Planet.MOON: ["Emotional instability", "Mother-related issues", "Public opinion"],
    Planet.MARS: ["Aggression", "Accidents", "Sibling conflicts", "Property disputes"],
    Planet.MERCURY: ["Communication problems", "Business failures", "Education blocks"],
    Planet.JUPITER: ["Dogmatism", "Over-expansion", "Guru issues", "Legal problems"],
    Planet.VENUS: ["Relationship troubles", "Financial setbacks", "Luxury addiction"],
    Planet.SATURN: ["Delays", "Hard work without results", "Chronic problems", "Loneliness"],
    Planet.RAHU: ["Deception", "Foreign troubles", "Unconventional obstacles"],
    Planet.KETU: ["Spiritual confusion", "Neglect of duties", "Past karma surfacing"],
}


# =============================================================================
# SIGN LORDS REFERENCE
# =============================================================================

SIGN_LORDS = {
    Zodiac.ARIES: Planet.MARS,
    Zodiac.TAURUS: Planet.VENUS,
    Zodiac.GEMINI: Planet.MERCURY,
    Zodiac.CANCER: Planet.MOON,
    Zodiac.LEO: Planet.SUN,
    Zodiac.VIRGO: Planet.MERCURY,
    Zodiac.LIBRA: Planet.VENUS,
    Zodiac.SCORPIO: Planet.MARS,
    Zodiac.SAGITTARIUS: Planet.JUPITER,
    Zodiac.CAPRICORN: Planet.SATURN,
    Zodiac.AQUARIUS: Planet.SATURN,
    Zodiac.PISCES: Planet.JUPITER,
}


# =============================================================================
# STAGE 12 CLASS
# =============================================================================

class Stage12JaiminiSynthesis:
    """
    Stage 12: Jaimini System Synthesis

    Analyzes the chart using Jaimini astrology concepts:
    1. Chara Karakas - planet significators by degree
    2. Atmakaraka - soul significator analysis
    3. Karakamsha - AK's Navamsha position
    4. Arudha Lagna - public image point
    5. Badhaka - obstruction house
    """

    def __init__(
        self,
        digital_twin: Dict[str, Any],
        d1_planets: Optional[List[Dict[str, Any]]] = None,
        d9_planets: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize Stage 12.

        Args:
            digital_twin: Full digital twin data
            d1_planets: Optional D1 planets list
            d9_planets: Optional D9 (Navamsha) planets list
        """
        self.digital_twin = digital_twin
        self.vargas = digital_twin.get("vargas", {})
        self.d1 = self.vargas.get("D1", {})
        self.d9 = self.vargas.get("D9", {})

        # Get chara karakas from digital twin if available
        self.chara_karakas_data = digital_twin.get("chara_karakas", {})

        # Planet lists
        self.d1_planets = d1_planets or self.d1.get("planets", [])
        self.d9_planets = d9_planets or self.d9.get("planets", [])

        # Ascendant info
        self.ascendant = self.d1.get("ascendant", {})
        self.lagna_sign_id = self.ascendant.get("sign_id", 1)

    def analyze(self) -> JaiminiAnalysis:
        """
        Run Stage 12 analysis.

        Returns:
            JaiminiAnalysis with complete Jaimini system interpretation
        """
        # Parse Chara Karakas
        chara_karakas = self._parse_chara_karakas()

        # Get Atmakaraka details
        ak_info = chara_karakas[0] if chara_karakas else None
        atmakaraka = self._analyze_atmakaraka(ak_info)

        # Get Karakamsha analysis
        karakamsha = self._analyze_karakamsha(ak_info)

        # Calculate Arudha Lagna
        arudha_lagna = self._calculate_arudha_lagna()

        # Analyze Badhaka
        badhaka = self._analyze_badhaka()

        # Calculate composite scores
        scores = self._calculate_scores(chara_karakas, atmakaraka, arudha_lagna, badhaka)

        # Create summary
        summary = self._create_summary(atmakaraka, karakamsha, scores)

        return JaiminiAnalysis(
            chara_karakas=chara_karakas,
            atmakaraka=atmakaraka,
            karakamsha=karakamsha,
            arudha_lagna=arudha_lagna,
            badhaka=badhaka,
            soul_clarity_score=scores["soul_clarity"],
            career_alignment_score=scores["career_alignment"],
            public_image_strength=scores["public_image"],
            obstruction_level=scores["obstruction"],
            jaimini_summary=summary,
        )

    def _parse_chara_karakas(self) -> List[CharaKarakaInfo]:
        """
        Parse Chara Karakas from digital twin or calculate from planets.

        Returns:
            List of CharaKarakaInfo sorted by degree (AK first)
        """
        karakas = []

        # Try to get from pre-calculated chara_karakas
        karaka_list = self.chara_karakas_data.get("karakas", [])

        if karaka_list:
            # Use pre-calculated karakas
            karaka_codes = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
            karaka_names = [
                "Atmakaraka", "Amatyakaraka", "Bhratrikaraka",
                "Matrikaraka", "Pitrikaraka", "Gnatikaraka", "Darakaraka"
            ]

            for k in karaka_list:
                code = k.get("karaka_code", "")
                if code in karaka_codes:
                    idx = karaka_codes.index(code)
                    karakas.append(CharaKarakaInfo(
                        karaka_code=code,
                        karaka_name=karaka_names[idx],
                        planet=k.get("planet", ""),
                        degrees_in_sign=k.get("degrees_in_sign", 0),
                        sign=k.get("sign", ""),
                        significance=KARAKA_SIGNIFICANCE.get(code, ""),
                    ))
        else:
            # Calculate from D1 planets (7-planet system, excluding Rahu)
            planet_degrees = []
            for p in self.d1_planets:
                name = _get_planet_attr(p, "name", "") or _get_planet_attr(p, "planet", "")
                if name.lower() == "rahu":
                    continue  # Skip Rahu in 7-planet system

                degrees = _get_planet_attr(p, "degrees", 0) or _get_planet_attr(p, "degrees_in_sign", 0)
                sign = _get_planet_attr(p, "sign", "") or _get_planet_attr(p, "sign_name", "")

                if name and degrees is not None:
                    planet_degrees.append({
                        "planet": name,
                        "degrees": float(degrees),
                        "sign": sign
                    })

            # Sort by degrees descending (highest first = AK)
            planet_degrees.sort(key=lambda x: x["degrees"], reverse=True)

            karaka_codes = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
            karaka_names = [
                "Atmakaraka", "Amatyakaraka", "Bhratrikaraka",
                "Matrikaraka", "Pitrikaraka", "Gnatikaraka", "Darakaraka"
            ]

            for i, pd in enumerate(planet_degrees[:7]):
                if i < len(karaka_codes):
                    karakas.append(CharaKarakaInfo(
                        karaka_code=karaka_codes[i],
                        karaka_name=karaka_names[i],
                        planet=pd["planet"],
                        degrees_in_sign=pd["degrees"],
                        sign=pd["sign"],
                        significance=KARAKA_SIGNIFICANCE.get(karaka_codes[i], ""),
                    ))

        return karakas

    def _analyze_atmakaraka(self, ak_info: Optional[CharaKarakaInfo]) -> AtmakarakaAnalysis:
        """
        Analyze Atmakaraka in detail.

        Args:
            ak_info: CharaKarakaInfo for AK

        Returns:
            AtmakarakaAnalysis with soul lesson interpretation
        """
        if not ak_info:
            # Default fallback
            return AtmakarakaAnalysis(
                planet="Unknown",
                degrees_in_sign=0,
                sign_d1="Unknown",
                sign_d9="Unknown",
                soul_lesson="Unable to determine",
                karmic_trap="Unable to determine",
                spiritual_path="Unable to determine",
                life_theme="Unable to determine",
                strengths=[],
                challenges=[],
            )

        # Get AK planet
        ak_planet_name = ak_info.planet
        try:
            ak_planet = Planet.from_string(ak_planet_name)
        except ValueError:
            ak_planet = Planet.SUN  # Default

        # Get AK meaning
        ak_meaning = get_atmakaraka_meaning(ak_planet)
        if not ak_meaning:
            ak_meaning = AtmakarakaMeaning(
                soul_lesson="Unique soul journey",
                karmic_trap="Individual challenges",
                spiritual_path="Personal spiritual development",
                life_theme="Self-discovery",
                strengths=["Unique gifts"],
                challenges=["Individual obstacles"]
            )

        # Find AK's position in D9 (Karakamsha)
        d9_sign = "Unknown"
        for p in self.d9_planets:
            name = _get_planet_attr(p, "name", "") or _get_planet_attr(p, "planet", "")
            if name.lower() == ak_planet_name.lower():
                d9_sign = _get_planet_attr(p, "sign", "") or _get_planet_attr(p, "sign_name", "")
                break

        return AtmakarakaAnalysis(
            planet=ak_planet_name,
            degrees_in_sign=ak_info.degrees_in_sign,
            sign_d1=ak_info.sign,
            sign_d9=d9_sign,
            soul_lesson=ak_meaning.soul_lesson,
            karmic_trap=ak_meaning.karmic_trap,
            spiritual_path=ak_meaning.spiritual_path,
            life_theme=ak_meaning.life_theme,
            strengths=ak_meaning.strengths,
            challenges=ak_meaning.challenges,
        )

    def _analyze_karakamsha(self, ak_info: Optional[CharaKarakaInfo]) -> KarakamshaAnalysis:
        """
        Analyze Karakamsha (AK's position in D9).

        Args:
            ak_info: CharaKarakaInfo for AK

        Returns:
            KarakamshaAnalysis with life purpose interpretation
        """
        if not ak_info:
            return KarakamshaAnalysis(
                sign="Unknown",
                life_purpose="Unable to determine",
                career_direction="Unable to determine",
                spiritual_path="Unable to determine",
                key_themes=[],
            )

        # Find AK in D9
        ak_planet_name = ak_info.planet.lower()
        karakamsha_sign = None

        for p in self.d9_planets:
            name = _get_planet_attr(p, "name", "") or _get_planet_attr(p, "planet", "")
            if name.lower() == ak_planet_name:
                sign_name = _get_planet_attr(p, "sign", "") or _get_planet_attr(p, "sign_name", "")
                sign_id = _get_planet_attr(p, "sign_id", 0)

                if sign_id:
                    karakamsha_sign = Zodiac(sign_id)
                elif sign_name:
                    try:
                        karakamsha_sign = Zodiac.from_string(sign_name)
                    except ValueError:
                        pass
                break

        if not karakamsha_sign:
            return KarakamshaAnalysis(
                sign="Unknown",
                life_purpose="Unable to determine - D9 data not available",
                career_direction="Unable to determine",
                spiritual_path="Unable to determine",
                key_themes=[],
            )

        # Get Karakamsha meaning
        km_meaning = get_karakamsha_meaning(karakamsha_sign)
        if not km_meaning:
            km_meaning = KarakamshaMeaning(
                life_purpose="Unique life direction",
                career_direction="Individual career path",
                spiritual_path="Personal spiritual journey",
                key_themes=["Self-discovery"]
            )

        return KarakamshaAnalysis(
            sign=karakamsha_sign.name.title(),
            life_purpose=km_meaning.life_purpose,
            career_direction=km_meaning.career_direction,
            spiritual_path=km_meaning.spiritual_path,
            key_themes=km_meaning.key_themes,
        )

    def _calculate_arudha_lagna(self) -> ArudhaLagnaAnalysis:
        """
        Calculate Arudha Lagna (AL).

        Arudha Lagna = Lord of Lagna counted from Lagna,
        then same distance from Lord's position.

        Returns:
            ArudhaLagnaAnalysis with public image interpretation
        """
        try:
            lagna_sign = Zodiac(self.lagna_sign_id)
        except (ValueError, TypeError):
            lagna_sign = Zodiac.ARIES

        # Get lagna lord
        lagna_lord = SIGN_LORDS.get(lagna_sign, Planet.MARS)

        # Find where lagna lord is placed
        lord_house = 1  # Default
        lord_sign_id = self.lagna_sign_id

        for p in self.d1_planets:
            name = _get_planet_attr(p, "name", "") or _get_planet_attr(p, "planet", "")
            if name.lower() == lagna_lord.value.lower():
                lord_sign_id = _get_planet_attr(p, "sign_id", self.lagna_sign_id)
                # Calculate house from lagna
                lord_house = ((lord_sign_id - self.lagna_sign_id) % 12) + 1
                break

        # Arudha = Count same distance from lord's position
        # AL sign = lord_sign + (lord_house - 1)
        al_sign_id = ((lord_sign_id - 1) + (lord_house - 1)) % 12 + 1

        # Handle special cases (if AL falls in 1 or 7 from lord, move to 10 or 4)
        al_from_lord = ((al_sign_id - lord_sign_id) % 12) + 1
        if al_from_lord == 1:
            al_sign_id = ((lord_sign_id - 1) + 9) % 12 + 1  # Move to 10th
        elif al_from_lord == 7:
            al_sign_id = ((lord_sign_id - 1) + 3) % 12 + 1  # Move to 4th

        try:
            al_sign = Zodiac(al_sign_id)
        except (ValueError, TypeError):
            al_sign = Zodiac.ARIES

        al_house_from_lagna = ((al_sign_id - self.lagna_sign_id) % 12) + 1

        interpretation = ARUDHA_INTERPRETATIONS.get(al_house_from_lagna, "Unique public image expression.")

        return ArudhaLagnaAnalysis(
            sign=al_sign.name.title(),
            house_from_lagna=al_house_from_lagna,
            interpretation=interpretation,
        )

    def _analyze_badhaka(self) -> BadhakaAnalysis:
        """
        Analyze Badhaka (obstruction) house.

        Badhaka rules:
        - Movable signs: 11th house is badhaka
        - Fixed signs: 9th house is badhaka
        - Dual signs: 7th house is badhaka

        Returns:
            BadhakaAnalysis with obstruction interpretation
        """
        try:
            lagna_sign = Zodiac(self.lagna_sign_id)
        except (ValueError, TypeError):
            lagna_sign = Zodiac.ARIES

        # Get badhaka house
        badhaka_house = get_badhaka_house(lagna_sign)

        # Calculate badhaka sign
        badhaka_sign_id = ((self.lagna_sign_id - 1) + (badhaka_house - 1)) % 12 + 1
        try:
            badhaka_sign = Zodiac(badhaka_sign_id)
        except (ValueError, TypeError):
            badhaka_sign = Zodiac.ARIES

        # Get badhaka lord
        badhaka_lord = SIGN_LORDS.get(badhaka_sign, Planet.MARS)

        # Get obstruction themes based on badhaka lord
        themes = BADHAKA_THEMES.get(badhaka_lord, ["General obstructions"])

        return BadhakaAnalysis(
            badhaka_house=badhaka_house,
            badhaka_sign=badhaka_sign.name.title(),
            badhaka_lord=badhaka_lord.value,
            obstruction_themes=themes,
        )

    def _calculate_scores(
        self,
        karakas: List[CharaKarakaInfo],
        atmakaraka: AtmakarakaAnalysis,
        arudha: ArudhaLagnaAnalysis,
        badhaka: BadhakaAnalysis,
    ) -> Dict[str, float]:
        """
        Calculate composite Jaimini scores.

        Returns:
            Dict with soul_clarity, career_alignment, public_image, obstruction scores
        """
        # Soul clarity: Based on AK strength and clarity
        soul_clarity = 50.0
        if atmakaraka.planet != "Unknown":
            # Higher degree AK = more mature soul
            soul_clarity = min(100, 50 + atmakaraka.degrees_in_sign * 1.5)

            # Bonus for benefic AK
            if atmakaraka.planet in ["Jupiter", "Venus", "Mercury", "Moon"]:
                soul_clarity = min(100, soul_clarity + 10)

        # Career alignment: Based on AK-AmK relationship
        career_alignment = 50.0
        if len(karakas) >= 2:
            ak = karakas[0]
            amk = karakas[1]

            # Check if AK and AmK are in friendly signs
            # Simple heuristic: closer degrees = more alignment
            degree_diff = abs(ak.degrees_in_sign - amk.degrees_in_sign)
            career_alignment = max(30, 80 - degree_diff * 2)

        # Public image strength: Based on Arudha position
        public_image = 50.0
        # Kendra positions (1,4,7,10) are strongest
        if arudha.house_from_lagna in [1, 4, 7, 10]:
            public_image = 80
        # Trikona positions (5,9) are also good
        elif arudha.house_from_lagna in [5, 9]:
            public_image = 70
        # Upachaya positions (3,6,11) grow with time
        elif arudha.house_from_lagna in [3, 6, 11]:
            public_image = 60
        # Dusthana positions (6,8,12) are challenging
        elif arudha.house_from_lagna in [8, 12]:
            public_image = 40

        # Obstruction level: Based on badhaka lord
        obstruction = 50.0
        # Malefic badhaka lords increase obstruction
        if badhaka.badhaka_lord in ["Saturn", "Mars", "Rahu", "Ketu"]:
            obstruction = 70
        elif badhaka.badhaka_lord == "Sun":
            obstruction = 60
        else:
            obstruction = 40

        return {
            "soul_clarity": soul_clarity,
            "career_alignment": career_alignment,
            "public_image": public_image,
            "obstruction": obstruction,
        }

    def _create_summary(
        self,
        atmakaraka: AtmakarakaAnalysis,
        karakamsha: KarakamshaAnalysis,
        scores: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Create investment-relevant Jaimini summary.

        Returns:
            Dict with key insights for talent assessment
        """
        # Determine soul archetype from AK planet
        soul_archetypes = {
            "Sun": "Leader & Authority",
            "Moon": "Nurturer & Connector",
            "Mars": "Warrior & Pioneer",
            "Mercury": "Communicator & Strategist",
            "Jupiter": "Teacher & Expander",
            "Venus": "Creator & Harmonizer",
            "Saturn": "Builder & Disciplinarian",
            "Rahu": "Innovator & Disruptor",
            "Ketu": "Mystic & Liberator",
        }

        soul_archetype = soul_archetypes.get(atmakaraka.planet, "Unknown")

        # Career suitability from Karakamsha
        return {
            "soul_archetype": soul_archetype,
            "life_theme": atmakaraka.life_theme,
            "career_direction": karakamsha.career_direction,
            "spiritual_path": karakamsha.spiritual_path,
            "key_strength": atmakaraka.strengths[0] if atmakaraka.strengths else "Self-awareness",
            "key_challenge": atmakaraka.challenges[0] if atmakaraka.challenges else "Self-improvement",
            "investment_insight": self._get_investment_insight(atmakaraka.planet, scores),
            "overall_jaimini_score": round(
                (scores["soul_clarity"] + scores["career_alignment"] + scores["public_image"] - scores["obstruction"] / 2) / 3,
                1
            ),
        }

    def _get_investment_insight(self, ak_planet: str, scores: Dict[str, float]) -> str:
        """Generate investment-relevant insight based on AK and scores."""
        insights = {
            "Sun": "Natural leader with authority. Strong execution but may need humility coaching.",
            "Moon": "Emotionally intelligent connector. Great for customer-facing roles.",
            "Mars": "High energy pioneer. Excellent for startups, may need conflict management.",
            "Mercury": "Sharp strategist and communicator. Ideal for business development.",
            "Jupiter": "Wise advisor and expander. Natural mentor, good for scaling organizations.",
            "Venus": "Creative harmonizer. Excellent for partnerships and brand building.",
            "Saturn": "Disciplined builder. Long-term vision, may be slow to start but reliable.",
        }

        base_insight = insights.get(ak_planet, "Unique profile requiring individual assessment.")

        # Add score-based modifier
        avg_score = (scores["soul_clarity"] + scores["career_alignment"]) / 2
        if avg_score > 70:
            return f"{base_insight} HIGH POTENTIAL - clear direction and alignment."
        elif avg_score > 50:
            return f"{base_insight} MODERATE POTENTIAL - good foundation with room for development."
        else:
            return f"{base_insight} DEVELOPING - needs mentorship and clarity building."
