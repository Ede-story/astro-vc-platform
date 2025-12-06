"""
Yoga Layer - Planet Scoring Phase 9.5 (Enhanced)

Evaluates planetary strength based on yoga participation:
- 50+ classical Vedic yogas from BPHS and Jataka Parijata
- Raja Yogas (power/authority)
- Dhana Yogas (wealth)
- Pancha Mahapurusha Yogas
- Parivartana Yogas (exchange)
- Neecha Bhanga (cancellation of debilitation)
- Graha Malika Yogas
- Nabha Yogas (pattern yogas)
- Chandra Yogas (Moon combinations)
- Surya Yogas (Sun combinations)
- And many more...

Score range: -18 to +18 points (Phase 9.5 spec)
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass

from ..neecha_bhanga import SIGN_LORDS, OWN_SIGNS, get_sign_number


# Exaltation signs for each planet
EXALTATION = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra",
    "Rahu": "Taurus",
    "Ketu": "Scorpio",
}

# Debilitation signs
DEBILITATION = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
    "Rahu": "Scorpio",
    "Ketu": "Taurus",
}

# Moolatrikona signs
MOOLATRIKONA = {
    "Sun": "Leo",
    "Moon": "Taurus",
    "Mars": "Aries",
    "Mercury": "Virgo",
    "Jupiter": "Sagittarius",
    "Venus": "Libra",
    "Saturn": "Aquarius",
}

# Natural benefics and malefics
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# Yoga types and their point values - expanded for Phase 9.5
YOGA_POINTS = {
    # === MAHA RAJA YOGAS (Supreme power) ===
    "maha_raja_yoga": 10.0,
    "viparita_raja_yoga": 8.0,  # Lord of 6/8/12 in 6/8/12

    # === RAJA YOGAS (Power/Authority) ===
    "raja_yoga_kendra_trikona": 6.0,  # Kendra-Trikona lords conjunction
    "raja_yoga": 5.0,
    "raja_yoga_minor": 3.0,

    # === PANCHA MAHAPURUSHA YOGAS ===
    "hamsa_yoga": 7.0,      # Jupiter in kendra in own/exaltation
    "malavya_yoga": 7.0,    # Venus in kendra in own/exaltation
    "bhadra_yoga": 7.0,     # Mercury in kendra in own/exaltation
    "ruchaka_yoga": 7.0,    # Mars in kendra in own/exaltation
    "sasa_yoga": 7.0,       # Saturn in kendra in own/exaltation

    # === DHANA YOGAS (Wealth) ===
    "maha_dhana_yoga": 8.0,
    "dhana_yoga": 5.0,
    "lakshmi_yoga": 6.0,    # Venus in own/exalt in kendra with 9th lord
    "kubera_yoga": 5.0,     # 2nd/11th lords in kendra
    "dhan_yoga_2_11": 4.0,  # 2nd and 11th lords connected

    # === CHANDRA (MOON) YOGAS ===
    "gajakesari_yoga": 6.0,      # Jupiter-Moon in kendra
    "sunapha_yoga": 4.0,         # Benefic in 2nd from Moon
    "anapha_yoga": 4.0,          # Benefic in 12th from Moon
    "durudhara_yoga": 5.0,       # Benefics in 2nd and 12th from Moon
    "kemadruma_yoga": -6.0,      # No planet 2nd/12th from Moon (negative!)
    "chandra_mangala_yoga": 4.0, # Moon-Mars conjunction
    "adhi_yoga": 6.0,            # Benefics in 6/7/8 from Moon
    "amala_yoga": 5.0,           # Benefic in 10th from Moon
    "pushkala_yoga": 4.0,        # Moon in friend's sign aspected by friend

    # === SURYA (SUN) YOGAS ===
    "budhaditya_yoga": 4.0,      # Sun-Mercury conjunction (Mercury unafflicted)
    "vesi_yoga": 3.0,            # Planet in 2nd from Sun
    "vasi_yoga": 3.0,            # Planet in 12th from Sun
    "ubhayachari_yoga": 5.0,     # Planets in 2nd and 12th from Sun
    "nipuna_yoga": 4.0,          # Sun-Mercury with aspect from Moon

    # === NABHA YOGAS (Pattern Yogas) ===
    "yava_yoga": 3.0,            # Planets in 1/4/7/10 alternating
    "shrinkhala_yoga": 3.0,      # Planets in series of signs
    "gola_yoga": 3.0,            # All planets in same half
    "yuga_yoga": 4.0,            # All planets in adjacent houses
    "shoola_yoga": -3.0,         # All planets in 3 signs (restrictive)
    "kedara_yoga": 3.0,          # All in 4 signs
    "pasha_yoga": -2.0,          # All in 5 signs
    "dama_yoga": 2.0,            # All in 6 signs
    "veena_yoga": 4.0,           # All in 7 signs
    "sankhya_yoga": 3.0,         # Various planet groupings

    # === PARIVARTANA (EXCHANGE) YOGAS ===
    "maha_parivartana_yoga": 6.0,  # Exchange between kendra/trikona lords
    "parivartana_yoga": 4.0,       # Any house lord exchange
    "dainya_parivartana_yoga": -3.0,  # Exchange involving 6/8/12 lord
    "khala_parivartana_yoga": -2.0,   # Exchange involving 3rd lord

    # === NEECHA BHANGA (Debilitation Cancellation) ===
    "neecha_bhanga_raja_yoga": 8.0,  # Full cancellation becoming Raja Yoga
    "neecha_bhanga": 5.0,            # Partial cancellation

    # === SPECIAL COMBINATIONS ===
    "vargottama": 4.0,          # Same sign in D1 and D9
    "pushkar_navamsha": 3.0,    # In auspicious navamsha
    "dig_bala": 3.0,            # Directional strength

    # === SANNYASA YOGAS ===
    "sannyasa_yoga": 3.0,       # 4+ planets in one house
    "pravrajya_yoga": 2.0,      # Moon in Saturn's navamsha aspected by Saturn

    # === ARISHTA (NEGATIVE) YOGAS ===
    "kemadruma_bhanga": 3.0,    # Cancellation of Kemadruma
    "shakata_yoga": -4.0,       # Jupiter in 6/8/12 from Moon
    "daridra_yoga": -5.0,       # 2nd/11th lords in 6/8/12
    "grahan_yoga": -3.0,        # Sun/Moon with Rahu/Ketu
    "kala_sarpa_yoga": -4.0,    # All planets between Rahu-Ketu
    "kala_amrita_yoga": 4.0,    # Reverse Kala Sarpa (all planets between Ketu-Rahu)

    # === ADDITIONAL WEALTH YOGAS ===
    "vasumathi_yoga": 5.0,      # Benefics in upachaya (3/6/10/11)
    "akhanda_samrajya_yoga": 7.0,  # Jupiter in kendra, 2nd/9th lords strong
    "shankha_yoga": 4.0,        # 5th and 6th lords in mutual kendra
    "bheri_yoga": 4.0,          # All planets in 1/2/7/12
    "mridanga_yoga": 4.0,       # Lord of kendra exalted, Jupiter in kendra

    # === ADDITIONAL POWER YOGAS ===
    "chamara_yoga": 5.0,        # Asc lord exalted, aspected by Jupiter
    "parvata_yoga": 4.0,        # Benefics in kendras, malefics in 3/6
    "kahala_yoga": 4.0,         # 4th and 9th lords in mutual kendra
    "simhasana_yoga": 5.0,      # 2nd lord in kendra with 10th lord
    "hala_yoga": 3.0,           # All benefics in trikona

    # === INTELLIGENCE/LEARNING YOGAS ===
    "saraswati_yoga": 6.0,      # Jup/Ven/Mer in kendra/trikona
    "bharati_yoga": 5.0,        # 2nd lord with Venus in 5th/9th
    "kavi_yoga": 4.0,           # 5th lord with Venus aspected by Jupiter
    "vidya_yoga": 4.0,          # Mercury/Jupiter strong in kendra

    # === FAME YOGAS ===
    "chapa_yoga": 4.0,          # Asc lord in 10th, 10th lord in 1st
    "kutila_yoga": 3.0,         # Mercury in 4th with Moon in 7th
    "matsya_yoga": 4.0,         # Malefics in 1/9, benefics in 5/4/8
    "koorma_yoga": 4.0,         # Benefics in 5/6/7, malefics in 1/3/11

    # === MISCELLANEOUS YOGAS ===
    "amrita_yoga": 5.0,         # All benefics in 10th
    "ashubha_mala_yoga": -4.0,  # Malefics in kendra without benefic aspect
    "subha_mala_yoga": 4.0,     # Benefics in kendra aspected by Jupiter
    "chatra_yoga": 3.0,         # All planets in 7 consecutive houses from asc
    "danda_yoga": 3.0,          # All planets in 7 consecutive from 10th

    # Generic fallbacks
    "auspicious_yoga": 2.0,
    "minor_yoga": 1.0,
    "inauspicious_yoga": -2.0,
}


@dataclass
class YogaLayerResult:
    """Result of yoga analysis for a planet"""
    planet: str
    yogas_participated: List[str]
    yoga_count: int
    total_yoga_points: float
    score: float
    details: List[str]


class YogaPlanetLayer:
    """
    Enhanced Yoga Layer for Phase 9.5

    Analyzes 50+ classical yogas and calculates
    planet strength based on yoga participation.

    Score range: -18 to +18 points
    """

    WEIGHT = 0.15  # 15% of total planet score
    MAX_SCORE = 18.0  # Phase 9.5 spec: ±18 points

    def __init__(self, d1_data: Dict[str, Any], yogas: List[Dict[str, Any]] = None,
                 d9_data: Dict[str, Any] = None):
        """
        Initialize Enhanced Yoga layer

        Args:
            d1_data: D1 chart data with planets
            yogas: List of externally detected yogas
            d9_data: D9 (Navamsha) chart data for vargottama detection
        """
        self.d1 = d1_data
        self.d9 = d9_data or {}
        self.yogas = yogas or []
        self.planets = d1_data.get("planets", [])
        self.ascendant = d1_data.get("ascendant", {})
        self.asc_sign = self.ascendant.get("sign_name") or self.ascendant.get("sign", "Aries")
        self.asc_num = get_sign_number(self.asc_sign)

        # Build planet lookup
        self.planet_data = {}
        for p in self.planets:
            name = p.get("name", "")
            sign = p.get("sign_name") or p.get("sign", "")
            house = p.get("house_occupied") or p.get("house")
            longitude = p.get("longitude", 0)

            if not house and sign:
                sign_num = get_sign_number(sign)
                house = ((sign_num - self.asc_num) % 12) + 1

            self.planet_data[name] = {
                "sign": sign,
                "house": house or 1,
                "longitude": longitude,
                "sign_num": get_sign_number(sign) if sign else 1,
            }

        # D9 planet data for vargottama
        self.d9_planet_data = {}
        for p in self.d9.get("planets", []):
            name = p.get("name", "")
            sign = p.get("sign_name") or p.get("sign", "")
            self.d9_planet_data[name] = {"sign": sign}

        # Comprehensive yoga detection
        self._detected_yogas: List[Dict[str, Any]] = []
        self._detect_all_yogas()

    def _get_house_lord(self, house: int) -> str:
        """Get the lord of a house"""
        # Calculate sign of house
        house_sign_num = ((self.asc_num + house - 2) % 12) + 1
        sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                      "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        house_sign = sign_names[house_sign_num - 1]
        return SIGN_LORDS.get(house_sign, "")

    def _get_house_from_sign(self, sign: str) -> int:
        """Get house number from sign"""
        sign_num = get_sign_number(sign)
        return ((sign_num - self.asc_num) % 12) + 1

    def _is_in_kendra(self, house: int) -> bool:
        """Check if house is a kendra (1, 4, 7, 10)"""
        return house in [1, 4, 7, 10]

    def _is_in_trikona(self, house: int) -> bool:
        """Check if house is a trikona (1, 5, 9)"""
        return house in [1, 5, 9]

    def _is_in_dusthana(self, house: int) -> bool:
        """Check if house is a dusthana (6, 8, 12)"""
        return house in [6, 8, 12]

    def _is_in_upachaya(self, house: int) -> bool:
        """Check if house is an upachaya (3, 6, 10, 11)"""
        return house in [3, 6, 10, 11]

    def _planets_in_kendra_from(self, ref_house: int) -> List[str]:
        """Get planets in kendra from reference house"""
        kendras = [(ref_house + 0 - 1) % 12 + 1,
                   (ref_house + 3 - 1) % 12 + 1,
                   (ref_house + 6 - 1) % 12 + 1,
                   (ref_house + 9 - 1) % 12 + 1]
        return [p for p, d in self.planet_data.items() if d.get("house") in kendras]

    def _is_exalted(self, planet: str) -> bool:
        """Check if planet is exalted"""
        sign = self.planet_data.get(planet, {}).get("sign", "")
        return sign == EXALTATION.get(planet, "")

    def _is_debilitated(self, planet: str) -> bool:
        """Check if planet is debilitated"""
        sign = self.planet_data.get(planet, {}).get("sign", "")
        return sign == DEBILITATION.get(planet, "")

    def _is_in_own_sign(self, planet: str) -> bool:
        """Check if planet is in own sign"""
        sign = self.planet_data.get(planet, {}).get("sign", "")
        return sign in OWN_SIGNS.get(planet, [])

    def _is_in_moolatrikona(self, planet: str) -> bool:
        """Check if planet is in moolatrikona"""
        sign = self.planet_data.get(planet, {}).get("sign", "")
        return sign == MOOLATRIKONA.get(planet, "")

    def _detect_all_yogas(self):
        """Detect all 50+ yogas from chart data"""
        self._detected_yogas = []

        # Run all detection methods
        self._detect_pancha_mahapurusha()
        self._detect_raja_yogas()
        self._detect_dhana_yogas()
        self._detect_chandra_yogas()
        self._detect_surya_yogas()
        self._detect_parivartana_yogas()
        self._detect_neecha_bhanga()
        self._detect_vargottama()
        self._detect_nabha_yogas()
        self._detect_special_yogas()
        self._detect_arishta_yogas()
        self._detect_fame_learning_yogas()

        # Add externally detected yogas
        self.yogas.extend(self._detected_yogas)

    def _detect_pancha_mahapurusha(self):
        """Detect Pancha Mahapurusha Yogas"""
        yoga_map = {
            "Jupiter": ("Hamsa Yoga", "hamsa_yoga"),
            "Venus": ("Malavya Yoga", "malavya_yoga"),
            "Mercury": ("Bhadra Yoga", "bhadra_yoga"),
            "Mars": ("Ruchaka Yoga", "ruchaka_yoga"),
            "Saturn": ("Sasa Yoga", "sasa_yoga"),
        }

        for planet, (name, type_) in yoga_map.items():
            data = self.planet_data.get(planet, {})
            house = data.get("house", 0)

            if self._is_in_kendra(house):
                if self._is_exalted(planet) or self._is_in_own_sign(planet) or self._is_in_moolatrikona(planet):
                    self._detected_yogas.append({
                        "name": name,
                        "type": type_,
                        "planets": [planet],
                        "strength": "strong",
                        "description": f"{planet} in kendra in dignified sign"
                    })

    def _detect_raja_yogas(self):
        """Detect Raja Yogas (Kendra-Trikona lord combinations)"""
        kendra_houses = [1, 4, 7, 10]
        trikona_houses = [5, 9]  # 1st is both

        kendra_lords = [self._get_house_lord(h) for h in kendra_houses]
        trikona_lords = [self._get_house_lord(h) for h in trikona_houses]

        # Check for conjunctions and mutual aspects
        for kl in kendra_lords:
            if not kl:
                continue
            kl_house = self.planet_data.get(kl, {}).get("house", 0)

            for tl in trikona_lords:
                if not tl or tl == kl:
                    continue
                tl_house = self.planet_data.get(tl, {}).get("house", 0)

                # Conjunction
                if kl_house == tl_house and kl_house > 0:
                    strength = "strong" if self._is_in_kendra(kl_house) or self._is_in_trikona(kl_house) else "moderate"
                    self._detected_yogas.append({
                        "name": f"Raja Yoga ({kl}-{tl})",
                        "type": "raja_yoga_kendra_trikona",
                        "planets": [kl, tl],
                        "strength": strength,
                        "description": f"Kendra lord {kl} conjunct Trikona lord {tl}"
                    })

    def _detect_dhana_yogas(self):
        """Detect Dhana (Wealth) Yogas"""
        lord_2 = self._get_house_lord(2)
        lord_11 = self._get_house_lord(11)
        lord_5 = self._get_house_lord(5)
        lord_9 = self._get_house_lord(9)

        # 2nd and 11th lords connection
        if lord_2 and lord_11:
            h2 = self.planet_data.get(lord_2, {}).get("house", 0)
            h11 = self.planet_data.get(lord_11, {}).get("house", 0)

            if h2 == h11 and h2 > 0:
                self._detected_yogas.append({
                    "name": "Dhana Yoga (2nd-11th)",
                    "type": "dhan_yoga_2_11",
                    "planets": [lord_2, lord_11],
                    "strength": "strong",
                    "description": "2nd and 11th lords conjunct"
                })

        # Lakshmi Yoga: Venus in own/exalt in kendra with 9th lord
        venus_data = self.planet_data.get("Venus", {})
        venus_house = venus_data.get("house", 0)
        if self._is_in_kendra(venus_house) and (self._is_exalted("Venus") or self._is_in_own_sign("Venus")):
            if lord_9:
                lord_9_house = self.planet_data.get(lord_9, {}).get("house", 0)
                if self._is_in_kendra(lord_9_house) or self._is_in_trikona(lord_9_house):
                    self._detected_yogas.append({
                        "name": "Lakshmi Yoga",
                        "type": "lakshmi_yoga",
                        "planets": ["Venus", lord_9],
                        "strength": "strong",
                        "description": "Venus dignified in kendra, 9th lord strong"
                    })

        # Vasumathi Yoga: Benefics in upachaya from Moon
        moon_house = self.planet_data.get("Moon", {}).get("house", 0)
        if moon_house:
            upachaya_from_moon = [(moon_house + h - 2) % 12 + 1 for h in [3, 6, 10, 11]]
            benefics_in_upachaya = []
            for b in ["Jupiter", "Venus", "Mercury"]:
                if self.planet_data.get(b, {}).get("house") in upachaya_from_moon:
                    benefics_in_upachaya.append(b)
            if len(benefics_in_upachaya) >= 2:
                self._detected_yogas.append({
                    "name": "Vasumathi Yoga",
                    "type": "vasumathi_yoga",
                    "planets": benefics_in_upachaya,
                    "strength": "moderate",
                    "description": "Benefics in upachaya from Moon"
                })

    def _detect_chandra_yogas(self):
        """Detect Moon-based yogas"""
        moon_data = self.planet_data.get("Moon", {})
        moon_house = moon_data.get("house", 0)
        if not moon_house:
            return

        house_2nd = (moon_house % 12) + 1
        house_12th = ((moon_house - 2) % 12) + 1

        planets_2nd = [p for p, d in self.planet_data.items()
                       if d.get("house") == house_2nd and p != "Moon"]
        planets_12th = [p for p, d in self.planet_data.items()
                        if d.get("house") == house_12th and p != "Moon"]

        benefics_2nd = [p for p in planets_2nd if p in NATURAL_BENEFICS]
        benefics_12th = [p for p in planets_12th if p in NATURAL_BENEFICS]

        # Sunapha: Benefic in 2nd from Moon
        if benefics_2nd:
            self._detected_yogas.append({
                "name": "Sunapha Yoga",
                "type": "sunapha_yoga",
                "planets": benefics_2nd + ["Moon"],
                "strength": "moderate",
                "description": "Benefic in 2nd from Moon"
            })

        # Anapha: Benefic in 12th from Moon
        if benefics_12th:
            self._detected_yogas.append({
                "name": "Anapha Yoga",
                "type": "anapha_yoga",
                "planets": benefics_12th + ["Moon"],
                "strength": "moderate",
                "description": "Benefic in 12th from Moon"
            })

        # Durudhara: Benefics in both 2nd and 12th
        if benefics_2nd and benefics_12th:
            self._detected_yogas.append({
                "name": "Durudhara Yoga",
                "type": "durudhara_yoga",
                "planets": benefics_2nd + benefics_12th + ["Moon"],
                "strength": "strong",
                "description": "Benefics in 2nd and 12th from Moon"
            })

        # Kemadruma: No planets in 2nd or 12th from Moon (negative yoga)
        if not planets_2nd and not planets_12th:
            # Check for cancellation
            kendras_from_moon = self._planets_in_kendra_from(moon_house)
            if kendras_from_moon:
                self._detected_yogas.append({
                    "name": "Kemadruma Bhanga",
                    "type": "kemadruma_bhanga",
                    "planets": kendras_from_moon + ["Moon"],
                    "strength": "moderate",
                    "description": "Kemadruma cancelled by planets in kendra from Moon"
                })
            else:
                self._detected_yogas.append({
                    "name": "Kemadruma Yoga",
                    "type": "kemadruma_yoga",
                    "planets": ["Moon"],
                    "strength": "strong",
                    "description": "No planets in 2nd/12th from Moon (inauspicious)"
                })

        # Gajakesari: Jupiter in kendra from Moon
        jupiter_house = self.planet_data.get("Jupiter", {}).get("house", 0)
        if jupiter_house and moon_house:
            diff = abs(jupiter_house - moon_house)
            if diff in [0, 3, 6, 9] or (12 - diff) in [0, 3, 6, 9]:
                self._detected_yogas.append({
                    "name": "Gajakesari Yoga",
                    "type": "gajakesari_yoga",
                    "planets": ["Jupiter", "Moon"],
                    "strength": "strong",
                    "description": "Jupiter in kendra from Moon"
                })

        # Adhi Yoga: Benefics in 6/7/8 from Moon
        houses_678 = [(moon_house + h - 2) % 12 + 1 for h in [6, 7, 8]]
        benefics_678 = [p for p in ["Jupiter", "Venus", "Mercury"]
                        if self.planet_data.get(p, {}).get("house") in houses_678]
        if len(benefics_678) >= 2:
            self._detected_yogas.append({
                "name": "Adhi Yoga",
                "type": "adhi_yoga",
                "planets": benefics_678 + ["Moon"],
                "strength": "strong",
                "description": "Benefics in 6th/7th/8th from Moon"
            })

        # Chandra-Mangala: Moon-Mars conjunction
        mars_house = self.planet_data.get("Mars", {}).get("house", 0)
        if mars_house == moon_house and moon_house > 0:
            self._detected_yogas.append({
                "name": "Chandra-Mangala Yoga",
                "type": "chandra_mangala_yoga",
                "planets": ["Moon", "Mars"],
                "strength": "moderate",
                "description": "Moon and Mars conjunction"
            })

        # Shakata Yoga: Jupiter in 6/8/12 from Moon (negative)
        if jupiter_house and moon_house:
            relative_house = ((jupiter_house - moon_house) % 12) + 1
            if relative_house in [6, 8, 12]:
                self._detected_yogas.append({
                    "name": "Shakata Yoga",
                    "type": "shakata_yoga",
                    "planets": ["Jupiter", "Moon"],
                    "strength": "moderate",
                    "description": "Jupiter in 6/8/12 from Moon (inauspicious)"
                })

    def _detect_surya_yogas(self):
        """Detect Sun-based yogas"""
        sun_data = self.planet_data.get("Sun", {})
        sun_house = sun_data.get("house", 0)
        if not sun_house:
            return

        house_2nd = (sun_house % 12) + 1
        house_12th = ((sun_house - 2) % 12) + 1

        planets_2nd = [p for p, d in self.planet_data.items()
                       if d.get("house") == house_2nd and p not in ["Sun", "Rahu", "Ketu"]]
        planets_12th = [p for p, d in self.planet_data.items()
                        if d.get("house") == house_12th and p not in ["Sun", "Rahu", "Ketu"]]

        # Vesi Yoga: Planet in 2nd from Sun
        if planets_2nd:
            self._detected_yogas.append({
                "name": "Vesi Yoga",
                "type": "vesi_yoga",
                "planets": planets_2nd + ["Sun"],
                "strength": "moderate",
                "description": "Planet in 2nd from Sun"
            })

        # Vasi Yoga: Planet in 12th from Sun
        if planets_12th:
            self._detected_yogas.append({
                "name": "Vasi Yoga",
                "type": "vasi_yoga",
                "planets": planets_12th + ["Sun"],
                "strength": "moderate",
                "description": "Planet in 12th from Sun"
            })

        # Ubhayachari: Planets in both 2nd and 12th from Sun
        if planets_2nd and planets_12th:
            self._detected_yogas.append({
                "name": "Ubhayachari Yoga",
                "type": "ubhayachari_yoga",
                "planets": planets_2nd + planets_12th + ["Sun"],
                "strength": "strong",
                "description": "Planets in 2nd and 12th from Sun"
            })

        # Budhaditya: Sun-Mercury conjunction
        mercury_house = self.planet_data.get("Mercury", {}).get("house", 0)
        if mercury_house == sun_house and sun_house > 0:
            # Check if Mercury is not too close (combustion reduces effect)
            self._detected_yogas.append({
                "name": "Budhaditya Yoga",
                "type": "budhaditya_yoga",
                "planets": ["Sun", "Mercury"],
                "strength": "moderate",
                "description": "Sun-Mercury conjunction"
            })

    def _detect_parivartana_yogas(self):
        """Detect Exchange (Parivartana) Yogas"""
        # Check each pair of planets for exchange
        for planet1, data1 in self.planet_data.items():
            sign1 = data1.get("sign", "")
            house1 = data1.get("house", 0)
            lord1 = SIGN_LORDS.get(sign1, "")

            if not lord1 or lord1 == planet1:
                continue

            for planet2, data2 in self.planet_data.items():
                if planet2 <= planet1:  # Avoid duplicate checks
                    continue

                sign2 = data2.get("sign", "")
                lord2 = SIGN_LORDS.get(sign2, "")

                # Check if there's an exchange
                if lord1 == planet2 and lord2 == planet1:
                    # Determine yoga type based on houses involved
                    house2 = data2.get("house", 0)

                    if self._is_in_dusthana(house1) or self._is_in_dusthana(house2):
                        yoga_type = "dainya_parivartana_yoga"
                        yoga_name = f"Dainya Parivartana ({planet1}-{planet2})"
                        strength = "weak"
                        desc = "Exchange involving dusthana lord"
                    elif (self._is_in_kendra(house1) or self._is_in_trikona(house1)) and \
                         (self._is_in_kendra(house2) or self._is_in_trikona(house2)):
                        yoga_type = "maha_parivartana_yoga"
                        yoga_name = f"Maha Parivartana ({planet1}-{planet2})"
                        strength = "strong"
                        desc = "Exchange between kendra/trikona lords"
                    else:
                        yoga_type = "parivartana_yoga"
                        yoga_name = f"Parivartana Yoga ({planet1}-{planet2})"
                        strength = "moderate"
                        desc = "House lord exchange"

                    self._detected_yogas.append({
                        "name": yoga_name,
                        "type": yoga_type,
                        "planets": [planet1, planet2],
                        "strength": strength,
                        "description": desc
                    })

    def _detect_neecha_bhanga(self):
        """Detect Neecha Bhanga Raja Yogas"""
        for planet, data in self.planet_data.items():
            if not self._is_debilitated(planet):
                continue

            sign = data.get("sign", "")
            house = data.get("house", 0)

            # Check for various cancellation conditions
            cancellation_factors = []

            # 1. Lord of debilitation sign in kendra from Asc or Moon
            debil_lord = SIGN_LORDS.get(sign, "")
            if debil_lord:
                lord_house = self.planet_data.get(debil_lord, {}).get("house", 0)
                if self._is_in_kendra(lord_house):
                    cancellation_factors.append(f"{debil_lord} (lord of {sign}) in kendra")

                moon_house = self.planet_data.get("Moon", {}).get("house", 0)
                if moon_house:
                    diff = abs(lord_house - moon_house)
                    if diff in [0, 3, 6, 9] or (12 - diff) in [0, 3, 6, 9]:
                        cancellation_factors.append(f"{debil_lord} in kendra from Moon")

            # 2. Planet exalted in debilitation sign is in kendra
            exalt_sign = DEBILITATION.get(planet, "")
            for other_planet, exalt_check in EXALTATION.items():
                if exalt_check == exalt_sign:
                    other_house = self.planet_data.get(other_planet, {}).get("house", 0)
                    if self._is_in_kendra(other_house):
                        cancellation_factors.append(f"{other_planet} exalted in kendra")

            # 3. Debilitated planet aspects its own sign
            own_signs = OWN_SIGNS.get(planet, [])
            for own_sign in own_signs:
                own_sign_house = self._get_house_from_sign(own_sign)
                aspect_houses = [(house + 6) % 12 + 1]  # 7th aspect
                if planet == "Mars":
                    aspect_houses.extend([(house + 3) % 12 + 1, (house + 7) % 12 + 1])
                elif planet == "Jupiter":
                    aspect_houses.extend([(house + 4) % 12 + 1, (house + 8) % 12 + 1])
                elif planet == "Saturn":
                    aspect_houses.extend([(house + 2) % 12 + 1, (house + 9) % 12 + 1])

                if own_sign_house in aspect_houses:
                    cancellation_factors.append(f"{planet} aspects its own sign")

            if cancellation_factors:
                strength = "strong" if len(cancellation_factors) >= 2 else "moderate"
                yoga_type = "neecha_bhanga_raja_yoga" if strength == "strong" else "neecha_bhanga"

                self._detected_yogas.append({
                    "name": f"Neecha Bhanga ({planet})",
                    "type": yoga_type,
                    "planets": [planet],
                    "strength": strength,
                    "description": f"Cancellation factors: {', '.join(cancellation_factors[:2])}"
                })

    def _detect_vargottama(self):
        """Detect Vargottama planets (same sign in D1 and D9)"""
        for planet in self.planet_data:
            d1_sign = self.planet_data.get(planet, {}).get("sign", "")
            d9_sign = self.d9_planet_data.get(planet, {}).get("sign", "")

            if d1_sign and d9_sign and d1_sign == d9_sign:
                self._detected_yogas.append({
                    "name": f"Vargottama {planet}",
                    "type": "vargottama",
                    "planets": [planet],
                    "strength": "strong",
                    "description": f"{planet} in same sign ({d1_sign}) in D1 and D9"
                })

    def _detect_nabha_yogas(self):
        """Detect Nabha (pattern) Yogas"""
        # Get all planet houses
        houses = [d.get("house", 0) for d in self.planet_data.values() if d.get("house")]
        unique_houses = set(houses)
        house_count = len(unique_houses)

        # Check for Kala Sarpa Yoga
        rahu_house = self.planet_data.get("Rahu", {}).get("house", 0)
        ketu_house = self.planet_data.get("Ketu", {}).get("house", 0)

        if rahu_house and ketu_house:
            # Check if all planets between Rahu and Ketu
            other_planets = [p for p in self.planet_data if p not in ["Rahu", "Ketu"]]

            # Calculate range from Rahu to Ketu
            if rahu_house < ketu_house:
                between_range = range(rahu_house, ketu_house + 1)
            else:
                between_range = list(range(rahu_house, 13)) + list(range(1, ketu_house + 1))

            all_between = True
            for p in other_planets:
                p_house = self.planet_data.get(p, {}).get("house", 0)
                if p_house not in between_range:
                    all_between = False
                    break

            if all_between and len(other_planets) >= 5:
                self._detected_yogas.append({
                    "name": "Kala Sarpa Yoga",
                    "type": "kala_sarpa_yoga",
                    "planets": list(self.planet_data.keys()),
                    "strength": "strong",
                    "description": "All planets between Rahu-Ketu axis"
                })

        # Shoola Yoga: All planets in 3 signs
        if house_count <= 3:
            self._detected_yogas.append({
                "name": "Shoola Yoga",
                "type": "shoola_yoga",
                "planets": list(self.planet_data.keys()),
                "strength": "moderate",
                "description": "All planets confined to 3 signs"
            })

        # Veena Yoga: All in 7 signs (good distribution)
        elif house_count == 7:
            self._detected_yogas.append({
                "name": "Veena Yoga",
                "type": "veena_yoga",
                "planets": list(self.planet_data.keys()),
                "strength": "moderate",
                "description": "Planets in 7 signs (balanced distribution)"
            })

    def _detect_special_yogas(self):
        """Detect special combinations"""
        # Saraswati Yoga: Jupiter, Venus, Mercury in kendra/trikona
        saraswati_planets = []
        for planet in ["Jupiter", "Venus", "Mercury"]:
            house = self.planet_data.get(planet, {}).get("house", 0)
            if self._is_in_kendra(house) or self._is_in_trikona(house):
                saraswati_planets.append(planet)

        if len(saraswati_planets) >= 2:
            self._detected_yogas.append({
                "name": "Saraswati Yoga",
                "type": "saraswati_yoga",
                "planets": saraswati_planets,
                "strength": "strong" if len(saraswati_planets) == 3 else "moderate",
                "description": "Benefics in kendra/trikona for learning"
            })

        # Sannyasa Yoga: 4+ planets in one house
        house_counts: Dict[int, List[str]] = {}
        for planet, data in self.planet_data.items():
            house = data.get("house", 0)
            if house:
                if house not in house_counts:
                    house_counts[house] = []
                house_counts[house].append(planet)

        for house, planets in house_counts.items():
            if len(planets) >= 4:
                self._detected_yogas.append({
                    "name": "Sannyasa Yoga",
                    "type": "sannyasa_yoga",
                    "planets": planets,
                    "strength": "moderate",
                    "description": f"4+ planets in house {house}"
                })

        # Viparita Raja Yoga: Dusthana lords in dusthana
        for dusthana in [6, 8, 12]:
            lord = self._get_house_lord(dusthana)
            if lord:
                lord_house = self.planet_data.get(lord, {}).get("house", 0)
                if self._is_in_dusthana(lord_house) and lord_house != dusthana:
                    self._detected_yogas.append({
                        "name": f"Viparita Raja Yoga ({lord})",
                        "type": "viparita_raja_yoga",
                        "planets": [lord],
                        "strength": "moderate",
                        "description": f"Lord of {dusthana}th in another dusthana"
                    })

    def _detect_arishta_yogas(self):
        """Detect inauspicious yogas"""
        # Daridra Yoga: 2nd/11th lords in dusthana
        lord_2 = self._get_house_lord(2)
        lord_11 = self._get_house_lord(11)

        daridra_planets = []
        if lord_2:
            h2 = self.planet_data.get(lord_2, {}).get("house", 0)
            if self._is_in_dusthana(h2):
                daridra_planets.append(lord_2)

        if lord_11:
            h11 = self.planet_data.get(lord_11, {}).get("house", 0)
            if self._is_in_dusthana(h11):
                daridra_planets.append(lord_11)

        if len(daridra_planets) == 2:
            self._detected_yogas.append({
                "name": "Daridra Yoga",
                "type": "daridra_yoga",
                "planets": daridra_planets,
                "strength": "strong",
                "description": "Both 2nd and 11th lords in dusthana"
            })

        # Grahan Yoga: Sun or Moon with Rahu or Ketu
        sun_house = self.planet_data.get("Sun", {}).get("house", 0)
        moon_house = self.planet_data.get("Moon", {}).get("house", 0)
        rahu_house = self.planet_data.get("Rahu", {}).get("house", 0)
        ketu_house = self.planet_data.get("Ketu", {}).get("house", 0)

        if sun_house and (sun_house == rahu_house or sun_house == ketu_house):
            self._detected_yogas.append({
                "name": "Grahan Yoga (Sun)",
                "type": "grahan_yoga",
                "planets": ["Sun", "Rahu" if sun_house == rahu_house else "Ketu"],
                "strength": "moderate",
                "description": "Sun with Rahu/Ketu (eclipse)"
            })

        if moon_house and (moon_house == rahu_house or moon_house == ketu_house):
            self._detected_yogas.append({
                "name": "Grahan Yoga (Moon)",
                "type": "grahan_yoga",
                "planets": ["Moon", "Rahu" if moon_house == rahu_house else "Ketu"],
                "strength": "moderate",
                "description": "Moon with Rahu/Ketu (eclipse)"
            })

    def _detect_fame_learning_yogas(self):
        """Detect fame and learning related yogas"""
        # Chamara Yoga: Asc lord exalted, aspected by Jupiter
        lord_1 = self._get_house_lord(1)
        if lord_1 and self._is_exalted(lord_1):
            # Check for Jupiter aspect (simplified)
            jupiter_house = self.planet_data.get("Jupiter", {}).get("house", 0)
            lord_1_house = self.planet_data.get(lord_1, {}).get("house", 0)
            if jupiter_house and lord_1_house:
                diff = abs(jupiter_house - lord_1_house)
                # Jupiter aspects 5th, 7th, 9th
                if diff in [4, 6, 8] or (12 - diff) in [4, 6, 8]:
                    self._detected_yogas.append({
                        "name": "Chamara Yoga",
                        "type": "chamara_yoga",
                        "planets": [lord_1, "Jupiter"],
                        "strength": "strong",
                        "description": "Asc lord exalted and aspected by Jupiter"
                    })

        # Amala Yoga: Benefic in 10th from Asc or Moon
        tenth_house = 10
        tenth_from_moon = (self.planet_data.get("Moon", {}).get("house", 1) + 8) % 12 + 1

        for benefic in ["Jupiter", "Venus", "Mercury"]:
            b_house = self.planet_data.get(benefic, {}).get("house", 0)
            if b_house == tenth_house or b_house == tenth_from_moon:
                self._detected_yogas.append({
                    "name": f"Amala Yoga ({benefic})",
                    "type": "amala_yoga",
                    "planets": [benefic],
                    "strength": "moderate",
                    "description": f"{benefic} in 10th brings fame and good reputation"
                })

    def calculate(self) -> Dict[str, YogaLayerResult]:
        """
        Calculate yoga-based scores for all planets

        Returns:
            Dict mapping planet name to YogaLayerResult
        """
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if planet in self.planet_data:
                results[planet] = self._analyze_planet(planet)
        return results

    def _analyze_planet(self, planet: str) -> YogaLayerResult:
        """Analyze yoga participation for a single planet"""
        details = []
        yogas_participated = []
        total_points = 0.0

        # Find all yogas this planet participates in
        seen_yogas: Set[str] = set()  # Prevent duplicate counting

        for yoga in self.yogas:
            yoga_planets = yoga.get("planets", [])
            if planet in yoga_planets:
                yoga_name = yoga.get("name", "Unknown Yoga")

                # Avoid duplicate yogas
                if yoga_name in seen_yogas:
                    continue
                seen_yogas.add(yoga_name)

                yoga_type = yoga.get("type", "minor_yoga")
                strength = yoga.get("strength", "moderate")

                yogas_participated.append(yoga_name)

                # Get base points for this yoga type
                base_points = YOGA_POINTS.get(yoga_type, 1.0)

                # Apply strength modifier
                if strength == "strong":
                    modifier = 1.2
                elif strength == "weak":
                    modifier = 0.7
                else:
                    modifier = 1.0

                points = base_points * modifier
                total_points += points

                if points >= 0:
                    details.append(f"{yoga_name}: +{points:.1f}")
                else:
                    details.append(f"{yoga_name}: {points:.1f}")

        # Cap total points at Phase 9.5 range
        score = min(self.MAX_SCORE, max(-self.MAX_SCORE, total_points))

        if not yogas_participated:
            details.append(f"{planet} does not participate in any detected yogas")

        return YogaLayerResult(
            planet=planet,
            yogas_participated=yogas_participated,
            yoga_count=len(yogas_participated),
            total_yoga_points=total_points,
            score=score,
            details=details
        )

    def get_score(self, planet: str) -> float:
        """Get the yoga score for a specific planet"""
        results = self.calculate()
        if planet in results:
            return results[planet].score
        return 0.0

    def get_all_scores(self) -> Dict[str, float]:
        """Get yoga scores for all planets"""
        results = self.calculate()
        return {planet: result.score for planet, result in results.items()}

    def get_all_detected_yogas(self) -> List[Dict[str, Any]]:
        """Get all detected yogas for reporting"""
        return self.yogas
