"""
Script to resave Vadim's profile with full D1+D9 structure
"""
import datetime
import json
from zoneinfo import ZoneInfo
from jyotishganit import calculate_birth_chart

import sys
sys.path.insert(0, '/app')
from db_utils import save_profile

# Test data for Vadim
BIRTH_DATE = datetime.datetime(1977, 10, 25, 6, 28)
LATITUDE = 61.70274
LONGITUDE = 30.691231
TIMEZONE = "Europe/Moscow"

def resave_vadim():
    print("Recalculating and saving Vadim's profile with full structure...")

    # Calculate timezone offset
    tz = ZoneInfo(TIMEZONE)
    local_dt_aware = BIRTH_DATE.replace(tzinfo=tz)
    offset = local_dt_aware.utcoffset().total_seconds() / 3600.0

    # Calculate chart
    chart = calculate_birth_chart(
        birth_date=BIRTH_DATE,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        timezone_offset=offset
    )

    # Build searchable planets structure (D1 + D9)
    planets_data = {}
    if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'planets'):
        for p in chart.d1_chart.planets:
            planet_key = str(p.celestial_body).upper()
            # Normalize key
            for pname in ['SUN', 'MOON', 'MARS', 'MERCURY', 'JUPITER', 'VENUS', 'SATURN', 'RAHU', 'KETU']:
                if pname in planet_key:
                    planet_key = pname
                    break

            planets_data[planet_key] = {
                'rasi': str(p.sign),
                'rasi_degrees': round(p.sign_degrees, 2),
                'nakshatra': str(p.nakshatra),
                'house': p.house,
                'navamsha': None
            }

    # Add D9 (Navamsha) data
    if hasattr(chart, 'divisional_charts') and 'd9' in chart.divisional_charts:
        d9 = chart.divisional_charts['d9']
        for house in d9.houses:
            for occupant in house.occupants:
                planet_key = str(occupant.celestial_body).upper()
                for pname in ['SUN', 'MOON', 'MARS', 'MERCURY', 'JUPITER', 'VENUS', 'SATURN', 'RAHU', 'KETU']:
                    if pname in planet_key:
                        planet_key = pname
                        break
                if planet_key in planets_data:
                    planets_data[planet_key]['navamsha'] = str(occupant.sign)

    # Get ascendant
    ascendant = None
    if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'houses') and chart.d1_chart.houses:
        ascendant = str(chart.d1_chart.houses[0].sign)

    chart_data = {
        'calculated_at': datetime.datetime.now().isoformat(),
        'ayanamsa': 'Lahiri',
        'input': {
            'name': 'Вадим',
            'gender': 'Мужской',
            'date': '1977-10-25',
            'time': '06:28:00',
            'city': 'Сортавала',
            'lat': LATITUDE,
            'lon': LONGITUDE,
            'tz': TIMEZONE
        },
        'ascendant': ascendant,
        'planets': planets_data
    }

    # Save to DB
    profile_id = save_profile(
        display_name='Вадим',
        gender='Мужской',
        birth_date=datetime.date(1977, 10, 25),
        birth_time=datetime.time(6, 28),
        birth_place='Сортавала',
        latitude=LATITUDE,
        longitude=LONGITUDE,
        timezone=TIMEZONE,
        chart_data=chart_data
    )

    print(f"\nProfile saved with ID: {profile_id}")
    print("\n" + "=" * 60)
    print("NEW DATABASE STRUCTURE:")
    print("=" * 60)
    print(json.dumps(chart_data, indent=2, ensure_ascii=False))

    return chart_data


if __name__ == "__main__":
    resave_vadim()
