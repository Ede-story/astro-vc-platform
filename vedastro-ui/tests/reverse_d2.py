"""
Reverse engineer D2 Ascendant from VedAstro ground truth
"""

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Ground truth from VedAstro
# D2: Saturn H1, Sun+Jupiter H3, Ketu H4, Venus H6, Mercury H7, Rahu H10, Moon+Mars H12
D2_GT = {
    "Saturn": 1,
    "Sun": 3,
    "Jupiter": 3,
    "Ketu": 4,
    "Venus": 6,
    "Mercury": 7,
    "Rahu": 10,
    "Moon": 12,
    "Mars": 12,
}

# D1 Positions (Raman ayanamsa)
positions = {
    "Sun": 189.5081, "Moon": 348.4403, "Mars": 97.1884,
    "Mercury": 193.5745, "Jupiter": 74.0393, "Venus": 167.9184,
    "Saturn": 126.4588, "Rahu": 172.0469, "Ketu": 352.0469,
    "Ascendant": 173.6218,
}


def d2_parivritti(longitude):
    """Parivritti/Vriddhakarika: 2N-1, 2N formula"""
    sign_idx = int(longitude / 30)
    deg = longitude % 30
    sign_num = sign_idx + 1
    first_half = (deg < 15)
    if first_half:
        d2_num = (2 * sign_num - 1)
    else:
        d2_num = (2 * sign_num)
    d2_idx = (d2_num - 1) % 12
    return SIGNS[d2_idx]


def d2_parivritti_v2(longitude):
    """Alternative Parivritti - different half determination"""
    sign_idx = int(longitude / 30)
    deg = longitude % 30
    sign_num = sign_idx + 1
    # Try: first half includes 15 degrees (0-15)
    first_half = (deg <= 15)
    if first_half:
        d2_num = (2 * sign_num - 1)
    else:
        d2_num = (2 * sign_num)
    d2_idx = (d2_num - 1) % 12
    return SIGNS[d2_idx]


print("="*70)
print("REVERSE ENGINEERING D2 ASCENDANT FROM GROUND TRUTH")
print("="*70)

# Step 1: Calculate D2 signs for all planets using Parivritti
print("\nPlanets' D2 signs (Parivritti method):")
planet_d2_signs = {}
for planet, long in positions.items():
    if planet == "Ascendant":
        continue
    d2_sign = d2_parivritti(long)
    planet_d2_signs[planet] = d2_sign
    sign_idx = int(long / 30)
    deg = long % 30
    print(f"  {planet}: D1={SIGNS[sign_idx]} {deg:.2f}° -> D2={d2_sign}")

# Step 2: From ground truth, derive D2 Ascendant
print("\n" + "="*70)
print("DERIVING D2 ASCENDANT FROM GROUND TRUTH")
print("="*70)

# Saturn is in H1, so D2 Asc = Saturn's D2 sign
# Saturn D2 = Capricorn (from Parivritti)
# So D2 Asc should be Capricorn for Saturn to be in H1

print("\nIf Saturn is in H1, then D2 Asc = Saturn's D2 sign")
saturn_d2 = planet_d2_signs["Saturn"]
print(f"Saturn D2 sign: {saturn_d2}")
print(f"Therefore, D2 Ascendant should be: {saturn_d2}")

# Step 3: Verify with this ascendant
print("\n" + "="*70)
print(f"VERIFICATION WITH D2 ASC = {saturn_d2}")
print("="*70)

asc_idx = SIGNS.index(saturn_d2)
calculated_houses = {}

for planet, d2_sign in planet_d2_signs.items():
    sign_idx = SIGNS.index(d2_sign)
    house = ((sign_idx - asc_idx) % 12) + 1
    if house not in calculated_houses:
        calculated_houses[house] = []
    calculated_houses[house].append(planet)
    print(f"  {planet}: D2={d2_sign} -> H{house}")

print(f"\nCalculated with D2 Asc = {saturn_d2}:")
for h in sorted(calculated_houses.keys()):
    print(f"  H{h}: {calculated_houses[h]}")

print(f"\nGround Truth:")
gt_by_house = {}
for planet, house in D2_GT.items():
    if house not in gt_by_house:
        gt_by_house[house] = []
    gt_by_house[house].append(planet)
for h in sorted(gt_by_house.keys()):
    print(f"  H{h}: {gt_by_house[h]}")

# Check matches
match = 0
total = len(D2_GT)
for planet, expected_house in D2_GT.items():
    d2_sign = planet_d2_signs.get(planet)
    if d2_sign:
        sign_idx = SIGNS.index(d2_sign)
        calc_house = ((sign_idx - asc_idx) % 12) + 1
        if calc_house == expected_house:
            match += 1
            status = "✓"
        else:
            status = f"✗ (got H{calc_house})"
        print(f"  {planet}: expected H{expected_house} {status}")

print(f"\nMatch: {match}/{total}")

# Step 4: Try all possible D2 Ascendants
print("\n" + "="*70)
print("TRYING ALL POSSIBLE D2 ASCENDANTS")
print("="*70)

best_match = 0
best_asc = None

for test_asc in SIGNS:
    test_asc_idx = SIGNS.index(test_asc)
    match_count = 0

    for planet, expected_house in D2_GT.items():
        d2_sign = planet_d2_signs.get(planet)
        if d2_sign:
            sign_idx = SIGNS.index(d2_sign)
            calc_house = ((sign_idx - test_asc_idx) % 12) + 1
            if calc_house == expected_house:
                match_count += 1

    if match_count >= best_match:
        if match_count > best_match:
            best_match = match_count
            best_asc = test_asc
        print(f"  D2 Asc = {test_asc}: {match_count}/9 matches")

print(f"\nBest match: D2 Asc = {best_asc} with {best_match}/9")

# Step 5: Check what D1 Ascendant longitude would give the best D2 Asc
print("\n" + "="*70)
print("CHECKING D1 ASCENDANT REQUIREMENTS")
print("="*70)

if best_asc:
    best_asc_idx = SIGNS.index(best_asc)
    # For Parivritti: D2 sign = (2*N - 1) or (2*N) mod 12
    # So we need to find which D1 signs map to best_asc

    print(f"\nTo get D2 Asc = {best_asc}, D1 Asc needs to be in:")

    for sign_idx in range(12):
        sign_num = sign_idx + 1
        # First half: (2*N - 1) - 1 = 2N - 2 mod 12
        d2_first = (2 * sign_num - 2) % 12
        # Second half: (2*N) - 1 = 2N - 1 mod 12
        d2_second = (2 * sign_num - 1) % 12

        if d2_first == best_asc_idx:
            print(f"  {SIGNS[sign_idx]} 0°-15° -> D2 = {best_asc}")
        if d2_second == best_asc_idx:
            print(f"  {SIGNS[sign_idx]} 15°-30° -> D2 = {best_asc}")

    print(f"\nCurrent D1 Asc: Virgo 23.62° -> D2 = {d2_parivritti(positions['Ascendant'])}")
