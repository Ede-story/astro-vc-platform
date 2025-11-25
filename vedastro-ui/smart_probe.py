import requests
import sys
import xml.etree.ElementTree as ET

# Internal URL inside docker network
BASE_URL = "http://vedastro-engine"

# Common params
LOC = "Location/London"
TIME = "Time/12:00/01/01/1990/+00:00"
PLANET = "PlanetName/Sun"
HOUSE_SYS = "HouseSystem/Raman" # Raman is common in VedAstro

TEST_VECTORS = [
    # 1. Resource Style with HouseSystem (injected before Planet?)
    f"/api/{LOC}/{TIME}/{HOUSE_SYS}/Planet/Sun/HousePlanetOccupies",
    f"/api/{LOC}/{TIME}/{HOUSE_SYS}/Planet/Sun/House",

    # 2. Resource Style with HouseSystem after Planet?
    f"/api/{LOC}/{TIME}/Planet/Sun/{HOUSE_SYS}/HousePlanetOccupies",
    f"/api/{LOC}/{TIME}/Planet/Sun/HouseSystem/Raman/House",

    # 3. Calculate Style (Detailed)
    # /api/Calculate/CalculatorName/Arg1/Val1/Arg2/Val2...
    f"/api/Calculate/HousePlanetOccupies/PlanetName/Sun/Location/London/Time/12:00/01/01/1990/+00:00/HouseSystem/Raman",
    f"/api/Calculate/HousePlanetOccupies/PlanetName/Sun/HouseSystem/Raman/Location/London/Time/12:00/01/01/1990/+00:00",

    # 4. Calculate Style with Short Params
    f"/api/Calculate/HousePlanetOccupies/Sun/Raman/London/12:00/01/01/1990/+00:00",

    # 5. Houses Cusp
    f"/api/Calculate/SignOnCusp/HouseName/House1/HouseSystem/Raman/Location/London/Time/12:00/01/01/1990/+00:00",
    f"/api/Calculate/SignOnCusp/HouseName/House1/Location/London/Time/12:00/01/01/1990/+00:00",

    # 6. House Resource Style with HouseSystem
    f"/api/{LOC}/{TIME}/{HOUSE_SYS}/House/House1/SignOnCusp",
    f"/api/{LOC}/{TIME}/{HOUSE_SYS}/House/House1/Sign",
    f"/api/{LOC}/{TIME}/House/House1/{HOUSE_SYS}/Sign",

    # 7. Check for All Calculators list
    "/api/Calculate/All",
    "/api/Calculate/List",
    "/api/Help",
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
    print(f"🔬 SMART PROBE 2.0 starting against {BASE_URL}...\n")
    found_any = False

    for path in TEST_VECTORS:
        url = f"{BASE_URL}{path}"
        print(f"👉 Checking: {url}")

        try:
            r = requests.get(url, timeout=5)
            print(f"   HTTP {r.status_code}")

            if r.status_code == 200:
                data = check_payload(r.text)
                if data:
                    print(f"   ✅ SUCCESS! Found Data: '{data}'")
                    print(f"   🏆 WORKING URL FORMAT: {path}")
                    found_any = True
                else:
                    print(f"   ⚠️  FAIL: Empty Payload. Raw: {r.text[:150]}...")
            elif r.status_code == 404:
                print("   ❌ 404 Not Found")
            # else:
            #     print(f"   ❌ Error Status: {r.status_code}")

        except Exception as e:
            print(f"   🚨 Exception: {e}")

        print("-" * 40)

if __name__ == "__main__":
    probe()
