"""
Jaimini Astrology Reference Data

Contains reference tables for the Jaimini system:
- Atmakaraka meanings (soul lessons per planet)
- Karakamsha meanings (life purpose per sign)
- Badhaka rules (obstruction houses)
- Sign modality mapping
"""

from typing import Dict, List
from dataclasses import dataclass
from ..models.types import Planet, Zodiac


# =============================================================================
# ATMAKARAKA MEANINGS
# Soul significator reveals the soul's primary lesson and karmic path
# =============================================================================

@dataclass
class AtmakarakaMeaning:
    """Meaning when a planet becomes Atmakaraka (soul significator)"""
    soul_lesson: str           # Primary karmic lesson
    karmic_trap: str           # Main obstacle to overcome
    spiritual_path: str        # Path to spiritual growth
    life_theme: str            # Overall life theme
    strengths: List[str]       # Natural talents
    challenges: List[str]      # Areas requiring work


ATMAKARAKA_MEANINGS: Dict[Planet, AtmakarakaMeaning] = {
    Planet.SUN: AtmakarakaMeaning(
        soul_lesson="Learning humility while maintaining authentic self-expression",
        karmic_trap="Ego inflation, need for recognition overshadowing purpose",
        spiritual_path="Service leadership, shining light for others without attachment",
        life_theme="Identity, authority, and finding one's true purpose",
        strengths=["Natural leadership", "Strong willpower", "Creative vision", "Courage"],
        challenges=["Pride", "Stubbornness", "Need for approval", "Dominating others"]
    ),

    Planet.MOON: AtmakarakaMeaning(
        soul_lesson="Emotional mastery and nurturing without attachment",
        karmic_trap="Emotional dependency, mood swings controlling decisions",
        spiritual_path="Compassionate detachment, serving through emotional wisdom",
        life_theme="Emotions, motherhood, inner peace, and public connection",
        strengths=["Emotional intelligence", "Intuition", "Nurturing ability", "Adaptability"],
        challenges=["Mood instability", "Over-sensitivity", "Attachment", "Indecision"]
    ),

    Planet.MARS: AtmakarakaMeaning(
        soul_lesson="Channeling aggression into righteous action",
        karmic_trap="Anger and impulsivity destroying relationships",
        spiritual_path="Warrior of dharma, protective force without violence",
        life_theme="Action, courage, competition, and protection",
        strengths=["Courage", "Initiative", "Physical energy", "Decisiveness"],
        challenges=["Anger", "Impatience", "Aggression", "Recklessness"]
    ),

    Planet.MERCURY: AtmakarakaMeaning(
        soul_lesson="Using intelligence for truth rather than manipulation",
        karmic_trap="Overthinking, using words to deceive or manipulate",
        spiritual_path="Sacred communication, teaching divine wisdom",
        life_theme="Communication, learning, commerce, and adaptability",
        strengths=["Intelligence", "Communication skills", "Analytical mind", "Versatility"],
        challenges=["Nervousness", "Duplicity", "Scattered energy", "Over-rationalization"]
    ),

    Planet.JUPITER: AtmakarakaMeaning(
        soul_lesson="True wisdom versus superficial knowledge",
        karmic_trap="Spiritual pride, preaching without practicing",
        spiritual_path="Humble teacher, embodying rather than just knowing truth",
        life_theme="Wisdom, expansion, teaching, and spiritual growth",
        strengths=["Wisdom", "Optimism", "Teaching ability", "Ethical foundation"],
        challenges=["Over-expansion", "Dogmatism", "Complacency", "False optimism"]
    ),

    Planet.VENUS: AtmakarakaMeaning(
        soul_lesson="Transcending sensual attachment while appreciating beauty",
        karmic_trap="Addiction to pleasure, relationships based on need",
        spiritual_path="Divine love, seeing beauty as reflection of the absolute",
        life_theme="Love, relationships, beauty, and material comfort",
        strengths=["Artistic sense", "Charm", "Diplomacy", "Appreciation of beauty"],
        challenges=["Indulgence", "Vanity", "Dependency", "Material attachment"]
    ),

    Planet.SATURN: AtmakarakaMeaning(
        soul_lesson="Accepting responsibility and limitations with grace",
        karmic_trap="Depression, rigidity, avoiding karma through escapism",
        spiritual_path="Karma yogi, working without attachment to results",
        life_theme="Discipline, responsibility, time, and karma",
        strengths=["Discipline", "Patience", "Endurance", "Practical wisdom"],
        challenges=["Depression", "Fear", "Rigidity", "Isolation"]
    ),

    Planet.RAHU: AtmakarakaMeaning(
        soul_lesson="Discerning true desires from illusory obsessions",
        karmic_trap="Endless craving, never satisfied with achievements",
        spiritual_path="Transforming worldly ambition into spiritual aspiration",
        life_theme="Ambition, unconventional paths, and breaking boundaries",
        strengths=["Ambition", "Innovation", "Risk-taking", "Breaking conventions"],
        challenges=["Obsession", "Deception", "Confusion", "Insatiability"]
    ),

    Planet.KETU: AtmakarakaMeaning(
        soul_lesson="Integrating spiritual insight with worldly engagement",
        karmic_trap="Excessive detachment, spiritual bypassing of duties",
        spiritual_path="Enlightened action, wisdom applied to material world",
        life_theme="Liberation, spirituality, and transcendence",
        strengths=["Spiritual insight", "Detachment", "Intuition", "Healing ability"],
        challenges=["Confusion", "Neglect of material duties", "Escapism", "Self-doubt"]
    ),
}


# =============================================================================
# KARAKAMSHA MEANINGS
# Atmakaraka's Navamsha position (D9) reveals life purpose and spiritual path
# =============================================================================

@dataclass
class KarakamshaMeaning:
    """Meaning of Atmakaraka's placement in Navamsha (Karakamsha)"""
    life_purpose: str          # Primary life direction
    career_direction: str      # Professional inclinations
    spiritual_path: str        # Spiritual development path
    key_themes: List[str]      # Important life themes


KARAKAMSHA_MEANINGS: Dict[Zodiac, KarakamshaMeaning] = {
    Zodiac.ARIES: KarakamshaMeaning(
        life_purpose="Pioneer and initiator, leading new ventures",
        career_direction="Military, sports, engineering, surgery, entrepreneurship",
        spiritual_path="Karma Yoga - action without attachment",
        key_themes=["Leadership", "Independence", "Courage", "New beginnings"]
    ),

    Zodiac.TAURUS: KarakamshaMeaning(
        life_purpose="Builder of lasting value and material security",
        career_direction="Finance, agriculture, arts, luxury goods, real estate",
        spiritual_path="Appreciation of divine beauty in material world",
        key_themes=["Stability", "Resources", "Sensory pleasure", "Accumulation"]
    ),

    Zodiac.GEMINI: KarakamshaMeaning(
        life_purpose="Communicator and connector of ideas",
        career_direction="Writing, teaching, journalism, trading, technology",
        spiritual_path="Jnana Yoga - path of knowledge",
        key_themes=["Communication", "Learning", "Versatility", "Networking"]
    ),

    Zodiac.CANCER: KarakamshaMeaning(
        life_purpose="Nurturer and protector of family/community",
        career_direction="Healthcare, hospitality, real estate, psychology, childcare",
        spiritual_path="Bhakti Yoga - devotional love",
        key_themes=["Nurturing", "Emotional security", "Home", "Traditions"]
    ),

    Zodiac.LEO: KarakamshaMeaning(
        life_purpose="Creative leader inspiring others through self-expression",
        career_direction="Entertainment, politics, management, speculation, education",
        spiritual_path="Self-realization through creative expression",
        key_themes=["Creativity", "Authority", "Recognition", "Romance"]
    ),

    Zodiac.VIRGO: KarakamshaMeaning(
        life_purpose="Healer and servant improving systems and health",
        career_direction="Healthcare, accounting, editing, analysis, service industries",
        spiritual_path="Seva - selfless service",
        key_themes=["Service", "Analysis", "Health", "Perfectionism"]
    ),

    Zodiac.LIBRA: KarakamshaMeaning(
        life_purpose="Harmonizer and diplomat creating balance",
        career_direction="Law, diplomacy, design, counseling, partnerships",
        spiritual_path="Balance between spiritual and material worlds",
        key_themes=["Relationships", "Justice", "Beauty", "Harmony"]
    ),

    Zodiac.SCORPIO: KarakamshaMeaning(
        life_purpose="Transformer uncovering hidden truths",
        career_direction="Research, occult sciences, psychology, surgery, investigation",
        spiritual_path="Tantric transformation of lower energies",
        key_themes=["Transformation", "Secrets", "Intensity", "Rebirth"]
    ),

    Zodiac.SAGITTARIUS: KarakamshaMeaning(
        life_purpose="Seeker and teacher of higher wisdom",
        career_direction="Education, law, publishing, travel, religion, philosophy",
        spiritual_path="Dharma - righteous living and teaching",
        key_themes=["Philosophy", "Expansion", "Higher learning", "Adventure"]
    ),

    Zodiac.CAPRICORN: KarakamshaMeaning(
        life_purpose="Builder of lasting structures and authority",
        career_direction="Government, management, construction, traditional business",
        spiritual_path="Karma Yoga through worldly responsibilities",
        key_themes=["Achievement", "Structure", "Authority", "Legacy"]
    ),

    Zodiac.AQUARIUS: KarakamshaMeaning(
        life_purpose="Innovator and humanitarian serving collective",
        career_direction="Technology, social work, networking, innovation, reforms",
        spiritual_path="Service to humanity, universal consciousness",
        key_themes=["Innovation", "Humanity", "Networks", "Future vision"]
    ),

    Zodiac.PISCES: KarakamshaMeaning(
        life_purpose="Spiritual seeker dissolving ego boundaries",
        career_direction="Arts, healing, spirituality, institutions, charity",
        spiritual_path="Moksha - liberation through surrender",
        key_themes=["Spirituality", "Compassion", "Imagination", "Transcendence"]
    ),
}


# =============================================================================
# BADHAKA RULES
# Obstruction houses based on sign modality
# =============================================================================

@dataclass
class BadhakaRule:
    """Badhaka (obstruction) house rules"""
    badhaka_house: int         # House number causing obstruction
    description: str           # Explanation


BADHAKA_RULES: Dict[str, BadhakaRule] = {
    "Movable": BadhakaRule(
        badhaka_house=11,
        description="For movable signs (Aries, Cancer, Libra, Capricorn), 11th house is badhaka"
    ),
    "Fixed": BadhakaRule(
        badhaka_house=9,
        description="For fixed signs (Taurus, Leo, Scorpio, Aquarius), 9th house is badhaka"
    ),
    "Dual": BadhakaRule(
        badhaka_house=7,
        description="For dual signs (Gemini, Virgo, Sagittarius, Pisces), 7th house is badhaka"
    ),
}


# =============================================================================
# SIGN MODALITY MAPPING
# =============================================================================

SIGN_MODALITY: Dict[Zodiac, str] = {
    Zodiac.ARIES: "Movable",
    Zodiac.TAURUS: "Fixed",
    Zodiac.GEMINI: "Dual",
    Zodiac.CANCER: "Movable",
    Zodiac.LEO: "Fixed",
    Zodiac.VIRGO: "Dual",
    Zodiac.LIBRA: "Movable",
    Zodiac.SCORPIO: "Fixed",
    Zodiac.SAGITTARIUS: "Dual",
    Zodiac.CAPRICORN: "Movable",
    Zodiac.AQUARIUS: "Fixed",
    Zodiac.PISCES: "Dual",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_badhaka_house(lagna_sign: Zodiac) -> int:
    """
    Get the badhaka (obstruction) house for a given ascendant.

    Args:
        lagna_sign: The ascendant sign

    Returns:
        House number (1-12) that is badhaka for this lagna
    """
    modality = SIGN_MODALITY[lagna_sign]
    return BADHAKA_RULES[modality].badhaka_house


def get_atmakaraka_meaning(planet: Planet) -> AtmakarakaMeaning:
    """
    Get the soul lesson and karmic meaning for a planet as Atmakaraka.

    Args:
        planet: The Atmakaraka planet

    Returns:
        AtmakarakaMeaning dataclass with full interpretation
    """
    return ATMAKARAKA_MEANINGS.get(planet)


def get_karakamsha_meaning(sign: Zodiac) -> KarakamshaMeaning:
    """
    Get the life purpose meaning for Atmakaraka's Navamsha placement.

    Args:
        sign: The Karakamsha sign (AK's position in D9)

    Returns:
        KarakamshaMeaning dataclass with full interpretation
    """
    return KARAKAMSHA_MEANINGS.get(sign)


# =============================================================================
# CHARA KARAKA ORDER
# 7-planet system (Rahu excluded), sorted by degrees in sign
# =============================================================================

CHARA_KARAKA_ORDER = [
    ("AK", "Atmakaraka", "Soul significator - highest degree"),
    ("AmK", "Amatyakaraka", "Minister/career - 2nd highest degree"),
    ("BK", "Bhratrikaraka", "Siblings/courage - 3rd highest degree"),
    ("MK", "Matrikaraka", "Mother/mind - 4th highest degree"),
    ("PK", "Pitrikaraka", "Father/children - 5th highest degree"),
    ("GK", "Gnatikaraka", "Enemies/obstacles - 6th highest degree"),
    ("DK", "Darakaraka", "Spouse - lowest degree"),
]


# =============================================================================
# JAIMINI ASPECT RULES
# Special aspects in Jaimini system (sign-based, not planet-based)
# =============================================================================

JAIMINI_ASPECTS = {
    "Movable": ["Fixed"],       # Movable signs aspect fixed signs (except adjacent)
    "Fixed": ["Movable"],       # Fixed signs aspect movable signs (except adjacent)
    "Dual": ["Dual"],           # Dual signs aspect other dual signs
}


def get_jaimini_aspects(sign: Zodiac) -> List[Zodiac]:
    """
    Get the signs aspected by a given sign in Jaimini system.

    In Jaimini:
    - Movable signs aspect fixed signs (except adjacent ones)
    - Fixed signs aspect movable signs (except adjacent ones)
    - Dual signs aspect other dual signs

    Args:
        sign: The sign doing the aspecting

    Returns:
        List of signs being aspected
    """
    modality = SIGN_MODALITY[sign]
    aspected_modality = JAIMINI_ASPECTS[modality][0]

    aspected_signs = []
    for s in Zodiac:
        if SIGN_MODALITY[s] == aspected_modality:
            # Check if not adjacent (difference should not be 1 or 11)
            diff = abs(s.value - sign.value)
            if diff != 1 and diff != 11:
                aspected_signs.append(s)

    return aspected_signs


# =============================================================================
# ARGALA RULES (Intervention)
# Houses that create intervention/support
# =============================================================================

@dataclass
class ArgalaRule:
    """Argala (intervention) rules"""
    argala_houses: List[int]        # Houses causing argala
    virodha_houses: List[int]       # Houses obstructing argala
    description: str


ARGALA_RULES = {
    "primary": ArgalaRule(
        argala_houses=[2, 4, 11],
        virodha_houses=[12, 10, 3],
        description="Primary argala from 2nd, 4th, 11th; obstructed by 12th, 10th, 3rd"
    ),
    "secondary": ArgalaRule(
        argala_houses=[5],
        virodha_houses=[9],
        description="Secondary argala from 5th; obstructed by 9th"
    ),
}
