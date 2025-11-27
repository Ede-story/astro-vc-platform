"""
StarMeet API - Astrology Router
Handles chart calculations and profile operations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import traceback

# Import the Golden Math engine
import sys
sys.path.insert(0, '/app/packages')
from astro_core.engine import AstroCore, calculate_all_vargas, get_varga_sign, SIGNS

router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class CalculateRequest(BaseModel):
    """Request model for chart calculation."""
    date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    time: str = Field(..., description="Birth time in HH:MM format")
    lat: float = Field(..., description="Latitude (-90 to 90)")
    lon: float = Field(..., description="Longitude (-180 to 180)")
    timezone: float = Field(default=0.0, description="Timezone offset in hours (e.g., 3 for Moscow)")
    ayanamsa: str = Field(default="lahiri", description="Ayanamsa: lahiri or raman")
    varga: Optional[str] = Field(default=None, description="Specific varga to calculate (D1-D60)")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "1982-05-30",
                "time": "09:45",
                "lat": 59.93,
                "lon": 30.33,
                "timezone": 3.0,
                "ayanamsa": "lahiri",
                "varga": "D4"
            }
        }


class PlanetData(BaseModel):
    """Planet position data."""
    name: str
    sign: str
    degrees: float
    house: int
    nakshatra: str
    nakshatra_pada: int
    abs_longitude: float
    varga_signs: Dict[str, str] = {}


class CalculateResponse(BaseModel):
    """Response model for chart calculation."""
    success: bool
    ayanamsa: str
    ayanamsa_delta: float
    ascendant: Dict[str, Any]
    planets: List[PlanetData]
    houses: List[Dict[str, Any]]
    requested_varga: Optional[str] = None
    varga_data: Optional[Dict[str, Any]] = None


class QuickVargaRequest(BaseModel):
    """Quick varga calculation from longitude."""
    longitude: float = Field(..., description="Absolute longitude (0-360)")
    varga: str = Field(..., description="Varga code (D1-D60)")


class QuickVargaResponse(BaseModel):
    """Quick varga response."""
    longitude: float
    varga: str
    result_sign: str


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/calculate", response_model=CalculateResponse)
async def calculate_chart(request: CalculateRequest):
    """
    Calculate a Vedic birth chart.

    This is the main calculation endpoint. It uses the jyotishganit library
    with the "Golden Math" engine to calculate planetary positions and Varga charts.

    Example request:
    ```json
    {
        "date": "1982-05-30",
        "time": "09:45",
        "lat": 59.93,
        "lon": 30.33,
        "timezone": 3.0,
        "ayanamsa": "lahiri"
    }
    ```
    """
    try:
        # Parse date and time
        try:
            birth_date = datetime.strptime(request.date, "%Y-%m-%d")
            time_parts = request.time.split(":")
            birth_datetime = birth_date.replace(
                hour=int(time_parts[0]),
                minute=int(time_parts[1]) if len(time_parts) > 1 else 0,
                second=0
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format: {e}")

        # Map ayanamsa
        ayanamsa_map = {
            "lahiri": "Lahiri",
            "raman": "Raman",
            "true_chitrapaksha": "True_Chitrapaksha",
        }
        ayanamsa = ayanamsa_map.get(request.ayanamsa.lower(), "Lahiri")

        # Calculate chart using Golden Math engine
        core = AstroCore()
        chart = core.calculate(
            birth_datetime=birth_datetime,
            latitude=request.lat,
            longitude=request.lon,
            tz_offset_hours=request.timezone,
            timezone_name=f"UTC{'+' if request.timezone >= 0 else ''}{request.timezone}",
            ayanamsa=ayanamsa
        )

        # Build response
        planets_data = []
        for p in chart.planets:
            planet_data = PlanetData(
                name=p.name,
                sign=p.sign,
                degrees=round(p.sign_degrees, 2),
                house=p.house,
                nakshatra=p.nakshatra,
                nakshatra_pada=p.nakshatra_pada,
                abs_longitude=round(p.abs_longitude, 4),
                varga_signs=p.varga_signs
            )
            planets_data.append(planet_data)

        houses_data = []
        for h in chart.houses:
            houses_data.append({
                "house": h.house_number,
                "sign": h.sign,
                "degrees": round(h.sign_degrees, 2),
                "abs_longitude": round(h.abs_longitude, 4)
            })

        # If specific varga requested, extract that data
        varga_data = None
        if request.varga:
            varga_code = request.varga.upper()
            varga_data = {
                "code": varga_code,
                "ascendant": get_varga_sign(chart.houses[0].abs_longitude, varga_code) if chart.houses else None,
                "planets": {}
            }
            for p in chart.planets:
                varga_data["planets"][p.name] = p.varga_signs.get(varga_code, "Unknown")

        return CalculateResponse(
            success=True,
            ayanamsa=ayanamsa,
            ayanamsa_delta=round(chart.ayanamsa_delta, 6),
            ascendant={
                "sign": chart.ascendant_sign,
                "degrees": round(chart.ascendant_degrees, 2),
                "abs_longitude": round(chart.houses[0].abs_longitude, 4) if chart.houses else 0
            },
            planets=planets_data,
            houses=houses_data,
            requested_varga=request.varga,
            varga_data=varga_data
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/quick-varga", response_model=QuickVargaResponse)
async def quick_varga(request: QuickVargaRequest):
    """
    Quick varga sign calculation from absolute longitude.

    Useful for testing or when you already have the longitude.
    """
    try:
        result_sign = get_varga_sign(request.longitude, request.varga.upper())
        return QuickVargaResponse(
            longitude=request.longitude,
            varga=request.varga.upper(),
            result_sign=result_sign
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Varga calculation error: {str(e)}")


@router.get("/signs")
async def get_signs():
    """Get list of zodiac signs."""
    return {"signs": SIGNS}


# =============================================================================
# SAVE PROFILE ENDPOINT
# =============================================================================

class SaveProfileRequest(BaseModel):
    """Request to save a calculated chart profile."""
    input_data: Dict[str, Any] = Field(..., description="Original input data (date, time, location)")
    chart_data: Dict[str, Any] = Field(..., description="Calculated chart response")


class SaveProfileResponse(BaseModel):
    """Response after saving profile."""
    success: bool
    message: str
    profile_id: Optional[str] = None


@router.post("/save", response_model=SaveProfileResponse)
async def save_profile(request: SaveProfileRequest):
    """
    Save a calculated chart profile.

    NOTE: This is a placeholder implementation that stores to a JSON file.
    In production, this should save to PostgreSQL.
    """
    import json
    import uuid
    from pathlib import Path

    try:
        # Generate unique profile ID
        profile_id = str(uuid.uuid4())[:8]

        # Create profiles directory if not exists
        profiles_dir = Path("/app/data/profiles")
        profiles_dir.mkdir(parents=True, exist_ok=True)

        # Prepare profile data
        profile = {
            "id": profile_id,
            "created_at": datetime.now().isoformat(),
            "input": request.input_data,
            "chart": request.chart_data,
        }

        # Save to JSON file
        profile_path = profiles_dir / f"{profile_id}.json"
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2, default=str)

        return SaveProfileResponse(
            success=True,
            message="Profile saved successfully",
            profile_id=profile_id
        )

    except Exception as e:
        traceback.print_exc()
        return SaveProfileResponse(
            success=False,
            message=f"Failed to save profile: {str(e)}",
            profile_id=None
        )


@router.get("/test-olya")
async def test_olya():
    """
    Test endpoint with Olya's birth data.

    Expected results for D4:
    - Sun should be in Scorpio (NOT Leo)
    - This validates the Golden Math engine is working correctly.
    """
    try:
        core = AstroCore()
        chart = core.calculate(
            birth_datetime=datetime(1982, 5, 30, 9, 45, 0),
            latitude=59.93,
            longitude=30.33,
            tz_offset_hours=3.0,
            timezone_name="Europe/Moscow",
            ayanamsa="Lahiri"
        )

        # Find Sun
        sun_data = None
        for p in chart.planets:
            if p.name == "Sun":
                sun_data = {
                    "name": p.name,
                    "D1_sign": p.sign,
                    "D1_degrees": round(p.sign_degrees, 2),
                    "abs_longitude": round(p.abs_longitude, 4),
                    "D4_sign": p.varga_signs.get("D4", "Unknown"),
                    "D10_sign": p.varga_signs.get("D10", "Unknown"),
                    "all_vargas": p.varga_signs
                }
                break

        return {
            "test": "Olya (1982-05-30 09:45 St.Petersburg)",
            "ayanamsa": "Lahiri",
            "ascendant": chart.ascendant_sign,
            "sun": sun_data,
            "validation": {
                "D4_sun_expected": "Scorpio",
                "D4_sun_actual": sun_data["D4_sign"] if sun_data else "N/A",
                "PASSED": sun_data["D4_sign"] == "Scorpio" if sun_data else False
            }
        }
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}
