"""Project backup manager for Aurora Studio v0.3.

Creates local backup copies of aurora_project.json bundles.
Never writes outside the project path.
Never silently deletes the current bundle.
"""

from __future__ import annotations

import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aurora_studio.contracts.recovery import ProjectBackupRecord

BACKUP_DIR = ".backups"
BUNDLE_FILE = "aurora_project.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts_label() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


class ProjectBackupManager:
    def _backup_dir(self, project_path: str | Path) -> Path:
        return Path(project_path) / BACKUP_DIR

    def _source_bundle(self, project_path: str | Path) -> Path:
        return Path(project_path) / BUNDLE_FILE

    def create_backup(self, project_path: str | Path, reason: str = "manual") -> ProjectBackupRecord:
        """Back up the current bundle to .backups/. Returns record.

        Raises FileNotFoundError if no bundle exists.
        Raises OSError on write failure.
        Never deletes or overwrites the source bundle.
        """
        project_path = Path(project_path).resolve()
        source = self._source_bundle(project_path)
        if not source.exists():
            raise FileNotFoundError(f"No bundle to back up: {source}")

        backup_dir = self._backup_dir(project_path)
        backup_dir.mkdir(parents=True, exist_ok=True)

        bid = str(uuid.uuid4())[:8]
        ts = _ts_label()
        backup_name = f"aurora_project.{ts}.{bid}.json"
        backup_path = backup_dir / backup_name

        shutil.copy2(str(source), str(backup_path))
        size = backup_path.stat().st_size

        return ProjectBackupRecord(
            backup_id=bid,
            project_id=str(project_path),
            source_path=str(source),
            backup_path=str(backup_path),
            reason=reason,
            created_at=_utc_now(),
            size_bytes=size,
        )

    def list_backups(self, project_path: str | Path) -> list[ProjectBackupRecord]:
        """List all backups under .backups/, sorted oldest first."""
        backup_dir = self._backup_dir(Path(project_path).resolve())
        if not backup_dir.exists():
            return []
        records = []
        for f in sorted(backup_dir.glob("aurora_project.*.json")):
            parts = f.stem.split(".")
            bid = parts[-1] if len(parts) >= 3 else str(f.name)
            records.append(ProjectBackupRecord(
                backup_id=bid,
                project_id=str(project_path),
                source_path=str(self._source_bundle(project_path)),
                backup_path=str(f),
                reason="unknown",
                created_at="",
                size_bytes=f.stat().st_size,
            ))
        return records

    def get_latest_backup(self, project_path: str | Path) -> ProjectBackupRecord | None:
        backups = self.list_backups(project_path)
        return backups[-1] if backups else None

    def prune_backups(self, project_path: str | Path, keep: int = 10) -> int:
        """Delete oldest backups, keeping the most recent `keep` files.

        Only deletes files matching aurora_project.*.json in .backups/.
        Returns count of deleted files.
        """
        backup_dir = self._backup_dir(Path(project_path).resolve())
        if not backup_dir.exists():
            return 0
        files = sorted(backup_dir.glob("aurora_project.*.json"))
        to_delete = files[:-keep] if keep > 0 else files
        for f in to_delete:
            f.unlink()
        return len(to_delete)
