"""Local JSON project store for Aurora Studio."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aurora_studio.contracts.project_bundle import (
    DEFAULT_BUNDLE_FILENAME,
    CURRENT_BUNDLE_VERSION,
    _SUPPORTED_VERSIONS,
    ProjectBundle,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError


def _backup_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


class LocalProjectStore:
    """Minimal local JSON project store."""

    def save_bundle(self, path: str | Path, bundle: ProjectBundle) -> Path:
        self.validate_bundle(bundle)
        file_path = self._resolve_file_path(Path(path))
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Backup before overwrite
        if file_path.exists():
            backup_dir = file_path.parent / ".backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            bak_name = f"{file_path.stem}.bak.{_backup_timestamp()}{file_path.suffix}"
            shutil.copy2(file_path, backup_dir / bak_name)

        updated = bundle.with_updates(modified_at=utc_now_iso())
        with file_path.open("w", encoding="utf-8") as handle:
            json.dump(updated.to_dict(), handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        return file_path

    def load_bundle(self, path: str | Path) -> ProjectBundle:
        file_path = self._resolve_file_path(Path(path))
        if not file_path.exists():
            raise ValidationError(f"Bundle file not found: {file_path}")
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValidationError(
                f"Bundle JSON is corrupt and cannot be loaded: {file_path}\nDetails: {exc}"
            ) from exc
        if not isinstance(data, dict):
            raise ValidationError(f"Bundle JSON must be a top-level object (dict): {file_path}")
        if "project_metadata" not in data or not isinstance(data["project_metadata"], dict):
            raise ValidationError(
                f"Bundle is missing required section 'project_metadata': {file_path}"
            )
        return ProjectBundle.from_dict(data)

    def validate_bundle_file(self, path: str | Path) -> dict[str, Any]:
        """Validate bundle file on disk — returns report dict, never raises."""
        file_path = self._resolve_file_path(Path(path))
        report: dict[str, Any] = {"ok": False, "path": str(file_path), "errors": [], "schema_version": None}
        if not file_path.exists():
            report["errors"].append(f"File not found: {file_path}")
            return report
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as exc:
            report["errors"].append(f"JSON parse error: {exc}")
            return report
        if not isinstance(data, dict):
            report["errors"].append("Root must be a JSON object.")
            return report
        sv = data.get("schema_version", "missing")
        report["schema_version"] = sv
        if sv not in _SUPPORTED_VERSIONS and sv != "missing":
            report["errors"].append(f"Unsupported schema_version: {sv!r}")
        if "project_metadata" not in data:
            report["errors"].append("Missing required section: project_metadata")
        if not report["errors"]:
            report["ok"] = True
        return report

    def export_bundle_copy(
        self, source_project_path: str | Path, destination_file_path: str | Path
    ) -> Path:
        """Copy the bundle file to a destination path."""
        src_file = self._resolve_file_path(Path(source_project_path))
        if not src_file.exists():
            raise ValidationError(f"Source bundle not found: {src_file}")
        dst = Path(destination_file_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            bak = dst.parent / f"{dst.stem}.bak.{_backup_timestamp()}{dst.suffix}"
            shutil.copy2(dst, bak)
        shutil.copy2(src_file, dst)
        return dst

    def import_bundle_copy(
        self, source_file_path: str | Path, destination_project_path: str | Path
    ) -> ProjectBundle:
        """Copy a bundle file into a project directory and load it."""
        src = Path(source_file_path)
        if not src.exists():
            raise ValidationError(f"Import source not found: {src}")
        try:
            with src.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"Import source JSON is corrupt: {exc}") from exc
        if not isinstance(data, dict):
            raise ValidationError("Import source must be a JSON object.")
        dst_dir = Path(destination_project_path)
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_file = dst_dir / DEFAULT_BUNDLE_FILENAME
        if dst_file.exists():
            bak = dst_dir / ".backups"
            bak.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst_file, bak / f"aurora_bundle.bak.{_backup_timestamp()}.json")
        shutil.copy2(src, dst_file)
        return self.load_bundle(dst_dir)

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
        asset_link_manager: Any = None,
        prompt_template_manager: Any = None,
        export_profile_manager: Any = None,
    ) -> ProjectBundle:
        """Build a ProjectBundle from optional in-memory manager objects."""
        if project_metadata is not None and hasattr(project_metadata, "to_dict"):
            meta_dict = project_metadata.to_dict()
        elif isinstance(project_metadata, dict):
            meta_dict = project_metadata
        else:
            meta_dict = {}

        workspace_state_dict: dict | None = None
        if workspace is not None and hasattr(workspace, "get_state"):
            state = workspace.get_state()
            if hasattr(state, "to_dict"):
                workspace_state_dict = state.to_dict()

        def collect(manager: Any, method: str) -> tuple:
            if manager is not None and hasattr(manager, method):
                return tuple(item.to_dict() for item in getattr(manager, method)())
            return ()

        def collect_custom_templates(mgr: Any) -> tuple:
            if mgr is not None and hasattr(mgr, "list_templates"):
                return tuple(t.to_dict() for t in mgr.list_templates(include_defaults=False))
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
            asset_links=collect(asset_link_manager, "list_all"),
            prompt_templates=collect_custom_templates(prompt_template_manager),
            export_profiles=collect(export_profile_manager, "list_profiles"),
            created_at=now,
            modified_at=now,
        )

    def validate_bundle(self, bundle: Any) -> bool:
        if not isinstance(bundle, ProjectBundle):
            raise ValidationError(f"Expected ProjectBundle, got {type(bundle).__name__}.")
        if bundle.schema_version not in _SUPPORTED_VERSIONS:
            raise ValidationError(f"Unsupported bundle schema_version: {bundle.schema_version!r}.")
        if not isinstance(bundle.project_metadata, dict):
            raise ValidationError("Bundle project_metadata must be a dict.")
        return True

    def _resolve_file_path(self, path: Path) -> Path:
        if path.is_dir() or not path.suffix:
            return path / DEFAULT_BUNDLE_FILENAME
        return path
