"""
Rating API Endpoint
Оценка потенциала основателя стартапа на основе натальной карты
"""

import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.birth_data import BirthData
from app.models.rating import RatingResponse
from app.models.birth_chart import BirthChartResponse
from app.services.vedastro_engine import get_vedastro_engine
from app.services.scoring import calculate_potential_score, generate_score_explanation


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["rating"])


@router.post("/rating", response_model=RatingResponse, status_code=status.HTTP_200_OK)
async def rate_startup_founder(birth_data: BirthData):
    """
    Оценка потенциала основателя стартапа (1-10 баллов)

    **Процесс:**
    1. Расчёт натальной карты через VedAstro
    2. AI-скоринг на основе 30 астрологических критериев
    3. Генерация объяснения и рекомендаций

    **Категории оценки:**
    - Денежный потенциал (30%)
    - Лидерство и власть (25%)
    - Удача и своевременность (20%)
    - Инновации и креативность (15%)
    - Стрессоустойчивость (10%)

    **Args:**
        birth_data: Данные о рождении (имя, дата, время, место)

    **Returns:**
        RatingResponse: Оценка потенциала с детальным объяснением

    **Example Request:**
    ```json
    {
      "name": "Steve Jobs",
      "date": "1955-02-24",
      "time": "19:15:00",
      "latitude": 37.77,
      "longitude": -122.42,
      "timezone": -8,
      "gender": "Male"
    }
    ```

    **Example Response:**
    ```json
    {
      "success": true,
      "score": 8,
      "score_max": 10,
      "explanation": "Excellent potential. Strong 10th house indicates leadership...",
      "person_name": "Steve Jobs",
      "chart_data": {...},
      "error": null
    }
    ```
    """
    try:
        logger.info(f"Rating request for: {birth_data.name}")

        # 1. Получение VedAstro Engine
        engine = get_vedastro_engine()

        # 2. Расчёт натальной карты
        try:
            birth_chart: BirthChartResponse = engine.calculate_birth_chart(birth_data)
            logger.info(f"Birth chart calculated successfully for {birth_data.name}")
        except ValueError as e:
            logger.error(f"Birth chart calculation failed: {e}")
            return RatingResponse(
                success=False,
                score=None,
                explanation=None,
                person_name=birth_data.name,
                chart_data=None,
                error=f"Failed to calculate birth chart: {str(e)}"
            )

        # 3. AI-скоринг потенциала
        try:
            final_score, score_breakdowns = calculate_potential_score(birth_chart)
            logger.info(f"Potential score calculated: {final_score}/10")
        except Exception as e:
            logger.error(f"Scoring failed: {e}")
            return RatingResponse(
                success=False,
                score=None,
                explanation=None,
                person_name=birth_data.name,
                chart_data=birth_chart.dict() if birth_chart else None,
                error=f"Scoring calculation failed: {str(e)}"
            )

        # 4. Генерация объяснения
        try:
            explanation = generate_score_explanation(final_score, score_breakdowns)
        except Exception as e:
            logger.warning(f"Explanation generation failed: {e}")
            explanation = f"Score: {final_score}/10. Unable to generate detailed explanation."

        # 5. Формирование ответа
        response = RatingResponse(
            success=True,
            score=int(round(final_score)),
            score_max=10,
            explanation=explanation,
            person_name=birth_data.name,
            chart_data=birth_chart.dict(),
            error=None
        )

        logger.info(f"Rating completed successfully: {final_score}/10 for {birth_data.name}")
        return response

    except Exception as e:
        # Непредвиденная ошибка
        logger.exception(f"Unexpected error in rating endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health/vedastro", status_code=status.HTTP_200_OK)
async def vedastro_health_check():
    """
    Проверка статуса VedAstro Engine

    **Returns:**
    ```json
    {
      "status": "healthy",
      "vedastro_available": true,
      "vedastro_version": "1.23.19",
      "redis_available": true
    }
    ```
    """
    try:
        engine = get_vedastro_engine()

        return JSONResponse(content={
            "status": "healthy",
            "vedastro_available": True,
            "vedastro_version": engine.redis_client is not None,  # Placeholder
            "redis_available": engine.redis_available,
        })

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def rating_info():
    """
    Информация о Rating API

    **Returns:**
    Описание доступных endpoints и их назначение
    """
    return {
        "service": "Astro-VC Rating API",
        "version": "0.1.0",
        "description": "AI-powered startup founder potential scoring based on Vedic astrology",
        "endpoints": {
            "POST /api/v1/rating": "Calculate potential score for a person",
            "GET /api/v1/health/vedastro": "Check VedAstro engine health",
            "GET /api/v1/": "This information page"
        },
        "criteria": {
            "wealth_potential": "30%",
            "leadership": "25%",
            "luck_timing": "20%",
            "innovation": "15%",
            "resilience": "10%"
        },
        "score_range": "1-10 (1=low, 10=excellent)",
        "cache": "Redis (24h TTL for birth charts)"
    }
