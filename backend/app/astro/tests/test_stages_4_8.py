"""
Tests for Stages 4-8 (Varga Bundle)

Tests the following stages:
- Stage 4: Wealth & Assets (D2, D4)
- Stage 5: Skills & Initiative (D3)
- Stage 6: Career & Status (D10)
- Stage 7: Creativity & Legacy (D5, D7)
- Stage 8: Profit & Expansion (D11, D12)
"""

import pytest
import json
from pathlib import Path

from ..stages.varga_utils import (
    parse_varga_chart, VargaType, VargaPlanetData, VargaChartData,
    get_sign_lord, is_benefic, is_malefic, get_dignity_in_sign,
    is_kendra, is_trikona, is_dusthana, get_element, get_modality
)
from ..stages.stage_04_wealth import Stage04WealthAnalysis, WealthType, AssetType
from ..stages.stage_05_skills import Stage05SkillsAnalysis, SkillType, InitiativeStyle
from ..stages.stage_06_career import Stage06CareerAnalysis, CareerArchetype, WorkStyle
from ..stages.stage_07_creativity import Stage07CreativityAnalysis, CreativeType, LegacyType
from ..stages.stage_08_profit import Stage08ProfitAnalysis, GainType, KarmicPattern
from ..formulas.indices import (
    calculate_wealth_index, calculate_career_composite_index,
    calculate_composite_indices, get_life_area_interpretations
)
from ..models.types import Planet, Zodiac, Dignity


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def digital_twin_fixture():
    """Load the test digital twin fixture"""
    fixture_path = Path(__file__).parent / "fixtures" / "digital_twin_fixture.json"
    with open(fixture_path, 'r') as f:
        data = json.load(f)
        # Extract digital_twin if wrapped in response
        return data.get("digital_twin", data)


@pytest.fixture
def mock_d1_planets():
    """Mock D1 planets for testing"""
    return []


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
# Varga Utils Tests
# ============================================================================

class TestVargaUtils:
    """Tests for varga utility functions"""

    def test_get_sign_lord(self):
        """Test sign lordship mapping"""
        assert get_sign_lord(Zodiac.ARIES) == Planet.MARS
        assert get_sign_lord(Zodiac.TAURUS) == Planet.VENUS
        assert get_sign_lord(Zodiac.GEMINI) == Planet.MERCURY
        assert get_sign_lord(Zodiac.CANCER) == Planet.MOON
        assert get_sign_lord(Zodiac.LEO) == Planet.SUN
        assert get_sign_lord(Zodiac.VIRGO) == Planet.MERCURY
        assert get_sign_lord(Zodiac.SAGITTARIUS) == Planet.JUPITER
        assert get_sign_lord(Zodiac.CAPRICORN) == Planet.SATURN

    def test_is_benefic(self):
        """Test benefic planet identification"""
        assert is_benefic(Planet.JUPITER) == True
        assert is_benefic(Planet.VENUS) == True
        assert is_benefic(Planet.MERCURY) == True
        assert is_benefic(Planet.MOON) == True
        assert is_benefic(Planet.SATURN) == False
        assert is_benefic(Planet.MARS) == False

    def test_is_malefic(self):
        """Test malefic planet identification"""
        assert is_malefic(Planet.SATURN) == True
        assert is_malefic(Planet.MARS) == True
        assert is_malefic(Planet.RAHU) == True
        assert is_malefic(Planet.KETU) == True
        assert is_malefic(Planet.JUPITER) == False
        assert is_malefic(Planet.VENUS) == False

    def test_get_dignity_in_sign(self):
        """Test dignity calculation"""
        # Exaltation
        assert get_dignity_in_sign(Planet.SUN, Zodiac.ARIES) == Dignity.EXALTED
        assert get_dignity_in_sign(Planet.MOON, Zodiac.TAURUS) == Dignity.EXALTED
        assert get_dignity_in_sign(Planet.JUPITER, Zodiac.CANCER) == Dignity.EXALTED

        # Debilitation
        assert get_dignity_in_sign(Planet.SUN, Zodiac.LIBRA) == Dignity.DEBILITATED
        assert get_dignity_in_sign(Planet.MOON, Zodiac.SCORPIO) == Dignity.DEBILITATED
        assert get_dignity_in_sign(Planet.MARS, Zodiac.CANCER) == Dignity.DEBILITATED

        # Own sign
        assert get_dignity_in_sign(Planet.SUN, Zodiac.LEO) == Dignity.OWN_SIGN
        assert get_dignity_in_sign(Planet.MOON, Zodiac.CANCER) == Dignity.OWN_SIGN
        assert get_dignity_in_sign(Planet.MARS, Zodiac.ARIES) == Dignity.OWN_SIGN

    def test_house_classification(self):
        """Test house classification functions"""
        # Kendras
        assert is_kendra(1) == True
        assert is_kendra(4) == True
        assert is_kendra(7) == True
        assert is_kendra(10) == True
        assert is_kendra(5) == False

        # Trikonas
        assert is_trikona(1) == True
        assert is_trikona(5) == True
        assert is_trikona(9) == True
        assert is_trikona(4) == False

        # Dusthanas
        assert is_dusthana(6) == True
        assert is_dusthana(8) == True
        assert is_dusthana(12) == True
        assert is_dusthana(1) == False

    def test_get_element(self):
        """Test element identification"""
        assert get_element(Zodiac.ARIES) == "fire"
        assert get_element(Zodiac.LEO) == "fire"
        assert get_element(Zodiac.TAURUS) == "earth"
        assert get_element(Zodiac.GEMINI) == "air"
        assert get_element(Zodiac.CANCER) == "water"

    def test_get_modality(self):
        """Test modality identification"""
        assert get_modality(Zodiac.ARIES) == "cardinal"
        assert get_modality(Zodiac.CANCER) == "cardinal"
        assert get_modality(Zodiac.TAURUS) == "fixed"
        assert get_modality(Zodiac.LEO) == "fixed"
        assert get_modality(Zodiac.GEMINI) == "mutable"
        assert get_modality(Zodiac.VIRGO) == "mutable"


# ============================================================================
# Stage 4 Tests - Wealth & Assets
# ============================================================================

class TestStage04Wealth:
    """Tests for Stage 4 Wealth Analysis"""

    def test_stage4_initialization(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 4 initialization"""
        stage4 = Stage04WealthAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        assert stage4 is not None
        assert stage4.digital_twin == digital_twin_fixture

    def test_stage4_analysis(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 4 complete analysis"""
        stage4 = Stage04WealthAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        result = stage4.analyze()

        # Check result structure
        assert result.hora is not None
        assert result.chaturthamsha is not None
        assert 0 <= result.wealth_accumulation_index <= 100
        assert 0 <= result.fixed_assets_index <= 100
        assert 0 <= result.financial_stability_index <= 100
        assert len(result.primary_wealth_types) >= 1

    def test_stage4_to_dict(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 4 result serialization"""
        stage4 = Stage04WealthAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        result = stage4.analyze()
        result_dict = result.to_dict()

        assert "hora" in result_dict
        assert "chaturthamsha" in result_dict
        assert "indices" in result_dict
        assert "wealth_types" in result_dict

    def test_wealth_type_enum(self):
        """Test WealthType enum values"""
        assert WealthType.EARNED.value == "earned"
        assert WealthType.INHERITED.value == "inherited"
        assert WealthType.SPECULATIVE.value == "speculative"

    def test_asset_type_enum(self):
        """Test AssetType enum values"""
        assert AssetType.REAL_ESTATE.value == "real_estate"
        assert AssetType.VEHICLES.value == "vehicles"
        assert AssetType.LAND.value == "land"


# ============================================================================
# Stage 5 Tests - Skills & Initiative
# ============================================================================

class TestStage05Skills:
    """Tests for Stage 5 Skills Analysis"""

    def test_stage5_initialization(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 5 initialization"""
        stage5 = Stage05SkillsAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        assert stage5 is not None

    def test_stage5_analysis(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 5 complete analysis"""
        stage5 = Stage05SkillsAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        result = stage5.analyze()

        assert result.drekkana is not None
        assert 0 <= result.initiative_index <= 100
        assert 0 <= result.communication_index <= 100
        assert 0 <= result.skill_diversity_index <= 100
        assert len(result.primary_skills) >= 1
        assert result.initiative_style is not None
        assert result.risk_tolerance in ["high", "moderate", "low"]

    def test_skill_type_enum(self):
        """Test SkillType enum values"""
        assert SkillType.COMMUNICATION.value == "communication"
        assert SkillType.TECHNICAL.value == "technical"
        assert SkillType.ARTISTIC.value == "artistic"

    def test_initiative_style_enum(self):
        """Test InitiativeStyle enum values"""
        assert InitiativeStyle.BOLD.value == "bold"
        assert InitiativeStyle.STRATEGIC.value == "strategic"
        assert InitiativeStyle.COLLABORATIVE.value == "collaborative"


# ============================================================================
# Stage 6 Tests - Career & Status
# ============================================================================

class TestStage06Career:
    """Tests for Stage 6 Career Analysis"""

    def test_stage6_initialization(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 6 initialization"""
        stage6 = Stage06CareerAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        assert stage6 is not None

    def test_stage6_analysis(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 6 complete analysis"""
        stage6 = Stage06CareerAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        result = stage6.analyze()

        assert result.dashamsha is not None
        assert 0 <= result.career_strength_index <= 100
        assert 0 <= result.professional_success_index <= 100
        assert 0 <= result.public_recognition_index <= 100
        assert 0 <= result.authority_index <= 100
        assert len(result.primary_archetypes) >= 1
        assert result.work_style is not None
        assert len(result.career_sectors) >= 1

    def test_career_archetype_enum(self):
        """Test CareerArchetype enum values"""
        assert CareerArchetype.LEADER.value == "leader"
        assert CareerArchetype.ADVISOR.value == "advisor"
        assert CareerArchetype.ARTIST.value == "artist"
        assert CareerArchetype.BUILDER.value == "builder"

    def test_work_style_enum(self):
        """Test WorkStyle enum values"""
        assert WorkStyle.INDEPENDENT.value == "independent"
        assert WorkStyle.COLLABORATIVE.value == "collaborative"
        assert WorkStyle.STRUCTURED.value == "structured"


# ============================================================================
# Stage 7 Tests - Creativity & Legacy
# ============================================================================

class TestStage07Creativity:
    """Tests for Stage 7 Creativity Analysis"""

    def test_stage7_initialization(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 7 initialization"""
        stage7 = Stage07CreativityAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        assert stage7 is not None

    def test_stage7_analysis(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 7 complete analysis"""
        stage7 = Stage07CreativityAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        result = stage7.analyze()

        assert result.panchamsha is not None
        assert result.saptamsha is not None
        assert 0 <= result.creativity_index <= 100
        assert 0 <= result.intellectual_index <= 100
        assert 0 <= result.progeny_index <= 100
        assert 0 <= result.spiritual_creativity_index <= 100
        assert len(result.primary_creative_types) >= 1
        assert len(result.legacy_types) >= 1

    def test_creative_type_enum(self):
        """Test CreativeType enum values"""
        assert CreativeType.ARTISTIC.value == "artistic"
        assert CreativeType.INTELLECTUAL.value == "intellectual"
        assert CreativeType.SPIRITUAL.value == "spiritual"

    def test_legacy_type_enum(self):
        """Test LegacyType enum values"""
        assert LegacyType.CHILDREN.value == "children"
        assert LegacyType.CREATIVE_WORKS.value == "creative_works"
        assert LegacyType.TEACHINGS.value == "teachings"


# ============================================================================
# Stage 8 Tests - Profit & Expansion
# ============================================================================

class TestStage08Profit:
    """Tests for Stage 8 Profit Analysis"""

    def test_stage8_initialization(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 8 initialization"""
        stage8 = Stage08ProfitAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        assert stage8 is not None

    def test_stage8_analysis(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test Stage 8 complete analysis"""
        stage8 = Stage08ProfitAnalysis(
            digital_twin_fixture,
            mock_d1_planets,
            mock_house_lords
        )
        result = stage8.analyze()

        assert result.rudramsha is not None
        assert result.dwadasamsha is not None
        assert 0 <= result.gains_index <= 100
        assert 0 <= result.network_index <= 100
        assert 0 <= result.desire_fulfillment_index <= 100
        assert 0 <= result.karmic_balance_index <= 100
        assert len(result.primary_gain_types) >= 1
        assert len(result.karmic_patterns) >= 1

    def test_gain_type_enum(self):
        """Test GainType enum values"""
        assert GainType.FINANCIAL.value == "financial"
        assert GainType.SOCIAL.value == "social"
        assert GainType.KNOWLEDGE.value == "knowledge"

    def test_karmic_pattern_enum(self):
        """Test KarmicPattern enum values"""
        assert KarmicPattern.LEADERSHIP.value == "leadership"
        assert KarmicPattern.SERVICE.value == "service"
        assert KarmicPattern.TEACHING.value == "teaching"


# ============================================================================
# Indices Formulas Tests
# ============================================================================

class TestIndicesFormulas:
    """Tests for composite index calculations"""

    def test_calculate_wealth_index(self):
        """Test wealth index formula"""
        # Normal case
        result = calculate_wealth_index(70.0, 60.0, 50.0)
        assert 0 <= result <= 100

        # All high values
        result = calculate_wealth_index(100.0, 100.0, 100.0)
        assert result == 100.0

        # All low values
        result = calculate_wealth_index(0.0, 0.0, 0.0)
        assert result == 0.0

    def test_calculate_career_composite_index(self):
        """Test career composite index formula"""
        result = calculate_career_composite_index(70.0, 65.0, 60.0, 55.0)
        assert 0 <= result <= 100

    def test_calculate_composite_indices(self):
        """Test composite indices calculation with mock data"""
        # Mock stage results
        stage4 = {"indices": {"wealth_accumulation": 65, "fixed_assets": 60, "financial_stability": 55}}
        stage5 = {"indices": {"initiative": 70, "communication": 65, "skill_diversity": 60}}
        stage6 = {"indices": {"career_strength": 75, "professional_success": 70, "authority": 65}}
        stage7 = {"indices": {"creativity": 60, "intellectual": 65, "progeny": 55, "spiritual_creativity": 50}}
        stage8 = {"indices": {"gains": 70, "network": 65, "desire_fulfillment": 60, "karmic_balance": 55}}

        indices = calculate_composite_indices(stage4, stage5, stage6, stage7, stage8)

        assert indices.wealth_index >= 0
        assert indices.career_index >= 0
        assert indices.creativity_index >= 0
        assert indices.gains_index >= 0
        assert indices.overall_prosperity_index >= 0
        assert indices.life_success_index >= 0
        assert indices.spiritual_evolution_index >= 0

    def test_get_life_area_interpretations(self):
        """Test life area interpretation generation"""
        stage4 = {"indices": {"wealth_accumulation": 80, "fixed_assets": 75, "financial_stability": 70}}
        stage5 = {"indices": {"initiative": 65, "communication": 60, "skill_diversity": 55}}
        stage6 = {"indices": {"career_strength": 85, "professional_success": 80, "authority": 75}}
        stage7 = {"indices": {"creativity": 70, "intellectual": 75, "progeny": 65, "spiritual_creativity": 60}}
        stage8 = {"indices": {"gains": 75, "network": 70, "desire_fulfillment": 65, "karmic_balance": 60}}

        indices = calculate_composite_indices(stage4, stage5, stage6, stage7, stage8)
        interpretations = get_life_area_interpretations(indices)

        assert "wealth" in interpretations
        assert "career" in interpretations
        assert "creativity" in interpretations
        assert interpretations["wealth"].score > 0
        assert len(interpretations["wealth"].interpretation) > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestStagesIntegration:
    """Integration tests for all stages working together"""

    def test_all_stages_run(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test that all stages 4-8 can run in sequence"""
        results = {}

        # Stage 4
        stage4 = Stage04WealthAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        results[4] = stage4.analyze()
        assert results[4] is not None

        # Stage 5
        stage5 = Stage05SkillsAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        results[5] = stage5.analyze()
        assert results[5] is not None

        # Stage 6
        stage6 = Stage06CareerAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        results[6] = stage6.analyze()
        assert results[6] is not None

        # Stage 7
        stage7 = Stage07CreativityAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        results[7] = stage7.analyze()
        assert results[7] is not None

        # Stage 8
        stage8 = Stage08ProfitAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        results[8] = stage8.analyze()
        assert results[8] is not None

    def test_results_serialization(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test that all stage results can be serialized to dict"""
        stage4 = Stage04WealthAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        stage5 = Stage05SkillsAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        stage6 = Stage06CareerAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        stage7 = Stage07CreativityAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        stage8 = Stage08ProfitAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)

        # All should serialize without error
        dict4 = stage4.analyze().to_dict()
        dict5 = stage5.analyze().to_dict()
        dict6 = stage6.analyze().to_dict()
        dict7 = stage7.analyze().to_dict()
        dict8 = stage8.analyze().to_dict()

        # Should be JSON serializable
        json.dumps(dict4)
        json.dumps(dict5)
        json.dumps(dict6)
        json.dumps(dict7)
        json.dumps(dict8)

    def test_composite_indices_from_stages(self, digital_twin_fixture, mock_d1_planets, mock_house_lords):
        """Test composite indices calculation from actual stage results"""
        stage4 = Stage04WealthAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        stage5 = Stage05SkillsAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        stage6 = Stage06CareerAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        stage7 = Stage07CreativityAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)
        stage8 = Stage08ProfitAnalysis(digital_twin_fixture, mock_d1_planets, mock_house_lords)

        r4 = stage4.analyze().to_dict()
        r5 = stage5.analyze().to_dict()
        r6 = stage6.analyze().to_dict()
        r7 = stage7.analyze().to_dict()
        r8 = stage8.analyze().to_dict()

        indices = calculate_composite_indices(r4, r5, r6, r7, r8, d9_synergy=60.0)

        assert indices is not None
        assert 0 <= indices.overall_prosperity_index <= 100
        assert 0 <= indices.life_success_index <= 100
        assert 0 <= indices.spiritual_evolution_index <= 100
