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
    AppStateViewModel,
    ProjectViewModel,
    SceneViewModel,
    ShotViewModel,
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

            app_state = AppStateViewModel(
                project=project_vm,
                workspace=workspace_vm,
                scenes=tuple(SceneViewModel.from_record(s) for s in scenes),
                shots=tuple(ShotViewModel.from_record(s) for s in shots),
            )
            return _ok(app_state.to_dict())
        except Exception as exc:
            return _fail(f"Unexpected error: {exc}")
