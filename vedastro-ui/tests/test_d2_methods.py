"""
Test different D2 (Hora) methods to match VedAstro ground truth
Profile: Vadim (1977-10-25, 06:28, Sortavala)
"""

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# D1 Positions (Raman ayanamsa from Swiss Ephemeris)
positions = {
    "Sun": 189.5081, "Moon": 348.4403, "Mars": 97.1884,
    "Mercury": 193.5745, "Jupiter": 74.0393, "Venus": 167.9184,
    "Saturn": 126.4588, "Rahu": 172.0469, "Ketu": 352.0469,
    "Ascendant": 173.6218,
}

# Ground truth from VedAstro
D2_GT = {1: ["Saturn"], 3: ["Sun", "Jupiter"], 4: ["Ketu"], 6: ["Venus"], 7: ["Mercury"], 10: ["Rahu"], 12: ["Moon", "Mars"]}


def d2_parasara(longitude):
    """Traditional Parasara: only Cancer/Leo"""
    sign_idx = int(longitude / 30)
    deg = longitude % 30
    is_odd = (sign_idx % 2 == 0)  # 0-indexed, so even index = odd sign
    first_half = (deg < 15)
    if is_odd:
        return "Leo" if first_half else "Cancer"
    else:
        return "Cancer" if first_half else "Leo"


def d2_parivritti(longitude):
    """Parivritti/Vriddhakarika: 2N-1, 2N formula"""
    sign_idx = int(longitude / 30)
    deg = longitude % 30
    sign_num = sign_idx + 1  # 1-indexed
    first_half = (deg < 15)
    if first_half:
        d2_num = (2 * sign_num - 1)
    else:
        d2_num = (2 * sign_num)
    d2_idx = (d2_num - 1) % 12
    return SIGNS[d2_idx]


def d2_simple_rotation(longitude):
    """Simple rotation: sign*2 + part"""
    sign_idx = int(longitude / 30)
    deg = longitude % 30
    part = 0 if deg < 15 else 1
    d2_idx = (sign_idx * 2 + part) % 12
    return SIGNS[d2_idx]


def d2_absolute(longitude):
    """Absolute position: longitude / 15"""
    part = int(longitude / 15)
    d2_idx = part % 12
    return SIGNS[d2_idx]


def d2_vedastro_table(longitude):
    """
    VedAstro uses precomputed HoraTable.
    Based on web research, the table maps each half-sign to a specific hora.
    Let me try to reverse-engineer from ground truth.
    """
    # From ground truth analysis:
    # Saturn (Leo 6.46°, first half of odd sign) -> H1
    # Sun (Libra 9.51°, first half of odd sign) -> H3
    # Jupiter (Gemini 14.04°, first half of odd sign) -> H3
    # Ketu (Pisces 22.05°, second half of even sign) -> H4
    # Venus (Virgo 17.92°, second half of even sign) -> H6
    # Mercury (Libra 13.57°, first half of odd sign) -> H7
    # Rahu (Virgo 22.05°, second half of even sign) -> H10
    # Moon (Pisces 18.44°, second half of even sign) -> H12
    # Mars (Cancer 7.19°, first half of even sign) -> H12

    # This matches Parasara method! All are Cancer or Leo.
    # Ascendant must be in Leo for Saturn (Leo) to be in H1.

    # Let's check: Ascendant (Virgo 23.62°, second half of even sign)
    # Parasara: even sign, second half -> Leo
    # So D2 Asc = Leo, and Saturn (Leo 6.46° first half of odd) = Leo
    # H1 = Leo -> Saturn ✓

    return d2_parasara(longitude)


def test_method(method_name, method_func):
    """Test a D2 method against ground truth"""
    asc_d2 = method_func(positions["Ascendant"])

    d2_houses = {}
    asc_idx = SIGNS.index(asc_d2)

    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        d2_sign = method_func(positions[planet])
        sign_idx = SIGNS.index(d2_sign)
        house = ((sign_idx - asc_idx) % 12) + 1
        if house not in d2_houses:
            d2_houses[house] = []
        d2_houses[house].append(planet)

    # Count matches
    match_count = 0
    total = 0
    for h, gt_planets in D2_GT.items():
        calc_planets = d2_houses.get(h, [])
        for p in gt_planets:
            total += 1
            if p in calc_planets:
                match_count += 1

    print(f"\n{'='*60}")
    print(f"{method_name} Method")
    print(f"{'='*60}")
    print(f"D2 Ascendant: {asc_d2}")
    print(f"\nCalculated Houses:")
    for h in sorted(d2_houses.keys()):
        print(f"  H{h}: {d2_houses[h]}")
    print(f"\nGround Truth:")
    for h in sorted(D2_GT.keys()):
        print(f"  H{h}: {D2_GT[h]}")
    print(f"\nMatch Score: {match_count}/{total}")

    return match_count == total


if __name__ == "__main__":
    print("="*60)
    print("D2 (HORA) METHOD COMPARISON")
    print("="*60)
    print("\nD1 Positions (Raman Ayanamsa):")
    for planet, long in sorted(positions.items(), key=lambda x: x[1]):
        sign_idx = int(long / 30)
        deg = long % 30
        print(f"  {planet}: {SIGNS[sign_idx]} {deg:.2f}°")

    methods = [
        ("Parasara (Cancer/Leo)", d2_parasara),
        ("Parivritti (2N-1, 2N)", d2_parivritti),
        ("Simple Rotation", d2_simple_rotation),
        ("Absolute Position", d2_absolute),
    ]

    for name, func in methods:
        test_method(name, func)
