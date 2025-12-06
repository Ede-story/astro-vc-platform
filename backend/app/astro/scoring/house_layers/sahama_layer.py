"""
Phase 8.5 Layer: Sahama (Arabic Parts/Sensitive Points) House Analysis (±3 points)

Sahamas (also called Arabic Parts or Lots) are sensitive mathematical points
calculated from three chart factors. They indicate where specific life themes
manifest most strongly.

7 Primary Sahamas:
1. Punya Sahama (Fortune) - Asc + Moon - Sun (day) / Asc + Sun - Moon (night)
2. Vidya Sahama (Knowledge) - Asc + Sun - Moon
3. Vivaha Sahama (Marriage) - Asc + Venus - Saturn
4. Santana Sahama (Children) - Asc + Jupiter - Moon
5. Rajya Sahama (Power/Kingdom) - Asc + Saturn - Sun
6. Mrityu Sahama (Death) - Asc + 8th cusp - Moon
7. Dhana Sahama (Wealth) - Asc + 2nd cusp - 2nd lord

Each Sahama adds positive influence to the house where it falls.
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


@dataclass
class SahamaData:
    """Data for a single Sahama."""
    name: str
    name_ru: str
    longitude: float
    sign: int
    house: int
    significance: str
    influence: float  # Always positive for Sahamas


@dataclass
class SahamaResult:
    """Result from Sahama analysis for a house."""
    house: int
    sahamas_present: List[str]
    raw_influence: float
    final_score: float
    details: Dict = field(default_factory=dict)


class SahamaLayer:
    """
    Phase 8.5 Layer: Sahama House Influence (±3 points)

    Calculates the position of 7 Sahamas and their positive influence on houses.
    Each Sahama brings beneficial energy to the house where it falls,
    especially when related to that house's natural significations.

    Score range: ±3 points
    """

    WEIGHT = 0.02  # 2% of total house score
    MAX_POINTS = 3.0

    # Sahama definitions with significance and influence strength
    # All Sahamas are considered beneficial - they show where themes manifest
    SAHAMA_DEFS = {
        'Punya': {
            'name_ru': 'Пунья (Удача)',
            'significance': 'fortune',
            'influence': 0.8,
            'related_houses': {1, 5, 9, 11}  # Best in trines and upachaya
        },
        'Vidya': {
            'name_ru': 'Видья (Знание)',
            'significance': 'education',
            'influence': 0.6,
            'related_houses': {4, 5, 9}  # Education houses
        },
        'Vivaha': {
            'name_ru': 'Виваха (Брак)',
            'significance': 'marriage',
            'influence': 0.6,
            'related_houses': {7}  # Marriage house
        },
        'Santana': {
            'name_ru': 'Сантана (Дети)',
            'significance': 'children',
            'influence': 0.6,
            'related_houses': {5}  # Children house
        },
        'Rajya': {
            'name_ru': 'Раджья (Власть)',
            'significance': 'power',
            'influence': 0.7,
            'related_houses': {10, 11}  # Power and gains
        },
        'Mrityu': {
            'name_ru': 'Мритью (Смерть)',
            'significance': 'longevity',
            'influence': -0.3,  # Negative when in bad houses
            'related_houses': {8}  # Death/transformation house
        },
        'Dhana': {
            'name_ru': 'Дхана (Богатство)',
            'significance': 'wealth',
            'influence': 0.7,
            'related_houses': {2, 11}  # Wealth houses
        },
    }

    def __init__(self, chart_data: Dict):
        """
        Initialize with chart data.

        Args:
            chart_data: Full chart data including planets and houses
        """
        self.chart_data = chart_data
        self.planets = self._extract_planets()
        self.asc_longitude = self._get_asc_longitude()
        self.lagna_sign = self._get_lagna_sign()
        self.is_day_chart = self._is_day_chart()
        self.sahamas = self._calculate_sahamas()

    def _extract_planets(self) -> Dict[int, float]:
        """Extract planet longitudes from chart data."""
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
                planets[planet_id] = p.get('longitude', 0.0)

        return planets

    def _get_asc_longitude(self) -> float:
        """Get ascendant longitude."""
        if 'vargas' in self.chart_data:
            d1 = self.chart_data.get('vargas', {}).get('D1', {})
        elif 'D1' in self.chart_data:
            d1 = self.chart_data.get('D1', {})
        else:
            d1 = self.chart_data

        asc = d1.get('ascendant', {})
        degree = asc.get('degree', 0.0)
        sign_str = asc.get('sign', 'Aries')
        sign_num = self._sign_to_number(sign_str)

        return (sign_num - 1) * 30 + degree

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

    def _is_day_chart(self) -> bool:
        """
        Determine if this is a day or night chart.
        Day = Sun above horizon (houses 7-12 from Asc)
        """
        sun_lon = self.planets.get(Planet.SUN, 0.0)
        sun_sign = int(sun_lon / 30) + 1
        sun_house = ((sun_sign - self.lagna_sign) % 12) + 1

        # Sun in houses 7-12 = above horizon = day chart
        return sun_house >= 7

    def _normalize_longitude(self, lon: float) -> float:
        """Normalize longitude to 0-360 range."""
        while lon < 0:
            lon += 360
        while lon >= 360:
            lon -= 360
        return lon

    def _longitude_to_sign(self, lon: float) -> int:
        """Convert longitude to sign number (1-12)."""
        return int(lon / 30) + 1

    def _longitude_to_house(self, lon: float) -> int:
        """Convert longitude to house number from Lagna."""
        sign = self._longitude_to_sign(lon)
        house = ((sign - self.lagna_sign) % 12) + 1
        return house

    def _get_house_cusp(self, house: int) -> float:
        """
        Get the cusp longitude of a house.
        Using whole sign houses, cusp = start of sign.
        """
        sign = ((self.lagna_sign - 1 + house - 1) % 12) + 1
        return (sign - 1) * 30.0

    def _calculate_sahamas(self) -> Dict[str, SahamaData]:
        """
        Calculate positions of all 7 Sahamas.

        Formulas (A + B - C):
        - Punya: Asc + Moon - Sun (day) / Asc + Sun - Moon (night)
        - Vidya: Asc + Sun - Moon
        - Vivaha: Asc + Venus - Saturn
        - Santana: Asc + Jupiter - Moon
        - Rajya: Asc + Saturn - Sun
        - Mrityu: Asc + 8th cusp - Moon
        - Dhana: Asc + 2nd cusp - 2nd lord
        """
        sahamas = {}

        asc = self.asc_longitude
        sun = self.planets.get(Planet.SUN, 0.0)
        moon = self.planets.get(Planet.MOON, 0.0)
        venus = self.planets.get(Planet.VENUS, 0.0)
        saturn = self.planets.get(Planet.SATURN, 0.0)
        jupiter = self.planets.get(Planet.JUPITER, 0.0)

        # 1. Punya Sahama (Fortune) - most important
        if self.is_day_chart:
            punya_lon = self._normalize_longitude(asc + moon - sun)
        else:
            punya_lon = self._normalize_longitude(asc + sun - moon)

        sahamas['Punya'] = self._create_sahama_data('Punya', punya_lon)

        # 2. Vidya Sahama (Knowledge)
        vidya_lon = self._normalize_longitude(asc + sun - moon)
        sahamas['Vidya'] = self._create_sahama_data('Vidya', vidya_lon)

        # 3. Vivaha Sahama (Marriage)
        vivaha_lon = self._normalize_longitude(asc + venus - saturn)
        sahamas['Vivaha'] = self._create_sahama_data('Vivaha', vivaha_lon)

        # 4. Santana Sahama (Children)
        santana_lon = self._normalize_longitude(asc + jupiter - moon)
        sahamas['Santana'] = self._create_sahama_data('Santana', santana_lon)

        # 5. Rajya Sahama (Power)
        rajya_lon = self._normalize_longitude(asc + saturn - sun)
        sahamas['Rajya'] = self._create_sahama_data('Rajya', rajya_lon)

        # 6. Mrityu Sahama (Death) - 8th house cusp
        cusp_8 = self._get_house_cusp(8)
        mrityu_lon = self._normalize_longitude(asc + cusp_8 - moon)
        sahamas['Mrityu'] = self._create_sahama_data('Mrityu', mrityu_lon)

        # 7. Dhana Sahama (Wealth) - 2nd house and lord
        cusp_2 = self._get_house_cusp(2)
        sign_2 = self._longitude_to_sign(cusp_2)
        lord_2 = SIGN_LORDS.get(sign_2, Planet.VENUS)
        lord_2_lon = self.planets.get(lord_2, 0.0)
        dhana_lon = self._normalize_longitude(asc + cusp_2 - lord_2_lon)
        sahamas['Dhana'] = self._create_sahama_data('Dhana', dhana_lon)

        return sahamas

    def _create_sahama_data(self, name: str, longitude: float) -> SahamaData:
        """Create SahamaData object from name and longitude."""
        sahama_def = self.SAHAMA_DEFS[name]
        house = self._longitude_to_house(longitude)

        return SahamaData(
            name=name,
            name_ru=sahama_def['name_ru'],
            longitude=longitude,
            sign=self._longitude_to_sign(longitude),
            house=house,
            significance=sahama_def['significance'],
            influence=sahama_def['influence']
        )

    def _get_sahamas_in_house(self, house: int) -> List[SahamaData]:
        """Get all Sahamas in a given house."""
        return [s for s in self.sahamas.values() if s.house == house]

    def calculate(self) -> Dict[int, SahamaResult]:
        """
        Calculate Sahama influence for all 12 houses.

        Returns:
            Dictionary mapping house number to SahamaResult
        """
        results = {}

        for house in range(1, 13):
            sahamas_in_house = self._get_sahamas_in_house(house)

            raw_influence = 0.0
            sahama_names = []

            for sahama in sahamas_in_house:
                sahama_names.append(sahama.name)
                sahama_def = self.SAHAMA_DEFS[sahama.name]

                # Bonus if Sahama is in its related house
                related_houses = sahama_def.get('related_houses', set())
                if house in related_houses:
                    # Extra strong influence
                    raw_influence += sahama.influence * 1.5
                else:
                    raw_influence += sahama.influence

            # Normalize to ±3 range
            # Max realistic influence is ~2-3 sahamas * 0.8 = 2.4
            final_score = raw_influence * (self.MAX_POINTS / 2.0)
            final_score = max(-self.MAX_POINTS, min(self.MAX_POINTS, final_score))

            results[house] = SahamaResult(
                house=house,
                sahamas_present=sahama_names,
                raw_influence=raw_influence,
                final_score=final_score,
                details={
                    'count': len(sahama_names),
                    'is_day_chart': self.is_day_chart
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

    def get_sahama_positions(self) -> Dict[str, Dict]:
        """Get all Sahama positions for debugging/display."""
        return {
            name: {
                'name_ru': s.name_ru,
                'longitude': s.longitude,
                'sign': s.sign,
                'house': s.house,
                'significance': s.significance
            }
            for name, s in self.sahamas.items()
        }

    def get_report(self) -> str:
        """Generate human-readable report."""
        results = self.calculate()

        lines = [
            "=" * 60,
            "SAHAMA (ARABIC PARTS) ANALYSIS",
            "=" * 60,
            f"Chart Type: {'Day' if self.is_day_chart else 'Night'} Chart",
            "",
            "Sahama Positions:",
        ]

        for name, s in self.sahamas.items():
            lines.append(f"  {name} ({s.name_ru}): {s.longitude:.2f}° (House {s.house})")
            lines.append(f"    Significance: {s.significance}")

        lines.append("\nHouse Influences:")

        for house in range(1, 13):
            r = results[house]
            if r.sahamas_present:
                sahamas_str = ", ".join(r.sahamas_present)
                lines.append(f"  House {house}: {sahamas_str} -> {r.final_score:+.2f}")
            else:
                lines.append(f"  House {house}: (none)")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
