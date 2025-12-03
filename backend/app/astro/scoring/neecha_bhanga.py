"""
Neecha Bhanga Raja Yoga - Cancellation of Debilitation

When a planet is debilitated, certain conditions can cancel the debilitation
and even convert it to a Raja Yoga (royal combination).

12 Classical Rules for Neecha Bhanga:
1. Debilitated planet's dispositor is in kendra from Lagna or Moon
2. Debilitated planet's dispositor is exalted
3. Lord of debilitated planet's exaltation sign is in kendra from Lagna or Moon
4. Debilitated planet is aspected by its dispositor
5. Debilitated planet is conjunct its exaltation lord
6. Debilitated planet is in kendra from Lagna or Moon
7. Debilitated planet exchanges signs with another planet
8. Debilitated planet is in Navamsha of exaltation or own sign
9. Debilitated planet is aspected by the exaltation lord
10. Dispositor of debilitated planet is in its own or exaltation sign
11. Debilitated planet is retrograde
12. Debilitated planet is conjunct or aspected by benefics

Scoring:
- 0 rules: -3 points (pure debilitation penalty)
- 1 rule: 0 points (cancellation only)
- 2 rules: +2 points (mild boost)
- 3+ rules: +3 to +4 points (Neecha Bhanga Raja Yoga)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


# Debilitation and exaltation data
DEBILITATION_SIGNS = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries", "Rahu": "Scorpio", "Ketu": "Taurus"
}

EXALTATION_SIGNS = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio"
}

# Sign lords (dispositors)
SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

OWN_SIGNS = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"],
    "Rahu": ["Aquarius"],
    "Ketu": ["Scorpio"]
}

NATURAL_BENEFICS = ["Jupiter", "Venus", "Mercury", "Moon"]


def get_sign_number(sign: str) -> int:
    """Convert sign name to number (1-12)"""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    try:
        return signs.index(sign) + 1
    except ValueError:
        return 1


def get_sign_name(num: int) -> str:
    """Convert sign number (1-12) to name"""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return signs[(num - 1) % 12]


def is_kendra(from_house: int, to_house: int) -> bool:
    """Check if to_house is in kendra (1, 4, 7, 10) from from_house"""
    diff = ((to_house - from_house) % 12) + 1
    return diff in [1, 4, 7, 10]


@dataclass
class NeechaBhangaResult:
    """Result of Neecha Bhanga analysis for a planet"""
    planet: str
    debilitation_sign: str
    house: int
    rules_satisfied: List[str]
    count: int
    is_raja_yoga: bool
    score_modifier: float


class NeechaBhangaAnalyzer:
    """
    Analyzes debilitated planets for Neecha Bhanga (cancellation of debilitation)
    """

    def __init__(self, d1_data: Dict[str, Any], d9_data: Optional[Dict[str, Any]] = None):
        """
        Initialize analyzer with D1 and optionally D9 data

        Args:
            d1_data: D1 chart data with planets and ascendant
            d9_data: Optional D9 (Navamsha) data
        """
        self.d1 = d1_data
        self.d9 = d9_data
        self.planets = d1_data.get("planets", [])
        self.ascendant = d1_data.get("ascendant", {})
        self.asc_sign = self.ascendant.get("sign_name") or self.ascendant.get("sign", "Aries")
        self.asc_num = get_sign_number(self.asc_sign)

        # Build planet lookup dicts
        self._build_planet_maps()

    def _build_planet_maps(self):
        """Build lookup maps for planets"""
        self.planet_signs = {}
        self.planet_houses = {}
        self.planet_is_retrograde = {}

        for p in self.planets:
            name = p.get("name", "")
            sign = p.get("sign_name") or p.get("sign", "")

            # Calculate house
            house = p.get("house_occupied") or p.get("house")
            if not house and sign:
                sign_num = get_sign_number(sign)
                house = ((sign_num - self.asc_num) % 12) + 1

            self.planet_signs[name] = sign
            self.planet_houses[name] = house or 0
            self.planet_is_retrograde[name] = p.get("is_retrograde", False)

        # Find Moon's house for Moon-based kendra checks
        self.moon_house = self.planet_houses.get("Moon", 1)

    def find_debilitated_planets(self) -> List[str]:
        """Find all debilitated planets in the chart"""
        debilitated = []
        for planet, deb_sign in DEBILITATION_SIGNS.items():
            if self.planet_signs.get(planet) == deb_sign:
                debilitated.append(planet)
        return debilitated

    def analyze_planet(self, planet: str) -> Optional[NeechaBhangaResult]:
        """
        Analyze a debilitated planet for Neecha Bhanga

        Args:
            planet: Name of the debilitated planet

        Returns:
            NeechaBhangaResult with analysis, or None if planet is not debilitated
        """
        deb_sign = DEBILITATION_SIGNS.get(planet)
        if not deb_sign or self.planet_signs.get(planet) != deb_sign:
            return None

        house = self.planet_houses.get(planet, 0)
        rules_satisfied = []

        # Get key players
        dispositor = SIGN_LORDS.get(deb_sign)
        exaltation_sign = EXALTATION_SIGNS.get(planet)
        exaltation_lord = SIGN_LORDS.get(exaltation_sign) if exaltation_sign else None
        dispositor_house = self.planet_houses.get(dispositor, 0)
        exaltation_lord_house = self.planet_houses.get(exaltation_lord, 0)

        # Rule 1: Dispositor in kendra from Lagna or Moon
        if dispositor and dispositor_house > 0:
            if is_kendra(1, dispositor_house) or is_kendra(self.moon_house, dispositor_house):
                rules_satisfied.append(f"Rule 1: {dispositor} (dispositor) in kendra from Lagna/Moon")

        # Rule 2: Dispositor is exalted
        if dispositor:
            dispositor_sign = self.planet_signs.get(dispositor, "")
            if dispositor_sign == EXALTATION_SIGNS.get(dispositor):
                rules_satisfied.append(f"Rule 2: {dispositor} (dispositor) is exalted in {dispositor_sign}")

        # Rule 3: Exaltation lord in kendra from Lagna or Moon
        if exaltation_lord and exaltation_lord_house > 0:
            if is_kendra(1, exaltation_lord_house) or is_kendra(self.moon_house, exaltation_lord_house):
                rules_satisfied.append(f"Rule 3: {exaltation_lord} (exaltation lord) in kendra from Lagna/Moon")

        # Rule 4: Debilitated planet aspected by its dispositor
        if self._is_aspected_by(planet, dispositor):
            rules_satisfied.append(f"Rule 4: {planet} aspected by {dispositor} (dispositor)")

        # Rule 5: Debilitated planet conjunct exaltation lord
        if exaltation_lord and house == self.planet_houses.get(exaltation_lord, -1):
            rules_satisfied.append(f"Rule 5: {planet} conjunct {exaltation_lord} (exaltation lord)")

        # Rule 6: Debilitated planet in kendra from Lagna or Moon
        if is_kendra(1, house) or is_kendra(self.moon_house, house):
            rules_satisfied.append(f"Rule 6: {planet} in kendra (house {house}) from Lagna/Moon")

        # Rule 7: Debilitated planet exchanges signs (Parivartana)
        for other_planet, other_sign in self.planet_signs.items():
            if other_planet != planet:
                planet_in_other_sign = (deb_sign == SIGN_LORDS.get(other_sign))
                other_in_planet_sign = (other_sign == SIGN_LORDS.get(deb_sign))
                # Check if planet owns the sign where other planet sits, and vice versa
                other_lord = SIGN_LORDS.get(other_sign)
                if other_lord == planet and SIGN_LORDS.get(deb_sign) == other_planet:
                    rules_satisfied.append(f"Rule 7: {planet} exchanges signs with {other_planet}")
                    break

        # Rule 8: Debilitated planet in Navamsha of exaltation or own sign
        if self.d9:
            d9_planets = self.d9.get("planets", [])
            for p in d9_planets:
                if p.get("name") == planet:
                    d9_sign = p.get("sign_name") or p.get("sign", "")
                    if d9_sign == exaltation_sign:
                        rules_satisfied.append(f"Rule 8: {planet} in exaltation sign in D9 ({d9_sign})")
                    elif d9_sign in OWN_SIGNS.get(planet, []):
                        rules_satisfied.append(f"Rule 8: {planet} in own sign in D9 ({d9_sign})")
                    break

        # Rule 9: Debilitated planet aspected by exaltation lord
        if exaltation_lord and exaltation_lord != dispositor:  # Don't double count with Rule 4
            if self._is_aspected_by(planet, exaltation_lord):
                rules_satisfied.append(f"Rule 9: {planet} aspected by {exaltation_lord} (exaltation lord)")

        # Rule 10: Dispositor in own or exaltation sign
        if dispositor:
            dispositor_sign = self.planet_signs.get(dispositor, "")
            if dispositor_sign in OWN_SIGNS.get(dispositor, []):
                rules_satisfied.append(f"Rule 10: {dispositor} (dispositor) in own sign ({dispositor_sign})")
            elif dispositor_sign == EXALTATION_SIGNS.get(dispositor):
                # This overlaps with Rule 2 for exaltation, so only add if not already there
                if f"Rule 2:" not in str(rules_satisfied):
                    rules_satisfied.append(f"Rule 10: {dispositor} (dispositor) exalted in {dispositor_sign}")

        # Rule 11: Debilitated planet is retrograde
        if self.planet_is_retrograde.get(planet, False):
            rules_satisfied.append(f"Rule 11: {planet} is retrograde (increased strength)")

        # Rule 12: Debilitated planet conjunct or aspected by benefics
        benefic_support = []
        for benefic in NATURAL_BENEFICS:
            if benefic != planet:
                # Check conjunction
                if self.planet_houses.get(benefic, -1) == house:
                    benefic_support.append(f"{benefic} conjunct")
                # Check aspect
                elif self._is_aspected_by(planet, benefic):
                    benefic_support.append(f"{benefic} aspects")

        if benefic_support:
            rules_satisfied.append(f"Rule 12: {planet} supported by benefics: {', '.join(benefic_support)}")

        # Calculate score modifier
        count = len(rules_satisfied)
        is_raja_yoga = count >= 3

        if count == 0:
            score_modifier = -3.0  # Full debilitation penalty
        elif count == 1:
            score_modifier = 0.0   # Cancellation only
        elif count == 2:
            score_modifier = 2.0   # Mild boost
        else:
            score_modifier = 4.0 if count >= 4 else 3.0  # Raja Yoga!

        return NeechaBhangaResult(
            planet=planet,
            debilitation_sign=deb_sign,
            house=house,
            rules_satisfied=rules_satisfied,
            count=count,
            is_raja_yoga=is_raja_yoga,
            score_modifier=score_modifier
        )

    def _is_aspected_by(self, target_planet: str, aspecting_planet: str) -> bool:
        """
        Check if target planet is aspected by aspecting planet

        Uses standard Vedic aspect rules:
        - All planets aspect 7th house
        - Mars also aspects 4th and 8th
        - Jupiter also aspects 5th and 9th
        - Saturn also aspects 3rd and 10th
        """
        if not aspecting_planet or aspecting_planet == target_planet:
            return False

        target_house = self.planet_houses.get(target_planet, 0)
        aspect_house = self.planet_houses.get(aspecting_planet, 0)

        if target_house == 0 or aspect_house == 0:
            return False

        # Calculate house difference (from aspecting to target)
        diff = ((target_house - aspect_house) % 12)
        if diff == 0:
            diff = 12

        # All planets aspect 7th
        if diff == 7:
            return True

        # Special aspects
        if aspecting_planet == "Mars" and diff in [4, 8]:
            return True
        if aspecting_planet == "Jupiter" and diff in [5, 9]:
            return True
        if aspecting_planet == "Saturn" and diff in [3, 10]:
            return True
        if aspecting_planet in ["Rahu", "Ketu"] and diff in [5, 9]:
            return True

        return False

    def analyze_all(self) -> List[NeechaBhangaResult]:
        """Analyze all debilitated planets in the chart"""
        results = []
        for planet in self.find_debilitated_planets():
            result = self.analyze_planet(planet)
            if result:
                results.append(result)
        return results


def analyze_all_neecha_bhanga(d1_data: Dict[str, Any], d9_data: Optional[Dict[str, Any]] = None) -> List[NeechaBhangaResult]:
    """
    Convenience function to analyze all debilitated planets

    Args:
        d1_data: D1 chart data
        d9_data: Optional D9 chart data

    Returns:
        List of NeechaBhangaResult for each debilitated planet
    """
    analyzer = NeechaBhangaAnalyzer(d1_data, d9_data)
    return analyzer.analyze_all()


def get_house_neecha_bhanga_modifier(
    d1_data: Dict[str, Any],
    d9_data: Optional[Dict[str, Any]] = None
) -> Dict[int, float]:
    """
    Get score modifiers for each house based on Neecha Bhanga analysis

    This replaces the simple -3 debilitation penalty with the calculated
    Neecha Bhanga score modifier.

    Args:
        d1_data: D1 chart data
        d9_data: Optional D9 chart data

    Returns:
        Dict mapping house number to score modifier
    """
    results = analyze_all_neecha_bhanga(d1_data, d9_data)

    modifiers = {}
    for result in results:
        if result.house > 0:
            modifiers[result.house] = result.score_modifier

    return modifiers


def get_neecha_bhanga_details(
    d1_data: Dict[str, Any],
    d9_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get detailed Neecha Bhanga analysis for reporting

    Args:
        d1_data: D1 chart data
        d9_data: Optional D9 chart data

    Returns:
        Dict with detailed analysis including all rules satisfied
    """
    results = analyze_all_neecha_bhanga(d1_data, d9_data)

    details = {}
    for result in results:
        details[result.planet] = {
            "debilitation_sign": result.debilitation_sign,
            "house": result.house,
            "rules_satisfied": result.rules_satisfied,
            "rule_count": result.count,
            "is_raja_yoga": result.is_raja_yoga,
            "score_modifier": result.score_modifier,
            "interpretation": _get_interpretation(result)
        }

    return details


def _get_interpretation(result: NeechaBhangaResult) -> str:
    """Generate human-readable interpretation"""
    if result.count == 0:
        return f"{result.planet} is fully debilitated in {result.debilitation_sign} with no cancellation factors."
    elif result.count == 1:
        return f"{result.planet} debilitation in {result.debilitation_sign} is partially cancelled but not strengthened."
    elif result.count == 2:
        return f"{result.planet} has Neecha Bhanga (cancellation) with mild positive effects."
    elif result.is_raja_yoga:
        return f"{result.planet} has Neecha Bhanga Raja Yoga! Debilitation becomes a powerful blessing with {result.count} supporting factors."
    else:
        return f"{result.planet} has strong Neecha Bhanga with {result.count} supporting factors."
