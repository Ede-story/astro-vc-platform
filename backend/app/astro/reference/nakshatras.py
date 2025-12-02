"""
Nakshatra (Lunar Mansion) Reference Data

Complete catalog of 27 Nakshatras with their properties,
used for Stage 11 Nakshatra Deep Dive analysis.
"""
from dataclasses import dataclass
from typing import Dict, List
from ..models.types import Planet, GanaType


@dataclass
class NakshatraData:
    """Complete data for a single Nakshatra"""
    number: int                    # 1-27
    name: str                      # English name
    sanskrit_name: str             # Sanskrit name
    start_degree: float            # Start degree (0-360)
    end_degree: float              # End degree (0-360)
    sign_start: str                # Starting zodiac sign
    lord: Planet                   # Ruling planet
    deity: str                     # Presiding deity
    gana: GanaType                 # Deva/Manushya/Rakshasa
    symbol: str                    # Traditional symbol
    shakti: str                    # Power/ability
    quality: str                   # Movable/Fixed/Dual
    element: str                   # Fire/Earth/Air/Water
    motivation: str                # Dharma/Artha/Kama/Moksha
    animal: str                    # Animal symbol
    sound_padas: List[str]         # Sounds for 4 padas
    positive_traits: List[str]
    negative_traits: List[str]
    career_inclinations: List[str]


# Nakshatra span: 13°20' = 13.333... degrees
NAKSHATRA_SPAN = 360.0 / 27.0  # 13.333...


# Complete 27 Nakshatra Catalog
NAKSHATRA_CATALOG: Dict[str, NakshatraData] = {
    "Ashwini": NakshatraData(
        number=1,
        name="Ashwini",
        sanskrit_name="अश्विनी",
        start_degree=0.0,
        end_degree=13.333333,
        sign_start="Aries",
        lord=Planet.KETU,
        deity="Ashwini Kumaras (Divine Physicians)",
        gana=GanaType.DEVA,
        symbol="Horse head",
        shakti="Power to quickly reach things",
        quality="Movable",
        element="Fire",
        motivation="Dharma",
        animal="Male Horse",
        sound_padas=["Chu", "Che", "Cho", "La"],
        positive_traits=["Quick", "Pioneering", "Healing ability", "Independent", "Courageous"],
        negative_traits=["Impulsive", "Aggressive", "Stubborn", "Impatient"],
        career_inclinations=["Medicine", "Emergency services", "Sports", "Entrepreneurship", "Racing"]
    ),

    "Bharani": NakshatraData(
        number=2,
        name="Bharani",
        sanskrit_name="भरणी",
        start_degree=13.333333,
        end_degree=26.666667,
        sign_start="Aries",
        lord=Planet.VENUS,
        deity="Yama (God of Death)",
        gana=GanaType.MANUSHYA,
        symbol="Yoni (female reproductive organ)",
        shakti="Power to take things away",
        quality="Fixed",
        element="Fire",
        motivation="Artha",
        animal="Male Elephant",
        sound_padas=["Li", "Lu", "Le", "Lo"],
        positive_traits=["Creative", "Responsible", "Nurturing", "Transformative", "Artistic"],
        negative_traits=["Jealous", "Possessive", "Judgmental", "Moralistic"],
        career_inclinations=["Art", "Publishing", "Hospitality", "Childcare", "Entertainment"]
    ),

    "Krittika": NakshatraData(
        number=3,
        name="Krittika",
        sanskrit_name="कृत्तिका",
        start_degree=26.666667,
        end_degree=40.0,
        sign_start="Aries",
        lord=Planet.SUN,
        deity="Agni (Fire God)",
        gana=GanaType.RAKSHASA,
        symbol="Razor/Flame/Axe",
        shakti="Power to burn/purify",
        quality="Dual",
        element="Fire",
        motivation="Kama",
        animal="Female Sheep",
        sound_padas=["A", "I", "U", "E"],
        positive_traits=["Sharp intellect", "Purifying", "Leader", "Determined", "Dignified"],
        negative_traits=["Critical", "Destructive", "Stubborn", "Hot-tempered"],
        career_inclinations=["Military", "Surgery", "Cooking", "Fire services", "Criticism"]
    ),

    "Rohini": NakshatraData(
        number=4,
        name="Rohini",
        sanskrit_name="रोहिणी",
        start_degree=40.0,
        end_degree=53.333333,
        sign_start="Taurus",
        lord=Planet.MOON,
        deity="Brahma (Creator)",
        gana=GanaType.MANUSHYA,
        symbol="Ox cart/Chariot",
        shakti="Power of growth",
        quality="Fixed",
        element="Earth",
        motivation="Moksha",
        animal="Male Serpent",
        sound_padas=["O", "Va", "Vi", "Vu"],
        positive_traits=["Beautiful", "Fertile", "Artistic", "Luxurious", "Magnetic"],
        negative_traits=["Materialistic", "Jealous", "Possessive", "Indulgent"],
        career_inclinations=["Fashion", "Beauty", "Agriculture", "Arts", "Luxury goods"]
    ),

    "Mrigashira": NakshatraData(
        number=5,
        name="Mrigashira",
        sanskrit_name="मृगशिरा",
        start_degree=53.333333,
        end_degree=66.666667,
        sign_start="Taurus",
        lord=Planet.MARS,
        deity="Soma (Moon God)",
        gana=GanaType.DEVA,
        symbol="Deer head",
        shakti="Power of fulfillment",
        quality="Movable",
        element="Earth",
        motivation="Moksha",
        animal="Female Serpent",
        sound_padas=["Ve", "Vo", "Ka", "Ki"],
        positive_traits=["Curious", "Searching", "Gentle", "Perceptive", "Sensitive"],
        negative_traits=["Restless", "Fickle", "Suspicious", "Nervous"],
        career_inclinations=["Research", "Travel", "Writing", "Singing", "Textiles"]
    ),

    "Ardra": NakshatraData(
        number=6,
        name="Ardra",
        sanskrit_name="आर्द्रा",
        start_degree=66.666667,
        end_degree=80.0,
        sign_start="Gemini",
        lord=Planet.RAHU,
        deity="Rudra (Storm God)",
        gana=GanaType.MANUSHYA,
        symbol="Teardrop/Diamond",
        shakti="Power of effort",
        quality="Dual",
        element="Air",
        motivation="Kama",
        animal="Female Dog",
        sound_padas=["Ku", "Gha", "Ng", "Chha"],
        positive_traits=["Intellectual", "Transformative", "Powerful", "Ambitious", "Research-oriented"],
        negative_traits=["Destructive", "Arrogant", "Ungrateful", "Anti-social"],
        career_inclinations=["Technology", "Research", "Electronics", "Psychology", "Investigation"]
    ),

    "Punarvasu": NakshatraData(
        number=7,
        name="Punarvasu",
        sanskrit_name="पुनर्वसु",
        start_degree=80.0,
        end_degree=93.333333,
        sign_start="Gemini",
        lord=Planet.JUPITER,
        deity="Aditi (Mother of Gods)",
        gana=GanaType.DEVA,
        symbol="Bow and quiver",
        shakti="Power of renewal",
        quality="Movable",
        element="Air",
        motivation="Artha",
        animal="Female Cat",
        sound_padas=["Ke", "Ko", "Ha", "Hi"],
        positive_traits=["Optimistic", "Philosophical", "Nurturing", "Adaptable", "Generous"],
        negative_traits=["Over-simplistic", "Fickle", "Unstable", "Indecisive"],
        career_inclinations=["Teaching", "Counseling", "Writing", "Travel", "Spirituality"]
    ),

    "Pushya": NakshatraData(
        number=8,
        name="Pushya",
        sanskrit_name="पुष्य",
        start_degree=93.333333,
        end_degree=106.666667,
        sign_start="Cancer",
        lord=Planet.SATURN,
        deity="Brihaspati (Jupiter/Guru)",
        gana=GanaType.DEVA,
        symbol="Flower/Circle/Arrow",
        shakti="Power of spiritual energy",
        quality="Fixed",
        element="Water",
        motivation="Dharma",
        animal="Male Sheep",
        sound_padas=["Hu", "He", "Ho", "Da"],
        positive_traits=["Nourishing", "Protective", "Religious", "Helpful", "Independent"],
        negative_traits=["Stubborn", "Doubtful", "Selfish", "Arrogant"],
        career_inclinations=["Religion", "Politics", "Counseling", "Food industry", "Charity"]
    ),

    "Ashlesha": NakshatraData(
        number=9,
        name="Ashlesha",
        sanskrit_name="आश्लेषा",
        start_degree=106.666667,
        end_degree=120.0,
        sign_start="Cancer",
        lord=Planet.MERCURY,
        deity="Nagas (Serpent Gods)",
        gana=GanaType.RAKSHASA,
        symbol="Coiled serpent",
        shakti="Power to inflict poison",
        quality="Dual",
        element="Water",
        motivation="Dharma",
        animal="Male Cat",
        sound_padas=["Di", "Du", "De", "Do"],
        positive_traits=["Intuitive", "Penetrating", "Mystical", "Kundalini", "Hypnotic"],
        negative_traits=["Deceptive", "Manipulative", "Cold", "Secretive"],
        career_inclinations=["Occult", "Psychology", "Pharmacy", "Politics", "Astrology"]
    ),

    "Magha": NakshatraData(
        number=10,
        name="Magha",
        sanskrit_name="मघा",
        start_degree=120.0,
        end_degree=133.333333,
        sign_start="Leo",
        lord=Planet.KETU,
        deity="Pitris (Ancestors)",
        gana=GanaType.RAKSHASA,
        symbol="Throne/Palanquin",
        shakti="Power to leave the body",
        quality="Movable",
        element="Fire",
        motivation="Artha",
        animal="Male Rat",
        sound_padas=["Ma", "Mi", "Mu", "Me"],
        positive_traits=["Regal", "Ambitious", "Generous", "Traditional", "Authoritative"],
        negative_traits=["Arrogant", "Elitist", "Disdainful", "Dominating"],
        career_inclinations=["Politics", "Administration", "History", "Genealogy", "Management"]
    ),

    "Purva Phalguni": NakshatraData(
        number=11,
        name="Purva Phalguni",
        sanskrit_name="पूर्वाफाल्गुनी",
        start_degree=133.333333,
        end_degree=146.666667,
        sign_start="Leo",
        lord=Planet.VENUS,
        deity="Bhaga (God of Fortune)",
        gana=GanaType.MANUSHYA,
        symbol="Front legs of bed/Hammock",
        shakti="Power of procreation",
        quality="Fixed",
        element="Fire",
        motivation="Kama",
        animal="Female Rat",
        sound_padas=["Mo", "Ta", "Ti", "Tu"],
        positive_traits=["Creative", "Carefree", "Social", "Affectionate", "Artistic"],
        negative_traits=["Vain", "Promiscuous", "Lazy", "Indulgent"],
        career_inclinations=["Entertainment", "Arts", "Music", "Acting", "Photography"]
    ),

    "Uttara Phalguni": NakshatraData(
        number=12,
        name="Uttara Phalguni",
        sanskrit_name="उत्तराफाल्गुनी",
        start_degree=146.666667,
        end_degree=160.0,
        sign_start="Leo",
        lord=Planet.SUN,
        deity="Aryaman (God of Contracts)",
        gana=GanaType.MANUSHYA,
        symbol="Back legs of bed",
        shakti="Power of accumulation",
        quality="Fixed",
        element="Fire",
        motivation="Moksha",
        animal="Male Cow",
        sound_padas=["Te", "To", "Pa", "Pi"],
        positive_traits=["Generous", "Prosperous", "Friendly", "Helpful", "Reliable"],
        negative_traits=["Stubborn", "Resentful", "Disdainful", "Bossy"],
        career_inclinations=["Social work", "Philanthropy", "Counseling", "UN/NGO", "Contracts"]
    ),

    "Hasta": NakshatraData(
        number=13,
        name="Hasta",
        sanskrit_name="हस्त",
        start_degree=160.0,
        end_degree=173.333333,
        sign_start="Virgo",
        lord=Planet.MOON,
        deity="Savitar (Sun God)",
        gana=GanaType.DEVA,
        symbol="Hand/Fist",
        shakti="Power to gain what we seek",
        quality="Movable",
        element="Earth",
        motivation="Moksha",
        animal="Female Buffalo",
        sound_padas=["Pu", "Sha", "Na", "Tha"],
        positive_traits=["Skillful", "Clever", "Entertaining", "Practical", "Cunning"],
        negative_traits=["Controlling", "Scheming", "Selfish", "Overactive"],
        career_inclinations=["Crafts", "Magic", "Healing", "Comedy", "Manual skills"]
    ),

    "Chitra": NakshatraData(
        number=14,
        name="Chitra",
        sanskrit_name="चित्रा",
        start_degree=173.333333,
        end_degree=186.666667,
        sign_start="Virgo",
        lord=Planet.MARS,
        deity="Vishvakarma (Divine Architect)",
        gana=GanaType.RAKSHASA,
        symbol="Bright jewel/Pearl",
        shakti="Power to accumulate merit",
        quality="Dual",
        element="Earth",
        motivation="Kama",
        animal="Female Tiger",
        sound_padas=["Pe", "Po", "Ra", "Ri"],
        positive_traits=["Artistic", "Elegant", "Creative", "Charismatic", "Visionary"],
        negative_traits=["Egotistic", "Self-indulgent", "Superficial", "Critical"],
        career_inclinations=["Architecture", "Design", "Fashion", "Jewelry", "Engineering"]
    ),

    "Swati": NakshatraData(
        number=15,
        name="Swati",
        sanskrit_name="स्वाति",
        start_degree=186.666667,
        end_degree=200.0,
        sign_start="Libra",
        lord=Planet.RAHU,
        deity="Vayu (Wind God)",
        gana=GanaType.DEVA,
        symbol="Young plant/Sword",
        shakti="Power to scatter like wind",
        quality="Movable",
        element="Air",
        motivation="Artha",
        animal="Male Buffalo",
        sound_padas=["Ru", "Re", "Ro", "Ta"],
        positive_traits=["Independent", "Diplomatic", "Compassionate", "Flexible", "Business-minded"],
        negative_traits=["Restless", "Ungrounded", "Self-absorbed", "Reclusive"],
        career_inclinations=["Business", "Trade", "Law", "Diplomacy", "Travel"]
    ),

    "Vishakha": NakshatraData(
        number=16,
        name="Vishakha",
        sanskrit_name="विशाखा",
        start_degree=200.0,
        end_degree=213.333333,
        sign_start="Libra",
        lord=Planet.JUPITER,
        deity="Indra-Agni (King and Fire)",
        gana=GanaType.RAKSHASA,
        symbol="Triumphal arch/Potter's wheel",
        shakti="Power to achieve many fruits",
        quality="Dual",
        element="Air",
        motivation="Dharma",
        animal="Male Tiger",
        sound_padas=["Ti", "Tu", "Te", "To"],
        positive_traits=["Determined", "Ambitious", "Focused", "Courageous", "Competitive"],
        negative_traits=["Jealous", "Frustrated", "Restless", "Quarrelsome"],
        career_inclinations=["Politics", "Leadership", "Research", "Speaking", "Religion"]
    ),

    "Anuradha": NakshatraData(
        number=17,
        name="Anuradha",
        sanskrit_name="अनुराधा",
        start_degree=213.333333,
        end_degree=226.666667,
        sign_start="Scorpio",
        lord=Planet.SATURN,
        deity="Mitra (God of Friendship)",
        gana=GanaType.DEVA,
        symbol="Lotus flower/Archway",
        shakti="Power of worship",
        quality="Movable",
        element="Water",
        motivation="Dharma",
        animal="Female Deer",
        sound_padas=["Na", "Ni", "Nu", "Ne"],
        positive_traits=["Devoted", "Friendly", "Cooperative", "Successful", "Spiritual"],
        negative_traits=["Jealous", "Controlling", "Melancholic", "Revengeful"],
        career_inclinations=["Organizations", "Numerology", "Statistics", "Occult", "Mining"]
    ),

    "Jyeshtha": NakshatraData(
        number=18,
        name="Jyeshtha",
        sanskrit_name="ज्येष्ठा",
        start_degree=226.666667,
        end_degree=240.0,
        sign_start="Scorpio",
        lord=Planet.MERCURY,
        deity="Indra (King of Gods)",
        gana=GanaType.RAKSHASA,
        symbol="Earring/Umbrella",
        shakti="Power to rise and conquer",
        quality="Dual",
        element="Water",
        motivation="Artha",
        animal="Male Deer",
        sound_padas=["No", "Ya", "Yi", "Yu"],
        positive_traits=["Protective", "Heroic", "Resourceful", "Leader", "Virtuous"],
        negative_traits=["Arrogant", "Hypocritical", "Vindictive", "Hidden"],
        career_inclinations=["Military", "Police", "Politics", "Occult", "Management"]
    ),

    "Mula": NakshatraData(
        number=19,
        name="Mula",
        sanskrit_name="मूल",
        start_degree=240.0,
        end_degree=253.333333,
        sign_start="Sagittarius",
        lord=Planet.KETU,
        deity="Nirriti (Goddess of Destruction)",
        gana=GanaType.RAKSHASA,
        symbol="Bunch of roots/Lion's tail",
        shakti="Power to destroy",
        quality="Dual",
        element="Fire",
        motivation="Kama",
        animal="Male Dog",
        sound_padas=["Ye", "Yo", "Bha", "Bhi"],
        positive_traits=["Philosophical", "Investigative", "Ambitious", "Skillful", "Rooted"],
        negative_traits=["Destructive", "Arrogant", "Self-destructive", "Rootless"],
        career_inclinations=["Research", "Medicine", "Politics", "Herbs", "Philosophy"]
    ),

    "Purva Ashadha": NakshatraData(
        number=20,
        name="Purva Ashadha",
        sanskrit_name="पूर्वाषाढ़ा",
        start_degree=253.333333,
        end_degree=266.666667,
        sign_start="Sagittarius",
        lord=Planet.VENUS,
        deity="Apas (Water God)",
        gana=GanaType.MANUSHYA,
        symbol="Elephant tusk/Fan",
        shakti="Power of invigoration",
        quality="Fixed",
        element="Fire",
        motivation="Moksha",
        animal="Male Monkey",
        sound_padas=["Bhu", "Dha", "Pha", "Dha"],
        positive_traits=["Invincible", "Ambitious", "Philosophical", "Confident", "Proud"],
        negative_traits=["Overconfident", "Uncompromising", "Egoistic", "Argumentative"],
        career_inclinations=["Philosophy", "Law", "Writing", "Debate", "Shipping"]
    ),

    "Uttara Ashadha": NakshatraData(
        number=21,
        name="Uttara Ashadha",
        sanskrit_name="उत्तराषाढ़ा",
        start_degree=266.666667,
        end_degree=280.0,
        sign_start="Sagittarius",
        lord=Planet.SUN,
        deity="Vishvadevas (Universal Gods)",
        gana=GanaType.MANUSHYA,
        symbol="Elephant tusk/Small bed",
        shakti="Power of final victory",
        quality="Fixed",
        element="Fire",
        motivation="Moksha",
        animal="Male Mongoose",
        sound_padas=["Be", "Bo", "Ja", "Ji"],
        positive_traits=["Leadership", "Responsible", "Righteous", "Enduring", "Sincere"],
        negative_traits=["Rigid", "Lonely", "Multiple relationships", "Restless"],
        career_inclinations=["Government", "Military", "Law", "Research", "Pioneers"]
    ),

    "Shravana": NakshatraData(
        number=22,
        name="Shravana",
        sanskrit_name="श्रवण",
        start_degree=280.0,
        end_degree=293.333333,
        sign_start="Capricorn",
        lord=Planet.MOON,
        deity="Vishnu (Preserver)",
        gana=GanaType.DEVA,
        symbol="Ear/Three footprints",
        shakti="Power of connection",
        quality="Movable",
        element="Earth",
        motivation="Artha",
        animal="Female Monkey",
        sound_padas=["Ju", "Je", "Jo", "Gha"],
        positive_traits=["Learned", "Charitable", "Wise", "Famous", "Listening"],
        negative_traits=["Sensitive", "Rigid", "Gossipy", "Extremist"],
        career_inclinations=["Teaching", "Counseling", "Media", "Music", "Languages"]
    ),

    "Dhanishta": NakshatraData(
        number=23,
        name="Dhanishta",
        sanskrit_name="धनिष्ठा",
        start_degree=293.333333,
        end_degree=306.666667,
        sign_start="Capricorn",
        lord=Planet.MARS,
        deity="Vasus (Eight Elemental Gods)",
        gana=GanaType.RAKSHASA,
        symbol="Drum/Flute",
        shakti="Power of fame",
        quality="Movable",
        element="Earth",
        motivation="Dharma",
        animal="Female Lion",
        sound_padas=["Ga", "Gi", "Gu", "Ge"],
        positive_traits=["Wealthy", "Musical", "Charitable", "Brave", "Ambitious"],
        negative_traits=["Arrogant", "Careless", "Self-absorbed", "Argumentative"],
        career_inclinations=["Music", "Real estate", "Surgery", "Military", "Mining"]
    ),

    "Shatabhisha": NakshatraData(
        number=24,
        name="Shatabhisha",
        sanskrit_name="शतभिषा",
        start_degree=306.666667,
        end_degree=320.0,
        sign_start="Aquarius",
        lord=Planet.RAHU,
        deity="Varuna (God of Cosmic Waters)",
        gana=GanaType.RAKSHASA,
        symbol="Empty circle/100 flowers",
        shakti="Power of healing",
        quality="Movable",
        element="Air",
        motivation="Dharma",
        animal="Female Horse",
        sound_padas=["Go", "Sa", "Si", "Su"],
        positive_traits=["Truthful", "Principled", "Healing", "Philosophical", "Independent"],
        negative_traits=["Secretive", "Harsh", "Stubborn", "Lonely"],
        career_inclinations=["Healing", "Astronomy", "Electricity", "Nuclear", "Aquatics"]
    ),

    "Purva Bhadrapada": NakshatraData(
        number=25,
        name="Purva Bhadrapada",
        sanskrit_name="पूर्वाभाद्रपदा",
        start_degree=320.0,
        end_degree=333.333333,
        sign_start="Aquarius",
        lord=Planet.JUPITER,
        deity="Aja Ekapada (One-footed Goat)",
        gana=GanaType.MANUSHYA,
        symbol="Front of funeral cot/Man with two faces",
        shakti="Power of spiritual fire",
        quality="Fixed",
        element="Air",
        motivation="Artha",
        animal="Male Lion",
        sound_padas=["Se", "So", "Da", "Di"],
        positive_traits=["Spiritual", "Intelligent", "Wealthy", "Transformative", "Passionate"],
        negative_traits=["Pessimistic", "Cynical", "Dark", "Violent"],
        career_inclinations=["Occult", "Astrology", "Research", "Mortician", "Metal work"]
    ),

    "Uttara Bhadrapada": NakshatraData(
        number=26,
        name="Uttara Bhadrapada",
        sanskrit_name="उत्तराभाद्रपदा",
        start_degree=333.333333,
        end_degree=346.666667,
        sign_start="Pisces",
        lord=Planet.SATURN,
        deity="Ahir Budhnya (Serpent of Deep)",
        gana=GanaType.MANUSHYA,
        symbol="Back of funeral cot/Twin",
        shakti="Power to bring rain",
        quality="Fixed",
        element="Water",
        motivation="Kama",
        animal="Female Cow",
        sound_padas=["Du", "Tha", "Jha", "Da"],
        positive_traits=["Wise", "Virtuous", "Wealthy", "Charitable", "Controlling"],
        negative_traits=["Lazy", "Irresponsible", "Possessive", "Secretive"],
        career_inclinations=["Charity", "Non-profit", "Yoga", "Import/Export", "Counseling"]
    ),

    "Revati": NakshatraData(
        number=27,
        name="Revati",
        sanskrit_name="रेवती",
        start_degree=346.666667,
        end_degree=360.0,
        sign_start="Pisces",
        lord=Planet.MERCURY,
        deity="Pushan (Nourisher)",
        gana=GanaType.DEVA,
        symbol="Fish/Drum",
        shakti="Power of nourishment",
        quality="Dual",
        element="Water",
        motivation="Moksha",
        animal="Female Elephant",
        sound_padas=["De", "Do", "Cha", "Chi"],
        positive_traits=["Prosperous", "Clean", "Brave", "Popular", "Artistic"],
        negative_traits=["Indecisive", "Dependent", "Stubborn", "Disappointed"],
        career_inclinations=["Travel", "Journalism", "Orphanages", "Animal care", "Clock making"]
    ),
}


# Nakshatra lords sequence (for Vimshottari Dasha)
NAKSHATRA_LORDS_SEQUENCE = [
    Planet.KETU, Planet.VENUS, Planet.SUN,
    Planet.MOON, Planet.MARS, Planet.RAHU,
    Planet.JUPITER, Planet.SATURN, Planet.MERCURY
]


def get_nakshatra_from_degree(longitude: float) -> NakshatraData:
    """
    Get nakshatra data from absolute longitude (0-360).

    Args:
        longitude: Absolute degree (0-360)

    Returns:
        NakshatraData for the nakshatra at that degree
    """
    # Normalize to 0-360
    longitude = longitude % 360

    # Find which nakshatra
    for nak_data in NAKSHATRA_CATALOG.values():
        if nak_data.start_degree <= longitude < nak_data.end_degree:
            return nak_data

    # Edge case: exactly 360 degrees = Ashwini
    return NAKSHATRA_CATALOG["Ashwini"]


def get_nakshatra_pada(longitude: float) -> int:
    """
    Get pada (quarter) 1-4 from longitude.
    Each nakshatra is 13°20', each pada is 3°20' (3.333...)
    """
    longitude = longitude % 360
    degree_in_nak = longitude % NAKSHATRA_SPAN
    pada = int(degree_in_nak / (NAKSHATRA_SPAN / 4)) + 1
    return min(4, max(1, pada))


def get_nakshatra_lord_from_degree(longitude: float) -> Planet:
    """Get ruling planet of nakshatra from longitude."""
    nak = get_nakshatra_from_degree(longitude)
    return nak.lord
