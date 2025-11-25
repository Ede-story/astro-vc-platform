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
    st.sidebar.error(f"⚠️ БД недоступна: {db_error}")
    st.sidebar.info("Данные будут храниться в памяти сессии")

st.title("🌟 StarMeet: Ведическая Астрология")

# --- SIDEBAR: SAVED PROFILES ---
with st.sidebar:
    st.header("📁 Сохраненные профили")

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
            if st.button("📂 Загрузить профиль"):
                profile_data = get_profile_by_name(selected_profile)
                if profile_data:
                    st.session_state['loaded_profile'] = profile_data
                    st.success(f"Загружен: {selected_profile}")
                    st.rerun()

            if st.button("🗑️ Удалить профиль"):
                if delete_profile(selected_profile):
                    st.success(f"Удален: {selected_profile}")
                    st.rerun()
    else:
        st.info("Нет сохраненных профилей")

    st.divider()

# --- SIDEBAR: INPUT FORM ---
with st.sidebar:
    st.header("✏️ Ввод данных")

    # Pre-fill from loaded profile
    loaded = st.session_state.get('loaded_profile', {})

    name = st.text_input("Имя", value=loaded.get('display_name', ""))
    gender = st.selectbox(
        "Пол",
        ["Мужской", "Женский"],
        index=0 if loaded.get('gender') != 'Женский' else 1
    )

    col1, col2 = st.columns(2)
    with col1:
        default_date = loaded.get('birth_date', datetime.date(1990, 1, 1))
        if isinstance(default_date, str):
            default_date = datetime.datetime.strptime(default_date, '%Y-%m-%d').date()
        date_input = st.date_input("Дата рождения", value=default_date)

    with col2:
        default_time = loaded.get('birth_time', datetime.time(12, 0))
        if isinstance(default_time, str):
            default_time = datetime.datetime.strptime(default_time, '%H:%M:%S').time()
        time_input = st.time_input("Время рождения", value=default_time)

    city = st.text_input("Город рождения", value=loaded.get('birth_place', ""))

    # Geolocation
    lat, lon, tz_str = None, None, None
    if city:
        geolocator = Nominatim(user_agent="starmeet_astro")
        location = geolocator.geocode(city)

        if location:
            lat = location.latitude
            lon = location.longitude
            st.success(f"📍 {lat:.4f}, {lon:.4f}")

            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lng=lon, lat=lat)
            st.info(f"🕐 {tz_str}")
        else:
            st.warning("Город не найден. Введите корректное название.")

    st.divider()

    # Action buttons
    col_calc, col_save = st.columns(2)

    with col_calc:
        calculate_btn = st.button("🔮 Рассчитать", type="primary", disabled=not (lat and lon))

    with col_save:
        save_btn = st.button("💾 Сохранить", disabled=not (name and lat and lon and db_ok))

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
                'date': date_input.isoformat(),  # Store as string
                'time': time_input.isoformat(),  # Store as string
                'city': city,
                'lat': lat,
                'lon': lon,
                'tz': tz_str
            }

            # Pre-calculate D1 data for caching
            d1_data = []
            if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'planets'):
                for p in chart.d1_chart.planets:
                    d1_data.append({
                        "Планета": str(p.celestial_body),
                        "Знак": str(p.sign),
                        "Градус": f"{p.sign_degrees:.2f}°",
                        "Накшатра": str(p.nakshatra),
                        "Дом": p.house
                    })
            st.session_state['d1_data'] = d1_data

            # Pre-calculate houses data
            houses_data = []
            if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'houses'):
                for h in chart.d1_chart.houses:
                    deg = getattr(h, 'sign_degrees', None)
                    houses_data.append({
                        "Дом": h.number,
                        "Знак": str(h.sign),
                        "Градус": f"{deg:.2f}°" if deg is not None else "—",
                        "Управитель": str(getattr(h, 'lord', '—'))
                    })
            st.session_state['houses_data'] = houses_data

            # Pre-calculate D9 data
            d9_data = []
            if hasattr(chart, 'divisional_charts') and 'd9' in chart.divisional_charts:
                d9 = chart.divisional_charts['d9']
                for house in d9.houses:
                    for occupant in house.occupants:
                        d9_data.append({
                            "Планета": str(occupant.celestial_body),
                            "Знак (D9)": str(occupant.sign),
                            "Дом (D9)": house.number,
                            "Дом (D1)": getattr(occupant, 'd1_house_placement', '—')
                        })
            st.session_state['d9_data'] = d9_data

            st.success("✅ Расчет выполнен!")

        except Exception as e:
            st.error(f"Ошибка расчета: {e}")
            import traceback
            st.code(traceback.format_exc())

    # Handle Save
    if save_btn and name and db_ok:
        try:
            # Prepare chart data for storage (serialize dates)
            chart_data = None
            if st.session_state.get('chart'):
                profile_input = st.session_state.get('current_profile', {})
                chart_data = {
                    'calculated_at': datetime.datetime.now().isoformat(),
                    'input': serialize_profile_data(profile_input),
                    'd1_planets': st.session_state.get('d1_data', [])
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
            st.success(f"✅ Профиль '{name}' сохранен (ID: {profile_id})")
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
        st.subheader(f"📊 Натальная карта: {profile.get('name', 'Unknown')}")
        st.caption(
            f"{profile.get('date')} {profile.get('time')} • "
            f"{profile.get('city')} ({profile.get('lat', 0):.2f}, {profile.get('lon', 0):.2f})"
        )

    # Get cached data from session state
    d1_data = st.session_state.get('d1_data', [])
    houses_data = st.session_state.get('houses_data', [])
    d9_data = st.session_state.get('d9_data', [])

    # Show Ascendant prominently
    if houses_data:
        asc = houses_data[0]  # House 1 = Ascendant
        st.info(f"⬆️ **Лагна (Асцендент):** {asc['Знак']} {asc['Градус']}")

    tab1, tab2, tab3, tab4 = st.tabs(["🌙 Планеты (D1)", "🏠 Дома (Бхавы)", "💎 Навамша (D9)", "📋 Сводка"])

    with tab1:
        st.subheader("Планеты в знаках (Раши)")

        if d1_data:
            df = pd.DataFrame(d1_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Highlight Ketu
            ketu_row = next((p for p in d1_data if 'Ketu' in p['Планета']), None)
            if ketu_row:
                st.success(f"🔮 **Кету:** {ketu_row['Знак']} ({ketu_row['Градус']}) — Дом {ketu_row['Дом']}")
        else:
            st.warning("Данные планет не найдены")

    with tab2:
        st.subheader("Бхавы (Дома)")

        if houses_data:
            df = pd.DataFrame(houses_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("Данные домов не найдены")

    with tab3:
        st.subheader("Карта Навамша (D9)")

        if d9_data:
            df = pd.DataFrame(d9_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("D9 карта недоступна")

    with tab4:
        st.subheader("📋 Краткая сводка")

        if d1_data:
            # Find key planets
            sun_data = next((p for p in d1_data if 'Sun' in p['Планета']), None)
            moon_data = next((p for p in d1_data if 'Moon' in p['Планета']), None)
            mars_data = next((p for p in d1_data if 'Mars' in p['Планета']), None)
            ketu_data = next((p for p in d1_data if 'Ketu' in p['Планета']), None)
            rahu_data = next((p for p in d1_data if 'Rahu' in p['Планета']), None)

            col1, col2, col3 = st.columns(3)

            with col1:
                if houses_data:
                    st.metric("⬆️ Лагна", houses_data[0]['Знак'])
                if sun_data:
                    st.metric("☀️ Солнце", sun_data['Знак'], f"Дом {sun_data['Дом']}")

            with col2:
                if moon_data:
                    st.metric("🌙 Луна", moon_data['Знак'], f"Дом {moon_data['Дом']}")
                if mars_data:
                    st.metric("♂️ Марс", mars_data['Знак'], f"Дом {mars_data['Дом']}")

            with col3:
                if rahu_data:
                    st.metric("☊ Раху", rahu_data['Знак'], f"Дом {rahu_data['Дом']}")
                if ketu_data:
                    st.metric("☋ Кету", ketu_data['Знак'], f"Дом {ketu_data['Дом']}")

else:
    st.info("👈 Введите данные рождения и нажмите 'Рассчитать'")

    # Show database status
    with st.expander("🔧 Статус системы"):
        if db_ok:
            st.success("✅ База данных подключена (PostgreSQL)")
            try:
                profiles = get_all_profiles()
                st.info(f"📊 Профилей в базе: {len(profiles)}")
            except:
                pass
        else:
            st.error(f"❌ База данных недоступна: {db_error}")

        st.info("📐 Астро-движок: jyotishganit (Python, Sidereal/Lahiri)")
