"""
LLM Prompts for StarMeet Personality Reports

This module contains system and user prompts for generating
astrological personality reports using MiniMax M2.
"""

from .system_prompt import (
    PERSONALITY_REPORT_SYSTEM_PROMPT,
    get_system_prompt
)

__all__ = [
    "PERSONALITY_REPORT_SYSTEM_PROMPT",
    "get_system_prompt"
]
