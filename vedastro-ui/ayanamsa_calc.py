"""
ayanamsa_calc.py - Backward Compatibility Layer
================================================

This file provides backward compatibility for the UI.
All actual calculations are now in utils/astro_core_v2.py

The UI imports from this file, and we re-export from the new core.
"""

# Re-export everything from the new core
from utils.astro_core_v2 import (
    # Constants
    SIGNS,
    NAKSHATRAS,
    AYANAMSA_IDS,
    VARGA_CODES,

    # Core functions
    datetime_to_jd,
    get_ayanamsa_delta,
    convert_planet_position,
    calculate_navamsha_sign,
    get_varga_sign,
    calculate_all_vargas,
    normalize_longitude,
    longitude_to_sign_degrees,
    longitude_to_nakshatra,

    # Classes
    AstroCore,
    ChartData,
    PlanetPosition,
    HousePosition,

    # Convenience
    calculate_chart,
)

# Legacy alias
calculate_varga_sign = get_varga_sign
datetime_to_jd_compat = datetime_to_jd


def convert_chart_to_ayanamsa(planets_data, houses_data, birth_datetime, timezone_offset, target_ayanamsa='Raman'):
    """
    Legacy compatibility function.

    Note: This function is deprecated. Use AstroCore.calculate() instead.
    """
    # This is a stub - the UI should use the new architecture
    raise NotImplementedError(
        "convert_chart_to_ayanamsa is deprecated. "
        "Use AstroCore().calculate() instead."
    )
