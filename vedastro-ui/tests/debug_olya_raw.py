#!/usr/bin/env python3
"""
debug_olya_raw.py - "Naked" Test for Olya
==========================================

MISSION: Test jyotishganit library with NO DELTA, NO RAMAN conversion.
We want to see what the LIBRARY ITSELF produces for Olya's chart.

Test Subject: Olga
- Birth: 1982-05-30
- Time: 09:45
- Location: St. Petersburg (59.9343°N, 30.3351°E)
"""

from datetime import datetime
from jyotishganit import calculate_birth_chart
from jyotishganit.components.divisional_charts import (
    navamsa_from_long,
    drekkana_from_long,
    shashtiamsa_from_long,
    hora_from_long,
)

# Olya's birth data
BIRTH_DATE = datetime(1982, 5, 30, 9, 45, 0)
LATITUDE = 59.9343   # St. Petersburg
LONGITUDE = 30.3351

print("=" * 70)
print("NAKED TEST: OLYA (NO DELTA, NO RAMAN)")
print("=" * 70)
print(f"Birth: {BIRTH_DATE}")
print(f"Location: St. Petersburg ({LATITUDE}°N, {LONGITUDE}°E)")
print("=" * 70)

# Calculate chart using library defaults (Lahiri/Chitrapaksha)
print("\n[1] CALCULATING CHART WITH LIBRARY DEFAULTS...")
chart = calculate_birth_chart(BIRTH_DATE, LATITUDE, LONGITUDE)

print("\n[2] RAW PLANET DATA FROM LIBRARY:")
print("-" * 50)

planets_to_check = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

for planet_name in planets_to_check:
    if planet_name in chart:
        p = chart[planet_name]
        sign = p.get('sign', 'N/A')
        degrees = p.get('degrees', 0)
        longitude = p.get('longitude', 'N/A')
        nakshatra = p.get('nakshatra', 'N/A')

        print(f"{planet_name:10} | Sign: {sign:12} | Deg: {degrees:6.2f}° | Long: {longitude}")

print("\n[3] VARGA CALCULATIONS (NATIVE LIBRARY FUNCTIONS):")
print("-" * 50)

# Get Sun data for Varga tests
if 'Sun' in chart:
    sun = chart['Sun']
    sun_sign = sun.get('sign', '')
    sun_degrees = sun.get('degrees', 0)

    print(f"\nSUN in D1: {sun_sign} at {sun_degrees:.2f}°")
    print()

    # Test native Varga functions
    try:
        # D2 - Hora
        hora_result = hora_from_long(sun_sign, sun_degrees)
        print(f"D2  (Hora):       {hora_result}")
    except Exception as e:
        print(f"D2  (Hora):       ERROR - {e}")

    try:
        # D3 - Drekkana
        drekkana_result = drekkana_from_long(sun_sign, sun_degrees)
        print(f"D3  (Drekkana):   {drekkana_result}")
    except Exception as e:
        print(f"D3  (Drekkana):   ERROR - {e}")

    try:
        # D9 - Navamsa
        navamsa_result = navamsa_from_long(sun_sign, sun_degrees)
        print(f"D9  (Navamsa):    {navamsa_result}")
    except Exception as e:
        print(f"D9  (Navamsa):    ERROR - {e}")

    try:
        # D60 - Shashtiamsa
        shashti_result = shashtiamsa_from_long(sun_sign, sun_degrees)
        print(f"D60 (Shashtiamsa): {shashti_result}")
    except Exception as e:
        print(f"D60 (Shashtiamsa): ERROR - {e}")

print("\n[4] COMPARISON TEST - ALL PLANETS D9 (NAVAMSA):")
print("-" * 50)

for planet_name in planets_to_check:
    if planet_name in chart:
        p = chart[planet_name]
        sign = p.get('sign', '')
        degrees = p.get('degrees', 0)

        try:
            navamsa = navamsa_from_long(sign, degrees)
            print(f"{planet_name:10} | D1: {sign:12} {degrees:5.2f}° | D9: {navamsa}")
        except Exception as e:
            print(f"{planet_name:10} | D1: {sign:12} {degrees:5.2f}° | D9: ERROR - {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nNOTE: Compare these results with VedAstro for the same birth data")
print("      using Lahiri (NOT Raman) ayanamsa.")
