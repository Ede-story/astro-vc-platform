"""
Stage 10: Timing (Vimshottari Dasha + Ashtakavarga)

Vimshottari Dasha:
- 120-year cycle based on Moon's nakshatra
- Shows: which planet is ruling current period
- Critical for predicting success/failure timing

Ashtakavarga:
- 8-fold strength analysis
- Shows: which houses are activated when
- Predicts transit effects
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from enum import Enum

from ..models.types import Planet, Zodiac


def _get_planet_attr(planet: Any, key: str, default: Any = None) -> Any:
    """Get attribute from planet dict or dataclass object."""
    if hasattr(planet, 'get'):
        return planet.get(key, default)
    return getattr(planet, key, default)


class DashaPeriodQuality(str, Enum):
    """Quality of a dasha period."""
    GOLDEN = "Golden"                 # 9-10 score
    VERY_FAVORABLE = "VeryFavorable"  # 7-8
    FAVORABLE = "Favorable"           # 5-6
    MIXED = "Mixed"                   # 4-5
    CHALLENGING = "Challenging"       # 2-4
    DIFFICULT = "Difficult"           # 0-2


class TimingRecommendation(str, Enum):
    """Investment timing recommendation."""
    INVEST_NOW = "InvestNow"           # Golden period
    FAVORABLE_TIMING = "FavorableTiming"
    WAIT_FOR_BETTER = "WaitForBetter"
    PROCEED_CAUTION = "ProceedCaution"
    DELAY_INVESTMENT = "DelayInvestment"


@dataclass
class DashaPeriod:
    """A dasha or antardasha period."""
    planet: str
    start_date: str  # ISO format
    end_date: str    # ISO format
    duration_years: float
    is_current: bool
    quality_score: float  # 1-10
    quality: DashaPeriodQuality
    key_themes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "planet": self.planet,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "duration_years": round(self.duration_years, 2),
            "is_current": self.is_current,
            "quality_score": round(self.quality_score, 1),
            "quality": self.quality.value,
            "key_themes": self.key_themes
        }


@dataclass
class DashaRoadmap:
    """Full dasha roadmap."""
    current_mahadasha: DashaPeriod
    current_antardasha: Optional[DashaPeriod]
    upcoming_periods: List[DashaPeriod]
    golden_periods: List[Dict[str, Any]]
    challenging_periods: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_mahadasha": self.current_mahadasha.to_dict(),
            "current_antardasha": self.current_antardasha.to_dict() if self.current_antardasha else None,
            "upcoming_periods": [p.to_dict() for p in self.upcoming_periods],
            "golden_periods": self.golden_periods,
            "challenging_periods": self.challenging_periods
        }


@dataclass
class AshtakavargaScore:
    """Ashtakavarga bindu scores by house."""
    house_bindus: Dict[int, int]
    total_bindus: int
    strongest_houses: List[int]
    weakest_houses: List[int]
    above_average_houses: List[int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "house_bindus": self.house_bindus,
            "total_bindus": self.total_bindus,
            "strongest_houses": self.strongest_houses,
            "weakest_houses": self.weakest_houses,
            "above_average_houses": self.above_average_houses
        }


@dataclass
class Stage10Result:
    """Complete Stage 10 analysis result."""
    dasha_roadmap: DashaRoadmap
    current_dasha_quality: DashaPeriodQuality
    ashtakavarga: AshtakavargaScore

    is_golden_period: bool
    years_until_golden: float
    timing_recommendation: TimingRecommendation

    best_years: List[int]
    caution_years: List[int]
    career_activation_years: List[int]
    wealth_activation_years: List[int]

    timing_summary: str
    indices: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dasha_roadmap": self.dasha_roadmap.to_dict(),
            "current_dasha_quality": self.current_dasha_quality.value,
            "ashtakavarga": self.ashtakavarga.to_dict(),
            "is_golden_period": self.is_golden_period,
            "years_until_golden": round(self.years_until_golden, 1),
            "timing_recommendation": self.timing_recommendation.value,
            "best_years": self.best_years,
            "caution_years": self.caution_years,
            "career_activation_years": self.career_activation_years,
            "wealth_activation_years": self.wealth_activation_years,
            "timing_summary": self.timing_summary,
            "indices": self.indices
        }


# Vimshottari Dasha periods (years)
DASHA_PERIODS: Dict[Planet, int] = {
    Planet.KETU: 7,
    Planet.VENUS: 20,
    Planet.SUN: 6,
    Planet.MOON: 10,
    Planet.MARS: 7,
    Planet.RAHU: 18,
    Planet.JUPITER: 16,
    Planet.SATURN: 19,
    Planet.MERCURY: 17,
}

# Dasha sequence
DASHA_SEQUENCE: List[Planet] = [
    Planet.KETU, Planet.VENUS, Planet.SUN, Planet.MOON, Planet.MARS,
    Planet.RAHU, Planet.JUPITER, Planet.SATURN, Planet.MERCURY
]

# Nakshatra lords (27 nakshatras)
NAKSHATRA_LORDS: Dict[int, Planet] = {
    1: Planet.KETU,     # Ashwini
    2: Planet.VENUS,    # Bharani
    3: Planet.SUN,      # Krittika
    4: Planet.MOON,     # Rohini
    5: Planet.MARS,     # Mrigashira
    6: Planet.RAHU,     # Ardra
    7: Planet.JUPITER,  # Punarvasu
    8: Planet.SATURN,   # Pushya
    9: Planet.MERCURY,  # Ashlesha
    10: Planet.KETU,    # Magha
    11: Planet.VENUS,   # Purva Phalguni
    12: Planet.SUN,     # Uttara Phalguni
    13: Planet.MOON,    # Hasta
    14: Planet.MARS,    # Chitra
    15: Planet.RAHU,    # Swati
    16: Planet.JUPITER, # Vishakha
    17: Planet.SATURN,  # Anuradha
    18: Planet.MERCURY, # Jyeshtha
    19: Planet.KETU,    # Moola
    20: Planet.VENUS,   # Purva Ashadha
    21: Planet.SUN,     # Uttara Ashadha
    22: Planet.MOON,    # Shravana
    23: Planet.MARS,    # Dhanishta
    24: Planet.RAHU,    # Shatabhisha
    25: Planet.JUPITER, # Purva Bhadrapada
    26: Planet.SATURN,  # Uttara Bhadrapada
    27: Planet.MERCURY, # Revati
}

# Planet themes for dasha interpretation
PLANET_THEMES: Dict[Planet, List[str]] = {
    Planet.JUPITER: ["expansion", "wisdom", "growth", "children", "education", "investments"],
    Planet.VENUS: ["relationships", "luxury", "arts", "pleasure", "finance", "partnerships"],
    Planet.MERCURY: ["communication", "business", "learning", "travel", "networking"],
    Planet.MOON: ["emotions", "mother", "public", "changes", "real_estate"],
    Planet.SUN: ["authority", "father", "government", "recognition", "leadership"],
    Planet.MARS: ["energy", "competition", "property", "surgery", "action"],
    Planet.SATURN: ["discipline", "delays", "structure", "karma", "hard_work"],
    Planet.RAHU: ["foreign", "innovation", "obsession", "unconventional", "sudden_gains"],
    Planet.KETU: ["spirituality", "loss", "detachment", "research", "endings"],
}


def get_nakshatra_number(moon_longitude: float) -> int:
    """Get nakshatra number (1-27) from Moon's longitude."""
    nakshatra_span = 360 / 27
    nakshatra = int(moon_longitude / nakshatra_span) + 1
    return min(27, max(1, nakshatra))


def get_dasha_balance(moon_longitude: float) -> Tuple[Planet, float]:
    """
    Calculate dasha balance at birth.

    Returns (dasha_lord, remaining_years).
    """
    nakshatra_span = 360 / 27
    nakshatra = get_nakshatra_number(moon_longitude)
    lord = NAKSHATRA_LORDS[nakshatra]

    # Position within nakshatra (0 to 1)
    position_in_nakshatra = (moon_longitude % nakshatra_span) / nakshatra_span

    # Remaining portion of current dasha
    full_period = DASHA_PERIODS[lord]
    remaining = full_period * (1 - position_in_nakshatra)

    return lord, remaining


def add_years_to_date(base_date: date, years: float) -> date:
    """Add years to a date."""
    days = int(years * 365.25)
    return base_date + timedelta(days=days)


def calculate_dasha_sequence(
    birth_date: date,
    moon_longitude: float,
    years_ahead: int = 100
) -> List[DashaPeriod]:
    """
    Calculate full dasha sequence from birth.
    """
    first_lord, remaining = get_dasha_balance(moon_longitude)

    periods = []
    current_date = birth_date

    # Find starting point in sequence
    start_idx = DASHA_SEQUENCE.index(first_lord)

    # First partial dasha
    end_date = add_years_to_date(birth_date, remaining)

    periods.append(DashaPeriod(
        planet=first_lord.value,
        start_date=birth_date.isoformat(),
        end_date=end_date.isoformat(),
        duration_years=remaining,
        is_current=False,
        quality_score=5.0,
        quality=DashaPeriodQuality.MIXED,
        key_themes=PLANET_THEMES.get(first_lord, [])
    ))

    current_date = end_date
    total_years = remaining

    # Continue through sequence
    idx = (start_idx + 1) % 9
    while total_years < years_ahead:
        lord = DASHA_SEQUENCE[idx]
        duration = DASHA_PERIODS[lord]

        end_date = add_years_to_date(current_date, duration)

        periods.append(DashaPeriod(
            planet=lord.value,
            start_date=current_date.isoformat(),
            end_date=end_date.isoformat(),
            duration_years=duration,
            is_current=False,
            quality_score=5.0,
            quality=DashaPeriodQuality.MIXED,
            key_themes=PLANET_THEMES.get(lord, [])
        ))

        current_date = end_date
        total_years += duration
        idx = (idx + 1) % 9

    return periods


def evaluate_dasha_quality(
    planet: Planet,
    planet_strength: Dict[str, float],
    yoga_planets: List[str]
) -> Tuple[float, DashaPeriodQuality]:
    """
    Evaluate quality of a dasha period.
    """
    # Base score from planet strength
    score = planet_strength.get(planet.value, 5.0)

    # Bonus if involved in yogas
    if planet.value in yoga_planets:
        score += 1.5

    # Benefic planets generally better
    if planet in [Planet.JUPITER, Planet.VENUS, Planet.MERCURY]:
        score += 0.5

    score = max(1.0, min(10.0, score))

    # Quality level
    if score >= 9:
        quality = DashaPeriodQuality.GOLDEN
    elif score >= 7:
        quality = DashaPeriodQuality.VERY_FAVORABLE
    elif score >= 5.5:
        quality = DashaPeriodQuality.FAVORABLE
    elif score >= 4:
        quality = DashaPeriodQuality.MIXED
    elif score >= 2:
        quality = DashaPeriodQuality.CHALLENGING
    else:
        quality = DashaPeriodQuality.DIFFICULT

    return score, quality


def calculate_sarvashtakavarga(
    digital_twin: Dict[str, Any]
) -> AshtakavargaScore:
    """
    Calculate Sarvashtakavarga (combined ashtakavarga) scores.

    Simplified calculation based on planet positions.
    Each house gets points based on benefic/malefic positions.
    """
    vargas = digital_twin.get("vargas", {})
    d1 = vargas.get("D1", {})
    planets = d1.get("planets", [])

    # Initialize house scores
    house_bindus: Dict[int, int] = {i: 28 for i in range(1, 13)}  # Base 28 (average)

    benefics = ["JUPITER", "VENUS", "MERCURY", "MOON"]
    malefics = ["SATURN", "MARS", "RAHU", "KETU"]

    for planet in planets:
        name = planet.get("name", "").upper()
        house = planet.get("house_occupied", 1)
        dignity = planet.get("dignity_state", "").lower()

        # Add/subtract based on planet nature and dignity
        if name in benefics:
            house_bindus[house] += 3
            if "exalt" in dignity:
                house_bindus[house] += 2
            elif "own" in dignity:
                house_bindus[house] += 1
        elif name in malefics:
            if "debilitat" in dignity:
                house_bindus[house] -= 2
            elif "enemy" in dignity:
                house_bindus[house] -= 1
            # Malefics in upachaya (3,6,10,11) are good
            if house in [3, 6, 10, 11]:
                house_bindus[house] += 2

    # Clamp values
    for house in house_bindus:
        house_bindus[house] = max(15, min(40, house_bindus[house]))

    total = sum(house_bindus.values())

    # Sort houses by score
    sorted_houses = sorted(house_bindus.items(), key=lambda x: x[1], reverse=True)
    strongest = [h[0] for h in sorted_houses[:3]]
    weakest = [h[0] for h in sorted_houses[-3:]]
    above_avg = [h for h, score in house_bindus.items() if score >= 28]

    return AshtakavargaScore(
        house_bindus=house_bindus,
        total_bindus=total,
        strongest_houses=strongest,
        weakest_houses=weakest,
        above_average_houses=above_avg
    )


def get_timing_recommendation(
    current_quality: DashaPeriodQuality,
    is_golden: bool,
    years_until_golden: float
) -> TimingRecommendation:
    """Get investment timing recommendation."""
    if is_golden:
        return TimingRecommendation.INVEST_NOW

    if current_quality == DashaPeriodQuality.VERY_FAVORABLE:
        return TimingRecommendation.FAVORABLE_TIMING

    if current_quality == DashaPeriodQuality.FAVORABLE:
        if years_until_golden <= 2:
            return TimingRecommendation.WAIT_FOR_BETTER
        return TimingRecommendation.FAVORABLE_TIMING

    if current_quality == DashaPeriodQuality.MIXED:
        return TimingRecommendation.PROCEED_CAUTION

    return TimingRecommendation.DELAY_INVESTMENT


class Stage10TimingAnalysis:
    """Stage 10: Timing analysis class."""

    def __init__(
        self,
        digital_twin: Dict[str, Any],
        d1_planets: List[Dict[str, Any]],
        planet_strength: Optional[Dict[str, float]] = None,
        yoga_planets: Optional[List[str]] = None
    ):
        self.digital_twin = digital_twin
        self.d1_planets = d1_planets
        # Default planet strength if not provided
        self.planet_strength = planet_strength or {
            "Sun": 0.5, "Moon": 0.5, "Mars": 0.5, "Mercury": 0.5,
            "Jupiter": 0.5, "Venus": 0.5, "Saturn": 0.5, "Rahu": 0.5, "Ketu": 0.5
        }
        # Default yoga planets (benefics) if not provided
        self.yoga_planets = yoga_planets or ["Jupiter", "Venus"]

        # Extract birth date and moon position
        meta = digital_twin.get("meta", {})
        birth_dt = meta.get("birth_datetime", "1990-01-01T12:00:00")
        self.birth_date = date.fromisoformat(birth_dt.split("T")[0])

        # Get Moon longitude
        self.moon_longitude = 0.0
        for p in d1_planets:
            name = _get_planet_attr(p, "name", "")
            if name.upper() == "MOON":
                self.moon_longitude = _get_planet_attr(p, "absolute_degree", 0.0)
                break

        self.today = date.today()

    def analyze(self) -> Stage10Result:
        """Run complete Stage 10 analysis."""
        # Calculate dasha sequence
        dasha_periods = calculate_dasha_sequence(
            self.birth_date,
            self.moon_longitude,
            years_ahead=120
        )

        # Evaluate quality for each period
        for period in dasha_periods:
            planet = Planet(period.planet)
            score, quality = evaluate_dasha_quality(
                planet, self.planet_strength, self.yoga_planets
            )
            period.quality_score = score
            period.quality = quality

        # Find current period
        current_mahadasha = None
        for period in dasha_periods:
            start = date.fromisoformat(period.start_date)
            end = date.fromisoformat(period.end_date)
            if start <= self.today <= end:
                current_mahadasha = period
                current_mahadasha.is_current = True
                break

        if not current_mahadasha:
            current_mahadasha = dasha_periods[0]
            current_mahadasha.is_current = True

        # Find upcoming periods (next 5)
        upcoming = []
        found_current = False
        for period in dasha_periods:
            if period.is_current:
                found_current = True
                continue
            if found_current and len(upcoming) < 5:
                upcoming.append(period)

        # Find golden and challenging periods
        golden_periods = []
        challenging_periods = []

        for period in dasha_periods:
            start = date.fromisoformat(period.start_date)
            # Only look at future periods
            if start < self.today:
                continue

            if period.quality in [DashaPeriodQuality.GOLDEN, DashaPeriodQuality.VERY_FAVORABLE]:
                golden_periods.append({
                    "start": period.start_date,
                    "end": period.end_date,
                    "planet": period.planet,
                    "quality": period.quality.value
                })
            elif period.quality in [DashaPeriodQuality.DIFFICULT, DashaPeriodQuality.CHALLENGING]:
                challenging_periods.append({
                    "start": period.start_date,
                    "end": period.end_date,
                    "planet": period.planet,
                    "quality": period.quality.value
                })

        # Dasha roadmap
        roadmap = DashaRoadmap(
            current_mahadasha=current_mahadasha,
            current_antardasha=None,  # Simplified - no antardasha calculation
            upcoming_periods=upcoming,
            golden_periods=golden_periods[:5],
            challenging_periods=challenging_periods[:5]
        )

        # Calculate Ashtakavarga
        ashtakavarga = calculate_sarvashtakavarga(self.digital_twin)

        # Is it a golden period?
        is_golden = current_mahadasha.quality in [
            DashaPeriodQuality.GOLDEN,
            DashaPeriodQuality.VERY_FAVORABLE
        ]

        # Years until next golden period
        years_until_golden = 0.0
        if not is_golden and golden_periods:
            next_golden_start = date.fromisoformat(golden_periods[0]["start"])
            years_until_golden = (next_golden_start - self.today).days / 365.25

        # Timing recommendation
        recommendation = get_timing_recommendation(
            current_mahadasha.quality,
            is_golden,
            years_until_golden
        )

        # Calculate best/caution years
        current_year = self.today.year
        best_years = []
        caution_years = []
        career_years = []
        wealth_years = []

        for period in dasha_periods:
            start = date.fromisoformat(period.start_date)
            end = date.fromisoformat(period.end_date)

            # Check if period overlaps with next 10 years
            for year in range(current_year, current_year + 10):
                year_start = date(year, 1, 1)
                year_end = date(year, 12, 31)

                if start <= year_end and end >= year_start:
                    if period.quality in [DashaPeriodQuality.GOLDEN, DashaPeriodQuality.VERY_FAVORABLE]:
                        if year not in best_years:
                            best_years.append(year)
                    elif period.quality in [DashaPeriodQuality.DIFFICULT, DashaPeriodQuality.CHALLENGING]:
                        if year not in caution_years:
                            caution_years.append(year)

                    # Career years (Sun, Saturn, Mars dashas)
                    if period.planet in ["Sun", "Saturn", "Mars"]:
                        if year not in career_years:
                            career_years.append(year)

                    # Wealth years (Venus, Jupiter, Mercury dashas)
                    if period.planet in ["Venus", "Jupiter", "Mercury"]:
                        if year not in wealth_years:
                            wealth_years.append(year)

        # Generate timing summary
        if is_golden:
            summary = f"Currently in {current_mahadasha.planet} Mahadasha - GOLDEN period. Excellent time for major initiatives and investments."
        elif current_mahadasha.quality == DashaPeriodQuality.FAVORABLE:
            summary = f"Currently in {current_mahadasha.planet} Mahadasha - Favorable period. Good time for steady progress."
        elif current_mahadasha.quality == DashaPeriodQuality.MIXED:
            summary = f"Currently in {current_mahadasha.planet} Mahadasha - Mixed period. Proceed with careful evaluation."
        else:
            if years_until_golden > 0:
                summary = f"Currently in {current_mahadasha.planet} Mahadasha - Challenging period. Better opportunities in {years_until_golden:.1f} years."
            else:
                summary = f"Currently in {current_mahadasha.planet} Mahadasha - Challenging period. Focus on consolidation."

        # Indices
        indices = {
            "current_dasha_score": current_mahadasha.quality_score,
            "ashtakavarga_total": ashtakavarga.total_bindus,
            "timing_favorability": current_mahadasha.quality_score / 10 * 100
        }

        return Stage10Result(
            dasha_roadmap=roadmap,
            current_dasha_quality=current_mahadasha.quality,
            ashtakavarga=ashtakavarga,
            is_golden_period=is_golden,
            years_until_golden=years_until_golden,
            timing_recommendation=recommendation,
            best_years=sorted(best_years)[:5],
            caution_years=sorted(caution_years)[:5],
            career_activation_years=sorted(career_years)[:5],
            wealth_activation_years=sorted(wealth_years)[:5],
            timing_summary=summary,
            indices=indices
        )
