"""Aurora Studio UI actions layer.

UISession wraps ApplicationService with UI-friendly error handling.
All results are UIActionResult — ok/message/payload — never raised exceptions.
Payload is always JSON-serializable.
Does not duplicate manager logic.
Does not read/write bundle JSON directly.
Does not call providers.
Does not execute plugins.
Standard-library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aurora_studio.core.errors import ValidationError
from aurora_studio.services import ApplicationService
from aurora_studio.ui.view_models import (
    AFLReportViewModel,
    AppStateViewModel,
    AssetViewModel,
    CharacterViewModel,
    ExportArtifactViewModel,
    PluginViewModel,
    ProjectViewModel,
    SceneViewModel,
    ShotViewModel,
    TimelineViewModel,
    WorkspaceViewModel,
)


@dataclass(frozen=True)
class UIActionResult:
    """Result of a UI action.

    ok: True on success, False on any error.
    message: Human-readable summary (empty string on success is fine).
    payload: JSON-serializable dict or None.
    """

    ok: bool
    message: str
    payload: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "message": self.message,
            "payload": self.payload,
        }


def _ok(payload: dict[str, Any] | None = None, message: str = "") -> UIActionResult:
    return UIActionResult(ok=True, message=message, payload=payload)


def _fail(message: str) -> UIActionResult:
    return UIActionResult(ok=False, message=message, payload=None)


class UISession:
    """Thin UI session that delegates all work to ApplicationService.

    All public methods catch errors and return UIActionResult.
    Never raises. Payload is always JSON-serializable.
    """

    def __init__(self, service: ApplicationService | None = None) -> None:
        self.service = service or ApplicationService()

    # ------------------------------------------------------------------
    # Project
    # ------------------------------------------------------------------

    def create_project(self, path: str | Path, title: str) -> UIActionResult:
        try:
            meta = self.service.create_project(path, title)
            return _ok(ProjectViewModel.from_metadata(meta).to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def open_project(self, path: str | Path) -> UIActionResult:
        try:
            meta = self.service.open_project(path)
            return _ok(ProjectViewModel.from_metadata(meta).to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # Scene / Shot
    # ------------------------------------------------------------------

    def create_scene(self, title: str, purpose: str = "") -> UIActionResult:
        try:
            record = self.service.create_scene(title, purpose)
            return _ok(SceneViewModel.from_record(record).to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def create_shot(
        self,
        scene_id: str,
        title: str,
        purpose: str = "",
        order_index: int | None = None,
    ) -> UIActionResult:
        try:
            record = self.service.create_shot(scene_id, title, purpose, order_index)
            return _ok(ShotViewModel.from_record(record).to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_bundle(self, path: str | Path) -> UIActionResult:
        try:
            saved_path = self.service.save_bundle(path)
            return _ok({"bundle_path": str(saved_path)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def load_and_rehydrate_bundle(self, path: str | Path) -> UIActionResult:
        try:
            result = self.service.load_and_rehydrate_bundle(path)
            summary = result["summary"]
            return _ok({
                "schema_version": result["bundle"].schema_version,
                "rehydrated": True,
                **summary,
            })
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # App state
    # ------------------------------------------------------------------

    def get_app_state(self) -> UIActionResult:
        try:
            ws_state = self.service.get_workspace_state()
            workspace_vm = WorkspaceViewModel.from_state(ws_state)

            meta = self.service._current_project_metadata
            project_vm = ProjectViewModel.from_metadata(meta) if meta is not None else None

            scenes = self.service.scene_manager.list_scenes()
            shots = self.service.shot_manager.list_shots()
            timelines = self.service.timeline_manager.list_timelines()
            assets = self.service.asset_manager.list_assets()
            characters = self.service.character_manager.list_characters()

            afl_reports = self.service.afl_engine.list_validation_reports()
            export_artifacts = self.service.prompt_export_manager.list_export_artifacts()
            plugins = self.service.plugin_manager.list_plugins()

            app_state = AppStateViewModel(
                project=project_vm,
                workspace=workspace_vm,
                scenes=tuple(SceneViewModel.from_record(s) for s in scenes),
                shots=tuple(ShotViewModel.from_record(s) for s in shots),
                timelines=tuple(TimelineViewModel.from_record(t) for t in timelines),
                assets=tuple(AssetViewModel.from_record(a) for a in assets),
                characters=tuple(CharacterViewModel.from_record(c) for c in characters),
                afl_reports=tuple(AFLReportViewModel.from_record(r) for r in afl_reports),
                export_artifacts=tuple(ExportArtifactViewModel.from_record(e) for e in export_artifacts),
                plugins=tuple(PluginViewModel.from_record(p) for p in plugins),
            )
            return _ok(app_state.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # Workspace selection helpers
    # ------------------------------------------------------------------

    def set_active_scene(self, scene_id: str | None) -> UIActionResult:
        """Set active scene in workspace. Returns UIActionResult."""
        try:
            state = self.service.workspace.set_active_scene(scene_id)
            return _ok({"active_scene_id": state.active_scene_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def set_active_shot(self, shot_id: str | None) -> UIActionResult:
        """Set active shot in workspace. Returns UIActionResult."""
        try:
            state = self.service.workspace.set_active_shot(shot_id)
            return _ok({"active_shot_id": state.active_shot_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # Timeline actions (TASK-000040)
    # ------------------------------------------------------------------

    def create_timeline(self, title: str) -> UIActionResult:
        try:
            pid = self.service._require_active_project()
            record = self.service.timeline_manager.create_timeline(pid, title)
            return _ok({"timeline_id": record.timeline_id, "title": record.title})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def add_timeline_item(
        self,
        timeline_id: str,
        item_type: str,
        target_id: str,
        order_index: int | None = None,
    ) -> UIActionResult:
        try:
            record = self.service.timeline_manager.add_item(
                timeline_id, item_type=item_type, target_id=target_id,
                order_index=order_index,
            )
            items = [
                {"item_id": it.item_id, "item_type": it.item_type,
                 "target_id": it.target_id, "order_index": it.order_index}
                for it in record.items
            ]
            return _ok({"timeline_id": timeline_id, "item_count": len(items), "items": items})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def remove_timeline_item(self, timeline_id: str, item_id: str) -> UIActionResult:
        try:
            record = self.service.timeline_manager.remove_item(timeline_id, item_id)
            return _ok({"timeline_id": timeline_id, "item_count": len(record.items)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def move_timeline_item(
        self, timeline_id: str, item_id: str, order_index: int
    ) -> UIActionResult:
        try:
            record = self.service.timeline_manager.move_item(
                timeline_id, item_id, order_index
            )
            return _ok({"timeline_id": timeline_id, "item_count": len(record.items)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # Asset actions (TASK-000040)
    # ------------------------------------------------------------------

    def import_asset(
        self,
        asset_type: str,
        display_name: str,
        location: str = "",
        owner_ref: str | None = None,
    ) -> UIActionResult:
        try:
            pid = self.service._require_active_project()
            record = self.service.asset_manager.import_asset(
                project_id=pid,
                asset_type=asset_type,
                display_name=display_name,
                location=location,
                owner_ref=owner_ref,
            )
            return _ok({
                "asset_id": record.asset_id,
                "display_name": record.display_name,
                "state": record.state,
            })
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def mark_asset_missing(self, asset_id: str) -> UIActionResult:
        try:
            record = self.service.asset_manager.mark_asset_missing(asset_id)
            return _ok({"asset_id": record.asset_id, "state": record.state})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def archive_asset(self, asset_id: str) -> UIActionResult:
        try:
            record = self.service.asset_manager.archive_asset(asset_id)
            return _ok({"asset_id": record.asset_id, "state": record.state})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # Character actions (TASK-000040)
    # ------------------------------------------------------------------

    def create_character(
        self, display_name: str, description: str = ""
    ) -> UIActionResult:
        try:
            pid = self.service._require_active_project()
            record = self.service.character_manager.create_character(
                project_id=pid,
                display_name=display_name,
                description=description,
            )
            return _ok({
                "character_id": record.character_id,
                "display_name": record.display_name,
            })
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def add_character_reference_asset(
        self, character_id: str, asset_id: str
    ) -> UIActionResult:
        try:
            record = self.service.character_manager.add_reference_asset(
                character_id, asset_id
            )
            return _ok({
                "character_id": record.character_id,
                "reference_asset_ids": list(record.reference_asset_ids),
            })
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def remove_character_reference_asset(
        self, character_id: str, asset_id: str
    ) -> UIActionResult:
        try:
            record = self.service.character_manager.remove_reference_asset(
                character_id, asset_id
            )
            return _ok({
                "character_id": record.character_id,
                "reference_asset_ids": list(record.reference_asset_ids),
            })
        except ValidationError as exc:
                    return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def archive_character(self, character_id: str) -> UIActionResult:
        try:
            record = self.service.character_manager.archive_character(character_id)
            return _ok({"character_id": record.character_id, "state": record.state})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # AFL actions (TASK-000041)
    # ------------------------------------------------------------------

    def validate_afl_structure(
        self, target_ref: str, payload_text: str
    ) -> UIActionResult:
        """Parse payload_text as JSON dict then call afl_engine.validate_structure."""
        import json as _json
        try:
            try:
                payload = _json.loads(payload_text)
            except Exception:
                return _fail("AFL payload is not valid JSON.")
            if not isinstance(payload, dict):
                return _fail("AFL payload must be a JSON object (dict).")
            report = self.service.afl_engine.validate_structure(target_ref, payload)
            return _ok({
                "report_id": report.report_id,
                "target_ref": report.target_ref,
                "status": report.status,
                "issue_count": len(report.issues),
            })
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_afl_reports(self) -> UIActionResult:
        try:
            reports = self.service.afl_engine.list_validation_reports()
            return _ok({
                "reports": [
                    {"report_id": r.report_id, "target_ref": r.target_ref,
                     "status": r.status, "issue_count": len(r.issues)}
                    for r in reports
                ]
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # Export actions (TASK-000041)
    # ------------------------------------------------------------------

    def create_export_artifact(
        self,
        source_id: str,
        artifact_type: str,
        content: str,
        provider_target: str | None = None,
    ) -> UIActionResult:
        try:
            record = self.service.prompt_export_manager.create_export_artifact(
                source_id=source_id,
                artifact_type=artifact_type,
                content=content,
                provider_target=provider_target or None,
            )
            return _ok({
                "artifact_id": record.artifact_id,
                "source_id": record.source_id,
                "artifact_type": record.artifact_type,
                "status": record.status,
            })
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def mark_export_ready(self, artifact_id: str) -> UIActionResult:
        try:
            record = self.service.prompt_export_manager.mark_export_ready(artifact_id)
            return _ok({"artifact_id": record.artifact_id, "status": record.status})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def mark_export_failed(
        self, artifact_id: str, message: str = ""
    ) -> UIActionResult:
        try:
            record = self.service.prompt_export_manager.mark_export_failed(
                artifact_id, message
            )
            return _ok({"artifact_id": record.artifact_id, "status": record.status})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_export_artifacts(self) -> UIActionResult:
        try:
            artifacts = self.service.prompt_export_manager.list_export_artifacts()
            return _ok({
                "artifacts": [
                    {"artifact_id": a.artifact_id, "source_id": a.source_id,
                     "artifact_type": a.artifact_type, "status": a.status}
                    for a in artifacts
                ]
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # Plugin actions (TASK-000041)
    # ------------------------------------------------------------------

    def register_plugin(
        self,
        name: str,
        version: str,
        capabilities_text: str = "",
        permissions_text: str = "",
    ) -> UIActionResult:
        try:
            caps = [c.strip() for c in capabilities_text.split(",") if c.strip()]
            perms = [p.strip() for p in permissions_text.split(",") if p.strip()]
            record = self.service.plugin_manager.register_plugin(
                name=name,
                version=version,
                capabilities=caps or None,
                permissions=perms or None,
            )
            return _ok({
                "plugin_id": record.plugin_id,
                "name": record.name,
                "version": record.version,
                "state": record.state,
            })
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def enable_plugin(self, plugin_id: str) -> UIActionResult:
        try:
            record = self.service.plugin_manager.enable_plugin(plugin_id)
            return _ok({"plugin_id": record.plugin_id, "state": record.state})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def disable_plugin(self, plugin_id: str) -> UIActionResult:
        try:
            record = self.service.plugin_manager.disable_plugin(plugin_id)
            return _ok({"plugin_id": record.plugin_id, "state": record.state})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_plugins(self) -> UIActionResult:
        try:
            plugins = self.service.plugin_manager.list_plugins()
            return _ok({
                "plugins": [
                    {"plugin_id": p.plugin_id, "name": p.name,
                     "version": p.version, "state": p.state}
                    for p in plugins
                ]
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")
