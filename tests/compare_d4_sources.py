#!/usr/bin/env python3
"""
ANALYSIS: Compare D4 and D60 data from different sources
=========================================================
Source 1: varga_signs dict from planets (calculated during D1 chart)
Source 2: varga_data dict (calculated separately when varga is requested)
Source 3: Digital Twin (calculated for all vargas during save)
"""

import json
from pathlib import Path

# Load the saved profile with Digital Twin
profiles = sorted(Path("/app/data/profiles").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
with open(profiles[0]) as f:
    profile = json.load(f)

print("=" * 80)
print("ANALYSIS: D4 DATA COMPARISON FROM DIFFERENT CALCULATION PATHS")
print("=" * 80)
print(f"\nProfile: {profile['input'].get('name', 'N/A')}")
print(f"Birth: {profile['input'].get('date')} {profile['input'].get('time')}")

# Source 1: From chart.planets[].varga_signs (legacy path)
chart = profile.get("chart", {})
print("\n" + "-" * 80)
print("SOURCE 1: chart.planets[].varga_signs (from D1 calculation)")
print("-" * 80)
print("This is calculated ONCE during D1 chart generation.")
print("It uses calculate_all_vargas(abs_longitude) for each planet.")
print("\nNOT AVAILABLE in this profile (chart_data is minimal)")

# Source 2: varga_data from /calculate?varga=D4 endpoint
print("\n" + "-" * 80)
print("SOURCE 2: varga_data from /calculate endpoint (when varga param is passed)")
print("-" * 80)
print("This is calculated using get_varga_sign_and_degrees() separately.")
print("\n>>> Data from API call with varga=D4:")
print("""
varga_data = {
    "code": "D4",
    "ascendant": "Capricorn",
    "ascendant_degrees": 6.83,
    "planets": {
        "Sun": {"sign": "Leo", "degrees": 7.45},      <-- API says LEO
        "Moon": {"sign": "Aquarius", "degrees": 5.44},
        "Mars": {"sign": "Sagittarius", "degrees": 1.30},
        "Mercury": {"sign": "Scorpio", "degrees": 3.78},
        "Jupiter": {"sign": "Capricorn", "degrees": 0.53},
        "Venus": {"sign": "Aries", "degrees": 5.72},
        "Saturn": {"sign": "Pisces", "degrees": 7.20},
        "Rahu": {"sign": "Sagittarius", "degrees": 6.44},
        "Ketu": {"sign": "Gemini", "degrees": 6.44}
    }
}
""")

# Source 3: Digital Twin
print("\n" + "-" * 80)
print("SOURCE 3: digital_twin.vargas.D4 (from generate_digital_twin())")
print("-" * 80)
print("This is calculated using _generate_varga_chart() for ALL 16 vargas.")
print("\n>>> Data from Digital Twin:")

d4_twin = profile.get("digital_twin", {}).get("vargas", {}).get("D4", {})
print(f"\nAscendant: {d4_twin.get('ascendant', {})}")
print("\nPlanets:")
for p in d4_twin.get("planets", []):
    print(f"  {p['name']:10}: {p['sign_name']:12} ({p['relative_degree']:.2f}°) - House {p['house_occupied']}")

# Also check what varga_signs says for Sun
print("\n" + "=" * 80)
print("CRITICAL COMPARISON: SUN IN D4")
print("=" * 80)
print("""
From API /calculate with varga=D4:
  - planets[Sun].varga_signs["D4"] = "Leo"     <-- varga_signs dict
  - varga_data.planets.Sun.sign = "Leo"        <-- varga_data dict

From Digital Twin:
  - vargas.D4.planets[Sun].sign_name = ???     <-- Let's check

The SAME library function get_varga_sign_and_degrees() is used in both places!
So why the discrepancy?
""")

# Check Sun in Digital Twin D4
sun_d4 = None
for p in d4_twin.get("planets", []):
    if p["name"] == "Sun":
        sun_d4 = p
        break

if sun_d4:
    print(f"\nDigital Twin D4 Sun: {sun_d4['sign_name']} ({sun_d4['relative_degree']}°)")
    print(f"API varga_data D4 Sun: Leo (7.45°)")

    if sun_d4['sign_name'] == "Leo":
        print("\n✓ MATCH - Both show Leo")
    else:
        print(f"\n✗ MISMATCH - Digital Twin shows {sun_d4['sign_name']}, API shows Leo")

print("\n" + "=" * 80)
print("ROOT CAUSE ANALYSIS")
print("=" * 80)
print("""
The discrepancy could be caused by:

1. DIFFERENT ASCENDANT CALCULATION
   - D1 Ascendant: Cancer (from /calculate response)
   - D4 Ascendant in varga_data: Capricorn (from /calculate?varga=D4)
   - D4 Ascendant in Digital Twin: Check below

   The houses are assigned based on ascendant. If ascendant differs,
   planets end up in different houses even if their signs are the same.

2. HOUSE VS SIGN CONFUSION
   - In UI, we might be showing HOUSES instead of SIGNS
   - Or the table is mixing up columns
""")

print(f"\nDigital Twin D4 Ascendant: {d4_twin.get('ascendant', {})}")

# Final comparison table
print("\n" + "=" * 80)
print("FULL D4 COMPARISON TABLE")
print("=" * 80)
print(f"{'Planet':10} | {'API varga_signs':15} | {'API varga_data':15} | {'Digital Twin':15}")
print("-" * 70)

# API data (hardcoded from the response above)
api_varga_signs = {
    "Sun": "Leo",
    "Moon": "Aquarius",
    "Mars": "Sagittarius",
    "Mercury": "Scorpio",
    "Jupiter": "Capricorn",
    "Venus": "Aries",
    "Saturn": "Pisces",
    "Rahu": "Sagittarius",
    "Ketu": "Gemini"
}

api_varga_data = {
    "Sun": "Leo",
    "Moon": "Aquarius",
    "Mars": "Sagittarius",
    "Mercury": "Scorpio",
    "Jupiter": "Capricorn",
    "Venus": "Aries",
    "Saturn": "Pisces",
    "Rahu": "Sagittarius",
    "Ketu": "Gemini"
}

for p in d4_twin.get("planets", []):
    name = p["name"]
    vs = api_varga_signs.get(name, "?")
    vd = api_varga_data.get(name, "?")
    dt = p["sign_name"]
    match = "✓" if vs == vd == dt else "✗"
    print(f"{name:10} | {vs:15} | {vd:15} | {dt:15} {match}")

print("\n" + "=" * 80)
print("D60 COMPARISON")
print("=" * 80)

# Check D60
d60_twin = profile.get("digital_twin", {}).get("vargas", {}).get("D60", {})
print(f"\nDigital Twin D60 Ascendant: {d60_twin.get('ascendant', {})}")

# API D60 varga_signs from the response
api_d60 = {
    "Sun": "Libra",
    "Moon": "Sagittarius",
    "Mars": "Aquarius",
    "Mercury": "Gemini",
    "Jupiter": "Aquarius",
    "Venus": "Pisces",
    "Saturn": "Taurus",
    "Rahu": "Sagittarius",
    "Ketu": "Gemini"
}

print(f"\n{'Planet':10} | {'API varga_signs':15} | {'Digital Twin':15}")
print("-" * 50)
for p in d60_twin.get("planets", []):
    name = p["name"]
    api = api_d60.get(name, "?")
    dt = p["sign_name"]
    match = "✓" if api == dt else "✗"
    print(f"{name:10} | {api:15} | {dt:15} {match}")
