#!/usr/bin/env python3
"""
AUDIT SCRIPT: Deep Storage Data Integrity Verification
=======================================================
This script verifies that saved profiles contain the full Digital Twin
with all 16 Varga charts and complete metadata.

Author: StarMeet Team
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Expected Varga codes (16 total)
EXPECTED_VARGAS = ['D1', 'D2', 'D3', 'D4', 'D7', 'D9', 'D10', 'D12',
                   'D16', 'D20', 'D24', 'D27', 'D30', 'D40', 'D45', 'D60']

# Required planet fields for Deep Storage
REQUIRED_PLANET_FIELDS = [
    'name', 'sign_id', 'sign_name', 'absolute_degree', 'relative_degree',
    'house_occupied', 'houses_owned', 'nakshatra', 'nakshatra_lord',
    'nakshatra_pada', 'sign_lord', 'dignity_state', 'aspects_giving_to',
    'aspects_receiving_from', 'conjunctions'
]

# Required house fields
REQUIRED_HOUSE_FIELDS = [
    'house_number', 'sign_id', 'sign_name', 'lord', 'occupants', 'aspects_received'
]


def print_separator(title: str = ""):
    """Print a visual separator."""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def audit_profile(profile_path: str):
    """
    Perform deep audit of a saved profile.

    Args:
        profile_path: Path to the JSON profile file
    """
    print_separator("DEEP STORAGE AUDIT REPORT")
    print(f"Audit Time: {datetime.now().isoformat()}")
    print(f"Profile File: {profile_path}")

    # Load profile
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    # Basic info
    print(f"\nProfile ID: {profile.get('id', 'N/A')}")
    print(f"Created At: {profile.get('created_at', 'N/A')}")

    input_data = profile.get('input', {})
    print(f"Profile Name: {input_data.get('name', 'N/A')}")
    print(f"Birth Date: {input_data.get('date', 'N/A')} {input_data.get('time', 'N/A')}")
    print(f"Location: {input_data.get('city', 'N/A')} ({input_data.get('lat', 0)}, {input_data.get('lon', 0)})")

    # Check for Digital Twin
    digital_twin = profile.get('digital_twin')

    if not digital_twin:
        print("\n❌ CRITICAL ERROR: No 'digital_twin' key found in profile!")
        print("   This profile was saved BEFORE Digital Twin implementation.")
        print("   Re-save the profile to generate Digital Twin data.")
        return False

    print_separator("A. VARGA CHECKLIST (16 Divisional Charts)")

    vargas = digital_twin.get('vargas', {})
    present_vargas = list(vargas.keys())

    print(f"\nTotal Vargas Found: {len(present_vargas)}")
    print("\nVarga Status:")

    all_present = True
    for varga in EXPECTED_VARGAS:
        status = "✓ PRESENT" if varga in present_vargas else "✗ MISSING"
        if varga not in present_vargas:
            all_present = False
        print(f"  {varga:4} ... {status}")

    # Check for unexpected vargas
    unexpected = set(present_vargas) - set(EXPECTED_VARGAS)
    if unexpected:
        print(f"\n⚠ Unexpected Vargas: {list(unexpected)}")

    print(f"\nVarga Checklist Result: {'✓ ALL 16 PRESENT' if all_present else '✗ INCOMPLETE'}")

    print_separator("B. DATA DEPTH CHECK (D10 - Dashamsha)")

    d10 = vargas.get('D10', {})

    if not d10:
        print("❌ D10 data not found!")
        return False

    # Ascendant info
    asc = d10.get('ascendant', {})
    print(f"\nD10 Ascendant:")
    print(f"  Sign: {asc.get('sign_name', 'N/A')} (ID: {asc.get('sign_id', 'N/A')})")
    print(f"  Degrees: {asc.get('degrees', 'N/A')}°")

    # Find Sun in D10
    planets = d10.get('planets', [])
    sun_d10 = None

    for planet in planets:
        if planet.get('name') == 'Sun':
            sun_d10 = planet
            break

    if not sun_d10:
        print("\n❌ Sun not found in D10 planets!")
        return False

    print("\n" + "-" * 50)
    print("RAW D10 SUN OBJECT:")
    print("-" * 50)
    print(json.dumps(sun_d10, indent=2, ensure_ascii=False))
    print("-" * 50)

    # Field verification
    print("\nFIELD VERIFICATION (Sun in D10):")

    critical_fields = {
        'absolute_degree': sun_d10.get('absolute_degree'),
        'dignity_state': sun_d10.get('dignity_state'),
        'nakshatra_lord': sun_d10.get('nakshatra_lord'),
        'houses_owned': sun_d10.get('houses_owned'),
        'aspects_giving_to': sun_d10.get('aspects_giving_to'),
        'house_occupied': sun_d10.get('house_occupied'),
        'sign_name': sun_d10.get('sign_name'),
        'relative_degree': sun_d10.get('relative_degree'),
        'conjunctions': sun_d10.get('conjunctions'),
        'aspects_receiving_from': sun_d10.get('aspects_receiving_from'),
    }

    all_fields_present = True
    for field, value in critical_fields.items():
        status = "✓" if value is not None else "✗"
        if value is None:
            all_fields_present = False
        value_str = str(value) if value is not None else "MISSING"
        # Truncate long values
        if len(value_str) > 50:
            value_str = value_str[:47] + "..."
        print(f"  {status} {field:25} = {value_str}")

    # Check all required planet fields
    print("\n  Full Planet Schema Check:")
    missing_fields = []
    for field in REQUIRED_PLANET_FIELDS:
        if field not in sun_d10:
            missing_fields.append(field)

    if missing_fields:
        print(f"  ✗ Missing fields: {missing_fields}")
    else:
        print(f"  ✓ All {len(REQUIRED_PLANET_FIELDS)} required fields present")

    # House data check
    print("\nD10 HOUSE DATA CHECK:")
    houses = d10.get('houses', [])
    print(f"  Houses found: {len(houses)}")

    if houses:
        house1 = houses[0]
        print(f"\n  Sample (House 1):")
        print(f"    Sign: {house1.get('sign_name', 'N/A')}")
        print(f"    Lord: {house1.get('lord', 'N/A')}")
        print(f"    Occupants: {house1.get('occupants', [])}")
        print(f"    Aspects: {house1.get('aspects_received', [])}")

        # Check house schema
        missing_house_fields = []
        for field in REQUIRED_HOUSE_FIELDS:
            if field not in house1:
                missing_house_fields.append(field)

        if missing_house_fields:
            print(f"  ✗ Missing house fields: {missing_house_fields}")
        else:
            print(f"  ✓ All {len(REQUIRED_HOUSE_FIELDS)} required house fields present")

    print_separator("C. STORAGE SIZE ANALYSIS")

    # Calculate sizes
    profile_size = len(json.dumps(profile, ensure_ascii=False))
    digital_twin_size = len(json.dumps(digital_twin, ensure_ascii=False))
    chart_size = len(json.dumps(profile.get('chart', {}), ensure_ascii=False))

    print(f"\nTotal Profile Size: {profile_size / 1024:.2f} KB")
    print(f"Digital Twin Size:  {digital_twin_size / 1024:.2f} KB")
    print(f"Legacy Chart Size:  {chart_size / 1024:.2f} KB")
    print(f"Input Data Size:    {len(json.dumps(input_data)) / 1024:.2f} KB")

    # Per-varga breakdown
    print("\nPer-Varga Size Breakdown (KB):")
    varga_sizes = []
    for varga_code in EXPECTED_VARGAS[:4]:  # Sample first 4
        varga_data = vargas.get(varga_code, {})
        size = len(json.dumps(varga_data, ensure_ascii=False))
        varga_sizes.append(size)
        print(f"  {varga_code}: {size / 1024:.2f} KB")

    avg_varga_size = sum(varga_sizes) / len(varga_sizes) if varga_sizes else 0
    print(f"  (Average per Varga: {avg_varga_size / 1024:.2f} KB)")

    print_separator("FINAL VERDICT")

    # Calculate verdict
    checks = {
        'All 16 Vargas Present': all_present,
        'Digital Twin Structure': digital_twin is not None,
        'D10 Sun Data Complete': all_fields_present,
        'Houses Data Present': len(houses) == 12,
        '9 Planets in D10': len(planets) == 9,
    }

    print("\nChecklist Results:")
    all_passed = True
    for check, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        if not result:
            all_passed = False
        print(f"  [{status}] {check}")

    print("\n" + "=" * 70)
    if all_passed:
        print("  ✓ AUDIT PASSED - Deep Storage implementation is COMPLETE")
    else:
        print("  ✗ AUDIT FAILED - Some checks did not pass")
    print("=" * 70 + "\n")

    return all_passed


def main():
    """Main entry point."""
    profiles_dir = Path("/app/data/profiles")

    if not profiles_dir.exists():
        print(f"Profiles directory not found: {profiles_dir}")
        sys.exit(1)

    # Get all profiles sorted by modification time (newest first)
    profiles = sorted(profiles_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not profiles:
        print("No profiles found!")
        sys.exit(1)

    print(f"\nFound {len(profiles)} profile(s)")
    print(f"Auditing newest profile: {profiles[0].name}\n")

    # Audit the newest profile
    success = audit_profile(str(profiles[0]))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
