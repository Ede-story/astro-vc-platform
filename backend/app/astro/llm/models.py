"""
LLM Output Models for StarMeet Personality Reports

These dataclasses define the structure of LLM-generated content.
All astrological calculations are done in Python (Stages 1-12).
LLM only generates human-readable interpretations.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PersonalityReportOutput:
    """
    Complete LLM-generated output for a profile.

    All text fields are in Russian language.
    Character limits are enforced by the validator.
    """

    # Main report (5000-15000 chars)
    personality_report: str

    # Brief summary for cards/previews (100-600 chars)
    personality_summary: str

    # Archetype from Stage 11 Nakshatra analysis
    archetype_name: str
    archetype_description: str

    # Soul purpose from Stage 12 Jaimini (Atmakaraka + Karakamsha)
    soul_purpose_description: str
    life_mission_statement: str

    # Public image from Arudha Lagna
    public_image_description: str

    # Current period advice from Stage 10 Timing
    current_period_advice: str

    # Lists of talents and growth areas
    top_talents: List[str] = field(default_factory=list)
    growth_areas: List[str] = field(default_factory=list)

    # Metadata
    generation_model: str = "MiniMax-Text-01"
    generation_version: str = "1.0"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "personality_report": self.personality_report,
            "personality_summary": self.personality_summary,
            "archetype_name": self.archetype_name,
            "archetype_description": self.archetype_description,
            "soul_purpose_description": self.soul_purpose_description,
            "life_mission_statement": self.life_mission_statement,
            "public_image_description": self.public_image_description,
            "current_period_advice": self.current_period_advice,
            "top_talents": self.top_talents,
            "growth_areas": self.growth_areas,
            "generation_model": self.generation_model,
            "generation_version": self.generation_version
        }


@dataclass
class ValidationResult:
    """Result of output validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    char_counts: dict  # Field -> char count

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "char_counts": self.char_counts
        }


@dataclass
class GenerationMetrics:
    """Metrics for LLM generation (for monitoring)"""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    retries: int = 0
    model: str = "MiniMax-Text-01"

    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": self.latency_ms,
            "retries": self.retries,
            "model": self.model
        }
