import streamlit as st
import pandas as pd
import datetime
import json
from datetime import date, time
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from jyotishganit import calculate_birth_chart

# Database imports
from db_utils import (
    init_database, save_profile, get_all_profiles,
    get_profile_by_name, delete_profile, test_connection
)

# Translation imports
from translations import (
    translate_planet, translate_sign, translate_nakshatra,
    get_sign_ruler, get_nakshatra_ruler, get_houses_owned,
    VARGA_NAMES, SIGN_RULERS
)

# Ayanamsa calculation imports (AstroCore V2 - Clean Slate)
from ayanamsa_calc import (
    datetime_to_jd, get_ayanamsa_delta,
    convert_planet_position, calculate_navamsha_sign, SIGNS,
    get_varga_sign  # Uses native jyotishganit Varga functions
)

# Backward compatibility alias
calculate_varga_sign = get_varga_sign

st.set_page_config(page_title="StarMeet Astro UI", layout="wide")


# --- JSON SERIALIZER FOR DATES ---
def json_serial(obj):
    """JSON serializer for objects not serializable by default"""
    if isinstance(obj, (date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, time):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def serialize_profile_data(data: dict) -> dict:
    """Convert all date/time objects to strings for JSON storage"""
    result = {}
    for key, value in data.items():
        if isinstance(value, (date, datetime.datetime)):
            result[key] = value.isoformat()
        elif isinstance(value, time):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_profile_data(value)
        else:
            result[key] = value
    return result


# --- DATABASE INITIALIZATION (runs once at startup) ---
@st.cache_resource
def setup_database():
    """Initialize database connection and schema"""
    try:
        success = init_database()
        return success, None
    except Exception as e:
        return False, str(e)


db_ok, db_error = setup_database()

# Show DB status in sidebar
if not db_ok:
    st.sidebar.error(f"БД недоступна: {db_error}")
    st.sidebar.info("Данные будут храниться в памяти сессии")

st.title("StarMeet: Ведическая Астрология")

# --- SIDEBAR: SAVED PROFILES ---
with st.sidebar:
    st.header("Сохраненные профили")

    # Load profiles from DB
    profiles = []
    if db_ok:
        try:
            profiles = get_all_profiles()
        except Exception as e:
            st.warning(f"Ошибка загрузки: {e}")

    if profiles:
        profile_names = ["-- Новый профиль --"] + [p['display_name'] for p in profiles]
        selected_profile = st.selectbox("Выберите профиль", profile_names)

        if selected_profile != "-- Новый профиль --":
            if st.button("Загрузить профиль"):
                profile_data = get_profile_by_name(selected_profile)
                if profile_data:
                    st.session_state['loaded_profile'] = profile_data
                    st.success(f"Загружен: {selected_profile}")
                    st.rerun()

            if st.button("Удалить профиль"):
                if delete_profile(selected_profile):
                    st.success(f"Удален: {selected_profile}")
                    st.rerun()
    else:
        st.info("Нет сохраненных профилей")

    st.divider()

# --- SIDEBAR: INPUT FORM ---
with st.sidebar:
    st.header("Ввод данных")

    # Pre-fill from loaded profile
    loaded = st.session_state.get('loaded_profile', {})

    name = st.text_input("Имя", value=loaded.get('display_name', ""))
    gender = st.selectbox(
        "Пол",
        ["Мужской", "Женский"],
        index=0 if loaded.get('gender') != 'Женский' else 1
    )

    # Date input
    default_date = loaded.get('birth_date', datetime.date(1990, 1, 1))
    if isinstance(default_date, str):
        default_date = datetime.datetime.strptime(default_date, '%Y-%m-%d').date()
    date_input = st.date_input("Дата рождения", value=default_date)

    # PRECISE TIME INPUT (hour/minute sliders)
    st.write("**Время рождения**")
    default_time = loaded.get('birth_time', datetime.time(12, 0))
    if isinstance(default_time, str):
        try:
            default_time = datetime.datetime.strptime(default_time, '%H:%M:%S').time()
        except ValueError:
            default_time = datetime.datetime.strptime(default_time, '%H:%M').time()

    col_hour, col_min = st.columns(2)
    with col_hour:
        hour_input = st.slider("Час", 0, 23, default_time.hour, key="hour_slider")
    with col_min:
        minute_input = st.slider("Минута", 0, 59, default_time.minute, key="minute_slider")

    time_input = datetime.time(hour_input, minute_input)
    st.caption(f"Выбрано: **{hour_input:02d}:{minute_input:02d}**")

    city = st.text_input("Город рождения", value=loaded.get('birth_place', ""))

    # Geolocation with caching to avoid repeated API calls on page rerun
    lat, lon, tz_str = None, None, None

    # Check if we have cached geo data for this city
    cached_city = st.session_state.get('cached_city')
    if city and city == cached_city:
        # Use cached coordinates
        lat = st.session_state.get('cached_lat')
        lon = st.session_state.get('cached_lon')
        tz_str = st.session_state.get('cached_tz')
        if lat and lon:
            st.success(f"Координаты: {lat:.4f}, {lon:.4f}")
            st.info(f"Часовой пояс: {tz_str}")
    elif city:
        # New city - fetch from geocoder
        try:
            geolocator = Nominatim(user_agent="starmeet_astro", timeout=10)
            location = geolocator.geocode(city)

            if location:
                lat = location.latitude
                lon = location.longitude
                st.success(f"Координаты: {lat:.4f}, {lon:.4f}")

                tf = TimezoneFinder()
                tz_str = tf.timezone_at(lng=lon, lat=lat)
                st.info(f"Часовой пояс: {tz_str}")

                # Cache the results
                st.session_state['cached_city'] = city
                st.session_state['cached_lat'] = lat
                st.session_state['cached_lon'] = lon
                st.session_state['cached_tz'] = tz_str
            else:
                st.warning("Город не найден. Введите корректное название.")
        except Exception as geo_error:
            st.error(f"Ошибка геокодера: {geo_error}")
            st.info("Попробуйте ввести город на английском языке или повторите позже.")

    st.divider()

    # AYANAMSA SELECTOR (Raman is default - index=0)
    st.write("**Система расчёта (Ayanamsa)**")
    ayanamsa_options = ["Raman", "Lahiri"]
    ayanamsa_labels = {
        "Raman": "Raman (B.V. Raman)",
        "Lahiri": "Lahiri (стандарт Индии)"
    }
    selected_ayanamsa = st.selectbox(
        "Ayanamsa",
        ayanamsa_options,
        index=0,  # Raman is default
        format_func=lambda x: ayanamsa_labels.get(x, x)
    )
    st.caption("jyotishganit использует True Chitrapaksha")

    # VARGA SELECTOR - Master Controller for Tables (Full Parashara Vargas)
    st.write("**Выбор Варги (дробной карты)**")
    available_vargas = [
        "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
        "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"
    ]
    selected_varga = st.selectbox(
        "Варга",
        available_vargas,
        format_func=lambda x: VARGA_NAMES.get(x, x),
        key="varga_selector"
    )
    st.caption("16 дробных карт по Парашаре")

    st.divider()

    # Action buttons
    col_calc, col_save = st.columns(2)

    with col_calc:
        calculate_btn = st.button("Рассчитать", type="primary", disabled=not (lat and lon))

    with col_save:
        save_btn = st.button("Сохранить", disabled=not (name and lat and lon and db_ok))

    # Handle Calculate
    if calculate_btn and lat and lon:
        local_dt = datetime.datetime.combine(date_input, time_input)
        tz = ZoneInfo(tz_str)
        local_dt_aware = local_dt.replace(tzinfo=tz)
        offset = local_dt_aware.utcoffset().total_seconds() / 3600.0

        try:
            chart = calculate_birth_chart(
                birth_date=local_dt,
                latitude=lat,
                longitude=lon,
                timezone_offset=offset
            )

            # Store in session state
            st.session_state['chart'] = chart
            st.session_state['calculated'] = True
            st.session_state['current_profile'] = {
                'name': name,
                'gender': gender,
                'date': date_input.isoformat(),
                'time': time_input.isoformat(),
                'city': city,
                'lat': lat,
                'lon': lon,
                'tz': tz_str
            }

            # Calculate Julian Day (needed for ayanamsa and Mean Nodes)
            jd = datetime_to_jd(local_dt, offset)
            st.session_state['julian_day'] = jd

            # Calculate ayanamsa delta if Raman is selected
            # MIDDLEWARE ARCHITECTURE: Use library values + delta shift only
            # (No external SwissEph Mean Nodes - use library's True Nodes with delta)
            ayanamsa_delta = 0.0

            if selected_ayanamsa == "Raman":
                ayanamsa_delta = get_ayanamsa_delta(jd, 'True_Chitrapaksha', 'Raman')
                st.session_state['ayanamsa_delta'] = ayanamsa_delta
            else:
                st.session_state['ayanamsa_delta'] = 0.0

            # Russian to English sign mapping
            ru_to_en_signs = {
                'Овен': 'Aries', 'Телец': 'Taurus', 'Близнецы': 'Gemini',
                'Рак': 'Cancer', 'Лев': 'Leo', 'Дева': 'Virgo',
                'Весы': 'Libra', 'Скорпион': 'Scorpio', 'Стрелец': 'Sagittarius',
                'Козерог': 'Capricorn', 'Водолей': 'Aquarius', 'Рыбы': 'Pisces'
            }
            en_to_ru_signs = {v: k for k, v in ru_to_en_signs.items()}

            # Get D1 ascendant sign for house ownership calculations
            d1_ascendant_sign = None
            if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'houses'):
                if chart.d1_chart.houses:
                    d1_ascendant_sign = str(chart.d1_chart.houses[0].sign)

            # Pre-calculate D1 Planet Data (with ayanamsa conversion if needed)
            d1_planet_data = []
            if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'planets'):
                for p in chart.d1_chart.planets:
                    planet_name = str(p.celestial_body)
                    planet_name_upper = planet_name.upper()
                    orig_sign_name = str(p.sign)
                    orig_degrees = p.sign_degrees

                    # MIDDLEWARE ARCHITECTURE: All planets (including Rahu/Ketu) use same delta shift
                    # Library provides True Nodes; we just apply ayanamsa delta
                    if ayanamsa_delta != 0:
                        # Apply ayanamsa delta (Raman conversion)
                        new_pos = convert_planet_position(orig_sign_name, orig_degrees, ayanamsa_delta)
                        sign_name = new_pos['sign']
                        sign_degrees = new_pos['degrees']
                        nakshatra_name = new_pos['nakshatra']
                        pada = new_pos['pada']
                        navamsha_sign = new_pos['navamsha']
                        longitude = new_pos['longitude']
                    else:
                        # Use raw jyotishganit output for Lahiri (no conversion)
                        sign_name = orig_sign_name
                        sign_degrees = orig_degrees
                        nakshatra_name = str(p.nakshatra)
                        pada = getattr(p, 'nakshatra_pada', getattr(p, 'pada', None))
                        navamsha_sign = None
                        # CRITICAL: Always calculate longitude for Varga calculations!
                        sign_idx = SIGNS.index(sign_name) if sign_name in SIGNS else 0
                        longitude = sign_idx * 30 + sign_degrees

                    d1_planet_data.append({
                        "Планета": translate_planet(planet_name),
                        "Знак и Градусы": f"{translate_sign(sign_name)} {sign_degrees:.2f}°",
                        "Накшатра-Пада": f"{translate_nakshatra(nakshatra_name)}-{pada}" if pada else translate_nakshatra(nakshatra_name),
                        "Дом": p.house,
                        "Управляемые Дома": get_houses_owned(planet_name, d1_ascendant_sign) if d1_ascendant_sign else "—",
                        "Управитель Знака": get_sign_ruler(sign_name),
                        "Управитель Накшатры": get_nakshatra_ruler(nakshatra_name),
                        "_navamsha": navamsha_sign,  # Store for D9 recalculation
                        "_longitude": longitude,
                    })
            st.session_state['d1_planet_data'] = d1_planet_data

            # Pre-calculate D1 House Data (with ayanamsa conversion if needed)
            d1_house_data = []
            if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'houses'):
                for h in chart.d1_chart.houses:
                    orig_deg = getattr(h, 'sign_degrees', None)
                    orig_sign_name = str(h.sign)
                    orig_nakshatra = getattr(h, 'nakshatra', None)
                    orig_pada = getattr(h, 'nakshatra_pada', getattr(h, 'pada', None))

                    # Apply ayanamsa delta to house cusps if Raman is selected
                    if ayanamsa_delta != 0 and orig_deg is not None:
                        house_pos = convert_planet_position(orig_sign_name, orig_deg, ayanamsa_delta)
                        sign_name = house_pos['sign']
                        deg = house_pos['degrees']
                        nakshatra = house_pos['nakshatra']
                        pada = house_pos['pada']
                    else:
                        sign_name = orig_sign_name
                        deg = orig_deg
                        nakshatra = orig_nakshatra
                        pada = orig_pada

                    # Find planets in this house
                    planets_in_house = []
                    if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'planets'):
                        for p in chart.d1_chart.planets:
                            if p.house == h.number:
                                planets_in_house.append(translate_planet(str(p.celestial_body)))

                    # Get aspecting planets
                    aspecting_planets = []
                    if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'planets'):
                        for p in chart.d1_chart.planets:
                            planet_name = str(p.celestial_body).upper()
                            planet_house = p.house

                            # 7th aspect (all planets)
                            if (planet_house + 6) % 12 + 1 == h.number:
                                aspecting_planets.append(translate_planet(str(p.celestial_body)))

                            # Mars special aspects (4th, 8th)
                            if 'MARS' in planet_name:
                                if (planet_house + 3) % 12 + 1 == h.number:
                                    aspecting_planets.append(f"{translate_planet(str(p.celestial_body))} (4)")
                                if (planet_house + 7) % 12 + 1 == h.number:
                                    aspecting_planets.append(f"{translate_planet(str(p.celestial_body))} (8)")

                            # Jupiter special aspects (5th, 9th)
                            if 'JUPITER' in planet_name:
                                if (planet_house + 4) % 12 + 1 == h.number:
                                    aspecting_planets.append(f"{translate_planet(str(p.celestial_body))} (5)")
                                if (planet_house + 8) % 12 + 1 == h.number:
                                    aspecting_planets.append(f"{translate_planet(str(p.celestial_body))} (9)")

                            # Saturn special aspects (3rd, 10th)
                            if 'SATURN' in planet_name:
                                if (planet_house + 2) % 12 + 1 == h.number:
                                    aspecting_planets.append(f"{translate_planet(str(p.celestial_body))} (3)")
                                if (planet_house + 9) % 12 + 1 == h.number:
                                    aspecting_planets.append(f"{translate_planet(str(p.celestial_body))} (10)")

                    aspecting_planets = list(dict.fromkeys(aspecting_planets))

                    d1_house_data.append({
                        "Дом": h.number,
                        "Знак и Градусы": f"{translate_sign(sign_name)} {deg:.2f}°" if deg is not None else translate_sign(sign_name),
                        "Накшатра-Пада": f"{translate_nakshatra(str(nakshatra))}-{pada}" if nakshatra and pada else (translate_nakshatra(str(nakshatra)) if nakshatra else "—"),
                        "Планеты в Доме": ", ".join(planets_in_house) if planets_in_house else "—",
                        "Аспектирующие Планеты": ", ".join(aspecting_planets) if aspecting_planets else "—",
                    })
            st.session_state['d1_house_data'] = d1_house_data

            # Pre-calculate D9 (Navamsha) Planet Data
            d9_planet_data = []
            d9_ascendant_sign = None

            # When ayanamsa delta is applied, use recalculated navamsha signs from D1 data
            if ayanamsa_delta != 0:
                # Build D9 from recalculated navamsha signs stored in d1_planet_data
                # Create a mapping from planet to navamsha sign
                planet_navamsha_map = {}
                for p_data in d1_planet_data:
                    planet_ru = p_data.get("Планета")
                    navamsha = p_data.get("_navamsha")
                    if navamsha:
                        planet_navamsha_map[planet_ru] = navamsha

                # Also recalculate D9 Ascendant from D1 Ascendant
                if d1_house_data:
                    asc_data = d1_house_data[0]  # First house is Ascendant
                    asc_sign_deg = asc_data.get("Знак и Градусы", "")
                    # Extract sign and degrees
                    parts = asc_sign_deg.split()
                    if len(parts) >= 2:
                        asc_sign_ru = parts[0]
                        asc_deg_str = parts[1].replace("°", "")
                        try:
                            asc_deg = float(asc_deg_str)
                            # Map Russian to English
                            ru_to_en = {
                                'Овен': 'Aries', 'Телец': 'Taurus', 'Близнецы': 'Gemini',
                                'Рак': 'Cancer', 'Лев': 'Leo', 'Дева': 'Virgo',
                                'Весы': 'Libra', 'Скорпион': 'Scorpio', 'Стрелец': 'Sagittarius',
                                'Козерог': 'Capricorn', 'Водолей': 'Aquarius', 'Рыбы': 'Pisces'
                            }
                            asc_sign_en = ru_to_en.get(asc_sign_ru, asc_sign_ru)
                            # Calculate navamsha for Ascendant
                            asc_longitude = SIGNS.index(asc_sign_en) * 30 + asc_deg if asc_sign_en in SIGNS else 0
                            d9_ascendant_sign = calculate_navamsha_sign(asc_longitude)
                        except (ValueError, IndexError):
                            pass

                # Build D9 planet data from recalculated navamsha signs
                for p_data in d1_planet_data:
                    planet_ru = p_data.get("Планета")
                    navamsha_sign = p_data.get("_navamsha")
                    if navamsha_sign:
                        d9_planet_data.append({
                            "Планета": planet_ru,
                            "Знак и Градусы": translate_sign(navamsha_sign),
                            "Накшатра-Пада": "—",
                            "Дом": "—",  # Would need to recalculate based on D9 Ascendant
                            "Управляемые Дома": "—",
                            "Управитель Знака": get_sign_ruler(navamsha_sign),
                            "Управитель Накшатры": "—",
                        })
            else:
                # Use library's D9 output when no ayanamsa conversion
                if hasattr(chart, 'divisional_charts') and 'd9' in chart.divisional_charts:
                    d9 = chart.divisional_charts['d9']

                    # Get D9 ascendant (first house)
                    if hasattr(d9, 'houses') and d9.houses:
                        d9_ascendant_sign = str(d9.houses[0].sign) if hasattr(d9.houses[0], 'sign') else None

                    # Build planet data from D9 houses
                    for house in d9.houses:
                        for occupant in house.occupants:
                            planet_name = str(occupant.celestial_body)
                            sign_name = str(occupant.sign)

                            d9_planet_data.append({
                                "Планета": translate_planet(planet_name),
                                "Знак и Градусы": translate_sign(sign_name),
                                "Накшатра-Пада": "—",  # D9 typically doesn't show pada
                                "Дом": house.number,
                                "Управляемые Дома": "—",
                                "Управитель Знака": get_sign_ruler(sign_name),
                                "Управитель Накшатры": "—",
                            })
            st.session_state['d9_planet_data'] = d9_planet_data

            # Pre-calculate D9 House Data
            d9_house_data = []

            if ayanamsa_delta != 0 and d9_ascendant_sign:
                # Build D9 houses from recalculated D9 Ascendant when ayanamsa is applied
                # D9 houses follow the zodiac from D9 Ascendant sign
                d9_asc_idx = SIGNS.index(d9_ascendant_sign) if d9_ascendant_sign in SIGNS else 0

                # Create a mapping of planets to their D9 signs
                planet_d9_signs = {}
                for p_data in d9_planet_data:
                    planet_ru = p_data.get("Планета")
                    sign_ru = p_data.get("Знак и Градусы", "")
                    planet_d9_signs[planet_ru] = sign_ru

                for house_num in range(1, 13):
                    house_sign_idx = (d9_asc_idx + house_num - 1) % 12
                    house_sign = SIGNS[house_sign_idx]

                    # Find planets in this house (planets whose D9 sign matches house sign)
                    planets_in_house = []
                    house_sign_ru = translate_sign(house_sign)
                    for planet_ru, sign_ru in planet_d9_signs.items():
                        if sign_ru == house_sign_ru:
                            planets_in_house.append(planet_ru)

                    d9_house_data.append({
                        "Дом": house_num,
                        "Знак и Градусы": house_sign_ru,
                        "Накшатра-Пада": "—",
                        "Планеты в Доме": ", ".join(planets_in_house) if planets_in_house else "—",
                        "Аспектирующие Планеты": "—",
                    })
            else:
                # Use library's D9 houses when no ayanamsa conversion
                if hasattr(chart, 'divisional_charts') and 'd9' in chart.divisional_charts:
                    d9 = chart.divisional_charts['d9']
                    if hasattr(d9, 'houses'):
                        for h in d9.houses:
                            sign_name = str(h.sign) if hasattr(h, 'sign') else "—"

                            # Find planets in this D9 house
                            planets_in_house = []
                            if hasattr(h, 'occupants'):
                                for occ in h.occupants:
                                    planets_in_house.append(translate_planet(str(occ.celestial_body)))

                            d9_house_data.append({
                                "Дом": h.number,
                                "Знак и Градусы": translate_sign(sign_name),
                                "Накшатра-Пада": "—",
                                "Планеты в Доме": ", ".join(planets_in_house) if planets_in_house else "—",
                                "Аспектирующие Планеты": "—",  # Simplified for D9
                            })
            st.session_state['d9_house_data'] = d9_house_data

            # Store ascendant info
            st.session_state['d1_ascendant_sign'] = d1_ascendant_sign
            st.session_state['d9_ascendant_sign'] = d9_ascendant_sign

            # Pre-calculate ALL divisional charts (D2-D60) using MANUAL PARASHARA FORMULAS
            # CRITICAL: Use corrected (Raman) longitudes from D1, NOT raw jyotishganit output
            all_vargas = ['D2', 'D3', 'D4', 'D7', 'D10', 'D12', 'D16', 'D20', 'D24', 'D27', 'D30', 'D40', 'D45', 'D60']

            # Build planet longitudes map from D1 data (already ayanamsa-corrected)
            planet_longitudes = {}
            for p_data in d1_planet_data:
                planet_ru = p_data.get("Планета")
                longitude = p_data.get("_longitude")  # Corrected absolute longitude
                if longitude is not None:
                    planet_longitudes[planet_ru] = longitude

            # Get D1 Ascendant longitude for Varga Ascendant calculations
            d1_asc_longitude = None
            if d1_house_data:
                asc_data = d1_house_data[0]
                asc_sign_deg = asc_data.get("Знак и Градусы", "")
                parts = asc_sign_deg.split()
                if len(parts) >= 2:
                    asc_sign_ru = parts[0]
                    asc_deg_str = parts[1].replace("°", "")
                    try:
                        asc_deg = float(asc_deg_str)
                        asc_sign_en = ru_to_en_signs.get(asc_sign_ru, asc_sign_ru)
                        if asc_sign_en in SIGNS:
                            d1_asc_longitude = SIGNS.index(asc_sign_en) * 30 + asc_deg
                    except (ValueError, IndexError):
                        pass

            for varga_key in all_vargas:
                varga_planet_data = []
                varga_house_data = []
                varga_ascendant = None

                # Calculate Varga Ascendant from D1 Ascendant longitude
                if d1_asc_longitude is not None:
                    varga_ascendant = calculate_varga_sign(d1_asc_longitude, varga_key)

                # Calculate Varga signs for all planets using corrected longitudes
                planet_varga_signs = {}
                for planet_ru, longitude in planet_longitudes.items():
                    varga_sign = calculate_varga_sign(longitude, varga_key)
                    planet_varga_signs[planet_ru] = varga_sign

                    varga_planet_data.append({
                        "Планета": planet_ru,
                        "Знак и Градусы": translate_sign(varga_sign),
                        "Накшатра-Пада": "—",
                        "Дом": "—",  # Will be calculated below based on Varga Ascendant
                        "Управляемые Дома": "—",
                        "Управитель Знака": get_sign_ruler(varga_sign),
                        "Управитель Накшатры": "—",
                    })

                # Build house data based on Varga Ascendant
                if varga_ascendant and varga_ascendant in SIGNS:
                    varga_asc_idx = SIGNS.index(varga_ascendant)

                    for house_num in range(1, 13):
                        house_sign_idx = (varga_asc_idx + house_num - 1) % 12
                        house_sign = SIGNS[house_sign_idx]

                        # Find planets in this house
                        planets_in_house = []
                        for planet_ru, sign in planet_varga_signs.items():
                            if sign == house_sign:
                                planets_in_house.append(planet_ru)

                        varga_house_data.append({
                            "Дом": house_num,
                            "Знак и Градусы": translate_sign(house_sign),
                            "Накшатра-Пада": "—",
                            "Планеты в Доме": ", ".join(planets_in_house) if planets_in_house else "—",
                            "Аспектирующие Планеты": "—",
                        })

                    # Update planet house numbers based on Varga Ascendant
                    for p_data in varga_planet_data:
                        planet_sign_ru = p_data.get("Знак и Градусы")
                        # Find which house this sign is
                        for h_data in varga_house_data:
                            if h_data.get("Знак и Градусы") == planet_sign_ru:
                                p_data["Дом"] = h_data.get("Дом")
                                break

                # Store in session state
                st.session_state[f'{varga_key}_planet_data'] = varga_planet_data
                st.session_state[f'{varga_key}_house_data'] = varga_house_data
                st.session_state[f'{varga_key}_ascendant_sign'] = varga_ascendant

            st.success("Расчет выполнен! (D1-D60 по формулам Парашары)")

        except Exception as e:
            st.error(f"Ошибка расчета: {e}")
            import traceback
            st.code(traceback.format_exc())

    # Handle Save
    if save_btn and name and db_ok:
        try:
            # Prepare chart data for storage with FULL structure for AI Matching
            chart_data = None
            chart = st.session_state.get('chart')
            if chart:
                profile_input = st.session_state.get('current_profile', {})

                # Build searchable planets structure from pre-calculated data (already ayanamsa-adjusted)
                planets_data = {}
                d1_planet_data = st.session_state.get('d1_planet_data', [])
                d9_planet_data = st.session_state.get('d9_planet_data', [])

                # Russian to English mappings for storage
                ru_to_en_planets = {
                    'Солнце': 'SUN', 'Луна': 'MOON', 'Марс': 'MARS',
                    'Меркурий': 'MERCURY', 'Юпитер': 'JUPITER', 'Венера': 'VENUS',
                    'Сатурн': 'SATURN', 'Раху': 'RAHU', 'Кету': 'KETU'
                }
                ru_to_en_signs = {
                    'Овен': 'Aries', 'Телец': 'Taurus', 'Близнецы': 'Gemini',
                    'Рак': 'Cancer', 'Лев': 'Leo', 'Дева': 'Virgo',
                    'Весы': 'Libra', 'Скорпион': 'Scorpio', 'Стрелец': 'Sagittarius',
                    'Козерог': 'Capricorn', 'Водолей': 'Aquarius', 'Рыбы': 'Pisces'
                }

                # Extract D1 data from pre-calculated table
                for p_data in d1_planet_data:
                    planet_ru = p_data.get("Планета", "")
                    planet_key = ru_to_en_planets.get(planet_ru, planet_ru.upper())

                    # Parse sign and degrees from "Знак и Градусы"
                    sign_deg_str = p_data.get("Знак и Градусы", "")
                    parts = sign_deg_str.split()
                    if len(parts) >= 2:
                        sign_ru = parts[0]
                        degrees_str = parts[1].replace("°", "")
                        try:
                            degrees = float(degrees_str)
                        except ValueError:
                            degrees = 0.0
                        sign_en = ru_to_en_signs.get(sign_ru, sign_ru)
                    else:
                        sign_en = sign_deg_str
                        degrees = 0.0

                    # Parse nakshatra from "Накшатра-Пада"
                    nakshatra_pada = p_data.get("Накшатра-Пада", "")
                    nakshatra = nakshatra_pada.split("-")[0] if "-" in nakshatra_pada else nakshatra_pada

                    planets_data[planet_key] = {
                        'rasi': sign_en,
                        'rasi_degrees': round(degrees, 2),
                        'nakshatra': nakshatra,
                        'house': p_data.get("Дом"),
                        'navamsha': p_data.get("_navamsha")  # Already calculated with correct ayanamsa
                    }

                # Add D9 signs from pre-calculated D9 data (fallback if _navamsha not set)
                for p_data in d9_planet_data:
                    planet_ru = p_data.get("Планета", "")
                    planet_key = ru_to_en_planets.get(planet_ru, planet_ru.upper())
                    sign_ru = p_data.get("Знак и Градусы", "")
                    sign_en = ru_to_en_signs.get(sign_ru, sign_ru)
                    if planet_key in planets_data and not planets_data[planet_key].get('navamsha'):
                        planets_data[planet_key]['navamsha'] = sign_en

                # Get ascendants
                d1_ascendant = st.session_state.get('d1_ascendant_sign')
                d9_ascendant = st.session_state.get('d9_ascendant_sign')

                chart_data = {
                    'calculated_at': datetime.datetime.now().isoformat(),
                    'ayanamsa': selected_ayanamsa,
                    'input': serialize_profile_data(profile_input),
                    'ascendant': d1_ascendant,
                    'd9_ascendant': d9_ascendant,
                    'planets': planets_data,
                    'd1_display': st.session_state.get('d1_planet_data', []),
                    'd9_display': st.session_state.get('d9_planet_data', [])
                }

            profile_id = save_profile(
                display_name=name,
                gender=gender,
                birth_date=date_input,
                birth_time=time_input,
                birth_place=city,
                latitude=lat,
                longitude=lon,
                timezone=tz_str,
                chart_data=chart_data
            )
            st.success(f"Профиль '{name}' сохранен (ID: {profile_id})")
            st.rerun()

        except Exception as e:
            st.error(f"Ошибка сохранения: {e}")
            import traceback
            st.code(traceback.format_exc())

# --- MAIN DISPLAY ---
if st.session_state.get('calculated'):
    profile = st.session_state.get('current_profile', {})

    # Profile header
    if profile:
        st.subheader(f"Натальная карта: {profile.get('name', 'Unknown')}")
        st.caption(
            f"{profile.get('date')} {profile.get('time')} | "
            f"{profile.get('city')} ({profile.get('lat', 0):.2f}, {profile.get('lon', 0):.2f})"
        )

    # Get selected Varga from sidebar
    current_varga = selected_varga
    varga_name = VARGA_NAMES.get(current_varga, current_varga)

    # Select data based on Varga (universal logic for all 16 Vargas)
    # Note: D1 and D9 use lowercase keys (d1_, d9_) for backward compatibility
    varga_key_lower = current_varga.lower()  # d1, d2, d3, etc.
    varga_key_upper = current_varga.upper()  # D1, D2, D3, etc.

    # Try lowercase first (for D1, D9), then uppercase (for D2-D60)
    planet_data = st.session_state.get(f'{varga_key_lower}_planet_data',
                  st.session_state.get(f'{varga_key_upper}_planet_data', []))
    house_data = st.session_state.get(f'{varga_key_lower}_house_data',
                 st.session_state.get(f'{varga_key_upper}_house_data', []))
    ascendant_sign = st.session_state.get(f'{varga_key_lower}_ascendant_sign',
                     st.session_state.get(f'{varga_key_upper}_ascendant_sign'))

    # Show current Varga indicator
    st.info(f"**Текущая карта:** {varga_name}")

    # Show Ascendant prominently
    if ascendant_sign:
        if current_varga == "D1":
            st.success(f"**Лагна (Асцендент):** {translate_sign(ascendant_sign)}")
        else:
            st.success(f"**Лагна {varga_name}:** {translate_sign(ascendant_sign)}")

    # Main Tables (switch based on Varga selector)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Таблица 1: Данные о планете ({varga_name})")

        if planet_data:
            df = pd.DataFrame(planet_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Данные планет для {varga_name} не найдены")

    with col2:
        st.subheader(f"Таблица 2: Данные о доме ({varga_name})")

        if house_data:
            df = pd.DataFrame(house_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Данные домов для {varga_name} не найдены")

    # Summary section
    st.divider()
    st.subheader("Краткая сводка")

    d1_planet_data = st.session_state.get('d1_planet_data', [])
    d9_planet_data = st.session_state.get('d9_planet_data', [])

    if d1_planet_data:
        def find_planet_d1(rus_name):
            return next((p for p in d1_planet_data if p['Планета'] == rus_name), None)

        def find_planet_d9(rus_name):
            return next((p for p in d9_planet_data if p['Планета'] == rus_name), None)

        sun_d1 = find_planet_d1("Солнце")
        moon_d1 = find_planet_d1("Луна")
        sun_d9 = find_planet_d9("Солнце")
        moon_d9 = find_planet_d9("Луна")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            d1_asc = st.session_state.get('d1_ascendant_sign')
            if d1_asc:
                st.metric("Лагна D1", translate_sign(d1_asc))

        with col2:
            d9_asc = st.session_state.get('d9_ascendant_sign')
            if d9_asc:
                st.metric("Лагна D9", translate_sign(d9_asc))

        with col3:
            if sun_d1:
                sign = sun_d1['Знак и Градусы'].split()[0]
                d9_sign = sun_d9['Знак и Градусы'] if sun_d9 else "—"
                st.metric("Солнце D1/D9", f"{sign}", f"D9: {d9_sign}")

        with col4:
            if moon_d1:
                sign = moon_d1['Знак и Градусы'].split()[0]
                d9_sign = moon_d9['Знак и Градусы'] if moon_d9 else "—"
                st.metric("Луна D1/D9", f"{sign}", f"D9: {d9_sign}")

else:
    st.info("Введите данные рождения в боковой панели и нажмите 'Рассчитать'")

    # Show database status
    with st.expander("Статус системы"):
        if db_ok:
            st.success("База данных подключена (PostgreSQL)")
            try:
                profiles = get_all_profiles()
                st.info(f"Профилей в базе: {len(profiles)}")
            except:
                pass
        else:
            st.error(f"База данных недоступна: {db_error}")

        st.info("Астро-движок: jyotishganit (Python, True Chitrapaksha Ayanamsa)")
