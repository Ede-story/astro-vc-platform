import traceback
import requests
from urllib.parse import quote
import json

def test_url(name, url):
    print(f"\n--- {name} ---")
    try:
        resp = requests.get(url, headers={"Accept": "application/json"})
        status = resp.status_code
        payload = "Error"
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)
            payload = root.find('Payload').text
        except:
            pass

        print(f"Status: {status}, Payload: '{payload}'")
    except Exception as e:
        print(f"Error: {e}")

base = "http://vedastro-engine/api"
loc = quote("London")
date_str = "01/01/1990"
day, month, year = "01", "01", "1990"
offset = quote("+00:00")
planet = "Sun"

base_nir = f"{base}/Location/{loc}/Time/{quote('12:00')}/{day}/{month}/{year}/{offset}/Planet/{planet}"

# House Brute Force
props = [
    "House",
    "HouseNumber",
    "Bhava",
    "BhavaNumber",
    "CurrentHouse",
    "HousePosition",
    "Position"
]

for p in props:
    test_url(f"Sun {p}", f"{base_nir}/{p}")

# Test Ascendant as Planet to get Lagna
base_asc = f"{base}/Location/{loc}/Time/{quote('12:00')}/{day}/{month}/{year}/{offset}/Planet/Lagba" # Typo check? usually Lagna or Ascendant
test_url("Ascendant Sign", f"{base}/Location/{loc}/Time/{quote('12:00')}/{day}/{month}/{year}/{offset}/Planet/Ascendant/Sign")
test_url("Lagna Sign", f"{base}/Location/{loc}/Time/{quote('12:00')}/{day}/{month}/{year}/{offset}/Planet/Lagna/Sign")
