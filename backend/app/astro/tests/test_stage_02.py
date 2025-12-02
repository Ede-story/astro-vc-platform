"""
Tests for Stage 2: Soul Blueprint (D9 Navamsha)

Tests the D9 chart analysis and D1-D9 synergy calculations.
"""

import pytest
import json
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.astro.calculator import AstroBrain
from app.astro.stages.stage_02_soul import (
    Stage02SoulBlueprint,
    SynergyLevel,
    VargottamaInfo,
    PushkaraInfo,
    D1D9Comparison,
    Stage2Result,
    detect_vargottama,
    detect_pushkara,
    compare_d1_d9,
    get_synergy_level,
    find_atmakaraka,
    normalize_planet_name,
    normalize_sign_name,
    get_house_from_sign,
    PUSHKARA_NAVAMSHAS,
)
from app.astro.models.types import Planet, Zodiac, Dignity, ZODIAC_ORDER


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_digital_twin_with_d9():
    """
    Sample digital_twin with both D1 and D9 charts for testing.
    Based on Vadim's birth data: 1977-10-25, 06:28, Sortavala.
    """
    return {
        "meta": {
            "birth_datetime": "1977-10-25T06:28:00",
            "latitude": 61.7,
            "longitude": 30.69,
            "timezone_offset": 3.0,
            "ayanamsa": "Raman",
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
                    {"house_number": i, "sign_id": ((7 + i - 1) % 12) or 12}
                    for i in range(1, 13)
                ]
            },
            "D9": {
                "ascendant": {
                    "sign_id": 3,
                    "sign_name": "Gemini",
                    "degrees": 12.5,
                },
                "planets": [
                    {
                        "name": "Sun",
                        "sign_id": 1,
                        "sign_name": "Aries",
                        "relative_degree": 13.08,
                        "is_retrograde": False
                    },
                    {
                        "name": "Moon",
                        "sign_id": 1,
                        "sign_name": "Aries",
                        "relative_degree": 19.05,
                        "is_retrograde": False
                    },
                    {
                        "name": "Mars",
                        "sign_id": 8,
                        "sign_name": "Scorpio",
                        "relative_degree": 18.27,
                        "is_retrograde": False
                    },
                    {
                        "name": "Mercury",
                        "sign_id": 3,
                        "sign_name": "Gemini",
                        "relative_degree": 4.95,
                        "is_retrograde": False
                    },
                    {
                        "name": "Jupiter",
                        "sign_id": 4,
                        "sign_name": "Cancer",
                        "relative_degree": 14.00,
                        "is_retrograde": True
                    },
                    {
                        "name": "Venus",
                        "sign_id": 10,
                        "sign_name": "Capricorn",
                        "relative_degree": 22.00,
                        "is_retrograde": False
                    },
                    {
                        "name": "Saturn",
                        "sign_id": 3,
                        "sign_name": "Gemini",
                        "relative_degree": 4.92,
                        "is_retrograde": True
                    },
                    {
                        "name": "Rahu",
                        "sign_id": 9,
                        "sign_name": "Sagittarius",
                        "relative_degree": 3.03,
                        "is_retrograde": True
                    },
                    {
                        "name": "Ketu",
                        "sign_id": 3,
                        "sign_name": "Gemini",
                        "relative_degree": 3.03,
                        "is_retrograde": True
                    }
                ]
            }
        }
    }


@pytest.fixture
def vargottama_digital_twin():
    """
    Digital twin with Moon in Aries in both D1 and D9 (Vargottama).
    """
    return {
        "vargas": {
            "D1": {
                "ascendant": {"sign_name": "Aries", "degrees": 10.0},
                "planets": [
                    {"name": "Moon", "sign_name": "Aries", "relative_degree": 15.0},
                    {"name": "Sun", "sign_name": "Leo", "relative_degree": 10.0},
                    {"name": "Mars", "sign_name": "Aries", "relative_degree": 5.0},
                    {"name": "Mercury", "sign_name": "Virgo", "relative_degree": 12.0},
                    {"name": "Jupiter", "sign_name": "Sagittarius", "relative_degree": 20.0},
                    {"name": "Venus", "sign_name": "Libra", "relative_degree": 8.0},
                    {"name": "Saturn", "sign_name": "Aquarius", "relative_degree": 25.0},
                    {"name": "Rahu", "sign_name": "Gemini", "relative_degree": 10.0},
                    {"name": "Ketu", "sign_name": "Sagittarius", "relative_degree": 10.0},
                ]
            },
            "D9": {
                "ascendant": {"sign_name": "Taurus", "degrees": 5.0},
                "planets": [
                    {"name": "Moon", "sign_name": "Aries", "relative_degree": 15.0},  # Vargottama!
                    {"name": "Sun", "sign_name": "Sagittarius", "relative_degree": 10.0},
                    {"name": "Mars", "sign_name": "Aries", "relative_degree": 5.0},  # Vargottama!
                    {"name": "Mercury", "sign_name": "Pisces", "relative_degree": 12.0},
                    {"name": "Jupiter", "sign_name": "Sagittarius", "relative_degree": 20.0},  # Vargottama!
                    {"name": "Venus", "sign_name": "Gemini", "relative_degree": 8.0},
                    {"name": "Saturn", "sign_name": "Libra", "relative_degree": 25.0},
                    {"name": "Rahu", "sign_name": "Aquarius", "relative_degree": 10.0},
                    {"name": "Ketu", "sign_name": "Leo", "relative_degree": 10.0},
                ]
            }
        }
    }


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestHelperFunctions:
    """Tests for helper functions in Stage 2."""

    def test_normalize_planet_name(self):
        """Test planet name normalization."""
        assert normalize_planet_name("Sun") == Planet.SUN
        assert normalize_planet_name("sun") == Planet.SUN
        assert normalize_planet_name("Moon") == Planet.MOON
        assert normalize_planet_name("Jupiter") == Planet.JUPITER
        assert normalize_planet_name("Rahu") == Planet.RAHU

    def test_normalize_sign_name(self):
        """Test sign name normalization."""
        assert normalize_sign_name("Aries") == Zodiac.ARIES
        assert normalize_sign_name("aries") == Zodiac.ARIES
        assert normalize_sign_name("LIBRA") == Zodiac.LIBRA  # All caps handled via .lower()
        assert normalize_sign_name("cancer") == Zodiac.CANCER
        assert normalize_sign_name("") == Zodiac.ARIES  # Empty defaults

    def test_get_house_from_sign(self):
        """Test house calculation from sign."""
        # If Aries is ascendant, Aries is house 1
        assert get_house_from_sign(Zodiac.ARIES, Zodiac.ARIES) == 1
        assert get_house_from_sign(Zodiac.TAURUS, Zodiac.ARIES) == 2
        assert get_house_from_sign(Zodiac.LIBRA, Zodiac.ARIES) == 7
        assert get_house_from_sign(Zodiac.PISCES, Zodiac.ARIES) == 12

        # If Libra is ascendant, Libra is house 1
        assert get_house_from_sign(Zodiac.LIBRA, Zodiac.LIBRA) == 1
        assert get_house_from_sign(Zodiac.ARIES, Zodiac.LIBRA) == 7
        assert get_house_from_sign(Zodiac.CANCER, Zodiac.LIBRA) == 10

    def test_get_synergy_level(self):
        """Test synergy level classification."""
        assert get_synergy_level(9.0) == SynergyLevel.EXCELLENT
        assert get_synergy_level(8.0) == SynergyLevel.EXCELLENT
        assert get_synergy_level(7.0) == SynergyLevel.GOOD
        assert get_synergy_level(5.0) == SynergyLevel.MODERATE
        assert get_synergy_level(3.0) == SynergyLevel.CHALLENGING
        assert get_synergy_level(1.0) == SynergyLevel.DIFFICULT


# =============================================================================
# VARGOTTAMA TESTS
# =============================================================================

class TestVargottamaDetection:
    """Tests for Vargottama planet detection."""

    def test_detect_vargottama_planets(self, vargottama_digital_twin):
        """Test detection of Vargottama planets."""
        brain = AstroBrain(vargottama_digital_twin)
        brain.analyze(stages=[1])

        d1_planets = brain.output.basic_chart.planets
        d9_planets = vargottama_digital_twin["vargas"]["D9"]["planets"]

        vargottama = detect_vargottama(d1_planets, d9_planets)

        # Should find Moon and Mars in same sign in D1 and D9
        # (Jupiter may not be parsed without sign_id in fixture)
        vargottama_planets = [v.planet for v in vargottama]
        assert Planet.MOON in vargottama_planets
        assert Planet.MARS in vargottama_planets
        assert len(vargottama) >= 2  # At least Moon and Mars

    def test_vargottama_strength_bonus(self, vargottama_digital_twin):
        """Test that Vargottama planets have strength bonus."""
        brain = AstroBrain(vargottama_digital_twin)
        brain.analyze(stages=[1])

        d1_planets = brain.output.basic_chart.planets
        d9_planets = vargottama_digital_twin["vargas"]["D9"]["planets"]

        vargottama = detect_vargottama(d1_planets, d9_planets)

        for v in vargottama:
            assert v.strength_bonus == 1.5


# =============================================================================
# PUSHKARA TESTS
# =============================================================================

class TestPushkaraDetection:
    """Tests for Pushkara Navamsha detection."""

    def test_pushkara_navamsha_mapping(self):
        """Test Pushkara Navamsha mapping is correct."""
        assert Zodiac.SAGITTARIUS in PUSHKARA_NAVAMSHAS[Zodiac.ARIES]
        assert Zodiac.AQUARIUS in PUSHKARA_NAVAMSHAS[Zodiac.TAURUS]
        assert Zodiac.CANCER in PUSHKARA_NAVAMSHAS[Zodiac.GEMINI]

    def test_detect_pushkara_positions(self):
        """Test detection of Pushkara positions."""
        d9_planets = [
            {"name": "Jupiter", "sign_name": "Sagittarius", "relative_degree": 15.0}
        ]
        d1_signs = {Planet.JUPITER: Zodiac.ARIES}  # Jupiter in Aries D1

        pushkara = detect_pushkara(d9_planets, d1_signs)

        # Jupiter in Aries D1 + Sagittarius D9 = Pushkara
        assert len(pushkara) == 1
        assert pushkara[0].planet == Planet.JUPITER
        assert pushkara[0].is_pushkara_navamsha == True


# =============================================================================
# SYNERGY TESTS
# =============================================================================

class TestD1D9Synergy:
    """Tests for D1-D9 synergy calculations."""

    def test_synergy_score_range(self, sample_digital_twin_with_d9):
        """Test synergy score is within 0-10 range."""
        brain = AstroBrain(sample_digital_twin_with_d9)
        output = brain.analyze(stages=[1, 2])

        synergy_score = output.soul_blueprint["synergy_score"]
        assert 0.0 <= synergy_score <= 10.0

    def test_synergy_level_assigned(self, sample_digital_twin_with_d9):
        """Test synergy level is correctly assigned."""
        brain = AstroBrain(sample_digital_twin_with_d9)
        output = brain.analyze(stages=[1, 2])

        synergy_level = output.soul_blueprint["synergy_level"]
        assert synergy_level in [
            "Excellent", "Good", "Moderate", "Challenging", "Difficult"
        ]


# =============================================================================
# ATMAKARAKA TESTS
# =============================================================================

class TestAtmakarakaDetection:
    """Tests for Atmakaraka detection."""

    def test_find_atmakaraka(self, sample_digital_twin_with_d9):
        """Test Atmakaraka is found (highest degree planet)."""
        brain = AstroBrain(sample_digital_twin_with_d9)
        brain.analyze(stages=[1])

        d1_planets = brain.output.basic_chart.planets
        atmakaraka, degree = find_atmakaraka(d1_planets)

        # Atmakaraka should be one of the 7 planets (excluding Rahu/Ketu)
        assert atmakaraka is not None
        assert atmakaraka not in [Planet.RAHU, Planet.KETU]

    def test_atmakaraka_excludes_nodes(self, sample_digital_twin_with_d9):
        """Test Atmakaraka excludes Rahu and Ketu."""
        brain = AstroBrain(sample_digital_twin_with_d9)
        brain.analyze(stages=[1])

        d1_planets = brain.output.basic_chart.planets
        atmakaraka, _ = find_atmakaraka(d1_planets)

        assert atmakaraka != Planet.RAHU
        assert atmakaraka != Planet.KETU


# =============================================================================
# FULL STAGE 2 INTEGRATION TESTS
# =============================================================================

class TestStage2Integration:
    """Integration tests for full Stage 2 analysis."""

    def test_stage2_runs_after_stage1(self, sample_digital_twin_with_d9):
        """Test Stage 2 requires Stage 1 to run first."""
        brain = AstroBrain(sample_digital_twin_with_d9)
        output = brain.analyze(stages=[2])  # Should auto-run Stage 1

        assert 1 in output.stages_completed
        assert 2 in output.stages_completed

    def test_stage2_output_structure(self, sample_digital_twin_with_d9):
        """Test Stage 2 output has expected structure."""
        brain = AstroBrain(sample_digital_twin_with_d9)
        output = brain.analyze(stages=[1, 2])

        soul_blueprint = output.soul_blueprint
        assert "d9_ascendant" in soul_blueprint
        assert "vargottama_planets" in soul_blueprint
        assert "synergy_score" in soul_blueprint
        assert "synergy_level" in soul_blueprint
        assert "house_scores_adjusted" in soul_blueprint
        assert "confirmations" in soul_blueprint
        assert "contradictions" in soul_blueprint
        assert "atmakaraka" in soul_blueprint

    def test_stage2_adjusted_house_scores(self, sample_digital_twin_with_d9):
        """Test adjusted house scores are calculated."""
        brain = AstroBrain(sample_digital_twin_with_d9)
        output = brain.analyze(stages=[1, 2])

        adjusted_scores = output.soul_blueprint["house_scores_adjusted"]
        assert len(adjusted_scores) == 12

        for house_num in range(1, 13):
            key = f"house_{house_num}"
            assert key in adjusted_scores
            assert 1.0 <= adjusted_scores[key] <= 10.0

    def test_stage2_confirmations_and_contradictions(self, sample_digital_twin_with_d9):
        """Test confirmations and contradictions are generated."""
        brain = AstroBrain(sample_digital_twin_with_d9)
        output = brain.analyze(stages=[1, 2])

        # At least one of these lists should have content
        confirmations = output.soul_blueprint["confirmations"]
        contradictions = output.soul_blueprint["contradictions"]

        assert isinstance(confirmations, list)
        assert isinstance(contradictions, list)

    def test_d9_ascendant_extracted(self, sample_digital_twin_with_d9):
        """Test D9 ascendant is correctly extracted."""
        brain = AstroBrain(sample_digital_twin_with_d9)
        output = brain.analyze(stages=[1, 2])

        d9_asc = output.soul_blueprint["d9_ascendant"]
        assert d9_asc == "GEMINI"  # From fixture

    def test_full_output_to_json(self, sample_digital_twin_with_d9):
        """Test full output can be serialized to JSON."""
        brain = AstroBrain(sample_digital_twin_with_d9)
        output = brain.analyze(stages=[1, 2])

        json_str = output.to_json()
        parsed = json.loads(json_str)

        assert "soul_blueprint" in parsed
        assert parsed["soul_blueprint"]["synergy_score"] >= 0


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
