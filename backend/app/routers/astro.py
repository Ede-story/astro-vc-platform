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
from astro_core.engine import (
    AstroCore,
    calculate_all_vargas,
    get_varga_sign,
    get_varga_sign_and_degrees,
    SIGNS,
    generate_digital_twin
)

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
    """Planet position data with extended astrological details."""
    name: str
    sign: str
    degrees: float
    house: int
    nakshatra: str
    nakshatra_pada: int
    abs_longitude: float
    varga_signs: Dict[str, str] = {}

    # Extended data
    sign_lord: str = ""
    nakshatra_lord: str = ""
    houses_owned: List[int] = []
    dignity: str = ""
    conjunctions: List[str] = []
    aspects_giving: List[int] = []
    aspects_receiving: List[str] = []


class HouseData(BaseModel):
    """House data with extended details."""
    house: int
    sign: str
    degrees: float
    abs_longitude: float
    lord: str = ""
    occupants: List[str] = []
    aspects_received: List[str] = []


class CalculateResponse(BaseModel):
    """Response model for chart calculation."""
    success: bool
    ayanamsa: str
    ayanamsa_delta: float
    ascendant: Dict[str, Any]
    planets: List[PlanetData]
    houses: List[HouseData]
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

        # Build response with extended data
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
                varga_signs=p.varga_signs,
                # Extended data
                sign_lord=p.sign_lord,
                nakshatra_lord=p.nakshatra_lord,
                houses_owned=p.houses_owned,
                dignity=p.dignity,
                conjunctions=p.conjunctions,
                aspects_giving=p.aspects_giving,
                aspects_receiving=p.aspects_receiving
            )
            planets_data.append(planet_data)

        houses_data = []
        for h in chart.houses:
            house_data = HouseData(
                house=h.house_number,
                sign=h.sign,
                degrees=round(h.sign_degrees, 2),
                abs_longitude=round(h.abs_longitude, 4),
                lord=h.lord,
                occupants=h.occupants,
                aspects_received=h.aspects_received
            )
            houses_data.append(house_data)

        # If specific varga requested, extract that data with degrees
        varga_data = None
        if request.varga:
            varga_code = request.varga.upper()
            asc_sign, asc_deg = get_varga_sign_and_degrees(
                chart.houses[0].abs_longitude, varga_code
            ) if chart.houses else (None, 0.0)
            varga_data = {
                "code": varga_code,
                "ascendant": asc_sign,
                "ascendant_degrees": round(asc_deg, 2),
                "planets": {}
            }
            for p in chart.planets:
                sign, degrees = get_varga_sign_and_degrees(p.abs_longitude, varga_code)
                varga_data["planets"][p.name] = {
                    "sign": sign,
                    "degrees": round(degrees, 2)
                }

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
    Save a calculated chart profile with FULL Digital Twin.

    The Digital Twin contains comprehensive data for ALL 16 Varga charts,
    including complete planetary and house data optimized for AI analysis.

    NOTE: This is a placeholder implementation that stores to a JSON file.
    In production, this should save to PostgreSQL JSONB.
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

        # Extract birth data from input
        input_data = request.input_data
        birth_date_str = input_data.get("date", "")
        birth_time_str = input_data.get("time", "00:00")
        latitude = float(input_data.get("lat", 0))
        longitude = float(input_data.get("lon", 0))
        timezone_offset = float(input_data.get("timezone", 0))
        ayanamsa = input_data.get("ayanamsa", "lahiri")

        # Map ayanamsa to engine format
        ayanamsa_map = {
            "lahiri": "Lahiri",
            "raman": "Raman",
            "true_chitrapaksha": "True_Chitrapaksha",
        }
        engine_ayanamsa = ayanamsa_map.get(ayanamsa.lower(), "Lahiri")

        # Parse birth datetime
        try:
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
            time_parts = birth_time_str.split(":")
            birth_datetime = birth_date.replace(
                hour=int(time_parts[0]),
                minute=int(time_parts[1]) if len(time_parts) > 1 else 0,
                second=0
            )
        except ValueError as e:
            return SaveProfileResponse(
                success=False,
                message=f"Invalid date/time format: {str(e)}",
                profile_id=None
            )

        # Generate Digital Twin (comprehensive data for all 16 Vargas)
        digital_twin = generate_digital_twin(
            birth_datetime=birth_datetime,
            latitude=latitude,
            longitude=longitude,
            tz_offset_hours=timezone_offset,
            ayanamsa=engine_ayanamsa
        )

        # Prepare profile data with Digital Twin
        profile = {
            "id": profile_id,
            "created_at": datetime.now().isoformat(),
            "input": request.input_data,
            "chart": request.chart_data,  # Keep original chart for backward compatibility
            "digital_twin": digital_twin,  # NEW: Full Digital Twin with all Vargas
        }

        # Save to JSON file
        profile_path = profiles_dir / f"{profile_id}.json"
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2, default=str)

        return SaveProfileResponse(
            success=True,
            message="Profile saved with Digital Twin",
            profile_id=profile_id
        )

    except Exception as e:
        traceback.print_exc()
        return SaveProfileResponse(
            success=False,
            message=f"Failed to save profile: {str(e)}",
            profile_id=None
        )


@router.get("/profiles")
async def list_profiles():
    """
    Get list of all saved profiles.
    Returns only metadata (id, name, created_at, input data).
    """
    import json
    from pathlib import Path

    try:
        profiles_dir = Path("/app/data/profiles")
        if not profiles_dir.exists():
            return {"profiles": []}

        profiles = []
        for profile_path in sorted(profiles_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    profiles.append({
                        "id": data.get("id"),
                        "name": data.get("input", {}).get("name", "Без имени"),
                        "created_at": data.get("created_at"),
                        "input": data.get("input", {})
                    })
            except Exception:
                continue

        return {"profiles": profiles}

    except Exception as e:
        traceback.print_exc()
        return {"profiles": [], "error": str(e)}


@router.get("/profiles/{profile_id}")
async def get_profile(profile_id: str):
    """
    Get a specific profile by ID.
    Returns full profile data including chart.
    """
    import json
    from pathlib import Path

    try:
        profile_path = Path(f"/app/data/profiles/{profile_id}.json")
        if not profile_path.exists():
            raise HTTPException(status_code=404, detail="Profile not found")

        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: str):
    """Delete a saved profile."""
    from pathlib import Path

    try:
        profile_path = Path(f"/app/data/profiles/{profile_id}.json")
        if not profile_path.exists():
            raise HTTPException(status_code=404, detail="Profile not found")

        profile_path.unlink()
        return {"success": True, "message": "Profile deleted"}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/test-digital-twin")
async def test_digital_twin():
    """
    Test Digital Twin generation with Olya's birth data.

    Validates that the Digital Twin contains complete data for D10 (Dashamsha):
    - dignity_state for all planets
    - house_occupied for all planets
    - absolute_degree and relative_degree
    """
    try:
        # Generate Digital Twin with Olya's data
        digital_twin = generate_digital_twin(
            birth_datetime=datetime(1982, 5, 30, 9, 45, 0),
            latitude=59.93,
            longitude=30.33,
            tz_offset_hours=3.0,
            ayanamsa="Lahiri"
        )

        # Extract D10 data for validation
        d10_data = digital_twin.get("vargas", {}).get("D10", {})
        d10_planets = d10_data.get("planets", [])
        d10_houses = d10_data.get("houses", [])

        # Find Sun in D10
        sun_d10 = None
        for p in d10_planets:
            if p.get("name") == "Sun":
                sun_d10 = p
                break

        # Validation checks
        validations = {
            "has_meta": "meta" in digital_twin,
            "has_all_16_vargas": len(digital_twin.get("vargas", {})) == 16,
            "d10_has_9_planets": len(d10_planets) == 9,
            "d10_has_12_houses": len(d10_houses) == 12,
            "sun_has_dignity_state": sun_d10.get("dignity_state") is not None if sun_d10 else False,
            "sun_has_house_occupied": sun_d10.get("house_occupied") is not None if sun_d10 else False,
            "sun_has_absolute_degree": sun_d10.get("absolute_degree") is not None if sun_d10 else False,
            "all_passed": True  # Will be updated below
        }
        validations["all_passed"] = all(v for k, v in validations.items() if k != "all_passed")

        return {
            "test": "Digital Twin - Olya (1982-05-30 09:45 St.Petersburg)",
            "meta": digital_twin.get("meta", {}),
            "vargas_count": len(digital_twin.get("vargas", {})),
            "varga_codes": list(digital_twin.get("vargas", {}).keys()),
            "d10_sample": {
                "ascendant": d10_data.get("ascendant", {}),
                "sun": sun_d10,
                "house_1": d10_houses[0] if d10_houses else None,
            },
            "validations": validations
        }

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}
