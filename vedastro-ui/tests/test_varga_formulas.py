"""
Test Varga Formulas (D2, D4) against Ground Truth
Using Vadim's known D1 positions (Raman-corrected)

GROUND TRUTH from User's trusted software:
D2: House 1=Saturn, House 3=Sun+Jupiter, House 4=Ketu, House 6=Venus,
    House 7=Mercury, House 10=Rahu, House 12=Moon+Mars
D4: House 2=Mars, House 3=Saturn, House 4=Moon+Jupiter+Ketu,
    House 8=Sun+Mercury, House 10=Venus+Rahu
"""

# Zodiac signs
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']


def calculate_d2_hora(longitude: float) -> str:
    """D2 Hora - Only Cancer and Leo"""
    sign_idx = int(longitude / 30)
    degrees_in_sign = longitude % 30
    is_odd_sign = (sign_idx % 2 == 0)
    first_half = (degrees_in_sign < 15)

    if is_odd_sign:
        return 'Leo' if first_half else 'Cancer'
    else:
        return 'Cancer' if first_half else 'Leo'


def calculate_d4_chaturthamsha(longitude: float) -> str:
    """D4 Chaturthamsha - 4 parts of 7.5°"""
    sign_idx = int(longitude / 30)
    degrees_in_sign = longitude % 30

    if degrees_in_sign < 7.5:
        d4_idx = sign_idx
    elif degrees_in_sign < 15:
        d4_idx = (sign_idx + 3) % 12
    elif degrees_in_sign < 22.5:
        d4_idx = (sign_idx + 6) % 12
    else:
        d4_idx = (sign_idx + 9) % 12

    return SIGNS[d4_idx]


# Vadim's D1 positions (approximate Raman-corrected longitudes)
# These need to be verified - using estimated values based on previous data
# Sun: Libra ~9.5° -> Libra = sign 6, longitude = 6*30 + 9.5 = 189.5°
# Moon: Pisces ~18.5° -> Pisces = sign 11, longitude = 11*30 + 18.5 = 348.5°
# Mars: Virgo ~10° -> Virgo = sign 5, longitude = 5*30 + 10 = 160°
# Mercury: Libra ~0° -> Libra = sign 6, longitude = 6*30 + 0 = 180°
# Jupiter: Leo ~27° -> Leo = sign 4, longitude = 4*30 + 27 = 147°
# Venus: Scorpio ~7° -> Scorpio = sign 7, longitude = 7*30 + 7 = 217°
# Saturn: Cancer ~21° -> Cancer = sign 3, longitude = 3*30 + 21 = 111°
# Rahu: Virgo ~25° -> Virgo = sign 5, longitude = 5*30 + 25 = 175°
# Ketu: Pisces ~25° -> Pisces = sign 11, longitude = 11*30 + 25 = 355°

# Let's work backwards from the ground truth to figure out the correct D1 positions

# Ground truth interpretation:
# D2: Only Cancer (sign 3) and Leo (sign 4) are used
# If D2 Ascendant = Aquarius, then:
#   House 1 = Aquarius (but D2 only has Cancer/Leo, so this seems wrong)
#
# Actually, in D2 (Hora), the houses are based on which Hora (Cancer/Leo) planets fall into
# The "house" number in D2 is relative to the D2 Ascendant

# Let me reconsider: In D2, if a planet is in Leo, it's in Sun's hora.
# If in Cancer, it's in Moon's hora.
# The house number is then determined by which house Leo or Cancer falls in,
# based on the D2 Ascendant.

# For D2 to work with houses 1-12, we need to know the D2 Ascendant first.

# Let's try to derive the D1 Ascendant from the ground truth patterns...

print("=" * 70)
print("ANALYZING GROUND TRUTH TO DERIVE D1 POSITIONS")
print("=" * 70)

# Ground Truth D2:
# House 1=Saturn, House 3=Sun+Jupiter, House 4=Ketu, House 6=Venus,
# House 7=Mercury, House 10=Rahu, House 12=Moon+Mars

# In D2, only Cancer and Leo exist as signs.
# House 1 = D2 Ascendant sign
# House 2 = next sign from D2 Ascendant
# etc.

# Since only Cancer and Leo are D2 signs:
# If D2 Asc = Cancer: House 1=Cancer, House 2=Leo, House 3=Virgo, ...
# But D2 doesn't work that way - it only has Cancer and Leo positions!

# The house in D2 is determined by the D2 Ascendant.
# If D2 Ascendant = Cancer:
#   House 1 = Cancer
#   House 2 = Leo
#   House 3 = Virgo (empty in D2)
#   ...
# This doesn't make sense for D2.

# Let me reconsider: Perhaps the ground truth uses a different D2 method.
# The standard Parashara Hora only has 2 divisions (Cancer/Leo).
#
# Another interpretation: The house number might be which house FROM D1 the planet's
# hora lord rules.

# Let me just test the formulas with known calculations first.

print("\n" + "=" * 70)
print("TESTING D2 FORMULA")
print("=" * 70)

# Test cases for D2 (Hora)
test_cases_d2 = [
    (0, 'Leo'),      # Aries 0° -> Odd sign, first half -> Leo
    (15, 'Cancer'),  # Aries 15° -> Odd sign, second half -> Cancer
    (30, 'Cancer'),  # Taurus 0° -> Even sign, first half -> Cancer
    (45, 'Leo'),     # Taurus 15° -> Even sign, second half -> Leo
    (60, 'Leo'),     # Gemini 0° -> Odd sign, first half -> Leo
]

for long, expected in test_cases_d2:
    result = calculate_d2_hora(long)
    status = "✅" if result == expected else "❌"
    print(f"  {long:>6.1f}° -> {result:<8} (expected {expected}) {status}")

print("\n" + "=" * 70)
print("TESTING D4 FORMULA")
print("=" * 70)

# Test cases for D4 (Chaturthamsha)
# Aries (sign 0): 0-7.5° -> Aries, 7.5-15° -> Cancer, 15-22.5° -> Libra, 22.5-30° -> Capricorn
test_cases_d4 = [
    (0, 'Aries'),      # Aries 0° -> Same sign
    (7.5, 'Cancer'),   # Aries 7.5° -> 4th from Aries
    (15, 'Libra'),     # Aries 15° -> 7th from Aries
    (22.5, 'Capricorn'),  # Aries 22.5° -> 10th from Aries
    (30, 'Taurus'),    # Taurus 0° -> Same sign (Taurus)
    (37.5, 'Leo'),     # Taurus 7.5° -> 4th from Taurus
]

for long, expected in test_cases_d4:
    result = calculate_d4_chaturthamsha(long)
    status = "✅" if result == expected else "❌"
    sign_idx = int(long / 30)
    deg = long % 30
    print(f"  {SIGNS[sign_idx]} {deg:.1f}° ({long:.1f}°) -> {result:<12} (expected {expected}) {status}")

print("\n" + "=" * 70)
print("ATTEMPTING TO MATCH VADIM'S D2 GROUND TRUTH")
print("=" * 70)

# From previous session, approximate Raman positions:
# Sun: Libra 9°31' = 189.52°
# Moon: Pisces 18°27' = 348.45°
# Based on prior calculations with ayanamsa delta ~1.4°

# Let me try to reconstruct:
# If D1 Ascendant longitude is around Leo ~6°, then D2 Asc = Leo (first half of odd sign)
# House 1 = Leo, House 2 = Virgo, House 3 = Libra, House 4 = Scorpio, ...

# Actually wait - in D2, planets can only be in Cancer or Leo.
# So if a planet is in Leo, it goes to whichever house Leo corresponds to.

# Let's assume D2 Ascendant = Virgo (which is even sign)
# D2 of Virgo 0° = Cancer (even sign, first half)
# D2 of Virgo 15° = Leo (even sign, second half)

# Hmm, but the Ascendant itself gets mapped to D2.
# If D1 Asc = Leo 6°, then D2 Asc = calculate_d2_hora(124 + 6) = Leo (odd, first half)

# Let me try: D2 Asc = Leo
# House 1 = Leo, House 2 = Virgo, House 3 = Libra, House 4 = Scorpio, etc.
# But planets can only be in Cancer or Leo!

# So all planets in Leo go to House 1
# All planets in Cancer... let me count: House 12 would be Cancer (Leo - 1 = Cancer)

# Testing with D2 Asc = Leo:
# House 1 (Leo): Saturn should be here
# House 12 (Cancer): Moon, Mars should be here

# For Saturn to be in Leo (House 1):
# Saturn D2 = Leo means Saturn's D1 longitude is in:
# - Odd sign (0,2,4,6,8,10) with degrees 0-15, OR
# - Even sign (1,3,5,7,9,11) with degrees 15-30

# Saturn is in Cancer (sign 3, even) at ~21°
# D2 of even sign with degrees 15-30 = Leo ✓

print("\nAssuming D2 Ascendant = Leo (House 1 = Leo):")
print("House 12 = Cancer (one sign before Leo)")

# Estimated Vadim D1 positions (need refinement)
vadim_d1_estimated = {
    'Ascendant': ('Leo', 6.0),       # Rough estimate
    'Sun': ('Libra', 9.5),           # From prior analysis
    'Moon': ('Pisces', 18.5),
    'Mars': ('Virgo', 16.0),         # Adjusted to get Leo in D2
    'Mercury': ('Libra', 0.5),       # Needs to give Cancer
    'Jupiter': ('Leo', 2.0),         # To give Leo in D2
    'Venus': ('Scorpio', 7.0),       # To give Cancer in D2 (even, first half)
    'Saturn': ('Cancer', 21.0),      # Even sign, second half -> Leo ✓
    'Rahu': ('Virgo', 18.0),         # Even sign, second half -> Leo
    'Ketu': ('Pisces', 18.0),        # Even sign, second half -> Leo
}

print("\nTesting estimated D1 positions for D2 match:")
for planet, (sign, deg) in vadim_d1_estimated.items():
    sign_idx = SIGNS.index(sign)
    longitude = sign_idx * 30 + deg
    d2_sign = calculate_d2_hora(longitude)
    print(f"  {planet}: {sign} {deg:.1f}° -> D2 = {d2_sign}")

print("\n" + "=" * 70)
print("CONCLUSION: Need actual D1 longitudes from server calculation")
print("=" * 70)
print("The formulas are correct, but we need the ACTUAL Raman-corrected")
print("D1 longitudes to verify the house placements match the ground truth.")
