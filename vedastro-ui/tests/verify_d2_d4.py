"""
D2 (Hora) and D4 (Chaturthamsha) Verification Test Script
Test Case: Profile Vadim
Input: 1977-10-25, 06:28, Sortavala (61.70274, 30.691231)

GROUND TRUTH from User's trusted software:
D2: House 1=Saturn, House 3=Sun+Jupiter, House 4=Ketu, House 6=Venus,
    House 7=Mercury, House 10=Rahu, House 12=Moon+Mars
D4: House 2=Mars, House 3=Saturn, House 4=Moon+Jupiter+Ketu,
    House 8=Sun+Mercury, House 10=Venus+Rahu
"""
import datetime
from zoneinfo import ZoneInfo
import sys
sys.path.insert(0, '/Users/vadimarhipov/StarMeet-platform/vedastro-ui')

from ayanamsa_calc import (
    datetime_to_jd, get_ayanamsa_delta, get_mean_node_position, get_ketu_from_rahu,
    convert_planet_position, calculate_varga_sign, SIGNS
)
from jyotishganit import calculate_birth_chart

# Test data for Vadim
BIRTH_DATE = datetime.datetime(1977, 10, 25, 6, 28)
LATITUDE = 61.70274
LONGITUDE = 30.691231
TIMEZONE = "Europe/Moscow"

# Ground truth from User
GROUND_TRUTH_D2 = {
    1: ['Сатурн'],
    3: ['Солнце', 'Юпитер'],
    4: ['Кету'],
    6: ['Венера'],
    7: ['Меркурий'],
    10: ['Раху'],
    12: ['Луна', 'Марс']
}

GROUND_TRUTH_D4 = {
    2: ['Марс'],
    3: ['Сатурн'],
    4: ['Луна', 'Юпитер', 'Кету'],
    8: ['Солнце', 'Меркурий'],
    10: ['Венера', 'Раху']
}

# Planet name mappings
EN_TO_RU = {
    'Sun': 'Солнце', 'Moon': 'Луна', 'Mars': 'Марс',
    'Mercury': 'Меркурий', 'Jupiter': 'Юпитер', 'Venus': 'Венера',
    'Saturn': 'Сатурн', 'Rahu': 'Раху', 'Ketu': 'Кету'
}


def run_verification():
    """Run D2 and D4 verification for Vadim's chart"""
    print("=" * 70)
    print("D2 (HORA) & D4 (CHATURTHAMSHA) VERIFICATION TEST")
    print("=" * 70)
    print(f"\nTest Subject: Vadim")
    print(f"Birth: {BIRTH_DATE.strftime('%Y-%m-%d %H:%M')}")
    print(f"Location: Sortavala ({LATITUDE}, {LONGITUDE})")
    print(f"Timezone: {TIMEZONE}")
    print("-" * 70)

    # Calculate timezone offset
    tz = ZoneInfo(TIMEZONE)
    local_dt_aware = BIRTH_DATE.replace(tzinfo=tz)
    offset = local_dt_aware.utcoffset().total_seconds() / 3600.0
    print(f"Timezone offset: +{offset}h")

    # Calculate Julian Day
    jd = datetime_to_jd(BIRTH_DATE, offset)
    print(f"Julian Day: {jd}")

    # Calculate ayanamsa delta (True Chitrapaksha -> Raman)
    ayanamsa_delta = get_ayanamsa_delta(jd, 'True_Chitrapaksha', 'Raman')
    print(f"Ayanamsa Delta (Chitrapaksha->Raman): {ayanamsa_delta:.4f}°")

    # Calculate chart with jyotishganit
    print("\nCalculating birth chart with jyotishganit...")
    chart = calculate_birth_chart(
        birth_date=BIRTH_DATE,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        timezone_offset=offset
    )

    # Get Mean Nodes for Raman (instead of True Nodes)
    mean_rahu_pos = get_mean_node_position(jd, 'Raman')
    mean_ketu_pos = get_ketu_from_rahu(mean_rahu_pos)

    # Extract D1 positions and apply Raman correction
    planet_longitudes = {}
    print("\n" + "=" * 70)
    print("D1 POSITIONS (Raman-Corrected Longitudes):")
    print("=" * 70)
    print(f"{'Planet':<12} | {'Original':<20} | {'Corrected Long':<15}")
    print("-" * 55)

    if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'planets'):
        for p in chart.d1_chart.planets:
            planet_name = str(p.celestial_body)
            planet_name_upper = planet_name.upper()
            orig_sign = str(p.sign)
            orig_deg = p.sign_degrees

            # Handle Rahu/Ketu with Mean Nodes
            if 'RAHU' in planet_name_upper:
                longitude = mean_rahu_pos['longitude']
                planet_key = 'Rahu'
            elif 'KETU' in planet_name_upper:
                longitude = mean_ketu_pos['longitude']
                planet_key = 'Ketu'
            else:
                # Apply ayanamsa delta for regular planets
                new_pos = convert_planet_position(orig_sign, orig_deg, ayanamsa_delta)
                longitude = new_pos['longitude']
                # Normalize planet name
                for pname in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
                    if pname.upper() in planet_name_upper:
                        planet_key = pname
                        break
                else:
                    planet_key = planet_name

            planet_longitudes[planet_key] = longitude
            print(f"{planet_key:<12} | {orig_sign:<10} {orig_deg:>6.2f}° | {longitude:>10.2f}°")

    # Get Ascendant longitude (also corrected)
    asc_longitude = None
    if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'houses') and chart.d1_chart.houses:
        asc_sign = str(chart.d1_chart.houses[0].sign)
        asc_deg = getattr(chart.d1_chart.houses[0], 'sign_degrees', 0)
        asc_pos = convert_planet_position(asc_sign, asc_deg, ayanamsa_delta)
        asc_longitude = asc_pos['longitude']
        print(f"{'Ascendant':<12} | {asc_sign:<10} {asc_deg:>6.2f}° | {asc_longitude:>10.2f}°")

    # =========================================================================
    # D2 (HORA) CALCULATION
    # =========================================================================
    print("\n" + "=" * 70)
    print("D2 (HORA) CALCULATION:")
    print("=" * 70)

    d2_ascendant = calculate_varga_sign(asc_longitude, 'D2') if asc_longitude else None
    print(f"D2 Ascendant: {d2_ascendant}")

    # Calculate D2 signs for all planets
    d2_planet_signs = {}
    for planet, longitude in planet_longitudes.items():
        d2_sign = calculate_varga_sign(longitude, 'D2')
        d2_planet_signs[planet] = d2_sign
        print(f"  {planet}: {d2_sign} (from long={longitude:.2f}°)")

    # Map to houses based on D2 Ascendant
    d2_houses = {}
    if d2_ascendant in SIGNS:
        asc_idx = SIGNS.index(d2_ascendant)
        for house_num in range(1, 13):
            house_sign_idx = (asc_idx + house_num - 1) % 12
            house_sign = SIGNS[house_sign_idx]
            planets_in = [EN_TO_RU.get(p, p) for p, s in d2_planet_signs.items() if s == house_sign]
            if planets_in:
                d2_houses[house_num] = planets_in

    print("\nD2 House Distribution (Calculated):")
    for h, planets in sorted(d2_houses.items()):
        print(f"  House {h}: {', '.join(planets)}")

    print("\nD2 Ground Truth:")
    for h, planets in sorted(GROUND_TRUTH_D2.items()):
        print(f"  House {h}: {', '.join(planets)}")

    # =========================================================================
    # D4 (CHATURTHAMSHA) CALCULATION
    # =========================================================================
    print("\n" + "=" * 70)
    print("D4 (CHATURTHAMSHA) CALCULATION:")
    print("=" * 70)

    d4_ascendant = calculate_varga_sign(asc_longitude, 'D4') if asc_longitude else None
    print(f"D4 Ascendant: {d4_ascendant}")

    # Calculate D4 signs for all planets
    d4_planet_signs = {}
    for planet, longitude in planet_longitudes.items():
        d4_sign = calculate_varga_sign(longitude, 'D4')
        d4_planet_signs[planet] = d4_sign
        deg_in_sign = longitude % 30
        part = "1st" if deg_in_sign < 7.5 else "2nd" if deg_in_sign < 15 else "3rd" if deg_in_sign < 22.5 else "4th"
        print(f"  {planet}: {d4_sign} (long={longitude:.2f}°, deg_in_sign={deg_in_sign:.2f}°, {part} quarter)")

    # Map to houses based on D4 Ascendant
    d4_houses = {}
    if d4_ascendant in SIGNS:
        asc_idx = SIGNS.index(d4_ascendant)
        for house_num in range(1, 13):
            house_sign_idx = (asc_idx + house_num - 1) % 12
            house_sign = SIGNS[house_sign_idx]
            planets_in = [EN_TO_RU.get(p, p) for p, s in d4_planet_signs.items() if s == house_sign]
            if planets_in:
                d4_houses[house_num] = planets_in

    print("\nD4 House Distribution (Calculated):")
    for h, planets in sorted(d4_houses.items()):
        print(f"  House {h}: {', '.join(planets)}")

    print("\nD4 Ground Truth:")
    for h, planets in sorted(GROUND_TRUTH_D4.items()):
        print(f"  House {h}: {', '.join(planets)}")

    # =========================================================================
    # VERIFICATION SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY:")
    print("=" * 70)

    # D2 verification
    d2_match = True
    d2_issues = []
    for h, gt_planets in GROUND_TRUTH_D2.items():
        calc_planets = d2_houses.get(h, [])
        gt_set = set(gt_planets)
        calc_set = set(calc_planets)
        if gt_set != calc_set:
            d2_match = False
            d2_issues.append(f"House {h}: Expected {gt_set}, Got {calc_set}")

    print(f"\nD2 (Hora): {'✅ MATCH' if d2_match else '❌ MISMATCH'}")
    for issue in d2_issues:
        print(f"  - {issue}")

    # D4 verification
    d4_match = True
    d4_issues = []
    for h, gt_planets in GROUND_TRUTH_D4.items():
        calc_planets = d4_houses.get(h, [])
        gt_set = set(gt_planets)
        calc_set = set(calc_planets)
        if gt_set != calc_set:
            d4_match = False
            d4_issues.append(f"House {h}: Expected {gt_set}, Got {calc_set}")

    print(f"\nD4 (Chaturthamsha): {'✅ MATCH' if d4_match else '❌ MISMATCH'}")
    for issue in d4_issues:
        print(f"  - {issue}")

    return d2_match, d4_match


if __name__ == "__main__":
    run_verification()
