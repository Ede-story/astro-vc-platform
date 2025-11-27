#!/usr/bin/env python3
"""
FINAL DEBUG: What EXACTLY does the UI code produce?
"""
from jyotishganit import calculate_birth_chart
from datetime import datetime
import sys
sys.path.insert(0, "/app")

from ayanamsa_calc import SIGNS, get_varga_sign
from translations import translate_planet, translate_sign

# Olya data
birth_dt = datetime(1982, 5, 30, 9, 45, 0)
latitude = 59.9607
longitude = 30.1587

chart = calculate_birth_chart(birth_dt, latitude, longitude)

ayanamsa_delta = 0.0

d1_planet_data = []
for p in chart.d1_chart.planets:
    planet_name = str(p.celestial_body)
    orig_sign_name = str(p.sign)
    orig_degrees = p.sign_degrees

    sign_name = orig_sign_name
    sign_degrees = orig_degrees
    sign_idx = SIGNS.index(sign_name) if sign_name in SIGNS else 0
    longitude_val = sign_idx * 30 + sign_degrees

    d1_planet_data.append({
        "planet": planet_name,
        "planet_ru": translate_planet(planet_name),
        "sign": sign_name,
        "sign_ru": translate_sign(sign_name),
        "degrees": sign_degrees,
        "longitude": longitude_val,
    })

print("=" * 80)
print("FINAL DEBUG: EXACT UI FLOW")
print("=" * 80)

print("\n[D1 PLANETS]")
for p in d1_planet_data:
    pru = p["planet_ru"]
    sru = p["sign_ru"]
    deg = p["degrees"]
    lon = p["longitude"]
    print(pru, "|", sru, "|", round(deg, 2), "| Long:", round(lon, 2))

planet_longitudes = {}
for p_data in d1_planet_data:
    planet_longitudes[p_data["planet_ru"]] = p_data["longitude"]

d1_asc_house = chart.d1_chart.houses[0]
d1_asc_sign = str(d1_asc_house.sign)
d1_asc_deg = d1_asc_house.sign_degrees if hasattr(d1_asc_house, "sign_degrees") else 0
d1_asc_idx = SIGNS.index(d1_asc_sign) if d1_asc_sign in SIGNS else 0
d1_asc_longitude = d1_asc_idx * 30 + d1_asc_deg

print("\n[D1 ASC]:", d1_asc_sign, round(d1_asc_deg, 2), "| Long:", round(d1_asc_longitude, 2))

print("\n[D4 RESULTS]")
d4_asc = get_varga_sign(d1_asc_longitude, "D4")
print("D4 Ascendant:", d4_asc, "(" + translate_sign(d4_asc) + ")")
for pru, lon in planet_longitudes.items():
    d4_sign = get_varga_sign(lon, "D4")
    print(pru, "| D4:", d4_sign, "(" + translate_sign(d4_sign) + ")")

print("\n[D10 RESULTS]")
d10_asc = get_varga_sign(d1_asc_longitude, "D10")
print("D10 Ascendant:", d10_asc, "(" + translate_sign(d10_asc) + ")")
for pru, lon in planet_longitudes.items():
    d10_sign = get_varga_sign(lon, "D10")
    print(pru, "| D10:", d10_sign, "(" + translate_sign(d10_sign) + ")")

print("\n" + "=" * 80)
