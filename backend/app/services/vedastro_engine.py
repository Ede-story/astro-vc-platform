"""
VedAstro Engine - обёртка над библиотекой VedAstro
Предоставляет высокоуровневые функции для астрологических расчётов
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import redis
import json

try:
    import vedastro as va
    VEDASTRO_AVAILABLE = True
    VEDASTRO_VERSION = getattr(va, '__version__', '1.23.19')
except ImportError:
    VEDASTRO_AVAILABLE = False
    VEDASTRO_VERSION = None
    logging.warning("VedAstro library not available. Install with: pip install vedastro")

from app.models.birth_chart import (
    BirthChartResponse,
    PlanetPosition,
    HouseData,
    DasaPeriod,
)
from app.models.birth_data import BirthData


logger = logging.getLogger(__name__)


class VedAstroEngine:
    """
    Движок астрологических расчётов на основе VedAstro
    """

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, cache_ttl: int = 86400):
        """
        Args:
            redis_host: Хост Redis для кэширования
            redis_port: Порт Redis
            cache_ttl: Время жизни кэша в секундах (по умолчанию 24 часа)
        """
        self.cache_ttl = cache_ttl

        # Подключение к Redis
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()
            self.redis_available = True
            logger.info(f"Redis connected: {redis_host}:{redis_port}")
        except Exception as e:
            self.redis_available = False
            self.redis_client = None
            logger.warning(f"Redis unavailable: {e}. Caching disabled.")

    def _get_cache_key(self, birth_data: BirthData) -> str:
        """Генерация уникального ключа для кэша"""
        key_parts = [
            birth_data.name.replace(" ", "_"),
            birth_data.date.isoformat(),
            birth_data.time.isoformat(),
            str(birth_data.latitude),
            str(birth_data.longitude),
            str(birth_data.timezone),
        ]
        return f"birth_chart:{'_'.join(key_parts)}"

    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Получить данные из кэша"""
        if not self.redis_available:
            return None

        try:
            cached = self.redis_client.get(key)
            if cached:
                logger.info(f"Cache HIT: {key}")
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Cache read error: {e}")

        return None

    def _save_to_cache(self, key: str, data: Dict) -> None:
        """Сохранить данные в кэш"""
        if not self.redis_available:
            return

        try:
            self.redis_client.setex(
                key,
                self.cache_ttl,
                json.dumps(data)
            )
            logger.info(f"Cache SAVE: {key} (TTL: {self.cache_ttl}s)")
        except Exception as e:
            logger.error(f"Cache write error: {e}")

    def calculate_birth_chart(self, birth_data: BirthData) -> BirthChartResponse:
        """
        Основная функция: расчёт натальной карты

        Args:
            birth_data: Данные о рождении (дата, время, место)

        Returns:
            BirthChartResponse: Полная натальная карта

        Raises:
            ValueError: Если VedAstro недоступен или данные некорректны
        """
        if not VEDASTRO_AVAILABLE:
            raise ValueError("VedAstro library is not installed")

        # Проверка кэша
        cache_key = self._get_cache_key(birth_data)
        cached_chart = self._get_from_cache(cache_key)
        if cached_chart:
            return BirthChartResponse(**cached_chart)

        logger.info(f"Calculating birth chart for: {birth_data.name}")

        try:
            # 1. Создание VedAstro Time object
            vedastro_time = self._create_vedastro_time(birth_data)

            # 2. Расчёт позиций планет
            planets = self._calculate_planets(vedastro_time)

            # 3. Расчёт домов
            houses = self._calculate_houses(vedastro_time)

            # 4. Расчёт Даша периодов
            current_dasa, dasa_periods = self._calculate_dasa_periods(vedastro_time)

            # 5. Дополнительные данные
            ayanamsa = self._calculate_ayanamsa(vedastro_time)
            nakshatra = self._calculate_moon_nakshatra(vedastro_time)
            ascendant = self._calculate_ascendant(vedastro_time)

            # 6. LLM резюме
            llm_summary = self._generate_llm_summary(planets, houses, current_dasa)

            # 7. Формирование ответа
            chart_response = BirthChartResponse(
                person_name=birth_data.name,
                birth_datetime=self._format_birth_datetime(birth_data),
                location={
                    "name": f"{birth_data.latitude}, {birth_data.longitude}",
                    "latitude": birth_data.latitude,
                    "longitude": birth_data.longitude,
                    "timezone": birth_data.timezone,
                },
                planets=planets,
                houses=houses,
                ascendant=ascendant,
                current_dasa=current_dasa,
                dasa_periods=dasa_periods,
                ayanamsa=ayanamsa,
                nakshatra=nakshatra,
                llm_summary=llm_summary,
                vedastro_version=VEDASTRO_VERSION,
            )

            # 8. Сохранение в кэш
            self._save_to_cache(cache_key, chart_response.dict())

            return chart_response

        except Exception as e:
            logger.error(f"Birth chart calculation failed: {e}")
            raise ValueError(f"Calculation error: {str(e)}")

    def _create_vedastro_time(self, birth_data: BirthData) -> 'va.Time':
        """Создать VedAstro Time object из BirthData"""
        # Создание геолокации
        location = va.GeoLocation(
            f"{birth_data.latitude},{birth_data.longitude}",
            birth_data.longitude,
            birth_data.latitude
        )

        # Форматирование времени для VedAstro: "HH:MM DD/MM/YYYY +TZ:00"
        time_str = birth_data.time.strftime("%H:%M")
        date_str = birth_data.date.strftime("%d/%m/%Y")
        tz_hours = int(birth_data.timezone)
        tz_minutes = int((birth_data.timezone - tz_hours) * 60)
        tz_str = f"{tz_hours:+03d}:{abs(tz_minutes):02d}"

        full_time_str = f"{time_str} {date_str} {tz_str}"

        logger.debug(f"VedAstro time string: {full_time_str}")

        return va.Time(full_time_str, location)

    def _calculate_planets(self, time: 'va.Time') -> Dict[str, PlanetPosition]:
        """Расчёт позиций всех планет"""
        planets_data = {}

        planet_names = [
            va.PlanetName.Sun,
            va.PlanetName.Moon,
            va.PlanetName.Mars,
            va.PlanetName.Mercury,
            va.PlanetName.Jupiter,
            va.PlanetName.Venus,
            va.PlanetName.Saturn,
            va.PlanetName.Rahu,
            va.PlanetName.Ketu,
        ]

        for planet_name in planet_names:
            try:
                # Получение всех данных планеты
                planet_longitude = va.Calculate.PlanetNirayanaLongitude(planet_name, time)
                zodiac_sign = va.Calculate.PlanetZodiacSign(planet_name, time)
                house = va.Calculate.HousePlanetIsIn(planet_name, time)

                # Shadbala (планетарная сила) - опционально
                try:
                    shadbala = va.Calculate.PlanetShadbala(planet_name, time)
                    shadbala_value = float(shadbala.ToString()) if hasattr(shadbala, 'ToString') else None
                except:
                    shadbala_value = None

                # Ретроградность
                try:
                    is_retrograde = va.Calculate.IsPlanetRetrograde(planet_name, time)
                except:
                    is_retrograde = False

                planets_data[planet_name.ToString()] = PlanetPosition(
                    name=planet_name.ToString(),
                    longitude=float(planet_longitude.TotalDegrees),
                    zodiac_sign=zodiac_sign.ToString(),
                    house=int(house.ToString()),
                    shadbala=shadbala_value,
                    is_retrograde=is_retrograde,
                )

            except Exception as e:
                logger.warning(f"Failed to calculate {planet_name}: {e}")

        return planets_data

    def _calculate_houses(self, time: 'va.Time') -> Dict[str, HouseData]:
        """Расчёт данных о домах"""
        houses_data = {}

        for house_number in range(1, 13):
            try:
                house_name = getattr(va.HouseName, f"House{house_number}")

                sign = va.Calculate.HouseSignName(house_name, time)
                sign_lord = va.Calculate.LordOfZodiacSign(sign, time)
                cusp_longitude = va.Calculate.HouseLongitude(house_name, time)

                houses_data[f"House{house_number}"] = HouseData(
                    house_number=house_number,
                    sign=sign.ToString(),
                    lord=sign_lord.ToString(),
                    longitude=float(cusp_longitude.TotalDegrees),
                )

            except Exception as e:
                logger.warning(f"Failed to calculate House {house_number}: {e}")

        return houses_data

    def _calculate_dasa_periods(self, time: 'va.Time') -> tuple:
        """Расчёт периодов Даша"""
        try:
            # Текущий Maha Dasa
            current_dasa_planet = va.Calculate.CurrentDasa8Levels(time).PD1

            # Упрощённая реализация: только текущий период
            current_dasa = DasaPeriod(
                planet=current_dasa_planet.ToString(),
                start_date=datetime.now().isoformat(),  # Placeholder
                end_date=(datetime.now().replace(year=datetime.now().year + 10)).isoformat(),
                level="Maha",
            )

            # TODO: Реализовать полный расчёт всех периодов Даша
            dasa_periods = [current_dasa]

            return current_dasa, dasa_periods

        except Exception as e:
            logger.warning(f"Dasa calculation failed: {e}")
            # Fallback
            current_dasa = DasaPeriod(
                planet="Unknown",
                start_date=datetime.now().isoformat(),
                end_date=datetime.now().isoformat(),
                level="Maha",
            )
            return current_dasa, [current_dasa]

    def _calculate_ayanamsa(self, time: 'va.Time') -> float:
        """Расчёт Айянамши (прецессия)"""
        try:
            ayanamsa = va.Calculate.Ayanamsa(time)
            return float(ayanamsa.TotalDegrees)
        except:
            return 24.15  # Default Lahiri ayanamsa (approximate)

    def _calculate_moon_nakshatra(self, time: 'va.Time') -> str:
        """Расчёт Накшатры Луны"""
        try:
            nakshatra = va.Calculate.PlanetConstellation(va.PlanetName.Moon, time)
            return nakshatra.ToString()
        except:
            return "Unknown"

    def _calculate_ascendant(self, time: 'va.Time') -> str:
        """Расчёт Асцендента (Лагна)"""
        try:
            asc_sign = va.Calculate.HouseSignName(va.HouseName.House1, time)
            return asc_sign.ToString()
        except:
            return "Unknown"

    def _format_birth_datetime(self, birth_data: BirthData) -> str:
        """Форматирование даты и времени рождения в ISO формат"""
        dt = datetime.combine(birth_data.date, birth_data.time)
        return dt.isoformat()

    def _generate_llm_summary(
        self,
        planets: Dict[str, PlanetPosition],
        houses: Dict[str, HouseData],
        current_dasa: DasaPeriod,
    ) -> str:
        """
        Генерация краткого резюме для LLM интерпретации

        Выделяет ключевые сильные и слабые стороны карты
        """
        summary_parts = []

        # Солнце (власть, лидерство)
        if "Sun" in planets:
            sun = planets["Sun"]
            summary_parts.append(
                f"Sun in {sun.zodiac_sign}, House {sun.house} - leadership potential"
            )

        # Луна (эмоции, ум)
        if "Moon" in planets:
            moon = planets["Moon"]
            summary_parts.append(f"Moon in {moon.zodiac_sign} - emotional nature")

        # 10 дом (карьера)
        if "House10" in houses:
            house10 = houses["House10"]
            summary_parts.append(f"10th house in {house10.sign} (career) ruled by {house10.lord}")

        # Текущий Даша период
        summary_parts.append(f"Current Dasa: {current_dasa.planet}")

        return ". ".join(summary_parts)


# Singleton instance для использования в endpoints
_vedastro_engine: Optional[VedAstroEngine] = None


def get_vedastro_engine() -> VedAstroEngine:
    """Получить singleton instance VedAstroEngine"""
    global _vedastro_engine
    if _vedastro_engine is None:
        _vedastro_engine = VedAstroEngine(
            redis_host="redis",  # Docker service name
            redis_port=6379,
            cache_ttl=86400,  # 24 hours
        )
    return _vedastro_engine
