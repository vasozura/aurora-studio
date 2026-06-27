"""AFL contract placeholders."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AFLValidationReport:
    """Placeholder AFL validation report contract."""

    target_id: str
    status: str
    message: str = ""
