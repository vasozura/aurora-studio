"""Autosave contracts for Aurora Studio v0.3.

Explicit autosave only. No background thread. No timer.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

AUTOSAVE_STATUSES = frozenset({
    "disabled", "idle", "dirty", "saved", "error", "recovery_available",
})


@dataclass(frozen=True)
class AutosaveState:
    project_id: str = ""
    enabled: bool = False
    dirty: bool = False
    last_manual_save_at: str = ""
    last_autosave_at: str = ""
    autosave_path: str = ""
    status: str = "disabled"
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AutosaveRecord:
    autosave_id: str
    project_id: str
    autosave_path: str
    created_at: str = ""
    size_bytes: int = 0
    is_valid_json: bool = False
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AutosaveRecoveryReport:
    has_recovery: bool
    autosave_path: str
    is_valid_json: bool
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
