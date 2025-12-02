"""
House (Bhava) Data Models

Represents house data from a chart with occupants, lord, and aspects.
Parses house data from digital_twin JSON format.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from .types import Planet, Zodiac, House, Degrees
from ..reference.dignities import get_sign_lord


@dataclass
class HouseData:
    """
    Complete house information for a single chart.

    Parsed from digital_twin["vargas"]["D1"]["houses"][index]
    """
    # Core identification
    house_number: House

    # Sign of house cusp
    sign: Zodiac
    lord: Planet

    # Occupants
    occupants: List[Planet]

    # Aspects received from planets
    aspects_received: List[Planet]

    # Raw data for reference
    _raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_digital_twin(cls, house_data: Dict[str, Any]) -> "HouseData":
        """
        Create HouseData from digital_twin house dict.

        Expected format:
        {
            "house_number": 1,
            "sign_id": 7,
            "sign_name": "Libra",
            "lord": "Venus",
            "occupants": ["Sun", "Mercury"],
            "aspects_received": ["Saturn"]
        }
        """
        # Parse house number
        house_num = house_data.get("house_number", 1)
        house_number = House(house_num)

        # Parse sign
        sign_id = house_data.get("sign_id", 1)
        sign = Zodiac(sign_id)

        # Parse lord
        lord_name = house_data.get("lord", "")
        if lord_name:
            lord = Planet.from_string(lord_name)
        else:
            lord = get_sign_lord(sign)

        # Parse occupants
        occupant_names = house_data.get("occupants", [])
        occupants = []
        for name in occupant_names:
            try:
                occupants.append(Planet.from_string(name))
            except ValueError:
                pass

        # Parse aspects
        aspect_names = house_data.get("aspects_received", [])
        aspects_received = []
        for name in aspect_names:
            try:
                aspects_received.append(Planet.from_string(name))
            except ValueError:
                pass

        return cls(
            house_number=house_number,
            sign=sign,
            lord=lord,
            occupants=occupants,
            aspects_received=aspects_received,
            _raw_data=house_data
        )

    @property
    def is_empty(self) -> bool:
        """Check if house has no planets"""
        return len(self.occupants) == 0

    @property
    def occupant_count(self) -> int:
        """Number of planets in house"""
        return len(self.occupants)

    @property
    def is_kendra(self) -> bool:
        """Check if this is an angular house (1, 4, 7, 10)"""
        return self.house_number.is_kendra

    @property
    def is_trikona(self) -> bool:
        """Check if this is a trinal house (1, 5, 9)"""
        return self.house_number.is_trikona

    @property
    def is_dusthana(self) -> bool:
        """Check if this is a difficult house (6, 8, 12)"""
        return self.house_number.is_dusthana

    @property
    def is_upachaya(self) -> bool:
        """Check if this is an upachaya house (3, 6, 10, 11)"""
        return self.house_number.value in [3, 6, 10, 11]

    def has_benefic(self) -> bool:
        """Check if house has natural benefic planets"""
        benefics = {Planet.JUPITER, Planet.VENUS, Planet.MERCURY, Planet.MOON}
        return any(p in benefics for p in self.occupants)

    def has_malefic(self) -> bool:
        """Check if house has natural malefic planets"""
        malefics = {Planet.SUN, Planet.MARS, Planet.SATURN, Planet.RAHU, Planet.KETU}
        return any(p in malefics for p in self.occupants)

    def receives_aspect_from(self, planet: Planet) -> bool:
        """Check if house receives aspect from specific planet"""
        return planet in self.aspects_received


@dataclass
class HouseAnalysis:
    """
    Analyzed house data for CalculatorOutput.

    This is what gets passed to LLM for interpretation.
    """
    house_number: int
    sign: str
    lord: str
    lord_house: int              # House where lord is placed
    occupants: List[str]
    aspects_from: List[str]
    strength_indicators: List[str]  # "Lord in kendra", "Benefic aspects", etc.

    @classmethod
    def from_house_data(
        cls,
        house: HouseData,
        lord_house: int,
        all_houses: Optional[Dict[int, "HouseData"]] = None
    ) -> "HouseAnalysis":
        """Create analysis from house data"""
        strength_indicators = []

        # Check lord placement
        if lord_house in [1, 4, 7, 10]:
            strength_indicators.append("Lord in kendra (strong)")
        elif lord_house in [5, 9]:
            strength_indicators.append("Lord in trikona (benefic)")
        elif lord_house in [6, 8, 12]:
            strength_indicators.append("Lord in dusthana (weak)")

        # Check occupants
        if house.has_benefic():
            strength_indicators.append("Has benefic planet(s)")
        if house.has_malefic():
            if house.is_upachaya:
                strength_indicators.append("Malefic in upachaya (good for growth)")
            else:
                strength_indicators.append("Has malefic planet(s)")

        # Check aspects
        benefic_aspects = [p for p in house.aspects_received
                         if p in {Planet.JUPITER, Planet.VENUS}]
        if benefic_aspects:
            strength_indicators.append(f"Benefic aspects from {', '.join(p.value for p in benefic_aspects)}")

        malefic_aspects = [p for p in house.aspects_received
                         if p in {Planet.SATURN, Planet.MARS, Planet.RAHU}]
        if malefic_aspects:
            strength_indicators.append(f"Malefic aspects from {', '.join(p.value for p in malefic_aspects)}")

        return cls(
            house_number=house.house_number.value,
            sign=house.sign.name.title(),
            lord=house.lord.value,
            lord_house=lord_house,
            occupants=[p.value for p in house.occupants],
            aspects_from=[p.value for p in house.aspects_received],
            strength_indicators=strength_indicators
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "house_number": self.house_number,
            "sign": self.sign,
            "lord": self.lord,
            "lord_house": self.lord_house,
            "occupants": self.occupants,
            "aspects_from": self.aspects_from,
            "strength_indicators": self.strength_indicators
        }


@dataclass
class ChartData:
    """
    Complete chart data containing all planets and houses for a varga.
    """
    varga_code: str
    ascendant_sign: Zodiac
    ascendant_degree: Degrees
    planets: Dict[Planet, "PlanetPosition"]  # Forward ref
    houses: Dict[House, HouseData]

    def get_planet(self, planet: Planet) -> Optional["PlanetPosition"]:
        """Get planet position by planet enum"""
        return self.planets.get(planet)

    def get_house(self, house: House) -> Optional[HouseData]:
        """Get house data by house number"""
        return self.houses.get(house)

    def get_house_lord(self, house: House) -> Optional[Planet]:
        """Get the lord of a house"""
        house_data = self.houses.get(house)
        if house_data:
            return house_data.lord
        return None

    def get_planets_in_house(self, house: House) -> List[Planet]:
        """Get all planets in a specific house"""
        house_data = self.houses.get(house)
        if house_data:
            return house_data.occupants
        return []

    def get_planets_in_sign(self, sign: Zodiac) -> List[Planet]:
        """Get all planets in a specific sign"""
        result = []
        for planet, pos in self.planets.items():
            if pos.sign == sign:
                result.append(planet)
        return result

    def count_planets_in_kendras(self) -> int:
        """Count planets in angular houses"""
        count = 0
        for house_num in [1, 4, 7, 10]:
            house = House(house_num)
            count += len(self.get_planets_in_house(house))
        return count

    def count_planets_in_dusthanas(self) -> int:
        """Count planets in difficult houses"""
        count = 0
        for house_num in [6, 8, 12]:
            house = House(house_num)
            count += len(self.get_planets_in_house(house))
        return count


# Type hint for forward reference
from .planets import PlanetPosition
ChartData.__annotations__["planets"] = Dict[Planet, PlanetPosition]
