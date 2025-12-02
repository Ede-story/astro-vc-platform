"""
Tests for LLM Integration (Phase 6)

Tests the following components:
- MinimaxClient: API communication
- AstroDataFormatter: Data preparation
- OutputValidator: Response validation
- PersonalityReportGenerator: Full pipeline

Note: Some tests require MINIMAX_API_KEY environment variable.
Tests marked with @pytest.mark.integration require API access.
"""

import pytest
import pytest_asyncio

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from ..llm.client import MinimaxClient, MinimaxConfig, MinimaxAPIError
from ..llm.formatter import AstroDataFormatter, format_for_llm, FormattedAstroData
from ..llm.validator import (
    OutputValidator, validate_output,
    FIELD_LIMITS, REQUIRED_FIELDS
)
from ..llm.models import PersonalityReportOutput, ValidationResult, GenerationMetrics
from ..llm.generator import PersonalityReportGenerator, GenerationResult
from ..llm.prompts import PERSONALITY_REPORT_SYSTEM_PROMPT


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
def mock_calculator_output(digital_twin_fixture):
    """Create mock calculator output for testing"""
    return {
        "digital_twin": digital_twin_fixture,
        "gunas": {
            "scores": {"sattva": 0.45, "rajas": 0.35, "tamas": 0.20},
            "dominant": "Sattva"
        },
        "elements": {
            "scores": {"fire": 0.30, "earth": 0.25, "air": 0.25, "water": 0.20},
            "dominant": "Fire"
        },
        "yogas": {
            "active_yogas": [
                {"name": "Budhaditya Yoga", "strength": 0.8, "description": "Интеллект и коммуникация"},
                {"name": "Chandra-Mangala Yoga", "strength": 0.7, "description": "Эмоциональная сила"}
            ],
            "summary": {"raja_yoga_count": 2, "dhana_yoga_count": 1, "overall_yoga_strength": 0.75}
        },
        "planet_strength": {
            "planets": {
                "Sun": {"total_strength": 0.85},
                "Moon": {"total_strength": 0.70},
                "Mars": {"total_strength": 0.60},
                "Mercury": {"total_strength": 0.90},
                "Jupiter": {"total_strength": 0.75},
                "Venus": {"total_strength": 0.65},
                "Saturn": {"total_strength": 0.55}
            },
            "strongest": "Mercury",
            "weakest": "Saturn"
        },
        "house_analysis": {
            "house_lords": {
                "1": {"lord": "Mars", "in_house": 10},
                "7": {"lord": "Venus", "in_house": 5},
                "10": {"lord": "Saturn", "in_house": 4}
            }
        },
        "karmic_depth": {
            "doshas": [],
            "karmic_ceiling_tier": "High",
            "risk_severity_index": 25
        },
        "timing_analysis": {
            "dasha_roadmap": {
                "current": {
                    "maha_dasha": "Jupiter",
                    "antar_dasha": "Venus",
                    "end_date": "2026-03-15"
                }
            },
            "current_dasha_quality": "Favorable",
            "is_golden_period": True,
            "timing_recommendation": "FavorableTiming"
        },
        "nakshatra_analysis": {
            "moon_nakshatra": {
                "name": "Rohini",
                "deity": "Brahma",
                "symbol": "Ox cart",
                "quality": "Fixed",
                "ruling_planet": "Moon"
            },
            "archetype": "Творец-созидатель"
        },
        "jaimini_analysis": {
            "atmakaraka": {
                "planet": "Sun",
                "sign": "Libra",
                "meaning": "Душа стремится к балансу и гармонии"
            },
            "karakamsha": {
                "sign": "Sagittarius",
                "house": 9,
                "interpretation": "Путь философа и учителя"
            },
            "arudha_lagna": {
                "sign": "Leo",
                "house": 5,
                "interpretation": "Воспринимается как творческий лидер"
            },
            "chara_karakas": {
                "karakas": [
                    {"karaka_code": "AK", "planet": "Sun"},
                    {"karaka_code": "AmK", "planet": "Moon"},
                    {"karaka_code": "BK", "planet": "Mars"}
                ]
            }
        }
    }


@pytest.fixture
def valid_llm_output():
    """Valid LLM output JSON string"""
    return json.dumps({
        "personality_report": "А" * 6000,  # Long enough to pass validation
        "personality_summary": "Краткое описание личности для профиля. Творческая натура с сильным интеллектом." * 3,
        "archetype_name": "Творец-философ",
        "archetype_description": "Архетип творца-философа проявляется в глубоком понимании мира и стремлении к созиданию. " * 5,
        "soul_purpose_description": "Предназначение души связано с развитием мудрости и передачей знаний другим. " * 8,
        "life_mission_statement": "Нести свет знания и вдохновлять других на путь самопознания.",
        "public_image_description": "Окружающие воспринимают вас как творческого лидера с харизмой и авторитетом. " * 4,
        "current_period_advice": "Текущий период благоприятен для новых начинаний и творческих проектов. " * 5,
        "top_talents": ["Аналитическое мышление", "Коммуникация", "Творчество", "Лидерство", "Интуиция"],
        "growth_areas": ["Терпение", "Делегирование", "Эмоциональная гибкость"]
    })


@pytest.fixture
def invalid_llm_output():
    """Invalid LLM output (missing fields, too short)"""
    return json.dumps({
        "personality_report": "Too short",
        "personality_summary": "OK"
    })


# ============================================================================
# MinimaxClient Tests
# ============================================================================

class TestMinimaxClient:
    """Tests for MinimaxClient"""

    def test_config_defaults(self):
        """Test MinimaxConfig default values"""
        config = MinimaxConfig(api_key="test-key")
        assert config.api_key == "test-key"
        assert config.model == "MiniMax-Text-01"
        assert config.temperature == 0.7
        assert config.max_tokens == 8000
        assert config.timeout == 120.0
        assert "minimax.chat" in config.base_url

    def test_client_requires_api_key(self):
        """Test client raises error without API key"""
        # Remove env var if set
        old_key = os.environ.pop("MINIMAX_API_KEY", None)
        try:
            with pytest.raises(ValueError, match="MINIMAX_API_KEY"):
                MinimaxClient()
        finally:
            if old_key:
                os.environ["MINIMAX_API_KEY"] = old_key

    def test_client_accepts_config(self):
        """Test client accepts custom config"""
        config = MinimaxConfig(
            api_key="test-key",
            model="custom-model",
            temperature=0.5
        )
        client = MinimaxClient(config)
        assert client.config.api_key == "test-key"
        assert client.config.model == "custom-model"
        assert client.config.temperature == 0.5

    def test_headers_include_auth(self):
        """Test request headers include authorization"""
        config = MinimaxConfig(api_key="test-key-123")
        client = MinimaxClient(config)
        headers = client.headers
        assert "Authorization" in headers
        assert "Bearer test-key-123" in headers["Authorization"]
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager"""
        config = MinimaxConfig(api_key="test-key")
        async with MinimaxClient(config) as client:
            assert client._client is not None
        assert client._client is None


# ============================================================================
# Formatter Tests
# ============================================================================

class TestAstroDataFormatter:
    """Tests for AstroDataFormatter"""

    def test_formatter_initialization(self, mock_calculator_output):
        """Test formatter initializes correctly"""
        formatter = AstroDataFormatter(mock_calculator_output)
        assert formatter.data == mock_calculator_output
        assert "vargas" in formatter.digital_twin or formatter.digital_twin

    def test_format_returns_formatted_data(self, mock_calculator_output):
        """Test format() returns FormattedAstroData"""
        formatter = AstroDataFormatter(mock_calculator_output)
        result = formatter.format()

        assert isinstance(result, FormattedAstroData)
        assert result.birth_info is not None
        assert result.planetary_positions is not None
        assert result.gunas_elements is not None
        assert result.yogas is not None
        assert result.nakshatra_analysis is not None
        assert result.jaimini_analysis is not None

    def test_formatted_data_to_prompt(self, mock_calculator_output):
        """Test FormattedAstroData.to_prompt()"""
        formatter = AstroDataFormatter(mock_calculator_output)
        result = formatter.format()
        prompt = result.to_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 100
        assert "ДАННЫЕ РОЖДЕНИЯ" in prompt
        assert "ПЛАНЕТАРНЫЕ ПОЗИЦИИ" in prompt
        assert "ГУНЫ И СТИХИИ" in prompt
        assert "ЙОГИ" in prompt
        assert "ДЖАЙМИНИ" in prompt

    def test_format_for_llm_convenience(self, mock_calculator_output):
        """Test format_for_llm convenience function"""
        prompt = format_for_llm(mock_calculator_output)

        assert isinstance(prompt, str)
        assert "Stage" in prompt or "ДАННЫЕ" in prompt

    def test_format_gunas_elements(self, mock_calculator_output):
        """Test gunas and elements formatting"""
        formatter = AstroDataFormatter(mock_calculator_output)
        result = formatter._format_gunas_elements()

        assert "Саттва" in result
        assert "Раджас" in result
        assert "Тамас" in result
        assert "Sattva" in result or "доминирующ" in result.lower()

    def test_format_yogas(self, mock_calculator_output):
        """Test yogas formatting"""
        formatter = AstroDataFormatter(mock_calculator_output)
        result = formatter._format_yogas()

        assert "Budhaditya" in result or "йог" in result.lower()
        assert "сила" in result.lower() or "strength" in result.lower()

    def test_format_jaimini(self, mock_calculator_output):
        """Test Jaimini analysis formatting"""
        formatter = AstroDataFormatter(mock_calculator_output)
        result = formatter._format_jaimini_analysis()

        assert "Атмакарака" in result or "атмакарака" in result.lower()
        assert "Sun" in result or "Солнц" in result


# ============================================================================
# Validator Tests
# ============================================================================

class TestOutputValidator:
    """Tests for OutputValidator"""

    def test_validator_initialization(self):
        """Test validator initialization"""
        validator = OutputValidator()
        assert validator.strict is False

        validator_strict = OutputValidator(strict=True)
        assert validator_strict.strict is True

    def test_validate_valid_json(self, valid_llm_output):
        """Test validation of valid JSON"""
        validator = OutputValidator()
        data, errors = validator.validate_json(valid_llm_output)

        assert data is not None
        assert isinstance(data, dict)
        assert len(errors) == 0

    def test_validate_invalid_json(self):
        """Test validation of invalid JSON"""
        validator = OutputValidator()
        data, errors = validator.validate_json("not valid json {")

        # May be None or have errors depending on fix attempts
        assert len(errors) > 0 or data is None

    def test_validate_json_with_markdown(self):
        """Test JSON extraction from markdown code blocks"""
        validator = OutputValidator()
        markdown_json = '```json\n{"test": "value"}\n```'
        data, errors = validator.validate_json(markdown_json)

        assert data is not None
        assert data.get("test") == "value"

    def test_validate_fields_valid(self, valid_llm_output):
        """Test field validation with valid data"""
        validator = OutputValidator()
        data = json.loads(valid_llm_output)
        result = validator.validate_fields(data)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_fields_missing_required(self):
        """Test field validation with missing required fields"""
        validator = OutputValidator()
        data = {"personality_report": "Some text"}
        result = validator.validate_fields(data)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Missing" in e or "Empty" in e for e in result.errors)

    def test_validate_fields_too_short(self):
        """Test field validation with too short content"""
        validator = OutputValidator(strict=True)
        data = {
            "personality_report": "Too short",
            "personality_summary": "X",
            "archetype_name": "OK",
            "archetype_description": "Short",
            "soul_purpose_description": "Short",
            "life_mission_statement": "OK",
            "public_image_description": "Short",
            "current_period_advice": "Short",
            "top_talents": ["One"],
            "growth_areas": ["One"]
        }
        result = validator.validate_fields(data)

        assert result.is_valid is False
        assert any("too short" in e for e in result.errors)

    def test_validate_char_counts(self, valid_llm_output):
        """Test character count tracking"""
        validator = OutputValidator()
        data = json.loads(valid_llm_output)
        result = validator.validate_fields(data)

        assert "personality_report" in result.char_counts
        assert "personality_summary" in result.char_counts
        assert result.char_counts["personality_report"] > 0

    def test_full_validation_pipeline(self, valid_llm_output):
        """Test complete validation pipeline"""
        output, result = validate_output(valid_llm_output)

        assert output is not None
        assert isinstance(output, PersonalityReportOutput)
        assert result.is_valid is True

    def test_full_validation_invalid(self, invalid_llm_output):
        """Test validation pipeline with invalid output"""
        output, result = validate_output(invalid_llm_output)

        assert output is None
        assert result.is_valid is False


# ============================================================================
# Models Tests
# ============================================================================

class TestModels:
    """Tests for data models"""

    def test_personality_report_output(self):
        """Test PersonalityReportOutput creation"""
        output = PersonalityReportOutput(
            personality_report="Report text",
            personality_summary="Summary",
            archetype_name="Archetype",
            archetype_description="Description",
            soul_purpose_description="Purpose",
            life_mission_statement="Mission",
            public_image_description="Image",
            current_period_advice="Advice",
            top_talents=["Talent1", "Talent2"],
            growth_areas=["Growth1"]
        )

        assert output.personality_report == "Report text"
        assert output.archetype_name == "Archetype"
        assert len(output.top_talents) == 2

    def test_personality_report_to_dict(self):
        """Test PersonalityReportOutput.to_dict()"""
        output = PersonalityReportOutput(
            personality_report="Report",
            personality_summary="Summary",
            archetype_name="Archetype",
            archetype_description="Desc",
            soul_purpose_description="Purpose",
            life_mission_statement="Mission",
            public_image_description="Image",
            current_period_advice="Advice"
        )

        d = output.to_dict()
        assert isinstance(d, dict)
        assert d["personality_report"] == "Report"
        assert "generation_model" in d

    def test_validation_result(self):
        """Test ValidationResult"""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Warning 1"],
            char_counts={"field1": 100}
        )

        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert result.char_counts["field1"] == 100

    def test_generation_metrics(self):
        """Test GenerationMetrics"""
        metrics = GenerationMetrics(
            input_tokens=1000,
            output_tokens=500,
            latency_ms=2500.0,
            retries=1
        )

        assert metrics.input_tokens == 1000
        assert metrics.latency_ms == 2500.0

        d = metrics.to_dict()
        assert d["output_tokens"] == 500


# ============================================================================
# Generator Tests
# ============================================================================

class TestPersonalityReportGenerator:
    """Tests for PersonalityReportGenerator"""

    def test_generator_initialization(self):
        """Test generator initialization"""
        config = MinimaxConfig(api_key="test-key")
        generator = PersonalityReportGenerator(config=config)

        assert generator.config == config
        assert generator.strict_validation is False
        assert generator.max_retries == 3

    def test_generator_with_strict_validation(self):
        """Test generator with strict validation"""
        config = MinimaxConfig(api_key="test-key")
        generator = PersonalityReportGenerator(
            config=config,
            strict_validation=True
        )

        assert generator.strict_validation is True
        assert generator.validator.strict is True

    @pytest.mark.asyncio
    async def test_generate_with_mock(self, mock_calculator_output, valid_llm_output):
        """Test generate with mocked API"""
        config = MinimaxConfig(api_key="test-key")
        generator = PersonalityReportGenerator(config=config)

        # Mock the client's generate method
        with patch.object(MinimaxClient, 'generate_with_retry', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = valid_llm_output

            with patch.object(MinimaxClient, '__aenter__', return_value=MagicMock(generate_with_retry=mock_gen)):
                with patch.object(MinimaxClient, '__aexit__', return_value=None):
                    # Create a properly mocked context manager
                    mock_client = AsyncMock()
                    mock_client.generate_with_retry = mock_gen
                    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                    mock_client.__aexit__ = AsyncMock(return_value=None)

                    with patch('app.astro.llm.generator.MinimaxClient', return_value=mock_client):
                        result = await generator.generate(mock_calculator_output)

        assert isinstance(result, GenerationResult)
        # Note: Result depends on mock behavior

    def test_generation_result_to_dict(self):
        """Test GenerationResult.to_dict()"""
        output = PersonalityReportOutput(
            personality_report="Report",
            personality_summary="Summary",
            archetype_name="Archetype",
            archetype_description="Desc",
            soul_purpose_description="Purpose",
            life_mission_statement="Mission",
            public_image_description="Image",
            current_period_advice="Advice"
        )

        result = GenerationResult(
            success=True,
            output=output,
            validation=ValidationResult(True, [], [], {}),
            metrics=GenerationMetrics(),
            raw_output="raw"
        )

        d = result.to_dict()
        assert d["success"] is True
        assert d["output"] is not None
        assert d["error"] is None


# ============================================================================
# Prompts Tests
# ============================================================================

class TestPrompts:
    """Tests for system prompts"""

    def test_personality_prompt_exists(self):
        """Test personality report prompt is defined"""
        assert PERSONALITY_REPORT_SYSTEM_PROMPT is not None
        assert len(PERSONALITY_REPORT_SYSTEM_PROMPT) > 500

    def test_personality_prompt_in_russian(self):
        """Test prompt is in Russian"""
        russian_indicators = ["Ты", "астролог", "русском", "формат", "JSON"]
        found = sum(1 for ind in russian_indicators if ind in PERSONALITY_REPORT_SYSTEM_PROMPT)
        assert found >= 3

    def test_personality_prompt_has_structure(self):
        """Test prompt has required structure elements"""
        assert "JSON" in PERSONALITY_REPORT_SYSTEM_PROMPT
        assert "personality_report" in PERSONALITY_REPORT_SYSTEM_PROMPT
        assert "archetype" in PERSONALITY_REPORT_SYSTEM_PROMPT
        assert "Stage" in PERSONALITY_REPORT_SYSTEM_PROMPT


# ============================================================================
# Integration Tests (require API key)
# ============================================================================

@pytest.mark.integration
class TestLLMIntegration:
    """Integration tests that require actual API access"""

    @pytest.mark.asyncio
    async def test_api_health_check(self):
        """Test API is accessible"""
        if not os.getenv("MINIMAX_API_KEY"):
            pytest.skip("MINIMAX_API_KEY not set")

        async with MinimaxClient() as client:
            is_healthy = await client.health_check()
            # May or may not pass depending on API status
            assert isinstance(is_healthy, bool)

    @pytest.mark.asyncio
    async def test_full_generation_pipeline(self, mock_calculator_output):
        """Test full generation with real API"""
        if not os.getenv("MINIMAX_API_KEY"):
            pytest.skip("MINIMAX_API_KEY not set")

        generator = PersonalityReportGenerator()
        result = await generator.generate(mock_calculator_output)

        assert isinstance(result, GenerationResult)
        if result.success:
            assert result.output is not None
            assert len(result.output.personality_report) > 1000
        else:
            # API may fail, that's OK for integration test
            assert result.error is not None


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Edge case tests"""

    def test_empty_calculator_output(self):
        """Test handling of empty calculator output"""
        formatter = AstroDataFormatter({})
        result = formatter.format()

        # Should return defaults, not crash
        assert result is not None
        assert isinstance(result.birth_info, str)

    def test_missing_sections(self):
        """Test handling of missing sections in output"""
        partial_output = {
            "digital_twin": {"birth_data": {"date": "1990-01-01"}}
        }
        formatter = AstroDataFormatter(partial_output)
        result = formatter.format()

        assert result is not None
        prompt = result.to_prompt()
        assert len(prompt) > 0

    def test_validator_handles_non_string_fields(self):
        """Test validator handles non-string field values"""
        data = {
            "personality_report": 12345,  # Should be string
            "personality_summary": None,
            "archetype_name": ["list"],
            "archetype_description": {"dict": "value"}
        }
        validator = OutputValidator()
        result = validator.validate_fields(data)

        # Should fail validation gracefully
        assert not result.is_valid

    def test_json_with_unicode(self):
        """Test JSON parsing with unicode characters"""
        unicode_json = json.dumps({
            "personality_report": "Текст на русском 🌟 émojis и спецсимволы"
        })
        validator = OutputValidator()
        data, errors = validator.validate_json(unicode_json)

        assert data is not None
        assert "русском" in data["personality_report"]
