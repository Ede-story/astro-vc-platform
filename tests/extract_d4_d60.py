#!/usr/bin/env python3
"""Extract and translate D4 and D60 chart data."""

import json
from pathlib import Path

# Load newest profile
profiles = sorted(Path("/app/data/profiles").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
with open(profiles[0]) as f:
    data = json.load(f)

dt = data["digital_twin"]
d4 = dt["vargas"]["D4"]
d60 = dt["vargas"]["D60"]

# Sign translations
SIGNS_RU = {
    "Aries": "Овен", "Taurus": "Телец", "Gemini": "Близнецы", "Cancer": "Рак",
    "Leo": "Лев", "Virgo": "Дева", "Libra": "Весы", "Scorpio": "Скорпион",
    "Sagittarius": "Стрелец", "Capricorn": "Козерог", "Aquarius": "Водолей", "Pisces": "Рыбы"
}

PLANETS_RU = {
    "Sun": "Солнце", "Moon": "Луна", "Mars": "Марс", "Mercury": "Меркурий",
    "Jupiter": "Юпитер", "Venus": "Венера", "Saturn": "Сатурн", "Rahu": "Раху", "Ketu": "Кету"
}

DIGNITY_RU = {
    "Exalted": "Экзальтация", "Moolatrikona": "Мулатрикона", "Own": "Свой знак",
    "Debilitated": "Падение", "Friend": "Друг", "Neutral": "Нейтрал", "Enemy": "Враг"
}

def print_chart(name, chart):
    print("")
    print("=" * 65)
    print(f"  {name}")
    print("=" * 65)

    asc = chart["ascendant"]
    print(f"\nАсцендент: {SIGNS_RU[asc['sign_name']]} ({asc['degrees']:.2f})")

    print(f"\n--- 12 ДОМОВ ---")
    print(f"{'Дом':<5} | {'Знак':<12} | {'Планеты в доме':<35}")
    print("-" * 65)

    for h in chart["houses"]:
        occupants = ", ".join([PLANETS_RU[p] for p in h["occupants"]]) if h["occupants"] else "-"
        sign_ru = SIGNS_RU[h["sign_name"]]
        print(f"{h['house_number']:<5} | {sign_ru:<12} | {occupants:<35}")

    print(f"\n--- ПЛАНЕТЫ ---")
    print(f"{'Планета':<10} | {'Знак':<12} | {'Дом':<4} | {'Достоинство':<12} | {'Град.':<8}")
    print("-" * 65)

    for p in chart["planets"]:
        name_ru = PLANETS_RU[p["name"]]
        sign_ru = SIGNS_RU[p["sign_name"]]
        dignity_ru = DIGNITY_RU.get(p["dignity_state"], p["dignity_state"])
        print(f"{name_ru:<10} | {sign_ru:<12} | {p['house_occupied']:<4} | {dignity_ru:<12} | {p['relative_degree']:>6.2f}")

print_chart("D4 - ЧАТУРТХАМША (Недвижимость, Счастье)", d4)
print_chart("D60 - ШАШТИАМША (Карма прошлых жизней)", d60)
