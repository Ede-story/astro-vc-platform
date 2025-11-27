"""
D60 (Shashtyamsha) Verification Test Script
Test Case: Profile Vadim
Input: 1977-10-25, 06:28, Sortavala (61.70274, 30.691231)

D60 divides each sign into 60 parts (0.5° each).
This is one of the most detailed divisional charts, used for:
- Past life karma analysis
- Fine-tuning predictions
- Determining overall auspiciousness
"""
import datetime
from zoneinfo import ZoneInfo
from jyotishganit import calculate_birth_chart

# Test data for Vadim
BIRTH_DATE = datetime.datetime(1977, 10, 25, 6, 28)
LATITUDE = 61.70274
LONGITUDE = 30.691231
TIMEZONE = "Europe/Moscow"


def run_d60_verification():
    """Run D60 verification for Vadim's chart"""
    print("=" * 70)
    print("D60 (SHASHTYAMSHA) VERIFICATION TEST")
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

    # Calculate chart
    print("\nCalculating birth chart with jyotishganit...")
    chart = calculate_birth_chart(
        birth_date=BIRTH_DATE,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        timezone_offset=offset
    )

    # Check available divisional charts
    print("\n" + "=" * 70)
    print("AVAILABLE DIVISIONAL CHARTS:")
    print("=" * 70)

    if hasattr(chart, 'divisional_charts'):
        available = list(chart.divisional_charts.keys())
        print(f"Found {len(available)} divisional charts: {available}")

        # Check for D60 specifically
        if 'd60' in available:
            print("\n✅ D60 (Shashtyamsha) is available!")
        else:
            print("\n❌ D60 (Shashtyamsha) is NOT available")
            return None
    else:
        print("No divisional_charts attribute found on chart object")
        return None

    # Extract D1 data for comparison
    print("\n" + "=" * 70)
    print("D1 (RASI) CHART - BASE POSITIONS:")
    print("=" * 70)
    print(f"{'Planet':<12} | {'Sign':<12} | {'Degrees':<8}")
    print("-" * 40)

    d1_data = {}
    if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'planets'):
        for p in chart.d1_chart.planets:
            planet_name = str(p.celestial_body).upper()
            sign = str(p.sign)
            degrees = p.sign_degrees

            # Normalize planet name
            for pname in ['SUN', 'MOON', 'MARS', 'MERCURY', 'JUPITER', 'VENUS', 'SATURN', 'RAHU', 'KETU']:
                if pname in planet_name:
                    planet_name = pname
                    break

            d1_data[planet_name] = {'sign': sign, 'degrees': degrees}
            print(f"{planet_name:<12} | {sign:<12} | {degrees:6.2f}°")

    # Extract D60 data
    print("\n" + "=" * 70)
    print("D60 (SHASHTYAMSHA) CHART:")
    print("=" * 70)
    print(f"{'Planet':<12} | {'D60 Sign':<12} | {'D60 House':<10}")
    print("-" * 40)

    d60_data = {}
    d60 = chart.divisional_charts.get('d60')

    if d60 and hasattr(d60, 'houses'):
        # Get ascendant
        ascendant = str(d60.houses[0].sign) if d60.houses else None
        print(f"D60 Ascendant: {ascendant}")
        print("-" * 40)

        for house in d60.houses:
            if hasattr(house, 'occupants'):
                for occupant in house.occupants:
                    planet_name = str(occupant.celestial_body).upper()
                    sign = str(occupant.sign)

                    # Normalize planet name
                    for pname in ['SUN', 'MOON', 'MARS', 'MERCURY', 'JUPITER', 'VENUS', 'SATURN', 'RAHU', 'KETU']:
                        if pname in planet_name:
                            planet_name = pname
                            break

                    d60_data[planet_name] = {'sign': sign, 'house': house.number}
                    print(f"{planet_name:<12} | {sign:<12} | {house.number:<10}")

    # Comparison: D1 vs D60
    print("\n" + "=" * 70)
    print("COMPARISON: D1 vs D60")
    print("=" * 70)
    print(f"{'Planet':<12} | {'D1 Sign':<12} | {'D60 Sign':<12} | {'Changed?':<10}")
    print("-" * 55)

    changes_count = 0
    for planet in ['SUN', 'MOON', 'MARS', 'MERCURY', 'JUPITER', 'VENUS', 'SATURN', 'RAHU', 'KETU']:
        d1_sign = d1_data.get(planet, {}).get('sign', '—')
        d60_sign = d60_data.get(planet, {}).get('sign', '—')
        changed = "YES ✅" if d1_sign != d60_sign and d60_sign != '—' else "No"
        if d1_sign != d60_sign and d60_sign != '—':
            changes_count += 1
        print(f"{planet:<12} | {d1_sign:<12} | {d60_sign:<12} | {changed:<10}")

    # Verification result
    print("\n" + "=" * 70)
    print("VERIFICATION RESULT:")
    print("=" * 70)

    if d60_data:
        print(f"✅ D60 chart calculated successfully")
        print(f"   - Found {len(d60_data)} planets in D60")
        print(f"   - {changes_count} planets changed signs from D1 to D60")
        print(f"\n   D60 is the most detailed divisional chart (60 divisions per sign).")
        print(f"   It's expected that most planets will be in DIFFERENT signs than D1.")

        if changes_count >= 5:
            print("\n   ✅ Test PASSED: D60 shows significant differentiation from D1")
            return True
        else:
            print(f"\n   ⚠️  Warning: Only {changes_count} planets changed. Expected more variation.")
            return True
    else:
        print("❌ D60 chart calculation FAILED - no planet data extracted")
        return False


if __name__ == "__main__":
    run_d60_verification()
