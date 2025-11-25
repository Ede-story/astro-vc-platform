import requests
import sys

# Используем localhost:3001 т.к. скрипт будем запускать с хоста VM,
# где порт 3001 проброшен в контейнер vedastro-api:80
BASE_URL = "http://localhost:3001"

TEST_VECTORS = [
    # Стандартный формат VedAstro (из документации)
    # /Calculate/{CalculatorName}/{Arg1}/{Val1}/{Arg2}/{Val2}...

    # Попытка 1: Полный формат
    "/api/Calculate/PlanetName/Sun/Sign/Location/Singapore/Time/12:00/22/12/2022/+08:00",

    # Попытка 2: Без /api
    "/Calculate/PlanetName/Sun/Sign/Location/Singapore/Time/12:00/22/12/2022/+08:00",

    # Попытка 3: PlanetSign калькулятор (прямой вызов)
    "/api/Calculate/PlanetSign/PlanetName/Sun/Location/Singapore/Time/12:00/22/12/2022/+08:00",

    # Попытка 4: Просто проверка живости (HelloWorld)
    "/api/Home/HelloWorld", # обычно есть такой метод в Azure Functions/VedAstro
    "/api",
    "/"
]

def probe():
    print(f"🔍 Probing VedAstro API at {BASE_URL}...")

    success = False

    for path in TEST_VECTORS:
        url = f"{BASE_URL}{path}"
        print(f"👉 Trying: {url}")
        try:
            r = requests.get(url, timeout=3)
            print(f"   Status: {r.status_code}")

            if r.status_code == 200:
                print(f"   ✅ SUCCESS! Response: {r.text[:200]}")
                success = True
            elif r.status_code == 404:
                 print(f"   ❌ 404 Not Found")
            else:
                 print(f"   ⚠️ {r.status_code}")

        except Exception as e:
            print(f"   🚨 Connection Error: {e}")

    if not success:
        print("\n❌ No working endpoints found.")
        sys.exit(1)
    else:
        print("\n✅ Found working endpoints.")

if __name__ == "__main__":
    probe()
