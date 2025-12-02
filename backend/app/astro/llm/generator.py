"""
Personality Report Generator

Main orchestrator that combines:
- AstroBrain calculator output formatting
- MiniMax M2 API calls
- Output validation and error handling

This is the primary interface for generating personality reports.
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .client import MinimaxClient, MinimaxConfig, MinimaxAPIError
from .formatter import AstroDataFormatter, format_for_llm
from .validator import OutputValidator, validate_output
from .prompts import PERSONALITY_REPORT_SYSTEM_PROMPT
from .models import PersonalityReportOutput, ValidationResult, GenerationMetrics

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Complete result of report generation"""
    success: bool
    output: Optional[PersonalityReportOutput]
    validation: Optional[ValidationResult]
    metrics: GenerationMetrics
    raw_output: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        return {
            "success": self.success,
            "output": self.output.to_dict() if self.output else None,
            "validation": self.validation.to_dict() if self.validation else None,
            "metrics": self.metrics.to_dict(),
            "error": self.error
        }


class PersonalityReportGenerator:
    """
    Generates personality reports from AstroBrain calculator output.

    Usage:
        calculator_output = brain.analyze()

        generator = PersonalityReportGenerator()
        result = await generator.generate(calculator_output)

        if result.success:
            print(result.output.personality_report)
    """

    def __init__(
        self,
        config: Optional[MinimaxConfig] = None,
        strict_validation: bool = False,
        max_retries: int = 3
    ):
        """
        Initialize generator.

        Args:
            config: Optional MinimaxConfig. If None, loads from environment.
            strict_validation: If True, validation warnings become errors.
            max_retries: Maximum API call retries on failure.
        """
        self.config = config
        self.strict_validation = strict_validation
        self.max_retries = max_retries
        self.validator = OutputValidator(strict=strict_validation)

    async def generate(
        self,
        calculator_output: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> GenerationResult:
        """
        Generate personality report from calculator output.

        Args:
            calculator_output: Full output from AstroBrain.analyze()
            system_prompt: Override default system prompt
            temperature: Override default temperature (0.0-1.0)
            max_tokens: Override default max tokens

        Returns:
            GenerationResult with output, validation, and metrics
        """
        metrics = GenerationMetrics()
        start_time = time.time()

        try:
            # Format input data
            logger.info("Formatting calculator output for LLM...")
            user_prompt = format_for_llm(calculator_output)

            logger.info(f"User prompt length: {len(user_prompt)} chars")

            # Use provided or default system prompt
            sys_prompt = system_prompt or PERSONALITY_REPORT_SYSTEM_PROMPT

            # Call API
            logger.info("Calling MiniMax API...")
            async with MinimaxClient(self.config) as client:
                raw_output = await client.generate_with_retry(
                    system_prompt=sys_prompt,
                    user_prompt=user_prompt,
                    max_retries=self.max_retries,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

            metrics.latency_ms = (time.time() - start_time) * 1000
            logger.info(f"API call completed in {metrics.latency_ms:.0f}ms")

            # Validate output
            logger.info("Validating LLM output...")
            output, validation = self.validator.validate(raw_output)

            if not validation.is_valid:
                logger.warning(f"Validation failed: {validation.errors}")
                return GenerationResult(
                    success=False,
                    output=None,
                    validation=validation,
                    metrics=metrics,
                    raw_output=raw_output,
                    error=f"Validation failed: {'; '.join(validation.errors)}"
                )

            if validation.warnings:
                logger.info(f"Validation warnings: {validation.warnings}")

            logger.info("Report generated successfully!")
            return GenerationResult(
                success=True,
                output=output,
                validation=validation,
                metrics=metrics,
                raw_output=raw_output
            )

        except MinimaxAPIError as e:
            metrics.latency_ms = (time.time() - start_time) * 1000
            logger.error(f"API error: {e}")
            return GenerationResult(
                success=False,
                output=None,
                validation=None,
                metrics=metrics,
                error=f"API error: {str(e)}"
            )

        except Exception as e:
            metrics.latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return GenerationResult(
                success=False,
                output=None,
                validation=None,
                metrics=metrics,
                error=f"Unexpected error: {str(e)}"
            )

    async def regenerate_section(
        self,
        calculator_output: Dict[str, Any],
        section: str,
        previous_output: PersonalityReportOutput
    ) -> GenerationResult:
        """
        Regenerate a specific section of the report.

        Useful when validation fails for one section but others are acceptable.

        Args:
            calculator_output: Original calculator output
            section: Section name to regenerate (e.g., "personality_summary")
            previous_output: Previous generation output

        Returns:
            GenerationResult with updated output
        """
        section_prompts = {
            "personality_summary": "Перегенерируй только краткое описание (personality_summary) на основе данных. 100-600 символов.",
            "archetype_name": "Предложи другой архетип (archetype_name) на основе накшатры.",
            "archetype_description": "Перепиши описание архетипа (archetype_description). 300-800 символов.",
            "soul_purpose_description": "Перепиши описание предназначения души (soul_purpose_description). 500-1500 символов.",
            "current_period_advice": "Перепиши рекомендации на текущий период (current_period_advice). 300-1000 символов.",
        }

        if section not in section_prompts:
            return GenerationResult(
                success=False,
                output=None,
                validation=None,
                metrics=GenerationMetrics(),
                error=f"Cannot regenerate section: {section}"
            )

        # Create focused prompt
        user_prompt = format_for_llm(calculator_output)
        user_prompt += f"\n\n## ЗАДАЧА:\n{section_prompts[section]}\n\nВыдай только JSON с полем {section}."

        metrics = GenerationMetrics()
        start_time = time.time()

        try:
            async with MinimaxClient(self.config) as client:
                raw_output = await client.generate(
                    system_prompt=PERSONALITY_REPORT_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    max_tokens=2000  # Smaller for single section
                )

            metrics.latency_ms = (time.time() - start_time) * 1000

            # Parse just the section
            import json
            data = json.loads(raw_output)

            if section in data:
                # Update previous output
                updated = PersonalityReportOutput(
                    personality_report=previous_output.personality_report,
                    personality_summary=data.get("personality_summary", previous_output.personality_summary),
                    archetype_name=data.get("archetype_name", previous_output.archetype_name),
                    archetype_description=data.get("archetype_description", previous_output.archetype_description),
                    soul_purpose_description=data.get("soul_purpose_description", previous_output.soul_purpose_description),
                    life_mission_statement=data.get("life_mission_statement", previous_output.life_mission_statement),
                    public_image_description=data.get("public_image_description", previous_output.public_image_description),
                    current_period_advice=data.get("current_period_advice", previous_output.current_period_advice),
                    top_talents=previous_output.top_talents,
                    growth_areas=previous_output.growth_areas,
                )

                return GenerationResult(
                    success=True,
                    output=updated,
                    validation=ValidationResult(is_valid=True, errors=[], warnings=[], char_counts={}),
                    metrics=metrics,
                    raw_output=raw_output
                )

            return GenerationResult(
                success=False,
                output=None,
                validation=None,
                metrics=metrics,
                error=f"Section {section} not in regenerated output"
            )

        except Exception as e:
            metrics.latency_ms = (time.time() - start_time) * 1000
            return GenerationResult(
                success=False,
                output=None,
                validation=None,
                metrics=metrics,
                error=str(e)
            )


# ============================================================================
# Synchronous Wrappers
# ============================================================================

def generate_personality_report_sync(
    calculator_output: Dict[str, Any],
    **kwargs
) -> GenerationResult:
    """
    Synchronous wrapper for generate().

    Args:
        calculator_output: Full output from AstroBrain.analyze()
        **kwargs: Additional args passed to generate()

    Returns:
        GenerationResult
    """
    import asyncio

    async def _run():
        generator = PersonalityReportGenerator()
        return await generator.generate(calculator_output, **kwargs)

    return asyncio.run(_run())


# ============================================================================
# Convenience Functions
# ============================================================================

async def generate_report(
    calculator_output: Dict[str, Any],
    **kwargs
) -> GenerationResult:
    """
    Generate personality report (async).

    Convenience function that creates a generator and runs generation.

    Args:
        calculator_output: Full output from AstroBrain.analyze()
        **kwargs: Additional args passed to PersonalityReportGenerator

    Returns:
        GenerationResult
    """
    generator = PersonalityReportGenerator(**kwargs)
    return await generator.generate(calculator_output)
