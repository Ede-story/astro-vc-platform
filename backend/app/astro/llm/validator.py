"""
Output Validator for LLM-generated Personality Reports

Validates that LLM output conforms to expected structure and constraints.
Ensures character limits, required fields, and content quality.
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .models import PersonalityReportOutput, ValidationResult

logger = logging.getLogger(__name__)


# Character limits for each field
FIELD_LIMITS = {
    "personality_report": (5000, 15000),
    "personality_summary": (100, 600),
    "archetype_name": (5, 100),
    "archetype_description": (300, 800),
    "soul_purpose_description": (500, 1500),
    "life_mission_statement": (50, 200),
    "public_image_description": (300, 800),
    "current_period_advice": (300, 1000),
}

# Required fields that cannot be empty
REQUIRED_FIELDS = [
    "personality_report",
    "personality_summary",
    "archetype_name",
    "archetype_description",
    "soul_purpose_description",
    "life_mission_statement",
    "public_image_description",
    "current_period_advice",
]

# List field constraints
LIST_LIMITS = {
    "top_talents": (3, 7),  # min, max items
    "growth_areas": (2, 5),
}


class OutputValidator:
    """
    Validates LLM output for personality reports.

    Checks:
    - JSON structure validity
    - Required fields presence
    - Character limits compliance
    - List constraints
    - Content quality indicators
    """

    def __init__(self, strict: bool = False):
        """
        Initialize validator.

        Args:
            strict: If True, warnings become errors
        """
        self.strict = strict

    def validate_json(self, raw_output: str) -> Tuple[Optional[dict], List[str]]:
        """
        Parse and validate JSON structure.

        Args:
            raw_output: Raw LLM output string

        Returns:
            Tuple of (parsed dict or None, list of errors)
        """
        errors = []

        # Try to extract JSON from markdown code blocks if present
        cleaned = self._extract_json(raw_output)

        try:
            data = json.loads(cleaned)
            return data, []
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {str(e)}")

            # Try to fix common issues
            fixed = self._attempt_json_fix(cleaned)
            if fixed:
                try:
                    data = json.loads(fixed)
                    errors = [f"JSON was auto-corrected: {str(e)}"]
                    return data, errors
                except json.JSONDecodeError:
                    pass

            return None, errors

    def _extract_json(self, text: str) -> str:
        """Extract JSON from markdown code blocks or raw text"""
        # Remove markdown code block markers
        text = re.sub(r'^```json?\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)

        # Try to find JSON object
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return match.group(0)

        return text.strip()

    def _attempt_json_fix(self, text: str) -> Optional[str]:
        """Attempt to fix common JSON issues"""
        # Fix trailing commas
        text = re.sub(r',(\s*[}\]])', r'\1', text)

        # Fix unescaped newlines in strings
        text = re.sub(r'(?<!\\)\n(?=(?:[^"]*"[^"]*")*[^"]*$)', ' ', text)

        return text

    def validate_fields(self, data: dict) -> ValidationResult:
        """
        Validate all fields in parsed data.

        Args:
            data: Parsed JSON dictionary

        Returns:
            ValidationResult with errors, warnings, and char counts
        """
        errors = []
        warnings = []
        char_counts = {}

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif not data[field] or not str(data[field]).strip():
                errors.append(f"Empty required field: {field}")

        # Check character limits
        for field, (min_len, max_len) in FIELD_LIMITS.items():
            if field in data and data[field]:
                length = len(str(data[field]))
                char_counts[field] = length

                if length < min_len:
                    msg = f"{field}: too short ({length} < {min_len} chars)"
                    if self.strict:
                        errors.append(msg)
                    else:
                        warnings.append(msg)

                elif length > max_len:
                    msg = f"{field}: too long ({length} > {max_len} chars)"
                    if self.strict:
                        errors.append(msg)
                    else:
                        warnings.append(msg)

        # Check list fields
        for field, (min_items, max_items) in LIST_LIMITS.items():
            if field in data:
                items = data[field]
                if not isinstance(items, list):
                    errors.append(f"{field}: expected list, got {type(items).__name__}")
                else:
                    count = len(items)
                    char_counts[f"{field}_count"] = count

                    if count < min_items:
                        msg = f"{field}: too few items ({count} < {min_items})"
                        if self.strict:
                            errors.append(msg)
                        else:
                            warnings.append(msg)

                    elif count > max_items:
                        msg = f"{field}: too many items ({count} > {max_items})"
                        warnings.append(msg)  # Not an error, just trim

        # Content quality checks
        quality_warnings = self._check_content_quality(data)
        warnings.extend(quality_warnings)

        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            char_counts=char_counts
        )

    def _check_content_quality(self, data: dict) -> List[str]:
        """Check content quality indicators"""
        warnings = []

        # Check for placeholder text
        placeholders = ["TODO", "PLACEHOLDER", "[", "]", "Lorem ipsum", "XXX"]
        for field in REQUIRED_FIELDS:
            if field in data and data[field]:
                content = str(data[field])
                for placeholder in placeholders:
                    if placeholder in content:
                        warnings.append(f"{field}: contains placeholder text '{placeholder}'")
                        break

        # Check personality_report has enough substance
        report = data.get("personality_report", "")
        if report and isinstance(report, str):
            # Check for paragraph structure
            paragraphs = [p for p in report.split("\n\n") if p.strip()]
            if len(paragraphs) < 3:
                warnings.append("personality_report: insufficient paragraph structure")

            # Check for astrological terms (basic quality check)
            astro_terms = [
                "планет", "дом", "знак", "йог", "накшатр",
                "лагн", "карак", "даш", "сил"
            ]
            found_terms = sum(1 for term in astro_terms if term in report.lower())
            if found_terms < 3:
                warnings.append("personality_report: may lack astrological specificity")

        # Check archetype coherence
        arch_name = data.get("archetype_name", "")
        arch_desc = data.get("archetype_description", "")
        if arch_name and arch_desc and isinstance(arch_name, str) and isinstance(arch_desc, str):
            # Name should appear in description
            name_words = arch_name.lower().split()
            if not any(word in arch_desc.lower() for word in name_words if len(word) > 3):
                warnings.append("archetype: name may not match description")

        return warnings

    def validate(self, raw_output: str) -> Tuple[Optional[PersonalityReportOutput], ValidationResult]:
        """
        Complete validation pipeline.

        Args:
            raw_output: Raw LLM output string

        Returns:
            Tuple of (PersonalityReportOutput or None, ValidationResult)
        """
        # Parse JSON
        data, json_errors = self.validate_json(raw_output)

        if data is None:
            return None, ValidationResult(
                is_valid=False,
                errors=json_errors,
                warnings=[],
                char_counts={}
            )

        # Validate fields
        result = self.validate_fields(data)

        # Add any JSON parsing warnings
        if json_errors:
            result.warnings = json_errors + result.warnings

        # Create output object if valid
        if result.is_valid:
            try:
                output = self._create_output(data)
                return output, result
            except Exception as e:
                result.errors.append(f"Failed to create output object: {str(e)}")
                result.is_valid = False
                return None, result

        return None, result

    def _create_output(self, data: dict) -> PersonalityReportOutput:
        """Create PersonalityReportOutput from validated data"""
        # Ensure lists are properly typed
        talents = data.get("top_talents", [])
        if not isinstance(talents, list):
            talents = []

        growth = data.get("growth_areas", [])
        if not isinstance(growth, list):
            growth = []

        return PersonalityReportOutput(
            personality_report=str(data.get("personality_report", "")),
            personality_summary=str(data.get("personality_summary", "")),
            archetype_name=str(data.get("archetype_name", "")),
            archetype_description=str(data.get("archetype_description", "")),
            soul_purpose_description=str(data.get("soul_purpose_description", "")),
            life_mission_statement=str(data.get("life_mission_statement", "")),
            public_image_description=str(data.get("public_image_description", "")),
            current_period_advice=str(data.get("current_period_advice", "")),
            top_talents=[str(t) for t in talents[:7]],  # Limit to max
            growth_areas=[str(g) for g in growth[:5]],  # Limit to max
        )


def validate_output(raw_output: str, strict: bool = False) -> Tuple[Optional[PersonalityReportOutput], ValidationResult]:
    """
    Convenience function for validation.

    Args:
        raw_output: Raw LLM output string
        strict: If True, warnings become errors

    Returns:
        Tuple of (PersonalityReportOutput or None, ValidationResult)
    """
    validator = OutputValidator(strict=strict)
    return validator.validate(raw_output)
