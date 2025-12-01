"""
StarMeet API - Astrology Router
Handles chart calculations and profile operations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import traceback

# Timezone detection
try:
    from timezonefinder import TimezoneFinder
    import pytz
    TZ_FINDER = TimezoneFinder()
except ImportError:
    TZ_FINDER = None
    pytz = None

# Import the Golden Math engine
import sys
sys.path.insert(0, '/app/packages')
from astro_core.engine import (
    AstroCore,
    calculate_all_vargas,
    get_varga_sign,
    get_varga_sign_and_degrees,
    SIGNS,
    generate_digital_twin,
    generate_digital_twin_enhanced,
    calculate_chara_karakas
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
    ayanamsa: str = Field(default="raman", description="Ayanamsa: raman or lahiri")
    timezone_override: Optional[float] = Field(default=None, description="Expert override: force specific UTC offset")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "1982-05-30",
                "time": "09:45",
                "lat": 59.93,
                "lon": 30.33,
                "ayanamsa": "raman"
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


class DetectedTimezone(BaseModel):
    """Detected timezone information."""
    timezone_name: str
    utc_offset: float
    is_dst: bool
    source: str  # "auto" or "override"


class CalculateResponse(BaseModel):
    """Response model for chart calculation - returns full Digital Twin."""
    success: bool
    detected_timezone: DetectedTimezone
    digital_twin: Dict[str, Any]  # Full 16-Varga Digital Twin


class QuickVargaRequest(BaseModel):
    """Quick varga calculation from longitude."""
    longitude: float = Field(..., description="Absolute longitude (0-360)")
    varga: str = Field(..., description="Varga code (D1-D60)")


class QuickVargaResponse(BaseModel):
    """Quick varga response."""
    longitude: float
    varga: str
    result_sign: str


class TimezoneRequest(BaseModel):
    """Request for timezone detection."""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(default="12:00", description="Time in HH:MM format")


class TimezoneResponse(BaseModel):
    """Response with detected timezone."""
    timezone_name: str
    utc_offset: float
    is_dst: bool
    dst_offset: float


# =============================================================================
# ENDPOINTS
# =============================================================================

def _detect_timezone(lat: float, lon: float, date_str: str, time_str: str) -> tuple[str, float, bool]:
    """
    Detect historical timezone for given coordinates and datetime.
    Returns: (timezone_name, utc_offset, is_dst)
    """
    if TZ_FINDER is None or pytz is None:
        # Fallback to geographic calculation
        tz_offset = round(lon / 15)
        return ("UTC", float(tz_offset), False)

    try:
        # Find timezone name by coordinates
        tz_name = TZ_FINDER.timezone_at(lat=lat, lng=lon)
        if not tz_name:
            tz_offset = round(lon / 15)
            return ("UTC", float(tz_offset), False)

        # Parse date and time
        try:
            naive_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            naive_dt = datetime.strptime(date_str, "%Y-%m-%d")

        # Get timezone object and localize the datetime
        tz = pytz.timezone(tz_name)
        local_dt = tz.localize(naive_dt, is_dst=None)

        # Calculate UTC offset in hours
        utc_offset = local_dt.utcoffset().total_seconds() / 3600

        # Check if DST is in effect
        dst = local_dt.dst()
        is_dst = dst is not None and dst.total_seconds() > 0

        return (tz_name, utc_offset, is_dst)

    except Exception:
        # Fallback to geographic calculation
        tz_offset = round(lon / 15)
        return ("UTC", float(tz_offset), False)


@router.post("/calculate", response_model=CalculateResponse)
async def calculate_chart(request: CalculateRequest):
    """
    Calculate a Vedic birth chart - returns FULL Digital Twin with all 16 Vargas.

    **Backend Authority Pattern**: Timezone is auto-detected from coordinates and date.
    Uses IANA timezone database for historical accuracy (e.g., USSR DST in 1982).

    Frontend sends only: date, time, lat, lon, ayanamsa.
    Backend auto-detects timezone and returns it in the response.

    Example request:
    ```json
    {
        "date": "1982-05-30",
        "time": "09:45",
        "lat": 59.93,
        "lon": 30.33,
        "ayanamsa": "raman"
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

        # AUTO-DETECT TIMEZONE (Backend Authority)
        if request.timezone_override is not None:
            # Expert mode: use provided override
            tz_offset = request.timezone_override
            tz_info = DetectedTimezone(
                timezone_name="Manual Override",
                utc_offset=tz_offset,
                is_dst=False,
                source="override"
            )
        else:
            # Auto-detect from coordinates and date
            tz_name, tz_offset, is_dst = _detect_timezone(
                request.lat, request.lon, request.date, request.time
            )
            tz_info = DetectedTimezone(
                timezone_name=tz_name,
                utc_offset=tz_offset,
                is_dst=is_dst,
                source="auto"
            )

        # Map ayanamsa
        ayanamsa_map = {
            "lahiri": "Lahiri",
            "raman": "Raman",
            "true_chitrapaksha": "True_Chitrapaksha",
        }
        ayanamsa = ayanamsa_map.get(request.ayanamsa.lower(), "Raman")

        # Generate FULL Digital Twin with all 20 Vargas + Dasha + Karakas
        digital_twin = generate_digital_twin_enhanced(
            birth_datetime=birth_datetime,
            latitude=request.lat,
            longitude=request.lon,
            tz_offset_hours=tz_offset,
            ayanamsa=ayanamsa
        )

        return CalculateResponse(
            success=True,
            detected_timezone=tz_info,
            digital_twin=digital_twin
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


@router.post("/timezone", response_model=TimezoneResponse)
async def get_timezone(request: TimezoneRequest):
    """
    Get historical timezone offset for a specific location and date.

    This endpoint uses the IANA timezone database to determine the correct
    UTC offset for any date in history, including DST transitions.

    Example: Saint Petersburg on May 30, 1982 was UTC+4 (summer time).
    """
    if TZ_FINDER is None or pytz is None:
        # Fallback to geographic calculation if libraries not available
        tz = round(request.lon / 15)
        return TimezoneResponse(
            timezone_name="UTC",
            utc_offset=float(tz),
            is_dst=False,
            dst_offset=0.0
        )

    try:
        # Find timezone name by coordinates
        tz_name = TZ_FINDER.timezone_at(lat=request.lat, lng=request.lon)
        if not tz_name:
            # Fallback for ocean/unknown areas
            tz = round(request.lon / 15)
            return TimezoneResponse(
                timezone_name="UTC",
                utc_offset=float(tz),
                is_dst=False,
                dst_offset=0.0
            )

        # Parse date and time
        dt_str = f"{request.date} {request.time}"
        try:
            naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            naive_dt = datetime.strptime(request.date, "%Y-%m-%d")

        # Get timezone object and localize the datetime
        tz = pytz.timezone(tz_name)
        local_dt = tz.localize(naive_dt, is_dst=None)

        # Calculate UTC offset in hours
        utc_offset = local_dt.utcoffset().total_seconds() / 3600

        # Check if DST is in effect
        dst_offset = local_dt.dst()
        is_dst = dst_offset is not None and dst_offset.total_seconds() > 0
        dst_hours = dst_offset.total_seconds() / 3600 if dst_offset else 0.0

        return TimezoneResponse(
            timezone_name=tz_name,
            utc_offset=utc_offset,
            is_dst=is_dst,
            dst_offset=dst_hours
        )

    except Exception as e:
        traceback.print_exc()
        # Fallback to geographic calculation
        tz = round(request.lon / 15)
        return TimezoneResponse(
            timezone_name="UTC",
            utc_offset=float(tz),
            is_dst=False,
            dst_offset=0.0
        )


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
        ayanamsa = input_data.get("ayanamsa", "raman")

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


@router.get("/test-chara-karakas")
async def test_chara_karakas():
    """
    Test Chara Karaka calculation with Vadim's birth data.

    Chara Karakas (Jaimini system) - variable significators based on planetary degrees.
    The planet with the highest degree in sign becomes Atmakaraka (AK).
    """
    try:
        # Generate enhanced Digital Twin with Vadim's data
        digital_twin = generate_digital_twin_enhanced(
            birth_datetime=datetime(1977, 10, 25, 6, 28, 0),
            latitude=61.7,
            longitude=30.7,
            tz_offset_hours=3.0,
            ayanamsa="Lahiri"
        )

        # Extract Chara Karakas
        chara_karakas = digital_twin.get("chara_karakas", {})

        return {
            "test": "Chara Karakas - Vadim (1977-10-25 06:28 Sortavala)",
            "ayanamsa": "Lahiri",
            "chara_karakas": chara_karakas,
            "has_dasha": "dasha" in digital_twin,
            "summary": {
                "atmakaraka": chara_karakas.get("by_karaka", {}).get("AK", "Unknown"),
                "darakaraka": chara_karakas.get("by_karaka", {}).get("DK", "Unknown")
            }
        }

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}
