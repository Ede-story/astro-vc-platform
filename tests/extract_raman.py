#!/usr/bin/env python3
"""Extract D4 and D60 chart data with Raman ayanamsa."""

import json
from pathlib import Path

# Sign translations
SIGNS_RU = {
    "Aries": "Oven", "Taurus": "Telec", "Gemini": "Bliznecy", "Cancer": "Rak",
    "Leo": "Lev", "Virgo": "Deva", "Libra": "Vesy", "Scorpio": "Skorpion",
    "Sagittarius": "Strelec", "Capricorn": "Kozerog", "Aquarius": "Vodolej", "Pisces": "Ryby"
}

PLANETS_RU = {
    "Sun": "Solnce", "Moon": "Luna", "Mars": "Mars", "Mercury": "Merkurij",
    "Jupiter": "Jupiter", "Venus": "Venera", "Saturn": "Saturn", "Rahu": "Rahu", "Ketu": "Ketu"
}

DIGNITY_RU = {
    "Exalted": "Exalted", "Moolatrikona": "Moolatrikona", "Own": "Own",
    "Debilitated": "Debilitated", "Friend": "Friend", "Neutral": "Neutral", "Enemy": "Enemy"
}

# Load newest profile (Olya Raman)
profiles = sorted(Path("/app/data/profiles").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
with open(profiles[0]) as f:
    data = json.load(f)

dt = data["digital_twin"]
meta = dt["meta"]
d4 = dt["vargas"]["D4"]
d60 = dt["vargas"]["D60"]

def print_chart(name, chart):
    print("")
    print("=" * 70)
    print(f"  {name}")
    print("=" * 70)

    asc = chart["ascendant"]
    print(f"\nAscendant: {SIGNS_RU[asc['sign_name']]} ({asc['degrees']:.2f})")

    print(f"\n--- 12 HOUSES ---")
    print(f"{'House':<6} | {'Sign':<12} | {'Planets':<35}")
    print("-" * 65)

    for h in chart["houses"]:
        occupants = ", ".join([PLANETS_RU[p] for p in h["occupants"]]) if h["occupants"] else "-"
        sign_ru = SIGNS_RU[h["sign_name"]]
        print(f"{h['house_number']:<6} | {sign_ru:<12} | {occupants:<35}")

    print(f"\n--- PLANETS ---")
    print(f"{'Planet':<10} | {'Sign':<12} | {'House':<5} | {'Dignity':<12} | {'Deg':<8}")
    print("-" * 65)

    for p in chart["planets"]:
        name_ru = PLANETS_RU[p["name"]]
        sign_ru = SIGNS_RU[p["sign_name"]]
        dignity_ru = DIGNITY_RU.get(p["dignity_state"], p["dignity_state"])
        print(f"{name_ru:<10} | {sign_ru:<12} | {p['house_occupied']:<5} | {dignity_ru:<12} | {p['relative_degree']:>6.2f}")

print("=" * 70)
print("  PROFILE: " + data["input"]["name"])
print("  Ayanamsa: " + meta["ayanamsa"])
print("  Ayanamsa Delta: " + str(meta["ayanamsa_delta"]))
print("=" * 70)

print_chart("D4 - CHATURTHAMSHA (Property, Happiness)", d4)
print_chart("D60 - SHASHTIAMSHA (Past Life Karma)", d60)
