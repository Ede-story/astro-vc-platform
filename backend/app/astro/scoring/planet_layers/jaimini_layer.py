"""
Jaimini Layer - Chara Karaka based planetary strength (±10 points)

Jaimini astrology is a unique system that uses Chara (movable) Karakas based on
planetary degrees rather than fixed natural significations.

Components:
1. Chara Karaka Status: AK, AmK, BK, etc.
   - Atmakaraka (AK): Soul significator - highest importance
   - Amatya Karaka (AmK): Career significator
   - Bhratru Karaka (BK): Siblings significator
   - Matru Karaka (MK): Mother significator
   - Pitru Karaka (PK): Father significator
   - Putra Karaka (PuK): Children significator
   - Gnati Karaka (GK): Enemy/disease significator
   - Dara Karaka (DK): Spouse significator

2. Karakamsha Analysis: AK's position in D9
   - Sign where AK is placed in Navamsha
   - Very important for soul's desires and destiny

3. Argala (Intervention): Planets in 2nd, 4th, 11th, 5th from planet
   - Benefics giving positive argala = support
   - Malefics = obstruction

Score Contribution: -10 to +10 points
- AK status: +8 to +10
- AmK status: +5 to +7
- Other karakas: +2 to +4
- Positive argala: +2 to +5
- Negative argala: -2 to -5
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class JaiminiScore:
    """Result from Jaimini analysis"""
    planet: str
    raw_score: float
    karaka_score: float  # From chara karaka status
    argala_score: float  # From argala analysis
    special_score: float  # From special Jaimini factors
    details: List[str] = field(default_factory=list)


class JaiminiPlanetLayer:
    """
    Calculates planet strength based on Jaimini system

    Weight: 10% of total planet score
    Range: -10 to +10 points
    """

    WEIGHT = 0.10  # 10% of total score
    MAX_CONTRIBUTION = 10.0
    MIN_CONTRIBUTION = -10.0

    # Karaka importance ranking and scores
    KARAKA_SCORES = {
        "AK": 10.0,   # Atmakaraka - most important
        "AmK": 7.0,   # Amatya Karaka - second most important
        "BK": 4.0,    # Bhratru Karaka
        "MK": 3.5,    # Matru Karaka
        "PK": 3.5,    # Pitru Karaka
        "PuK": 3.0,   # Putra Karaka
        "GK": -2.0,   # Gnati Karaka - negative (enemies/diseases)
        "DK": 4.0,    # Dara Karaka - spouse
    }

    # Russian karaka codes to English
    KARAKA_RU_TO_EN = {
        "АК": "AK",
        "АмК": "AmK",
        "БК": "BK",
        "МК": "MK",
        "ПК": "PK",
        "ПуК": "PuK",
        "ГК": "GK",
        "ДК": "DK",
    }

    # Zodiac signs
    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    # Natural benefics and malefics
    NATURAL_BENEFICS = ["Jupiter", "Venus", "Mercury", "Moon"]  # Mercury when alone, Moon when waxing
    NATURAL_MALEFICS = ["Saturn", "Mars", "Sun", "Rahu", "Ketu"]

    def __init__(
        self,
        d1_chart: Dict[str, Any],
        d9_chart: Dict[str, Any] = None,
        chara_karakas: Dict[str, Any] = None
    ):
        """
        Initialize with chart data and chara karakas

        Args:
            d1_chart: D1 chart data
            d9_chart: D9 (Navamsha) chart data
            chara_karakas: Pre-calculated chara karaka assignments
        """
        self.d1 = d1_chart
        self.d9 = d9_chart or {}
        self.chara_karakas = chara_karakas or {}
        self.planets = self._extract_planets()
        self.karaka_map = self._build_karaka_map()

    def _extract_planets(self) -> Dict[str, Dict[str, Any]]:
        """Extract planet positions from D1 chart"""
        planets = {}
        for planet_data in self.d1.get("planets", []):
            name = planet_data.get("name", "")
            eng_name = self._to_english(name)
            if eng_name:
                planets[eng_name] = {
                    "sign": planet_data.get("sign", ""),
                    "degree": planet_data.get("longitude", 0) % 30,
                    "house": planet_data.get("house", 1),
                    "longitude": planet_data.get("longitude", 0),
                }
        return planets

    def _to_english(self, name: str) -> Optional[str]:
        """Convert planet name to English"""
        mapping = {
            "Солнце": "Sun", "Sun": "Sun",
            "Луна": "Moon", "Moon": "Moon",
            "Марс": "Mars", "Mars": "Mars",
            "Меркурий": "Mercury", "Mercury": "Mercury",
            "Юпитер": "Jupiter", "Jupiter": "Jupiter",
            "Венера": "Venus", "Venus": "Venus",
            "Сатурн": "Saturn", "Saturn": "Saturn",
            "Раху": "Rahu", "Rahu": "Rahu",
            "Кету": "Ketu", "Ketu": "Ketu",
        }
        return mapping.get(name)

    def _build_karaka_map(self) -> Dict[str, str]:
        """Build mapping from planet to karaka code"""
        karaka_map = {}

        karakas = self.chara_karakas.get("karakas", [])
        for karaka in karakas:
            planet = karaka.get("planet", "")
            code = karaka.get("karaka_code", "")

            # Convert to English
            eng_planet = self._to_english(planet)
            eng_code = self.KARAKA_RU_TO_EN.get(code, code)

            if eng_planet and eng_code:
                karaka_map[eng_planet] = eng_code

        return karaka_map

    def _get_sign_index(self, sign: str) -> int:
        """Get 0-based index of sign"""
        try:
            return self.SIGNS.index(sign)
        except ValueError:
            return 0

    def _house_from_sign(self, from_sign: str, to_sign: str) -> int:
        """Calculate house number from one sign to another (1-12)"""
        from_idx = self._get_sign_index(from_sign)
        to_idx = self._get_sign_index(to_sign)
        return ((to_idx - from_idx) % 12) + 1

    def _get_ascendant_sign(self) -> str:
        """Get D1 ascendant sign"""
        asc_data = self.d1.get("ascendant", {})
        return asc_data.get("sign", "Aries")

    def calculate_karaka_score(self, planet: str) -> tuple:
        """
        Calculate score based on chara karaka status

        Returns:
            (score, details list)
        """
        score = 0.0
        details = []

        karaka = self.karaka_map.get(planet)
        if karaka:
            karaka_score = self.KARAKA_SCORES.get(karaka, 0)
            score = karaka_score

            if karaka == "AK":
                details.append(f"Atmakaraka (AK): Soul significator (+{karaka_score})")
            elif karaka == "AmK":
                details.append(f"Amatya Karaka (AmK): Career significator (+{karaka_score})")
            elif karaka == "GK":
                details.append(f"Gnati Karaka (GK): Enemy/disease significator ({karaka_score})")
            elif karaka == "DK":
                details.append(f"Dara Karaka (DK): Spouse significator (+{karaka_score})")
            else:
                details.append(f"{karaka}: Chara Karaka (+{karaka_score})")
        else:
            details.append("No significant karaka status")

        return score, details

    def calculate_argala(self, planet: str) -> tuple:
        """
        Calculate Argala (intervention) score

        Argala houses from planet:
        - 2nd house: Dhana argala (wealth intervention)
        - 4th house: Sukha argala (happiness intervention)
        - 11th house: Labha argala (gains intervention)
        - 5th house: Putra argala (children/merit intervention)

        Counter argala (virodha):
        - 12th counters 2nd
        - 10th counters 4th
        - 3rd counters 11th
        - 9th counters 5th

        Returns:
            (score, details list)
        """
        score = 0.0
        details = []

        if planet not in self.planets:
            return 0.0, ["Planet not found"]

        planet_sign = self.planets[planet]["sign"]

        # Argala positions and their meanings
        argala_houses = {
            2: ("Dhana", 12),   # (name, counter house)
            4: ("Sukha", 10),
            11: ("Labha", 3),
            5: ("Putra", 9),
        }

        for argala_house, (name, counter_house) in argala_houses.items():
            # Find planets in argala house from this planet
            argala_planets = []
            counter_planets = []

            for other_planet, data in self.planets.items():
                if other_planet == planet:
                    continue

                house_from_planet = self._house_from_sign(planet_sign, data["sign"])

                if house_from_planet == argala_house:
                    argala_planets.append(other_planet)
                elif house_from_planet == counter_house:
                    counter_planets.append(other_planet)

            # Calculate net argala
            if argala_planets:
                # Count benefics vs malefics
                benefic_argala = sum(1 for p in argala_planets if p in self.NATURAL_BENEFICS)
                malefic_argala = sum(1 for p in argala_planets if p in self.NATURAL_MALEFICS)

                benefic_counter = sum(1 for p in counter_planets if p in self.NATURAL_BENEFICS)
                malefic_counter = sum(1 for p in counter_planets if p in self.NATURAL_MALEFICS)

                # Net effect: argala - counter
                net_benefic = benefic_argala - benefic_counter
                net_malefic = malefic_argala - malefic_counter

                if net_benefic > 0:
                    argala_score = net_benefic * 1.5
                    score += argala_score
                    details.append(f"{name} argala: benefic support (+{argala_score:.1f})")

                if net_malefic > 0:
                    argala_score = net_malefic * -1.0
                    score += argala_score
                    details.append(f"{name} argala: malefic obstruction ({argala_score:.1f})")

        return score, details

    def calculate_special_factors(self, planet: str) -> tuple:
        """
        Calculate special Jaimini factors

        1. Karakamsha analysis (for AK)
        2. Swamsha (AK in own sign in D9)
        3. Raj yoga karakas conjunction

        Returns:
            (score, details list)
        """
        score = 0.0
        details = []

        karaka = self.karaka_map.get(planet)

        # 1. Special AK factors
        if karaka == "AK":
            # Check Karakamsha (AK's position in D9)
            if self.d9:
                d9_planets = self.d9.get("planets", [])
                for p in d9_planets:
                    name = self._to_english(p.get("name", ""))
                    if name == planet:
                        d9_sign = p.get("sign", "")
                        d9_house = p.get("house", 1)

                        # AK in good houses in D9
                        if d9_house in [1, 4, 5, 7, 9, 10]:
                            score += 2.0
                            details.append(f"AK in auspicious Karakamsha house {d9_house} (+2)")

                        # AK in own/exaltation in D9
                        if self._is_strong_dignity(planet, d9_sign):
                            score += 2.0
                            details.append(f"AK has dignity in Karakamsha (+2)")
                        break

        # 2. AmK + AK conjunction/aspect
        if karaka == "AmK":
            ak_planet = None
            for p, k in self.karaka_map.items():
                if k == "AK":
                    ak_planet = p
                    break

            if ak_planet and ak_planet in self.planets and planet in self.planets:
                ak_sign = self.planets[ak_planet]["sign"]
                planet_sign = self.planets[planet]["sign"]

                # Same sign (conjunction)
                if ak_sign == planet_sign:
                    score += 3.0
                    details.append("AmK conjunct AK: Strong raj yoga karaka (+3)")
                else:
                    # Check if they aspect each other (mutual aspect)
                    house_ak_to_amk = self._house_from_sign(ak_sign, planet_sign)
                    if house_ak_to_amk in [5, 7, 9]:  # Trinal/opposition aspect
                        score += 1.5
                        details.append("AmK aspected by AK (+1.5)")

        # 3. DK with AK connection (relationship success indicator)
        if karaka == "DK":
            ak_planet = None
            for p, k in self.karaka_map.items():
                if k == "AK":
                    ak_planet = p
                    break

            if ak_planet and ak_planet in self.planets and planet in self.planets:
                ak_sign = self.planets[ak_planet]["sign"]
                planet_sign = self.planets[planet]["sign"]

                if ak_sign == planet_sign:
                    score += 2.0
                    details.append("DK conjunct AK: Soul-mate connection (+2)")

        return score, details

    def _is_strong_dignity(self, planet: str, sign: str) -> bool:
        """Check if planet has strong dignity in sign"""
        own_signs = {
            "Sun": ["Leo"],
            "Moon": ["Cancer"],
            "Mars": ["Aries", "Scorpio"],
            "Mercury": ["Gemini", "Virgo"],
            "Jupiter": ["Sagittarius", "Pisces"],
            "Venus": ["Taurus", "Libra"],
            "Saturn": ["Capricorn", "Aquarius"],
        }

        exaltation = {
            "Sun": "Aries",
            "Moon": "Taurus",
            "Mars": "Capricorn",
            "Mercury": "Virgo",
            "Jupiter": "Cancer",
            "Venus": "Pisces",
            "Saturn": "Libra",
        }

        return sign in own_signs.get(planet, []) or sign == exaltation.get(planet, "")

    def calculate(self, planet: str) -> JaiminiScore:
        """
        Calculate complete Jaimini score for a planet

        Returns:
            JaiminiScore with breakdown
        """
        all_details = []

        if planet not in self.planets:
            return JaiminiScore(
                planet=planet,
                raw_score=0,
                karaka_score=0,
                argala_score=0,
                special_score=0,
                details=["Planet not found in chart"]
            )

        # 1. Karaka status score
        karaka_score, karaka_details = self.calculate_karaka_score(planet)
        all_details.extend(karaka_details)

        # 2. Argala score
        argala_score, argala_details = self.calculate_argala(planet)
        all_details.extend(argala_details)

        # 3. Special factors
        special_score, special_details = self.calculate_special_factors(planet)
        all_details.extend(special_details)

        # Total
        raw_score = karaka_score + argala_score + special_score

        # Normalize to range
        raw_score = max(self.MIN_CONTRIBUTION, min(self.MAX_CONTRIBUTION, raw_score))

        return JaiminiScore(
            planet=planet,
            raw_score=raw_score,
            karaka_score=karaka_score,
            argala_score=argala_score,
            special_score=special_score,
            details=all_details
        )

    def calculate_all(self) -> Dict[str, JaiminiScore]:
        """Calculate Jaimini scores for all planets"""
        results = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            results[planet] = self.calculate(planet)
        return results


def calculate_jaimini_score(
    d1_chart: Dict[str, Any],
    d9_chart: Dict[str, Any],
    chara_karakas: Dict[str, Any],
    planet: str
) -> float:
    """
    Convenience function to calculate Jaimini score for a planet

    Returns score in range -10 to +10
    """
    layer = JaiminiPlanetLayer(d1_chart, d9_chart, chara_karakas)
    result = layer.calculate(planet)
    return result.raw_score


def get_jaimini_details(
    d1_chart: Dict[str, Any],
    d9_chart: Dict[str, Any],
    chara_karakas: Dict[str, Any],
    planet: str
) -> Dict[str, Any]:
    """
    Get detailed Jaimini analysis for a planet
    """
    layer = JaiminiPlanetLayer(d1_chart, d9_chart, chara_karakas)
    result = layer.calculate(planet)

    return {
        "planet": result.planet,
        "score": result.raw_score,
        "karaka_score": result.karaka_score,
        "argala_score": result.argala_score,
        "special_score": result.special_score,
        "details": result.details,
    }
