"""
Birth Chart Response Model
Структура данных для результатов астрологических расчётов VedAstro
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class PlanetPosition(BaseModel):
    """Позиция планеты в натальной карте"""
    name: str = Field(..., description="Название планеты (Sun, Moon, Mars, etc.)")
    longitude: float = Field(..., description="Долгота в градусах (0-360)")
    zodiac_sign: str = Field(..., description="Знак зодиака (Aries, Taurus, etc.)")
    house: int = Field(..., ge=1, le=12, description="Дом гороскопа (1-12)")
    shadbala: Optional[float] = Field(None, description="Шадбала (планетарная сила)")
    is_retrograde: bool = Field(default=False, description="Ретроградность")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sun",
                "longitude": 123.45,
                "zodiac_sign": "Leo",
                "house": 10,
                "shadbala": 350.5,
                "is_retrograde": False
            }
        }


class HouseData(BaseModel):
    """Данные о доме гороскопа"""
    house_number: int = Field(..., ge=1, le=12, description="Номер дома (1-12)")
    sign: str = Field(..., description="Знак зодиака на куспиде")
    lord: str = Field(..., description="Управитель дома")
    longitude: float = Field(..., description="Долгота куспида в градусах")

    class Config:
        json_schema_extra = {
            "example": {
                "house_number": 1,
                "sign": "Aries",
                "lord": "Mars",
                "longitude": 15.30
            }
        }


class DasaPeriod(BaseModel):
    """Период Даша (планетарный период)"""
    planet: str = Field(..., description="Планета-управитель периода")
    start_date: str = Field(..., description="Дата начала (ISO format)")
    end_date: str = Field(..., description="Дата окончания (ISO format)")
    level: str = Field(default="Maha", description="Уровень даши (Maha, Antar, Pratyantar)")

    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Jupiter",
                "start_date": "2020-01-01",
                "end_date": "2036-01-01",
                "level": "Maha"
            }
        }


class BirthChartResponse(BaseModel):
    """
    Полная натальная карта с результатами расчётов VedAstro
    """
    person_name: str = Field(..., description="Имя человека")
    birth_datetime: str = Field(..., description="Дата и время рождения (ISO format)")
    location: Dict[str, Any] = Field(..., description="Локация рождения")

    # Основные данные
    planets: Dict[str, PlanetPosition] = Field(..., description="Позиции планет")
    houses: Dict[str, HouseData] = Field(..., description="Данные о домах")
    ascendant: str = Field(..., description="Асцендент (Лагна)")

    # Периоды
    current_dasa: DasaPeriod = Field(..., description="Текущий период Даша")
    dasa_periods: List[DasaPeriod] = Field(default_factory=list, description="Все периоды Даша")

    # Дополнительные данные
    ayanamsa: float = Field(..., description="Айянамша (прецессия)")
    nakshatra: Optional[str] = Field(None, description="Накшатра Луны")

    # Для LLM интерпретации
    llm_summary: Optional[str] = Field(
        None,
        description="Краткое резюме для LLM (key strengths, weaknesses, opportunities)"
    )

    # Метаданные
    calculation_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Время выполнения расчёта"
    )
    vedastro_version: Optional[str] = Field(None, description="Версия VedAstro")

    class Config:
        json_schema_extra = {
            "example": {
                "person_name": "John Doe",
                "birth_datetime": "1990-01-15T14:30:00+05:30",
                "location": {
                    "name": "New Delhi, India",
                    "latitude": 28.7041,
                    "longitude": 77.1025,
                    "timezone": 5.5
                },
                "planets": {
                    "Sun": {
                        "name": "Sun",
                        "longitude": 270.5,
                        "zodiac_sign": "Capricorn",
                        "house": 10,
                        "shadbala": 420.3,
                        "is_retrograde": False
                    }
                },
                "houses": {
                    "House1": {
                        "house_number": 1,
                        "sign": "Aries",
                        "lord": "Mars",
                        "longitude": 15.30
                    }
                },
                "ascendant": "Aries",
                "current_dasa": {
                    "planet": "Jupiter",
                    "start_date": "2020-01-01",
                    "end_date": "2036-01-01",
                    "level": "Maha"
                },
                "dasa_periods": [],
                "ayanamsa": 24.15,
                "nakshatra": "Rohini",
                "llm_summary": "Strong 10th house Sun indicates leadership potential. Jupiter Dasa brings growth opportunities.",
                "calculation_timestamp": "2025-11-08T12:00:00Z",
                "vedastro_version": "1.23.19"
            }
        }


class ScoreBreakdown(BaseModel):
    """
    Детализация скоринга по критериям
    """
    criterion_name: str = Field(..., description="Название критерия")
    score: float = Field(..., ge=0, le=10, description="Балл по критерию (0-10)")
    weight: float = Field(..., ge=0, le=1, description="Вес критерия (0-1)")
    explanation: str = Field(..., description="Объяснение оценки")

    class Config:
        json_schema_extra = {
            "example": {
                "criterion_name": "2nd_house_strength",
                "score": 8.5,
                "weight": 0.15,
                "explanation": "Strong 2nd house lord in own sign indicates wealth potential"
            }
        }
