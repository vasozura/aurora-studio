"""Project recovery manager for Aurora Studio v0.3.

Scans for recovery candidates, validates, and restores backups.
Never writes outside the project path.
Always creates a safety backup before restore.
"""

from __future__ import annotations

import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aurora_studio.contracts.recovery import (
    ProjectRecoveryCandidate,
    ProjectRecoveryReport,
)

BACKUP_DIR = ".backups"
BUNDLE_FILE = "aurora_project.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProjectRecoveryManager:
    def _project_path(self, project_path: str | Path) -> Path:
        return Path(project_path).resolve()

    def scan_recovery_candidates(self, project_path: str | Path) -> list[ProjectRecoveryCandidate]:
        """Scan .backups/ for JSON recovery candidates. No file content execution."""
        pp = self._project_path(project_path)
        backup_dir = pp / BACKUP_DIR
        candidates: list[ProjectRecoveryCandidate] = []
        if not backup_dir.exists():
            return candidates

        for f in sorted(backup_dir.glob("aurora_project.*.json")):
            cid = str(uuid.uuid4())[:8]
            valid, msg = self._validate_json(f)
            candidates.append(ProjectRecoveryCandidate(
                candidate_id=cid,
                project_id=str(pp),
                candidate_path=str(f),
                candidate_type="backup",
                created_at=_utc_now(),
                size_bytes=f.stat().st_size,
                is_valid_json=valid,
                validation_message=msg,
            ))
        return candidates

    def _validate_json(self, path: Path) -> tuple[bool, str]:
        """Validate that a file is valid JSON. Returns (is_valid, message)."""
        try:
            with open(path) as f:
                json.load(f)
            return True, "Valid JSON."
        except json.JSONDecodeError as exc:
            return False, f"Invalid JSON: {exc}"
        except OSError as exc:
            return False, f"Cannot read file: {exc}"

    def validate_recovery_candidate(self, candidate_path: str | Path) -> tuple[bool, str]:
        return self._validate_json(Path(candidate_path))

    def restore_backup(self, project_path: str | Path, backup_path: str | Path) -> str:
        """Restore a backup to the project bundle.

        Steps:
        1. Validate backup JSON before touching anything.
        2. If current bundle exists, create a pre-restore safety backup.
        3. Copy backup to bundle location.
        4. Return path of restored bundle.

        Never writes outside project_path.
        Never silently destroys current bundle.
        """
        pp = self._project_path(project_path)
        backup_path = Path(backup_path).resolve()
        bundle_path = pp / BUNDLE_FILE

        # Validate backup JSON first
        valid, msg = self._validate_json(backup_path)
        if not valid:
            raise ValueError(f"Backup is not valid JSON and cannot be restored: {msg}")

        # Safety: validate backup is under known location (no path traversal)
        try:
            backup_path.relative_to(pp)
        except ValueError:
            raise ValueError(f"Backup path is outside project path — restore refused.")

        # Create pre-restore backup of current bundle if it exists
        if bundle_path.exists():
            from aurora_studio.modules.project_backup import ProjectBackupManager
            mgr = ProjectBackupManager()
            mgr.create_backup(pp, reason="pre-restore")

        # Restore
        shutil.copy2(str(backup_path), str(bundle_path))
        return str(bundle_path)

    def build_recovery_report(self, project_path: str | Path) -> ProjectRecoveryReport:
        """Build a full recovery report for the project path."""
        candidates = self.scan_recovery_candidates(project_path)
        valid_count = sum(1 for c in candidates if c.is_valid_json)
        if not candidates:
            status = "no_candidates"
            message = "No backup recovery candidates found."
        elif valid_count == 0:
            status = "all_invalid"
            message = f"{len(candidates)} candidate(s) found but none are valid JSON."
        else:
            status = "candidates_available"
            message = f"{valid_count} valid candidate(s) available for recovery."
        return ProjectRecoveryReport(
            status=status,
            candidate_count=len(candidates),
            candidates=tuple(candidates),
            message=message,
        )
