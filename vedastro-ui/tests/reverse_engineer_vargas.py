"""
Reverse Engineer D2, D30, D60 from VedAstro Ground Truth
Profile: Vadim (1977-10-25, 06:28, Sortavala)

Ground Truth from VedAstro:
D2: Saturn H1, Sun+Jupiter H3, Ketu H4, Venus H6, Mercury H7, Rahu H10, Moon+Mars H12
D30: Sun+Saturn+Rahu+Ketu H1, Mars H6, Moon+Mercury+Jupiter+Venus H12
D60: Venus+Saturn H1, Mars H2, Jupiter H3, Ketu H4, Mercury H6, Moon H8, Sun+Rahu H10

Goal: Find D1 longitudes and formulas that match this output
"""

import sys
sys.path.insert(0, '/Users/vadimarhipov/StarMeet-platform/vedastro-ui')

from datetime import datetime
from zoneinfo import ZoneInfo
from ayanamsa_calc import (
    datetime_to_jd, get_ayanamsa_delta, get_mean_node_position, get_ketu_from_rahu,
    convert_planet_position, SIGNS
)
from jyotishganit import calculate_birth_chart

# Test data for Vadim
BIRTH_DATE = datetime(1977, 10, 25, 6, 28)
LATITUDE = 61.70274
LONGITUDE = 30.691231
TIMEZONE = "Europe/Moscow"

# Ground truth
D2_GT = {1: ['Saturn'], 3: ['Sun', 'Jupiter'], 4: ['Ketu'], 6: ['Venus'], 7: ['Mercury'], 10: ['Rahu'], 12: ['Moon', 'Mars']}
D30_GT = {1: ['Sun', 'Saturn', 'Rahu', 'Ketu'], 6: ['Mars'], 12: ['Moon', 'Mercury', 'Jupiter', 'Venus']}
D60_GT = {1: ['Venus', 'Saturn'], 2: ['Mars'], 3: ['Jupiter'], 4: ['Ketu'], 6: ['Mercury'], 8: ['Moon'], 10: ['Sun', 'Rahu']}


def get_d1_positions():
    """Get D1 positions with Raman correction"""
    tz = ZoneInfo(TIMEZONE)
    local_dt_aware = BIRTH_DATE.replace(tzinfo=tz)
    offset = local_dt_aware.utcoffset().total_seconds() / 3600.0

    jd = datetime_to_jd(BIRTH_DATE, offset)
    ayanamsa_delta = get_ayanamsa_delta(jd, 'True_Chitrapaksha', 'Raman')

    # Calculate chart with jyotishganit
    chart = calculate_birth_chart(
        birth_date=BIRTH_DATE,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        timezone_offset=offset
    )

    # Get Mean Nodes for Raman
    mean_rahu_pos = get_mean_node_position(jd, 'Raman')
    mean_ketu_pos = get_ketu_from_rahu(mean_rahu_pos)

    planet_longitudes = {}

    if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'planets'):
        for p in chart.d1_chart.planets:
            planet_name = str(p.celestial_body).upper()
            orig_sign = str(p.sign)
            orig_deg = p.sign_degrees

            # Handle Rahu/Ketu with Mean Nodes
            if 'RAHU' in planet_name:
                longitude = mean_rahu_pos['longitude']
                planet_key = 'Rahu'
            elif 'KETU' in planet_name:
                longitude = mean_ketu_pos['longitude']
                planet_key = 'Ketu'
            else:
                new_pos = convert_planet_position(orig_sign, orig_deg, ayanamsa_delta)
                longitude = new_pos['longitude']

                for pname in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
                    if pname.upper() in planet_name:
                        planet_key = pname
                        break
                else:
                    continue

            planet_longitudes[planet_key] = longitude

    # Get Ascendant
    if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'houses') and chart.d1_chart.houses:
        asc_sign = str(chart.d1_chart.houses[0].sign)
        asc_deg = getattr(chart.d1_chart.houses[0], 'sign_degrees', 0)
        asc_pos = convert_planet_position(asc_sign, asc_deg, ayanamsa_delta)
        planet_longitudes['Ascendant'] = asc_pos['longitude']

    return planet_longitudes


def calc_d60_vedastro_formula(longitude: float) -> str:
    """
    D60 formula from web research:
    1. Take degrees in sign
    2. Multiply by 2
    3. Divide by 12
    4. Remainder + 1 = sign number (1-indexed)
    """
    degrees_in_sign = longitude % 30

    # Formula: (degrees * 2) / 12, take remainder, add 1
    result = int(degrees_in_sign * 2)
    sign_num = (result % 12) + 1  # 1-indexed

    return SIGNS[sign_num - 1]  # Convert to 0-indexed for array


def calc_d60_method_standard(longitude: float) -> str:
    """D60 standard: start from same sign"""
    sign_idx = int(longitude / 30)
    degrees_in_sign = longitude % 30
    part = int(degrees_in_sign // 0.5)
    if part > 59:
        part = 59
    d60_idx = (sign_idx + part) % 12
    return SIGNS[d60_idx]


def calc_d60_method_absolute(longitude: float) -> str:
    """D60 absolute: use full longitude"""
    part = int(longitude // 0.5)  # 720 total parts
    d60_idx = part % 12
    return SIGNS[d60_idx]


def calc_d30_parasara(longitude: float) -> str:
    """D30 Parasara method with unequal divisions"""
    sign_idx = int(longitude / 30)
    degrees_in_sign = longitude % 30
    is_odd = (sign_idx % 2 == 0)

    if is_odd:
        if degrees_in_sign < 5:
            return 'Aries'
        elif degrees_in_sign < 10:
            return 'Aquarius'
        elif degrees_in_sign < 18:
            return 'Sagittarius'
        elif degrees_in_sign < 25:
            return 'Gemini'
        else:
            return 'Libra'
    else:
        if degrees_in_sign < 5:
            return 'Taurus'
        elif degrees_in_sign < 12:
            return 'Virgo'
        elif degrees_in_sign < 20:
            return 'Pisces'
        elif degrees_in_sign < 25:
            return 'Capricorn'
        else:
            return 'Scorpio'


def calc_d2_parasara(longitude: float) -> str:
    """D2 Parasara method - only Cancer and Leo"""
    sign_idx = int(longitude / 30)
    degrees_in_sign = longitude % 30
    is_odd_sign = (sign_idx % 2 == 0)
    first_half = (degrees_in_sign < 15)

    if is_odd_sign:
        return 'Leo' if first_half else 'Cancer'
    else:
        return 'Cancer' if first_half else 'Leo'


def get_house_from_sign(planet_sign: str, asc_sign: str) -> int:
    """Calculate house number given planet sign and ascendant sign"""
    planet_idx = SIGNS.index(planet_sign)
    asc_idx = SIGNS.index(asc_sign)
    house = ((planet_idx - asc_idx) % 12) + 1
    return house


def analyze_d2():
    """Analyze D2 ground truth"""
    print("\n" + "=" * 70)
    print("D2 (HORA) ANALYSIS")
    print("=" * 70)

    positions = get_d1_positions()

    # In D2, only Cancer and Leo exist
    # Ground truth: Saturn H1, Sun+Jupiter H3, etc.
    # This means D2 Ascendant determines house positions

    print("\nD1 Positions (Raman-corrected):")
    for planet, long in sorted(positions.items(), key=lambda x: x[1]):
        sign_idx = int(long / 30)
        deg = long % 30
        d2_sign = calc_d2_parasara(long)
        print(f"  {planet}: {SIGNS[sign_idx]} {deg:.2f}° -> D2={d2_sign}")

    # Calculate D2 Ascendant
    asc_long = positions.get('Ascendant', 0)
    d2_asc = calc_d2_parasara(asc_long)
    print(f"\nD2 Ascendant: {d2_asc}")

    # Map to houses
    print("\nD2 House Distribution (calculated):")
    d2_houses = {}
    for planet, long in positions.items():
        if planet == 'Ascendant':
            continue
        d2_sign = calc_d2_parasara(long)
        house = get_house_from_sign(d2_sign, d2_asc)
        if house not in d2_houses:
            d2_houses[house] = []
        d2_houses[house].append(planet)

    for h in sorted(d2_houses.keys()):
        print(f"  House {h}: {', '.join(d2_houses[h])}")

    print("\nD2 Ground Truth:")
    for h in sorted(D2_GT.keys()):
        print(f"  House {h}: {', '.join(D2_GT[h])}")

    # Try to find the correct D2 Ascendant from ground truth
    print("\n--- Reverse Engineering D2 Ascendant ---")
    # Saturn is in H1. If D2 Asc = Leo, Saturn's D2 should be Leo
    saturn_long = positions.get('Saturn', 0)
    saturn_d2 = calc_d2_parasara(saturn_long)
    print(f"Saturn D2 = {saturn_d2}")
    print(f"If Saturn is in H1, D2 Asc should be {saturn_d2}")

    # Moon+Mars in H12 means they are 1 sign before Asc
    moon_long = positions.get('Moon', 0)
    moon_d2 = calc_d2_parasara(moon_long)
    print(f"Moon D2 = {moon_d2}")

    # If D2 Asc = Leo (index 4), H12 = Cancer (index 3)
    # So Moon+Mars should be in Cancer
    print(f"\nIf D2 Asc = Leo:")
    print(f"  H1 = Leo, H12 = Cancer")
    print(f"  Saturn D2 = {saturn_d2} (should be Leo for H1)")
    print(f"  Moon D2 = {moon_d2} (should be Cancer for H12)")


def analyze_d60():
    """Analyze D60 ground truth"""
    print("\n" + "=" * 70)
    print("D60 (SHASHTYAMSHA) ANALYSIS")
    print("=" * 70)

    positions = get_d1_positions()

    print("\nD1 Positions and D60 calculations:")
    print(f"{'Planet':<10} {'D1 Long':>10} {'Deg in Sign':>12} {'D60 Std':<12} {'D60 VedA':<12} {'D60 Abs':<12}")
    print("-" * 70)

    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        if planet not in positions:
            continue
        long = positions[planet]
        deg_in_sign = long % 30

        d60_std = calc_d60_method_standard(long)
        d60_veda = calc_d60_vedastro_formula(long)
        d60_abs = calc_d60_method_absolute(long)

        print(f"{planet:<10} {long:>10.4f} {deg_in_sign:>12.4f} {d60_std:<12} {d60_veda:<12} {d60_abs:<12}")

    # Calculate D60 Ascendant
    asc_long = positions.get('Ascendant', 0)
    d60_asc_std = calc_d60_method_standard(asc_long)
    d60_asc_veda = calc_d60_vedastro_formula(asc_long)

    print(f"\nD60 Ascendant (Standard): {d60_asc_std}")
    print(f"D60 Ascendant (VedAstro formula): {d60_asc_veda}")

    print("\n--- Testing different D60 Ascendants ---")
    # Ground truth: Venus+Saturn H1
    # This means Venus and Saturn should be in the same sign as D60 Asc
    venus_long = positions.get('Venus', 0)
    saturn_long = positions.get('Saturn', 0)

    for method_name, method_func in [('Standard', calc_d60_method_standard),
                                      ('VedAstro', calc_d60_vedastro_formula),
                                      ('Absolute', calc_d60_method_absolute)]:
        venus_d60 = method_func(venus_long)
        saturn_d60 = method_func(saturn_long)
        asc_d60 = method_func(asc_long)

        print(f"\n{method_name} Method:")
        print(f"  Venus D60: {venus_d60}")
        print(f"  Saturn D60: {saturn_d60}")
        print(f"  Asc D60: {asc_d60}")

        if venus_d60 == saturn_d60:
            print(f"  Venus & Saturn in same sign! D60 Asc could be: {venus_d60}")


def analyze_d30():
    """Analyze D30 ground truth"""
    print("\n" + "=" * 70)
    print("D30 (TRIMSHAMSHA) ANALYSIS")
    print("=" * 70)

    positions = get_d1_positions()

    print("\nD1 Positions and D30 Parasara calculations:")
    print(f"{'Planet':<10} {'D1 Long':>10} {'D1 Sign':<12} {'Deg in Sign':>12} {'D30 Sign':<12}")
    print("-" * 70)

    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        if planet not in positions:
            continue
        long = positions[planet]
        sign_idx = int(long / 30)
        deg_in_sign = long % 30
        d30_sign = calc_d30_parasara(long)

        print(f"{planet:<10} {long:>10.4f} {SIGNS[sign_idx]:<12} {deg_in_sign:>12.4f} {d30_sign:<12}")

    # Calculate D30 Ascendant
    asc_long = positions.get('Ascendant', 0)
    d30_asc = calc_d30_parasara(asc_long)
    print(f"\nD30 Ascendant: {d30_asc}")

    # Map to houses
    print("\nD30 House Distribution (calculated):")
    d30_houses = {}
    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        if planet not in positions:
            continue
        long = positions[planet]
        d30_sign = calc_d30_parasara(long)
        house = get_house_from_sign(d30_sign, d30_asc)
        if house not in d30_houses:
            d30_houses[house] = []
        d30_houses[house].append(planet)

    for h in sorted(d30_houses.keys()):
        print(f"  House {h}: {', '.join(d30_houses[h])}")

    print("\nD30 Ground Truth:")
    for h in sorted(D30_GT.keys()):
        print(f"  House {h}: {', '.join(D30_GT[h])}")


if __name__ == "__main__":
    print("=" * 70)
    print("REVERSE ENGINEERING VARGA FORMULAS FROM VEDASTRO GROUND TRUTH")
    print("=" * 70)
    print(f"Profile: Vadim ({BIRTH_DATE.strftime('%Y-%m-%d %H:%M')})")
    print(f"Location: Sortavala ({LATITUDE}, {LONGITUDE})")

    try:
        analyze_d2()
        analyze_d30()
        analyze_d60()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
