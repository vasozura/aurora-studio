"""Command stack contracts for Aurora Studio v0.3.

In-memory only. No persistence. No cross-session undo.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CommandRecord:
    command_id: str
    command_type: str
    target_type: str
    target_id: str
    description: str = ""
    before_state: str = ""   # JSON string snapshot
    after_state: str = ""    # JSON string snapshot
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "CommandRecord":
        return cls(
            command_id=str(data.get("command_id", "")),
            command_type=str(data.get("command_type", "")),
            target_type=str(data.get("target_type", "")),
            target_id=str(data.get("target_id", "")),
            description=str(data.get("description", "")),
            before_state=str(data.get("before_state", "")),
            after_state=str(data.get("after_state", "")),
            created_at=str(data.get("created_at", "")),
        )


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    command_id: str
    message: str
    applied_state: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CommandStackState:
    undo_count: int
    redo_count: int
    last_command_id: str
    can_undo: bool
    can_redo: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
