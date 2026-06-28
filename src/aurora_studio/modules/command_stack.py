"""Minimal in-memory command stack for Aurora Studio v0.3.

In-memory only. No persistence. No database. No cross-session undo.
Maximum stack size: 100.
Safe actions only: update_scene_detail, update_shot_detail,
  update_asset_metadata, update_character_detail.

Undo/redo applies before/after state snapshots.
Unsupported commands return not_supported rather than corrupting state.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.command import CommandRecord, CommandResult, CommandStackState

MAX_STACK_SIZE = 100

SUPPORTED_COMMAND_TYPES = frozenset({
    "update_scene_detail",
    "update_shot_detail",
    "update_asset_metadata",
    "update_character_detail",
})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CommandStack:
    """Minimal in-memory undo/redo stack."""

    def __init__(self) -> None:
        self._undo_stack: list[CommandRecord] = []
        self._redo_stack: list[CommandRecord] = []

    def push(self, command: CommandRecord) -> None:
        """Push a command onto the undo stack. Clears the redo stack."""
        self._undo_stack.append(command)
        if len(self._undo_stack) > MAX_STACK_SIZE:
            self._undo_stack = self._undo_stack[-MAX_STACK_SIZE:]
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def get_state(self) -> CommandStackState:
        last_id = self._undo_stack[-1].command_id if self._undo_stack else ""
        return CommandStackState(
            undo_count=len(self._undo_stack),
            redo_count=len(self._redo_stack),
            last_command_id=last_id,
            can_undo=self.can_undo(),
            can_redo=self.can_redo(),
        )

    def undo(self) -> CommandResult:
        """Undo the last command. Returns CommandResult."""
        if not self._undo_stack:
            return CommandResult(ok=False, command_id="", message="Nothing to undo.")

        command = self._undo_stack.pop()
        if command.command_type not in SUPPORTED_COMMAND_TYPES:
            # Put it back and report not_supported
            self._undo_stack.append(command)
            return CommandResult(
                ok=False,
                command_id=command.command_id,
                message=f"Undo not supported for command type {command.command_type!r}.",
                applied_state="not_supported",
            )

        self._redo_stack.append(command)
        return CommandResult(
            ok=True,
            command_id=command.command_id,
            message=f"Undone: {command.description}",
            applied_state=command.before_state,
        )

    def redo(self) -> CommandResult:
        """Redo the last undone command."""
        if not self._redo_stack:
            return CommandResult(ok=False, command_id="", message="Nothing to redo.")

        command = self._redo_stack.pop()
        if command.command_type not in SUPPORTED_COMMAND_TYPES:
            self._redo_stack.append(command)
            return CommandResult(
                ok=False,
                command_id=command.command_id,
                message=f"Redo not supported for command type {command.command_type!r}.",
                applied_state="not_supported",
            )

        self._undo_stack.append(command)
        return CommandResult(
            ok=True,
            command_id=command.command_id,
            message=f"Redone: {command.description}",
            applied_state=command.after_state,
        )

    def clear(self) -> None:
        """Clear both stacks."""
        self._undo_stack.clear()
        self._redo_stack.clear()


def make_command(
    command_type: str,
    target_type: str,
    target_id: str,
    before_state: dict[str, Any],
    after_state: dict[str, Any],
    description: str = "",
) -> CommandRecord:
    """Helper to build a CommandRecord with JSON-serialized snapshots."""
    return CommandRecord(
        command_id=str(uuid.uuid4())[:8],
        command_type=command_type,
        target_type=target_type,
        target_id=target_id,
        description=description or f"{command_type} on {target_type}:{target_id}",
        before_state=json.dumps(before_state),
        after_state=json.dumps(after_state),
        created_at=_utc_now(),
    )
