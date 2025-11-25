import requests
import json

API_BASE = "http://vedastro-engine/api"

def check_endpoint(url, description):
    print(f"\n--- Testing: {description} ---")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.text[:200]}")
            return response.text
        else:
            print(f"Error Status")
    except Exception as e:
        print(f"Exception: {e}")

def main():
    print("Starting Ketu Anomaly Investigation - Phase 10: Final House Probe...")

    base_params = "Location/London/Time/06:28/25/10/1977/+00:00"

    # 1. Test HouseSystem Injection
    # smart_probe suggested: /api/{LOC}/{TIME}/{HOUSE_SYS}/Planet/Sun/HousePlanetOccupies
    check_endpoint(f"{API_BASE}/{base_params}/HouseSystem/Raman/Planet/Sun/HousePlanetOccupies", "HouseSystem/Raman/Planet/Sun/HousePlanetOccupies")

    # 2. Test Post-Planet Injection
    check_endpoint(f"{API_BASE}/{base_params}/Planet/Sun/HouseSystem/Raman/House", "Planet/Sun/HouseSystem/Raman/House")

    # 3. Test Ayanamsa (Value check)
    check_endpoint(f"{API_BASE}/{base_params}/Ayanamsa", "Ayanamsa Check")
    check_endpoint(f"{API_BASE}/{base_params}/AyanamsaDegree", "AyanamsaDegree Check")

    # 4. Test Sidereal Sign directly?
    # Maybe 'NirayanaSign'?
    check_endpoint(f"{API_BASE}/{base_params}/Planet/Ketu/NirayanaSign", "Planet/Ketu/NirayanaSign")

if __name__ == "__main__":
    main()
