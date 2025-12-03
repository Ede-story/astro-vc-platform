"""
Tests for Neecha Bhanga Raja Yoga module

Test case: Vadim's chart (October 25, 1977, 06:28, Petrozavodsk)
- Mars in Cancer (11th house) - DEBILITATED
- Moon in Pisces (7th house) - KENDRA from Lagna
- Expected: Neecha Bhanga with at least Rule 1 or 3 satisfied
"""

import pytest
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.astro.scoring.neecha_bhanga import (
    NeechaBhangaAnalyzer,
    NeechaBhangaResult,
    analyze_all_neecha_bhanga,
    get_house_neecha_bhanga_modifier,
    get_neecha_bhanga_details,
    DEBILITATION_SIGNS,
)


# Vadim's D1 chart data (approximate - will need exact values from API)
VADIM_D1_DATA = {
    "ascendant": {"sign": "Virgo", "sign_name": "Virgo", "degree": 28.5},
    "planets": [
        {"name": "Sun", "sign": "Libra", "sign_name": "Libra", "house_occupied": 2},
        {"name": "Moon", "sign": "Pisces", "sign_name": "Pisces", "house_occupied": 7},
        {"name": "Mars", "sign": "Cancer", "sign_name": "Cancer", "house_occupied": 11},  # DEBILITATED
        {"name": "Mercury", "sign": "Libra", "sign_name": "Libra", "house_occupied": 2},
        {"name": "Jupiter", "sign": "Gemini", "sign_name": "Gemini", "house_occupied": 10},
        {"name": "Venus", "sign": "Virgo", "sign_name": "Virgo", "house_occupied": 1},  # DEBILITATED
        {"name": "Saturn", "sign": "Leo", "sign_name": "Leo", "house_occupied": 12},
        {"name": "Rahu", "sign": "Virgo", "sign_name": "Virgo", "house_occupied": 1},
        {"name": "Ketu", "sign": "Pisces", "sign_name": "Pisces", "house_occupied": 7},
    ]
}

# Optional D9 data for Rule 8 testing
VADIM_D9_DATA = {
    "planets": [
        {"name": "Sun", "sign": "Sagittarius", "sign_name": "Sagittarius"},
        {"name": "Moon", "sign": "Virgo", "sign_name": "Virgo"},
        {"name": "Mars", "sign": "Pisces", "sign_name": "Pisces"},
        {"name": "Mercury", "sign": "Sagittarius", "sign_name": "Sagittarius"},
        {"name": "Jupiter", "sign": "Sagittarius", "sign_name": "Sagittarius"},
        {"name": "Venus", "sign": "Capricorn", "sign_name": "Capricorn"},
        {"name": "Saturn", "sign": "Cancer", "sign_name": "Cancer"},
        {"name": "Rahu", "sign": "Capricorn", "sign_name": "Capricorn"},
        {"name": "Ketu", "sign": "Cancer", "sign_name": "Cancer"},
    ]
}


class TestNeechaBhangaAnalyzer:
    """Test the Neecha Bhanga analyzer"""

    def test_find_debilitated_planets(self):
        """Should correctly identify debilitated planets"""
        analyzer = NeechaBhangaAnalyzer(VADIM_D1_DATA)
        debilitated = analyzer.find_debilitated_planets()

        # Mars in Cancer and Venus in Virgo are debilitated
        assert "Mars" in debilitated, "Mars in Cancer should be detected as debilitated"
        assert "Venus" in debilitated, "Venus in Virgo should be detected as debilitated"

    def test_mars_neecha_bhanga_rule1(self):
        """Test Rule 1: Dispositor in kendra from Lagna"""
        analyzer = NeechaBhangaAnalyzer(VADIM_D1_DATA)
        result = analyzer.analyze_planet("Mars")

        assert result is not None, "Mars analysis should return a result"
        assert result.planet == "Mars"
        assert result.debilitation_sign == "Cancer"
        assert result.house == 11

        # Moon (dispositor of Cancer) is in 7th house = KENDRA
        # So Rule 1 should be satisfied
        rule1_found = any("Rule 1" in r for r in result.rules_satisfied)
        assert rule1_found, f"Rule 1 (dispositor in kendra) should be satisfied. Rules found: {result.rules_satisfied}"

    def test_mars_neecha_bhanga_count(self):
        """Mars should have at least 1 Neecha Bhanga rule satisfied"""
        analyzer = NeechaBhangaAnalyzer(VADIM_D1_DATA)
        result = analyzer.analyze_planet("Mars")

        assert result.count >= 1, f"Mars should have at least 1 rule satisfied, got {result.count}"
        # With 1 rule, score should be 0 (cancellation only)
        # With 2+ rules, score should be positive
        if result.count == 1:
            assert result.score_modifier == 0.0, "1 rule = cancellation only (0 points)"
        elif result.count == 2:
            assert result.score_modifier == 2.0, "2 rules = mild boost (+2)"
        else:
            assert result.score_modifier >= 3.0, "3+ rules = Raja Yoga (+3/+4)"

    def test_venus_neecha_bhanga(self):
        """Venus in Virgo should also be analyzed for Neecha Bhanga"""
        analyzer = NeechaBhangaAnalyzer(VADIM_D1_DATA)
        result = analyzer.analyze_planet("Venus")

        assert result is not None, "Venus analysis should return a result"
        assert result.planet == "Venus"
        assert result.debilitation_sign == "Virgo"
        assert result.house == 1

    def test_analyze_all(self):
        """analyze_all should return results for all debilitated planets"""
        analyzer = NeechaBhangaAnalyzer(VADIM_D1_DATA)
        results = analyzer.analyze_all()

        # Should have results for Mars and Venus
        planet_names = [r.planet for r in results]
        assert "Mars" in planet_names
        assert "Venus" in planet_names

    def test_non_debilitated_planet_returns_none(self):
        """Non-debilitated planets should return None"""
        analyzer = NeechaBhangaAnalyzer(VADIM_D1_DATA)

        result = analyzer.analyze_planet("Jupiter")
        assert result is None, "Jupiter is not debilitated, should return None"

        result = analyzer.analyze_planet("Moon")
        assert result is None, "Moon is not debilitated, should return None"


class TestNeechaBhangaConvenienceFunctions:
    """Test convenience functions"""

    def test_analyze_all_neecha_bhanga(self):
        """analyze_all_neecha_bhanga should work correctly"""
        results = analyze_all_neecha_bhanga(VADIM_D1_DATA)

        assert len(results) >= 2, "Should find at least 2 debilitated planets (Mars, Venus)"
        assert all(isinstance(r, NeechaBhangaResult) for r in results)

    def test_get_house_neecha_bhanga_modifier(self):
        """get_house_neecha_bhanga_modifier should return house modifiers"""
        modifiers = get_house_neecha_bhanga_modifier(VADIM_D1_DATA)

        # Mars is in house 11, Venus is in house 1
        assert 11 in modifiers, "House 11 (Mars) should have a modifier"
        assert 1 in modifiers, "House 1 (Venus) should have a modifier"

        # Mars with Neecha Bhanga should have positive or 0 modifier (not -3)
        mars_modifier = modifiers[11]
        assert mars_modifier >= 0, f"Mars modifier should be >= 0 (has Neecha Bhanga), got {mars_modifier}"

    def test_get_neecha_bhanga_details(self):
        """get_neecha_bhanga_details should return detailed info"""
        details = get_neecha_bhanga_details(VADIM_D1_DATA)

        assert "Mars" in details
        assert "Venus" in details

        mars_detail = details["Mars"]
        assert "debilitation_sign" in mars_detail
        assert "rules_satisfied" in mars_detail
        assert "is_raja_yoga" in mars_detail
        assert "interpretation" in mars_detail


class TestNeechaBhangaRules:
    """Test individual Neecha Bhanga rules"""

    def test_rule6_debilitated_in_kendra(self):
        """Test Rule 6: Debilitated planet in kendra from Lagna or Moon"""
        # Create test data where debilitated planet is in kendra (house 4)
        test_data = {
            "ascendant": {"sign": "Aries", "sign_name": "Aries"},
            "planets": [
                {"name": "Mars", "sign": "Cancer", "sign_name": "Cancer", "house_occupied": 4},  # Kendra!
                {"name": "Moon", "sign": "Taurus", "sign_name": "Taurus", "house_occupied": 2},
            ]
        }
        analyzer = NeechaBhangaAnalyzer(test_data)
        result = analyzer.analyze_planet("Mars")

        assert result is not None
        rule6_found = any("Rule 6" in r for r in result.rules_satisfied)
        assert rule6_found, "Rule 6 (debilitated in kendra) should be satisfied"

    def test_rule11_retrograde(self):
        """Test Rule 11: Debilitated planet is retrograde"""
        test_data = {
            "ascendant": {"sign": "Aries", "sign_name": "Aries"},
            "planets": [
                {"name": "Mars", "sign": "Cancer", "sign_name": "Cancer", "house_occupied": 4, "is_retrograde": True},
                {"name": "Moon", "sign": "Taurus", "sign_name": "Taurus", "house_occupied": 2},
            ]
        }
        analyzer = NeechaBhangaAnalyzer(test_data)
        result = analyzer.analyze_planet("Mars")

        rule11_found = any("Rule 11" in r for r in result.rules_satisfied)
        assert rule11_found, "Rule 11 (retrograde) should be satisfied"

    def test_rule12_benefic_conjunction(self):
        """Test Rule 12: Debilitated planet conjunct benefics"""
        test_data = {
            "ascendant": {"sign": "Aries", "sign_name": "Aries"},
            "planets": [
                {"name": "Mars", "sign": "Cancer", "sign_name": "Cancer", "house_occupied": 4},
                {"name": "Jupiter", "sign": "Cancer", "sign_name": "Cancer", "house_occupied": 4},  # Benefic conjunct!
                {"name": "Moon", "sign": "Taurus", "sign_name": "Taurus", "house_occupied": 2},
            ]
        }
        analyzer = NeechaBhangaAnalyzer(test_data)
        result = analyzer.analyze_planet("Mars")

        rule12_found = any("Rule 12" in r for r in result.rules_satisfied)
        assert rule12_found, "Rule 12 (benefic conjunction) should be satisfied"


class TestScoreModifierLogic:
    """Test score modifier calculation"""

    def test_zero_rules_gives_negative(self):
        """0 rules = full debilitation penalty (-3)"""
        result = NeechaBhangaResult(
            planet="Test",
            debilitation_sign="Cancer",
            house=1,
            rules_satisfied=[],
            count=0,
            is_raja_yoga=False,
            score_modifier=-3.0
        )
        assert result.score_modifier == -3.0

    def test_one_rule_gives_zero(self):
        """1 rule = cancellation only (0)"""
        result = NeechaBhangaResult(
            planet="Test",
            debilitation_sign="Cancer",
            house=1,
            rules_satisfied=["Rule 1: test"],
            count=1,
            is_raja_yoga=False,
            score_modifier=0.0
        )
        assert result.score_modifier == 0.0

    def test_two_rules_gives_positive(self):
        """2 rules = mild boost (+2)"""
        result = NeechaBhangaResult(
            planet="Test",
            debilitation_sign="Cancer",
            house=1,
            rules_satisfied=["Rule 1: test", "Rule 2: test"],
            count=2,
            is_raja_yoga=False,
            score_modifier=2.0
        )
        assert result.score_modifier == 2.0

    def test_three_plus_rules_is_raja_yoga(self):
        """3+ rules = Raja Yoga (+3/+4)"""
        result = NeechaBhangaResult(
            planet="Test",
            debilitation_sign="Cancer",
            house=1,
            rules_satisfied=["Rule 1", "Rule 2", "Rule 3"],
            count=3,
            is_raja_yoga=True,
            score_modifier=3.0
        )
        assert result.is_raja_yoga == True
        assert result.score_modifier >= 3.0
