import requests
import json
import time

# Target: VedAstro Engine internal URL
BASE_URL = "http://vedastro-engine:80"

# Test Parameters
LOCATION = "Location/London/Time/12:00/24/11/2025/+00:00"
PLANET = "PlanetName/Sun"
AYANAMSA = "/Ayanamsa/Lahiri"

# SANITY CHECK (Known working from v3?)
KNOWN_GOOD_URL = "/api/Calculate/PlanetNirayanaLongitude/PlanetName/Sun/Location/London/Time/12:00/01/01/1990/+00:00"

# Candidate Endpoints to probe
PATTERNS = [
    # Method Names in Resource Style
    f"/api/{LOCATION}/Planet/Sun/HousePlanetOccupies",
    f"/api/{LOCATION}/Planet/Sun/HousePlanetOccupiesBasedOnSign",
    f"/api/{LOCATION}/Planet/Sun/HousePlanetOccupiesBasedOnLongitudes",
    f"/api/{LOCATION}/Planet/Sun/PlanetToHouse",

    # Check Lord Relationship
    f"/api/{LOCATION}/House/House1/Lord",
    f"/api/{LOCATION}/House/House1/LordOfHouse",
    f"/api/{LOCATION}/House/1/Lord",

    # Check All Planet Data again specifically via Location style?
    f"/api/{LOCATION}/Planet/Sun/AllPlanetData",

    # Check Ascendant again
    f"/api/{LOCATION}/Planet/Lagna/Sign", # Failed "Parse"
    # Maybe "Lagna" is House1?

    # Check Strength
    f"/api/{LOCATION}/Planet/Sun/ShadbalaPinda",
    f"/api/{LOCATION}/Planet/Sun/IsPlanetInKendra",
]

def probe():
    print(f"--- PROBING VEDASTRO HOUSE APIs at {BASE_URL} ---")
    results = []

    for url_suffix in PATTERNS:
        full_url = f"{BASE_URL}{url_suffix}"
        print(f"Testing: {url_suffix} ... ", end="")
        try:
            start = time.time()
            resp = requests.get(full_url, timeout=5)
            # Try to see if it returns a valid number or JSON
            content = resp.text.strip()
            status = resp.status_code

            # Simple heuristic: Success if 200 and content is not empty error
            is_success = status == 200 and "<html" not in content and "Error" not in content

            print(f"Status: {status} | Len: {len(content)}")
            if is_success:
                 print(f"   >>> SUCCESS? Content: {content[:100]}")
                 results.append((url_suffix, content))
            else:
                 pass # print(f"   >>> FAIL: {content[:50]}")

        except Exception as e:
            print(f"EXCEPTION: {e}")

    print("\n--- SUMMARY OF WORKING APIs ---")
    if not results:
        print("No successful endpoints found.")
    else:
        for r in results:
            print(f"URL: {r[0]}")
            print(f"RES: {r[1]}\n")

if __name__ == "__main__":
    probe()
