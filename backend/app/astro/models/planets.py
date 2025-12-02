"""
Planet Position Model

Represents a planet's position in a chart with all relevant attributes.
Parses planet data from digital_twin JSON format.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from .types import (
    Planet, Zodiac, Dignity, House, Nakshatra, NakshatraPada,
    Degrees, NakshatraInfo
)
from ..reference.dignities import (
    get_dignity, get_dignity_from_string, get_sign_lord,
    is_exalted, is_debilitated, EXALTATION_DEGREES, DEBILITATION_DEGREES
)


@dataclass
class PlanetPosition:
    """
    Complete planet position information for a single chart.

    Parsed from digital_twin["vargas"]["D1"]["planets"][index]
    """
    # Core identification
    planet: Planet

    # Sign placement
    sign: Zodiac
    sign_lord: Planet

    # Degrees
    absolute_degree: Degrees      # 0-360
    relative_degree: Degrees      # 0-30 within sign

    # House placement
    house_occupied: House
    houses_owned: List[House]     # Houses this planet lords over

    # Nakshatra data
    nakshatra: Nakshatra
    nakshatra_lord: Planet
    nakshatra_pada: NakshatraPada

    # Dignity
    dignity: Dignity

    # Motion
    is_retrograde: bool

    # Relationships (aspect and conjunction)
    aspects_giving_to: List[House]      # Houses this planet aspects
    aspects_receiving_from: List[Planet]  # Planets aspecting this planet
    conjunctions: List[Planet]          # Planets in same sign

    # Raw data for reference
    _raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_digital_twin(
        cls,
        planet_data: Dict[str, Any],
        varga_code: str = "D1"
    ) -> "PlanetPosition":
        """
        Create PlanetPosition from digital_twin planet dict.

        Expected format:
        {
            "name": "Sun",
            "sign_id": 7,
            "sign_name": "Libra",
            "absolute_degree": 188.12,
            "relative_degree": 8.12,
            "house_occupied": 1,
            "houses_owned": [11],
            "nakshatra": "Swati",
            "nakshatra_lord": "Rahu",
            "nakshatra_pada": 2,
            "sign_lord": "Venus",
            "dignity_state": "Debilitated",
            "aspects_giving_to": [7],
            "aspects_receiving_from": ["Saturn"],
            "conjunctions": ["Mercury"],
            "is_retrograde": false
        }
        """
        # Parse planet name
        planet_name = planet_data.get("name", "")
        planet = Planet.from_string(planet_name)

        # Parse sign
        sign_id = planet_data.get("sign_id", 1)
        sign = Zodiac(sign_id)

        # Parse sign lord
        sign_lord_name = planet_data.get("sign_lord", "")
        if sign_lord_name:
            sign_lord = Planet.from_string(sign_lord_name)
        else:
            sign_lord = get_sign_lord(sign)

        # Parse degrees
        absolute_degree = float(planet_data.get("absolute_degree", 0))
        relative_degree = float(planet_data.get("relative_degree", 0))

        # Parse house
        house_num = planet_data.get("house_occupied", 1)
        house_occupied = House(house_num)

        # Parse houses owned
        houses_owned_nums = planet_data.get("houses_owned", [])
        houses_owned = [House(h) for h in houses_owned_nums]

        # Parse nakshatra
        nakshatra_name = planet_data.get("nakshatra", "Ashwini")
        try:
            nakshatra = Nakshatra.from_string(nakshatra_name)
        except ValueError:
            nakshatra = Nakshatra.ASHWINI  # Fallback

        # Parse nakshatra lord
        nakshatra_lord_name = planet_data.get("nakshatra_lord", "Ketu")
        try:
            nakshatra_lord = Planet.from_string(nakshatra_lord_name)
        except ValueError:
            nakshatra_lord = Planet.KETU

        # Parse nakshatra pada
        pada_num = planet_data.get("nakshatra_pada", 1)
        nakshatra_pada = NakshatraPada(pada_num)

        # Parse dignity
        dignity_str = planet_data.get("dignity_state", "Neutral")
        dignity = get_dignity_from_string(dignity_str)

        # Parse retrograde
        is_retrograde = planet_data.get("is_retrograde", False)

        # Parse aspects giving
        aspects_giving_nums = planet_data.get("aspects_giving_to", [])
        aspects_giving_to = [House(h) for h in aspects_giving_nums]

        # Parse aspects receiving
        aspects_receiving_names = planet_data.get("aspects_receiving_from", [])
        aspects_receiving_from = []
        for name in aspects_receiving_names:
            try:
                aspects_receiving_from.append(Planet.from_string(name))
            except ValueError:
                pass

        # Parse conjunctions
        conjunction_names = planet_data.get("conjunctions", [])
        conjunctions = []
        for name in conjunction_names:
            try:
                conjunctions.append(Planet.from_string(name))
            except ValueError:
                pass

        return cls(
            planet=planet,
            sign=sign,
            sign_lord=sign_lord,
            absolute_degree=absolute_degree,
            relative_degree=relative_degree,
            house_occupied=house_occupied,
            houses_owned=houses_owned,
            nakshatra=nakshatra,
            nakshatra_lord=nakshatra_lord,
            nakshatra_pada=nakshatra_pada,
            dignity=dignity,
            is_retrograde=is_retrograde,
            aspects_giving_to=aspects_giving_to,
            aspects_receiving_from=aspects_receiving_from,
            conjunctions=conjunctions,
            _raw_data=planet_data
        )

    @property
    def is_exalted(self) -> bool:
        """Check if planet is exalted"""
        return self.dignity == Dignity.EXALTED

    @property
    def is_debilitated(self) -> bool:
        """Check if planet is debilitated"""
        return self.dignity == Dignity.DEBILITATED

    @property
    def is_in_own_sign(self) -> bool:
        """Check if planet is in own sign"""
        return self.dignity == Dignity.OWN_SIGN

    @property
    def is_in_kendra(self) -> bool:
        """Check if planet is in angular house (1, 4, 7, 10)"""
        return self.house_occupied.is_kendra

    @property
    def is_in_trikona(self) -> bool:
        """Check if planet is in trinal house (1, 5, 9)"""
        return self.house_occupied.is_trikona

    @property
    def is_in_dusthana(self) -> bool:
        """Check if planet is in difficult house (6, 8, 12)"""
        return self.house_occupied.is_dusthana

    @property
    def exaltation_strength(self) -> float:
        """
        Calculate strength based on proximity to exaltation degree.
        Returns 0-100 where 100 = exact exaltation.
        """
        if not is_exalted(self.planet, self.sign):
            return 0.0

        exalt_deg = EXALTATION_DEGREES.get(self.planet, 15.0)
        diff = abs(self.relative_degree - exalt_deg)
        # Max distance in sign is 15 degrees from exact point
        strength = max(0, 100 - (diff * (100 / 15)))
        return round(strength, 2)

    @property
    def debilitation_depth(self) -> float:
        """
        Calculate depth of debilitation based on proximity to exact debilitation point.
        Returns 0-100 where 100 = exact debilitation (worst).
        """
        if not is_debilitated(self.planet, self.sign):
            return 0.0

        debil_deg = DEBILITATION_DEGREES.get(self.planet, 15.0)
        diff = abs(self.relative_degree - debil_deg)
        depth = max(0, 100 - (diff * (100 / 15)))
        return round(depth, 2)

    def get_nakshatra_info(self) -> NakshatraInfo:
        """Get detailed nakshatra information"""
        # Calculate degrees within nakshatra (each nakshatra = 13.333... degrees)
        nakshatra_size = 360 / 27
        nakshatra_index = int(self.absolute_degree / nakshatra_size)
        degrees_in_nakshatra = self.absolute_degree % nakshatra_size

        return NakshatraInfo(
            name=self.nakshatra,
            pada=self.nakshatra_pada,
            lord=self.nakshatra_lord,
            degrees_in_nakshatra=degrees_in_nakshatra
        )


@dataclass
class PlanetSummary:
    """
    Condensed planet summary for CalculatorOutput.

    This is what gets passed to LLM for interpretation.
    """
    name: str
    sign: str
    house: int
    dignity: str
    nakshatra: str
    nakshatra_lord: str
    is_retrograde: bool
    key_aspects: List[str]       # "Saturn aspects Sun", etc.
    key_conjunctions: List[str]  # "Conjunct Mercury", etc.
    degree: float = 15.0         # Relative degree in sign (for atmakaraka)

    @property
    def planet(self) -> Planet:
        """Get Planet enum from name string."""
        return Planet.from_string(self.name)

    @property
    def sign_zodiac(self) -> Zodiac:
        """Get Zodiac enum from sign string."""
        return Zodiac.from_string(self.sign)

    @property
    def dignity_enum(self) -> Dignity:
        """Get Dignity enum from dignity string."""
        from ..reference.dignities import get_dignity_from_string
        return get_dignity_from_string(self.dignity)

    @classmethod
    def from_position(cls, pos: PlanetPosition) -> "PlanetSummary":
        """Create summary from full position data"""
        # Format aspects
        key_aspects = []
        for aspecting_planet in pos.aspects_receiving_from:
            key_aspects.append(f"{aspecting_planet.value} aspects {pos.planet.value}")

        # Format conjunctions
        key_conjunctions = []
        for conj_planet in pos.conjunctions:
            key_conjunctions.append(f"Conjunct {conj_planet.value}")

        return cls(
            name=pos.planet.value,
            sign=pos.sign.name.title(),
            house=pos.house_occupied.value,
            dignity=pos.dignity.value,
            nakshatra=pos.nakshatra.value,
            nakshatra_lord=pos.nakshatra_lord.value,
            is_retrograde=pos.is_retrograde,
            key_aspects=key_aspects,
            key_conjunctions=key_conjunctions,
            degree=pos.relative_degree
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "sign": self.sign,
            "house": self.house,
            "dignity": self.dignity,
            "nakshatra": self.nakshatra,
            "nakshatra_lord": self.nakshatra_lord,
            "is_retrograde": self.is_retrograde,
            "key_aspects": self.key_aspects,
            "key_conjunctions": self.key_conjunctions
        }
