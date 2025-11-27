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


@dataclass
class HousePosition:
    """Clean representation of a house cusp."""
    house_number: int            # 1-12
    abs_longitude: float         # CORRECTED absolute longitude (0-360)
    sign: str                    # Sign name
    sign_degrees: float          # Degrees within sign (0-30)


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

        # Step 3: Process planets - apply delta and calculate vargas
        planets = []

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

                # Create planet position object
                planet = PlanetPosition(
                    name=str(p.celestial_body),
                    abs_longitude=corrected_longitude,
                    sign=corrected_sign,
                    sign_degrees=corrected_degrees,
                    nakshatra=nakshatra,
                    nakshatra_pada=pada,
                    house=p.house,
                    varga_signs=varga_signs
                )
                planets.append(planet)

        # Step 4: Process houses - apply delta
        houses = []
        ascendant_sign = "Aries"
        ascendant_degrees = 0.0

        if hasattr(raw_chart, 'd1_chart') and hasattr(raw_chart.d1_chart, 'houses'):
            for i, h in enumerate(raw_chart.d1_chart.houses):
                raw_sign = str(h.sign)
                raw_degrees = float(getattr(h, 'sign_degrees', 0))

                # Calculate RAW absolute longitude
                raw_sign_idx = SIGNS.index(raw_sign) if raw_sign in SIGNS else 0
                raw_abs_longitude = raw_sign_idx * 30 + raw_degrees

                # Apply Raman delta
                corrected_longitude = normalize_longitude(raw_abs_longitude + ayanamsa_delta)

                # Convert back to sign + degrees
                corrected_sign, corrected_degrees = longitude_to_sign_degrees(corrected_longitude)

                house = HousePosition(
                    house_number=i + 1,
                    abs_longitude=corrected_longitude,
                    sign=corrected_sign,
                    sign_degrees=corrected_degrees
                )
                houses.append(house)

                # Store ascendant info (House 1)
                if i == 0:
                    ascendant_sign = corrected_sign
                    ascendant_degrees = corrected_degrees

        # Step 5: Create and return ChartData
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
