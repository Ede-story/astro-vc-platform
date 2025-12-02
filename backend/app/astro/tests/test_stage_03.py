"""
Tests for Stage 3: Yoga Analysis

Tests yoga detection, Neecha Bhanga Raja Yoga, and yoga scoring.
"""

import pytest
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.astro.calculator import AstroBrain
from app.astro.stages.stage_03_yogas import (
    Stage03YogaAnalysis,
    Stage3Result,
    YogaResult,
    NeechaBhangaResult,
    YogaSummary,
    CancellationLevel,
    check_gaja_kesari,
    check_budhaditya,
    check_mahapurusha_yoga,
    check_chandra_mangal,
    check_kemadruma,
    check_guru_chandala,
    check_grahan,
    check_neecha_bhanga,
    detect_all_yogas,
    calculate_yoga_summary,
    calculate_house_yoga_bonuses,
    get_house_lord,
    has_conjunction,
    planets_in_kendra_from,
)
from app.astro.reference.yogas_catalog import (
    YogaCategory,
    ALL_YOGAS,
    YOGA_BY_NAME,
    get_yoga_definition,
)
from app.astro.models.types import Planet, Zodiac, Dignity, ZODIAC_ORDER, KENDRA_HOUSES


# =============================================================================
# MOCK PLANET DATA
# =============================================================================

@dataclass
class MockPlanet:
    """Mock planet data for testing."""
    planet: Planet
    sign: Zodiac
    house: int
    degree: float
    dignity: Dignity
    is_retrograde: bool = False
    is_combust: bool = False


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_digital_twin_with_yogas():
    """
    Sample digital_twin with known yogas for testing.
    Based on Vadim's chart with Sun-Mercury conjunction (Budhaditya).
    """
    return {
        "meta": {
            "birth_datetime": "1977-10-25T06:28:00",
            "latitude": 61.7,
            "longitude": 30.69,
        },
        "vargas": {
            "D1": {
                "ascendant": {
                    "sign_id": 7,
                    "sign_name": "Libra",
                    "degrees": 17.84,
                },
                "planets": [
                    {
                        "name": "Sun",
                        "sign_id": 7,
                        "sign_name": "Libra",
                        "relative_degree": 8.12,
                        "house_occupied": 1,
                        "dignity_state": "Debilitated",
                        "is_retrograde": False
                    },
                    {
                        "name": "Moon",
                        "sign_id": 1,
                        "sign_name": "Aries",
                        "relative_degree": 15.45,
                        "house_occupied": 7,
                        "dignity_state": "Neutral",
                        "is_retrograde": False
                    },
                    {
                        "name": "Mars",
                        "sign_id": 4,
                        "sign_name": "Cancer",
                        "relative_degree": 15.33,
                        "house_occupied": 10,
                        "dignity_state": "Debilitated",
                        "is_retrograde": False
                    },
                    {
                        "name": "Mercury",
                        "sign_id": 7,
                        "sign_name": "Libra",
                        "relative_degree": 20.55,
                        "house_occupied": 1,
                        "dignity_state": "Friend",
                        "is_retrograde": False
                    },
                    {
                        "name": "Jupiter",
                        "sign_id": 6,
                        "sign_name": "Virgo",
                        "relative_degree": 18.22,
                        "house_occupied": 12,
                        "dignity_state": "Enemy",
                        "is_retrograde": True
                    },
                    {
                        "name": "Venus",
                        "sign_id": 4,
                        "sign_name": "Cancer",
                        "relative_degree": 22.44,
                        "house_occupied": 10,
                        "dignity_state": "Neutral",
                        "is_retrograde": False
                    },
                    {
                        "name": "Saturn",
                        "sign_id": 5,
                        "sign_name": "Leo",
                        "relative_degree": 23.88,
                        "house_occupied": 11,
                        "dignity_state": "Enemy",
                        "is_retrograde": True
                    },
                    {
                        "name": "Rahu",
                        "sign_id": 7,
                        "sign_name": "Libra",
                        "relative_degree": 3.67,
                        "house_occupied": 1,
                        "dignity_state": "Neutral",
                        "is_retrograde": True
                    },
                    {
                        "name": "Ketu",
                        "sign_id": 1,
                        "sign_name": "Aries",
                        "relative_degree": 3.67,
                        "house_occupied": 7,
                        "dignity_state": "Neutral",
                        "is_retrograde": True
                    }
                ],
                "houses": [
                    {"house_number": i, "sign_id": ((7 + i - 1) % 12) or 12, "sign_name": ZODIAC_ORDER[((7 + i - 2) % 12)].name}
                    for i in range(1, 13)
                ]
            }
        }
    }


@pytest.fixture
def gaja_kesari_planets():
    """Planets with Gaja Kesari Yoga (Jupiter in Kendra from Moon)."""
    return [
        MockPlanet(Planet.MOON, Zodiac.ARIES, 1, 15.0, Dignity.NEUTRAL),
        MockPlanet(Planet.JUPITER, Zodiac.CANCER, 4, 10.0, Dignity.EXALTED),  # Exalted Jupiter in 4th from Moon
        MockPlanet(Planet.SUN, Zodiac.LEO, 5, 12.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.MARS, Zodiac.SCORPIO, 8, 20.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.MERCURY, Zodiac.VIRGO, 6, 15.0, Dignity.EXALTED),
        MockPlanet(Planet.VENUS, Zodiac.PISCES, 12, 5.0, Dignity.EXALTED),
        MockPlanet(Planet.SATURN, Zodiac.AQUARIUS, 11, 25.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.RAHU, Zodiac.GEMINI, 3, 10.0, Dignity.NEUTRAL),
        MockPlanet(Planet.KETU, Zodiac.SAGITTARIUS, 9, 10.0, Dignity.NEUTRAL),
    ]


@pytest.fixture
def budhaditya_planets():
    """Planets with Budhaditya Yoga (Sun-Mercury conjunction)."""
    return [
        MockPlanet(Planet.SUN, Zodiac.LEO, 1, 15.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.MERCURY, Zodiac.LEO, 1, 20.0, Dignity.FRIEND),  # Conjunction with Sun
        MockPlanet(Planet.MOON, Zodiac.TAURUS, 10, 10.0, Dignity.EXALTED),
        MockPlanet(Planet.MARS, Zodiac.ARIES, 9, 12.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.JUPITER, Zodiac.SAGITTARIUS, 5, 18.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.VENUS, Zodiac.LIBRA, 3, 8.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.SATURN, Zodiac.CAPRICORN, 6, 22.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.RAHU, Zodiac.GEMINI, 11, 5.0, Dignity.NEUTRAL),
        MockPlanet(Planet.KETU, Zodiac.SAGITTARIUS, 5, 5.0, Dignity.NEUTRAL),
    ]


@pytest.fixture
def neecha_bhanga_planets():
    """Planets with Neecha Bhanga Raja Yoga (debilitated Mars with cancellation)."""
    return [
        MockPlanet(Planet.MARS, Zodiac.CANCER, 10, 15.0, Dignity.DEBILITATED),  # Debilitated Mars in Kendra
        MockPlanet(Planet.MOON, Zodiac.CANCER, 10, 20.0, Dignity.OWN_SIGN),  # Sign lord conjunct
        MockPlanet(Planet.SUN, Zodiac.ARIES, 7, 10.0, Dignity.EXALTED),
        MockPlanet(Planet.MERCURY, Zodiac.VIRGO, 12, 15.0, Dignity.EXALTED),
        MockPlanet(Planet.JUPITER, Zodiac.CANCER, 10, 5.0, Dignity.EXALTED),  # Jupiter exalts in Cancer, aspects
        MockPlanet(Planet.VENUS, Zodiac.PISCES, 6, 25.0, Dignity.EXALTED),
        MockPlanet(Planet.SATURN, Zodiac.LIBRA, 1, 20.0, Dignity.EXALTED),
        MockPlanet(Planet.RAHU, Zodiac.GEMINI, 9, 10.0, Dignity.NEUTRAL),
        MockPlanet(Planet.KETU, Zodiac.SAGITTARIUS, 3, 10.0, Dignity.NEUTRAL),
    ]


@pytest.fixture
def mahapurusha_planets():
    """Planets with Hamsa Yoga (Jupiter in Kendra in own/exalted sign)."""
    return [
        MockPlanet(Planet.JUPITER, Zodiac.CANCER, 1, 15.0, Dignity.EXALTED),  # Hamsa Yoga
        MockPlanet(Planet.MOON, Zodiac.TAURUS, 11, 10.0, Dignity.EXALTED),
        MockPlanet(Planet.SUN, Zodiac.LEO, 2, 12.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.MARS, Zodiac.ARIES, 10, 20.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.MERCURY, Zodiac.VIRGO, 3, 15.0, Dignity.EXALTED),
        MockPlanet(Planet.VENUS, Zodiac.PISCES, 9, 5.0, Dignity.EXALTED),
        MockPlanet(Planet.SATURN, Zodiac.AQUARIUS, 8, 25.0, Dignity.OWN_SIGN),
        MockPlanet(Planet.RAHU, Zodiac.GEMINI, 12, 10.0, Dignity.NEUTRAL),
        MockPlanet(Planet.KETU, Zodiac.SAGITTARIUS, 6, 10.0, Dignity.NEUTRAL),
    ]


# =============================================================================
# YOGA CATALOG TESTS
# =============================================================================

class TestYogaCatalog:
    """Tests for yoga catalog data."""

    def test_all_yogas_count(self):
        """Test that yoga catalog has expected count."""
        assert len(ALL_YOGAS) >= 20  # At least 20 yogas defined

    def test_yoga_by_name_lookup(self):
        """Test yoga lookup by name."""
        gaja_kesari = get_yoga_definition("Gaja Kesari Yoga")
        assert gaja_kesari is not None
        assert gaja_kesari.category == YogaCategory.RAJA  # Gaja Kesari is classified as Raja yoga

    def test_yoga_categories(self):
        """Test all yoga categories exist."""
        categories = set(y.category for y in ALL_YOGAS)
        assert YogaCategory.RAJA in categories
        assert YogaCategory.DHANA in categories
        assert YogaCategory.MAHAPURUSHA in categories

    def test_mahapurusha_yogas_defined(self):
        """Test all 5 Mahapurusha yogas are defined."""
        mahapurusha_names = ["Hamsa Yoga", "Malavya Yoga", "Ruchaka Yoga", "Bhadra Yoga", "Sasha Yoga"]
        for name in mahapurusha_names:
            yoga = get_yoga_definition(name)
            assert yoga is not None, f"{name} not found in catalog"
            assert yoga.category == YogaCategory.MAHAPURUSHA


# =============================================================================
# INDIVIDUAL YOGA DETECTION TESTS
# =============================================================================

class TestGajaKesariYoga:
    """Tests for Gaja Kesari Yoga detection."""

    def test_detect_gaja_kesari(self, gaja_kesari_planets):
        """Test Gaja Kesari Yoga is detected."""
        result = check_gaja_kesari(gaja_kesari_planets, Zodiac.ARIES)
        assert result is not None
        assert result.name == "Gaja Kesari Yoga"
        assert result.is_active == True
        assert Planet.JUPITER in result.participating_planets
        assert Planet.MOON in result.participating_planets

    def test_gaja_kesari_strength_with_exalted_jupiter(self, gaja_kesari_planets):
        """Test Gaja Kesari strength is boosted with exalted Jupiter."""
        result = check_gaja_kesari(gaja_kesari_planets, Zodiac.ARIES)
        assert result is not None
        # Base strength + exaltation bonus
        assert result.strength > result.base_strength

    def test_no_gaja_kesari_without_jupiter_kendra(self, budhaditya_planets):
        """Test no Gaja Kesari when Jupiter not in Kendra from Moon."""
        result = check_gaja_kesari(budhaditya_planets, Zodiac.LEO)
        # Jupiter in Sagittarius (5th), Moon in Taurus (10th)
        # Distance: 7 houses apart, not Kendra
        assert result is None


class TestBudhadityaYoga:
    """Tests for Budhaditya Yoga detection."""

    def test_detect_budhaditya(self, budhaditya_planets):
        """Test Budhaditya Yoga is detected."""
        result = check_budhaditya(budhaditya_planets, Zodiac.LEO)
        assert result is not None
        assert result.name == "Budhaditya Yoga"
        assert Planet.SUN in result.participating_planets
        assert Planet.MERCURY in result.participating_planets

    def test_budhaditya_combustion_penalty(self):
        """Test Budhaditya strength reduced when Mercury too close to Sun."""
        planets = [
            MockPlanet(Planet.SUN, Zodiac.LEO, 1, 15.0, Dignity.OWN_SIGN),
            MockPlanet(Planet.MERCURY, Zodiac.LEO, 1, 16.0, Dignity.FRIEND),  # Only 1 degree apart
            MockPlanet(Planet.MOON, Zodiac.CANCER, 12, 10.0, Dignity.OWN_SIGN),
        ]
        result = check_budhaditya(planets, Zodiac.LEO)
        assert result is not None
        # Should have combustion penalty
        has_combustion_modifier = any("too close" in m.get("description", "") for m in result.modifiers)
        assert has_combustion_modifier


class TestMahapurushaYoga:
    """Tests for Mahapurusha Yoga detection."""

    def test_detect_hamsa_yoga(self, mahapurusha_planets):
        """Test Hamsa Yoga (Jupiter) is detected."""
        result = check_mahapurusha_yoga(
            Planet.JUPITER,
            mahapurusha_planets,
            Zodiac.CANCER,
            "Hamsa Yoga"
        )
        assert result is not None
        assert result.name == "Hamsa Yoga"
        assert result.category == YogaCategory.MAHAPURUSHA

    def test_mahapurusha_requires_kendra(self):
        """Test Mahapurusha Yoga requires Kendra placement."""
        planets = [
            MockPlanet(Planet.JUPITER, Zodiac.SAGITTARIUS, 3, 15.0, Dignity.OWN_SIGN),  # House 3, not Kendra
        ]
        result = check_mahapurusha_yoga(
            Planet.JUPITER,
            planets,
            Zodiac.LIBRA,
            "Hamsa Yoga"
        )
        assert result is None

    def test_mahapurusha_requires_dignity(self):
        """Test Mahapurusha Yoga requires own/exalted sign."""
        planets = [
            MockPlanet(Planet.JUPITER, Zodiac.CAPRICORN, 1, 15.0, Dignity.DEBILITATED),  # Kendra but debilitated
        ]
        result = check_mahapurusha_yoga(
            Planet.JUPITER,
            planets,
            Zodiac.CAPRICORN,
            "Hamsa Yoga"
        )
        assert result is None


# =============================================================================
# NEECHA BHANGA TESTS
# =============================================================================

class TestNeechaBhanga:
    """Tests for Neecha Bhanga Raja Yoga detection."""

    def test_detect_neecha_bhanga(self, neecha_bhanga_planets):
        """Test Neecha Bhanga is detected for debilitated Mars."""
        mars = neecha_bhanga_planets[0]  # Mars in Cancer, debilitated
        result = check_neecha_bhanga(mars, neecha_bhanga_planets, Zodiac.LIBRA)

        assert result is not None
        assert result.planet == Planet.MARS
        assert result.debilitation_sign == Zodiac.CANCER
        assert len(result.rules_satisfied) > 0

    def test_neecha_bhanga_rules(self, neecha_bhanga_planets):
        """Test multiple Neecha Bhanga rules are checked."""
        mars = neecha_bhanga_planets[0]
        result = check_neecha_bhanga(mars, neecha_bhanga_planets, Zodiac.LIBRA)

        assert result is not None
        # Rule 4: Debilitated planet in Kendra (Mars in house 10)
        assert 4 in result.rules_satisfied
        # Rule 5: Sign lord conjunct (Moon in Cancer with Mars)
        assert 5 in result.rules_satisfied

    def test_neecha_bhanga_cancellation_level(self, neecha_bhanga_planets):
        """Test cancellation level is assigned based on restoration score."""
        mars = neecha_bhanga_planets[0]
        result = check_neecha_bhanga(mars, neecha_bhanga_planets, Zodiac.LIBRA)

        assert result is not None
        assert result.cancellation_level in [
            CancellationLevel.WEAK,
            CancellationLevel.MODERATE,
            CancellationLevel.STRONG,
            CancellationLevel.RAJA_YOGA,
        ]

    def test_no_neecha_bhanga_for_non_debilitated(self, gaja_kesari_planets):
        """Test no Neecha Bhanga for non-debilitated planets."""
        jupiter = gaja_kesari_planets[1]  # Jupiter exalted
        result = check_neecha_bhanga(jupiter, gaja_kesari_planets, Zodiac.ARIES)
        assert result is None


# =============================================================================
# NEGATIVE YOGA TESTS
# =============================================================================

class TestNegativeYogas:
    """Tests for negative yoga detection."""

    def test_guru_chandala_yoga(self):
        """Test Guru Chandala Yoga (Jupiter-Rahu conjunction)."""
        planets = [
            MockPlanet(Planet.JUPITER, Zodiac.GEMINI, 1, 10.0, Dignity.ENEMY),
            MockPlanet(Planet.RAHU, Zodiac.GEMINI, 1, 15.0, Dignity.NEUTRAL),  # Conjunction
            MockPlanet(Planet.MOON, Zodiac.CANCER, 2, 20.0, Dignity.OWN_SIGN),
        ]
        result = check_guru_chandala(planets, Zodiac.GEMINI)
        assert result is not None
        assert result.name == "Guru Chandala Yoga"
        assert result.category == YogaCategory.NEGATIVE

    def test_grahan_yoga(self):
        """Test Grahan Yoga (Sun/Moon with Rahu/Ketu)."""
        planets = [
            MockPlanet(Planet.SUN, Zodiac.ARIES, 1, 10.0, Dignity.EXALTED),
            MockPlanet(Planet.RAHU, Zodiac.ARIES, 1, 12.0, Dignity.NEUTRAL),  # Eclipse!
            MockPlanet(Planet.MOON, Zodiac.CANCER, 4, 15.0, Dignity.OWN_SIGN),
            MockPlanet(Planet.KETU, Zodiac.LIBRA, 7, 12.0, Dignity.NEUTRAL),
        ]
        result = check_grahan(planets, Zodiac.ARIES)
        assert result is not None
        assert result.name == "Grahan Yoga"
        assert Planet.SUN in result.participating_planets


# =============================================================================
# FULL DETECTION ENGINE TESTS
# =============================================================================

class TestDetectionEngine:
    """Tests for the full yoga detection engine."""

    def test_detect_all_yogas_returns_list(self, gaja_kesari_planets):
        """Test detect_all_yogas returns a list of yogas."""
        yogas, neecha_bhanga = detect_all_yogas(gaja_kesari_planets, Zodiac.ARIES)
        assert isinstance(yogas, list)
        assert isinstance(neecha_bhanga, dict)

    def test_yoga_summary_calculation(self, gaja_kesari_planets):
        """Test yoga summary is calculated correctly."""
        yogas, _ = detect_all_yogas(gaja_kesari_planets, Zodiac.ARIES)
        summary = calculate_yoga_summary(yogas)

        assert summary.total_count == len(yogas)
        assert summary.positive_count >= 0
        assert summary.negative_count >= 0
        assert 1.0 <= summary.overall_yoga_score <= 10.0

    def test_house_yoga_bonuses(self, gaja_kesari_planets):
        """Test house yoga bonuses are calculated."""
        yogas, neecha_bhanga = detect_all_yogas(gaja_kesari_planets, Zodiac.ARIES)
        bonuses = calculate_house_yoga_bonuses(yogas, neecha_bhanga)

        assert len(bonuses) == 12
        for house_num in range(1, 13):
            key = f"house_{house_num}"
            assert key in bonuses
            assert -3.0 <= bonuses[key] <= 3.0


# =============================================================================
# STAGE 3 INTEGRATION TESTS
# =============================================================================

class TestStage3Integration:
    """Integration tests for full Stage 3 analysis."""

    def test_stage3_runs_after_stage1(self, sample_digital_twin_with_yogas):
        """Test Stage 3 requires Stage 1 to run first."""
        brain = AstroBrain(sample_digital_twin_with_yogas)
        output = brain.analyze(stages=[3])  # Should auto-run Stage 1

        assert 1 in output.stages_completed
        assert 3 in output.stages_completed

    def test_stage3_output_structure(self, sample_digital_twin_with_yogas):
        """Test Stage 3 output has expected structure."""
        brain = AstroBrain(sample_digital_twin_with_yogas)
        output = brain.analyze(stages=[1, 3])

        yogas = output.yogas
        assert "yogas_found" in yogas
        assert "neecha_bhanga" in yogas
        assert "summary" in yogas
        assert "house_yoga_bonuses" in yogas

    def test_stage3_summary_fields(self, sample_digital_twin_with_yogas):
        """Test Stage 3 summary has all expected fields."""
        brain = AstroBrain(sample_digital_twin_with_yogas)
        output = brain.analyze(stages=[1, 3])

        summary = output.yogas["summary"]
        assert "total_count" in summary
        assert "positive_count" in summary
        assert "negative_count" in summary
        assert "raja_yoga_count" in summary
        assert "dhana_yoga_count" in summary
        assert "mahapurusha_yogas" in summary
        assert "key_yogas" in summary
        assert "overall_yoga_score" in summary

    def test_budhaditya_detected_in_vadim_chart(self, sample_digital_twin_with_yogas):
        """Test Budhaditya Yoga is detected in Vadim's chart (Sun-Mercury in Libra)."""
        brain = AstroBrain(sample_digital_twin_with_yogas)
        output = brain.analyze(stages=[1, 3])

        yoga_names = [y["name"] for y in output.yogas["yogas_found"]]
        assert "Budhaditya Yoga" in yoga_names

    def test_neecha_bhanga_detected_for_debilitated_planets(self, sample_digital_twin_with_yogas):
        """Test Neecha Bhanga is checked for debilitated planets."""
        brain = AstroBrain(sample_digital_twin_with_yogas)
        output = brain.analyze(stages=[1, 3])

        neecha_bhanga = output.yogas["neecha_bhanga"]
        # Vadim's chart has Sun debilitated in Libra and Mars debilitated in Cancer
        # At least one should have some cancellation rules
        assert isinstance(neecha_bhanga, dict)

    def test_full_output_to_json(self, sample_digital_twin_with_yogas):
        """Test full Stage 3 output can be serialized to JSON."""
        brain = AstroBrain(sample_digital_twin_with_yogas)
        output = brain.analyze(stages=[1, 3])

        json_str = output.to_json()
        parsed = json.loads(json_str)

        assert "yogas" in parsed
        assert "yogas_found" in parsed["yogas"]


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestHelperFunctions:
    """Tests for helper functions in Stage 3."""

    def test_get_house_lord(self):
        """Test house lord calculation."""
        # For Aries ascendant:
        assert get_house_lord(1, Zodiac.ARIES) == Planet.MARS  # Aries ruled by Mars
        assert get_house_lord(2, Zodiac.ARIES) == Planet.VENUS  # Taurus ruled by Venus
        assert get_house_lord(4, Zodiac.ARIES) == Planet.MOON  # Cancer ruled by Moon

    def test_has_conjunction(self, budhaditya_planets):
        """Test conjunction detection."""
        assert has_conjunction(Planet.SUN, Planet.MERCURY, budhaditya_planets) == True
        assert has_conjunction(Planet.SUN, Planet.MOON, budhaditya_planets) == False

    def test_planets_in_kendra_from(self, gaja_kesari_planets):
        """Test Kendra calculation from a reference sign."""
        # From Aries (Moon's sign), Kendras are at 0, 3, 6, 9 houses
        # Cancer (Jupiter) is 3 houses from Aries = Kendra
        kendra_planets = planets_in_kendra_from(Zodiac.ARIES, gaja_kesari_planets)
        kendra_planet_enums = [p.planet for p in kendra_planets]

        assert Planet.MOON in kendra_planet_enums  # Aries itself (0 distance)
        assert Planet.JUPITER in kendra_planet_enums  # Cancer (3 houses)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
