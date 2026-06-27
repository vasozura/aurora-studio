"""Validation contract placeholders."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationIssue:
    """Placeholder validation issue contract."""

    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True)
class ValidationReport:
    """Placeholder validation report contract."""

    target_id: str
    status: str
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)
