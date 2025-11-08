"""
Unit Tests for VedAstro Engine
Тестирование астрологических расчётов
"""

import pytest
from datetime import date, time
from app.services.vedastro_engine import VedAstroEngine, VEDASTRO_AVAILABLE
from app.models.birth_data import BirthData


# Skip tests if VedAstro not available
pytestmark = pytest.mark.skipif(
    not VEDASTRO_AVAILABLE,
    reason="VedAstro library not installed"
)


@pytest.fixture
def engine():
    """Fixture: VedAstro Engine instance (без Redis для тестов)"""
    return VedAstroEngine(redis_host="localhost", redis_port=9999, cache_ttl=60)


@pytest.fixture
def test_birth_data():
    """Fixture: Тестовые данные рождения (Steve Jobs)"""
    return BirthData(
        name="Steve Jobs",
        date=date(1955, 2, 24),
        time=time(19, 15, 0),
        latitude=37.77,
        longitude=-122.42,
        timezone=-8.0,
        gender="Male"
    )


@pytest.fixture
def test_birth_data_2():
    """Fixture: Тестовые данные 2 (Elon Musk)"""
    return BirthData(
        name="Elon Musk",
        date=date(1971, 6, 28),
        time=time(7, 30, 0),
        latitude=-25.75,
        longitude=28.19,
        timezone=2.0,
        gender="Male"
    )


class TestVedAstroEngine:
    """Тесты для VedAstro Engine"""

    def test_engine_initialization(self, engine):
        """Тест: Инициализация движка"""
        assert engine is not None
        assert engine.cache_ttl == 60
        # Redis недоступен на порту 9999, должно быть False
        assert engine.redis_available is False

    def test_cache_key_generation(self, engine, test_birth_data):
        """Тест: Генерация уникального ключа кэша"""
        key = engine._get_cache_key(test_birth_data)

        assert isinstance(key, str)
        assert "birth_chart:" in key
        assert "Steve_Jobs" in key
        assert "1955-02-24" in key

    def test_create_vedastro_time(self, engine, test_birth_data):
        """Тест: Создание VedAstro Time object"""
        vedastro_time = engine._create_vedastro_time(test_birth_data)

        assert vedastro_time is not None
        # Проверка что объект создан корректно (есть атрибуты VedAstro)
        assert hasattr(vedastro_time, 'GetLmtDateTimeOffset')

    def test_calculate_birth_chart(self, engine, test_birth_data):
        """Тест: Расчёт полной натальной карты"""
        chart = engine.calculate_birth_chart(test_birth_data)

        assert chart is not None
        assert chart.person_name == "Steve Jobs"

        # Проверка планет
        assert "Sun" in chart.planets
        assert "Moon" in chart.planets
        assert "Mars" in chart.planets
        assert "Mercury" in chart.planets
        assert "Jupiter" in chart.planets

        # Проверка домов
        assert "House1" in chart.houses
        assert "House10" in chart.houses

        # Проверка асцендента
        assert chart.ascendant is not None
        assert len(chart.ascendant) > 0

        # Проверка текущего Даша
        assert chart.current_dasa is not None
        assert chart.current_dasa.planet is not None

    def test_calculate_planets(self, engine, test_birth_data):
        """Тест: Расчёт позиций планет"""
        vedastro_time = engine._create_vedastro_time(test_birth_data)
        planets = engine._calculate_planets(vedastro_time)

        assert len(planets) > 0

        # Проверка Солнца
        assert "Sun" in planets
        sun = planets["Sun"]
        assert sun.name == "Sun"
        assert 0 <= sun.longitude <= 360
        assert 1 <= sun.house <= 12
        assert sun.zodiac_sign in [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

    def test_calculate_houses(self, engine, test_birth_data):
        """Тест: Расчёт домов гороскопа"""
        vedastro_time = engine._create_vedastro_time(test_birth_data)
        houses = engine._calculate_houses(vedastro_time)

        assert len(houses) == 12

        # Проверка 1-го дома (Асцендент)
        assert "House1" in houses
        house1 = houses["House1"]
        assert house1.house_number == 1
        assert house1.sign is not None
        assert house1.lord is not None

    def test_calculate_ayanamsa(self, engine, test_birth_data):
        """Тест: Расчёт Айянамши"""
        vedastro_time = engine._create_vedastro_time(test_birth_data)
        ayanamsa = engine._calculate_ayanamsa(vedastro_time)

        # Айянамша должна быть в разумных пределах (примерно 20-25 градусов в 20-21 веке)
        assert 15.0 <= ayanamsa <= 30.0

    def test_calculate_moon_nakshatra(self, engine, test_birth_data):
        """Тест: Расчёт Накшатры Луны"""
        vedastro_time = engine._create_vedastro_time(test_birth_data)
        nakshatra = engine._calculate_moon_nakshatra(vedastro_time)

        assert nakshatra is not None
        assert len(nakshatra) > 0
        # Накшатра должна быть одной из 27
        # (не проверяем конкретное имя, так как могут быть разные варианты написания)

    def test_llm_summary_generation(self, engine):
        """Тест: Генерация LLM резюме"""
        from app.models.birth_chart import PlanetPosition, HouseData, DasaPeriod

        # Mock данные
        planets = {
            "Sun": PlanetPosition(
                name="Sun",
                longitude=150.5,
                zodiac_sign="Leo",
                house=10,
                shadbala=400.0,
                is_retrograde=False
            ),
            "Moon": PlanetPosition(
                name="Moon",
                longitude=250.0,
                zodiac_sign="Sagittarius",
                house=4,
                shadbala=350.0,
                is_retrograde=False
            )
        }

        houses = {
            "House10": HouseData(
                house_number=10,
                sign="Leo",
                lord="Sun",
                longitude=150.0
            )
        }

        current_dasa = DasaPeriod(
            planet="Jupiter",
            start_date="2020-01-01",
            end_date="2036-01-01",
            level="Maha"
        )

        summary = engine._generate_llm_summary(planets, houses, current_dasa)

        assert summary is not None
        assert len(summary) > 0
        assert "Sun" in summary
        assert "Jupiter" in summary

    def test_chart_caching_disabled(self, engine, test_birth_data):
        """Тест: Проверка что кэширование корректно отключается при отсутствии Redis"""
        # Redis на порту 9999 недоступен
        assert engine.redis_available is False

        # Расчёт должен работать и без кэша
        chart = engine.calculate_birth_chart(test_birth_data)
        assert chart is not None
        assert chart.person_name == "Steve Jobs"

    def test_multiple_calculations(self, engine, test_birth_data, test_birth_data_2):
        """Тест: Множественные расчёты (тестируем стабильность)"""
        chart1 = engine.calculate_birth_chart(test_birth_data)
        chart2 = engine.calculate_birth_chart(test_birth_data_2)

        assert chart1.person_name == "Steve Jobs"
        assert chart2.person_name == "Elon Musk"

        # Карты должны отличаться
        assert chart1.ascendant != chart2.ascendant or \
               chart1.planets["Sun"].zodiac_sign != chart2.planets["Sun"].zodiac_sign


class TestVedAstroEngineSingleton:
    """Тесты для singleton паттерна VedAstro Engine"""

    def test_get_vedastro_engine_singleton(self):
        """Тест: Проверка что get_vedastro_engine возвращает один и тот же instance"""
        from app.services.vedastro_engine import get_vedastro_engine

        engine1 = get_vedastro_engine()
        engine2 = get_vedastro_engine()

        # Должен быть один и тот же объект
        assert engine1 is engine2


# ============= INTEGRATION TESTS (требуют Docker Redis) =============

@pytest.mark.integration
class TestVedAstroEngineWithRedis:
    """Integration тесты с Redis (требуют docker-compose up)"""

    @pytest.fixture
    def engine_with_redis(self):
        """Fixture: Engine с реальным Redis (docker-compose должен быть запущен)"""
        return VedAstroEngine(redis_host="localhost", redis_port=6379, cache_ttl=10)

    def test_caching_works(self, engine_with_redis, test_birth_data):
        """Тест: Проверка что кэширование работает"""
        import time

        if not engine_with_redis.redis_available:
            pytest.skip("Redis не доступен (запустите docker-compose up)")

        # Первый расчёт - пойдёт в кэш
        chart1 = engine_with_redis.calculate_birth_chart(test_birth_data)

        # Второй расчёт - должен взяться из кэша (быстрее)
        start = time.time()
        chart2 = engine_with_redis.calculate_birth_chart(test_birth_data)
        cache_time = time.time() - start

        # Данные должны совпадать
        assert chart1.person_name == chart2.person_name
        assert chart1.ascendant == chart2.ascendant

        # Cache hit должен быть быстрым (< 0.1 секунды)
        assert cache_time < 0.1
