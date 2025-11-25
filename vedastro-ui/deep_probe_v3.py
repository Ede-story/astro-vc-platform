import requests
import sys
import xml.etree.ElementTree as ET

BASE_URL = "http://vedastro-engine"
LOC = "Location/London"
TIME = "Time/12:00/01/01/1990/+00:00" # Standard testing time

# EXACT Method Names found in Core.cs
# Needed arguments:
# PlanetName -> PlanetName/Sun
# HouseName -> HouseName/House1
# Time -> (Implicit in Location/Time string part)

VECTORS = [
    # 1. House Occupied
    f"/api/Calculate/HousePlanetOccupiesBasedOnLongitudes/PlanetName/Sun/{LOC}/{TIME}",
    f"/api/Calculate/HousePlanetOccupiesBasedOnSign/PlanetName/Sun/{LOC}/{TIME}",

    # 2. Planet Lord of Sign (Dispositor)
    f"/api/Calculate/PlanetLordOfZodiacSign/PlanetName/Sun/{LOC}/{TIME}",

    # 3. Houses Owned
    f"/api/Calculate/HousesOwnedByPlanet/PlanetName/Sun/{LOC}/{TIME}",

    # 4. Planet in D9 (Navamsa) - Checking variations
    f"/api/Calculate/PlanetNavamsaSign/PlanetName/Sun/{LOC}/{TIME}", # Likely exists if Navamsa works
    # Also trying the resource style that worked:
    f"/api/{LOC}/{TIME}/Planet/Sun/Navamsa",

    # 5. House Cusp Signs
    f"/api/Calculate/HouseSignName/HouseName/House1/{LOC}/{TIME}",
    f"/api/Calculate/HouseZodiacSign/HouseName/House1/{LOC}/{TIME}",

    # 6. Nakshatra of House Cusp
    f"/api/Calculate/HouseConstellation/HouseName/House1/{LOC}/{TIME}",

    # 7. Planets in House
    f"/api/Calculate/PlanetsInHouse/HouseName/House1/{LOC}/{TIME}",
    f"/api/Calculate/PlanetsInHouseBasedOnSign/HouseName/House1/{LOC}/{TIME}",

    # 8. Ketu Check (Trying to see longitude)
    f"/api/Calculate/PlanetNirayanaLongitude/PlanetName/Ketu/{LOC}/{TIME}",
    f"/api/Calculate/PlanetNirayanaLongitude/PlanetName/Rahu/{LOC}/{TIME}",
    # Try Mean Ketu if implied? No explicit name found.
]

def check_payload(text):
    try:
        root = ET.fromstring(text)
        payload = root.find("Payload")
        if payload is not None and payload.text:
            return payload.text.strip()
        return None
    except:
        return None

def probe():
    print("🔬 DEEP PROBE V3 - Testing Exact Methods from Core.cs")

    for url_path in VECTORS:
        full_url = BASE_URL + url_path
        print(f"👉 {url_path}")
        try:
            r = requests.get(full_url, timeout=10)
            if r.status_code == 200:
                val = check_payload(r.text)
                if val:
                    print(f"   ✅ FOUND: {val}")
                else:
                    # sometimes returns JSON Array? parser handles XML.
                    # If JSON, raw text might be useful
                    if r.text.strip().startswith("[") or r.text.strip().startswith("{"):
                         print(f"   ✅ FOUND JSON: {r.text[:100]}...")
                    else:
                         print(f"   ⚠️  EMPTY PAYLOAD. Raw: {r.text[:50]}")
            else:
                print(f"   ❌ {r.status_code}")
        except Exception as e:
            print(f"   🚨 ERR: {e}")
        print("-" * 20)

if __name__ == "__main__":
    probe()
