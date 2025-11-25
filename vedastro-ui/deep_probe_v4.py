import requests
import sys
import xml.etree.ElementTree as ET

BASE_URL = "http://vedastro-engine"
LOC = "Location/London"
TIME = "Time/12:00/01/01/1990/+00:00"

# Trying to get BULK data to calculate locally if needed
VECTORS = [
    # 1. All Planet Longitudes
    f"/api/Calculate/AllPlanetLongitude/{LOC}/{TIME}",
    f"/api/Calculate/AllPlanetFixedLongitude/{LOC}/{TIME}",

    # 2. All House Longitudes
    f"/api/Calculate/AllHouseLongitudes/{LOC}/{TIME}", # Returns List<House>
    f"/api/Calculate/GetAllHouseNirayanaMiddleLongitudes/{LOC}/{TIME}", # returns double[]

    # 3. Ketu Sign check
    f"/api/{LOC}/{TIME}/Planet/Ketu/Sign",
    f"/api/{LOC}/{TIME}/Planet/Rahu/Sign",
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
    print("🔬 DEEP PROBE V4 - Bulk Data & Ketu Check")

    for url_path in VECTORS:
        full_url = BASE_URL + url_path
        print(f"👉 {url_path}")
        try:
            r = requests.get(full_url, timeout=10)
            if r.status_code == 200:
                val = check_payload(r.text)
                if val:
                    print(f"   ✅ FOUND: {val[:100]}...")
                else:
                    # Check if JSON
                    stripped = r.text.strip()
                    if stripped.startswith("[") or stripped.startswith("{"):
                         print(f"   ✅ FOUND JSON: {stripped[:100]}...")
                    else:
                         print(f"   ⚠️  EMPTY PAYLOAD. Raw: {r.text[:50]}")
            else:
                print(f"   ❌ {r.status_code}")
        except Exception as e:
            print(f"   🚨 ERR: {e}")
        print("-" * 20)

if __name__ == "__main__":
    probe()
