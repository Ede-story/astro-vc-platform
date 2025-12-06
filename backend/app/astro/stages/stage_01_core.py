"""
Stage 1: Core Personality Analysis (D1 Chart)

This is the foundational stage that parses the digital_twin JSON
and extracts basic chart information from the D1 (Rashi) chart.

Output: BasicChartData with ascendant, sun, moon, and all planet positions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.types import (
    Planet, Zodiac, Dignity, House, Nakshatra,
    AscendantInfo, NakshatraInfo, Degrees
)
from ..models.planets import PlanetPosition, PlanetSummary
from ..models.houses import HouseData, HouseAnalysis
from ..reference.dignities import get_sign_lord, SIGN_LORDS


@dataclass
class BasicChartData:
    """
    Section 1 of CalculatorOutput: Basic Chart Data

    This contains the essential chart information extracted from D1.
    """
    # Ascendant info
    ascendant: AscendantInfo

    # Key signs for quick reference
    sun_sign: str       # Western sun sign (for context)
    moon_sign: str      # Vedic moon sign (rashi)
    moon_nakshatra: NakshatraInfo

    # All planet positions
    planets: List[PlanetSummary]

    # Quick reference: strongest and weakest planets
    strongest_planets: List[str]
    weakest_planets: List[str]

    # House lord positions (for yoga analysis)
    house_lords: Dict[int, Dict[str, Any]]  # {1: {"lord": "Venus", "in_house": 3}, ...}

    # House scores (base scores for Stage 2 adjustments)
    house_scores: Dict[str, float] = field(default_factory=lambda: {f"house_{i}": 5.0 for i in range(1, 13)})

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "ascendant": {
                "sign": self.ascendant.sign.name.title(),
                "degree": round(self.ascendant.degree, 2),
                "nakshatra": self.ascendant.nakshatra.name.value if self.ascendant.nakshatra else None,
                "nakshatra_pada": self.ascendant.nakshatra.pada.value if self.ascendant.nakshatra else None,
                "lord": self.ascendant.lord.value
            },
            "sun_sign": self.sun_sign,
            "moon_sign": self.moon_sign,
            "moon_nakshatra": {
                "name": self.moon_nakshatra.name.value,
                "pada": self.moon_nakshatra.pada.value,
                "lord": self.moon_nakshatra.lord.value
            } if self.moon_nakshatra else None,
            "planets": [p.to_dict() for p in self.planets],
            "strongest_planets": self.strongest_planets,
            "weakest_planets": self.weakest_planets,
            "house_lords": self.house_lords,
            "house_scores": self.house_scores
        }


class Stage01CorePersonality:
    """
    Stage 1: Parse D1 chart and extract core personality indicators.

    Input: digital_twin JSON
    Output: BasicChartData
    """

    def __init__(self, digital_twin: Dict[str, Any]):
        """
        Initialize with digital_twin JSON.

        Args:
            digital_twin: The full digital_twin dict from API response
        """
        self.digital_twin = digital_twin
        self.vargas = digital_twin.get("vargas", {})
        self.d1 = self.vargas.get("D1", {})

        # Parsed data
        self.planets: Dict[Planet, PlanetPosition] = {}
        self.houses: Dict[House, HouseData] = {}
        self.ascendant_data: Optional[Dict[str, Any]] = None

    def parse(self) -> BasicChartData:
        """
        Parse the D1 chart and return BasicChartData.

        Returns:
            BasicChartData object ready for CalculatorOutput
        """
        # Parse ascendant
        self._parse_ascendant()

        # Parse all planets
        self._parse_planets()

        # Parse all houses
        self._parse_houses()

        # Build BasicChartData
        return self._build_basic_chart_data()

    def _parse_ascendant(self) -> None:
        """Parse ascendant (lagna) data"""
        asc_data = self.d1.get("ascendant", {})
        self.ascendant_data = asc_data

    def _parse_planets(self) -> None:
        """Parse all planet positions from D1"""
        planets_list = self.d1.get("planets", [])

        for planet_data in planets_list:
            try:
                position = PlanetPosition.from_digital_twin(planet_data, "D1")
                self.planets[position.planet] = position
            except (ValueError, KeyError) as e:
                # Log error but continue parsing other planets
                print(f"Warning: Could not parse planet: {e}")

    def _parse_houses(self) -> None:
        """Parse all house data from D1"""
        houses_list = self.d1.get("houses", [])

        for house_data in houses_list:
            try:
                house = HouseData.from_digital_twin(house_data)
                self.houses[house.house_number] = house
            except (ValueError, KeyError) as e:
                print(f"Warning: Could not parse house: {e}")

    def _build_basic_chart_data(self) -> BasicChartData:
        """Build the BasicChartData output"""
        # Build ascendant info
        asc_sign_id = self.ascendant_data.get("sign_id", 1)
        asc_sign = Zodiac(asc_sign_id)
        asc_degree = float(self.ascendant_data.get("degrees", 0))

        # Get ascendant nakshatra if available
        asc_nakshatra_name = self.ascendant_data.get("nakshatra", "")
        asc_nakshatra_pada = self.ascendant_data.get("nakshatra_pada", 1)
        asc_nakshatra_lord = self.ascendant_data.get("nakshatra_lord", "")

        asc_nakshatra = None
        if asc_nakshatra_name:
            try:
                from ..models.types import NakshatraPada
                asc_nakshatra = NakshatraInfo(
                    name=Nakshatra.from_string(asc_nakshatra_name),
                    pada=NakshatraPada(asc_nakshatra_pada),
                    lord=Planet.from_string(asc_nakshatra_lord) if asc_nakshatra_lord else Planet.KETU,
                    degrees_in_nakshatra=asc_degree % (360/27)
                )
            except ValueError:
                pass

        ascendant = AscendantInfo(
            sign=asc_sign,
            degree=asc_degree,
            nakshatra=asc_nakshatra,
            lord=get_sign_lord(asc_sign)
        )

        # Get Sun and Moon info
        sun = self.planets.get(Planet.SUN)
        moon = self.planets.get(Planet.MOON)

        sun_sign = sun.sign.name.title() if sun else "Unknown"
        moon_sign = moon.sign.name.title() if moon else "Unknown"

        moon_nakshatra = None
        if moon:
            moon_nakshatra = moon.get_nakshatra_info()

        # Build planet summaries
        planet_summaries = []
        for planet in Planet:
            if planet in self.planets:
                summary = PlanetSummary.from_position(self.planets[planet])
                planet_summaries.append(summary)

        # Determine strongest and weakest planets by dignity
        dignity_scores = []
        for planet, pos in self.planets.items():
            if not planet.is_shadow:  # Exclude Rahu/Ketu from ranking
                score = pos.dignity.strength_score
                dignity_scores.append((planet.value, score, pos.dignity))

        # Sort by score descending
        dignity_scores.sort(key=lambda x: x[1], reverse=True)

        strongest = [p[0] for p in dignity_scores[:3]]  # Top 3
        weakest = [p[0] for p in dignity_scores[-3:]]   # Bottom 3

        # Build house lord positions
        house_lords = {}
        for house_num in range(1, 13):
            house = House(house_num)
            house_data = self.houses.get(house)
            if house_data:
                lord = house_data.lord
                # Find where lord is placed
                lord_position = self.planets.get(lord)
                lord_house = lord_position.house_occupied.value if lord_position else 0

                house_lords[house_num] = {
                    "lord": lord.value,
                    "in_house": lord_house,
                    "sign": house_data.sign.name.title()
                }

        return BasicChartData(
            ascendant=ascendant,
            sun_sign=sun_sign,
            moon_sign=moon_sign,
            moon_nakshatra=moon_nakshatra,
            planets=planet_summaries,
            strongest_planets=strongest,
            weakest_planets=weakest,
            house_lords=house_lords
        )

    def get_planet(self, planet: Planet) -> Optional[PlanetPosition]:
        """Get parsed planet position"""
        return self.planets.get(planet)

    def get_house(self, house: House) -> Optional[HouseData]:
        """Get parsed house data"""
        return self.houses.get(house)

    def get_planets_in_house(self, house: House) -> List[Planet]:
        """Get all planets in a specific house"""
        house_data = self.houses.get(house)
        if house_data:
            return house_data.occupants
        return []

    def get_house_lord(self, house: House) -> Optional[Planet]:
        """Get the lord of a house"""
        house_data = self.houses.get(house)
        if house_data:
            return house_data.lord
        return None

    def is_kendra_lord(self, planet: Planet) -> bool:
        """Check if planet lords a kendra (1, 4, 7, 10)"""
        for house_num in [1, 4, 7, 10]:
            house = House(house_num)
            house_data = self.houses.get(house)
            if house_data and house_data.lord == planet:
                return True
        return False

    def is_trikona_lord(self, planet: Planet) -> bool:
        """Check if planet lords a trikona (1, 5, 9)"""
        for house_num in [1, 5, 9]:
            house = House(house_num)
            house_data = self.houses.get(house)
            if house_data and house_data.lord == planet:
                return True
        return False

    def is_dusthana_lord(self, planet: Planet) -> bool:
        """Check if planet lords a dusthana (6, 8, 12)"""
        for house_num in [6, 8, 12]:
            house = House(house_num)
            house_data = self.houses.get(house)
            if house_data and house_data.lord == planet:
                return True
        return False
