"""
D9 (Navamsha) Verification Test Script
Test Case: Profile Vadim
Input: 1977-10-25, 06:28, Sortavala (61.70274, 30.691231)
Expected D9: Sun and Moon in Sagittarius
"""
import datetime
from zoneinfo import ZoneInfo
from jyotishganit import calculate_birth_chart

# Test data for Vadim
BIRTH_DATE = datetime.datetime(1977, 10, 25, 6, 28)
LATITUDE = 61.70274
LONGITUDE = 30.691231
TIMEZONE = "Europe/Moscow"

def calculate_navamsha_sign(rasi_sign: str, degrees: float) -> str:
    """
    Calculate Navamsha (D9) sign from Rasi position.

    Navamsha divides each sign into 9 parts (3°20' each = 3.333°)
    The starting sign depends on the element of the Rasi:
    - Fire signs (Aries, Leo, Sagittarius): Start from Aries
    - Earth signs (Taurus, Virgo, Capricorn): Start from Capricorn
    - Air signs (Gemini, Libra, Aquarius): Start from Libra
    - Water signs (Cancer, Scorpio, Pisces): Start from Cancer
    """
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    # Normalize sign name
    rasi = None
    for s in signs:
        if s.lower() in str(rasi_sign).lower():
            rasi = s
            break

    if not rasi:
        return f"Unknown ({rasi_sign})"

    rasi_idx = signs.index(rasi)

    # Determine starting sign based on element
    fire_signs = [0, 4, 8]  # Aries, Leo, Sagittarius
    earth_signs = [1, 5, 9]  # Taurus, Virgo, Capricorn
    air_signs = [2, 6, 10]  # Gemini, Libra, Aquarius
    water_signs = [3, 7, 11]  # Cancer, Scorpio, Pisces

    if rasi_idx in fire_signs:
        start_sign = 0  # Aries
    elif rasi_idx in earth_signs:
        start_sign = 9  # Capricorn
    elif rasi_idx in air_signs:
        start_sign = 6  # Libra
    else:  # Water
        start_sign = 3  # Cancer

    # Calculate which navamsha pada (0-8)
    navamsha_pada = int(degrees / 3.333333)
    if navamsha_pada > 8:
        navamsha_pada = 8

    # Calculate final navamsha sign
    navamsha_idx = (start_sign + navamsha_pada) % 12

    return signs[navamsha_idx]


def run_verification():
    """Run D9 verification for Vadim's chart"""
    print("=" * 60)
    print("D9 (NAVAMSHA) VERIFICATION TEST")
    print("=" * 60)
    print(f"\nTest Subject: Vadim")
    print(f"Birth: {BIRTH_DATE.strftime('%Y-%m-%d %H:%M')}")
    print(f"Location: Sortavala ({LATITUDE}, {LONGITUDE})")
    print(f"Timezone: {TIMEZONE}")
    print("-" * 60)

    # Calculate timezone offset
    tz = ZoneInfo(TIMEZONE)
    local_dt_aware = BIRTH_DATE.replace(tzinfo=tz)
    offset = local_dt_aware.utcoffset().total_seconds() / 3600.0
    print(f"Timezone offset: +{offset}h")

    # Calculate chart
    print("\nCalculating birth chart with jyotishganit...")
    chart = calculate_birth_chart(
        birth_date=BIRTH_DATE,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        timezone_offset=offset
    )

    # Extract D1 data
    print("\n" + "=" * 60)
    print("D1 (RASI) CHART:")
    print("=" * 60)

    sun_d1 = None
    moon_d1 = None

    if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'planets'):
        for p in chart.d1_chart.planets:
            planet_name = str(p.celestial_body).upper()
            sign = str(p.sign)
            degrees = p.sign_degrees

            print(f"{planet_name:12} | {sign:12} | {degrees:6.2f}°")

            if 'SUN' in planet_name:
                sun_d1 = {'sign': sign, 'degrees': degrees}
            if 'MOON' in planet_name:
                moon_d1 = {'sign': sign, 'degrees': degrees}

    # Calculate D9 manually
    print("\n" + "=" * 60)
    print("D9 (NAVAMSHA) CALCULATION:")
    print("=" * 60)

    results = {}

    if sun_d1:
        sun_d9 = calculate_navamsha_sign(sun_d1['sign'], sun_d1['degrees'])
        print(f"SUN:  D1={sun_d1['sign']} {sun_d1['degrees']:.2f}° -> D9={sun_d9}")
        results['sun_d9'] = sun_d9

    if moon_d1:
        moon_d9 = calculate_navamsha_sign(moon_d1['sign'], moon_d1['degrees'])
        print(f"MOON: D1={moon_d1['sign']} {moon_d1['degrees']:.2f}° -> D9={moon_d9}")
        results['moon_d9'] = moon_d9

    # Check library's D9 if available
    print("\n" + "-" * 60)
    print("Library D9 output (if available):")

    if hasattr(chart, 'divisional_charts'):
        print(f"Available divisional charts: {list(chart.divisional_charts.keys())}")
        if 'd9' in chart.divisional_charts:
            d9 = chart.divisional_charts['d9']
            if hasattr(d9, 'planets'):
                for p in d9.planets:
                    print(f"  {p.celestial_body}: {p.sign}")
            elif hasattr(d9, 'houses'):
                for h in d9.houses:
                    if hasattr(h, 'occupants'):
                        for occ in h.occupants:
                            print(f"  {occ.celestial_body}: {occ.sign}")
    else:
        print("  No divisional_charts attribute found")

    # Verification result
    print("\n" + "=" * 60)
    print("VERIFICATION RESULT:")
    print("=" * 60)

    expected_sun = "Sagittarius"
    expected_moon = "Sagittarius"

    sun_status = "PASS" if results.get('sun_d9') == expected_sun else "FAIL"
    moon_status = "PASS" if results.get('moon_d9') == expected_moon else "FAIL"

    print(f"Expected Sun D9:  {expected_sun}")
    print(f"Actual Sun D9:    {results.get('sun_d9', 'N/A')} [{sun_status}]")
    print()
    print(f"Expected Moon D9: {expected_moon}")
    print(f"Actual Moon D9:   {results.get('moon_d9', 'N/A')} [{moon_status}]")
    print()

    overall = "PASSED" if sun_status == "PASS" and moon_status == "PASS" else "FAILED"
    print(f"Overall Status: {overall}")

    return results


if __name__ == "__main__":
    run_verification()
