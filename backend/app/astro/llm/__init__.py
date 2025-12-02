"""
LLM Integration Module for StarMeet

This module provides MiniMax M2 API integration for generating
personality reports based on pre-calculated astrological data.

Main Components:
- client: MinimaxClient for API communication
- formatter: AstroDataFormatter for data preparation
- generator: PersonalityReportGenerator for orchestration
- validator: OutputValidator for response validation
- models: Data models for outputs and metrics

Usage:
    from app.astro.llm import PersonalityReportGenerator, generate_report

    # Async usage
    result = await generate_report(calculator_output)
    if result.success:
        print(result.output.personality_report)

    # Or with generator instance
    generator = PersonalityReportGenerator()
    result = await generator.generate(calculator_output)
"""

# Client
from .client import (
    MinimaxClient,
    MinimaxConfig,
    MinimaxAPIError,
    generate_sync,
    generate_with_retry_sync,
)

# Formatter
from .formatter import (
    AstroDataFormatter,
    FormattedAstroData,
    format_for_llm,
)

# Generator
from .generator import (
    PersonalityReportGenerator,
    GenerationResult,
    generate_report,
    generate_personality_report_sync,
)

# Validator
from .validator import (
    OutputValidator,
    validate_output,
    FIELD_LIMITS,
    REQUIRED_FIELDS,
)

# Models
from .models import (
    PersonalityReportOutput,
    ValidationResult,
    GenerationMetrics,
)

# Prompts
from .prompts import (
    PERSONALITY_REPORT_SYSTEM_PROMPT,
    get_system_prompt,
)

__all__ = [
    # Client
    "MinimaxClient",
    "MinimaxConfig",
    "MinimaxAPIError",
    "generate_sync",
    "generate_with_retry_sync",
    # Formatter
    "AstroDataFormatter",
    "FormattedAstroData",
    "format_for_llm",
    # Generator
    "PersonalityReportGenerator",
    "GenerationResult",
    "generate_report",
    "generate_personality_report_sync",
    # Validator
    "OutputValidator",
    "validate_output",
    "FIELD_LIMITS",
    "REQUIRED_FIELDS",
    # Models
    "PersonalityReportOutput",
    "ValidationResult",
    "GenerationMetrics",
    # Prompts
    "PERSONALITY_REPORT_SYSTEM_PROMPT",
    "get_system_prompt",
]
