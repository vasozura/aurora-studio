"""Local JSON project store for Aurora Studio."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aurora_studio.contracts.project_bundle import (
    DEFAULT_BUNDLE_FILENAME,
    CURRENT_BUNDLE_VERSION,
    ProjectBundle,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError


class LocalProjectStore:
    """Minimal local JSON project store.

    Saves and loads project bundles as UTF-8 JSON files.

    Does not implement:
    - Database persistence
    - Migration engine
    - Automatic manager rehydration
    - File locking
    - Incremental saves
    - Binary media storage
    - Encryption
    - GUI dialogs
    - Provider integration
    - Plugin execution
    """

    def save_bundle(self, path: str | Path, bundle: ProjectBundle) -> Path:
        """Save a project bundle to a JSON file.

        If path is a directory, saves to path / aurora_bundle.json.
        Creates parent directories as needed.
        Returns the final file path.
        """

        self.validate_bundle(bundle)
        file_path = self._resolve_file_path(Path(path))
        file_path.parent.mkdir(parents=True, exist_ok=True)

        updated = bundle.with_updates(modified_at=utc_now_iso())

        with file_path.open("w", encoding="utf-8") as handle:
            json.dump(updated.to_dict(), handle, indent=2, ensure_ascii=False)
            handle.write("\n")

        return file_path

    def load_bundle(self, path: str | Path) -> ProjectBundle:
        """Load a project bundle from a JSON file.

        If path is a directory, loads from path / aurora_bundle.json.
        """

        file_path = self._resolve_file_path(Path(path))

        if not file_path.exists():
            raise ValidationError(f"Bundle file not found: {file_path}")

        try:
            with file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"Invalid bundle JSON: {file_path}") from exc

        if not isinstance(data, dict):
            raise ValidationError(f"Bundle JSON must be an object: {file_path}")

        return ProjectBundle.from_dict(data)

    def create_bundle(
        self,
        project_metadata: Any = None,
        workspace: Any = None,
        scene_manager: Any = None,
        shot_manager: Any = None,
        timeline_manager: Any = None,
        asset_manager: Any = None,
        character_manager: Any = None,
        afl_engine: Any = None,
        prompt_export_manager: Any = None,
        plugin_manager: Any = None,
    ) -> ProjectBundle:
        """Build a ProjectBundle from optional in-memory manager objects.

        Does not mutate any manager.
        """

        # Resolve project_metadata
        if project_metadata is not None and hasattr(project_metadata, "to_dict"):
            meta_dict = project_metadata.to_dict()
        elif isinstance(project_metadata, dict):
            meta_dict = project_metadata
        else:
            meta_dict = {}

        # Resolve workspace state
        workspace_state_dict: dict | None = None
        if workspace is not None and hasattr(workspace, "get_state"):
            state = workspace.get_state()
            if hasattr(state, "to_dict"):
                workspace_state_dict = state.to_dict()

        # Resolve collections
        def collect(manager: Any, method: str) -> tuple:
            if manager is not None and hasattr(manager, method):
                return tuple(item.to_dict() for item in getattr(manager, method)())
            return ()

        now = utc_now_iso()

        return ProjectBundle(
            schema_version=CURRENT_BUNDLE_VERSION,
            project_metadata=meta_dict,
            workspace_state=workspace_state_dict,
            scenes=collect(scene_manager, "list_scenes"),
            shots=collect(shot_manager, "list_shots"),
            timelines=collect(timeline_manager, "list_timelines"),
            assets=collect(asset_manager, "list_assets"),
            characters=collect(character_manager, "list_characters"),
            afl_reports=collect(afl_engine, "list_validation_reports"),
            export_artifacts=collect(prompt_export_manager, "list_export_artifacts"),
            plugins=collect(plugin_manager, "list_plugins"),
            created_at=now,
            modified_at=now,
        )

    def validate_bundle(self, bundle: Any) -> bool:
        """Validate a bundle object. Returns True or raises ValidationError."""

        if not isinstance(bundle, ProjectBundle):
            raise ValidationError(
                f"Expected ProjectBundle, got {type(bundle).__name__}."
            )
        if bundle.schema_version not in {"0.1.0"}:
            raise ValidationError(
                f"Unsupported bundle schema_version: {bundle.schema_version!r}."
            )
        if not isinstance(bundle.project_metadata, dict):
            raise ValidationError("Bundle project_metadata must be a dict.")
        return True

    def _resolve_file_path(self, path: Path) -> Path:
        """Resolve a file path, appending default filename for directories."""

        if path.is_dir() or not path.suffix:
            return path / DEFAULT_BUNDLE_FILENAME
        return path
