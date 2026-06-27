"""Minimal result object for controlled skeleton operations."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Result:
    """A minimal operation result.

    This is a placeholder contract, not a final application result model.
    """

    success: bool
    message: str = ""
    data: Any | None = None
    errors: tuple[str, ...] = field(default_factory=tuple)
