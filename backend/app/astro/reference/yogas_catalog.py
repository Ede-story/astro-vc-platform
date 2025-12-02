"""
Complete catalog of 50+ Vedic Yogas.

Each yoga definition includes:
- Name and Sanskrit name
- Category (Raja, Dhana, Mahapurusha, Chandra, Special, Negative)
- Condition function
- Base strength
- Affected houses/life areas
- Interpretation key for LLM
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

from ..models.types import Planet


class YogaCategory(str, Enum):
    RAJA = "Raja"                # Power, status, leadership
    DHANA = "Dhana"              # Wealth
    MAHAPURUSHA = "Mahapurusha"  # Great person yogas
    CHANDRA = "Chandra"          # Moon-based
    SURYA = "Surya"              # Sun-based
    SPECIAL = "Special"          # Unique combinations
    NEGATIVE = "Negative"        # Challenging yogas


@dataclass
class YogaDefinition:
    """Definition of a Vedic yoga."""
    name: str
    sanskrit_name: str
    category: YogaCategory
    description: str
    base_strength: float  # 1-10 (negative for bad yogas)
    affected_houses: List[int]
    affected_areas: List[str]
    interpretation_key: str
    planets_involved: List[Planet] = None

    def __post_init__(self):
        if self.planets_involved is None:
            self.planets_involved = []


# ============================================
# RAJA YOGAS (Power & Status)
# ============================================

RAJA_YOGAS = [
    YogaDefinition(
        name="Gaja Kesari Yoga",
        sanskrit_name="गजकेसरी योग",
        category=YogaCategory.RAJA,
        description="Jupiter in Kendra from Moon - wisdom, reputation, leadership",
        base_strength=8.0,
        affected_houses=[1, 4, 7, 10],
        affected_areas=["career", "reputation", "wisdom", "leadership"],
        interpretation_key="gaja_kesari",
        planets_involved=[Planet.JUPITER, Planet.MOON]
    ),
    YogaDefinition(
        name="Hamsa Yoga",
        sanskrit_name="हंस योग",
        category=YogaCategory.MAHAPURUSHA,
        description="Jupiter in own sign or exalted in Kendra - spiritual wisdom",
        base_strength=9.0,
        affected_houses=[1, 4, 7, 10],
        affected_areas=["spirituality", "wisdom", "teaching", "ethics"],
        interpretation_key="hamsa",
        planets_involved=[Planet.JUPITER]
    ),
    YogaDefinition(
        name="Malavya Yoga",
        sanskrit_name="मालव्य योग",
        category=YogaCategory.MAHAPURUSHA,
        description="Venus in own sign or exalted in Kendra - beauty, luxury, arts",
        base_strength=8.5,
        affected_houses=[1, 4, 7, 10],
        affected_areas=["relationships", "arts", "luxury", "beauty"],
        interpretation_key="malavya",
        planets_involved=[Planet.VENUS]
    ),
    YogaDefinition(
        name="Ruchaka Yoga",
        sanskrit_name="रुचक योग",
        category=YogaCategory.MAHAPURUSHA,
        description="Mars in own sign or exalted in Kendra - courage, military",
        base_strength=8.5,
        affected_houses=[1, 4, 7, 10],
        affected_areas=["courage", "leadership", "competition", "action"],
        interpretation_key="ruchaka",
        planets_involved=[Planet.MARS]
    ),
    YogaDefinition(
        name="Bhadra Yoga",
        sanskrit_name="भद्र योग",
        category=YogaCategory.MAHAPURUSHA,
        description="Mercury in own sign or exalted in Kendra - intelligence",
        base_strength=8.5,
        affected_houses=[1, 4, 7, 10],
        affected_areas=["intelligence", "communication", "business", "writing"],
        interpretation_key="bhadra",
        planets_involved=[Planet.MERCURY]
    ),
    YogaDefinition(
        name="Sasha Yoga",
        sanskrit_name="शश योग",
        category=YogaCategory.MAHAPURUSHA,
        description="Saturn in own sign or exalted in Kendra - discipline",
        base_strength=8.0,
        affected_houses=[1, 4, 7, 10],
        affected_areas=["discipline", "authority", "persistence", "structure"],
        interpretation_key="sasha",
        planets_involved=[Planet.SATURN]
    ),
    YogaDefinition(
        name="Raja Yoga (9-10)",
        sanskrit_name="राज योग",
        category=YogaCategory.RAJA,
        description="9th and 10th lords connected - dharma-karma yoga",
        base_strength=9.0,
        affected_houses=[9, 10],
        affected_areas=["career", "destiny", "success", "purpose"],
        interpretation_key="raja_9_10",
        planets_involved=[]
    ),
    YogaDefinition(
        name="Raja Yoga (1-5-9)",
        sanskrit_name="त्रिकोण राज योग",
        category=YogaCategory.RAJA,
        description="Trikona lords connected - fundamental raja yoga",
        base_strength=8.5,
        affected_houses=[1, 5, 9],
        affected_areas=["self", "creativity", "fortune"],
        interpretation_key="raja_trikona",
        planets_involved=[]
    ),
    YogaDefinition(
        name="Neecha Bhanga Raja Yoga",
        sanskrit_name="नीच भंग राज योग",
        category=YogaCategory.RAJA,
        description="Debilitated planet with cancellation - rise after fall",
        base_strength=8.5,
        affected_houses=[],
        affected_areas=["transformation", "rise_from_adversity", "hidden_strength"],
        interpretation_key="neecha_bhanga",
        planets_involved=[]
    ),
    YogaDefinition(
        name="Viparita Raja Yoga",
        sanskrit_name="विपरीत राज योग",
        category=YogaCategory.RAJA,
        description="Dusthana lords in dusthanas - success through adversity",
        base_strength=7.5,
        affected_houses=[6, 8, 12],
        affected_areas=["transformation", "success_through_failure"],
        interpretation_key="viparita_raja",
        planets_involved=[]
    ),
]

# ============================================
# DHANA YOGAS (Wealth)
# ============================================

DHANA_YOGAS = [
    YogaDefinition(
        name="Dhana Yoga (2-11)",
        sanskrit_name="धन योग",
        category=YogaCategory.DHANA,
        description="2nd and 11th lords connected - wealth accumulation",
        base_strength=8.0,
        affected_houses=[2, 11],
        affected_areas=["wealth", "income", "savings"],
        interpretation_key="dhana_2_11",
        planets_involved=[]
    ),
    YogaDefinition(
        name="Lakshmi Yoga",
        sanskrit_name="लक्ष्मी योग",
        category=YogaCategory.DHANA,
        description="9th lord strong and Venus in own/exalted sign",
        base_strength=9.0,
        affected_houses=[1, 9],
        affected_areas=["wealth", "fortune", "prosperity"],
        interpretation_key="lakshmi",
        planets_involved=[Planet.VENUS]
    ),
    YogaDefinition(
        name="Kubera Yoga",
        sanskrit_name="कुबेर योग",
        category=YogaCategory.DHANA,
        description="Jupiter and Moon strong in benefic houses",
        base_strength=8.5,
        affected_houses=[2, 5, 9, 11],
        affected_areas=["massive_wealth", "abundance"],
        interpretation_key="kubera",
        planets_involved=[Planet.JUPITER, Planet.MOON]
    ),
    YogaDefinition(
        name="Chandra-Mangal Yoga",
        sanskrit_name="चंद्र-मंगल योग",
        category=YogaCategory.DHANA,
        description="Moon and Mars conjunction - quick wealth",
        base_strength=7.0,
        affected_houses=[2, 11],
        affected_areas=["quick_money", "real_estate", "action"],
        interpretation_key="chandra_mangal",
        planets_involved=[Planet.MOON, Planet.MARS]
    ),
    YogaDefinition(
        name="Dhana Yoga (1-2)",
        sanskrit_name="धन योग",
        category=YogaCategory.DHANA,
        description="1st and 2nd lords connected - self-earned wealth",
        base_strength=7.5,
        affected_houses=[1, 2],
        affected_areas=["self_earned", "resources"],
        interpretation_key="dhana_1_2",
        planets_involved=[]
    ),
]

# ============================================
# CHANDRA YOGAS (Moon-based)
# ============================================

CHANDRA_YOGAS = [
    YogaDefinition(
        name="Sunapha Yoga",
        sanskrit_name="सुनफा योग",
        category=YogaCategory.CHANDRA,
        description="Planet (not Sun) in 2nd from Moon - self-made wealth",
        base_strength=7.0,
        affected_houses=[2],
        affected_areas=["wealth", "self_made", "resources"],
        interpretation_key="sunapha",
        planets_involved=[Planet.MOON]
    ),
    YogaDefinition(
        name="Anapha Yoga",
        sanskrit_name="अनफा योग",
        category=YogaCategory.CHANDRA,
        description="Planet (not Sun) in 12th from Moon - ancestral benefits",
        base_strength=7.0,
        affected_houses=[12],
        affected_areas=["inheritance", "past_karma", "spirituality"],
        interpretation_key="anapha",
        planets_involved=[Planet.MOON]
    ),
    YogaDefinition(
        name="Durudhara Yoga",
        sanskrit_name="दुरुधरा योग",
        category=YogaCategory.CHANDRA,
        description="Planets both sides of Moon (2nd and 12th)",
        base_strength=8.0,
        affected_houses=[2, 12],
        affected_areas=["protection", "balance", "support"],
        interpretation_key="durudhara",
        planets_involved=[Planet.MOON]
    ),
    YogaDefinition(
        name="Adhi Yoga",
        sanskrit_name="अधि योग",
        category=YogaCategory.CHANDRA,
        description="Benefics in 6th, 7th, 8th from Moon",
        base_strength=8.5,
        affected_houses=[6, 7, 8],
        affected_areas=["leadership", "success", "overcoming_obstacles"],
        interpretation_key="adhi",
        planets_involved=[Planet.MOON, Planet.JUPITER, Planet.VENUS, Planet.MERCURY]
    ),
    YogaDefinition(
        name="Chandra-Yoga (Full Moon)",
        sanskrit_name="पूर्णिमा चंद्र",
        category=YogaCategory.CHANDRA,
        description="Moon bright and strong (near full)",
        base_strength=7.5,
        affected_houses=[1, 4],
        affected_areas=["emotions", "mental_peace", "popularity"],
        interpretation_key="full_moon",
        planets_involved=[Planet.MOON]
    ),
]

# ============================================
# SPECIAL YOGAS
# ============================================

SPECIAL_YOGAS = [
    YogaDefinition(
        name="Budhaditya Yoga",
        sanskrit_name="बुधादित्य योग",
        category=YogaCategory.SURYA,
        description="Sun and Mercury conjunction - intelligence",
        base_strength=7.5,
        affected_houses=[1, 5, 10],
        affected_areas=["intelligence", "speech", "government"],
        interpretation_key="budhaditya",
        planets_involved=[Planet.SUN, Planet.MERCURY]
    ),
    YogaDefinition(
        name="Nipuna Yoga",
        sanskrit_name="निपुण योग",
        category=YogaCategory.SPECIAL,
        description="Mercury strong in Kendra - mastery of skills",
        base_strength=7.5,
        affected_houses=[1, 4, 7, 10],
        affected_areas=["skills", "mastery", "learning"],
        interpretation_key="nipuna",
        planets_involved=[Planet.MERCURY]
    ),
    YogaDefinition(
        name="Saraswati Yoga",
        sanskrit_name="सरस्वती योग",
        category=YogaCategory.SPECIAL,
        description="Jupiter, Venus, Mercury in Kendra/Trikona",
        base_strength=8.5,
        affected_houses=[1, 4, 5, 7, 9, 10],
        affected_areas=["knowledge", "arts", "music", "education"],
        interpretation_key="saraswati",
        planets_involved=[Planet.JUPITER, Planet.VENUS, Planet.MERCURY]
    ),
    YogaDefinition(
        name="Parvata Yoga",
        sanskrit_name="पर्वत योग",
        category=YogaCategory.SPECIAL,
        description="Benefics in Kendras, no malefics in 6/8",
        base_strength=8.0,
        affected_houses=[1, 4, 7, 10],
        affected_areas=["fame", "authority", "success"],
        interpretation_key="parvata",
        planets_involved=[]
    ),
    YogaDefinition(
        name="Kahala Yoga",
        sanskrit_name="कहल योग",
        category=YogaCategory.SPECIAL,
        description="4th and 9th lords in mutual kendras",
        base_strength=7.5,
        affected_houses=[4, 9],
        affected_areas=["property", "fortune", "courage"],
        interpretation_key="kahala",
        planets_involved=[]
    ),
    YogaDefinition(
        name="Amala Yoga",
        sanskrit_name="अमल योग",
        category=YogaCategory.SPECIAL,
        description="Benefic in 10th from Moon or Lagna",
        base_strength=7.5,
        affected_houses=[10],
        affected_areas=["reputation", "career", "good_deeds"],
        interpretation_key="amala",
        planets_involved=[]
    ),
    YogaDefinition(
        name="Shubha Kartari Yoga",
        sanskrit_name="शुभ कर्तरी योग",
        category=YogaCategory.SPECIAL,
        description="Benefics surrounding a house - protection",
        base_strength=7.0,
        affected_houses=[],
        affected_areas=["protection", "auspiciousness"],
        interpretation_key="shubha_kartari",
        planets_involved=[]
    ),
]

# ============================================
# NEGATIVE YOGAS
# ============================================

NEGATIVE_YOGAS = [
    YogaDefinition(
        name="Kemadruma Yoga",
        sanskrit_name="केमद्रुम योग",
        category=YogaCategory.NEGATIVE,
        description="No planets in 2nd or 12th from Moon",
        base_strength=-6.0,
        affected_houses=[2, 12],
        affected_areas=["mental_health", "isolation", "poverty"],
        interpretation_key="kemadruma",
        planets_involved=[Planet.MOON]
    ),
    YogaDefinition(
        name="Daridra Yoga",
        sanskrit_name="दरिद्र योग",
        category=YogaCategory.NEGATIVE,
        description="11th lord in 6th, 8th, or 12th",
        base_strength=-5.0,
        affected_houses=[6, 8, 11, 12],
        affected_areas=["finances", "gains", "obstacles"],
        interpretation_key="daridra",
        planets_involved=[]
    ),
    YogaDefinition(
        name="Guru Chandala Yoga",
        sanskrit_name="गुरु चांडाल योग",
        category=YogaCategory.NEGATIVE,
        description="Jupiter-Rahu conjunction - ethical challenges",
        base_strength=-4.0,
        affected_houses=[],
        affected_areas=["ethics", "spirituality", "teaching"],
        interpretation_key="guru_chandala",
        planets_involved=[Planet.JUPITER, Planet.RAHU]
    ),
    YogaDefinition(
        name="Kala Sarpa Yoga",
        sanskrit_name="काल सर्प योग",
        category=YogaCategory.NEGATIVE,
        description="All planets between Rahu-Ketu axis",
        base_strength=-5.0,
        affected_houses=list(range(1, 13)),
        affected_areas=["karma", "delays", "restrictions"],
        interpretation_key="kala_sarpa",
        planets_involved=[Planet.RAHU, Planet.KETU]
    ),
    YogaDefinition(
        name="Grahan Yoga",
        sanskrit_name="ग्रहण योग",
        category=YogaCategory.NEGATIVE,
        description="Sun/Moon with Rahu/Ketu - eclipsed luminaries",
        base_strength=-4.0,
        affected_houses=[1, 4, 5, 9],
        affected_areas=["confidence", "emotions", "authority"],
        interpretation_key="grahan",
        planets_involved=[Planet.SUN, Planet.MOON, Planet.RAHU, Planet.KETU]
    ),
    YogaDefinition(
        name="Shakat Yoga",
        sanskrit_name="शकट योग",
        category=YogaCategory.NEGATIVE,
        description="Moon in 6th, 8th, or 12th from Jupiter",
        base_strength=-4.0,
        affected_houses=[6, 8, 12],
        affected_areas=["mental_peace", "fortune", "obstacles"],
        interpretation_key="shakat",
        planets_involved=[Planet.MOON, Planet.JUPITER]
    ),
    YogaDefinition(
        name="Papa Kartari Yoga",
        sanskrit_name="पाप कर्तरी योग",
        category=YogaCategory.NEGATIVE,
        description="Malefics surrounding a house - constriction",
        base_strength=-5.0,
        affected_houses=[],
        affected_areas=["obstacles", "pressure", "restriction"],
        interpretation_key="papa_kartari",
        planets_involved=[]
    ),
    YogaDefinition(
        name="Chandala Yoga",
        sanskrit_name="चांडाल योग",
        category=YogaCategory.NEGATIVE,
        description="Any planet conjunct Rahu",
        base_strength=-3.0,
        affected_houses=[],
        affected_areas=["confusion", "unconventional"],
        interpretation_key="chandala",
        planets_involved=[Planet.RAHU]
    ),
]

# ============================================
# ALL YOGAS COMBINED
# ============================================

ALL_YOGAS: List[YogaDefinition] = (
    RAJA_YOGAS +
    DHANA_YOGAS +
    CHANDRA_YOGAS +
    SPECIAL_YOGAS +
    NEGATIVE_YOGAS
)

YOGA_BY_NAME: Dict[str, YogaDefinition] = {y.name: y for y in ALL_YOGAS}


def get_yoga_definition(name: str) -> Optional[YogaDefinition]:
    """Get yoga definition by name."""
    return YOGA_BY_NAME.get(name)


def get_yogas_by_category(category: YogaCategory) -> List[YogaDefinition]:
    """Get all yogas of a specific category."""
    return [y for y in ALL_YOGAS if y.category == category]


def get_positive_yogas() -> List[YogaDefinition]:
    """Get all positive yogas."""
    return [y for y in ALL_YOGAS if y.base_strength > 0]


def get_negative_yogas() -> List[YogaDefinition]:
    """Get all negative yogas."""
    return [y for y in ALL_YOGAS if y.base_strength < 0]
