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

    # ------------------------------------------------------------------
    # Scene Detail actions (TASK-000051)
    # ------------------------------------------------------------------

    def get_scene_detail(self, scene_id: str) -> UIActionResult:
        """Return full SceneDetailViewModel for the given scene_id."""
        from aurora_studio.ui.view_models import SceneDetailViewModel
        try:
            record = self.service.scene_manager.get_scene(scene_id)
            return _ok(SceneDetailViewModel.from_record(record).to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def update_scene_detail(self, scene_id: str, fields: dict) -> UIActionResult:
        """Update scene detail fields. Validates and delegates to SceneManager."""
        if not isinstance(fields, dict):
            return _fail("fields must be a dict.")
        if not scene_id or not scene_id.strip():
            return _fail("scene_id must not be empty.")
        from aurora_studio.ui.view_models import SceneDetailViewModel
        try:
            record = self.service.scene_manager.update_scene_details(scene_id, **fields)
            return _ok(SceneDetailViewModel.from_record(record).to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def validate_scene_detail_fields(self, fields: dict) -> UIActionResult:
        """Validate scene detail fields without saving.

        Returns ok=True with a validation summary, or ok=False with an error.
        """
        if not isinstance(fields, dict):
            return _fail("fields must be a dict.")
        if "title" in fields:
            title = fields["title"]
            if title is None or str(title).strip() == "":
                return _fail("title must not be empty.")
        return _ok({"valid": True, "field_count": len(fields)})

    # ------------------------------------------------------------------
    # Shot Detail actions (TASK-000052)
    # ------------------------------------------------------------------

    def get_shot_detail(self, shot_id: str) -> UIActionResult:
        """Return full ShotDetailViewModel for the given shot_id."""
        from aurora_studio.ui.view_models import ShotDetailViewModel
        try:
            record = self.service.shot_manager.get_shot(shot_id)
            return _ok(ShotDetailViewModel.from_record(record).to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def update_shot_detail(self, shot_id: str, fields: dict) -> UIActionResult:
        """Update shot detail fields. Validates and delegates to ShotManager."""
        if not isinstance(fields, dict):
            return _fail("fields must be a dict.")
        if not shot_id or not shot_id.strip():
            return _fail("shot_id must not be empty.")
        from aurora_studio.ui.view_models import ShotDetailViewModel
        try:
            record = self.service.shot_manager.update_shot_details(shot_id, **fields)
            return _ok(ShotDetailViewModel.from_record(record).to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def validate_shot_detail_fields(self, fields: dict) -> UIActionResult:
        """Validate shot detail fields without saving."""
        if not isinstance(fields, dict):
            return _fail("fields must be a dict.")
        if "title" in fields:
            title = fields["title"]
            if title is None or str(title).strip() == "":
                return _fail("title must not be empty.")
        duration = fields.get("duration_seconds")
        if duration is not None:
            try:
                d = float(duration)
            except (TypeError, ValueError):
                return _fail("duration_seconds must be a number.")
            if d < 0:
                return _fail("duration_seconds must not be negative.")
        return _ok({"valid": True, "field_count": len(fields)})

    # ------------------------------------------------------------------
    # Timeline extended actions (TASK-000054/055)
    # ------------------------------------------------------------------

    def move_timeline_item_up(self, timeline_id: str, item_id: str) -> UIActionResult:
        """Move timeline item up (lower order_index)."""
        try:
            record = self.service.timeline_manager.move_item_up(timeline_id, item_id)
            return _ok({"timeline_id": timeline_id, "item_count": len(record.items)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def move_timeline_item_down(self, timeline_id: str, item_id: str) -> UIActionResult:
        """Move timeline item down (higher order_index)."""
        try:
            record = self.service.timeline_manager.move_item_down(timeline_id, item_id)
            return _ok({"timeline_id": timeline_id, "item_count": len(record.items)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_timeline_items(self, timeline_id: str) -> UIActionResult:
        """Return sorted list of timeline items with timeline_id exposed."""
        try:
            items = self.service.timeline_manager.list_items(timeline_id)
            return _ok({
                "timeline_id": timeline_id,
                "items": [
                    {
                        "item_id": it.item_id,
                        "timeline_id": timeline_id,
                        "item_type": it.item_type,
                        "target_id": it.target_id,
                        "order_index": it.order_index,
                    }
                    for it in items
                ]
            })
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def add_scene_to_timeline(self, timeline_id: str, scene_id: str) -> UIActionResult:
        """Add selected scene to timeline as a scene item."""
        if not timeline_id or not timeline_id.strip():
            return _fail("No timeline selected.")
        if not scene_id or not scene_id.strip():
            return _fail("No scene selected.")
        try:
            record = self.service.timeline_manager.add_item(
                timeline_id, item_type="scene", target_id=scene_id
            )
            return _ok({"timeline_id": timeline_id, "item_count": len(record.items)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def add_shot_to_timeline(self, timeline_id: str, shot_id: str) -> UIActionResult:
        """Add selected shot to timeline as a shot item."""
        if not timeline_id or not timeline_id.strip():
            return _fail("No timeline selected.")
        if not shot_id or not shot_id.strip():
            return _fail("No shot selected.")
        try:
            record = self.service.timeline_manager.add_item(
                timeline_id, item_type="shot", target_id=shot_id
            )
            return _ok({"timeline_id": timeline_id, "item_count": len(record.items)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def get_timeline_summary(self, timeline_id: str) -> UIActionResult:
        """Return timeline summary including duration and counts."""
        from aurora_studio.ui.view_models import TimelineSummaryViewModel
        try:
            summary = self.service.timeline_manager.get_timeline_summary(
                timeline_id, shot_manager=self.service.shot_manager
            )
            vm = TimelineSummaryViewModel.from_summary(summary)
            return _ok(vm.to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def normalize_timeline_order(self, timeline_id: str) -> UIActionResult:
        """Normalize timeline item order indexes to be contiguous."""
        try:
            record = self.service.timeline_manager.normalize_timeline_order(timeline_id)
            return _ok({"timeline_id": timeline_id, "item_count": len(record.items)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000056: Asset Browser Pack
    # ------------------------------------------------------------------

    def get_asset_detail(self, asset_id: str) -> UIActionResult:
        """Return full asset detail as AssetDetailViewModel dict."""
        try:
            from aurora_studio.ui.view_models import AssetDetailViewModel
            record = self.service.asset_manager.get_asset(asset_id)
            vm = AssetDetailViewModel.from_record(record)
            return _ok(vm.to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def update_asset_metadata(self, asset_id: str, fields: dict) -> UIActionResult:
        """Update asset metadata fields."""
        try:
            record = self.service.asset_manager.update_asset_metadata(asset_id, **fields)
            return _ok({"asset_id": record.asset_id, "display_name": record.display_name})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def parse_asset_tags(self, tags_text: str) -> UIActionResult:
        """Parse comma-separated tags text into a list."""
        try:
            from aurora_studio.modules.asset_manager import parse_tags
            tags = list(parse_tags(tags_text))
            return _ok({"tags": tags, "count": len(tags)})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def search_assets(
        self, query: str = "", asset_type: str | None = None, state: str | None = None
    ) -> UIActionResult:
        """Search assets by query text, type, and/or state."""
        try:
            records = self.service.asset_manager.list_assets(asset_type=asset_type)
            q = query.strip().lower()
            results = []
            for r in records:
                if state is not None and r.state != state:
                    continue
                if q and q not in r.display_name.lower() and q not in r.asset_type.lower():
                    continue
                results.append({"asset_id": r.asset_id, "display_name": r.display_name,
                                 "asset_type": r.asset_type, "state": r.state})
            return _ok({"results": results, "count": len(results)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000057: Asset Linking Pack
    # ------------------------------------------------------------------

    def link_asset_to_scene(self, asset_id: str, scene_id: str) -> UIActionResult:
        try:
            pid = self.service.get_workspace_state().active_project_id or ""
            link = self.service.asset_link_manager.link(pid, asset_id, "scene", scene_id)
            return _ok({"link_id": link.link_id, "asset_id": asset_id, "target_id": scene_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def unlink_asset_from_scene(self, asset_id: str, scene_id: str) -> UIActionResult:
        try:
            removed = self.service.asset_link_manager.unlink(asset_id, "scene", scene_id)
            return _ok({"removed": removed, "asset_id": asset_id, "target_id": scene_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def link_asset_to_shot(self, asset_id: str, shot_id: str) -> UIActionResult:
        try:
            pid = self.service.get_workspace_state().active_project_id or ""
            link = self.service.asset_link_manager.link(pid, asset_id, "shot", shot_id)
            return _ok({"link_id": link.link_id, "asset_id": asset_id, "target_id": shot_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def unlink_asset_from_shot(self, asset_id: str, shot_id: str) -> UIActionResult:
        try:
            removed = self.service.asset_link_manager.unlink(asset_id, "shot", shot_id)
            return _ok({"removed": removed, "asset_id": asset_id, "target_id": shot_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def link_asset_to_character(self, asset_id: str, character_id: str) -> UIActionResult:
        try:
            pid = self.service.get_workspace_state().active_project_id or ""
            link = self.service.asset_link_manager.link(pid, asset_id, "character", character_id)
            return _ok({"link_id": link.link_id, "asset_id": asset_id, "target_id": character_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def unlink_asset_from_character(self, asset_id: str, character_id: str) -> UIActionResult:
        try:
            removed = self.service.asset_link_manager.unlink(asset_id, "character", character_id)
            return _ok({"removed": removed, "asset_id": asset_id, "target_id": character_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def get_linked_assets(self, target_type: str, target_id: str) -> UIActionResult:
        try:
            links = self.service.asset_link_manager.list_links_for_target(target_type, target_id)
            items = [{"link_id": lnk.link_id, "asset_id": lnk.asset_id,
                      "target_type": lnk.target_type, "target_id": lnk.target_id}
                     for lnk in links]
            return _ok({"links": items, "count": len(items)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000058: Character Detail Editor Pack
    # ------------------------------------------------------------------

    def get_character_detail(self, character_id: str) -> UIActionResult:
        try:
            from aurora_studio.ui.view_models import CharacterDetailViewModel
            record = self.service.character_manager.get_character(character_id)
            vm = CharacterDetailViewModel.from_record(record)
            return _ok(vm.to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def update_character_detail(self, character_id: str, fields: dict) -> UIActionResult:
        try:
            record = self.service.character_manager.update_character_details(character_id, **fields)
            return _ok({"character_id": record.character_id, "display_name": record.display_name})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000059: Character Reference Workflow Pack
    # ------------------------------------------------------------------

    def add_character_reference(
        self, character_id: str, asset_id: str,
        reference_type: str = "other", is_primary: bool = False, notes: str = ""
    ) -> UIActionResult:
        try:
            record = self.service.character_manager.add_reference(
                character_id, asset_id, reference_type, is_primary, notes)
            refs = [r.to_dict() for r in record.reference_assets]
            return _ok({"character_id": record.character_id, "reference_count": len(refs)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def remove_character_reference(
        self, character_id: str, asset_id: str, reference_type: str | None = None
    ) -> UIActionResult:
        try:
            record = self.service.character_manager.remove_reference(
                character_id, asset_id, reference_type)
            return _ok({"character_id": record.character_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def mark_primary_character_reference(
        self, character_id: str, asset_id: str, reference_type: str = "face"
    ) -> UIActionResult:
        try:
            record = self.service.character_manager.mark_primary_reference(
                character_id, asset_id, reference_type)
            return _ok({"character_id": record.character_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000060: AFL Expanded Validation Pack
    # ------------------------------------------------------------------

    def validate_current_project_structure(self) -> UIActionResult:
        """Validate current in-memory project structure."""
        try:
            state = self.service.get_workspace_state()
            pid = state.active_project_id or "project"
            service_state = {
                "project_id": pid,
                "scenes": self.service.scene_manager.list_scenes(),
                "shots": self.service.shot_manager.list_shots(),
                "timelines": self.service.timeline_manager.list_timelines(),
                "characters": self.service.character_manager.list_characters(),
                "assets": self.service.asset_manager.list_assets(),
            }
            report = self.service.afl_engine.validate_project_structure(service_state)
            return _ok({
                "report_id": report.report_id,
                "status": report.status,
                "issue_count": report.issue_count,
                "issues": [i.to_dict() for i in report.issues],
            })
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000061: Prompt Template System
    # ------------------------------------------------------------------

    def create_prompt_template(
        self,
        name: str,
        target_type: str,
        template_text: str,
        description: str = "",
    ) -> UIActionResult:
        """Create a custom prompt template."""
        try:
            ws = self.service.get_workspace_state()
            pid = ws.active_project_id or ""
            record = self.service.prompt_template_manager.create_template(
                name=name,
                target_type=target_type,
                template_text=template_text,
                description=description,
                project_id=pid,
            )
            return _ok({"template_id": record.template_id, "name": record.name})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_prompt_templates(self, target_type: str | None = None) -> UIActionResult:
        """List available prompt templates (defaults + custom)."""
        try:
            records = self.service.prompt_template_manager.list_templates(
                target_type=target_type
            )
            return _ok({
                "count": len(records),
                "templates": [r.to_dict() for r in records],
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def render_prompt_template(
        self, template_id: str, source_type: str, source_id: str
    ) -> UIActionResult:
        """Render a stored template with context from the project state."""
        try:
            context = self._build_render_context(source_type, source_id)
            text = self.service.prompt_template_manager.render_template(
                template_id, context
            )
            return _ok({"rendered_text": text, "template_id": template_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def render_prompt_template_text(
        self, template_text: str, source_type: str, source_id: str
    ) -> UIActionResult:
        """Render arbitrary template text with context from the project state."""
        try:
            context = self._build_render_context(source_type, source_id)
            text = self.service.prompt_template_manager.render_template_text(
                template_text, context
            )
            return _ok({"rendered_text": text})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def _build_render_context(self, source_type: str, source_id: str) -> dict:
        """Build a flat context dict from current project state for template rendering.

        Raises ValidationError if the requested source is not found.
        """
        svc = self.service
        context: dict = {}

        # Project context
        meta = svc._current_project_metadata
        if meta is not None:
            context["project.title"] = meta.title
            context["project.id"] = meta.project_id

        st = source_type.strip().lower()
        sid = source_id.strip()

        if st == "scene":
            scene = svc.scene_manager.get_scene(sid)
            context.update({
                "scene.title": scene.title,
                "scene.description": getattr(scene, "description", ""),
                "scene.location": getattr(scene, "location", ""),
                "scene.time_of_day": getattr(scene, "time_of_day", ""),
                "scene.mood": getattr(scene, "mood", ""),
                "scene.conflict": getattr(scene, "conflict", ""),
                "scene.narrative_beat": getattr(scene, "narrative_beat", ""),
                "scene.notes": getattr(scene, "notes", ""),
            })
        elif st == "shot":
            shot = svc.shot_manager.get_shot(sid)
            context.update({
                "shot.title": shot.title,
                "shot.description": getattr(shot, "description", ""),
                "shot.shot_type": getattr(shot, "shot_type", ""),
                "shot.camera_angle": getattr(shot, "camera_angle", ""),
                "shot.camera_movement": getattr(shot, "camera_movement", ""),
                "shot.framing": getattr(shot, "framing", ""),
                "shot.lens": getattr(shot, "lens", ""),
                "shot.emotion_target": getattr(shot, "emotion_target", ""),
                "shot.visual_focus": getattr(shot, "visual_focus", ""),
            })
        elif st == "character":
            char = svc.character_manager.get_character(sid)
            context.update({
                "character.display_name": char.display_name,
                "character.description": getattr(char, "description", ""),
                "character.role": getattr(char, "role", ""),
                "character.visual_description": getattr(char, "visual_description", ""),
                "character.personality": getattr(char, "personality", ""),
                "character.motivation": getattr(char, "motivation", ""),
            })
        elif st == "asset":
            asset = svc.asset_manager.get_asset(sid)
            context.update({
                "asset.display_name": asset.display_name,
                "asset.asset_type": asset.asset_type,
                "asset.description": getattr(asset, "description", ""),
                "asset.notes": getattr(asset, "notes", ""),
            })
        elif st == "project":
            pass  # project context already set above
        else:
            raise ValidationError(f"Unknown source_type: {source_type!r}")

        return context

    # ------------------------------------------------------------------
    # TASK-000061: Bundle/file helpers
    # ------------------------------------------------------------------

    def validate_bundle_file(self, path: str) -> UIActionResult:
        """Validate a bundle file on disk without loading it."""
        try:
            report = self.service.project_store.validate_bundle_file(path)
            return _ok(report) if report["ok"] else _fail(
                "; ".join(report["errors"]), report
            )
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def export_bundle_copy(self, destination: str) -> UIActionResult:
        """Copy current project bundle to a destination file."""
        try:
            ws = self.service.get_workspace_state()
            pid = ws.active_project_id
            if not pid:
                return _fail("No active project.")
            # We need the current project path — save to tmp then copy
            import tempfile, pathlib
            with tempfile.TemporaryDirectory() as tmp:
                src = self.service.save_bundle(tmp)
                dst = self.service.project_store.export_bundle_copy(src, destination)
            return _ok({"destination": str(dst)})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def import_bundle_copy(self, source: str) -> UIActionResult:
        """Import a bundle copy from a source file into current project."""
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                bundle = self.service.project_store.import_bundle_copy(source, tmp)
                # rehydrate into current service
                from aurora_studio.persistence.rehydration import BundleRehydrator
                rehydrator = BundleRehydrator()
                summary = rehydrator.rehydrate(
                    bundle,
                    scene_manager=self.service.scene_manager,
                    shot_manager=self.service.shot_manager,
                    timeline_manager=self.service.timeline_manager,
                    asset_manager=self.service.asset_manager,
                    character_manager=self.service.character_manager,
                    prompt_export_manager=self.service.prompt_export_manager,
                    plugin_manager=self.service.plugin_manager,
                    asset_link_manager=self.service.asset_link_manager,
                    prompt_template_manager=self.service.prompt_template_manager,
                )
            return _ok({"imported": True, "summary": summary})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000062: Prompt Export Preview
    # ------------------------------------------------------------------

    def render_prompt_preview(
        self, template_id: str, source_type: str, source_id: str
    ) -> "UIActionResult":
        """Render a prompt template preview without saving as export artifact."""
        try:
            ctx = self._build_render_context(source_type, source_id)
            rendered = self.service.prompt_template_manager.render_template(
                template_id, ctx
            )
            return _ok({"rendered_text": rendered, "template_id": template_id,
                        "source_type": source_type, "source_id": source_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def save_prompt_preview_as_export(
        self,
        template_id: str,
        source_type: str,
        source_id: str,
        artifact_type: str = "prompt",
        provider_target: str | None = None,
    ) -> "UIActionResult":
        """Render a prompt and save it as an export artifact."""
        try:
            ctx = self._build_render_context(source_type, source_id)
            rendered = self.service.prompt_template_manager.render_template(
                template_id, ctx
            )
            project_id = ""
            if self.service._current_project_metadata is not None:
                project_id = getattr(
                    self.service._current_project_metadata, "project_id", ""
                )
            artifact = self.service.prompt_export_manager.create_export_artifact(
                source_id=source_id,
                artifact_type=artifact_type,
                content=rendered,
                provider_target=provider_target,
                project_id=project_id,
                source_type=source_type,
                template_id=template_id,
            )
            return _ok({"artifact": artifact.to_dict(), "rendered_text": artifact.content})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000063: Export Profiles
    # ------------------------------------------------------------------

    def list_export_profiles(self, target_type: str | None = None) -> "UIActionResult":
        """List export profiles, optionally filtered by target_type."""
        try:
            profiles = self.service.export_profile_manager.list_profiles(
                target_type=target_type or None
            )
            return _ok({"profiles": [p.to_dict() for p in profiles]})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def render_export_profile(
        self, profile_id: str, source_type: str, source_id: str
    ) -> "UIActionResult":
        """Render an export profile for a source object."""
        try:
            ctx = self._build_render_context(source_type, source_id)
            rendered = self.service.export_profile_manager.render_with_profile(
                profile_id, ctx,
                prompt_template_manager=self.service.prompt_template_manager,
            )
            return _ok({"rendered_text": rendered, "profile_id": profile_id,
                        "source_type": source_type, "source_id": source_id})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def save_profile_render_as_export(
        self,
        profile_id: str,
        source_type: str,
        source_id: str,
        artifact_type: str = "prompt",
        provider_target: str | None = None,
    ) -> "UIActionResult":
        """Render an export profile and save it as an export artifact."""
        try:
            ctx = self._build_render_context(source_type, source_id)
            rendered = self.service.export_profile_manager.render_with_profile(
                profile_id, ctx,
                prompt_template_manager=self.service.prompt_template_manager,
            )
            project_id = ""
            if self.service._current_project_metadata is not None:
                project_id = getattr(
                    self.service._current_project_metadata, "project_id", ""
                )
            artifact = self.service.prompt_export_manager.create_export_artifact(
                source_id=source_id,
                artifact_type=artifact_type,
                content=rendered,
                provider_target=provider_target,
                project_id=project_id,
                source_type=source_type,
                profile_id=profile_id,
            )
            return _ok({"artifact": artifact.to_dict(), "rendered_text": artifact.content})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000064: Project Search and Filters
    # ------------------------------------------------------------------

    def search_scenes(
        self, query: str = "", status: str | None = None
    ) -> "UIActionResult":
        try:
            q = query.lower()
            results = self.service.scene_manager.list_scenes()
            if q:
                results = [
                    r for r in results
                    if q in r.title.lower() or q in getattr(r, "description", "").lower()
                ]
            if status is not None:
                results = [r for r in results if r.state == status]
            return _ok({"scenes": [r.to_dict() for r in results]})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def search_shots(
        self, query: str = "", scene_id: str | None = None, status: str | None = None
    ) -> "UIActionResult":
        try:
            q = query.lower()
            results = self.service.shot_manager.list_shots()
            if q:
                results = [
                    r for r in results
                    if q in r.title.lower() or q in getattr(r, "description", "").lower()
                ]
            if scene_id is not None:
                results = [r for r in results if r.scene_id == scene_id]
            if status is not None:
                results = [r for r in results if r.state == status]
            return _ok({"shots": [r.to_dict() for r in results]})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def search_assets(
        self,
        query: str = "",
        asset_type: str | None = None,
        state: str | None = None,
        tag: str | None = None,
    ) -> "UIActionResult":
        try:
            q = query.lower()
            results = self.service.asset_manager.list_assets()
            if q:
                results = [
                    r for r in results
                    if q in r.display_name.lower()
                    or q in getattr(r, "description", "").lower()
                ]
            if asset_type is not None:
                results = [r for r in results if r.asset_type == asset_type]
            if state is not None:
                results = [r for r in results if r.state == state]
            if tag is not None:
                tl = tag.lower()
                results = [
                    r for r in results
                    if any(tl == t.lower() for t in getattr(r, "tags", ()))
                ]
            return _ok({"assets": [r.to_dict() for r in results]})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def search_characters(
        self, query: str = "", role: str | None = None, status: str | None = None
    ) -> "UIActionResult":
        try:
            q = query.lower()
            results = self.service.character_manager.list_characters()
            if q:
                results = [
                    r for r in results
                    if q in r.display_name.lower()
                    or q in getattr(r, "description", "").lower()
                ]
            if role is not None:
                results = [r for r in results if getattr(r, "role", "") == role]
            if status is not None:
                results = [r for r in results if r.state == status]
            return _ok({"characters": [r.to_dict() for r in results]})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def search_exports(
        self,
        query: str = "",
        artifact_type: str | None = None,
        status: str | None = None,
        source_type: str | None = None,
    ) -> "UIActionResult":
        try:
            q = query.lower()
            results = self.service.prompt_export_manager.list_export_artifacts()
            if q:
                results = [
                    r for r in results
                    if q in r.content.lower() or q in r.artifact_type.lower()
                ]
            if artifact_type is not None:
                results = [r for r in results if r.artifact_type == artifact_type]
            if status is not None:
                results = [r for r in results if r.status == status]
            if source_type is not None:
                results = [
                    r for r in results
                    if getattr(r, "source_type", "") == source_type
                ]
            return _ok({"exports": [r.to_dict() for r in results]})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def search_plugins(
        self, query: str = "", state: str | None = None
    ) -> "UIActionResult":
        try:
            q = query.lower()
            results = self.service.plugin_manager.list_plugins()
            if q:
                results = [r for r in results if q in r.name.lower()]
            if state is not None:
                results = [r for r in results if getattr(r, "state", "") == state]
            return _ok({"plugins": [r.to_dict() for r in results]})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000077: Provider Registry
    # ------------------------------------------------------------------

    def list_providers(
        self, provider_type: str | None = None, state: str | None = None
    ) -> "UIActionResult":
        try:
            providers = self.service.provider_registry.list_providers(
                provider_type=provider_type or None,
                state=state or None,
            )
            from aurora_studio.ui.view_models import ProviderViewModel
            return _ok({"providers": [ProviderViewModel.from_record(p).to_dict() for p in providers]})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def get_provider(self, provider_id: str) -> "UIActionResult":
        try:
            defn = self.service.provider_registry.get_provider(provider_id)
            from aurora_studio.ui.view_models import ProviderViewModel
            return _ok({"provider": ProviderViewModel.from_record(defn).to_dict()})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def enable_provider(self, provider_id: str) -> "UIActionResult":
        try:
            defn = self.service.provider_registry.enable_provider(provider_id)
            return _ok({"provider_id": defn.provider_id, "state": defn.state})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def disable_provider(self, provider_id: str) -> "UIActionResult":
        try:
            defn = self.service.provider_registry.disable_provider(provider_id)
            return _ok({"provider_id": defn.provider_id, "state": defn.state})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000079: Provider Dry-Run Adapter
    # ------------------------------------------------------------------

    def execute_provider_dry_run(
        self,
        provider_id: str,
        source_type: str,
        source_id: str,
        prompt_text: str,
        profile_id: str = "",
        template_id: str = "",
    ) -> "UIActionResult":
        try:
            from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
            pid = (provider_id or "").strip() or "dry-run-local"
            defn = self.service.provider_registry.get_provider(pid)
            if defn.state == "disabled":
                return _fail(f"Provider {pid!r} is disabled.")
            if not defn.supports_dry_run:
                return _fail(f"Provider {pid!r} does not support dry-run.")
            adapter = ProviderDryRunAdapter(provider_id=pid)
            request = ProviderDryRunAdapter.build_request(
                provider_id=pid,
                source_type=(source_type or "").strip(),
                source_id=(source_id or "").strip(),
                prompt_text=(prompt_text or "").strip(),
                profile_id=(profile_id or "").strip(),
                template_id=(template_id or "").strip(),
            )
            response = adapter.execute(request)
            self.service.provider_log.record(request, response, event_type="dry_run_completed")
            self.service.prompt_run_history.record_dry_run(request, response)
            return _ok({
                "request_id": response.request_id,
                "response_id": response.response_id,
                "provider_id": response.provider_id,
                "status": response.status,
                "output_text": response.output_text,
            })
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000080: Provider Request/Response Log
    # ------------------------------------------------------------------

    def list_provider_logs(
        self,
        provider_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> "UIActionResult":
        try:
            entries = self.service.provider_log.list_entries(
                provider_id=provider_id or None,
                status=status or None,
                limit=limit,
            )
            return _ok({"logs": [e.to_dict() for e in entries], "count": len(entries)})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def clear_provider_logs(self) -> "UIActionResult":
        try:
            count = self.service.provider_log.clear()
            return _ok({"cleared": count})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000081: Prompt Execution Queue
    # ------------------------------------------------------------------

    def enqueue_prompt_execution(
        self,
        provider_id: str,
        source_type: str,
        source_id: str,
        prompt_text: str,
        profile_id: str = "",
        template_id: str = "",
        parameters: dict | None = None,
        priority: int = 0,
    ) -> "UIActionResult":
        try:
            import uuid
            from datetime import datetime, timezone
            from aurora_studio.contracts.prompt_execution import PromptExecutionRequest
            if not (provider_id or "").strip():
                return _fail("provider_id must not be empty.")
            if not (source_type or "").strip():
                return _fail("source_type must not be empty.")
            if not (prompt_text or "").strip():
                return _fail("prompt_text must not be empty.")
            # Validate provider exists
            try:
                self.service.provider_registry.get_provider(provider_id.strip())
            except ValidationError as exc:
                return _fail(str(exc))
            request = PromptExecutionRequest(
                request_id=f"req-{uuid.uuid4().hex[:12]}",
                project_id="",
                provider_id=provider_id.strip(),
                source_type=source_type.strip(),
                source_id=(source_id or "").strip(),
                prompt_text=prompt_text.strip(),
                profile_id=(profile_id or "").strip(),
                template_id=(template_id or "").strip(),
                parameters=dict(parameters or {}),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            item = self.service.prompt_execution_queue.enqueue_request(request, priority=priority)
            from aurora_studio.ui.view_models import PromptExecutionQueueItemViewModel
            return _ok({"item": PromptExecutionQueueItemViewModel.from_record(item).to_dict()})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_prompt_execution_queue(
        self,
        status: str | None = None,
        provider_id: str | None = None,
        source_type: str | None = None,
    ) -> "UIActionResult":
        try:
            items = self.service.prompt_execution_queue.list_items(
                status=status or None,
                provider_id=provider_id or None,
                source_type=source_type or None,
            )
            queue_status = self.service.prompt_execution_queue.queue_status()
            from aurora_studio.ui.view_models import PromptExecutionQueueItemViewModel
            return _ok({
                "items": [PromptExecutionQueueItemViewModel.from_record(i).to_dict() for i in items],
                "status": queue_status.to_dict(),
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def cancel_prompt_execution(self, queue_item_id: str) -> "UIActionResult":
        try:
            item = self.service.prompt_execution_queue.cancel_item(queue_item_id)
            return _ok({"queue_item_id": item.queue_item_id, "status": item.status})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def run_next_prompt_execution_dry_run(self) -> "UIActionResult":
        try:
            from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
            adapter = ProviderDryRunAdapter()
            result = self.service.prompt_execution_queue.execute_next_with_dry_run(adapter)
            if result is None:
                return _ok({"ran": False, "message": "No queued items."})
            return _ok({"ran": True, **result})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000082: Batch Prompt Export
    # ------------------------------------------------------------------

    def create_batch_prompt_export(
        self,
        source_type: str,
        source_ids: list[str] | str,
        template_id: str = "",
        profile_id: str = "",
        artifact_type: str = "prompt",
        provider_target: str = "",
    ) -> "UIActionResult":
        try:
            import uuid
            from datetime import datetime, timezone
            from aurora_studio.contracts.prompt_execution import BatchPromptExportRequest

            # Accept comma-separated string or list
            if isinstance(source_ids, str):
                ids = [s.strip() for s in source_ids.split(",") if s.strip()]
            else:
                ids = [s.strip() for s in source_ids if s.strip()]

            if not ids:
                return _fail("source_ids must not be empty.")
            if not (source_type or "").strip():
                return _fail("source_type must not be empty.")
            if not (template_id or "").strip() and not (profile_id or "").strip():
                return _fail("Either template_id or profile_id must be provided.")

            request = BatchPromptExportRequest(
                batch_id=f"batch-{uuid.uuid4().hex[:12]}",
                project_id="",
                source_type=source_type.strip(),
                source_ids=tuple(ids),
                template_id=(template_id or "").strip(),
                profile_id=(profile_id or "").strip(),
                artifact_type=(artifact_type or "prompt").strip(),
                provider_target=(provider_target or "").strip(),
                created_at=datetime.now(timezone.utc).isoformat(),
            )

            result = self.service.batch_prompt_export_manager.create_export_artifacts_for_batch(
                request=request,
                export_manager=self.service.prompt_export_manager,
                template_manager=self.service.prompt_template_manager,
                profile_manager=self.service.export_profile_manager,
            )

            return _ok(result.to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000083: Prompt Run History
    # ------------------------------------------------------------------

    def list_prompt_run_history(
        self,
        run_type: str | None = None,
        status: str | None = None,
        provider_id: str | None = None,
        source_type: str | None = None,
    ) -> "UIActionResult":
        try:
            records = self.service.prompt_run_history.list_history(
                run_type=run_type or None,
                status=status or None,
                provider_id=provider_id or None,
                source_type=source_type or None,
            )
            return _ok({"history": [r.to_dict() for r in records], "count": len(records)})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def clear_prompt_run_history(self) -> "UIActionResult":
        try:
            count = self.service.prompt_run_history.clear_history()
            return _ok({"cleared": count})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000086: Plugin Manifest Validation
    # ------------------------------------------------------------------

    def validate_plugin_manifest(self, manifest_text: str) -> "UIActionResult":
        try:
            import json as _json
            try:
                data = _json.loads(manifest_text)
            except Exception:
                return _fail("Invalid JSON: manifest_text must be a valid JSON object.")
            if not isinstance(data, dict):
                return _fail("Manifest must be a JSON object.")
            report = self.service.plugin_manager.validate_plugin_manifest(data)
            return _ok(report.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def register_plugin_manifest(self, manifest_text: str) -> "UIActionResult":
        try:
            import json as _json
            try:
                data = _json.loads(manifest_text)
            except Exception:
                return _fail("Invalid JSON: manifest_text must be a valid JSON object.")
            if not isinstance(data, dict):
                return _fail("Manifest must be a JSON object.")
            manifest = self.service.plugin_manager.register_manifest_dict(data)
            return _ok({"plugin_id": manifest.plugin_id, "state": manifest.state})
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_plugin_manifests(self) -> "UIActionResult":
        try:
            manifests = self.service.plugin_manager.list_plugin_manifests()
            return _ok({"manifests": [m.to_dict() for m in manifests], "count": len(manifests)})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000087: Plugin Permission Model
    # ------------------------------------------------------------------

    def list_plugin_permissions(self) -> "UIActionResult":
        try:
            from aurora_studio.modules.plugin_permission_model import PluginPermissionModel
            model = PluginPermissionModel()
            perms = model.list_known_permissions()
            return _ok({"permissions": [p.to_dict() for p in perms], "count": len(perms)})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def evaluate_plugin_permissions(self, permission_names: list) -> "UIActionResult":
        try:
            from aurora_studio.modules.plugin_permission_model import PluginPermissionModel
            model = PluginPermissionModel()
            if not isinstance(permission_names, list):
                return _fail("permission_names must be a list.")
            decisions = model.evaluate_requested_permissions(permission_names)
            return _ok({"decisions": [d.to_dict() for d in decisions], "count": len(decisions)})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def get_plugin_permission_summary(self, permission_names: list) -> "UIActionResult":
        try:
            from aurora_studio.modules.plugin_permission_model import PluginPermissionModel
            model = PluginPermissionModel()
            if not isinstance(permission_names, list):
                return _fail("permission_names must be a list.")
            decisions = model.evaluate_requested_permissions(permission_names)
            allowed = [d.permission for d in decisions if d.decision == "allowed"]
            denied = [d.permission for d in decisions if d.decision == "denied"]
            requires_approval = [d.permission for d in decisions if d.decision == "requires_approval"]
            not_supported = [d.permission for d in decisions if d.decision == "not_supported"]
            return _ok({
                "allowed": allowed,
                "denied": denied,
                "requires_approval": requires_approval,
                "not_supported": not_supported,
                "all_allowed": len(denied) == 0 and len(not_supported) == 0 and len(requires_approval) == 0,
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000088: Plugin Sandbox Policy
    # ------------------------------------------------------------------

    def get_plugin_sandbox_policy(self, plugin_id: str = "") -> "UIActionResult":
        try:
            from aurora_studio.modules.plugin_sandbox import PluginSandbox
            sandbox = PluginSandbox()
            result = sandbox.get_policy(plugin_id=plugin_id)
            return _ok(result.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def is_plugin_execution_allowed(self, plugin_id: str = "") -> "UIActionResult":
        try:
            from aurora_studio.modules.plugin_sandbox import PluginSandbox
            sandbox = PluginSandbox()
            allowed = sandbox.is_execution_allowed(plugin_id=plugin_id)
            return _ok({"allowed": allowed, "plugin_id": plugin_id})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000089: Plugin Runtime Stub
    # ------------------------------------------------------------------

    def execute_plugin_stub(self, plugin_id: str, action: str = "", payload: str = "") -> "UIActionResult":
        try:
            result = self.service.plugin_manager.execute_plugin_stub(
                plugin_id=plugin_id, action=action, payload=payload
            )
            return _ok(result.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000092: Asset media metadata
    # ------------------------------------------------------------------

    def update_asset_media_metadata(self, asset_id: str, fields: dict) -> "UIActionResult":
        try:
            record = self.service.asset_manager.update_media_reference_metadata(asset_id, **fields)
            return _ok(record.to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except ValueError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def set_asset_preview_status(self, asset_id: str, preview_status: str, preview_error: str = "") -> "UIActionResult":
        try:
            record = self.service.asset_manager.set_preview_status(asset_id, preview_status, preview_error)
            return _ok(record.to_dict())
        except ValidationError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000093: Project Backup / Recovery
    # ------------------------------------------------------------------

    def create_project_backup(self, project_path: str = "", reason: str = "manual") -> "UIActionResult":
        try:
            from aurora_studio.modules.project_backup import ProjectBackupManager
            if not project_path:
                return _fail("project_path is required.")
            mgr = ProjectBackupManager()
            record = mgr.create_backup(project_path, reason=reason)
            return _ok(record.to_dict())
        except FileNotFoundError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_project_backups(self, project_path: str = "") -> "UIActionResult":
        try:
            from aurora_studio.modules.project_backup import ProjectBackupManager
            if not project_path:
                return _fail("project_path is required.")
            mgr = ProjectBackupManager()
            records = mgr.list_backups(project_path)
            return _ok({"backups": [r.to_dict() for r in records], "count": len(records)})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def scan_project_recovery(self, project_path: str = "") -> "UIActionResult":
        try:
            from aurora_studio.modules.project_recovery import ProjectRecoveryManager
            if not project_path:
                return _fail("project_path is required.")
            mgr = ProjectRecoveryManager()
            report = mgr.build_recovery_report(project_path)
            return _ok(report.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def restore_project_backup(self, project_path: str = "", backup_path: str = "") -> "UIActionResult":
        try:
            from aurora_studio.modules.project_recovery import ProjectRecoveryManager
            if not project_path or not backup_path:
                return _fail("project_path and backup_path are required.")
            mgr = ProjectRecoveryManager()
            restored = mgr.restore_backup(project_path, backup_path)
            return _ok({"restored_path": restored})
        except ValueError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000094: Autosave
    # ------------------------------------------------------------------

    def enable_autosave(self, project_path: str = "") -> "UIActionResult":
        try:
            from aurora_studio.modules.autosave_manager import AutosaveManager
            if not hasattr(self.service, '_autosave_manager') or self.service._autosave_manager is None:
                self.service._autosave_manager = AutosaveManager()
            state = self.service._autosave_manager.enable_autosave(project_path or ".")
            return _ok(state.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def disable_autosave(self) -> "UIActionResult":
        try:
            if not hasattr(self.service, '_autosave_manager') or self.service._autosave_manager is None:
                from aurora_studio.modules.autosave_manager import AutosaveManager
                self.service._autosave_manager = AutosaveManager()
            state = self.service._autosave_manager.disable_autosave()
            return _ok(state.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def mark_project_dirty(self, reason: str = "") -> "UIActionResult":
        try:
            if not hasattr(self.service, '_autosave_manager') or self.service._autosave_manager is None:
                from aurora_studio.modules.autosave_manager import AutosaveManager
                self.service._autosave_manager = AutosaveManager()
            state = self.service._autosave_manager.mark_dirty(reason=reason)
            return _ok(state.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def write_project_autosave(self, project_path: str = "") -> "UIActionResult":
        try:
            if not hasattr(self.service, '_autosave_manager') or self.service._autosave_manager is None:
                from aurora_studio.modules.autosave_manager import AutosaveManager
                self.service._autosave_manager = AutosaveManager()
            bundle_data = {"schema_version": "0.3", "autosave": True}
            record = self.service._autosave_manager.write_autosave(bundle_data, project_path or ".")
            return _ok(record.to_dict())
        except ValueError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def check_autosave_recovery(self, project_path: str = "") -> "UIActionResult":
        try:
            if not hasattr(self.service, '_autosave_manager') or self.service._autosave_manager is None:
                from aurora_studio.modules.autosave_manager import AutosaveManager
                self.service._autosave_manager = AutosaveManager()
            report = self.service._autosave_manager.build_recovery_report(project_path or ".")
            return _ok(report.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def load_autosave_recovery(self, project_path: str = "") -> "UIActionResult":
        try:
            if not hasattr(self.service, '_autosave_manager') or self.service._autosave_manager is None:
                from aurora_studio.modules.autosave_manager import AutosaveManager
                self.service._autosave_manager = AutosaveManager()
            data = self.service._autosave_manager.load_autosave(project_path or ".")
            return _ok({"loaded": True, "keys": list(data.keys())})
        except FileNotFoundError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def discard_autosave_recovery(self, project_path: str = "") -> "UIActionResult":
        try:
            if not hasattr(self.service, '_autosave_manager') or self.service._autosave_manager is None:
                from aurora_studio.modules.autosave_manager import AutosaveManager
                self.service._autosave_manager = AutosaveManager()
            discarded = self.service._autosave_manager.discard_autosave(project_path or ".")
            return _ok({"discarded": discarded})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def get_autosave_state(self, project_path: str = "") -> "UIActionResult":
        try:
            if not hasattr(self.service, '_autosave_manager') or self.service._autosave_manager is None:
                from aurora_studio.modules.autosave_manager import AutosaveManager
                self.service._autosave_manager = AutosaveManager()
            state = self.service._autosave_manager.get_state()
            return _ok(state.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000095: Undo/Redo Command Stack
    # ------------------------------------------------------------------

    def _get_command_stack(self):
        if not hasattr(self.service, '_command_stack') or self.service._command_stack is None:
            from aurora_studio.modules.command_stack import CommandStack
            self.service._command_stack = CommandStack()
        return self.service._command_stack

    def undo_last_action(self) -> "UIActionResult":
        try:
            result = self._get_command_stack().undo()
            return _ok(result.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def redo_last_action(self) -> "UIActionResult":
        try:
            result = self._get_command_stack().redo()
            return _ok(result.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def get_command_stack_state(self) -> "UIActionResult":
        try:
            state = self._get_command_stack().get_state()
            return _ok(state.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000101: Provider Execution Gate
    # ------------------------------------------------------------------

    def evaluate_provider_execution_gate(
        self, provider_id: str, requested_action: str, mode: str = "dry_run",
        config: dict | None = None,
    ) -> "UIActionResult":
        """Evaluate execution gate for a provider in the given mode.

        Dry-run and mock are allowed without prerequisites.
        Real text execution requires all prerequisites in config.
        """
        try:
            from aurora_studio.modules.provider_execution_gate import ProviderExecutionGate
            gate = ProviderExecutionGate()
            decision = gate.evaluate_execution(
                provider_id, requested_action, mode=mode, config=config
            )
            return _ok(decision.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000102: User API Key Entry Boundary
    # ------------------------------------------------------------------

    def preview_provider_key_entry(
        self, provider_id: str, secret_value: str
    ) -> "UIActionResult":
        """Preview a redacted API key entry — never stores the real key."""
        try:
            from aurora_studio.modules.provider_secret_redaction import redact_secret
            from aurora_studio.contracts.provider_config import ProviderKeyEntryState
            import dataclasses
            if not provider_id:
                return _fail("provider_id is required")
            redacted = redact_secret(secret_value)
            has_input = bool(secret_value.strip()) if isinstance(secret_value, str) else False
            status = "entered_not_saved" if has_input else "empty"
            state = ProviderKeyEntryState(
                provider_id=provider_id,
                has_user_input=has_input,
                redacted_value=redacted,
                status=status,
                message="Not saved. Storage not configured. Real provider calls disabled.",
            )
            return _ok(state.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def clear_provider_key_entry(self, provider_id: str) -> "UIActionResult":
        """Clear the API key entry for a provider — returns safe cleared state."""
        try:
            from aurora_studio.contracts.provider_config import ProviderKeyEntryState
            if not provider_id:
                return _fail("provider_id is required")
            state = ProviderKeyEntryState(
                provider_id=provider_id,
                has_user_input=False,
                redacted_value="",
                status="cleared",
                message="Key entry cleared. Storage not configured. Real provider calls disabled.",
            )
            return _ok(state.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def sanitize_provider_config_payload(self, payload: dict) -> "UIActionResult":
        """Sanitize a provider config payload, removing key-like fields."""
        try:
            from aurora_studio.modules.provider_secret_redaction import sanitize_provider_config_payload
            safe = sanitize_provider_config_payload(payload)
            return _ok({"sanitized": safe})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000104: Provider Config UI Hardening
    # ------------------------------------------------------------------

    def _get_provider_config_manager(self):
        if not hasattr(self.service, '_provider_config_manager') or \
                self.service._provider_config_manager is None:
            from aurora_studio.modules.provider_config_manager import ProviderConfigManager
            self.service._provider_config_manager = ProviderConfigManager()
        return self.service._provider_config_manager

    def get_provider_config_ui_state(self, provider_id: str) -> "UIActionResult":
        """Get the UI-safe config state for a provider."""
        try:
            from aurora_studio.ui.view_models import ProviderConfigViewModel
            mgr = self._get_provider_config_manager()
            record = mgr.get_provider_config_metadata(provider_id)
            if record is None:
                # Return a default not_configured state
                vm = ProviderConfigViewModel(
                    provider_id=provider_id,
                    config_status="not_configured",
                    notes="Not saved. Storage not configured. Real provider calls disabled.",
                )
            else:
                vm = ProviderConfigViewModel.from_record(record)
            return _ok(vm.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_provider_config_ui_states(self) -> "UIActionResult":
        """List all provider config UI states."""
        try:
            from aurora_studio.ui.view_models import ProviderConfigViewModel
            mgr = self._get_provider_config_manager()
            records = mgr.list_provider_config_metadata()
            vms = [ProviderConfigViewModel.from_record(r).to_dict() for r in records]
            return _ok({"providers": vms})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def update_provider_config_metadata(
        self, provider_id: str, fields: dict
    ) -> "UIActionResult":
        """Update provider config metadata (non-secret fields only)."""
        try:
            mgr = self._get_provider_config_manager()
            updated = mgr.set_provider_config_metadata(provider_id, **fields)
            return _ok(updated)
        except ValueError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def set_provider_enabled(self, provider_id: str, enabled: bool) -> "UIActionResult":
        """Enable or disable a provider."""
        try:
            mgr = self._get_provider_config_manager()
            updated = mgr.set_provider_enabled(provider_id, enabled)
            return _ok(updated)
        except ValueError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def set_provider_secret_storage_status(
        self, provider_id: str, status: str
    ) -> "UIActionResult":
        """Set the secret storage status for a provider."""
        try:
            mgr = self._get_provider_config_manager()
            updated = mgr.set_secret_storage_status(provider_id, status)
            return _ok(updated)
        except ValueError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def request_real_execution_enable(self, provider_id: str) -> "UIActionResult":
        """Request real execution enable — always returns blocked in v0.4."""
        try:
            return _fail(
                "Real provider execution cannot be enabled in v0.4. "
                "Prerequisites not met: no OS keyring, no provider adapter, no user consent. "
                "Deferred to TASK-000106+."
            )
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000105: Provider Test Connection Dry/Mock
    # ------------------------------------------------------------------

    def test_provider_connection(
        self, provider_id: str, mode: str = "dry_run"
    ) -> "UIActionResult":
        """Test provider connection — dry/mock only in v0.4. No network."""
        try:
            from aurora_studio.modules.provider_test_connection import (
                ProviderTestConnectionManager,
            )
            if not provider_id:
                return _fail("provider_id is required")
            from aurora_studio.contracts.provider import TEST_CONNECTION_MODES
            if mode not in TEST_CONNECTION_MODES:
                return _fail(
                    f"Invalid mode '{mode}'. Allowed: {sorted(TEST_CONNECTION_MODES)}"
                )
            mgr = ProviderTestConnectionManager()
            result = mgr.test_connection(provider_id, mode)
            return _ok(result.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000106: Extended Execution Gate
    # ------------------------------------------------------------------

    def list_real_text_provider_prerequisites(self) -> "UIActionResult":
        """List all prerequisites required for real text provider execution."""
        try:
            from aurora_studio.modules.provider_execution_gate import ProviderExecutionGate
            gate = ProviderExecutionGate()
            prereqs = gate.list_real_text_prerequisites()
            return _ok({"prerequisites": [p.to_dict() for p in prereqs]})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000108: Text Provider Execution (mock / blocked-real)
    # ------------------------------------------------------------------

    def execute_text_provider_mock(
        self,
        provider_id: str,
        prompt: str,
        model_id: str = "",
        max_tokens: int = 512,
        temperature: float = 0.7,
        system_prompt: str = "",
    ) -> "UIActionResult":
        """Execute a text provider in mock mode. No network call, no secret needed."""
        try:
            from aurora_studio.contracts.text_provider import TextProviderRequest
            from aurora_studio.modules.openai_compatible_text_adapter import OpenAICompatibleTextAdapter
            adapter = OpenAICompatibleTextAdapter(provider_id=provider_id)
            request = TextProviderRequest(
                provider_id=provider_id,
                prompt=prompt,
                model_id=model_id,
                execution_mode="mock",
                max_tokens=max_tokens,
                temperature=temperature,
                system_prompt=system_prompt,
            )
            response = adapter.execute_mock(request)
            return _ok(response.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def execute_text_provider_real_blocked(
        self,
        provider_id: str,
        prompt: str,
    ) -> "UIActionResult":
        """Attempt real text execution — always returns blocked in v0.4."""
        try:
            from aurora_studio.contracts.text_provider import TextProviderRequest
            from aurora_studio.modules.openai_compatible_text_adapter import OpenAICompatibleTextAdapter
            adapter = OpenAICompatibleTextAdapter(provider_id=provider_id)
            request = TextProviderRequest(
                provider_id=provider_id,
                prompt=prompt,
                execution_mode="real_text",
            )
            response = adapter.execute(request, ephemeral_secret="")
            return _ok(response.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def execute_text_provider_real_with_ephemeral_secret(
        self,
        provider_id: str,
        prompt: str,
        ephemeral_secret: str,
        model_id: str = "",
        confirm: bool = False,
    ) -> "UIActionResult":
        """Execute real text with ephemeral secret. Requires confirm=True.

        Secret is used call-time only and never stored or returned in payload.
        Blocked by default (gate always returns False in v0.4).
        """
        if not confirm:
            return _fail(
                "Real text execution requires confirm=True. "
                "This is an explicit gate requiring user acknowledgement."
            )
        try:
            from aurora_studio.contracts.text_provider import TextProviderRequest
            from aurora_studio.modules.openai_compatible_text_adapter import OpenAICompatibleTextAdapter
            adapter = OpenAICompatibleTextAdapter(provider_id=provider_id)
            request = TextProviderRequest(
                provider_id=provider_id,
                prompt=prompt,
                model_id=model_id,
                execution_mode="real_text",
                # ephemeral_secret_ref is a label, not the secret value
                ephemeral_secret_ref="call-time-ephemeral",
            )
            # ephemeral_secret passed at call time, never stored on adapter or request
            response = adapter.execute(request, ephemeral_secret=ephemeral_secret)
            # Never return secret in payload
            payload = response.to_dict()
            return _ok(payload)
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000109: Text Provider Execution UI Finalization
    # ------------------------------------------------------------------

    def evaluate_text_provider_real_readiness(
        self,
        provider_id: str,
        config: dict | None = None,
    ) -> "UIActionResult":
        """Evaluate whether all prerequisites for real text execution are satisfied.

        Returns a readiness report with which prerequisites pass/fail.
        Real execution is blocked by default; this is informational only.
        """
        try:
            from aurora_studio.modules.provider_execution_gate import ProviderExecutionGate
            gate = ProviderExecutionGate()
            decision = gate.evaluate_real_text_execution(provider_id, config=config)
            prereqs = gate.list_real_text_prerequisites()
            return _ok({
                "provider_id": provider_id,
                "real_execution_ready": decision.allowed,
                "gate_decision": decision.to_dict(),
                "prerequisites": [p.to_dict() for p in prereqs],
                "missing_conditions": list(decision.missing_conditions),
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_text_provider_runs(
        self,
        provider_id: str = "",
        limit: int = 50,
    ) -> "UIActionResult":
        """List recent text provider run records (in-memory only, no secret fields).

        Runs are stored in an ephemeral in-memory list that is cleared on restart.
        No secret values are ever stored in run records.
        """
        try:
            if not hasattr(self, "_text_provider_runs"):
                self._text_provider_runs: list[dict] = []
            runs = self._text_provider_runs
            if provider_id:
                runs = [r for r in runs if r.get("provider_id") == provider_id]
            return _ok({
                "provider_id": provider_id or "all",
                "total": len(runs),
                "runs": runs[-limit:],
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def _record_text_provider_run(self, response_dict: dict) -> None:
        """Internal: record a sanitized text provider run result. No secrets stored."""
        if not hasattr(self, "_text_provider_runs"):
            self._text_provider_runs: list[dict] = []
        # Explicitly remove any key that might accidentally contain a secret
        safe = {
            k: v for k, v in response_dict.items()
            if k not in {"ephemeral_secret", "api_key", "secret", "token", "authorization"}
        }
        self._text_provider_runs.append(safe)

    # ------------------------------------------------------------------
    # TASK-000111: Image Provider Execution Gate
    # ------------------------------------------------------------------

    def evaluate_image_provider_execution_gate(
        self,
        provider_id: str,
        requested_action: str,
        mode: str = "mock_image",
        config: dict | None = None,
    ) -> "UIActionResult":
        """Evaluate image provider execution gate for the given mode.

        mock_image always allowed. real_image blocked by default.
        """
        try:
            from aurora_studio.modules.provider_execution_gate import ImageProviderExecutionGate
            gate = ImageProviderExecutionGate()
            decision = gate.evaluate_execution(
                provider_id, requested_action, mode=mode, config=config
            )
            return _ok(decision.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_real_image_provider_prerequisites(self) -> "UIActionResult":
        """List all prerequisites required for real image provider execution."""
        try:
            from aurora_studio.modules.provider_execution_gate import ImageProviderExecutionGate
            gate = ImageProviderExecutionGate()
            prereqs = gate.list_real_image_prerequisites()
            return _ok({"prerequisites": [p.to_dict() for p in prereqs]})
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000113: Mock Image Provider Adapter
    # ------------------------------------------------------------------

    def execute_image_provider_mock(
        self,
        provider_id: str,
        prompt_text: str,
        negative_prompt_text: str = "",
        model: str | None = None,
        parameters: dict | None = None,
    ) -> "UIActionResult":
        """Execute mock image provider. No network, no secret, no image files."""
        try:
            from aurora_studio.modules.mock_image_provider_adapter import MockImageProviderAdapter
            adapter = MockImageProviderAdapter()
            request = adapter.build_request(
                prompt_text=prompt_text,
                provider_id=provider_id,
                mode="mock_image",
                negative_prompt_text=negative_prompt_text,
                model=model or "",
                parameters=parameters or {},
            )
            response = adapter.execute_mock(request)
            return _ok(response.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def evaluate_image_provider_real_readiness(
        self,
        provider_id: str,
        prompt_text: str = "",
        model: str | None = None,
        config: dict | None = None,
    ) -> "UIActionResult":
        """Evaluate real image provider readiness. Always blocked in v0.4."""
        try:
            from aurora_studio.modules.provider_execution_gate import ImageProviderExecutionGate
            gate = ImageProviderExecutionGate()
            decision = gate.evaluate_real_image(provider_id, config=config)
            prereqs = gate.list_real_image_prerequisites()
            return _ok({
                "provider_id": provider_id,
                "real_image_execution_ready": decision.allowed,
                "gate_decision": decision.to_dict(),
                "prerequisites": [p.to_dict() for p in prereqs],
                "missing_conditions": list(decision.missing_conditions),
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000114: Image Prompt Export Bridge
    # ------------------------------------------------------------------

    def _get_image_bridge(self) -> "ImagePromptExportBridge":
        if not hasattr(self, "_image_bridge"):
            from aurora_studio.modules.image_prompt_export_bridge import ImagePromptExportBridge
            self._image_bridge = ImagePromptExportBridge()
        return self._image_bridge

    def run_mock_image_from_prompt(
        self,
        provider_id: str,
        prompt_text: str,
        negative_prompt_text: str = "",
        model: str | None = None,
        parameters: dict | None = None,
    ) -> "UIActionResult":
        """Run mock image from prompt text. No network, no image file, no secret."""
        try:
            bridge = self._get_image_bridge()
            result = bridge.run_mock_image_from_prompt(
                provider_id, prompt_text,
                negative_prompt_text=negative_prompt_text,
                model=model, parameters=parameters,
            )
            return _ok(result)
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def run_mock_image_from_export(
        self,
        provider_id: str,
        export_artifact_id: str,
        model: str | None = None,
        parameters: dict | None = None,
    ) -> "UIActionResult":
        """Run mock image from export artifact. No network, no image file."""
        try:
            bridge = self._get_image_bridge()
            result = bridge.run_mock_image_from_export(
                provider_id, export_artifact_id, model=model, parameters=parameters,
            )
            return _ok(result)
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def run_mock_image_from_template(
        self,
        provider_id: str,
        source_type: str,
        source_id: str,
        template_id: str | None = None,
        profile_id: str | None = None,
        model: str | None = None,
        parameters: dict | None = None,
    ) -> "UIActionResult":
        """Run mock image from template/profile. No network, no image file."""
        try:
            bridge = self._get_image_bridge()
            result = bridge.run_mock_image_from_template(
                provider_id, source_type, source_id,
                template_id=template_id, profile_id=profile_id,
                model=model, parameters=parameters,
            )
            return _ok(result)
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_image_provider_runs(
        self,
        provider_id: str | None = None,
        status: str | None = None,
    ) -> "UIActionResult":
        """List in-memory image provider runs. Ephemeral. No secrets stored."""
        try:
            bridge = self._get_image_bridge()
            runs = bridge.list_image_provider_runs(provider_id=provider_id, status=status)
            return _ok({
                "provider_id": provider_id or "all",
                "status_filter": status or "all",
                "total": len(runs),
                "runs": runs,
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000116: Video Provider Safety Boundary
    # ------------------------------------------------------------------

    def evaluate_video_provider_execution_gate(
        self,
        provider_id: str,
        requested_action: str,
        mode: str = "mock_video",
        config: dict | None = None,
    ) -> "UIActionResult":
        """Evaluate video provider execution gate. Real video always blocked in v0.4."""
        try:
            from aurora_studio.modules.provider_execution_gate import VideoProviderExecutionGate
            gate = VideoProviderExecutionGate()
            decision = gate.evaluate_execution(provider_id, requested_action, mode=mode, config=config)
            return _ok(decision.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_real_video_provider_prerequisites(self) -> "UIActionResult":
        """List prerequisites for real video execution. All unsatisfied in v0.4."""
        try:
            from aurora_studio.modules.provider_execution_gate import VideoProviderExecutionGate
            gate = VideoProviderExecutionGate()
            prereqs = gate.list_real_video_prerequisites()
            return _ok({
                "prerequisites": [p.to_dict() for p in prereqs],
                "total": len(prereqs),
                "all_satisfied": False,
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000118: Mock Video Provider Adapter
    # ------------------------------------------------------------------

    def execute_video_provider_mock(
        self,
        provider_id: str,
        prompt_text: str,
        negative_prompt_text: str = "",
        model: str | None = None,
        parameters: dict | None = None,
    ) -> "UIActionResult":
        """Execute mock video provider. No network, no secret, no video file."""
        try:
            from aurora_studio.modules.mock_video_provider_adapter import MockVideoProviderAdapter
            adapter = MockVideoProviderAdapter()
            request = adapter.build_request(
                prompt_text=prompt_text,
                provider_id=provider_id,
                mode="mock_video",
                negative_prompt_text=negative_prompt_text,
                model=model or "",
                parameters=parameters or {},
            )
            response = adapter.execute_mock(request)
            return _ok(response.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def evaluate_video_provider_real_readiness(
        self,
        provider_id: str,
        prompt_text: str = "",
        model: str | None = None,
        config: dict | None = None,
    ) -> "UIActionResult":
        """Evaluate real video provider readiness. Always blocked in v0.4."""
        try:
            from aurora_studio.modules.provider_execution_gate import VideoProviderExecutionGate
            gate = VideoProviderExecutionGate()
            decision = gate.evaluate_real_video(provider_id, config=config)
            prereqs = gate.list_real_video_prerequisites()
            return _ok({
                "provider_id": provider_id,
                "real_video_execution_ready": decision.allowed,
                "gate_decision": decision.to_dict(),
                "prerequisites": [p.to_dict() for p in prereqs],
                "missing_conditions": list(decision.missing_conditions),
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # TASK-000119: Video Prompt Export Bridge
    # ------------------------------------------------------------------

    def _get_video_bridge(self) -> "VideoPromptExportBridge":
        if not hasattr(self, "_video_bridge"):
            from aurora_studio.modules.video_prompt_export_bridge import VideoPromptExportBridge
            self._video_bridge = VideoPromptExportBridge()
        return self._video_bridge

    def run_mock_video_from_prompt(
        self,
        provider_id: str,
        prompt_text: str,
        negative_prompt_text: str = "",
        model: str | None = None,
        parameters: dict | None = None,
    ) -> "UIActionResult":
        """Run mock video from prompt text. No network, no video file, no secret."""
        try:
            bridge = self._get_video_bridge()
            result = bridge.run_mock_video_from_prompt(
                provider_id, prompt_text,
                negative_prompt_text=negative_prompt_text,
                model=model, parameters=parameters,
            )
            return _ok(result)
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def run_mock_video_from_export(
        self,
        provider_id: str,
        export_artifact_id: str,
        model: str | None = None,
        parameters: dict | None = None,
    ) -> "UIActionResult":
        """Run mock video from export artifact. No network, no video file."""
        try:
            bridge = self._get_video_bridge()
            result = bridge.run_mock_video_from_export(
                provider_id, export_artifact_id, model=model, parameters=parameters,
            )
            return _ok(result)
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def run_mock_video_from_template(
        self,
        provider_id: str,
        source_type: str,
        source_id: str,
        template_id: str | None = None,
        profile_id: str | None = None,
        model: str | None = None,
        parameters: dict | None = None,
    ) -> "UIActionResult":
        """Run mock video from template/profile. No network, no video file."""
        try:
            bridge = self._get_video_bridge()
            result = bridge.run_mock_video_from_template(
                provider_id, source_type, source_id,
                template_id=template_id, profile_id=profile_id,
                model=model, parameters=parameters,
            )
            return _ok(result)
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")

    def list_video_provider_runs(
        self,
        provider_id: str | None = None,
        status: str | None = None,
    ) -> "UIActionResult":
        """List in-memory video provider runs. Ephemeral. No secrets stored."""
        try:
            bridge = self._get_video_bridge()
            runs = bridge.list_video_provider_runs(provider_id=provider_id, status=status)
            return _ok({
                "provider_id": provider_id or "all",
                "status_filter": status or "all",
                "total": len(runs),
                "runs": runs,
            })
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")
