"""
Russian translations for astrological terms
All mappings for planets, signs, nakshatras, and UI labels
"""

# Planets (Graha)
PLANETS_EN_TO_RU = {
    "Sun": "Солнце",
    "Moon": "Луна",
    "Mars": "Марс",
    "Mercury": "Меркурий",
    "Jupiter": "Юпитер",
    "Venus": "Венера",
    "Saturn": "Сатурн",
    "Rahu": "Раху",
    "Ketu": "Кету",
    # Alternative names from jyotishganit
    "SUN": "Солнце",
    "MOON": "Луна",
    "MARS": "Марс",
    "MERCURY": "Меркурий",
    "JUPITER": "Юпитер",
    "VENUS": "Венера",
    "SATURN": "Сатурн",
    "RAHU": "Раху",
    "KETU": "Кету",
    # CelestialBody enum values
    "CelestialBody.SUN": "Солнце",
    "CelestialBody.MOON": "Луна",
    "CelestialBody.MARS": "Марс",
    "CelestialBody.MERCURY": "Меркурий",
    "CelestialBody.JUPITER": "Юпитер",
    "CelestialBody.VENUS": "Венера",
    "CelestialBody.SATURN": "Сатурн",
    "CelestialBody.RAHU": "Раху",
    "CelestialBody.KETU": "Кету",
}

# Zodiac Signs (Rashi)
SIGNS_EN_TO_RU = {
    "Aries": "Овен",
    "Taurus": "Телец",
    "Gemini": "Близнецы",
    "Cancer": "Рак",
    "Leo": "Лев",
    "Virgo": "Дева",
    "Libra": "Весы",
    "Scorpio": "Скорпион",
    "Sagittarius": "Стрелец",
    "Capricorn": "Козерог",
    "Aquarius": "Водолей",
    "Pisces": "Рыбы",
    # Uppercase variants
    "ARIES": "Овен",
    "TAURUS": "Телец",
    "GEMINI": "Близнецы",
    "CANCER": "Рак",
    "LEO": "Лев",
    "VIRGO": "Дева",
    "LIBRA": "Весы",
    "SCORPIO": "Скорпион",
    "SAGITTARIUS": "Стрелец",
    "CAPRICORN": "Козерог",
    "AQUARIUS": "Водолей",
    "PISCES": "Рыбы",
    # Sign enum values
    "Sign.ARIES": "Овен",
    "Sign.TAURUS": "Телец",
    "Sign.GEMINI": "Близнецы",
    "Sign.CANCER": "Рак",
    "Sign.LEO": "Лев",
    "Sign.VIRGO": "Дева",
    "Sign.LIBRA": "Весы",
    "Sign.SCORPIO": "Скорпион",
    "Sign.SAGITTARIUS": "Стрелец",
    "Sign.CAPRICORN": "Козерог",
    "Sign.AQUARIUS": "Водолей",
    "Sign.PISCES": "Рыбы",
}

# Nakshatras (27 Lunar Mansions)
NAKSHATRAS_EN_TO_RU = {
    "Ashwini": "Ашвини",
    "Bharani": "Бхарани",
    "Krittika": "Криттика",
    "Rohini": "Рохини",
    "Mrigashira": "Мригаширша",
    "Ardra": "Ардра",
    "Punarvasu": "Пунарвасу",
    "Pushya": "Пушья",
    "Ashlesha": "Ашлеша",
    "Magha": "Магха",
    "Purva Phalguni": "Пурва Пхалгуни",
    "Uttara Phalguni": "Уттара Пхалгуни",
    "Hasta": "Хаста",
    "Chitra": "Читра",
    "Swati": "Свати",
    "Vishakha": "Вишакха",
    "Anuradha": "Анурадха",
    "Jyeshtha": "Джьештха",
    "Mula": "Мула",
    "Purva Ashadha": "Пурва Ашадха",
    "Uttara Ashadha": "Уттара Ашадха",
    "Shravana": "Шравана",
    "Dhanishta": "Дхаништха",
    "Shatabhisha": "Шатабхиша",
    "Purva Bhadrapada": "Пурва Бхадрапада",
    "Uttara Bhadrapada": "Уттара Бхадрапада",
    "Revati": "Ревати",
    # Uppercase variants
    "ASHWINI": "Ашвини",
    "BHARANI": "Бхарани",
    "KRITTIKA": "Криттика",
    "ROHINI": "Рохини",
    "MRIGASHIRA": "Мригаширша",
    "ARDRA": "Ардра",
    "PUNARVASU": "Пунарвасу",
    "PUSHYA": "Пушья",
    "ASHLESHA": "Ашлеша",
    "MAGHA": "Магха",
    "PURVA_PHALGUNI": "Пурва Пхалгуни",
    "UTTARA_PHALGUNI": "Уттара Пхалгуни",
    "HASTA": "Хаста",
    "CHITRA": "Читра",
    "SWATI": "Свати",
    "VISHAKHA": "Вишакха",
    "ANURADHA": "Анурадха",
    "JYESHTHA": "Джьештха",
    "MULA": "Мула",
    "PURVA_ASHADHA": "Пурва Ашадха",
    "UTTARA_ASHADHA": "Уттара Ашадха",
    "SHRAVANA": "Шравана",
    "DHANISHTA": "Дхаништха",
    "SHATABHISHA": "Шатабхиша",
    "PURVA_BHADRAPADA": "Пурва Бхадрапада",
    "UTTARA_BHADRAPADA": "Уттара Бхадрапада",
    "REVATI": "Ревати",
    # Nakshatra enum values
    "Nakshatra.ASHWINI": "Ашвини",
    "Nakshatra.BHARANI": "Бхарани",
    "Nakshatra.KRITTIKA": "Криттика",
    "Nakshatra.ROHINI": "Рохини",
    "Nakshatra.MRIGASHIRA": "Мригаширша",
    "Nakshatra.ARDRA": "Ардра",
    "Nakshatra.PUNARVASU": "Пунарвасу",
    "Nakshatra.PUSHYA": "Пушья",
    "Nakshatra.ASHLESHA": "Ашлеша",
    "Nakshatra.MAGHA": "Магха",
    "Nakshatra.PURVA_PHALGUNI": "Пурва Пхалгуни",
    "Nakshatra.UTTARA_PHALGUNI": "Уттара Пхалгуни",
    "Nakshatra.HASTA": "Хаста",
    "Nakshatra.CHITRA": "Читра",
    "Nakshatra.SWATI": "Свати",
    "Nakshatra.VISHAKHA": "Вишакха",
    "Nakshatra.ANURADHA": "Анурадха",
    "Nakshatra.JYESHTHA": "Джьештха",
    "Nakshatra.MULA": "Мула",
    "Nakshatra.PURVA_ASHADHA": "Пурва Ашадха",
    "Nakshatra.UTTARA_ASHADHA": "Уттара Ашадха",
    "Nakshatra.SHRAVANA": "Шравана",
    "Nakshatra.DHANISHTA": "Дхаништха",
    "Nakshatra.SHATABHISHA": "Шатабхиша",
    "Nakshatra.PURVA_BHADRAPADA": "Пурва Бхадрапада",
    "Nakshatra.UTTARA_BHADRAPADA": "Уттара Бхадрапада",
    "Nakshatra.REVATI": "Ревати",
}

# Sign rulers (lords)
SIGN_RULERS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

# Nakshatra rulers
NAKSHATRA_RULERS = {
    "Ashwini": "Ketu",
    "Bharani": "Venus",
    "Krittika": "Sun",
    "Rohini": "Moon",
    "Mrigashira": "Mars",
    "Ardra": "Rahu",
    "Punarvasu": "Jupiter",
    "Pushya": "Saturn",
    "Ashlesha": "Mercury",
    "Magha": "Ketu",
    "Purva Phalguni": "Venus",
    "Uttara Phalguni": "Sun",
    "Hasta": "Moon",
    "Chitra": "Mars",
    "Swati": "Rahu",
    "Vishakha": "Jupiter",
    "Anuradha": "Saturn",
    "Jyeshtha": "Mercury",
    "Mula": "Ketu",
    "Purva Ashadha": "Venus",
    "Uttara Ashadha": "Sun",
    "Shravana": "Moon",
    "Dhanishta": "Mars",
    "Shatabhisha": "Rahu",
    "Purva Bhadrapada": "Jupiter",
    "Uttara Bhadrapada": "Saturn",
    "Revati": "Mercury",
}

# Houses owned by planets
PLANET_HOUSES = {
    "Sun": [5],  # Leo
    "Moon": [4],  # Cancer
    "Mars": [1, 8],  # Aries, Scorpio
    "Mercury": [3, 6],  # Gemini, Virgo
    "Jupiter": [9, 12],  # Sagittarius, Pisces
    "Venus": [2, 7],  # Taurus, Libra
    "Saturn": [10, 11],  # Capricorn, Aquarius
    "Rahu": [],  # Shadow planet
    "Ketu": [],  # Shadow planet
}

# Varga (Divisional Charts) names
VARGA_NAMES = {
    "D1": "Раши (D1)",
    "D2": "Хора (D2)",
    "D3": "Дреккана (D3)",
    "D4": "Чатуртхамша (D4)",
    "D7": "Саптамша (D7)",
    "D9": "Навамша (D9)",
    "D10": "Дашамша (D10)",
    "D12": "Двадашамша (D12)",
    "D16": "Шодашамша (D16)",
    "D20": "Вимшамша (D20)",
    "D24": "Чатурвимшамша (D24)",
    "D27": "Бхамша (D27)",
    "D30": "Тримшамша (D30)",
    "D40": "Кхаведамша (D40)",
    "D45": "Акшаведамша (D45)",
    "D60": "Шаштьямша (D60)",
}


def translate_planet(planet_name: str) -> str:
    """Translate planet name to Russian"""
    name = str(planet_name)
    if name in PLANETS_EN_TO_RU:
        return PLANETS_EN_TO_RU[name]
    # Try to extract from enum string
    for key, value in PLANETS_EN_TO_RU.items():
        if key.lower() in name.lower():
            return value
    return name


def translate_sign(sign_name: str) -> str:
    """Translate zodiac sign to Russian"""
    name = str(sign_name)
    if name in SIGNS_EN_TO_RU:
        return SIGNS_EN_TO_RU[name]
    # Try to extract from enum string
    for key, value in SIGNS_EN_TO_RU.items():
        if key.lower() in name.lower():
            return value
    return name


def translate_nakshatra(nakshatra_name: str) -> str:
    """Translate nakshatra to Russian"""
    name = str(nakshatra_name)
    if name in NAKSHATRAS_EN_TO_RU:
        return NAKSHATRAS_EN_TO_RU[name]
    # Try to extract from enum string
    for key, value in NAKSHATRAS_EN_TO_RU.items():
        if key.lower().replace("_", " ") in name.lower().replace("_", " "):
            return value
    return name


def get_sign_ruler(sign_name: str) -> str:
    """Get the ruling planet of a sign (in Russian)"""
    # Normalize sign name
    for eng_sign, ruler in SIGN_RULERS.items():
        if eng_sign.lower() in str(sign_name).lower():
            return translate_planet(ruler)
    return "—"


def get_nakshatra_ruler(nakshatra_name: str) -> str:
    """Get the ruling planet of a nakshatra (in Russian)"""
    for eng_nakshatra, ruler in NAKSHATRA_RULERS.items():
        if eng_nakshatra.lower().replace(" ", "") in str(nakshatra_name).lower().replace(" ", "").replace("_", ""):
            return translate_planet(ruler)
    return "—"


def get_houses_owned(planet_name: str, ascendant_sign: str) -> str:
    """
    Get houses owned by a planet based on ascendant sign.
    Returns comma-separated house numbers.
    """
    # Get planet's signs
    planet_signs = []
    for sign, ruler in SIGN_RULERS.items():
        if ruler.lower() in str(planet_name).lower():
            planet_signs.append(sign)

    if not planet_signs:
        return "—"

    # Find ascendant position in zodiac
    zodiac_order = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    asc_idx = None
    for i, sign in enumerate(zodiac_order):
        if sign.lower() in str(ascendant_sign).lower():
            asc_idx = i
            break

    if asc_idx is None:
        return "—"

    # Calculate house numbers for planet's signs
    houses = []
    for planet_sign in planet_signs:
        for i, sign in enumerate(zodiac_order):
            if sign == planet_sign:
                house_num = ((i - asc_idx) % 12) + 1
                houses.append(str(house_num))
                break

    return ", ".join(sorted(houses, key=int)) if houses else "—"
