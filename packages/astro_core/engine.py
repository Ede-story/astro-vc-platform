"""
AstroCore V2 - Clean Slate Implementation
==========================================
The "New Heart" of StarMeet Astro Calculations.

Architecture: MIDDLEWARE PATTERN
--------------------------------
1. INPUT: Date/Time/Location
2. STEP A: Get RAW ABSOLUTE LONGITUDE (0-360) from jyotishganit (True Chitrapaksha)
3. STEP B: Calculate RAMAN_DELTA using swisseph, apply shift
4. STEP C: Pass CORRECTED_ABS_LONGITUDE (0-360) to native library Varga functions
5. OUTPUT: Clean data structure for UI

KEY PRINCIPLE: We ALWAYS work with ABSOLUTE LONGITUDE (0-360).
             We NEVER manually calculate Varga signs - trust the library.

Author: StarMeet Team
Version: 2.0.0 (Clean Slate)
"""

import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

# Swiss Ephemeris for ayanamsa calculations
import swisseph as swe

# jyotishganit library - our trusted calculation engine
from jyotishganit import calculate_birth_chart

# Native Varga functions from jyotishganit
from jyotishganit.components.divisional_charts import (
    hora_from_long,
    drekkana_from_long,
    chaturtamsa_from_long,
    saptamsa_from_long,
    navamsa_from_long,
    dasamsa_from_long,
    dwadasamsa_from_long,
    shodasamsa_from_long,
    vimsamsa_from_long,
    chaturvimsamsa_from_long,
    sapta_vimsamsa_from_long,
    trimsamsa_from_long,
    khavedamsa_from_long,
    akshavedamsa_from_long,
    shashtiamsa_from_long,
)

# =============================================================================
# CONSTANTS
# =============================================================================

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

# Ayanamsa IDs for Swiss Ephemeris
AYANAMSA_IDS = {
    'Lahiri': swe.SIDM_LAHIRI,
    'Raman': swe.SIDM_RAMAN,
    'True_Chitrapaksha': swe.SIDM_TRUE_CITRA,
    'Krishnamurti': swe.SIDM_KRISHNAMURTI,
    'Fagan_Bradley': swe.SIDM_FAGAN_BRADLEY,
}

# All supported Varga charts
VARGA_CODES = ['D1', 'D2', 'D3', 'D4', 'D7', 'D9', 'D10', 'D12',
               'D16', 'D20', 'D24', 'D27', 'D30', 'D40', 'D45', 'D60']

# Sign Lords (Rulers)
SIGN_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

# Nakshatra Lords (Vimshottari Dasha order)
NAKSHATRA_LORDS = {
    'Ashwini': 'Ketu', 'Bharani': 'Venus', 'Krittika': 'Sun',
    'Rohini': 'Moon', 'Mrigashira': 'Mars', 'Ardra': 'Rahu',
    'Punarvasu': 'Jupiter', 'Pushya': 'Saturn', 'Ashlesha': 'Mercury',
    'Magha': 'Ketu', 'Purva Phalguni': 'Venus', 'Uttara Phalguni': 'Sun',
    'Hasta': 'Moon', 'Chitra': 'Mars', 'Swati': 'Rahu',
    'Vishakha': 'Jupiter', 'Anuradha': 'Saturn', 'Jyeshtha': 'Mercury',
    'Mula': 'Ketu', 'Purva Ashadha': 'Venus', 'Uttara Ashadha': 'Sun',
    'Shravana': 'Moon', 'Dhanishta': 'Mars', 'Shatabhisha': 'Rahu',
    'Purva Bhadrapada': 'Jupiter', 'Uttara Bhadrapada': 'Saturn', 'Revati': 'Mercury'
}

# Planet Exaltation Signs
EXALTATION_SIGNS = {
    'Sun': 'Aries', 'Moon': 'Taurus', 'Mars': 'Capricorn', 'Mercury': 'Virgo',
    'Jupiter': 'Cancer', 'Venus': 'Pisces', 'Saturn': 'Libra',
    'Rahu': 'Taurus', 'Ketu': 'Scorpio'
}

# Planet Debilitation Signs
DEBILITATION_SIGNS = {
    'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer', 'Mercury': 'Pisces',
    'Jupiter': 'Capricorn', 'Venus': 'Virgo', 'Saturn': 'Aries',
    'Rahu': 'Scorpio', 'Ketu': 'Taurus'
}

# Own Signs (Swakshetra)
OWN_SIGNS = {
    'Sun': ['Leo'],
    'Moon': ['Cancer'],
    'Mars': ['Aries', 'Scorpio'],
    'Mercury': ['Gemini', 'Virgo'],
    'Jupiter': ['Sagittarius', 'Pisces'],
    'Venus': ['Taurus', 'Libra'],
    'Saturn': ['Capricorn', 'Aquarius'],
    'Rahu': ['Aquarius'],
    'Ketu': ['Scorpio']
}

# Moolatrikona Signs (with degree ranges)
# Format: {planet: (sign, start_degree, end_degree)}
MOOLATRIKONA = {
    'Sun': ('Leo', 0, 20),           # Sun: Leo 0-20°
    'Moon': ('Taurus', 3, 30),       # Moon: Taurus 3-30°
    'Mars': ('Aries', 0, 12),        # Mars: Aries 0-12°
    'Mercury': ('Virgo', 15, 20),    # Mercury: Virgo 15-20°
    'Jupiter': ('Sagittarius', 0, 10), # Jupiter: Sagittarius 0-10°
    'Venus': ('Libra', 0, 15),       # Venus: Libra 0-15°
    'Saturn': ('Aquarius', 0, 20),   # Saturn: Aquarius 0-20°
}

# Natural Friendships
NATURAL_FRIENDS = {
    'Sun': ['Moon', 'Mars', 'Jupiter'],
    'Moon': ['Sun', 'Mercury'],
    'Mars': ['Sun', 'Moon', 'Jupiter'],
    'Mercury': ['Sun', 'Venus'],
    'Jupiter': ['Sun', 'Moon', 'Mars'],
    'Venus': ['Mercury', 'Saturn'],
    'Saturn': ['Mercury', 'Venus'],
    'Rahu': ['Mercury', 'Venus', 'Saturn'],
    'Ketu': ['Mars', 'Venus', 'Saturn']
}

# Natural Enemies
NATURAL_ENEMIES = {
    'Sun': ['Venus', 'Saturn'],
    'Moon': [],
    'Mars': ['Mercury'],
    'Mercury': ['Moon'],
    'Jupiter': ['Mercury', 'Venus'],
    'Venus': ['Sun', 'Moon'],
    'Saturn': ['Sun', 'Moon', 'Mars'],
    'Rahu': ['Sun', 'Moon', 'Mars'],
    'Ketu': ['Sun', 'Moon']
}

# Graha Drishti (Planetary Aspects) - which houses from own position
PLANETARY_ASPECTS = {
    'Sun': [7],       # 7th aspect
    'Moon': [7],      # 7th aspect
    'Mars': [4, 7, 8],  # 4th, 7th, 8th aspects
    'Mercury': [7],   # 7th aspect
    'Jupiter': [5, 7, 9],  # 5th, 7th, 9th aspects
    'Venus': [7],     # 7th aspect
    'Saturn': [3, 7, 10],  # 3rd, 7th, 10th aspects
    'Rahu': [5, 7, 9],  # Same as Jupiter
    'Ketu': [5, 7, 9]   # Same as Jupiter
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PlanetPosition:
    """Clean representation of a planet's position."""
    name: str                    # English name (Sun, Moon, Mars, etc.)
    abs_longitude: float         # CORRECTED absolute longitude (0-360)
    sign: str                    # Sign name (Aries, Taurus, etc.)
    sign_degrees: float          # Degrees within sign (0-30)
    nakshatra: str               # Nakshatra name
    nakshatra_pada: int          # Pada (1-4)
    house: int                   # House number (1-12)

    # Varga signs (populated by calculate_all_vargas)
    varga_signs: Dict[str, str] = field(default_factory=dict)

    # Extended data (Lords, Dignity, Aspects)
    sign_lord: str = ""          # Lord of the sign this planet occupies
    nakshatra_lord: str = ""     # Lord of the nakshatra
    houses_owned: List[int] = field(default_factory=list)  # Houses this planet rules
    dignity: str = ""            # Exalted/Debilitated/Own/Friend/Neutral/Enemy
    conjunctions: List[str] = field(default_factory=list)  # Planets in same sign
    aspects_giving: List[int] = field(default_factory=list)  # Houses this planet aspects
    aspects_receiving: List[str] = field(default_factory=list)  # Planets aspecting this one


@dataclass
class HousePosition:
    """Clean representation of a house cusp."""
    house_number: int            # 1-12
    abs_longitude: float         # CORRECTED absolute longitude (0-360)
    sign: str                    # Sign name
    sign_degrees: float          # Degrees within sign (0-30)

    # Extended data
    lord: str = ""               # Planet ruling this house's sign
    occupants: List[str] = field(default_factory=list)  # Planets in this house
    aspects_received: List[str] = field(default_factory=list)  # Planets aspecting this house


@dataclass
class ChartData:
    """Complete chart data structure."""
    # Input data
    birth_datetime: datetime.datetime
    latitude: float
    longitude: float
    timezone: str
    ayanamsa: str

    # Calculated data
    julian_day: float
    ayanamsa_delta: float        # Delta applied to convert from True_Chitrapaksha to target

    # Positions
    planets: List[PlanetPosition]
    houses: List[HousePosition]

    # Ascendant info
    ascendant_sign: str
    ascendant_degrees: float


# =============================================================================
# HELPER FUNCTIONS FOR EXTENDED DATA
# =============================================================================

def get_planet_dignity(planet_name: str, sign: str, degrees: float = None) -> str:
    """
    Calculate the dignity of a planet in a given sign.

    Priority order (highest to lowest):
    1. Exalted (Uccha)
    2. Moolatrikona (if degrees within range)
    3. Own (Swakshetra)
    4. Debilitated (Neecha)
    5. Friend/Neutral/Enemy (based on sign lord relationship)

    Args:
        planet_name: Name of the planet
        sign: Sign name
        degrees: Degrees within sign (0-30), needed for Moolatrikona check

    Returns: 'Exalted', 'Moolatrikona', 'Own', 'Debilitated', 'Friend', 'Neutral', or 'Enemy'
    """
    if planet_name not in EXALTATION_SIGNS:
        return 'Neutral'

    # Check exaltation
    if EXALTATION_SIGNS.get(planet_name) == sign:
        return 'Exalted'

    # Check debilitation
    if DEBILITATION_SIGNS.get(planet_name) == sign:
        return 'Debilitated'

    # Check Moolatrikona (requires degrees)
    if planet_name in MOOLATRIKONA and degrees is not None:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet_name]
        if sign == mt_sign and mt_start <= degrees <= mt_end:
            return 'Moolatrikona'

    # Check own sign
    if sign in OWN_SIGNS.get(planet_name, []):
        return 'Own'

    # Check friendship with sign lord
    sign_lord = SIGN_LORDS.get(sign, '')
    if sign_lord == planet_name:
        return 'Own'

    if sign_lord in NATURAL_FRIENDS.get(planet_name, []):
        return 'Friend'

    if sign_lord in NATURAL_ENEMIES.get(planet_name, []):
        return 'Enemy'

    return 'Neutral'


def get_houses_owned(planet_name: str, house_signs: Dict[int, str]) -> List[int]:
    """
    Find which houses a planet owns (rules) based on house signs.

    Args:
        planet_name: Name of the planet
        house_signs: Dict mapping house number to sign

    Returns:
        List of house numbers this planet rules
    """
    owned = []
    for house_num, sign in house_signs.items():
        if SIGN_LORDS.get(sign) == planet_name:
            owned.append(house_num)
    return sorted(owned)


def get_aspects_giving(planet_name: str, planet_house: int) -> List[int]:
    """
    Calculate which houses a planet aspects from its position.

    Args:
        planet_name: Name of the planet
        planet_house: House number where planet is placed (1-12)

    Returns:
        List of house numbers the planet aspects
    """
    aspect_offsets = PLANETARY_ASPECTS.get(planet_name, [7])
    aspected_houses = []

    for offset in aspect_offsets:
        target_house = ((planet_house - 1 + offset) % 12) + 1
        aspected_houses.append(target_house)

    return sorted(aspected_houses)


# =============================================================================
# CORE CALCULATION FUNCTIONS
# =============================================================================

def datetime_to_jd(dt: datetime.datetime, tz_offset_hours: float) -> float:
    """
    Convert datetime to Julian Day.

    Args:
        dt: Local datetime
        tz_offset_hours: Timezone offset in hours (e.g., +3 for Moscow)

    Returns:
        Julian Day number
    """
    # Convert to UTC
    utc_dt = dt - datetime.timedelta(hours=tz_offset_hours)

    # Calculate Julian Day
    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day
    hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0

    jd = swe.julday(year, month, day, hour)
    return jd


def get_ayanamsa_value(jd: float, ayanamsa_name: str) -> float:
    """
    Get ayanamsa value for a given Julian Day.

    Args:
        jd: Julian Day
        ayanamsa_name: Name of ayanamsa (Lahiri, Raman, True_Chitrapaksha, etc.)

    Returns:
        Ayanamsa value in degrees
    """
    ayanamsa_id = AYANAMSA_IDS.get(ayanamsa_name, swe.SIDM_TRUE_CITRA)
    swe.set_sid_mode(ayanamsa_id)
    return swe.get_ayanamsa_ut(jd)


def calculate_raman_delta(jd: float) -> float:
    """
    Calculate the delta between True_Chitrapaksha (jyotishganit default) and Raman.

    This delta is ADDED to True_Chitrapaksha positions to get Raman positions.

    Formula:
        Delta = True_Chitrapaksha_Ayanamsa - Raman_Ayanamsa
        (Because: sidereal_long = tropical_long - ayanamsa)
        (If Raman has smaller ayanamsa, its sidereal longitude is higher)

    Args:
        jd: Julian Day

    Returns:
        Delta in degrees (positive means add to get Raman)
    """
    chitrapaksha_value = get_ayanamsa_value(jd, 'True_Chitrapaksha')
    raman_value = get_ayanamsa_value(jd, 'Raman')

    # Delta = source - target
    delta = chitrapaksha_value - raman_value
    return delta


def normalize_longitude(longitude: float) -> float:
    """Normalize longitude to 0-360 range."""
    longitude = longitude % 360
    if longitude < 0:
        longitude += 360
    return longitude


def longitude_to_sign_degrees(abs_longitude: float) -> Tuple[str, float]:
    """
    Convert absolute longitude (0-360) to sign name and degrees within sign.

    Args:
        abs_longitude: Absolute longitude in degrees (0-360)

    Returns:
        Tuple of (sign_name, degrees_in_sign)
    """
    abs_longitude = normalize_longitude(abs_longitude)
    sign_idx = int(abs_longitude / 30)
    degrees_in_sign = abs_longitude % 30
    return SIGNS[sign_idx], degrees_in_sign


def longitude_to_nakshatra(abs_longitude: float) -> Tuple[str, int]:
    """
    Convert absolute longitude to nakshatra and pada.

    Each nakshatra spans 13°20' (13.333...°)
    Each pada spans 3°20' (3.333...°)

    Args:
        abs_longitude: Absolute longitude in degrees (0-360)

    Returns:
        Tuple of (nakshatra_name, pada_number)
    """
    abs_longitude = normalize_longitude(abs_longitude)

    # Each nakshatra = 360/27 = 13.333... degrees
    nakshatra_span = 360.0 / 27.0
    pada_span = nakshatra_span / 4.0

    nakshatra_idx = int(abs_longitude / nakshatra_span)
    nakshatra_idx = min(nakshatra_idx, 26)  # Safety bound

    # Calculate pada within nakshatra
    degrees_in_nakshatra = abs_longitude % nakshatra_span
    pada = int(degrees_in_nakshatra / pada_span) + 1
    pada = min(pada, 4)  # Safety bound

    return NAKSHATRAS[nakshatra_idx], pada


# =============================================================================
# VARGA CALCULATION - THE CRITICAL PART
# =============================================================================

def get_varga_sign(abs_longitude: float, varga_code: str) -> str:
    """
    Calculate the sign for a given Varga chart using NATIVE library functions.

    THIS IS THE HEART OF THE SYSTEM.

    CRITICAL: We pass ABSOLUTE LONGITUDE (0-360), not relative degrees!
    The library functions expect (sign_name, degrees_in_sign) format,
    so we convert internally.

    Args:
        abs_longitude: CORRECTED absolute longitude (0-360) - already Raman-shifted
        varga_code: Varga chart code (D1, D2, D3, ..., D60)

    Returns:
        Sign name in the specified Varga chart
    """
    # Safety check
    if abs_longitude is None:
        return "Aries"

    # Normalize to 0-360
    abs_longitude = normalize_longitude(float(abs_longitude))

    # Convert to sign + degrees format for library functions
    sign_name, degrees_in_sign = longitude_to_sign_degrees(abs_longitude)

    varga_upper = varga_code.upper()

    try:
        if varga_upper == 'D1':
            return sign_name

        elif varga_upper == 'D2':
            _, result_sign, _ = hora_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D3':
            _, result_sign, _ = drekkana_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D4':
            _, result_sign, _ = chaturtamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D7':
            _, result_sign, _ = saptamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D9':
            _, result_sign, _ = navamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D10':
            _, result_sign, _ = dasamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D12':
            _, result_sign, _ = dwadasamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D16':
            _, result_sign, _ = shodasamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D20':
            _, result_sign, _ = vimsamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D24':
            _, result_sign, _ = chaturvimsamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D27':
            _, result_sign, _ = sapta_vimsamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D30':
            _, result_sign, _ = trimsamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D40':
            _, result_sign, _ = khavedamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D45':
            _, result_sign, _ = akshavedamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        elif varga_upper == 'D60':
            _, result_sign, _ = shashtiamsa_from_long(sign_name, degrees_in_sign)
            return result_sign

        else:
            # Unknown Varga - return D1 sign
            return sign_name

    except Exception as e:
        # Fallback to D1 sign if library function fails
        return sign_name


def get_varga_sign_and_degrees(abs_longitude: float, varga_code: str) -> Tuple[str, float]:
    """
    Calculate the sign AND degrees for a given Varga chart.

    The library functions return a tuple: (part_number, sign, degrees_in_part)
    For varga degrees, we calculate where the planet is within its varga sign.

    Args:
        abs_longitude: CORRECTED absolute longitude (0-360)
        varga_code: Varga chart code (D1, D2, D3, ..., D60)

    Returns:
        Tuple of (sign_name, degrees_in_varga_sign)
    """
    if abs_longitude is None:
        return ("Aries", 0.0)

    abs_longitude = normalize_longitude(float(abs_longitude))
    sign_name, degrees_in_sign = longitude_to_sign_degrees(abs_longitude)

    varga_upper = varga_code.upper()

    try:
        if varga_upper == 'D1':
            return (sign_name, degrees_in_sign)

        elif varga_upper == 'D2':
            part, result_sign, deg = hora_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D3':
            part, result_sign, deg = drekkana_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D4':
            part, result_sign, deg = chaturtamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D7':
            part, result_sign, deg = saptamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D9':
            part, result_sign, deg = navamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D10':
            part, result_sign, deg = dasamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D12':
            part, result_sign, deg = dwadasamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D16':
            part, result_sign, deg = shodasamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D20':
            part, result_sign, deg = vimsamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D24':
            part, result_sign, deg = chaturvimsamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D27':
            part, result_sign, deg = sapta_vimsamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D30':
            part, result_sign, deg = trimsamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D40':
            part, result_sign, deg = khavedamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D45':
            part, result_sign, deg = akshavedamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        elif varga_upper == 'D60':
            part, result_sign, deg = shashtiamsa_from_long(sign_name, degrees_in_sign)
            return (result_sign, deg if deg is not None else 0.0)

        else:
            return (sign_name, degrees_in_sign)

    except Exception as e:
        return (sign_name, degrees_in_sign)


def calculate_all_vargas(abs_longitude: float) -> Dict[str, str]:
    """
    Calculate all Varga signs for a given absolute longitude.

    Args:
        abs_longitude: CORRECTED absolute longitude (0-360)

    Returns:
        Dict mapping Varga code to sign name
    """
    vargas = {}
    for varga_code in VARGA_CODES:
        vargas[varga_code] = get_varga_sign(abs_longitude, varga_code)
    return vargas


def calculate_all_vargas_with_degrees(abs_longitude: float) -> Dict[str, Dict[str, Any]]:
    """
    Calculate all Varga signs AND degrees for a given absolute longitude.

    Args:
        abs_longitude: CORRECTED absolute longitude (0-360)

    Returns:
        Dict mapping Varga code to {sign, degrees}
    """
    vargas = {}
    for varga_code in VARGA_CODES:
        sign, degrees = get_varga_sign_and_degrees(abs_longitude, varga_code)
        vargas[varga_code] = {"sign": sign, "degrees": round(degrees, 4)}
    return vargas


# =============================================================================
# MAIN CALCULATION CLASS
# =============================================================================

class AstroCore:
    """
    Main calculation engine for Vedic Astrology.

    Usage:
        core = AstroCore()
        chart = core.calculate(
            birth_datetime=datetime.datetime(1977, 10, 25, 6, 28),
            latitude=61.7,
            longitude=30.7,
            tz_offset_hours=3.0,
            ayanamsa='Raman'
        )
    """

    def __init__(self):
        """Initialize the calculation core."""
        pass

    def calculate(
        self,
        birth_datetime: datetime.datetime,
        latitude: float,
        longitude: float,
        tz_offset_hours: float,
        timezone_name: str = 'UTC',
        ayanamsa: str = 'Raman'
    ) -> ChartData:
        """
        Calculate a complete Vedic chart.

        THE MIDDLEWARE PATTERN:
        1. Get RAW data from jyotishganit (True Chitrapaksha)
        2. Calculate Raman delta
        3. Apply delta to all positions
        4. Calculate Vargas from CORRECTED absolute longitudes

        Args:
            birth_datetime: Birth date and time (local time)
            latitude: Birth latitude
            longitude: Birth longitude (geographic, not to confuse with celestial)
            tz_offset_hours: Timezone offset in hours
            timezone_name: Timezone name for display
            ayanamsa: Target ayanamsa ('Raman', 'Lahiri', etc.)

        Returns:
            Complete ChartData object
        """
        # Step 0: Calculate Julian Day
        jd = datetime_to_jd(birth_datetime, tz_offset_hours)

        # Step 1: Get RAW chart from jyotishganit (True Chitrapaksha)
        raw_chart = calculate_birth_chart(
            birth_date=birth_datetime,
            latitude=latitude,
            longitude=longitude,
            timezone_offset=tz_offset_hours
        )

        # Step 2: Calculate ayanamsa delta (only if Raman is selected)
        if ayanamsa == 'Raman':
            ayanamsa_delta = calculate_raman_delta(jd)
        else:
            ayanamsa_delta = 0.0

        # Step 3: Process houses FIRST (we need house signs for planet lordships)
        houses = []
        house_signs: Dict[int, str] = {}
        ascendant_sign = "Aries"
        ascendant_degrees = 0.0

        if hasattr(raw_chart, 'd1_chart') and hasattr(raw_chart.d1_chart, 'houses'):
            for i, h in enumerate(raw_chart.d1_chart.houses):
                raw_sign = str(h.sign)
                raw_degrees = float(getattr(h, 'sign_degrees', 0) or 0)

                # Calculate RAW absolute longitude
                raw_sign_idx = SIGNS.index(raw_sign) if raw_sign in SIGNS else 0
                raw_abs_longitude = raw_sign_idx * 30 + raw_degrees

                # Apply Raman delta
                corrected_longitude = normalize_longitude(raw_abs_longitude + ayanamsa_delta)

                # Convert back to sign + degrees
                corrected_sign, corrected_degrees = longitude_to_sign_degrees(corrected_longitude)

                house_num = i + 1
                house_signs[house_num] = corrected_sign

                house = HousePosition(
                    house_number=house_num,
                    abs_longitude=corrected_longitude,
                    sign=corrected_sign,
                    sign_degrees=corrected_degrees,
                    lord=SIGN_LORDS.get(corrected_sign, '')
                )
                houses.append(house)

                # Store ascendant info (House 1)
                if i == 0:
                    ascendant_sign = corrected_sign
                    ascendant_degrees = corrected_degrees

        # Step 4: Process planets - apply delta and calculate vargas
        planets = []
        planet_signs: Dict[str, str] = {}  # For conjunction calculation
        planet_houses: Dict[str, int] = {}  # For aspect calculation

        if hasattr(raw_chart, 'd1_chart') and hasattr(raw_chart.d1_chart, 'planets'):
            for p in raw_chart.d1_chart.planets:
                # Get RAW absolute longitude from library
                raw_sign = str(p.sign)
                raw_degrees = float(p.sign_degrees)

                # Calculate RAW absolute longitude
                raw_sign_idx = SIGNS.index(raw_sign) if raw_sign in SIGNS else 0
                raw_abs_longitude = raw_sign_idx * 30 + raw_degrees

                # Apply Raman delta (THE SHIFT)
                corrected_longitude = normalize_longitude(raw_abs_longitude + ayanamsa_delta)

                # Convert back to sign + degrees
                corrected_sign, corrected_degrees = longitude_to_sign_degrees(corrected_longitude)

                # Get nakshatra from CORRECTED longitude
                nakshatra, pada = longitude_to_nakshatra(corrected_longitude)

                # Calculate ALL Varga signs from CORRECTED longitude
                varga_signs = calculate_all_vargas(corrected_longitude)

                planet_name = str(p.celestial_body)
                planet_signs[planet_name] = corrected_sign
                planet_houses[planet_name] = p.house

                # Create planet position object with extended data
                planet = PlanetPosition(
                    name=planet_name,
                    abs_longitude=corrected_longitude,
                    sign=corrected_sign,
                    sign_degrees=corrected_degrees,
                    nakshatra=nakshatra,
                    nakshatra_pada=pada,
                    house=p.house,
                    varga_signs=varga_signs,
                    sign_lord=SIGN_LORDS.get(corrected_sign, ''),
                    nakshatra_lord=NAKSHATRA_LORDS.get(nakshatra, ''),
                    houses_owned=get_houses_owned(planet_name, house_signs),
                    dignity=get_planet_dignity(planet_name, corrected_sign, corrected_degrees),
                    aspects_giving=get_aspects_giving(planet_name, p.house)
                )
                planets.append(planet)

        # Step 5: Calculate conjunctions and aspects received (need all planets first)
        for planet in planets:
            # Conjunctions - planets in the same sign
            planet.conjunctions = [
                p_name for p_name, p_sign in planet_signs.items()
                if p_sign == planet.sign and p_name != planet.name
            ]

            # Aspects receiving - which planets aspect this planet's house
            for other_planet in planets:
                if other_planet.name != planet.name:
                    if planet.house in other_planet.aspects_giving:
                        planet.aspects_receiving.append(other_planet.name)

        # Step 6: Update houses with occupants and aspects
        for house in houses:
            # Occupants - planets in this house
            house.occupants = [
                p.name for p in planets if p.house == house.house_number
            ]

            # Aspects received - planets aspecting this house
            house.aspects_received = [
                p.name for p in planets if house.house_number in p.aspects_giving
            ]

        # Step 7: Create and return ChartData
        return ChartData(
            birth_datetime=birth_datetime,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone_name,
            ayanamsa=ayanamsa,
            julian_day=jd,
            ayanamsa_delta=ayanamsa_delta,
            planets=planets,
            houses=houses,
            ascendant_sign=ascendant_sign,
            ascendant_degrees=ascendant_degrees
        )


# =============================================================================
# CONVENIENCE FUNCTIONS (for backward compatibility with UI)
# =============================================================================

def calculate_chart(
    birth_datetime: datetime.datetime,
    latitude: float,
    longitude: float,
    tz_offset_hours: float,
    timezone_name: str = 'UTC',
    ayanamsa: str = 'Raman'
) -> ChartData:
    """
    Convenience function to calculate a chart.

    Same as AstroCore().calculate()
    """
    core = AstroCore()
    return core.calculate(
        birth_datetime=birth_datetime,
        latitude=latitude,
        longitude=longitude,
        tz_offset_hours=tz_offset_hours,
        timezone_name=timezone_name,
        ayanamsa=ayanamsa
    )


# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# =============================================================================

def datetime_to_jd_compat(dt: datetime.datetime, offset: float) -> float:
    """Legacy compatibility wrapper for datetime_to_jd."""
    return datetime_to_jd(dt, offset)


def get_ayanamsa_delta(jd: float, source: str = 'True_Chitrapaksha', target: str = 'Raman') -> float:
    """
    Legacy compatibility function for getting ayanamsa delta.

    Note: We only support True_Chitrapaksha -> Raman conversion.
    """
    if target == 'Raman':
        return calculate_raman_delta(jd)
    return 0.0


def convert_planet_position(original_sign: str, original_degrees: float, delta: float) -> Dict:
    """
    Legacy compatibility function for converting planet position.

    Converts sign + degrees with a delta shift.

    Args:
        original_sign: Original sign name
        original_degrees: Degrees within sign (0-30)
        delta: Delta to add

    Returns:
        Dict with new position data
    """
    # Calculate original absolute longitude
    original_sign = original_sign.strip().title() if original_sign else "Aries"
    sign_idx = SIGNS.index(original_sign) if original_sign in SIGNS else 0
    original_longitude = sign_idx * 30 + original_degrees

    # Apply delta
    new_longitude = normalize_longitude(original_longitude + delta)

    # Get new values
    new_sign, new_degrees = longitude_to_sign_degrees(new_longitude)
    nakshatra, pada = longitude_to_nakshatra(new_longitude)
    navamsha = get_varga_sign(new_longitude, 'D9')

    return {
        'longitude': new_longitude,
        'sign': new_sign,
        'degrees': new_degrees,
        'nakshatra': nakshatra,
        'pada': pada,
        'navamsha': navamsha
    }


def calculate_navamsha_sign(abs_longitude: float) -> str:
    """Legacy compatibility function for calculating navamsha sign."""
    return get_varga_sign(abs_longitude, 'D9')


# =============================================================================
# DIGITAL TWIN GENERATOR
# =============================================================================

def generate_digital_twin(
    birth_datetime: datetime.datetime,
    latitude: float,
    longitude: float,
    tz_offset_hours: float,
    ayanamsa: str = 'Lahiri'
) -> Dict[str, Any]:
    """
    Generate a complete "Digital Twin" - comprehensive astrological data
    for ALL 16 Varga charts, optimized for AI/LLM analysis.

    This function produces a rich JSON structure containing:
    - For each of 16 Vargas (D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60):
      - Ascendant data (sign, degrees)
      - Complete planetary data (9 planets) with:
        - sign_id, sign_name, absolute_degree, relative_degree
        - house_occupied, houses_owned, nakshatra, nakshatra_lord, pada
        - sign_lord, dignity_state, aspects_giving, aspects_receiving, conjunctions
      - Complete house data (12 houses) with:
        - sign, lord, occupants, aspects_received

    Args:
        birth_datetime: Birth date and time (local time)
        latitude: Birth latitude
        longitude: Birth longitude
        tz_offset_hours: Timezone offset in hours
        ayanamsa: Ayanamsa to use ('Lahiri', 'Raman', etc.)

    Returns:
        Dict with structure: {
            "meta": {...},
            "vargas": {
                "D1": {"ascendant": {...}, "planets": [...], "houses": [...]},
                "D9": {...},
                ...
            }
        }
    """
    # Step 1: Calculate base D1 chart using AstroCore
    core = AstroCore()
    base_chart = core.calculate(
        birth_datetime=birth_datetime,
        latitude=latitude,
        longitude=longitude,
        tz_offset_hours=tz_offset_hours,
        timezone_name=f"UTC{'+' if tz_offset_hours >= 0 else ''}{tz_offset_hours}",
        ayanamsa=ayanamsa
    )

    # Build meta information
    meta = {
        "birth_datetime": birth_datetime.isoformat(),
        "latitude": latitude,
        "longitude": longitude,
        "timezone_offset": tz_offset_hours,
        "ayanamsa": ayanamsa,
        "ayanamsa_delta": round(base_chart.ayanamsa_delta, 6),
        "julian_day": base_chart.julian_day,
        "generated_at": datetime.datetime.now().isoformat()
    }

    # Step 2: Generate data for all 16 Vargas
    vargas_data = {}

    for varga_code in VARGA_CODES:
        varga_data = _generate_varga_chart(base_chart, varga_code)
        vargas_data[varga_code] = varga_data

    return {
        "meta": meta,
        "vargas": vargas_data
    }


def _generate_varga_chart(base_chart: ChartData, varga_code: str) -> Dict[str, Any]:
    """
    Generate complete chart data for a specific Varga.

    Uses base D1 chart absolute longitudes and recalculates:
    - Sign positions for this varga
    - House assignments based on varga ascendant
    - Dignities, aspects, conjunctions for this varga

    Args:
        base_chart: The calculated D1 ChartData
        varga_code: Varga code (D1, D2, ..., D60)

    Returns:
        Dict with ascendant, planets, and houses data
    """
    # Get ascendant for this varga
    asc_longitude = base_chart.houses[0].abs_longitude if base_chart.houses else 0
    asc_sign, asc_degrees = get_varga_sign_and_degrees(asc_longitude, varga_code)
    asc_sign_id = SIGNS.index(asc_sign) + 1 if asc_sign in SIGNS else 1

    # Build house signs for this varga (12 houses starting from ascendant sign)
    varga_house_signs: Dict[int, str] = {}
    for house_num in range(1, 13):
        # Each house is one sign forward from ascendant
        house_sign_idx = (asc_sign_id - 1 + house_num - 1) % 12
        varga_house_signs[house_num] = SIGNS[house_sign_idx]

    # Process planets for this varga
    planets_data = []
    planet_in_varga_sign: Dict[str, str] = {}  # For conjunctions
    planet_in_varga_house: Dict[str, int] = {}  # For aspects

    for planet in base_chart.planets:
        # Get varga sign and degrees
        varga_sign, varga_degrees = get_varga_sign_and_degrees(
            planet.abs_longitude, varga_code
        )
        varga_sign_id = SIGNS.index(varga_sign) + 1 if varga_sign in SIGNS else 1

        # Calculate house occupied in this varga
        # House = (planet_sign_id - ascendant_sign_id) % 12 + 1
        house_occupied = ((varga_sign_id - asc_sign_id) % 12) + 1

        # Calculate houses owned in this varga
        houses_owned = get_houses_owned(planet.name, varga_house_signs)

        # Get dignity for this varga position
        dignity = get_planet_dignity(planet.name, varga_sign, varga_degrees)

        # Get sign lord
        sign_lord = SIGN_LORDS.get(varga_sign, '')

        # Calculate aspects giving (based on house occupied in this varga)
        aspects_giving = get_aspects_giving(planet.name, house_occupied)

        # Store for conjunction/aspect calculations
        planet_in_varga_sign[planet.name] = varga_sign
        planet_in_varga_house[planet.name] = house_occupied

        planet_data = {
            "name": planet.name,
            "sign_id": varga_sign_id,
            "sign_name": varga_sign,
            "absolute_degree": round(planet.abs_longitude, 4),
            "relative_degree": round(varga_degrees, 2),
            "house_occupied": house_occupied,
            "houses_owned": houses_owned,
            "nakshatra": planet.nakshatra,
            "nakshatra_lord": planet.nakshatra_lord,
            "nakshatra_pada": planet.nakshatra_pada,
            "sign_lord": sign_lord,
            "dignity_state": dignity,
            "aspects_giving_to": aspects_giving,
            "aspects_receiving_from": [],  # Will be filled after all planets processed
            "conjunctions": [],  # Will be filled after all planets processed
            "is_retrograde": False  # TODO: Add retrograde detection
        }
        planets_data.append(planet_data)

    # Second pass: Calculate conjunctions and aspects received
    for planet_data in planets_data:
        planet_name = planet_data["name"]
        planet_sign = planet_in_varga_sign[planet_name]
        planet_house = planet_in_varga_house[planet_name]

        # Conjunctions - planets in the same sign in this varga
        planet_data["conjunctions"] = [
            p_name for p_name, p_sign in planet_in_varga_sign.items()
            if p_sign == planet_sign and p_name != planet_name
        ]

        # Aspects receiving - which planets aspect this planet's house
        for other_name, other_house in planet_in_varga_house.items():
            if other_name != planet_name:
                other_aspects = get_aspects_giving(other_name, other_house)
                if planet_house in other_aspects:
                    planet_data["aspects_receiving_from"].append(other_name)

    # Build houses data for this varga
    houses_data = []
    for house_num in range(1, 13):
        house_sign = varga_house_signs[house_num]
        house_sign_id = SIGNS.index(house_sign) + 1 if house_sign in SIGNS else 1
        house_lord = SIGN_LORDS.get(house_sign, '')

        # Get occupants (planets in this house in this varga)
        occupants = [
            p_name for p_name, p_house in planet_in_varga_house.items()
            if p_house == house_num
        ]

        # Get aspects received (planets aspecting this house)
        aspects_received = []
        for p_name, p_house in planet_in_varga_house.items():
            planet_aspects = get_aspects_giving(p_name, p_house)
            if house_num in planet_aspects:
                aspects_received.append(p_name)

        house_data = {
            "house_number": house_num,
            "sign_id": house_sign_id,
            "sign_name": house_sign,
            "lord": house_lord,
            "occupants": occupants,
            "aspects_received": aspects_received
        }
        houses_data.append(house_data)

    return {
        "ascendant": {
            "sign_id": asc_sign_id,
            "sign_name": asc_sign,
            "degrees": round(asc_degrees, 2)
        },
        "planets": planets_data,
        "houses": houses_data
    }


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AstroCore V2 - Clean Slate Test")
    print("=" * 70)

    # Test with Vadim's birth data
    import datetime

    core = AstroCore()
    chart = core.calculate(
        birth_datetime=datetime.datetime(1977, 10, 25, 6, 28),
        latitude=61.7,
        longitude=30.7,
        tz_offset_hours=3.0,
        timezone_name='Europe/Moscow',
        ayanamsa='Raman'
    )

    print(f"\nJulian Day: {chart.julian_day}")
    print(f"Ayanamsa Delta: {chart.ayanamsa_delta:.6f}°")
    print(f"Ascendant: {chart.ascendant_sign} {chart.ascendant_degrees:.2f}°")

    print("\n--- PLANETS ---")
    for planet in chart.planets:
        print(f"{planet.name}: {planet.sign} {planet.sign_degrees:.2f}° "
              f"(abs: {planet.abs_longitude:.2f}°) | "
              f"D9: {planet.varga_signs.get('D9', '?')}")

    print("\n--- D2 HORA ---")
    for planet in chart.planets:
        print(f"{planet.name}: {planet.varga_signs.get('D2', '?')}")

    print("\n--- D60 SHASHTIAMSHA ---")
    for planet in chart.planets:
        print(f"{planet.name}: {planet.varga_signs.get('D60', '?')}")
