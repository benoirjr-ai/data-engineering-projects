"""
Define consistent structures for validation errors and results.

This module describes validation outcomes. It does not validate
files, move files to quarantine, or configure logging.
"""
from dataclasses import dataclass, field

@dataclass
class ValidationError:
    """Describe one validation problems"""

    category: str
    message: str
    row_number: int | None = None


@dataclass
class ValidationResult:
    """Summarize the outcome of validating one file."""

    valid: bool
    row_count: int = 0
    errors: list[ValidationError] = field(default_factory=list)