"""Minimal event placeholder for Aurora Studio."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Event:
    """A minimal event record.

    This is not an event bus implementation.
    """

    event_type: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
