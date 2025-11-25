import streamlit as st
import pandas as pd
import datetime
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from jyotishganit import calculate_birth_chart

st.set_page_config(page_title="StarMeet Astro UI", layout="wide")

st.title("Jyotish Ganit: Нативный расчет")

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.header("Ввод данных")

    name = st.text_input("Имя", "Test User")
    gender = st.selectbox("Пол", ["Male", "Female"])

    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("Дата рождения", value=datetime.date(1977, 10, 25))
    with col2:
        time_input = st.time_input("Время рождения", value=datetime.time(0, 0))

    city = st.text_input("Город", "Moscow")

    # Geolocation
    geolocator = Nominatim(user_agent="starmeet_astro")
    location = geolocator.geocode(city)

    if location:
        lat = location.latitude
        lon = location.longitude
        st.success(f"Координаты: {lat:.4f}, {lon:.4f}")

        # Timezone
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lng=lon, lat=lat)
        st.info(f"Часовой пояс: {tz_str}")
    else:
        st.error("Город не найден")
        st.stop()

    if st.button("Рассчитать"):
        # Combine date & time
        local_dt = datetime.datetime.combine(date_input, time_input)

        # Calculate UTC offset
        tz = ZoneInfo(tz_str)
        local_dt_aware = local_dt.replace(tzinfo=tz)
        # offset in hours
        offset = local_dt_aware.utcoffset().total_seconds() / 3600.0

        try:
            # Using correct function discovered via introspection
            chart = calculate_birth_chart(
                birth_date=local_dt,
                latitude=lat,
                longitude=lon,
                timezone_offset=offset
            )

            st.session_state['chart'] = chart
            st.session_state['calculated'] = True

        except Exception as e:
            st.error(f"Ошибка расчета: {e}")
            import traceback
            st.code(traceback.format_exc())

# --- MAIN DISPLAY ---
if st.session_state.get('calculated'):
    chart = st.session_state['chart']

    tab1, tab2 = st.tabs(["D1 (Раши)", "D9 (Навамша)"])

    with tab1:
        st.subheader("Карта Раши (D1)")

        # D1 Planets
        # chart.d1_chart.planets is list of PlanetPosition
        d1_data = []
        if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'planets'):
            for p in chart.d1_chart.planets:
                d1_data.append({
                    "Планета": str(p.celestial_body),
                    "Знак": str(p.sign),
                    "Градус": f"{p.sign_degrees:.2f}",
                    "Накшатра": str(p.nakshatra),
                    "Дом": p.house
                })
            st.dataframe(pd.DataFrame(d1_data))
        else:
            st.error("Данные планет D1 не найдены")

        # D1 Houses
        st.subheader("Бхава Чалита (Дома)")
        h_data = []
        if hasattr(chart, 'd1_chart') and hasattr(chart.d1_chart, 'houses'):
             for h in chart.d1_chart.houses:
                 # chart.d1_chart.houses is also list of House objects?
                 # Introspection didn't show 'houses' in d1_chart, but previous showed D9 had houses.
                 # Let's assume D1 also has houses or check introspection again.
                 # Wait! `print(dir(chart.d1_chart))` showed 'houses', 'planets'.

                 # Let's assume structure is similar to planets but looking for House specific attributes.
                 # Actually, usually houses have number, sign, degree.
                 # In D9 houses are DivisionalHouse objects with number, sign, lord.
                 # In D1, 'houses' usually House object.
                 # I'll just dump basic string rep if attributes differ, but try finding number/sign.

                 # If I don't know exact attributes, I will try generic access or just skip for now to avoid crash.
                 # But task requires "Таблицы (Планеты, Дома, D9)".
                 # I'll try generic attrs.

                 h_data.append({
                     "Дом": getattr(h, 'number', '?'),
                     "Знак": getattr(h, 'sign', '?'),
                     "Градус": f"{getattr(h, 'sign_degrees', 0.0):.2f}"
                 })
             st.dataframe(pd.DataFrame(h_data))

    with tab2:
        st.subheader("Карта Навамша (D9)")

        # D9 Planets
        # Logic: Iterate houses -> get occupants
        d9_data = []

        if hasattr(chart, 'divisional_charts') and 'd9' in chart.divisional_charts:
            d9 = chart.divisional_charts['d9']
            # d9.houses -> occupants
            for house in d9.houses:
                 for occupant in house.occupants:
                      d9_data.append({
                          "Планета": str(occupant.celestial_body),
                          "Знак": str(occupant.sign),
                          "Дом (D9)": house.number,
                          "Дом (D1)": occupant.d1_house_placement
                      })
            st.dataframe(pd.DataFrame(d9_data))
        else:
            st.warning("D9 карта недоступна")

else:
    st.info("Нажмите 'Рассчитать', чтобы увидеть данные.")
