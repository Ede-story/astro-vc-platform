"""
Scoring System - AI-скоринг потенциала основателя стартапа
Основан на 30 астрологических критериях
"""

import logging
from typing import Dict, List, Tuple
from app.models.birth_chart import BirthChartResponse, PlanetPosition, HouseData, ScoreBreakdown


logger = logging.getLogger(__name__)


# Веса критериев (сумма = 1.0)
SCORING_WEIGHTS = {
    # КАТЕГОРИЯ 1: Денежный потенциал (вес 0.30)
    "2nd_house_strength": 0.05,      # Дом богатства
    "11th_house_strength": 0.05,     # Дом прибыли
    "jupiter_placement": 0.04,       # Юпитер (богатство)
    "mercury_strength": 0.03,        # Меркурий (бизнес, коммуникация)
    "venus_placement": 0.03,         # Венера (роскошь, деньги)
    "moon_2nd_11th": 0.02,          # Луна в домах богатства
    "jupiter_2nd_11th": 0.03,       # Юпитер в домах богатства
    "dhana_yoga": 0.05,             # Йога богатства (комбинации)

    # КАТЕГОРИЯ 2: Лидерство и власть (вес 0.25)
    "sun_placement": 0.05,           # Солнце (власть, эго)
    "10th_house_strength": 0.05,     # Дом карьеры
    "mars_strength": 0.03,           # Марс (энергия, драйв)
    "ascendant_lord": 0.04,          # Лагнеш (жизненная сила)
    "sun_10th_house": 0.03,          # Солнце в 10 доме
    "rajayoga": 0.05,                # Раджа-йога (королевская комбинация)

    # КАТЕГОРИЯ 3: Удача и своевременность (вес 0.20)
    "9th_house_strength": 0.04,      # Дом удачи
    "current_dasa_period": 0.05,     # Текущий планетарный период
    "jupiter_transits": 0.03,        # Транзит Юпитера
    "saturn_transits": 0.02,         # Транзит Сатурна
    "5th_house_fortune": 0.03,       # 5 дом (удача, спекуляции)
    "jupiter_9th_house": 0.03,       # Юпитер в доме удачи

    # КАТЕГОРИЯ 4: Инновации и креативность (вес 0.15)
    "5th_house_strength": 0.04,      # Дом творчества
    "rahu_placement": 0.03,          # Раху (инновации, технологии)
    "ketu_placement": 0.02,          # Кету (духовность, интуиция)
    "mercury_5th_house": 0.03,       # Меркурий в доме креативности
    "rahu_ketu_axis": 0.03,          # Ось Раху-Кету (кармическая задача)

    # КАТЕГОРИЯ 5: Стрессоустойчивость (вес 0.10)
    "moon_strength": 0.03,           # Луна (эмоции, ум)
    "saturn_maturity": 0.02,         # Сатурн (дисциплина)
    "6th_house_enemies": 0.02,       # 6 дом (враги, препятствия)
    "mars_courage": 0.03,            # Марс (храбрость)
}


def calculate_potential_score(chart: BirthChartResponse) -> Tuple[float, List[ScoreBreakdown]]:
    """
    Расчёт финального скора потенциала (1-10)

    Args:
        chart: Натальная карта с полными данными

    Returns:
        Tuple[float, List[ScoreBreakdown]]: (итоговый балл, детализация по критериям)
    """
    total_score = 0.0
    score_breakdowns = []

    # 1. КАТЕГОРИЯ: Денежный потенциал
    score, breakdown = _evaluate_wealth_potential(chart)
    total_score += score
    score_breakdowns.extend(breakdown)

    # 2. КАТЕГОРИЯ: Лидерство
    score, breakdown = _evaluate_leadership(chart)
    total_score += score
    score_breakdowns.extend(breakdown)

    # 3. КАТЕГОРИЯ: Удача и своевременность
    score, breakdown = _evaluate_luck_timing(chart)
    total_score += score
    score_breakdowns.extend(breakdown)

    # 4. КАТЕГОРИЯ: Инновации
    score, breakdown = _evaluate_innovation(chart)
    total_score += score
    score_breakdowns.extend(breakdown)

    # 5. КАТЕГОРИЯ: Стрессоустойчивость
    score, breakdown = _evaluate_resilience(chart)
    total_score += score
    score_breakdowns.extend(breakdown)

    # Нормализация к шкале 1-10
    # total_score сейчас в диапазоне 0-1 (сумма весов)
    # Переводим в 1-10: score * 9 + 1
    final_score = total_score * 9 + 1
    final_score = round(final_score, 1)

    logger.info(f"Potential score calculated: {final_score}/10")

    return final_score, score_breakdowns


def _evaluate_wealth_potential(chart: BirthChartResponse) -> Tuple[float, List[ScoreBreakdown]]:
    """Оценка денежного потенциала"""
    score = 0.0
    breakdowns = []

    # 2nd house strength (дом богатства)
    house2 = chart.houses.get("House2")
    if house2:
        criterion_score = _evaluate_house_strength(house2, chart.planets)
        weighted_score = criterion_score * SCORING_WEIGHTS["2nd_house_strength"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="2nd House (Wealth)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["2nd_house_strength"],
            explanation=f"2nd house in {house2.sign}, lord {house2.lord} - wealth accumulation"
        ))

    # 11th house strength (дом прибыли)
    house11 = chart.houses.get("House11")
    if house11:
        criterion_score = _evaluate_house_strength(house11, chart.planets)
        weighted_score = criterion_score * SCORING_WEIGHTS["11th_house_strength"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="11th House (Gains)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["11th_house_strength"],
            explanation=f"11th house in {house11.sign}, lord {house11.lord} - income potential"
        ))

    # Jupiter placement (планета богатства)
    jupiter = chart.planets.get("Jupiter")
    if jupiter:
        criterion_score = _evaluate_planet_placement(jupiter, favorable_houses=[2, 5, 9, 11])
        weighted_score = criterion_score * SCORING_WEIGHTS["jupiter_placement"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="Jupiter Placement",
            score=criterion_score,
            weight=SCORING_WEIGHTS["jupiter_placement"],
            explanation=f"Jupiter in {jupiter.zodiac_sign}, House {jupiter.house} - expansion & wealth"
        ))

    # Mercury strength (бизнес-коммуникация)
    mercury = chart.planets.get("Mercury")
    if mercury:
        criterion_score = _evaluate_planet_strength(mercury)
        weighted_score = criterion_score * SCORING_WEIGHTS["mercury_strength"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="Mercury (Business)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["mercury_strength"],
            explanation=f"Mercury in {mercury.zodiac_sign} - communication & trade"
        ))

    # Venus placement (роскошь, деньги)
    venus = chart.planets.get("Venus")
    if venus:
        criterion_score = _evaluate_planet_placement(venus, favorable_houses=[2, 7, 11])
        weighted_score = criterion_score * SCORING_WEIGHTS["venus_placement"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="Venus (Luxury)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["venus_placement"],
            explanation=f"Venus in House {venus.house} - wealth & comfort"
        ))

    return score, breakdowns


def _evaluate_leadership(chart: BirthChartResponse) -> Tuple[float, List[ScoreBreakdown]]:
    """Оценка лидерских качеств"""
    score = 0.0
    breakdowns = []

    # Sun placement (лидерство, власть)
    sun = chart.planets.get("Sun")
    if sun:
        criterion_score = _evaluate_planet_placement(sun, favorable_houses=[1, 5, 9, 10])
        weighted_score = criterion_score * SCORING_WEIGHTS["sun_placement"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="Sun (Leadership)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["sun_placement"],
            explanation=f"Sun in {sun.zodiac_sign}, House {sun.house} - authority & power"
        ))

    # 10th house strength (карьера)
    house10 = chart.houses.get("House10")
    if house10:
        criterion_score = _evaluate_house_strength(house10, chart.planets)
        weighted_score = criterion_score * SCORING_WEIGHTS["10th_house_strength"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="10th House (Career)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["10th_house_strength"],
            explanation=f"10th house in {house10.sign} - professional success"
        ))

    # Mars strength (энергия, драйв)
    mars = chart.planets.get("Mars")
    if mars:
        criterion_score = _evaluate_planet_strength(mars)
        weighted_score = criterion_score * SCORING_WEIGHTS["mars_strength"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="Mars (Energy)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["mars_strength"],
            explanation=f"Mars in {mars.zodiac_sign} - drive & action"
        ))

    return score, breakdowns


def _evaluate_luck_timing(chart: BirthChartResponse) -> Tuple[float, List[ScoreBreakdown]]:
    """Оценка удачи и своевременности"""
    score = 0.0
    breakdowns = []

    # 9th house strength (удача, дхарма)
    house9 = chart.houses.get("House9")
    if house9:
        criterion_score = _evaluate_house_strength(house9, chart.planets)
        weighted_score = criterion_score * SCORING_WEIGHTS["9th_house_strength"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="9th House (Fortune)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["9th_house_strength"],
            explanation=f"9th house in {house9.sign} - luck & opportunities"
        ))

    # Current Dasa period (текущий планетарный период)
    if chart.current_dasa:
        criterion_score = _evaluate_dasa_period(chart.current_dasa, chart.planets)
        weighted_score = criterion_score * SCORING_WEIGHTS["current_dasa_period"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="Current Dasa",
            score=criterion_score,
            weight=SCORING_WEIGHTS["current_dasa_period"],
            explanation=f"Running {chart.current_dasa.planet} Dasa - timing & opportunity window"
        ))

    return score, breakdowns


def _evaluate_innovation(chart: BirthChartResponse) -> Tuple[float, List[ScoreBreakdown]]:
    """Оценка инновационного потенциала"""
    score = 0.0
    breakdowns = []

    # 5th house strength (креативность)
    house5 = chart.houses.get("House5")
    if house5:
        criterion_score = _evaluate_house_strength(house5, chart.planets)
        weighted_score = criterion_score * SCORING_WEIGHTS["5th_house_strength"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="5th House (Creativity)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["5th_house_strength"],
            explanation=f"5th house in {house5.sign} - innovation & intelligence"
        ))

    # Rahu placement (технологии, инновации)
    rahu = chart.planets.get("Rahu")
    if rahu:
        criterion_score = _evaluate_planet_placement(rahu, favorable_houses=[3, 6, 10, 11])
        weighted_score = criterion_score * SCORING_WEIGHTS["rahu_placement"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="Rahu (Innovation)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["rahu_placement"],
            explanation=f"Rahu in House {rahu.house} - disruption & technology"
        ))

    return score, breakdowns


def _evaluate_resilience(chart: BirthChartResponse) -> Tuple[float, List[ScoreBreakdown]]:
    """Оценка стрессоустойчивости"""
    score = 0.0
    breakdowns = []

    # Moon strength (эмоциональная стабильность)
    moon = chart.planets.get("Moon")
    if moon:
        criterion_score = _evaluate_planet_strength(moon)
        weighted_score = criterion_score * SCORING_WEIGHTS["moon_strength"]
        score += weighted_score

        breakdowns.append(ScoreBreakdown(
            criterion_name="Moon (Mind)",
            score=criterion_score,
            weight=SCORING_WEIGHTS["moon_strength"],
            explanation=f"Moon in {moon.zodiac_sign} - emotional resilience"
        ))

    return score, breakdowns


# ============= HELPER FUNCTIONS =============

def _evaluate_house_strength(house: HouseData, planets: Dict[str, PlanetPosition]) -> float:
    """
    Оценка силы дома (0-10)

    Факторы:
    - Знак зодиака (благоприятный/неблагоприятный)
    - Планеты в доме
    - Управитель дома (где находится, его сила)
    """
    score = 5.0  # Базовый балл

    # Упрощённая оценка: если есть планета в доме, +2 балла
    for planet in planets.values():
        if f"House{house.house_number}" == f"House{planet.house}":
            score += 2.0

    return min(score, 10.0)


def _evaluate_planet_placement(planet: PlanetPosition, favorable_houses: List[int]) -> float:
    """
    Оценка расположения планеты (0-10)

    Args:
        planet: Планета
        favorable_houses: Благоприятные дома для этой планеты
    """
    score = 5.0  # Базовый балл

    if planet.house in favorable_houses:
        score += 3.0

    # Учёт Шадбала (если доступно)
    if planet.shadbala and planet.shadbala > 0:
        # Нормализация Shadbala (обычно 0-500)
        shadbala_normalized = min(planet.shadbala / 50, 10)
        score = (score + shadbala_normalized) / 2

    return min(score, 10.0)


def _evaluate_planet_strength(planet: PlanetPosition) -> float:
    """Общая оценка силы планеты (0-10)"""
    score = 5.0  # Базовый балл

    # Учёт Shadbala
    if planet.shadbala and planet.shadbala > 0:
        shadbala_normalized = min(planet.shadbala / 50, 10)
        score = shadbala_normalized

    # Штраф за ретроградность (кроме Юпитера и Венеры)
    if planet.is_retrograde and planet.name not in ["Jupiter", "Venus"]:
        score *= 0.8

    return min(score, 10.0)


def _evaluate_dasa_period(dasa: 'DasaPeriod', planets: Dict[str, PlanetPosition]) -> float:
    """
    Оценка текущего периода Даша (0-10)

    Благоприятность зависит от силы планеты-управителя
    """
    dasa_planet = planets.get(dasa.planet)

    if dasa_planet:
        return _evaluate_planet_strength(dasa_planet)

    return 5.0  # Default если планета не найдена


def generate_score_explanation(
    final_score: float,
    breakdowns: List[ScoreBreakdown]
) -> str:
    """
    Генерация текстового объяснения скора

    Args:
        final_score: Итоговый балл (1-10)
        breakdowns: Детализация по критериям

    Returns:
        str: Человекочитаемое объяснение
    """
    explanation_parts = [
        f"Potential Score: {final_score}/10\n",
        "\nTop Strengths:",
    ]

    # Топ-3 сильных критериев
    sorted_breakdowns = sorted(breakdowns, key=lambda x: x.score * x.weight, reverse=True)
    for breakdown in sorted_breakdowns[:3]:
        explanation_parts.append(f"  • {breakdown.criterion_name}: {breakdown.score:.1f}/10 - {breakdown.explanation}")

    # Рекомендации
    explanation_parts.append("\nRecommendations:")
    if final_score >= 8:
        explanation_parts.append("  Excellent potential. High probability of success.")
    elif final_score >= 6:
        explanation_parts.append("  Good potential. Consider timing and partnerships carefully.")
    else:
        explanation_parts.append("  Moderate potential. Focus on strengths and address weaknesses.")

    return "\n".join(explanation_parts)
