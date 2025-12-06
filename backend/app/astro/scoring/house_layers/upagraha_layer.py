"""
Phase 8.5 Layer: Upagraha (Shadow Planets) House Analysis (±3 points)

Upagrahas are mathematical points derived from the Sun's position that
influence the houses where they fall. They are secondary planets (shadows)
that add subtle influences.

5 Main Upagrahas:
1. Dhuma (Smoke) - Sun + 133°20' - Malefic, obscures/challenges
2. Vyatipata (Calamity) - 360° - Dhuma - Malefic, indicates obstacles
3. Parivesha (Halo) - Vyatipata + 180° - Mixed, protective but challenging
4. Indrachapa (Rainbow) - 360° - Parivesha - Benefic, divine grace
5. Upaketu (Comet's Tail) - Indrachapa + 16°40' - Malefic, sudden events

Each Upagraha in a house modifies its score based on nature.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import math


@dataclass
class UpagrahaData:
    """Data for a single Upagraha."""
    name: str
    longitude: float
    sign: int
    house: int
    nature: str  # 'benefic', 'malefic', 'mixed'
    influence: float  # -1 to +1


@dataclass
class UpagrahaResult:
    """Result from Upagraha analysis for a house."""
    house: int
    upagrahas_present: List[str]
    raw_influence: float
    final_score: float
    details: Dict = field(default_factory=dict)


class UpagrahaLayer:
    """
    Phase 8.5 Layer: Upagraha House Influence (±3 points)

    Calculates the position of 5 Upagrahas and their influence on houses.
    - Malefic Upagrahas reduce house strength
    - Benefic Upagrahas increase house strength
    - Effects are subtle but significant

    Score range: ±3 points
    """

    WEIGHT = 0.02  # 2% of total house score
    MAX_POINTS = 3.0

    # Upagraha definitions with nature and influence strength
    UPAGRAHA_DEFS = {
        'Dhuma': {'nature': 'malefic', 'influence': -0.6},
        'Vyatipata': {'nature': 'malefic', 'influence': -0.8},
        'Parivesha': {'nature': 'mixed', 'influence': -0.2},
        'Indrachapa': {'nature': 'benefic', 'influence': 0.7},
        'Upaketu': {'nature': 'malefic', 'influence': -0.5},
    }

    # Houses where malefics give good results (Upachaya houses)
    UPACHAYA_HOUSES = {3, 6, 10, 11}

    def __init__(self, chart_data: Dict):
        """
        Initialize with chart data.

        Args:
            chart_data: Full chart data including Sun position
        """
        self.chart_data = chart_data
        self.sun_longitude = self._get_sun_longitude()
        self.lagna_sign = self._get_lagna_sign()
        self.upagrahas = self._calculate_upagrahas()

    def _get_sun_longitude(self) -> float:
        """Get Sun's longitude from chart data."""
        # Try different formats
        if 'vargas' in self.chart_data:
            d1 = self.chart_data.get('vargas', {}).get('D1', {})
        elif 'D1' in self.chart_data:
            d1 = self.chart_data.get('D1', {})
        else:
            d1 = self.chart_data

        planets = d1.get('planets', [])
        for p in planets:
            name = p.get('name', '')
            if name in ('Sun', 'Солнце'):
                return p.get('longitude', 0.0)

        return 0.0

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

    def _calculate_upagrahas(self) -> Dict[str, UpagrahaData]:
        """
        Calculate positions of all 5 Upagrahas.

        Formulas:
        - Dhuma = Sun + 133°20' (4 signs + 13°20')
        - Vyatipata = 360° - Dhuma
        - Parivesha = Vyatipata + 180°
        - Indrachapa = 360° - Parivesha
        - Upaketu = Indrachapa + 16°40'
        """
        upagrahas = {}

        # 1. Dhuma (Smoke)
        dhuma_lon = self._normalize_longitude(self.sun_longitude + 133.333333)  # 133°20'
        upagrahas['Dhuma'] = UpagrahaData(
            name='Dhuma',
            longitude=dhuma_lon,
            sign=self._longitude_to_sign(dhuma_lon),
            house=self._longitude_to_house(dhuma_lon),
            nature=self.UPAGRAHA_DEFS['Dhuma']['nature'],
            influence=self.UPAGRAHA_DEFS['Dhuma']['influence']
        )

        # 2. Vyatipata (Calamity)
        vyatipata_lon = self._normalize_longitude(360 - dhuma_lon)
        upagrahas['Vyatipata'] = UpagrahaData(
            name='Vyatipata',
            longitude=vyatipata_lon,
            sign=self._longitude_to_sign(vyatipata_lon),
            house=self._longitude_to_house(vyatipata_lon),
            nature=self.UPAGRAHA_DEFS['Vyatipata']['nature'],
            influence=self.UPAGRAHA_DEFS['Vyatipata']['influence']
        )

        # 3. Parivesha (Halo)
        parivesha_lon = self._normalize_longitude(vyatipata_lon + 180)
        upagrahas['Parivesha'] = UpagrahaData(
            name='Parivesha',
            longitude=parivesha_lon,
            sign=self._longitude_to_sign(parivesha_lon),
            house=self._longitude_to_house(parivesha_lon),
            nature=self.UPAGRAHA_DEFS['Parivesha']['nature'],
            influence=self.UPAGRAHA_DEFS['Parivesha']['influence']
        )

        # 4. Indrachapa (Rainbow)
        indrachapa_lon = self._normalize_longitude(360 - parivesha_lon)
        upagrahas['Indrachapa'] = UpagrahaData(
            name='Indrachapa',
            longitude=indrachapa_lon,
            sign=self._longitude_to_sign(indrachapa_lon),
            house=self._longitude_to_house(indrachapa_lon),
            nature=self.UPAGRAHA_DEFS['Indrachapa']['nature'],
            influence=self.UPAGRAHA_DEFS['Indrachapa']['influence']
        )

        # 5. Upaketu (Comet's Tail)
        upaketu_lon = self._normalize_longitude(indrachapa_lon + 16.666667)  # 16°40'
        upagrahas['Upaketu'] = UpagrahaData(
            name='Upaketu',
            longitude=upaketu_lon,
            sign=self._longitude_to_sign(upaketu_lon),
            house=self._longitude_to_house(upaketu_lon),
            nature=self.UPAGRAHA_DEFS['Upaketu']['nature'],
            influence=self.UPAGRAHA_DEFS['Upaketu']['influence']
        )

        return upagrahas

    def _get_upagrahas_in_house(self, house: int) -> List[UpagrahaData]:
        """Get all Upagrahas in a given house."""
        return [u for u in self.upagrahas.values() if u.house == house]

    def calculate(self) -> Dict[int, UpagrahaResult]:
        """
        Calculate Upagraha influence for all 12 houses.

        Returns:
            Dictionary mapping house number to UpagrahaResult
        """
        results = {}

        for house in range(1, 13):
            upagrahas_in_house = self._get_upagrahas_in_house(house)

            raw_influence = 0.0
            upagraha_names = []

            for upagraha in upagrahas_in_house:
                upagraha_names.append(upagraha.name)

                # Reverse effect for malefics in upachaya houses
                if upagraha.nature == 'malefic' and house in self.UPACHAYA_HOUSES:
                    # Malefics give good results in 3, 6, 10, 11
                    raw_influence += abs(upagraha.influence) * 0.5
                else:
                    raw_influence += upagraha.influence

            # Normalize to ±3 range
            # Max possible influence is ~3 upagrahas * 0.8 = 2.4
            final_score = raw_influence * (self.MAX_POINTS / 2.0)
            final_score = max(-self.MAX_POINTS, min(self.MAX_POINTS, final_score))

            results[house] = UpagrahaResult(
                house=house,
                upagrahas_present=upagraha_names,
                raw_influence=raw_influence,
                final_score=final_score,
                details={
                    'count': len(upagraha_names),
                    'is_upachaya': house in self.UPACHAYA_HOUSES
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

    def get_upagraha_positions(self) -> Dict[str, Dict]:
        """Get all Upagraha positions for debugging/display."""
        return {
            name: {
                'longitude': u.longitude,
                'sign': u.sign,
                'house': u.house,
                'nature': u.nature
            }
            for name, u in self.upagrahas.items()
        }

    def get_report(self) -> str:
        """Generate human-readable report."""
        results = self.calculate()

        lines = [
            "=" * 60,
            "UPAGRAHA (SHADOW PLANETS) ANALYSIS",
            "=" * 60,
            f"Sun Longitude: {self.sun_longitude:.2f}°",
            "",
            "Upagraha Positions:",
        ]

        for name, u in self.upagrahas.items():
            lines.append(f"  {name}: {u.longitude:.2f}° (House {u.house}, {u.nature})")

        lines.append("\nHouse Influences:")

        for house in range(1, 13):
            r = results[house]
            if r.upagrahas_present:
                upagrahas_str = ", ".join(r.upagrahas_present)
                lines.append(f"  House {house}: {upagrahas_str} -> {r.final_score:+.2f}")
            else:
                lines.append(f"  House {house}: (none)")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
