"""
Phase 8.5 Layer: Tara Bala (Star Strength) House Analysis (±3 points)

Tara Bala analyzes the relationship between the Janma Nakshatra (birth star)
and the nakshatras of house lords. There are 9 Taras that cycle repeatedly,
each with different qualities.

The 9 Taras (starting from Janma Nakshatra):
1. Janma (Birth) - Average, identity
2. Sampat (Wealth) - Very Good, prosperity
3. Vipat (Danger) - Bad, obstacles
4. Kshema (Well-being) - Very Good, comfort
5. Pratyari (Obstruction) - Bad, enemies
6. Sadhaka (Achievement) - Very Good, success
7. Vadha (Death) - Bad, suffering
8. Mitra (Friend) - Very Good, friendship
9. Ati-Mitra (Great Friend) - Very Good, excellent support

When house lord is in a favorable Tara from Janma Nakshatra, the house benefits.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import IntEnum


class Planet(IntEnum):
    """Planet identifiers."""
    SUN = 0
    MOON = 1
    MARS = 2
    MERCURY = 3
    JUPITER = 4
    VENUS = 5
    SATURN = 6
    RAHU = 7
    KETU = 8


# Sign rulers
SIGN_LORDS = {
    1: Planet.MARS,      # Aries
    2: Planet.VENUS,     # Taurus
    3: Planet.MERCURY,   # Gemini
    4: Planet.MOON,      # Cancer
    5: Planet.SUN,       # Leo
    6: Planet.MERCURY,   # Virgo
    7: Planet.VENUS,     # Libra
    8: Planet.MARS,      # Scorpio
    9: Planet.JUPITER,   # Sagittarius
    10: Planet.SATURN,   # Capricorn
    11: Planet.SATURN,   # Aquarius
    12: Planet.JUPITER,  # Pisces
}

# 27 Nakshatras with their names
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira',
    'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha', 'Magha',
    'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati',
    'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha',
    'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada',
    'Uttara Bhadrapada', 'Revati'
]


@dataclass
class TaraInfo:
    """Information about a Tara."""
    number: int
    name: str
    name_ru: str
    quality: str  # 'good', 'bad', 'neutral'
    influence: float


# The 9 Taras with their qualities
TARAS = {
    1: TaraInfo(1, 'Janma', 'Джанма (Рождение)', 'neutral', 0.0),
    2: TaraInfo(2, 'Sampat', 'Сампат (Богатство)', 'good', 0.8),
    3: TaraInfo(3, 'Vipat', 'Випат (Опасность)', 'bad', -0.6),
    4: TaraInfo(4, 'Kshema', 'Кшема (Благополучие)', 'good', 0.7),
    5: TaraInfo(5, 'Pratyari', 'Пратьяри (Препятствие)', 'bad', -0.5),
    6: TaraInfo(6, 'Sadhaka', 'Садхака (Достижение)', 'good', 0.8),
    7: TaraInfo(7, 'Vadha', 'Вадха (Смерть)', 'bad', -0.7),
    8: TaraInfo(8, 'Mitra', 'Митра (Друг)', 'good', 0.6),
    9: TaraInfo(9, 'Ati-Mitra', 'Ати-Митра (Лучший Друг)', 'good', 0.9),
}


@dataclass
class TaraResult:
    """Result from Tara Bala analysis for a house."""
    house: int
    house_lord: Optional[int]
    lord_nakshatra: str
    tara_number: int
    tara_name: str
    tara_quality: str
    raw_influence: float
    final_score: float
    details: Dict = field(default_factory=dict)


class TaraBalLayer:
    """
    Phase 8.5 Layer: Tara Bala House Strength (±3 points)

    Analyzes the Tara relationship between Janma Nakshatra
    and each house lord's nakshatra.

    Score range: ±3 points
    """

    WEIGHT = 0.02  # 2% of total house score
    MAX_POINTS = 3.0

    def __init__(self, chart_data: Dict):
        """
        Initialize with chart data.

        Args:
            chart_data: Full chart data including Moon and planets
        """
        self.chart_data = chart_data
        self.planets = self._extract_planets()
        self.lagna_sign = self._get_lagna_sign()
        self.janma_nakshatra = self._get_janma_nakshatra()

    def _extract_planets(self) -> Dict[int, Dict]:
        """Extract planet data from chart data."""
        planets = {}

        # Try different formats
        if 'vargas' in self.chart_data:
            d1 = self.chart_data.get('vargas', {}).get('D1', {})
        elif 'D1' in self.chart_data:
            d1 = self.chart_data.get('D1', {})
        else:
            d1 = self.chart_data

        planet_list = d1.get('planets', [])

        # Map planet names to enum
        name_map = {
            'Sun': Planet.SUN, 'Moon': Planet.MOON, 'Mars': Planet.MARS,
            'Mercury': Planet.MERCURY, 'Jupiter': Planet.JUPITER,
            'Venus': Planet.VENUS, 'Saturn': Planet.SATURN,
            'Rahu': Planet.RAHU, 'Ketu': Planet.KETU,
            'Солнце': Planet.SUN, 'Луна': Planet.MOON, 'Марс': Planet.MARS,
            'Меркурий': Planet.MERCURY, 'Юпитер': Planet.JUPITER,
            'Венера': Planet.VENUS, 'Сатурн': Planet.SATURN,
            'Раху': Planet.RAHU, 'Кету': Planet.KETU
        }

        for p in planet_list:
            name = p.get('name', '')
            if name in name_map:
                planet_id = name_map[name]
                planets[planet_id] = {
                    'longitude': p.get('longitude', 0.0),
                    'nakshatra': self._longitude_to_nakshatra(p.get('longitude', 0.0))
                }

        return planets

    def _get_lagna_sign(self) -> int:
        """Get ascendant sign number (1-12)."""
        if 'vargas' in self.chart_data:
            d1 = self.chart_data.get('vargas', {}).get('D1', {})
        elif 'D1' in self.chart_data:
            d1 = self.chart_data.get('D1', {})
        else:
            d1 = self.chart_data

        asc = d1.get('ascendant', {})
        sign_str = asc.get('sign', 'Aries')
        return self._sign_to_number(sign_str)

    def _sign_to_number(self, sign: str) -> int:
        """Convert sign name to number (1-12)."""
        signs = {
            'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
            'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
            'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12,
            'Овен': 1, 'Телец': 2, 'Близнецы': 3, 'Рак': 4,
            'Лев': 5, 'Дева': 6, 'Весы': 7, 'Скорпион': 8,
            'Стрелец': 9, 'Козерог': 10, 'Водолей': 11, 'Рыбы': 12
        }
        return signs.get(sign, 1)

    def _longitude_to_nakshatra(self, longitude: float) -> int:
        """
        Convert longitude to nakshatra number (1-27).
        Each nakshatra spans 13°20' (13.333...°)
        """
        # Normalize longitude
        while longitude < 0:
            longitude += 360
        while longitude >= 360:
            longitude -= 360

        # Calculate nakshatra (0-26)
        nakshatra = int(longitude / (360 / 27))
        return nakshatra + 1  # 1-27

    def _get_janma_nakshatra(self) -> int:
        """Get Janma Nakshatra (Moon's nakshatra)."""
        moon_data = self.planets.get(Planet.MOON, {})
        return moon_data.get('nakshatra', 1)

    def _calculate_tara(self, nakshatra: int) -> TaraInfo:
        """
        Calculate which Tara a nakshatra falls into relative to Janma.

        The Tara cycle repeats every 9 nakshatras:
        - Nakshatra 1 from Janma = Tara 1 (Janma)
        - Nakshatra 2 from Janma = Tara 2 (Sampat)
        - etc.
        """
        # Calculate distance from Janma nakshatra
        distance = nakshatra - self.janma_nakshatra
        if distance <= 0:
            distance += 27

        # Tara cycles every 9 nakshatras
        tara_number = ((distance - 1) % 9) + 1

        return TARAS[tara_number]

    def _get_house_lord(self, house: int) -> Optional[Planet]:
        """Get the lord of a house."""
        # Calculate which sign rules this house
        house_sign = ((self.lagna_sign - 1 + house - 1) % 12) + 1
        return SIGN_LORDS.get(house_sign)

    def calculate(self) -> Dict[int, TaraResult]:
        """
        Calculate Tara Bala for all 12 houses.

        Returns:
            Dictionary mapping house number to TaraResult
        """
        results = {}

        for house in range(1, 13):
            house_lord = self._get_house_lord(house)

            if house_lord is not None and house_lord in self.planets:
                lord_data = self.planets[house_lord]
                lord_nakshatra = lord_data.get('nakshatra', 1)

                # Calculate Tara for this lord
                tara = self._calculate_tara(lord_nakshatra)

                raw_influence = tara.influence

                # Normalize to ±3 range
                final_score = raw_influence * self.MAX_POINTS
                final_score = max(-self.MAX_POINTS, min(self.MAX_POINTS, final_score))

                results[house] = TaraResult(
                    house=house,
                    house_lord=house_lord,
                    lord_nakshatra=NAKSHATRAS[lord_nakshatra - 1],
                    tara_number=tara.number,
                    tara_name=tara.name,
                    tara_quality=tara.quality,
                    raw_influence=raw_influence,
                    final_score=final_score,
                    details={
                        'janma_nakshatra': NAKSHATRAS[self.janma_nakshatra - 1],
                        'tara_name_ru': tara.name_ru
                    }
                )
            else:
                # No lord data available
                results[house] = TaraResult(
                    house=house,
                    house_lord=house_lord,
                    lord_nakshatra='Unknown',
                    tara_number=1,
                    tara_name='Janma',
                    tara_quality='neutral',
                    raw_influence=0.0,
                    final_score=0.0,
                    details={
                        'janma_nakshatra': NAKSHATRAS[self.janma_nakshatra - 1],
                        'error': 'House lord not found'
                    }
                )

        return results

    def calculate_for_houses(self) -> Dict[int, float]:
        """
        Calculate simplified scores for integration with HouseScoreCalculator.

        Returns:
            Dictionary mapping house number (1-12) to score (±3)
        """
        results = self.calculate()
        return {house: result.final_score for house, result in results.items()}

    def get_report(self) -> str:
        """Generate human-readable report."""
        results = self.calculate()

        lines = [
            "=" * 60,
            "TARA BALA (STAR STRENGTH) ANALYSIS",
            "=" * 60,
            f"Janma Nakshatra: {NAKSHATRAS[self.janma_nakshatra - 1]}",
            "",
            "House Analysis:",
        ]

        for house in range(1, 13):
            r = results[house]
            quality_symbol = '+' if r.tara_quality == 'good' else ('-' if r.tara_quality == 'bad' else '=')
            lines.append(
                f"  House {house}: Lord in {r.lord_nakshatra} -> "
                f"Tara {r.tara_number} ({r.tara_name}) [{quality_symbol}] = {r.final_score:+.2f}"
            )

        lines.append("\nTara Reference:")
        for num, tara in TARAS.items():
            quality_symbol = '+' if tara.quality == 'good' else ('-' if tara.quality == 'bad' else '=')
            lines.append(f"  {num}. {tara.name} ({tara.name_ru}) [{quality_symbol}]")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
