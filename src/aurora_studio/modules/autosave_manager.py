"""Autosave manager for Aurora Studio v0.3.

Explicit autosave only. No background thread. No timer.
Autosave written only when explicitly called.
Autosave file is separate from the manual save bundle.
Never silently restores. Recovery must be explicit.
Never writes outside the project path.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aurora_studio.contracts.autosave import (
    AutosaveRecord,
    AutosaveRecoveryReport,
    AutosaveState,
)

AUTOSAVE_DIR = ".autosave"
AUTOSAVE_FILE = "aurora_project.autosave.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AutosaveManager:
    """Manages explicit autosave state. No background thread created."""

    def __init__(self) -> None:
        self._state = AutosaveState()

    def get_state(self) -> AutosaveState:
        return self._state

    def enable_autosave(self, project_path: str | Path) -> AutosaveState:
        autosave_path = str(Path(project_path).resolve() / AUTOSAVE_DIR / AUTOSAVE_FILE)
        self._state = AutosaveState(
            project_id=str(project_path),
            enabled=True,
            dirty=self._state.dirty,
            last_manual_save_at=self._state.last_manual_save_at,
            last_autosave_at=self._state.last_autosave_at,
            autosave_path=autosave_path,
            status="idle",
            message="Autosave enabled.",
        )
        return self._state

    def disable_autosave(self) -> AutosaveState:
        self._state = AutosaveState(
            project_id=self._state.project_id,
            enabled=False,
            dirty=False,
            last_manual_save_at=self._state.last_manual_save_at,
            last_autosave_at=self._state.last_autosave_at,
            autosave_path=self._state.autosave_path,
            status="disabled",
            message="Autosave disabled.",
        )
        return self._state

    def mark_dirty(self, reason: str = "") -> AutosaveState:
        if not self._state.enabled:
            return self._state
        self._state = AutosaveState(
            project_id=self._state.project_id,
            enabled=True,
            dirty=True,
            last_manual_save_at=self._state.last_manual_save_at,
            last_autosave_at=self._state.last_autosave_at,
            autosave_path=self._state.autosave_path,
            status="dirty",
            message=f"Project has unsaved changes.{' ' + reason if reason else ''}",
        )
        return self._state

    def clear_dirty(self) -> AutosaveState:
        self._state = AutosaveState(
            project_id=self._state.project_id,
            enabled=self._state.enabled,
            dirty=False,
            last_manual_save_at=self._state.last_manual_save_at,
            last_autosave_at=self._state.last_autosave_at,
            autosave_path=self._state.autosave_path,
            status="idle" if self._state.enabled else "disabled",
            message="",
        )
        return self._state

    def write_autosave(self, bundle_data: dict[str, Any], project_path: str | Path) -> AutosaveRecord:
        """Write autosave file. Never overwrites manual save bundle.

        Raises:
            ValueError: if autosave is disabled.
            OSError: if write fails.
        """
        if not self._state.enabled:
            raise ValueError("Autosave is disabled. Enable autosave before writing.")

        pp = Path(project_path).resolve()
        autosave_dir = pp / AUTOSAVE_DIR
        autosave_dir.mkdir(parents=True, exist_ok=True)
        autosave_path = autosave_dir / AUTOSAVE_FILE

        # Verify we're writing inside the project path (no traversal)
        try:
            autosave_path.resolve().relative_to(pp)
        except ValueError:
            raise ValueError("Autosave path is outside project path — write refused.")

        with open(autosave_path, "w", encoding="utf-8") as f:
            json.dump(bundle_data, f, indent=2)

        size = autosave_path.stat().st_size
        now = _utc_now()

        self._state = AutosaveState(
            project_id=self._state.project_id,
            enabled=True,
            dirty=False,
            last_manual_save_at=self._state.last_manual_save_at,
            last_autosave_at=now,
            autosave_path=str(autosave_path),
            status="saved",
            message="Autosave written successfully.",
        )

        return AutosaveRecord(
            autosave_id=str(uuid.uuid4())[:8],
            project_id=self._state.project_id,
            autosave_path=str(autosave_path),
            created_at=now,
            size_bytes=size,
            is_valid_json=True,
            message="Autosave written.",
        )

    def has_recovery(self, project_path: str | Path) -> bool:
        """Return True if an autosave file exists at the project path."""
        p = Path(project_path).resolve() / AUTOSAVE_DIR / AUTOSAVE_FILE
        return p.exists()

    def build_recovery_report(self, project_path: str | Path) -> AutosaveRecoveryReport:
        """Check if an autosave recovery file exists and is valid JSON."""
        p = Path(project_path).resolve() / AUTOSAVE_DIR / AUTOSAVE_FILE
        if not p.exists():
            return AutosaveRecoveryReport(
                has_recovery=False, autosave_path=str(p),
                is_valid_json=False, message="No autosave file found.",
            )
        try:
            with open(p) as f:
                json.load(f)
            return AutosaveRecoveryReport(
                has_recovery=True, autosave_path=str(p),
                is_valid_json=True, message="Valid autosave found.",
            )
        except json.JSONDecodeError as exc:
            return AutosaveRecoveryReport(
                has_recovery=True, autosave_path=str(p),
                is_valid_json=False, message=f"Invalid autosave JSON: {exc}",
            )

    def load_autosave(self, project_path: str | Path) -> dict[str, Any]:
        """Load and return autosave data. Validates JSON first."""
        p = Path(project_path).resolve() / AUTOSAVE_DIR / AUTOSAVE_FILE
        if not p.exists():
            raise FileNotFoundError(f"No autosave file: {p}")
        with open(p) as f:
            data = json.load(f)  # raises JSONDecodeError if invalid
        return data

    def discard_autosave(self, project_path: str | Path) -> bool:
        """Remove only the autosave file. Never touches manual save bundle."""
        p = Path(project_path).resolve() / AUTOSAVE_DIR / AUTOSAVE_FILE
        if p.exists():
            p.unlink()
            self._state = AutosaveState(
                project_id=self._state.project_id,
                enabled=self._state.enabled,
                dirty=False,
                last_manual_save_at=self._state.last_manual_save_at,
                last_autosave_at=self._state.last_autosave_at,
                autosave_path=self._state.autosave_path,
                status="idle" if self._state.enabled else "disabled",
                message="Autosave discarded.",
            )
            return True
        return False
