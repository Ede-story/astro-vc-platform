"""
Quick test script to verify VedAstro installation and basic functionality
"""

import sys
from datetime import datetime

def test_vedastro_import():
    """Test if VedAstro can be imported"""
    try:
        import vedastro
        print("✅ VedAstro imported successfully")
        print(f"   Version: {vedastro.__version__ if hasattr(vedastro, '__version__') else 'Unknown'}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import VedAstro: {e}")
        return False

def test_vedastro_calculation():
    """Test basic birth chart calculation"""
    try:
        from vedastro import Calculate, GeoLocation, Time, PlanetName, HouseName
        import json

        print("\n🧪 Testing basic calculation...")

        # Create test birth data
        geo = GeoLocation("Tokyo, Japan", 139.83, 35.65)
        birth_time = Time("23:40 31/12/2010 +08:00", geo)

        print(f"   Birth location: Tokyo, Japan (139.83, 35.65)")
        print(f"   Birth time: 23:40 31/12/2010 +08:00")

        # Calculate Sun position
        print("\n   Calculating Sun position...")
        sun_data = Calculate.AllPlanetData(PlanetName.Sun, birth_time)

        if sun_data:
            print("✅ Birth chart calculation successful!")
            print(f"   Sun data type: {type(sun_data)}")

            # Try to show some data if it's a list/dict
            if isinstance(sun_data, (list, dict)):
                data_str = json.dumps(sun_data, indent=2)
                print(f"   Sun data sample: {data_str[:200]}...")

            return True
        else:
            print("❌ Birth chart calculation returned no data")
            return False

    except Exception as e:
        print(f"❌ Calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_redis():
    """Test Redis connection"""
    try:
        import redis
        print("\n🔌 Testing Redis connection...")

        # Try to connect to localhost Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()

        print("✅ Redis connection successful")

        # Test set/get
        test_key = "test_vedastro_key"
        test_value = "Hello from VedAstro!"
        r.setex(test_key, 10, test_value)  # Expire in 10 seconds
        retrieved = r.get(test_key)

        if retrieved == test_value:
            print(f"   ✅ Redis set/get working: {retrieved}")
            r.delete(test_key)
            return True
        else:
            print("   ❌ Redis set/get mismatch")
            return False

    except Exception as e:
        print(f"⚠️  Redis not available: {e}")
        print("   (This is OK for initial setup - Redis is optional)")
        return None  # Not critical

def main():
    """Run all tests"""
    print("=" * 60)
    print("VedAstro Installation Test Suite")
    print("=" * 60)

    results = {
        "Import": test_vedastro_import(),
        "Calculation": False,
        "Redis": None
    }

    if results["Import"]:
        results["Calculation"] = test_vedastro_calculation()

    results["Redis"] = test_redis()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"{test:20} {status}")

    # Final verdict
    critical_tests_passed = results["Import"] and results["Calculation"]

    if critical_tests_passed:
        print("\n🎉 All critical tests passed! VedAstro is ready to use.")
        return 0
    else:
        print("\n❌ Some critical tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
