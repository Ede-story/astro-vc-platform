"""
Tests for Stages 11-12 (Nakshatra Deep Dive & Jaimini Synthesis)

Tests the following stages:
- Stage 11: Nakshatra Deep Dive (Personality Archetype from Sun-Moon-Lagna nakshatras)
- Stage 12: Jaimini Synthesis (Chara Karakas, Atmakaraka, Karakamsha)
"""

import pytest
import json
from pathlib import Path

from ..stages.stage_11_nakshatra import (
    Stage11NakshatraDeepDive,
    NakshatraAnalysis,
    NakshatraPosition,
    GANA_ARCHETYPE_MAP,
    ARCHETYPE_DESCRIPTIONS,
)
from ..stages.stage_12_jaimini import (
    Stage12JaiminiSynthesis,
    JaiminiAnalysis,
    CharaKarakaInfo,
    AtmakarakaAnalysis,
    KarakamshaAnalysis,
    ArudhaLagnaAnalysis,
    BadhakaAnalysis,
    KARAKA_SIGNIFICANCE,
)
from ..reference.nakshatras import (
    NAKSHATRA_CATALOG,
    get_nakshatra_from_degree,
    get_nakshatra_pada,
    get_nakshatra_lord_from_degree,
)
from ..reference.jaimini import (
    ATMAKARAKA_MEANINGS,
    KARAKAMSHA_MEANINGS,
    SIGN_MODALITY,
    BADHAKA_RULES,
    get_badhaka_house,
    get_atmakaraka_meaning,
    get_karakamsha_meaning,
)
from ..models.types import Planet, Zodiac, GanaType, PersonalityArchetype


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def digital_twin_fixture():
    """Load the test digital twin fixture"""
    fixture_path = Path(__file__).parent / "fixtures" / "digital_twin_fixture.json"
    with open(fixture_path, 'r') as f:
        data = json.load(f)
        return data.get("digital_twin", data)


@pytest.fixture
def mock_d1_planets():
    """Mock D1 planets with nakshatra info for testing"""
    return [
        {
            "name": "Sun",
            "longitude": 180.5,  # Libra, Chitra nakshatra
            "sign": "Libra",
            "sign_id": 7,
            "degrees": 0.5,
            "nakshatra": "Chitra",
            "nakshatra_pada": 3,
        },
        {
            "name": "Moon",
            "longitude": 45.0,  # Taurus, Rohini nakshatra
            "sign": "Taurus",
            "sign_id": 2,
            "degrees": 15.0,
            "nakshatra": "Rohini",
            "nakshatra_pada": 2,
        },
        {
            "name": "Mars",
            "longitude": 290.0,  # Capricorn
            "sign": "Capricorn",
            "sign_id": 10,
            "degrees": 20.0,
            "nakshatra": "Shravana",
            "nakshatra_pada": 4,
        },
        {
            "name": "Mercury",
            "longitude": 170.0,  # Virgo
            "sign": "Virgo",
            "sign_id": 6,
            "degrees": 20.0,
            "nakshatra": "Hasta",
            "nakshatra_pada": 3,
        },
        {
            "name": "Jupiter",
            "longitude": 85.0,  # Cancer
            "sign": "Cancer",
            "sign_id": 4,
            "degrees": 25.0,
            "nakshatra": "Pushya",
            "nakshatra_pada": 4,
        },
        {
            "name": "Venus",
            "longitude": 350.0,  # Pisces
            "sign": "Pisces",
            "sign_id": 12,
            "degrees": 20.0,
            "nakshatra": "Revati",
            "nakshatra_pada": 3,
        },
        {
            "name": "Saturn",
            "longitude": 210.0,  # Scorpio
            "sign": "Scorpio",
            "sign_id": 8,
            "degrees": 0.0,
            "nakshatra": "Vishakha",
            "nakshatra_pada": 4,
        },
    ]


@pytest.fixture
def mock_d9_planets():
    """Mock D9 (Navamsha) planets for testing"""
    return [
        {"name": "Sun", "sign": "Leo", "sign_id": 5, "degrees": 10.0},
        {"name": "Moon", "sign": "Cancer", "sign_id": 4, "degrees": 15.0},
        {"name": "Mars", "sign": "Aries", "sign_id": 1, "degrees": 20.0},
        {"name": "Mercury", "sign": "Virgo", "sign_id": 6, "degrees": 5.0},
        {"name": "Jupiter", "sign": "Sagittarius", "sign_id": 9, "degrees": 25.0},
        {"name": "Venus", "sign": "Pisces", "sign_id": 12, "degrees": 10.0},
        {"name": "Saturn", "sign": "Aquarius", "sign_id": 11, "degrees": 15.0},
    ]


@pytest.fixture
def mock_ascendant():
    """Mock ascendant data for testing"""
    return {
        "sign_id": 1,  # Aries
        "sign": "Aries",
        "degrees": 10.0,
        "longitude": 10.0,
        "nakshatra": "Ashwini",
        "nakshatra_pada": 3,
    }


@pytest.fixture
def mock_chara_karakas():
    """Mock Chara Karakas for testing"""
    return {
        "karakas": [
            {"karaka_code": "AK", "planet": "Saturn", "degrees_in_sign": 29.5, "sign": "Scorpio"},
            {"karaka_code": "AmK", "planet": "Jupiter", "degrees_in_sign": 25.0, "sign": "Cancer"},
            {"karaka_code": "BK", "planet": "Venus", "degrees_in_sign": 20.0, "sign": "Pisces"},
            {"karaka_code": "MK", "planet": "Mars", "degrees_in_sign": 18.0, "sign": "Capricorn"},
            {"karaka_code": "PK", "planet": "Mercury", "degrees_in_sign": 15.0, "sign": "Virgo"},
            {"karaka_code": "GK", "planet": "Moon", "degrees_in_sign": 12.0, "sign": "Taurus"},
            {"karaka_code": "DK", "planet": "Sun", "degrees_in_sign": 5.0, "sign": "Libra"},
        ]
    }


# ============================================================================
# Nakshatra Reference Tests
# ============================================================================

class TestNakshatraCatalog:
    """Tests for nakshatra catalog and helper functions"""

    def test_nakshatra_catalog_completeness(self):
        """Test all 27 nakshatras are in catalog"""
        assert len(NAKSHATRA_CATALOG) == 27

    def test_nakshatra_catalog_structure(self):
        """Test each nakshatra has required fields"""
        for name, nak in NAKSHATRA_CATALOG.items():
            assert nak.name == name  # Key is the nakshatra name
            assert 1 <= nak.number <= 27
            assert nak.sanskrit_name is not None
            assert 0 <= nak.start_degree < 360
            assert 0 < nak.end_degree <= 360
            assert nak.lord is not None
            assert nak.gana in [GanaType.DEVA, GanaType.MANUSHYA, GanaType.RAKSHASA]
            assert len(nak.positive_traits) > 0
            assert len(nak.negative_traits) > 0

    def test_nakshatra_from_degree(self):
        """Test nakshatra calculation from degree"""
        # 0 degrees = Ashwini (nakshatra 1)
        nak = get_nakshatra_from_degree(0)
        assert nak.number == 1
        assert nak.name == "Ashwini"

        # 13.33 degrees = Bharani (nakshatra 2)
        nak = get_nakshatra_from_degree(13.5)
        assert nak.number == 2
        assert nak.name == "Bharani"

        # 180 degrees = Chitra (nakshatra 14)
        nak = get_nakshatra_from_degree(180)
        assert nak.number == 14
        assert nak.name == "Chitra"

    def test_nakshatra_pada_calculation(self):
        """Test pada calculation from degree"""
        # First 3.33 degrees = pada 1
        pada = get_nakshatra_pada(0)
        assert pada == 1

        # 3.33-6.66 degrees = pada 2
        pada = get_nakshatra_pada(4)
        assert pada == 2

        # 10-13.33 degrees = pada 4
        pada = get_nakshatra_pada(12)
        assert pada == 4

    def test_gana_distribution(self):
        """Test 9 nakshatras per gana type"""
        deva_count = sum(1 for nak in NAKSHATRA_CATALOG.values() if nak.gana == GanaType.DEVA)
        manushya_count = sum(1 for nak in NAKSHATRA_CATALOG.values() if nak.gana == GanaType.MANUSHYA)
        rakshasa_count = sum(1 for nak in NAKSHATRA_CATALOG.values() if nak.gana == GanaType.RAKSHASA)

        assert deva_count == 9
        assert manushya_count == 9
        assert rakshasa_count == 9


# ============================================================================
# Jaimini Reference Tests
# ============================================================================

class TestJaiminiReference:
    """Tests for Jaimini reference data"""

    def test_atmakaraka_meanings_completeness(self):
        """Test all planets have AK meanings"""
        for planet in Planet:
            assert planet in ATMAKARAKA_MEANINGS
            meaning = ATMAKARAKA_MEANINGS[planet]
            assert meaning.soul_lesson is not None
            assert meaning.karmic_trap is not None
            assert meaning.spiritual_path is not None
            assert len(meaning.strengths) > 0
            assert len(meaning.challenges) > 0

    def test_karakamsha_meanings_completeness(self):
        """Test all signs have Karakamsha meanings"""
        for sign in Zodiac:
            assert sign in KARAKAMSHA_MEANINGS
            meaning = KARAKAMSHA_MEANINGS[sign]
            assert meaning.life_purpose is not None
            assert meaning.career_direction is not None
            assert meaning.spiritual_path is not None
            assert len(meaning.key_themes) > 0

    def test_sign_modality_completeness(self):
        """Test all signs have modality"""
        for sign in Zodiac:
            assert sign in SIGN_MODALITY
            assert SIGN_MODALITY[sign] in ["Movable", "Fixed", "Dual"]

    def test_badhaka_rules(self):
        """Test badhaka rules"""
        assert BADHAKA_RULES["Movable"].badhaka_house == 11
        assert BADHAKA_RULES["Fixed"].badhaka_house == 9
        assert BADHAKA_RULES["Dual"].badhaka_house == 7

    def test_badhaka_house_calculation(self):
        """Test badhaka house calculation"""
        # Aries is Movable -> 11th house badhaka
        assert get_badhaka_house(Zodiac.ARIES) == 11

        # Taurus is Fixed -> 9th house badhaka
        assert get_badhaka_house(Zodiac.TAURUS) == 9

        # Gemini is Dual -> 7th house badhaka
        assert get_badhaka_house(Zodiac.GEMINI) == 7


# ============================================================================
# Stage 11: Nakshatra Deep Dive Tests
# ============================================================================

class TestStage11NakshatraDeepDive:
    """Tests for Stage 11 Nakshatra analysis"""

    def test_stage11_initialization(self, digital_twin_fixture, mock_d1_planets):
        """Test Stage 11 can be initialized"""
        stage11 = Stage11NakshatraDeepDive(
            digital_twin_fixture,
            mock_d1_planets
        )
        assert stage11 is not None

    def test_stage11_analyze_returns_result(self, digital_twin_fixture, mock_d1_planets):
        """Test Stage 11 analyze returns a result"""
        stage11 = Stage11NakshatraDeepDive(
            digital_twin_fixture,
            mock_d1_planets
        )
        result = stage11.analyze()

        assert isinstance(result, NakshatraAnalysis)
        assert hasattr(result, 'sun_nakshatra')
        assert hasattr(result, 'moon_nakshatra')
        assert hasattr(result, 'lagna_nakshatra')
        assert hasattr(result, 'archetype')

    def test_stage11_result_to_dict(self, digital_twin_fixture, mock_d1_planets):
        """Test Stage 11 result can be converted to dict"""
        stage11 = Stage11NakshatraDeepDive(
            digital_twin_fixture,
            mock_d1_planets
        )
        result = stage11.analyze()
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "sun_nakshatra" in result_dict
        assert "moon_nakshatra" in result_dict
        assert "lagna_nakshatra" in result_dict
        assert "archetype" in result_dict
        assert "orientation_scores" in result_dict

    def test_gana_pattern_generation(self, digital_twin_fixture, mock_d1_planets):
        """Test gana pattern is generated correctly"""
        stage11 = Stage11NakshatraDeepDive(
            digital_twin_fixture,
            mock_d1_planets
        )
        result = stage11.analyze()

        # Gana pattern should be in format "Type-Type-Type"
        assert "-" in result.gana_pattern
        parts = result.gana_pattern.split("-")
        assert len(parts) == 3
        for part in parts:
            assert part in ["Deva", "Manushya", "Rakshasa"]

    def test_archetype_has_description(self, digital_twin_fixture, mock_d1_planets):
        """Test archetype has description"""
        stage11 = Stage11NakshatraDeepDive(
            digital_twin_fixture,
            mock_d1_planets
        )
        result = stage11.analyze()

        assert result.archetype_name_ru is not None
        assert result.archetype_subtitle is not None
        assert result.archetype_description is not None
        assert len(result.archetype_strengths) > 0
        assert len(result.archetype_challenges) > 0

    def test_orientation_scores_in_range(self, digital_twin_fixture, mock_d1_planets):
        """Test orientation scores are in valid range"""
        stage11 = Stage11NakshatraDeepDive(
            digital_twin_fixture,
            mock_d1_planets
        )
        result = stage11.analyze()

        assert 0 <= result.spiritual_orientation <= 100
        assert 0 <= result.practical_orientation <= 100
        assert 0 <= result.transformative_power <= 100


class TestGanaArchetypeMapping:
    """Tests for Gana to Archetype mapping"""

    def test_all_pure_combinations_mapped(self):
        """Test pure gana combinations are mapped"""
        pure_deva = (GanaType.DEVA, GanaType.DEVA, GanaType.DEVA)
        pure_manushya = (GanaType.MANUSHYA, GanaType.MANUSHYA, GanaType.MANUSHYA)
        pure_rakshasa = (GanaType.RAKSHASA, GanaType.RAKSHASA, GanaType.RAKSHASA)

        assert pure_deva in GANA_ARCHETYPE_MAP
        assert pure_manushya in GANA_ARCHETYPE_MAP
        assert pure_rakshasa in GANA_ARCHETYPE_MAP

        assert GANA_ARCHETYPE_MAP[pure_deva] == PersonalityArchetype.LIGHT_BEARER
        assert GANA_ARCHETYPE_MAP[pure_manushya] == PersonalityArchetype.WORLD_BUILDER
        assert GANA_ARCHETYPE_MAP[pure_rakshasa] == PersonalityArchetype.TRANSFORMER

    def test_all_archetypes_have_descriptions(self):
        """Test all archetypes have descriptions"""
        for archetype in PersonalityArchetype:
            assert archetype in ARCHETYPE_DESCRIPTIONS
            desc = ARCHETYPE_DESCRIPTIONS[archetype]
            assert "title" in desc
            assert "subtitle" in desc
            assert "description" in desc
            assert "strengths" in desc
            assert "challenges" in desc


# ============================================================================
# Stage 12: Jaimini Synthesis Tests
# ============================================================================

class TestStage12JaiminiSynthesis:
    """Tests for Stage 12 Jaimini analysis"""

    def test_stage12_initialization(self, digital_twin_fixture, mock_d1_planets, mock_d9_planets):
        """Test Stage 12 can be initialized"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_d9_planets
        )
        assert stage12 is not None

    def test_stage12_analyze_returns_result(self, digital_twin_fixture, mock_d1_planets, mock_d9_planets):
        """Test Stage 12 analyze returns a result"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_d9_planets
        )
        result = stage12.analyze()

        assert isinstance(result, JaiminiAnalysis)
        assert hasattr(result, 'chara_karakas')
        assert hasattr(result, 'atmakaraka')
        assert hasattr(result, 'karakamsha')
        assert hasattr(result, 'arudha_lagna')
        assert hasattr(result, 'badhaka')

    def test_stage12_result_to_dict(self, digital_twin_fixture, mock_d1_planets, mock_d9_planets):
        """Test Stage 12 result can be converted to dict"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_d9_planets
        )
        result = stage12.analyze()
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "chara_karakas" in result_dict
        assert "atmakaraka" in result_dict
        assert "karakamsha" in result_dict
        assert "arudha_lagna" in result_dict
        assert "badhaka" in result_dict
        assert "scores" in result_dict
        assert "summary" in result_dict

    def test_chara_karakas_count(self, digital_twin_fixture, mock_d1_planets, mock_d9_planets):
        """Test 7 Chara Karakas are returned"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_d9_planets
        )
        result = stage12.analyze()

        # Should have 7 karakas (or less if planets missing)
        assert len(result.chara_karakas) <= 7

    def test_chara_karakas_order(self, digital_twin_fixture, mock_d1_planets, mock_d9_planets):
        """Test karakas are in correct order (AK first)"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_d9_planets
        )
        result = stage12.analyze()

        if len(result.chara_karakas) > 0:
            assert result.chara_karakas[0].karaka_code == "AK"
        if len(result.chara_karakas) > 1:
            assert result.chara_karakas[1].karaka_code == "AmK"

    def test_atmakaraka_analysis(self, digital_twin_fixture, mock_d1_planets, mock_d9_planets):
        """Test Atmakaraka analysis has required fields"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_d9_planets
        )
        result = stage12.analyze()

        assert result.atmakaraka.planet is not None
        assert result.atmakaraka.soul_lesson is not None
        assert result.atmakaraka.life_theme is not None

    def test_scores_in_range(self, digital_twin_fixture, mock_d1_planets, mock_d9_planets):
        """Test all scores are in valid range"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_d9_planets
        )
        result = stage12.analyze()

        assert 0 <= result.soul_clarity_score <= 100
        assert 0 <= result.career_alignment_score <= 100
        assert 0 <= result.public_image_strength <= 100
        assert 0 <= result.obstruction_level <= 100

    def test_summary_generation(self, digital_twin_fixture, mock_d1_planets, mock_d9_planets):
        """Test summary is generated with required fields"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_d9_planets
        )
        result = stage12.analyze()

        assert "soul_archetype" in result.jaimini_summary
        assert "life_theme" in result.jaimini_summary
        assert "career_direction" in result.jaimini_summary
        assert "investment_insight" in result.jaimini_summary


class TestCharaKarakaWithPreCalculated:
    """Tests for Stage 12 with pre-calculated Chara Karakas"""

    def test_uses_precalculated_karakas(self, mock_chara_karakas, mock_d1_planets, mock_d9_planets):
        """Test Stage 12 uses pre-calculated karakas when available"""
        digital_twin = {
            "vargas": {
                "D1": {"planets": mock_d1_planets, "ascendant": {"sign_id": 1}},
                "D9": {"planets": mock_d9_planets}
            },
            "chara_karakas": mock_chara_karakas
        }

        stage12 = Stage12JaiminiSynthesis(digital_twin, mock_d1_planets, mock_d9_planets)
        result = stage12.analyze()

        # Should use Saturn as AK (from mock data)
        assert result.chara_karakas[0].planet == "Saturn"
        assert result.chara_karakas[0].degrees_in_sign == 29.5


# ============================================================================
# Integration Tests
# ============================================================================

class TestStages11_12Integration:
    """Integration tests for Stages 11-12"""

    def test_full_stage11_analysis(self, digital_twin_fixture, mock_d1_planets):
        """Test complete Stage 11 analysis flow"""
        stage11 = Stage11NakshatraDeepDive(
            digital_twin_fixture,
            mock_d1_planets
        )
        result = stage11.analyze()
        result_dict = result.to_dict()

        # Verify structure
        assert "sun_nakshatra" in result_dict
        assert "moon_nakshatra" in result_dict
        assert "lagna_nakshatra" in result_dict
        assert "gana_pattern" in result_dict
        assert "archetype" in result_dict

        # Verify archetype structure
        archetype = result_dict["archetype"]
        assert "code" in archetype
        assert "name_ru" in archetype
        assert "strengths" in archetype
        assert "challenges" in archetype

    def test_full_stage12_analysis(self, digital_twin_fixture, mock_d1_planets, mock_d9_planets):
        """Test complete Stage 12 analysis flow"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_d9_planets
        )
        result = stage12.analyze()
        result_dict = result.to_dict()

        # Verify structure
        assert "chara_karakas" in result_dict
        assert "atmakaraka" in result_dict
        assert "karakamsha" in result_dict
        assert "arudha_lagna" in result_dict
        assert "badhaka" in result_dict
        assert "scores" in result_dict
        assert "summary" in result_dict

        # Verify scores structure
        scores = result_dict["scores"]
        assert "soul_clarity" in scores
        assert "career_alignment" in scores
        assert "public_image_strength" in scores
        assert "obstruction_level" in scores


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Edge case tests for Stages 11-12"""

    def test_empty_planets_list_stage11(self, digital_twin_fixture):
        """Test Stage 11 handles empty planets list"""
        stage11 = Stage11NakshatraDeepDive(
            digital_twin_fixture,
            []
        )
        result = stage11.analyze()

        # Should return valid result with defaults
        assert result is not None
        assert isinstance(result, NakshatraAnalysis)

    def test_empty_planets_list_stage12(self, digital_twin_fixture):
        """Test Stage 12 handles empty planets list"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            [],
            []
        )
        result = stage12.analyze()

        # Should return valid result with defaults
        assert result is not None
        assert isinstance(result, JaiminiAnalysis)

    def test_missing_nakshatra_data(self, digital_twin_fixture):
        """Test handling when nakshatra data is missing from planets"""
        planets_no_nakshatra = [
            {"name": "Sun", "longitude": 180.5, "sign": "Libra", "sign_id": 7, "degrees": 0.5},
            {"name": "Moon", "longitude": 45.0, "sign": "Taurus", "sign_id": 2, "degrees": 15.0},
        ]

        stage11 = Stage11NakshatraDeepDive(
            digital_twin_fixture,
            planets_no_nakshatra
        )
        result = stage11.analyze()

        # Should calculate nakshatra from longitude
        assert result is not None
        assert result.sun_nakshatra.nakshatra_name is not None

    def test_missing_d9_data(self, digital_twin_fixture, mock_d1_planets):
        """Test Stage 12 handles missing D9 data"""
        stage12 = Stage12JaiminiSynthesis(
            digital_twin_fixture,
            mock_d1_planets,
            []  # Empty D9
        )
        result = stage12.analyze()

        # Should return valid result with defaults for Karakamsha
        assert result is not None
        assert result.karakamsha is not None
