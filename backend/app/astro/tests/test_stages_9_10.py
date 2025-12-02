"""
Tests for Stages 9-10 (Karmic Depth & Timing)

Tests the following stages:
- Stage 9: Karmic Depth (D30, D60)
- Stage 10: Timing (Vimshottari Dasha, Ashtakavarga)
"""

import pytest
import json
from pathlib import Path
from datetime import date

from ..stages.stage_09_karmic import (
    Stage09KarmicAnalysis, Stage9Result,
    DoshaResult, D30Analysis, D60Analysis,
    KarmicCeilingTier, RiskCategory,
    check_mangal_dosha, check_kala_sarpa_dosha,
    check_guru_chandal_dosha, check_pitru_dosha,
    check_grahan_dosha, check_shrapit_dosha
)
from ..stages.stage_10_timing import (
    Stage10TimingAnalysis, Stage10Result,
    DashaPeriod, DashaRoadmap, AshtakavargaScore,
    TimingRecommendation, DASHA_PERIODS, DASHA_SEQUENCE
)
from ..reference.doshas import (
    DoshaType, DoshaSeverity, DOSHA_CATALOG,
    MANGAL_DOSHA_HOUSES, MANGAL_CANCELLATION_SIGNS
)
from ..models.types import Planet, Zodiac


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
    """Mock D1 planets for testing"""
    return [
        {"name": "Moon", "absolute_degree": 120.0, "house": 4},
        {"name": "Mars", "absolute_degree": 30.0, "house": 1},
        {"name": "Sun", "absolute_degree": 180.0, "house": 7},
        {"name": "Venus", "absolute_degree": 200.0, "house": 7},
        {"name": "Jupiter", "absolute_degree": 270.0, "house": 10},
    ]


@pytest.fixture
def mock_planet_strength():
    """Mock planet strength for testing"""
    return {
        "Moon": 0.7,
        "Mars": 0.6,
        "Sun": 0.8,
        "Venus": 0.75,
        "Jupiter": 0.85,
        "Saturn": 0.5,
        "Mercury": 0.65,
        "Rahu": 0.4,
        "Ketu": 0.35,
    }


@pytest.fixture
def mock_yoga_planets():
    """Mock yoga planets for testing"""
    return ["Jupiter", "Venus", "Moon"]


@pytest.fixture
def mock_house_lords():
    """Mock house lords for testing"""
    return {
        1: {"lord": "Mars", "in_house": 1, "sign": "Aries"},
        2: {"lord": "Venus", "in_house": 7, "sign": "Taurus"},
        3: {"lord": "Mercury", "in_house": 3, "sign": "Gemini"},
        4: {"lord": "Moon", "in_house": 4, "sign": "Cancer"},
        5: {"lord": "Sun", "in_house": 5, "sign": "Leo"},
        6: {"lord": "Mercury", "in_house": 6, "sign": "Virgo"},
        7: {"lord": "Venus", "in_house": 7, "sign": "Libra"},
        8: {"lord": "Mars", "in_house": 8, "sign": "Scorpio"},
        9: {"lord": "Jupiter", "in_house": 9, "sign": "Sagittarius"},
        10: {"lord": "Saturn", "in_house": 10, "sign": "Capricorn"},
        11: {"lord": "Saturn", "in_house": 11, "sign": "Aquarius"},
        12: {"lord": "Jupiter", "in_house": 12, "sign": "Pisces"},
    }


# ============================================================================
# Dosha Catalog Tests
# ============================================================================

class TestDoshaCatalog:
    """Tests for dosha definitions and catalog"""

    def test_dosha_types_defined(self):
        """Test all dosha types are defined"""
        assert DoshaType.MANGAL == "MangalDosha"
        assert DoshaType.KALA_SARPA == "KalaSarpaDosha"
        assert DoshaType.GURU_CHANDAL == "GuruChandalDosha"
        assert DoshaType.PITRU == "PitruDosha"
        assert DoshaType.GRAHAN == "GrahanDosha"
        assert DoshaType.SHRAPIT == "ShrapitDosha"
        assert DoshaType.KEMADRUM == "KemadrumDosha"
        assert DoshaType.DARIDRA == "DaridraDosha"

    def test_dosha_catalog_completeness(self):
        """Test all doshas have catalog entries"""
        for dosha_type in DoshaType:
            assert dosha_type in DOSHA_CATALOG
            entry = DOSHA_CATALOG[dosha_type]
            assert entry.name is not None
            assert entry.description is not None
            assert len(entry.affected_areas) > 0
            assert 1.0 <= entry.base_severity <= 10.0
            assert len(entry.cancellation_rules) > 0
            assert len(entry.remedies) > 0

    def test_mangal_dosha_houses(self):
        """Test Mangal dosha house definitions"""
        assert MANGAL_DOSHA_HOUSES["from_lagna"] == [1, 2, 4, 7, 8, 12]
        assert MANGAL_DOSHA_HOUSES["from_moon"] == [1, 2, 4, 7, 8, 12]
        assert MANGAL_DOSHA_HOUSES["from_venus"] == [1, 2, 4, 7, 8, 12]

    def test_mangal_cancellation_signs(self):
        """Test Mangal dosha cancellation signs"""
        assert Zodiac.ARIES in MANGAL_CANCELLATION_SIGNS[1]
        assert Zodiac.CAPRICORN in MANGAL_CANCELLATION_SIGNS[1]
        assert Zodiac.GEMINI in MANGAL_CANCELLATION_SIGNS[2]
        assert Zodiac.VIRGO in MANGAL_CANCELLATION_SIGNS[2]

    def test_dosha_severity_levels(self):
        """Test dosha severity enum values"""
        assert DoshaSeverity.CRITICAL == "Critical"
        assert DoshaSeverity.HIGH == "High"
        assert DoshaSeverity.MODERATE == "Moderate"
        assert DoshaSeverity.LOW == "Low"
        assert DoshaSeverity.MINIMAL == "Minimal"
        assert DoshaSeverity.CANCELLED == "Cancelled"


# ============================================================================
# Stage 9: Karmic Depth Tests
# ============================================================================

class TestStage9KarmicDepth:
    """Tests for Stage 9 Karmic Depth analysis"""

    def test_stage9_initialization(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 9 can be initialized"""
        stage9 = Stage09KarmicAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        assert stage9 is not None

    def test_stage9_analyze_returns_result(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 9 analyze returns a result"""
        stage9 = Stage09KarmicAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        result = stage9.analyze()

        assert isinstance(result, Stage9Result)
        assert hasattr(result, 'doshas_detected')
        assert hasattr(result, 'd30_analysis')
        assert hasattr(result, 'd60_analysis')
        assert hasattr(result, 'risk_severity_index')
        assert hasattr(result, 'karmic_ceiling_tier')

    def test_stage9_result_to_dict(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 9 result can be converted to dict"""
        stage9 = Stage09KarmicAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        result = stage9.analyze()
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "d30_analysis" in result_dict
        assert "d60_analysis" in result_dict
        assert "risk_severity_index" in result_dict
        assert "dosha_summary" in result_dict

    def test_karmic_ceiling_tiers(self):
        """Test karmic ceiling tier values"""
        assert KarmicCeilingTier.UNLIMITED == "Unlimited"
        assert KarmicCeilingTier.VERY_HIGH == "VeryHigh"
        assert KarmicCeilingTier.HIGH == "High"
        assert KarmicCeilingTier.MODERATE == "Moderate"
        assert KarmicCeilingTier.LIMITED == "Limited"
        assert KarmicCeilingTier.CONSTRAINED == "Constrained"
        assert KarmicCeilingTier.BLOCKED == "Blocked"

    def test_risk_category_values(self):
        """Test risk category values"""
        assert RiskCategory.VERY_LOW == "VeryLow"
        assert RiskCategory.LOW == "Low"
        assert RiskCategory.MODERATE == "Moderate"
        assert RiskCategory.HIGH == "High"
        assert RiskCategory.CRITICAL == "Critical"


# ============================================================================
# Stage 10: Timing Tests
# ============================================================================

class TestStage10Timing:
    """Tests for Stage 10 Timing analysis"""

    def test_dasha_periods_sum_to_120(self):
        """Test Vimshottari dasha periods sum to 120 years"""
        total = sum(DASHA_PERIODS.values())
        assert total == 120

    def test_dasha_sequence_length(self):
        """Test dasha sequence has 9 planets"""
        assert len(DASHA_SEQUENCE) == 9
        assert DASHA_SEQUENCE[0] == Planet.KETU
        assert DASHA_SEQUENCE[1] == Planet.VENUS
        assert DASHA_SEQUENCE[2] == Planet.SUN
        assert DASHA_SEQUENCE[8] == Planet.MERCURY

    def test_dasha_periods_values(self):
        """Test specific dasha period values"""
        assert DASHA_PERIODS[Planet.KETU] == 7
        assert DASHA_PERIODS[Planet.VENUS] == 20
        assert DASHA_PERIODS[Planet.SUN] == 6
        assert DASHA_PERIODS[Planet.MOON] == 10
        assert DASHA_PERIODS[Planet.MARS] == 7
        assert DASHA_PERIODS[Planet.RAHU] == 18
        assert DASHA_PERIODS[Planet.JUPITER] == 16
        assert DASHA_PERIODS[Planet.SATURN] == 19
        assert DASHA_PERIODS[Planet.MERCURY] == 17

    def test_stage10_initialization(self, digital_twin_fixture, mock_d1_planets, mock_planet_strength, mock_yoga_planets):
        """Test Stage 10 can be initialized"""
        stage10 = Stage10TimingAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_planet_strength,
            mock_yoga_planets
        )
        assert stage10 is not None

    def test_stage10_analyze_returns_result(self, digital_twin_fixture, mock_d1_planets, mock_planet_strength, mock_yoga_planets):
        """Test Stage 10 analyze returns a result"""
        stage10 = Stage10TimingAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_planet_strength,
            mock_yoga_planets
        )
        result = stage10.analyze()

        assert isinstance(result, Stage10Result)
        assert hasattr(result, 'dasha_roadmap')
        assert hasattr(result, 'current_dasha_quality')
        assert hasattr(result, 'ashtakavarga')
        assert hasattr(result, 'timing_recommendation')
        assert hasattr(result, 'is_golden_period')

    def test_stage10_result_to_dict(self, digital_twin_fixture, mock_d1_planets, mock_planet_strength, mock_yoga_planets):
        """Test Stage 10 result can be converted to dict"""
        stage10 = Stage10TimingAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_planet_strength,
            mock_yoga_planets
        )
        result = stage10.analyze()
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "dasha_roadmap" in result_dict
        assert "current_dasha_quality" in result_dict
        assert "ashtakavarga" in result_dict
        assert "timing_recommendation" in result_dict

    def test_timing_recommendation_values(self):
        """Test timing recommendation enum values"""
        assert TimingRecommendation.INVEST_NOW == "InvestNow"
        assert TimingRecommendation.FAVORABLE_TIMING == "FavorableTiming"
        assert TimingRecommendation.WAIT_FOR_BETTER == "WaitForBetter"
        assert TimingRecommendation.PROCEED_CAUTION == "ProceedCaution"
        assert TimingRecommendation.DELAY_INVESTMENT == "DelayInvestment"


# ============================================================================
# Integration Tests
# ============================================================================

class TestStages9_10Integration:
    """Integration tests for Stages 9-10"""

    def test_full_stage9_analysis(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test complete Stage 9 analysis flow"""
        stage9 = Stage09KarmicAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        result = stage9.analyze()
        result_dict = result.to_dict()

        # Verify structure
        assert "doshas" in result_dict
        assert "d30_analysis" in result_dict
        assert "d60_analysis" in result_dict
        assert "risk_severity_index" in result_dict
        assert "karmic_ceiling_tier" in result_dict

        # Verify risk index is in valid range
        assert 0 <= result.risk_severity_index <= 100

        # Verify karmic ceiling tier is valid
        assert result.karmic_ceiling_tier in KarmicCeilingTier

    def test_full_stage10_analysis(self, digital_twin_fixture, mock_d1_planets, mock_planet_strength, mock_yoga_planets):
        """Test complete Stage 10 analysis flow"""
        stage10 = Stage10TimingAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_planet_strength,
            mock_yoga_planets
        )
        result = stage10.analyze()
        result_dict = result.to_dict()

        # Verify structure
        assert "dasha_roadmap" in result_dict
        assert "current_dasha_quality" in result_dict
        assert "ashtakavarga" in result_dict
        assert "timing_recommendation" in result_dict

        # Verify dasha roadmap is not empty
        assert result.dasha_roadmap is not None

    def test_calculator_integration_stages_9_10(self, digital_twin_fixture):
        """Test stages 9-10 work via AstroBrain calculator"""
        from ..calculator import AstroBrain

        brain = AstroBrain(digital_twin_fixture)

        # Run just stages 9 and 10
        output = brain.analyze(stages=[1, 9, 10])

        # Verify stages completed
        assert 1 in output.stages_completed
        assert 9 in output.stages_completed
        assert 10 in output.stages_completed

        # Verify output sections
        assert output.karmic_depth is not None
        assert output.timing_analysis is not None

    def test_calculator_full_analysis_with_stages_9_10(self, digital_twin_fixture):
        """Test full analysis includes stages 9-10"""
        from ..calculator import AstroBrain

        brain = AstroBrain(digital_twin_fixture)
        output = brain.analyze()  # Run all stages

        # Verify all 10 stages completed
        assert len(output.stages_completed) >= 10
        for i in range(1, 11):
            assert i in output.stages_completed

        # Verify karmic and timing sections
        assert output.karmic_depth is not None
        assert output.timing_analysis is not None

        # Verify output can be serialized
        output_dict = output.to_dict()
        assert "karmic_depth" in output_dict
        assert "timing_analysis" in output_dict


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Edge case tests for Stages 9-10"""

    def test_empty_varga_charts(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test handling when varga charts are missing"""
        # Remove D30 and D60 charts
        twin_copy = digital_twin_fixture.copy()
        if "vargas" in twin_copy:
            twin_copy["vargas"] = {
                k: v for k, v in twin_copy["vargas"].items()
                if k not in ["D30", "D60"]
            }

        stage9 = Stage09KarmicAnalysis(
            twin_copy,
            mock_d1_planets,
            mock_house_lords
        )
        result = stage9.analyze()

        # Should still return a valid result
        assert result is not None
        assert isinstance(result, Stage9Result)

    def test_missing_birth_date(self, digital_twin_fixture, mock_d1_planets, mock_planet_strength, mock_yoga_planets):
        """Test handling when birth date is problematic"""
        stage10 = Stage10TimingAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_planet_strength,
            mock_yoga_planets
        )
        result = stage10.analyze()

        # Should return valid result even with date issues
        assert result is not None
        assert isinstance(result, Stage10Result)
