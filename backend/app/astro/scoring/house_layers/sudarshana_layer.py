"""
Phase 8.5 Layer: Sudarshana Chakra House Analysis (±5 points)

Sudarshana Chakra is the "Beautiful Wheel" technique that analyzes houses
from three perspectives simultaneously:
1. Lagna (Ascendant) - Physical/Material perspective (40%)
2. Chandra (Moon) - Mental/Emotional perspective (35%)
3. Surya (Sun) - Soul/Dharmic perspective (25%)

When all three perspectives show strength for a house, results are amplified.
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

# Natural benefics and malefics
NATURAL_BENEFICS = {Planet.JUPITER, Planet.VENUS, Planet.MERCURY, Planet.MOON}
NATURAL_MALEFICS = {Planet.SATURN, Planet.MARS, Planet.RAHU, Planet.KETU, Planet.SUN}


@dataclass
class SudarshanaResult:
    """Result from Sudarshana Chakra analysis."""
    house: int
    lagna_score: float  # Score from Lagna perspective
    chandra_score: float  # Score from Moon perspective
    surya_score: float  # Score from Sun perspective
    weighted_score: float  # Combined weighted score
    convergence_bonus: float  # Bonus when all agree
    final_score: float  # Final ±5 range score
    details: Dict = field(default_factory=dict)


class SudarshanaLayer:
    """
    Phase 8.5 Layer: Sudarshana Chakra House Analysis

    Analyzes each house from three chakra perspectives:
    - Lagna Chakra (from Ascendant)
    - Chandra Chakra (from Moon sign)
    - Surya Chakra (from Sun sign)

    Score range: ±5 points
    """

    WEIGHT = 0.04  # 4% of total house score
    MAX_POINTS = 5.0

    # Perspective weights
    LAGNA_WEIGHT = 0.40   # Physical/material reality
    CHANDRA_WEIGHT = 0.35  # Mental/emotional experience
    SURYA_WEIGHT = 0.25   # Soul/dharmic purpose

    # Convergence bonus when all perspectives agree
    CONVERGENCE_THRESHOLD = 0.6  # All scores above 60% = strong agreement
    MAX_CONVERGENCE_BONUS = 1.5  # Additional points

    def __init__(self, chart_data: Dict):
        """
        Initialize with chart data.

        Args:
            chart_data: Full chart data including D1 planets, houses
        """
        self.chart_data = chart_data
        self.planets = self._extract_planets()
        self.lagna_sign = self._get_lagna_sign()
        self.moon_sign = self._get_planet_sign(Planet.MOON)
        self.sun_sign = self._get_planet_sign(Planet.SUN)

    def _extract_planets(self) -> Dict[int, Dict]:
        """Extract planet data from chart."""
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
                sign_num = self._sign_to_number(p.get('sign', ''))
                planets[planet_id] = {
                    'sign': sign_num,
                    'house': p.get('house', 0),
                    'longitude': p.get('longitude', 0.0),
                    'retrograde': p.get('retrograde', False)
                }

        return planets

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

    def _get_lagna_sign(self) -> int:
        """Get ascendant sign number."""
        if 'vargas' in self.chart_data:
            d1 = self.chart_data.get('vargas', {}).get('D1', {})
        elif 'D1' in self.chart_data:
            d1 = self.chart_data.get('D1', {})
        else:
            d1 = self.chart_data

        asc = d1.get('ascendant', {})
        return self._sign_to_number(asc.get('sign', 'Aries'))

    def _get_planet_sign(self, planet: Planet) -> int:
        """Get sign number for a planet."""
        p_data = self.planets.get(planet, {})
        return p_data.get('sign', 1)

    def _get_house_from_reference(self, house: int, reference_sign: int) -> int:
        """
        Calculate house number from a reference sign.

        If reference_sign is the "1st house" from that perspective,
        what house does the given D1 house represent?

        Args:
            house: Original house number (1-12)
            reference_sign: Sign that is the 1st house from this perspective

        Returns:
            House number from reference perspective (1-12)
        """
        # Get sign of the house
        house_sign = ((self.lagna_sign - 1 + house - 1) % 12) + 1

        # Calculate what house this sign is from reference perspective
        perspective_house = ((house_sign - reference_sign) % 12) + 1
        return perspective_house

    def _count_planets_in_house(self, perspective_house: int, reference_sign: int) -> List[Planet]:
        """
        Count planets in a house from a specific perspective.

        Args:
            perspective_house: House number (1-12) from perspective
            reference_sign: Sign that is 1st house from perspective

        Returns:
            List of planets in that house
        """
        planets_in_house = []

        # Calculate which sign corresponds to this house from perspective
        target_sign = ((reference_sign - 1 + perspective_house - 1) % 12) + 1

        for planet, data in self.planets.items():
            if data.get('sign') == target_sign:
                planets_in_house.append(planet)

        return planets_in_house

    def _evaluate_perspective(self, d1_house: int, reference_sign: int) -> Tuple[float, Dict]:
        """
        Evaluate a house from one perspective (Lagna, Moon, or Sun).

        Args:
            d1_house: Original D1 house number (1-12)
            reference_sign: Sign that is 1st house from this perspective

        Returns:
            Tuple of (score 0-1, details dict)
        """
        score = 0.5  # Neutral base
        details = {'factors': []}

        # What house is this from the perspective?
        perspective_house = self._get_house_from_reference(d1_house, reference_sign)

        # Check lord placement
        house_sign = ((self.lagna_sign - 1 + d1_house - 1) % 12) + 1
        lord = SIGN_LORDS.get(house_sign)

        if lord is not None and lord in self.planets:
            lord_sign = self.planets[lord].get('sign', 0)
            lord_perspective_house = self._get_house_from_reference(
                ((lord_sign - self.lagna_sign) % 12) + 1,
                reference_sign
            )

            # Good houses from perspective: 1, 2, 4, 5, 7, 9, 10, 11
            good_houses = {1, 2, 4, 5, 7, 9, 10, 11}
            # Bad houses: 6, 8, 12
            bad_houses = {6, 8, 12}

            if lord_perspective_house in good_houses:
                score += 0.15
                details['factors'].append(f'Lord in {lord_perspective_house}H from perspective (+)')
            elif lord_perspective_house in bad_houses:
                score -= 0.10
                details['factors'].append(f'Lord in {lord_perspective_house}H from perspective (-)')

        # Check planets in house from perspective
        planets_in_perspective = self._count_planets_in_house(perspective_house, reference_sign)

        benefic_count = sum(1 for p in planets_in_perspective if p in NATURAL_BENEFICS)
        malefic_count = sum(1 for p in planets_in_perspective if p in NATURAL_MALEFICS)

        if benefic_count > 0:
            score += 0.1 * benefic_count
            details['factors'].append(f'{benefic_count} benefic(s) aspect (+)')

        if malefic_count > 0 and perspective_house not in {3, 6, 10, 11}:
            # Malefics are good in upachaya houses
            score -= 0.05 * malefic_count
            details['factors'].append(f'{malefic_count} malefic(s) (-)')
        elif malefic_count > 0:
            score += 0.05 * malefic_count
            details['factors'].append(f'{malefic_count} malefic(s) in upachaya (+)')

        # House nature bonus from perspective
        # Kendras (1, 4, 7, 10), Trikonas (1, 5, 9), Upachayas (3, 6, 10, 11)
        if perspective_house in {1, 4, 7, 10}:  # Kendra
            score += 0.08
            details['factors'].append(f'Kendra position ({perspective_house}H) (+)')
        elif perspective_house in {5, 9}:  # Trikona
            score += 0.10
            details['factors'].append(f'Trikona position ({perspective_house}H) (+)')
        elif perspective_house in {6, 8, 12}:  # Dusthana
            score -= 0.08
            details['factors'].append(f'Dusthana position ({perspective_house}H) (-)')

        # Clamp score
        score = max(0.0, min(1.0, score))
        details['perspective_house'] = perspective_house
        details['score'] = score

        return score, details

    def calculate(self) -> Dict[int, SudarshanaResult]:
        """
        Calculate Sudarshana scores for all 12 houses.

        Returns:
            Dictionary mapping house number to SudarshanaResult
        """
        results = {}

        for house in range(1, 13):
            # Evaluate from all three perspectives
            lagna_score, lagna_details = self._evaluate_perspective(house, self.lagna_sign)
            chandra_score, chandra_details = self._evaluate_perspective(house, self.moon_sign)
            surya_score, surya_details = self._evaluate_perspective(house, self.sun_sign)

            # Calculate weighted score
            weighted = (
                lagna_score * self.LAGNA_WEIGHT +
                chandra_score * self.CHANDRA_WEIGHT +
                surya_score * self.SURYA_WEIGHT
            )

            # Check for convergence (all three perspectives agree)
            convergence_bonus = 0.0
            all_strong = all(s >= self.CONVERGENCE_THRESHOLD for s in [lagna_score, chandra_score, surya_score])
            all_weak = all(s <= (1 - self.CONVERGENCE_THRESHOLD) for s in [lagna_score, chandra_score, surya_score])

            if all_strong:
                convergence_bonus = self.MAX_CONVERGENCE_BONUS
            elif all_weak:
                convergence_bonus = -self.MAX_CONVERGENCE_BONUS * 0.5

            # Normalize to ±5 range
            # weighted is 0-1, so (weighted - 0.5) * 2 gives -1 to +1
            normalized = (weighted - 0.5) * 2 * self.MAX_POINTS
            final_score = normalized + convergence_bonus

            # Clamp to ±5
            final_score = max(-self.MAX_POINTS, min(self.MAX_POINTS, final_score))

            results[house] = SudarshanaResult(
                house=house,
                lagna_score=lagna_score,
                chandra_score=chandra_score,
                surya_score=surya_score,
                weighted_score=weighted,
                convergence_bonus=convergence_bonus,
                final_score=final_score,
                details={
                    'lagna': lagna_details,
                    'chandra': chandra_details,
                    'surya': surya_details,
                    'convergence': 'strong' if all_strong else ('weak' if all_weak else 'mixed')
                }
            )

        return results

    def calculate_for_houses(self) -> Dict[int, float]:
        """
        Calculate simplified scores for integration with HouseScoreCalculator.

        Returns:
            Dictionary mapping house number (1-12) to score (±5)
        """
        results = self.calculate()
        return {house: result.final_score for house, result in results.items()}

    def get_report(self) -> str:
        """Generate human-readable report."""
        results = self.calculate()

        lines = [
            "=" * 60,
            "SUDARSHANA CHAKRA ANALYSIS",
            "=" * 60,
            f"Lagna Sign: {self.lagna_sign} (weight: {self.LAGNA_WEIGHT:.0%})",
            f"Moon Sign: {self.moon_sign} (weight: {self.CHANDRA_WEIGHT:.0%})",
            f"Sun Sign: {self.sun_sign} (weight: {self.SURYA_WEIGHT:.0%})",
            "",
        ]

        for house in range(1, 13):
            r = results[house]
            lines.append(f"\nHouse {house}:")
            lines.append(f"  Lagna perspective: {r.lagna_score:.2f}")
            lines.append(f"  Chandra perspective: {r.chandra_score:.2f}")
            lines.append(f"  Surya perspective: {r.surya_score:.2f}")
            lines.append(f"  Convergence: {r.details['convergence']} ({r.convergence_bonus:+.2f})")
            lines.append(f"  Final Score: {r.final_score:+.2f}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
