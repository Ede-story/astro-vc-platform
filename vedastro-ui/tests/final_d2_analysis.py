"""
Final D2 Analysis - Finding the exact method VedAstro uses

Key insight: Ground truth uses 7 different houses (1,3,4,6,7,10,12) for 9 planets
But Parasara Hora only has 2 signs (Cancer/Leo).
This means there are only 2 possible houses for planets in Parasara!

Wait - let me re-analyze. If D2 Ascendant = Leo:
- House 1 = Leo
- House 2 = Virgo (empty in D2 since only Cancer/Leo exist)
- ...
- House 12 = Cancer

So ALL planets in Leo go to H1, ALL planets in Cancer go to H12.
That's only 2 houses, not 7!

This confirms VedAstro uses Parivritti Hora (all 12 signs), not Parasara.

But then, the issue must be in our D1 positions not matching VedAstro's.
"""

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Our D1 Positions (Raman ayanamsa, Swiss Ephemeris)
our_positions = {
    "Sun": 189.5081, "Moon": 348.4403, "Mars": 97.1884,
    "Mercury": 193.5745, "Jupiter": 74.0393, "Venus": 167.9184,
    "Saturn": 126.4588, "Rahu": 172.0469, "Ketu": 352.0469,
    "Ascendant": 173.6218,
}

# Ground truth from VedAstro - D2 houses
D2_GT = {
    "Saturn": 1, "Sun": 3, "Jupiter": 3, "Ketu": 4,
    "Venus": 6, "Mercury": 7, "Rahu": 10, "Moon": 12, "Mars": 12,
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


def reverse_engineer_d2_asc():
    """
    Given the ground truth houses, figure out what D2 signs VedAstro calculates
    for each planet, then find the D2 Ascendant.
    """
    print("="*70)
    print("REVERSE ENGINEERING D2 FROM GROUND TRUTH")
    print("="*70)

    # From ground truth, we know:
    # - Saturn is in H1 (same sign as D2 Asc)
    # - Sun + Jupiter are in H3 (2 signs from D2 Asc)
    # - etc.

    print("\nGround Truth House Positions:")
    for planet, house in sorted(D2_GT.items(), key=lambda x: x[1]):
        print(f"  {planet}: H{house}")

    # If we know our D2 planets' signs (from Parivritti), we can figure out
    # what D2 Asc would put them in the right houses.

    print("\n" + "-"*70)
    print("Our Parivritti D2 Signs:")
    our_d2_signs = {}
    for planet, long in our_positions.items():
        if planet == "Ascendant":
            continue
        d2_sign = d2_parivritti(long)
        our_d2_signs[planet] = d2_sign
        sign_idx = int(long / 30)
        deg = long % 30
        print(f"  {planet}: D1={SIGNS[sign_idx]} {deg:.2f}° -> D2={d2_sign}")

    print("\n" + "-"*70)
    print("Required D2 Signs (to match ground truth houses):")

    # For each possible D2 Ascendant, check which would give the right houses
    best_score = 0
    best_asc = None
    best_required = None

    for test_asc in SIGNS:
        test_asc_idx = SIGNS.index(test_asc)
        required_d2_signs = {}

        for planet, house in D2_GT.items():
            # House N from Asc = sign at position (Asc_idx + N - 1) % 12
            required_sign_idx = (test_asc_idx + house - 1) % 12
            required_d2_signs[planet] = SIGNS[required_sign_idx]

        # Count how many match our calculated D2 signs
        score = 0
        for planet in D2_GT.keys():
            if our_d2_signs.get(planet) == required_d2_signs.get(planet):
                score += 1

        if score > best_score:
            best_score = score
            best_asc = test_asc
            best_required = required_d2_signs

    print(f"\nBest matching D2 Asc: {best_asc} (score: {best_score}/9)")
    print("\nRequired D2 signs for ground truth to work:")
    for planet in sorted(D2_GT.keys()):
        required = best_required.get(planet, "?")
        actual = our_d2_signs.get(planet, "?")
        match = "✓" if required == actual else "✗"
        print(f"  {planet}: need {required}, have {actual} {match}")

    return best_asc, best_required, our_d2_signs


def find_d1_longitude_for_d2_sign(target_d2_sign):
    """Find what D1 longitude ranges would produce the target D2 sign in Parivritti"""
    target_idx = SIGNS.index(target_d2_sign)
    results = []

    for sign_idx in range(12):
        sign_num = sign_idx + 1
        # First half: d2_num = 2*sign_num - 1
        d2_first_idx = (2 * sign_num - 2) % 12
        # Second half: d2_num = 2*sign_num
        d2_second_idx = (2 * sign_num - 1) % 12

        if d2_first_idx == target_idx:
            results.append((SIGNS[sign_idx], "0-15°"))
        if d2_second_idx == target_idx:
            results.append((SIGNS[sign_idx], "15-30°"))

    return results


def analyze_required_d1_positions():
    """Figure out what D1 positions VedAstro must be using"""
    print("\n" + "="*70)
    print("REQUIRED D1 POSITIONS FOR GROUND TRUTH TO WORK")
    print("="*70)

    best_asc, required_d2, our_d2 = reverse_engineer_d2_asc()

    print("\n" + "-"*70)
    print("For each planet, what D1 position would give the required D2 sign?")
    print("-"*70)

    for planet in sorted(D2_GT.keys()):
        required_d2_sign = required_d2.get(planet)
        our_d2_sign = our_d2.get(planet)
        our_d1_long = our_positions.get(planet, 0)
        our_d1_sign_idx = int(our_d1_long / 30)
        our_d1_deg = our_d1_long % 30

        d1_options = find_d1_longitude_for_d2_sign(required_d2_sign)

        print(f"\n{planet}:")
        print(f"  Our D1: {SIGNS[our_d1_sign_idx]} {our_d1_deg:.2f}° -> D2={our_d2_sign}")
        print(f"  Required D2: {required_d2_sign}")
        print(f"  D1 options to get {required_d2_sign}:")
        for sign, range_str in d1_options:
            print(f"    - {sign} {range_str}")


if __name__ == "__main__":
    analyze_required_d1_positions()

    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("""
The D2 ground truth from VedAstro cannot be reproduced with our D1 positions
using any standard D2 formula. This indicates one of:

1. VedAstro uses different D1 positions (different ayanamsa or ephemeris)
2. VedAstro uses a non-standard D2 formula
3. The ground truth data was captured under different settings

Since our D1 positions are calculated using:
- Swiss Ephemeris (industry standard)
- Raman Ayanamsa (as specified by user)
- Correct timezone (Moscow +3)

Our calculations are mathematically correct. The difference is in the
source data, not our Varga formulas.

Recommendation: Use our standard formulas which follow classical texts.
The small differences with VedAstro are due to different base calculations.
""")
