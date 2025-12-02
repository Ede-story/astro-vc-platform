"""
Core Type Definitions for Astro Brain

Enums and type definitions for Vedic astrology calculations.
These are used throughout all 12 stages of the calculator.
"""

from enum import Enum, IntEnum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


class Planet(str, Enum):
    """Nine Vedic planets (Navagraha)"""
    SUN = "Sun"
    MOON = "Moon"
    MARS = "Mars"
    MERCURY = "Mercury"
    JUPITER = "Jupiter"
    VENUS = "Venus"
    SATURN = "Saturn"
    RAHU = "Rahu"      # North Node
    KETU = "Ketu"      # South Node

    @classmethod
    def from_string(cls, name: str) -> "Planet":
        """Convert string to Planet enum (case-insensitive)"""
        name_upper = name.upper()
        for planet in cls:
            if planet.value.upper() == name_upper:
                return planet
        raise ValueError(f"Unknown planet: {name}")

    @property
    def is_benefic(self) -> bool:
        """Natural benefics"""
        return self in [Planet.JUPITER, Planet.VENUS, Planet.MERCURY, Planet.MOON]

    @property
    def is_malefic(self) -> bool:
        """Natural malefics"""
        return self in [Planet.SUN, Planet.MARS, Planet.SATURN, Planet.RAHU, Planet.KETU]

    @property
    def is_shadow(self) -> bool:
        """Shadow planets (nodes)"""
        return self in [Planet.RAHU, Planet.KETU]


class Zodiac(IntEnum):
    """12 Zodiac signs (1-indexed as in Vedic tradition)"""
    ARIES = 1
    TAURUS = 2
    GEMINI = 3
    CANCER = 4
    LEO = 5
    VIRGO = 6
    LIBRA = 7
    SCORPIO = 8
    SAGITTARIUS = 9
    CAPRICORN = 10
    AQUARIUS = 11
    PISCES = 12

    @classmethod
    def from_string(cls, name: str) -> "Zodiac":
        """Convert string to Zodiac enum (case-insensitive)"""
        name_upper = name.upper()
        for sign in cls:
            if sign.name == name_upper:
                return sign
        raise ValueError(f"Unknown sign: {name}")

    @classmethod
    def from_degree(cls, degree: float) -> "Zodiac":
        """Get zodiac sign from absolute degree (0-360)"""
        sign_num = int(degree / 30) + 1
        if sign_num > 12:
            sign_num = 12
        return cls(sign_num)

    @property
    def element(self) -> str:
        """Fire, Earth, Air, Water"""
        elements = {
            1: "Fire", 2: "Earth", 3: "Air", 4: "Water",
            5: "Fire", 6: "Earth", 7: "Air", 8: "Water",
            9: "Fire", 10: "Earth", 11: "Air", 12: "Water"
        }
        return elements[self.value]

    @property
    def modality(self) -> str:
        """Cardinal (Movable), Fixed, Mutable (Dual)"""
        modalities = {
            1: "Movable", 4: "Movable", 7: "Movable", 10: "Movable",
            2: "Fixed", 5: "Fixed", 8: "Fixed", 11: "Fixed",
            3: "Dual", 6: "Dual", 9: "Dual", 12: "Dual"
        }
        return modalities[self.value]

    @property
    def is_odd(self) -> bool:
        """Odd signs (masculine): Aries, Gemini, Leo, Libra, Sagittarius, Aquarius"""
        return self.value % 2 == 1

    @property
    def is_even(self) -> bool:
        """Even signs (feminine): Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces"""
        return self.value % 2 == 0


class Dignity(str, Enum):
    """Planetary dignity states (ordered from strongest to weakest)"""
    EXALTED = "Exalted"              # Highest strength
    MOOLATRIKONA = "Moolatrikona"    # Very strong (own sign special zone)
    OWN_SIGN = "Own Sign"            # Strong (ruling sign)
    GREAT_FRIEND = "Great Friend"    # Good placement
    FRIEND = "Friend"                # Supportive placement
    NEUTRAL = "Neutral"              # Neither good nor bad
    ENEMY = "Enemy"                  # Weak placement
    GREAT_ENEMY = "Great Enemy"      # Very weak
    DEBILITATED = "Debilitated"      # Lowest strength

    @property
    def strength_score(self) -> float:
        """Numeric strength score (1-9)"""
        scores = {
            Dignity.EXALTED: 9.0,
            Dignity.MOOLATRIKONA: 8.0,
            Dignity.OWN_SIGN: 7.0,
            Dignity.GREAT_FRIEND: 6.0,
            Dignity.FRIEND: 5.0,
            Dignity.NEUTRAL: 4.0,
            Dignity.ENEMY: 3.0,
            Dignity.GREAT_ENEMY: 2.0,
            Dignity.DEBILITATED: 1.0,
        }
        return scores[self]


class House(IntEnum):
    """12 Astrological houses (bhavas)"""
    FIRST = 1      # Lagna - Self, body, personality
    SECOND = 2     # Wealth, speech, family
    THIRD = 3      # Siblings, courage, communication
    FOURTH = 4     # Mother, home, emotions
    FIFTH = 5      # Children, creativity, romance
    SIXTH = 6      # Enemies, disease, service
    SEVENTH = 7    # Marriage, partnerships
    EIGHTH = 8     # Death, transformation, occult
    NINTH = 9      # Dharma, luck, father, higher learning
    TENTH = 10     # Career, status, authority
    ELEVENTH = 11  # Gains, friends, aspirations
    TWELFTH = 12   # Losses, moksha, foreign lands

    @property
    def is_kendra(self) -> bool:
        """Angular houses: 1, 4, 7, 10 (strongest for planets)"""
        return self.value in [1, 4, 7, 10]

    @property
    def is_trikona(self) -> bool:
        """Trinal houses: 1, 5, 9 (dharma houses)"""
        return self.value in [1, 5, 9]

    @property
    def is_dusthana(self) -> bool:
        """Difficult houses: 6, 8, 12"""
        return self.value in [6, 8, 12]

    @property
    def is_trishadaya(self) -> bool:
        """Upachaya houses: 3, 6, 10, 11 (improve with time)"""
        return self.value in [3, 6, 10, 11]

    @property
    def is_maraka(self) -> bool:
        """Maraka (death-dealing) houses: 2, 7"""
        return self.value in [2, 7]

    @property
    def significance(self) -> str:
        """Primary significance of the house"""
        significances = {
            1: "Self, Body, Personality",
            2: "Wealth, Speech, Family",
            3: "Siblings, Courage, Will",
            4: "Mother, Home, Comfort",
            5: "Children, Creativity, Intelligence",
            6: "Enemies, Health, Service",
            7: "Marriage, Partnerships",
            8: "Transformation, Occult, Longevity",
            9: "Fortune, Dharma, Higher Learning",
            10: "Career, Status, Actions",
            11: "Gains, Friends, Aspirations",
            12: "Losses, Liberation, Foreign"
        }
        return significances[self.value]


class Nakshatra(str, Enum):
    """27 Lunar Mansions"""
    ASHWINI = "Ashwini"
    BHARANI = "Bharani"
    KRITTIKA = "Krittika"
    ROHINI = "Rohini"
    MRIGASHIRA = "Mrigashira"
    ARDRA = "Ardra"
    PUNARVASU = "Punarvasu"
    PUSHYA = "Pushya"
    ASHLESHA = "Ashlesha"
    MAGHA = "Magha"
    PURVA_PHALGUNI = "Purva Phalguni"
    UTTARA_PHALGUNI = "Uttara Phalguni"
    HASTA = "Hasta"
    CHITRA = "Chitra"
    SWATI = "Swati"
    VISHAKHA = "Vishakha"
    ANURADHA = "Anuradha"
    JYESHTHA = "Jyeshtha"
    MULA = "Mula"
    PURVA_ASHADHA = "Purva Ashadha"
    UTTARA_ASHADHA = "Uttara Ashadha"
    SHRAVANA = "Shravana"
    DHANISHTA = "Dhanishta"
    SHATABHISHA = "Shatabhisha"
    PURVA_BHADRAPADA = "Purva Bhadrapada"
    UTTARA_BHADRAPADA = "Uttara Bhadrapada"
    REVATI = "Revati"

    @classmethod
    def from_string(cls, name: str) -> "Nakshatra":
        """Convert string to Nakshatra enum (handles various spellings)"""
        name_clean = name.strip().replace(" ", "_").upper()
        for nakshatra in cls:
            if nakshatra.value.replace(" ", "_").upper() == name_clean:
                return nakshatra
        # Fallback: partial match
        for nakshatra in cls:
            if name_clean in nakshatra.value.upper().replace(" ", "_"):
                return nakshatra
        raise ValueError(f"Unknown nakshatra: {name}")


class NakshatraPada(IntEnum):
    """Four quarters of each nakshatra (3°20' each)"""
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4


class Karaka(str, Enum):
    """Chara Karakas (7-planet Jaimini system)"""
    ATMA_KARAKA = "AK"        # Soul significator (highest degree)
    AMATYA_KARAKA = "AmK"     # Minister, career
    BHRATRI_KARAKA = "BK"     # Siblings, courage
    MATRI_KARAKA = "MK"       # Mother, mind
    PITRI_KARAKA = "PK"       # Father, fortune
    GNATI_KARAKA = "GK"       # Enemies, obstacles
    DARA_KARAKA = "DK"        # Spouse (lowest degree)


class GanaType(str, Enum):
    """Three Gana (temperament) types from Nakshatra classification"""
    DEVA = "Deva"           # Divine, sattvic, spiritual
    MANUSHYA = "Manushya"   # Human, rajasic, worldly
    RAKSHASA = "Rakshasa"   # Demonic, tamasic, intense


class PersonalityArchetype(str, Enum):
    """12 Personality Archetypes based on Sun-Moon-Lagna Gana combinations"""
    LIGHT_BEARER = "Светоносец"                    # Deva-Deva-Deva
    NOBLE_PRACTITIONER = "Благородный Практик"     # Deva-Deva-Manushya
    HARMONIZER = "Гармонизатор"                    # Deva-Manushya-Deva
    WORLD_BUILDER = "Строитель Мира"               # Manushya-Manushya-Manushya
    TRANSFORMER = "Трансформатор"                  # Rakshasa-Rakshasa-Rakshasa
    LIGHT_WARRIOR = "Воин Света"                   # Rakshasa-Deva-Manushya
    REFORMER = "Реформатор"                        # Manushya-Rakshasa-Deva
    SPIRITUAL_WARRIOR = "Духовный Воин"            # Deva-Rakshasa-Manushya
    WISE_DESTROYER = "Мудрый Разрушитель"          # Rakshasa-Deva-Deva
    PRACTICAL_IDEALIST = "Практичный Идеалист"     # Deva-Manushya-Manushya
    INTENSE_CREATOR = "Интенсивный Созидатель"     # Manushya-Rakshasa-Rakshasa
    DIVINE_TRANSFORMER = "Божественный Трансформатор"  # Deva-Rakshasa-Deva
    MIXED = "Смешанный"                            # Other combinations

    @property
    def significance(self) -> str:
        """Primary significance of the karaka"""
        significances = {
            Karaka.ATMA_KARAKA: "Soul, Self, Destiny",
            Karaka.AMATYA_KARAKA: "Career, Status, Mind",
            Karaka.BHRATRI_KARAKA: "Siblings, Courage, Efforts",
            Karaka.MATRI_KARAKA: "Mother, Education, Property",
            Karaka.PITRI_KARAKA: "Father, Children, Fortune",
            Karaka.GNATI_KARAKA: "Enemies, Disease, Obstacles",
            Karaka.DARA_KARAKA: "Spouse, Partnerships",
        }
        return significances[self]


class DashaLevel(str, Enum):
    """Vimshottari Dasha levels"""
    MAHADASHA = "MD"      # Major period (varies by planet)
    ANTARDASHA = "AD"     # Sub-period
    PRATYANTARDASHA = "PD"  # Sub-sub-period


class VargaCode(str, Enum):
    """20 Divisional charts used in Vedic astrology"""
    D1 = "D1"      # Rashi - Main chart
    D2 = "D2"      # Hora - Wealth
    D3 = "D3"      # Drekkana - Siblings, courage
    D4 = "D4"      # Chaturthamsha - Fortune, property
    D5 = "D5"      # Panchamsha - Spiritual merit
    D7 = "D7"      # Saptamsha - Children
    D9 = "D9"      # Navamsha - Spouse, dharma (most important)
    D10 = "D10"    # Dashamsha - Career
    D11 = "D11"    # Rudramsha - Wealth acquisition
    D12 = "D12"    # Dwadashamsha - Parents
    D16 = "D16"    # Shodashamsha - Vehicles, luxury
    D20 = "D20"    # Vimsamsha - Spiritual progress
    D24 = "D24"    # Chaturvimsamsha - Education, learning
    D27 = "D27"    # Bhamsha - Physical strength
    D30 = "D30"    # Trimsamsha - Misfortunes
    D40 = "D40"    # Khavedamsha - Auspicious effects
    D45 = "D45"    # Akshavedamsha - General wellbeing
    D60 = "D60"    # Shashtiamsha - Past life karma (most subtle)

    @property
    def significance(self) -> str:
        """Primary significance of the varga"""
        significances = {
            VargaCode.D1: "Main Chart, General Life",
            VargaCode.D2: "Wealth, Resources",
            VargaCode.D3: "Siblings, Courage",
            VargaCode.D4: "Fortune, Property",
            VargaCode.D5: "Spiritual Merit",
            VargaCode.D7: "Children, Progeny",
            VargaCode.D9: "Spouse, Dharma, Soul",
            VargaCode.D10: "Career, Status",
            VargaCode.D11: "Wealth Acquisition",
            VargaCode.D12: "Parents",
            VargaCode.D16: "Vehicles, Luxury",
            VargaCode.D20: "Spiritual Progress",
            VargaCode.D24: "Education, Learning",
            VargaCode.D27: "Physical Strength",
            VargaCode.D30: "Misfortunes, Evil",
            VargaCode.D40: "Auspicious Effects",
            VargaCode.D45: "General Wellbeing",
            VargaCode.D60: "Past Life Karma",
        }
        return significances[self]


# Type aliases for clarity
Degrees = float  # 0-360 for absolute, 0-30 for relative
HouseNumber = int  # 1-12
SignNumber = int  # 1-12

# House category constants
KENDRA_HOUSES = [1, 4, 7, 10]       # Angular houses
TRIKONA_HOUSES = [1, 5, 9]          # Trinal houses
DUSTHANA_HOUSES = [6, 8, 12]        # Difficult houses
UPACHAYA_HOUSES = [3, 6, 10, 11]    # Improving houses
MARAKA_HOUSES = [2, 7]              # Death-dealing houses

# Zodiac order list for calculations
ZODIAC_ORDER = [
    Zodiac.ARIES, Zodiac.TAURUS, Zodiac.GEMINI, Zodiac.CANCER,
    Zodiac.LEO, Zodiac.VIRGO, Zodiac.LIBRA, Zodiac.SCORPIO,
    Zodiac.SAGITTARIUS, Zodiac.CAPRICORN, Zodiac.AQUARIUS, Zodiac.PISCES
]


@dataclass
class NakshatraInfo:
    """Detailed nakshatra information"""
    name: Nakshatra
    pada: NakshatraPada
    lord: Planet
    degrees_in_nakshatra: Degrees  # 0-13.333...


@dataclass
class AscendantInfo:
    """Ascendant (Lagna) details"""
    sign: Zodiac
    degree: Degrees  # Degree within sign (0-30)
    nakshatra: NakshatraInfo
    lord: Planet


@dataclass
class DashaInfo:
    """Vimshottari Dasha period information"""
    level: DashaLevel
    planet: Planet
    start_date: str  # ISO format
    end_date: str
    duration_years: float


@dataclass
class YogaFound:
    """Detected yoga combination"""
    name: str
    category: str  # Raja, Dhana, Special, Negative
    planets_involved: List[Planet]
    houses_involved: List[House]
    strength: str  # HIGH, MEDIUM, LOW
    description: str


@dataclass
class NeechaBhanga:
    """Debilitation cancellation analysis"""
    debilitated_planet: Planet
    cancellation_type: str
    cancelling_planet: Optional[Planet]
    strength: str  # FULL, PARTIAL


@dataclass
class ViparitaRaja:
    """Viparita Raja Yoga (success through adversity)"""
    dusthana_lord: Planet
    dusthana_house: House
    placed_in: House
    strength: str


@dataclass
class LifeAreaAnalysis:
    """Analysis of a specific life area"""
    area_name: str
    houses_analyzed: List[House]
    vargas_analyzed: List[VargaCode]
    strength_score: float  # 0-100
    key_planets: List[Planet]
    key_findings: List[str]
    timing_hints: List[str]


@dataclass
class FinalScores:
    """Final calculated scores for talent assessment"""
    leadership_potential: float    # 0-100
    creativity_index: float        # 0-100
    analytical_ability: float      # 0-100
    emotional_intelligence: float  # 0-100
    entrepreneurship_score: float  # 0-100
    wealth_potential: float        # 0-100
    resilience: float              # 0-100
    risk_tolerance: float          # 0-100
    talent_score: float            # 0-100 (weighted composite)
    watchlist_tier: str            # A+, A, B, C
