"""Project Manager first minimal implementation."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from aurora_studio.contracts.project import (
    CURRENT_PROJECT_VERSION,
    PROJECT_FILENAME,
    ProjectMetadata,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id
from aurora_studio.core.readiness import Readiness


class ProjectManager:
    """Minimal Project Manager implementation.

    This class implements only local JSON project metadata create/open/save behavior.

    It does not implement:
    - Scene management
    - Shot management
    - Asset management
    - Workspace management
    - Database persistence
    - Provider integration
    - Plugin execution
    - GUI behavior
    """

    module_name = "Project Manager"
    readiness = Readiness.NOT_READY

    def get_readiness(self) -> Readiness:
        """Return module readiness."""

        return self.readiness

    def describe(self) -> str:
        """Return a short implementation description."""

        return (
            "Project Manager supports minimal local metadata create/open/save "
            "and remains not ready for full product implementation."
        )

    def create_project(self, root_path: str | Path, title: str) -> ProjectMetadata:
        """Create a minimal Aurora project metadata file.

        The project is represented by a local JSON file named ``aurora_project.json``.
        """

        clean_title = self._validate_title(title)
        root = Path(root_path)
        project_file = self._project_file(root)

        if project_file.exists():
            raise ValidationError(f"Project already exists: {project_file}")

        root.mkdir(parents=True, exist_ok=True)

        now = utc_now_iso()
        metadata = ProjectMetadata(
            project_id=new_id("project"),
            title=clean_title,
            version=CURRENT_PROJECT_VERSION,
            created_at=now,
            modified_at=now,
        )
        self._write_metadata(project_file, metadata)
        return metadata

    def open_project(self, root_path: str | Path) -> ProjectMetadata:
        """Open a minimal Aurora project metadata file."""

        project_file = self._project_file(Path(root_path))
        if not project_file.exists():
            raise ValidationError(f"Project metadata file not found: {project_file}")

        data = self._read_json(project_file)
        try:
            return ProjectMetadata.from_dict(data)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    def save_project(self, root_path: str | Path, metadata: ProjectMetadata) -> ProjectMetadata:
        """Save project metadata and update ``modified_at``."""

        root = Path(root_path)
        project_file = self._project_file(root)
        if not project_file.exists():
            raise ValidationError(f"Project metadata file not found: {project_file}")

        clean_title = self._validate_title(metadata.title)
        updated = replace(metadata, title=clean_title, modified_at=utc_now_iso())
        self._write_metadata(project_file, updated)
        return updated

    def _project_file(self, root: Path) -> Path:
        """Return project metadata file path."""

        return root / PROJECT_FILENAME

    def _validate_title(self, title: str) -> str:
        """Validate and normalize project title."""

        clean_title = title.strip()
        if not clean_title:
            raise ValidationError("Project title must not be empty.")
        return clean_title

    def _read_json(self, path: Path) -> dict[str, Any]:
        """Read a JSON object from disk."""

        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"Invalid project metadata JSON: {path}") from exc

        if not isinstance(data, dict):
            raise ValidationError(f"Project metadata must be a JSON object: {path}")
        return data

    def _write_metadata(self, path: Path, metadata: ProjectMetadata) -> None:
        """Write metadata to disk as UTF-8 JSON."""

        with path.open("w", encoding="utf-8") as handle:
            json.dump(metadata.to_dict(), handle, indent=2, ensure_ascii=False)
            handle.write("\n")
