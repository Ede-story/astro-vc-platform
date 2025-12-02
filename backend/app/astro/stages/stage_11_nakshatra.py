"""
Stage 11: Nakshatra Deep Dive

Analyzes the nakshatra positions of Sun, Moon, and Lagna to determine
personality archetype based on Gana (temperament) combinations.

Key concepts:
- Gana Types: Deva (divine), Manushya (human), Rakshasa (demonic)
- 27 Nakshatras grouped into 9 Deva, 9 Manushya, 9 Rakshasa
- Personality Archetype from Sun-Moon-Lagna gana combination
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from ..models.types import (
    Planet, GanaType, PersonalityArchetype, Nakshatra, NakshatraPada
)
from ..reference.nakshatras import (
    NAKSHATRA_CATALOG,
    NakshatraData,
    get_nakshatra_from_degree,
    get_nakshatra_pada
)


# =============================================================================
# GANA COMBINATION TO ARCHETYPE MAPPING
# =============================================================================

GANA_ARCHETYPE_MAP: Dict[Tuple[GanaType, GanaType, GanaType], PersonalityArchetype] = {
    # Pure combinations
    (GanaType.DEVA, GanaType.DEVA, GanaType.DEVA): PersonalityArchetype.LIGHT_BEARER,
    (GanaType.MANUSHYA, GanaType.MANUSHYA, GanaType.MANUSHYA): PersonalityArchetype.WORLD_BUILDER,
    (GanaType.RAKSHASA, GanaType.RAKSHASA, GanaType.RAKSHASA): PersonalityArchetype.TRANSFORMER,

    # Deva-dominant combinations
    (GanaType.DEVA, GanaType.DEVA, GanaType.MANUSHYA): PersonalityArchetype.NOBLE_PRACTITIONER,
    (GanaType.DEVA, GanaType.MANUSHYA, GanaType.DEVA): PersonalityArchetype.HARMONIZER,
    (GanaType.MANUSHYA, GanaType.DEVA, GanaType.DEVA): PersonalityArchetype.PRACTICAL_IDEALIST,
    (GanaType.DEVA, GanaType.DEVA, GanaType.RAKSHASA): PersonalityArchetype.WISE_DESTROYER,
    (GanaType.DEVA, GanaType.RAKSHASA, GanaType.DEVA): PersonalityArchetype.DIVINE_TRANSFORMER,
    (GanaType.RAKSHASA, GanaType.DEVA, GanaType.DEVA): PersonalityArchetype.WISE_DESTROYER,

    # Manushya-dominant combinations
    (GanaType.DEVA, GanaType.MANUSHYA, GanaType.MANUSHYA): PersonalityArchetype.PRACTICAL_IDEALIST,
    (GanaType.MANUSHYA, GanaType.DEVA, GanaType.MANUSHYA): PersonalityArchetype.NOBLE_PRACTITIONER,
    (GanaType.MANUSHYA, GanaType.MANUSHYA, GanaType.DEVA): PersonalityArchetype.HARMONIZER,
    (GanaType.MANUSHYA, GanaType.MANUSHYA, GanaType.RAKSHASA): PersonalityArchetype.INTENSE_CREATOR,
    (GanaType.MANUSHYA, GanaType.RAKSHASA, GanaType.MANUSHYA): PersonalityArchetype.REFORMER,
    (GanaType.RAKSHASA, GanaType.MANUSHYA, GanaType.MANUSHYA): PersonalityArchetype.LIGHT_WARRIOR,

    # Rakshasa-dominant combinations
    (GanaType.RAKSHASA, GanaType.RAKSHASA, GanaType.DEVA): PersonalityArchetype.DIVINE_TRANSFORMER,
    (GanaType.RAKSHASA, GanaType.DEVA, GanaType.RAKSHASA): PersonalityArchetype.SPIRITUAL_WARRIOR,
    (GanaType.DEVA, GanaType.RAKSHASA, GanaType.RAKSHASA): PersonalityArchetype.INTENSE_CREATOR,
    (GanaType.RAKSHASA, GanaType.RAKSHASA, GanaType.MANUSHYA): PersonalityArchetype.REFORMER,
    (GanaType.RAKSHASA, GanaType.MANUSHYA, GanaType.RAKSHASA): PersonalityArchetype.LIGHT_WARRIOR,
    (GanaType.MANUSHYA, GanaType.RAKSHASA, GanaType.RAKSHASA): PersonalityArchetype.INTENSE_CREATOR,

    # Mixed combinations (one of each)
    (GanaType.DEVA, GanaType.MANUSHYA, GanaType.RAKSHASA): PersonalityArchetype.SPIRITUAL_WARRIOR,
    (GanaType.DEVA, GanaType.RAKSHASA, GanaType.MANUSHYA): PersonalityArchetype.SPIRITUAL_WARRIOR,
    (GanaType.MANUSHYA, GanaType.DEVA, GanaType.RAKSHASA): PersonalityArchetype.LIGHT_WARRIOR,
    (GanaType.MANUSHYA, GanaType.RAKSHASA, GanaType.DEVA): PersonalityArchetype.REFORMER,
    (GanaType.RAKSHASA, GanaType.DEVA, GanaType.MANUSHYA): PersonalityArchetype.LIGHT_WARRIOR,
    (GanaType.RAKSHASA, GanaType.MANUSHYA, GanaType.DEVA): PersonalityArchetype.REFORMER,
}


# =============================================================================
# ARCHETYPE DESCRIPTIONS
# =============================================================================

ARCHETYPE_DESCRIPTIONS: Dict[PersonalityArchetype, Dict[str, Any]] = {
    PersonalityArchetype.LIGHT_BEARER: {
        "title": "Светоносец",
        "subtitle": "Духовный лидер и проводник света",
        "description": "Чистая духовная природа. Излучает свет и мудрость. Естественный учитель и целитель.",
        "strengths": ["Духовная чистота", "Интуитивная мудрость", "Целительные способности", "Естественный авторитет"],
        "challenges": ["Оторванность от материального мира", "Наивность", "Трудности с земными делами"],
        "career_fit": ["Духовное лидерство", "Преподавание", "Целительство", "Консультирование"],
        "investment_profile": "Идеалист с долгосрочным видением. Может игнорировать практические аспекты.",
    },
    PersonalityArchetype.NOBLE_PRACTITIONER: {
        "title": "Благородный Практик",
        "subtitle": "Мост между небом и землёй",
        "description": "Сочетает духовные идеалы с практическим подходом. Способен воплощать возвышенные идеи в реальность.",
        "strengths": ["Практическая мудрость", "Этичность в бизнесе", "Способность вдохновлять", "Надёжность"],
        "challenges": ["Внутренний конфликт идеалов и реальности", "Перфекционизм"],
        "career_fit": ["Социальное предпринимательство", "Этичные инвестиции", "Образование", "Менеджмент"],
        "investment_profile": "Ищет баланс между прибылью и смыслом. Предпочитает устойчивое развитие.",
    },
    PersonalityArchetype.HARMONIZER: {
        "title": "Гармонизатор",
        "subtitle": "Творец баланса и красоты",
        "description": "Создаёт гармонию везде, где появляется. Прирождённый дипломат и эстет.",
        "strengths": ["Дипломатичность", "Эстетическое чутьё", "Умение примирять противоположности"],
        "challenges": ["Избегание конфликтов", "Сложность принятия жёстких решений"],
        "career_fit": ["Дизайн", "Дипломатия", "HR", "Искусство", "Медиация"],
        "investment_profile": "Предпочитает консенсус и партнёрства. Избегает агрессивных стратегий.",
    },
    PersonalityArchetype.WORLD_BUILDER: {
        "title": "Строитель Мира",
        "subtitle": "Архитектор материальной реальности",
        "description": "Практичный созидатель. Строит устойчивые структуры и системы. Надёжен и последователен.",
        "strengths": ["Практичность", "Организаторские способности", "Надёжность", "Системное мышление"],
        "challenges": ["Материализм", "Недостаток воображения", "Сопротивление переменам"],
        "career_fit": ["Строительство", "Бизнес", "Финансы", "Управление проектами"],
        "investment_profile": "Консервативный, надёжный исполнитель. Строит долгосрочно.",
    },
    PersonalityArchetype.TRANSFORMER: {
        "title": "Трансформатор",
        "subtitle": "Агент радикальных перемен",
        "description": "Мощная разрушительно-созидательная сила. Трансформирует устаревшие системы.",
        "strengths": ["Трансформационная сила", "Бесстрашие", "Интенсивность", "Проникновение в суть"],
        "challenges": ["Разрушительность", "Сложности в отношениях", "Экстремизм"],
        "career_fit": ["Кризисный менеджмент", "Реструктуризация", "Исследования", "Хирургия"],
        "investment_profile": "Высокий риск, высокая награда. Видит возможности там, где другие видят хаос.",
    },
    PersonalityArchetype.LIGHT_WARRIOR: {
        "title": "Воин Света",
        "subtitle": "Защитник истины и справедливости",
        "description": "Борец за правое дело. Использует силу для защиты высших ценностей.",
        "strengths": ["Храбрость", "Справедливость", "Защита слабых", "Лидерство в кризис"],
        "challenges": ["Агрессивность", "Нетерпимость", "Сложность с компромиссами"],
        "career_fit": ["Право", "Правозащита", "Армия/полиция", "Активизм", "Спорт"],
        "investment_profile": "Действует из принципов. Готов бороться за свои инвестиции.",
    },
    PersonalityArchetype.REFORMER: {
        "title": "Реформатор",
        "subtitle": "Эволюционный преобразователь систем",
        "description": "Меняет мир изнутри. Работает через существующие структуры для позитивных изменений.",
        "strengths": ["Стратегическое мышление", "Терпение", "Понимание систем", "Постепенность"],
        "challenges": ["Манипулятивность", "Медлительность", "Компромиссность"],
        "career_fit": ["Политика", "Корпоративные реформы", "Консалтинг", "Социальные изменения"],
        "investment_profile": "Долгосрочный стратег. Понимает как работают системы.",
    },
    PersonalityArchetype.SPIRITUAL_WARRIOR: {
        "title": "Духовный Воин",
        "subtitle": "Бескомпромиссный искатель истины",
        "description": "Сочетает духовную глубину с воинским духом. Защитник духовных ценностей.",
        "strengths": ["Духовная сила", "Бесстрашие", "Интенсивная практика", "Харизма"],
        "challenges": ["Фанатизм", "Нетерпимость к слабости", "Одиночество"],
        "career_fit": ["Духовное лидерство", "Экстремальные виды спорта", "Исследования", "Медицина"],
        "investment_profile": "Всё или ничего. Инвестирует во что верит полностью.",
    },
    PersonalityArchetype.WISE_DESTROYER: {
        "title": "Мудрый Разрушитель",
        "subtitle": "Устранитель иллюзий и заблуждений",
        "description": "Разрушает ложные конструкции с мудростью. Освобождает от иллюзий.",
        "strengths": ["Проницательность", "Разрушение иллюзий", "Глубокое понимание", "Освобождение"],
        "challenges": ["Цинизм", "Отчуждение", "Деструктивность без созидания"],
        "career_fit": ["Критика", "Аудит", "Журналистика", "Психотерапия", "Исследования"],
        "investment_profile": "Видит сквозь хайп. Хорош в выявлении переоценённых активов.",
    },
    PersonalityArchetype.PRACTICAL_IDEALIST: {
        "title": "Практичный Идеалист",
        "subtitle": "Воплотитель мечты в реальность",
        "description": "Мечтает с открытыми глазами. Умеет превращать идеалы в работающие решения.",
        "strengths": ["Реалистичный оптимизм", "Умение вдохновлять команду", "Практичное творчество"],
        "challenges": ["Внутренний конфликт", "Разочарование в людях"],
        "career_fit": ["Стартапы", "Социальное предпринимательство", "Инновации", "Образование"],
        "investment_profile": "Ищет проекты с миссией и потенциалом. Идеальный фаундер.",
    },
    PersonalityArchetype.INTENSE_CREATOR: {
        "title": "Интенсивный Созидатель",
        "subtitle": "Творец через трансформацию",
        "description": "Создаёт через разрушение и перестройку. Интенсивная творческая энергия.",
        "strengths": ["Творческая сила", "Интенсивность", "Оригинальность", "Глубина"],
        "challenges": ["Эмоциональная нестабильность", "Перфекционизм", "Истощение"],
        "career_fit": ["Искусство", "Инновации", "Startups", "R&D", "Режиссура"],
        "investment_profile": "Высокая креативность, высокий риск. Создаёт новые рынки.",
    },
    PersonalityArchetype.DIVINE_TRANSFORMER: {
        "title": "Божественный Трансформатор",
        "subtitle": "Канал высших сил перемен",
        "description": "Проводит трансформационную энергию из высших источников. Катализатор духовных изменений.",
        "strengths": ["Духовная трансформация", "Целительство", "Интуиция", "Харизма"],
        "challenges": ["Неземность", "Сложности с бытом", "Энергетическое истощение"],
        "career_fit": ["Духовное целительство", "Трансформационный коучинг", "Искусство"],
        "investment_profile": "Нетрадиционные подходы. Может видеть то, что не видят другие.",
    },
    PersonalityArchetype.MIXED: {
        "title": "Смешанный",
        "subtitle": "Уникальное сочетание энергий",
        "description": "Необычная комбинация качеств. Требует индивидуального анализа.",
        "strengths": ["Уникальность", "Адаптивность", "Многогранность"],
        "challenges": ["Внутренние противоречия", "Сложность самоидентификации"],
        "career_fit": ["Зависит от конкретной комбинации"],
        "investment_profile": "Требует индивидуальной оценки.",
    },
}


# =============================================================================
# OUTPUT DATACLASS
# =============================================================================

@dataclass
class NakshatraPosition:
    """Nakshatra position for a planet or point"""
    nakshatra_name: str
    nakshatra_number: int
    pada: int
    gana: GanaType
    lord: str
    deity: str
    shakti: str
    symbol: str
    degree_in_nakshatra: float


@dataclass
class NakshatraAnalysis:
    """
    Stage 11 Output: Nakshatra Deep Dive Analysis

    Contains:
    - Sun, Moon, Lagna nakshatra positions
    - Gana analysis for each
    - Personality archetype determination
    - Detailed archetype description
    """
    # Nakshatra positions
    sun_nakshatra: NakshatraPosition
    moon_nakshatra: NakshatraPosition
    lagna_nakshatra: NakshatraPosition

    # Gana analysis
    sun_gana: GanaType
    moon_gana: GanaType
    lagna_gana: GanaType
    gana_pattern: str  # e.g., "Deva-Manushya-Rakshasa"

    # Personality archetype
    archetype: PersonalityArchetype
    archetype_name_ru: str
    archetype_subtitle: str
    archetype_description: str
    archetype_strengths: List[str]
    archetype_challenges: List[str]
    archetype_career_fit: List[str]
    investment_profile: str

    # Compatibility hints
    compatible_archetypes: List[str]
    challenging_archetypes: List[str]

    # Overall scores
    spiritual_orientation: float  # 0-100: higher = more spiritual (Deva)
    practical_orientation: float  # 0-100: higher = more practical (Manushya)
    transformative_power: float   # 0-100: higher = more intense (Rakshasa)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "sun_nakshatra": {
                "name": self.sun_nakshatra.nakshatra_name,
                "number": self.sun_nakshatra.nakshatra_number,
                "pada": self.sun_nakshatra.pada,
                "gana": self.sun_gana.value,
                "lord": self.sun_nakshatra.lord,
                "deity": self.sun_nakshatra.deity,
                "shakti": self.sun_nakshatra.shakti,
            },
            "moon_nakshatra": {
                "name": self.moon_nakshatra.nakshatra_name,
                "number": self.moon_nakshatra.nakshatra_number,
                "pada": self.moon_nakshatra.pada,
                "gana": self.moon_gana.value,
                "lord": self.moon_nakshatra.lord,
                "deity": self.moon_nakshatra.deity,
                "shakti": self.moon_nakshatra.shakti,
            },
            "lagna_nakshatra": {
                "name": self.lagna_nakshatra.nakshatra_name,
                "number": self.lagna_nakshatra.nakshatra_number,
                "pada": self.lagna_nakshatra.pada,
                "gana": self.lagna_gana.value,
                "lord": self.lagna_nakshatra.lord,
                "deity": self.lagna_nakshatra.deity,
                "shakti": self.lagna_nakshatra.shakti,
            },
            "gana_pattern": self.gana_pattern,
            "archetype": {
                "code": self.archetype.name,
                "name_ru": self.archetype_name_ru,
                "subtitle": self.archetype_subtitle,
                "description": self.archetype_description,
                "strengths": self.archetype_strengths,
                "challenges": self.archetype_challenges,
                "career_fit": self.archetype_career_fit,
                "investment_profile": self.investment_profile,
            },
            "compatibility": {
                "compatible_archetypes": self.compatible_archetypes,
                "challenging_archetypes": self.challenging_archetypes,
            },
            "orientation_scores": {
                "spiritual": round(self.spiritual_orientation, 1),
                "practical": round(self.practical_orientation, 1),
                "transformative": round(self.transformative_power, 1),
            },
        }


# =============================================================================
# STAGE 11 CLASS
# =============================================================================

class Stage11NakshatraDeepDive:
    """
    Stage 11: Nakshatra Deep Dive

    Analyzes Sun, Moon, and Lagna nakshatras to determine:
    1. Individual nakshatra qualities
    2. Gana (temperament) for each
    3. Personality archetype from gana combination
    4. Compatibility patterns
    """

    def __init__(
        self,
        digital_twin: Dict[str, Any],
        d1_planets: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize Stage 11.

        Args:
            digital_twin: Full digital twin data
            d1_planets: Optional list of D1 planets (if already parsed)
        """
        self.digital_twin = digital_twin
        self.vargas = digital_twin.get("vargas", {})
        self.d1 = self.vargas.get("D1", {})

        # Use provided planets or extract from D1
        self.planets = d1_planets or self.d1.get("planets", [])
        self.ascendant = self.d1.get("ascendant", {})

    def analyze(self) -> NakshatraAnalysis:
        """
        Run Stage 11 analysis.

        Returns:
            NakshatraAnalysis with full nakshatra-based personality profile
        """
        # Get nakshatra positions
        sun_nak = self._get_nakshatra_position("Sun")
        moon_nak = self._get_nakshatra_position("Moon")
        lagna_nak = self._get_lagna_nakshatra_position()

        # Determine archetype from gana combination
        gana_tuple = (sun_nak.gana, moon_nak.gana, lagna_nak.gana)
        archetype = GANA_ARCHETYPE_MAP.get(gana_tuple, PersonalityArchetype.MIXED)

        # Get archetype details
        archetype_info = ARCHETYPE_DESCRIPTIONS.get(archetype, ARCHETYPE_DESCRIPTIONS[PersonalityArchetype.MIXED])

        # Calculate orientation scores
        spiritual, practical, transformative = self._calculate_orientation_scores(
            sun_nak.gana, moon_nak.gana, lagna_nak.gana
        )

        # Get compatibility hints
        compatible, challenging = self._get_compatibility_hints(archetype)

        return NakshatraAnalysis(
            sun_nakshatra=sun_nak,
            moon_nakshatra=moon_nak,
            lagna_nakshatra=lagna_nak,
            sun_gana=sun_nak.gana,
            moon_gana=moon_nak.gana,
            lagna_gana=lagna_nak.gana,
            gana_pattern=f"{sun_nak.gana.value}-{moon_nak.gana.value}-{lagna_nak.gana.value}",
            archetype=archetype,
            archetype_name_ru=archetype_info["title"],
            archetype_subtitle=archetype_info["subtitle"],
            archetype_description=archetype_info["description"],
            archetype_strengths=archetype_info["strengths"],
            archetype_challenges=archetype_info["challenges"],
            archetype_career_fit=archetype_info["career_fit"],
            investment_profile=archetype_info["investment_profile"],
            compatible_archetypes=compatible,
            challenging_archetypes=challenging,
            spiritual_orientation=spiritual,
            practical_orientation=practical,
            transformative_power=transformative,
        )

    def _get_planet_data(self, planet_name: str) -> Optional[Dict[str, Any]]:
        """Get planet data from planets list"""
        for p in self.planets:
            name = p.get("name", "") or p.get("planet", "")
            if name.lower() == planet_name.lower():
                return p
        return None

    def _get_nakshatra_position(self, planet_name: str) -> NakshatraPosition:
        """
        Get nakshatra position for a planet.

        Args:
            planet_name: Name of the planet (Sun, Moon, etc.)

        Returns:
            NakshatraPosition with full nakshatra data
        """
        planet_data = self._get_planet_data(planet_name)

        if planet_data:
            # Try to get nakshatra from planet data directly
            nak_name = planet_data.get("nakshatra", "")
            nak_pada = planet_data.get("nakshatra_pada", 1)

            # Get longitude for degree calculation
            longitude = planet_data.get("longitude", 0)

            if nak_name:
                # Look up nakshatra in catalog by name
                for nak_data in NAKSHATRA_CATALOG.values():
                    if nak_data.name.lower() == nak_name.lower() or nak_data.sanskrit_name.lower() == nak_name.lower():
                        return NakshatraPosition(
                            nakshatra_name=nak_data.name,
                            nakshatra_number=nak_data.number,
                            pada=nak_pada,
                            gana=nak_data.gana,
                            lord=nak_data.lord.value,
                            deity=nak_data.deity,
                            shakti=nak_data.shakti,
                            symbol=nak_data.symbol,
                            degree_in_nakshatra=longitude % 13.333333
                        )

            # Fallback: calculate from longitude
            if longitude > 0:
                nak_data = get_nakshatra_from_degree(longitude)
                pada = get_nakshatra_pada(longitude)
                return NakshatraPosition(
                    nakshatra_name=nak_data.name,
                    nakshatra_number=nak_data.number,
                    pada=pada,
                    gana=nak_data.gana,
                    lord=nak_data.lord.value,
                    deity=nak_data.deity,
                    shakti=nak_data.shakti,
                    symbol=nak_data.symbol,
                    degree_in_nakshatra=longitude % 13.333333
                )

        # Default fallback (Ashwini)
        default_nak = NAKSHATRA_CATALOG["Ashwini"]
        return NakshatraPosition(
            nakshatra_name=default_nak.name,
            nakshatra_number=1,
            pada=1,
            gana=default_nak.gana,
            lord=default_nak.lord.value,
            deity=default_nak.deity,
            shakti=default_nak.shakti,
            symbol=default_nak.symbol,
            degree_in_nakshatra=0
        )

    def _get_lagna_nakshatra_position(self) -> NakshatraPosition:
        """Get nakshatra position for Lagna (Ascendant)"""
        nak_name = self.ascendant.get("nakshatra", "")
        nak_pada = self.ascendant.get("nakshatra_pada", 1)
        longitude = self.ascendant.get("longitude", 0)

        # Try to get degrees from various sources
        if not longitude:
            degrees = self.ascendant.get("degrees", 0)
            sign_id = self.ascendant.get("sign_id", 1)
            longitude = (sign_id - 1) * 30 + degrees

        if nak_name:
            # Look up nakshatra in catalog by name
            for nak_data in NAKSHATRA_CATALOG.values():
                if nak_data.name.lower() == nak_name.lower() or nak_data.sanskrit_name.lower() == nak_name.lower():
                    return NakshatraPosition(
                        nakshatra_name=nak_data.name,
                        nakshatra_number=nak_data.number,
                        pada=nak_pada,
                        gana=nak_data.gana,
                        lord=nak_data.lord.value,
                        deity=nak_data.deity,
                        shakti=nak_data.shakti,
                        symbol=nak_data.symbol,
                        degree_in_nakshatra=longitude % 13.333333 if longitude else 0
                    )

        # Fallback: calculate from longitude
        if longitude > 0:
            nak_data = get_nakshatra_from_degree(longitude)
            pada = get_nakshatra_pada(longitude)
            return NakshatraPosition(
                nakshatra_name=nak_data.name,
                nakshatra_number=nak_data.number,
                pada=pada,
                gana=nak_data.gana,
                lord=nak_data.lord.value,
                deity=nak_data.deity,
                shakti=nak_data.shakti,
                symbol=nak_data.symbol,
                degree_in_nakshatra=longitude % 13.333333
            )

        # Default fallback
        default_nak = NAKSHATRA_CATALOG[1]
        return NakshatraPosition(
            nakshatra_name=default_nak.name,
            nakshatra_number=1,
            pada=1,
            gana=default_nak.gana,
            lord=default_nak.lord.value,
            deity=default_nak.deity,
            shakti=default_nak.shakti,
            symbol=default_nak.symbol,
            degree_in_nakshatra=0
        )

    def _calculate_orientation_scores(
        self,
        sun_gana: GanaType,
        moon_gana: GanaType,
        lagna_gana: GanaType
    ) -> Tuple[float, float, float]:
        """
        Calculate orientation scores based on gana distribution.

        Returns:
            Tuple of (spiritual, practical, transformative) scores (0-100)
        """
        ganas = [sun_gana, moon_gana, lagna_gana]

        # Count each type
        deva_count = sum(1 for g in ganas if g == GanaType.DEVA)
        manushya_count = sum(1 for g in ganas if g == GanaType.MANUSHYA)
        rakshasa_count = sum(1 for g in ganas if g == GanaType.RAKSHASA)

        # Base scores from counts
        spiritual = (deva_count / 3) * 100
        practical = (manushya_count / 3) * 100
        transformative = (rakshasa_count / 3) * 100

        # Weight Moon more heavily for emotional nature
        if moon_gana == GanaType.DEVA:
            spiritual += 10
        elif moon_gana == GanaType.MANUSHYA:
            practical += 10
        else:
            transformative += 10

        # Weight Lagna for outward expression
        if lagna_gana == GanaType.DEVA:
            spiritual += 5
        elif lagna_gana == GanaType.MANUSHYA:
            practical += 5
        else:
            transformative += 5

        # Normalize to ensure max is 100
        total = spiritual + practical + transformative
        if total > 0:
            factor = 100 / max(spiritual, practical, transformative)
            spiritual = min(100, spiritual * factor * 0.9)
            practical = min(100, practical * factor * 0.9)
            transformative = min(100, transformative * factor * 0.9)

        return spiritual, practical, transformative

    def _get_compatibility_hints(self, archetype: PersonalityArchetype) -> Tuple[List[str], List[str]]:
        """
        Get compatibility hints based on archetype.

        Returns:
            Tuple of (compatible archetypes, challenging archetypes)
        """
        compatibility_map = {
            PersonalityArchetype.LIGHT_BEARER: {
                "compatible": ["Благородный Практик", "Гармонизатор", "Духовный Воин"],
                "challenging": ["Трансформатор", "Интенсивный Созидатель"]
            },
            PersonalityArchetype.NOBLE_PRACTITIONER: {
                "compatible": ["Светоносец", "Строитель Мира", "Практичный Идеалист"],
                "challenging": ["Трансформатор", "Мудрый Разрушитель"]
            },
            PersonalityArchetype.HARMONIZER: {
                "compatible": ["Светоносец", "Практичный Идеалист", "Реформатор"],
                "challenging": ["Трансформатор", "Воин Света"]
            },
            PersonalityArchetype.WORLD_BUILDER: {
                "compatible": ["Благородный Практик", "Реформатор", "Практичный Идеалист"],
                "challenging": ["Светоносец", "Божественный Трансформатор"]
            },
            PersonalityArchetype.TRANSFORMER: {
                "compatible": ["Интенсивный Созидатель", "Духовный Воин", "Божественный Трансформатор"],
                "challenging": ["Светоносец", "Гармонизатор", "Строитель Мира"]
            },
            PersonalityArchetype.LIGHT_WARRIOR: {
                "compatible": ["Духовный Воин", "Реформатор", "Мудрый Разрушитель"],
                "challenging": ["Гармонизатор", "Светоносец"]
            },
            PersonalityArchetype.REFORMER: {
                "compatible": ["Строитель Мира", "Воин Света", "Практичный Идеалист"],
                "challenging": ["Трансформатор", "Интенсивный Созидатель"]
            },
            PersonalityArchetype.SPIRITUAL_WARRIOR: {
                "compatible": ["Трансформатор", "Воин Света", "Божественный Трансформатор"],
                "challenging": ["Строитель Мира", "Гармонизатор"]
            },
            PersonalityArchetype.WISE_DESTROYER: {
                "compatible": ["Духовный Воин", "Воин Света", "Мудрый Разрушитель"],
                "challenging": ["Светоносец", "Практичный Идеалист"]
            },
            PersonalityArchetype.PRACTICAL_IDEALIST: {
                "compatible": ["Благородный Практик", "Гармонизатор", "Реформатор"],
                "challenging": ["Трансформатор", "Мудрый Разрушитель"]
            },
            PersonalityArchetype.INTENSE_CREATOR: {
                "compatible": ["Трансформатор", "Духовный Воин", "Божественный Трансформатор"],
                "challenging": ["Светоносец", "Строитель Мира"]
            },
            PersonalityArchetype.DIVINE_TRANSFORMER: {
                "compatible": ["Трансформатор", "Интенсивный Созидатель", "Духовный Воин"],
                "challenging": ["Строитель Мира", "Благородный Практик"]
            },
            PersonalityArchetype.MIXED: {
                "compatible": ["Любой архетип (зависит от комбинации)"],
                "challenging": ["Зависит от конкретной комбинации"]
            },
        }

        hints = compatibility_map.get(archetype, compatibility_map[PersonalityArchetype.MIXED])
        return hints["compatible"], hints["challenging"]
