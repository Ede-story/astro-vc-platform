import requests
import time

# Target: VedAstro Engine internal URL
BASE_URL = "http://vedastro-engine:80"

# Test Parameters
# Time string believed to be consumed by Time.FromUrl
TIME_STR = "Location/London/Time/12:00/24/11/2025/+00:00"

# Candidate Endpoints
PATTERNS = [
    # TRY WITHOUT /api PREFIX
    f"/Calculate/DayDurationHours/{TIME_STR}",
    f"/Calculate/PlanetNirayanaLongitude/PlanetName/Sun/{TIME_STR}",
    f"/Calculate/HousePlanetOccupiesBasedOnSign/PlanetName/Sun/{TIME_STR}",

    # TRY RESOURCE STYLE WITHOUT /api PREFIX
    f"/Location/London/Time/12:00/24/11/2025/+00:00/Planet/Sun/Sign",

    # TRY WITH /api PREFIX (Retest known failure)
    f"/api/Calculate/HousePlanetOccupiesBasedOnSign/PlanetName/Sun/{TIME_STR}",
]

def probe():
    print(f"--- PROBING CALCULATE METHODS at {BASE_URL} ---")
    for url_suffix in PATTERNS:
        full_url = f"{BASE_URL}{url_suffix}"
        print(f"Testing: {url_suffix} ... ", end="")
        try:
            resp = requests.get(full_url, timeout=5)
            content = resp.text.strip()
            status = resp.status_code
            print(f"Status: {status} | Len: {len(content)}")
            if status == 200:
                 print(f"   >>> SUCCESS? Content: {content[:100]}")
        except Exception as e:
            print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    probe()
