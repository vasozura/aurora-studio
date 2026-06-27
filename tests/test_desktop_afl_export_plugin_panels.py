"""Tests for TASK-000041: Desktop AFL / Export / Plugin panels.

All tests are headless-safe.  No display required.
"""

import json
import sys
import types
import unittest
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _src_on_path() -> None:
    import pathlib
    src = str(pathlib.Path(__file__).parent.parent / "src")
    if src not in sys.path:
        sys.path.insert(0, src)


_src_on_path()


# ---------------------------------------------------------------------------
# Fake manager records for view-model tests
# ---------------------------------------------------------------------------

@dataclass
class FakeAFLReport:
    report_id: str = "rpt-001"
    target_ref: str = "scene:s1"
    status: str = "ok"
    issues: list = field(default_factory=list)
    created_at: str = "2026-06-27T00:00:00"


@dataclass
class FakeExportArtifact:
    artifact_id: str = "art-001"
    source_id: str = "src-001"
    artifact_type: str = "prompt"
    status: str = "pending"
    provider_target: str | None = None


@dataclass
class FakePluginRecord:
    plugin_id: str = "plg-001"
    name: str = "smoke-plugin"
    version: str = "0.1.0"
    state: str = "registered"
    capabilities: list = field(default_factory=lambda: ["gen"])
    permissions: list = field(default_factory=lambda: ["read"])


# ---------------------------------------------------------------------------
# 1. Import safety
# ---------------------------------------------------------------------------

class TestImportSafety(unittest.TestCase):

    def test_desktop_shell_importable(self) -> None:
        from aurora_studio.ui import desktop_shell  # noqa: F401

    def test_import_does_not_open_window(self) -> None:
        import aurora_studio.ui.desktop_shell as ds
        self.assertTrue(hasattr(ds, "DesktopShell"))
        self.assertTrue(hasattr(ds, "headless_smoke"))

    def test_view_models_importable(self) -> None:
        from aurora_studio.ui.view_models import (
            AFLReportViewModel,
            ExportArtifactViewModel,
            PluginViewModel,
        )

    def test_ui_init_exports(self) -> None:
        import aurora_studio.ui as ui
        for name in ("AFLReportViewModel", "ExportArtifactViewModel", "PluginViewModel"):
            self.assertTrue(hasattr(ui, name), f"Missing: {name}")


# ---------------------------------------------------------------------------
# 2. headless_smoke
# ---------------------------------------------------------------------------

class TestHeadlessSmoke(unittest.TestCase):

    def test_headless_smoke_returns_dict(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertIsInstance(result, dict)

    def test_headless_smoke_ok(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertTrue(result.get("ok"))

    def test_headless_smoke_json_serializable(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        serialized = json.dumps(result)
        parsed = json.loads(serialized)
        self.assertIsInstance(parsed, dict)

    def test_headless_smoke_no_tkinter(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertNotIn("tkinter", str(result))


# ---------------------------------------------------------------------------
# 3. AFLReportViewModel
# ---------------------------------------------------------------------------

class TestAFLReportViewModel(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.view_models import AFLReportViewModel
        self.VM = AFLReportViewModel

    def test_from_record_fields(self) -> None:
        rec = FakeAFLReport(issues=["issue1", "issue2"])
        vm = self.VM.from_record(rec)
        self.assertEqual(vm.report_id, "rpt-001")
        self.assertEqual(vm.target_ref, "scene:s1")
        self.assertEqual(vm.status, "ok")
        self.assertEqual(vm.issue_count, 2)
        self.assertEqual(vm.created_at, "2026-06-27T00:00:00")

    def test_issue_count_zero(self) -> None:
        rec = FakeAFLReport(issues=[])
        vm = self.VM.from_record(rec)
        self.assertEqual(vm.issue_count, 0)

    def test_to_dict_json_serializable(self) -> None:
        rec = FakeAFLReport()
        d = self.VM.from_record(rec).to_dict()
        json.dumps(d)

    def test_to_dict_keys(self) -> None:
        rec = FakeAFLReport()
        d = self.VM.from_record(rec).to_dict()
        for k in ("report_id", "target_ref", "status", "issue_count", "created_at"):
            self.assertIn(k, d)

    def test_frozen(self) -> None:
        rec = FakeAFLReport()
        vm = self.VM.from_record(rec)
        with self.assertRaises((AttributeError, TypeError)):
            vm.report_id = "x"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 4. ExportArtifactViewModel
# ---------------------------------------------------------------------------

class TestExportArtifactViewModel(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.view_models import ExportArtifactViewModel
        self.VM = ExportArtifactViewModel

    def test_from_record_fields(self) -> None:
        rec = FakeExportArtifact()
        vm = self.VM.from_record(rec)
        self.assertEqual(vm.artifact_id, "art-001")
        self.assertEqual(vm.source_id, "src-001")
        self.assertEqual(vm.artifact_type, "prompt")
        self.assertEqual(vm.status, "pending")
        self.assertIsNone(vm.provider_target)

    def test_from_record_with_provider(self) -> None:
        rec = FakeExportArtifact(provider_target="runwayml")
        vm = self.VM.from_record(rec)
        self.assertEqual(vm.provider_target, "runwayml")

    def test_to_dict_json_serializable(self) -> None:
        rec = FakeExportArtifact()
        d = self.VM.from_record(rec).to_dict()
        json.dumps(d)

    def test_to_dict_keys(self) -> None:
        d = self.VM.from_record(FakeExportArtifact()).to_dict()
        for k in ("artifact_id", "source_id", "artifact_type", "status", "provider_target"):
            self.assertIn(k, d)

    def test_frozen(self) -> None:
        vm = self.VM.from_record(FakeExportArtifact())
        with self.assertRaises((AttributeError, TypeError)):
            vm.status = "ready"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 5. PluginViewModel
# ---------------------------------------------------------------------------

class TestPluginViewModel(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.view_models import PluginViewModel
        self.VM = PluginViewModel

    def test_from_record_fields(self) -> None:
        rec = FakePluginRecord()
        vm = self.VM.from_record(rec)
        self.assertEqual(vm.plugin_id, "plg-001")
        self.assertEqual(vm.name, "smoke-plugin")
        self.assertEqual(vm.version, "0.1.0")
        self.assertEqual(vm.state, "registered")
        self.assertIn("gen", vm.capabilities)
        self.assertIn("read", vm.permissions)

    def test_capabilities_is_tuple(self) -> None:
        vm = self.VM.from_record(FakePluginRecord())
        self.assertIsInstance(vm.capabilities, tuple)

    def test_permissions_is_tuple(self) -> None:
        vm = self.VM.from_record(FakePluginRecord())
        self.assertIsInstance(vm.permissions, tuple)

    def test_to_dict_json_serializable(self) -> None:
        d = self.VM.from_record(FakePluginRecord()).to_dict()
        json.dumps(d)

    def test_to_dict_capabilities_list(self) -> None:
        d = self.VM.from_record(FakePluginRecord()).to_dict()
        self.assertIsInstance(d["capabilities"], list)

    def test_to_dict_permissions_list(self) -> None:
        d = self.VM.from_record(FakePluginRecord()).to_dict()
        self.assertIsInstance(d["permissions"], list)

    def test_to_dict_keys(self) -> None:
        d = self.VM.from_record(FakePluginRecord()).to_dict()
        for k in ("plugin_id", "name", "version", "state", "capabilities", "permissions"):
            self.assertIn(k, d)

    def test_frozen(self) -> None:
        vm = self.VM.from_record(FakePluginRecord())
        with self.assertRaises((AttributeError, TypeError)):
            vm.state = "enabled"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 6. AppStateViewModel includes new fields
# ---------------------------------------------------------------------------

class TestAppStateViewModelExtended(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.view_models import (
            AppStateViewModel,
            ProjectViewModel,
            WorkspaceViewModel,
            AFLReportViewModel,
            ExportArtifactViewModel,
            PluginViewModel,
        )
        self.AppStateViewModel = AppStateViewModel

        class FakeWS:
            active_project_id = None
            active_scene_id = None
            active_shot_id = None
            mode = "idle"

        self.ws = WorkspaceViewModel.from_state(FakeWS())

    def test_default_afl_reports_empty(self) -> None:
        vm = self.AppStateViewModel(project=None, workspace=self.ws, scenes=(), shots=())
        self.assertEqual(vm.afl_reports, ())

    def test_default_export_artifacts_empty(self) -> None:
        vm = self.AppStateViewModel(project=None, workspace=self.ws, scenes=(), shots=())
        self.assertEqual(vm.export_artifacts, ())

    def test_default_plugins_empty(self) -> None:
        vm = self.AppStateViewModel(project=None, workspace=self.ws, scenes=(), shots=())
        self.assertEqual(vm.plugins, ())

    def test_to_dict_includes_afl_reports(self) -> None:
        vm = self.AppStateViewModel(project=None, workspace=self.ws, scenes=(), shots=())
        d = vm.to_dict()
        self.assertIn("afl_reports", d)

    def test_to_dict_includes_export_artifacts(self) -> None:
        vm = self.AppStateViewModel(project=None, workspace=self.ws, scenes=(), shots=())
        d = vm.to_dict()
        self.assertIn("export_artifacts", d)

    def test_to_dict_includes_plugins(self) -> None:
        vm = self.AppStateViewModel(project=None, workspace=self.ws, scenes=(), shots=())
        d = vm.to_dict()
        self.assertIn("plugins", d)

    def test_to_dict_json_serializable(self) -> None:
        vm = self.AppStateViewModel(project=None, workspace=self.ws, scenes=(), shots=())
        json.dumps(vm.to_dict())


# ---------------------------------------------------------------------------
# 7. UISession AFL actions
# ---------------------------------------------------------------------------

class TestUISessionAFLActions(unittest.TestCase):

    def setUp(self) -> None:
        import tempfile, os
        from aurora_studio.ui.actions import UISession
        self.session = UISession()
        self._tmpdir = tempfile.mkdtemp(prefix="aurora_afl_")
        r = self.session.create_project(self._tmpdir, "AFL Test")
        self.assertTrue(r.ok, f"create_project failed: {r.message}")

    def test_validate_afl_valid_json(self) -> None:
        r = self.session.validate_afl_structure("scene:s1", '{"kind": "smoke"}')
        self.assertIsInstance(r.ok, bool)
        # valid JSON dict → should succeed
        self.assertTrue(r.ok, r.message)

    def test_validate_afl_invalid_json(self) -> None:
        r = self.session.validate_afl_structure("scene:s1", "not json")
        self.assertFalse(r.ok)

    def test_validate_afl_json_not_dict(self) -> None:
        r = self.session.validate_afl_structure("scene:s1", "[1, 2, 3]")
        self.assertFalse(r.ok)

    def test_validate_afl_payload_json_serializable(self) -> None:
        r = self.session.validate_afl_structure("scene:s1", '{"kind": "smoke"}')
        if r.payload is not None:
            json.dumps(r.payload)

    def test_list_afl_reports(self) -> None:
        r = self.session.list_afl_reports()
        self.assertIsInstance(r.ok, bool)

    def test_list_afl_reports_after_validate(self) -> None:
        self.session.validate_afl_structure("scene:s1", '{"kind": "smoke"}')
        r = self.session.list_afl_reports()
        self.assertTrue(r.ok)
        reports = r.payload or []
        self.assertGreaterEqual(len(reports), 1)

    def test_validate_afl_returns_ui_action_result(self) -> None:
        from aurora_studio.ui.actions import UIActionResult
        r = self.session.validate_afl_structure("t", '{"k": 1}')
        self.assertIsInstance(r, UIActionResult)

    def test_validate_afl_empty_payload(self) -> None:
        r = self.session.validate_afl_structure("scene:s1", "")
        self.assertFalse(r.ok)


# ---------------------------------------------------------------------------
# 8. UISession Export actions
# ---------------------------------------------------------------------------

class TestUISessionExportActions(unittest.TestCase):

    def setUp(self) -> None:
        import tempfile
        from aurora_studio.ui.actions import UISession
        self.session = UISession()
        self._tmpdir = tempfile.mkdtemp(prefix="aurora_exp_")
        r = self.session.create_project(self._tmpdir, "Export Test")
        self.assertTrue(r.ok, r.message)

    def test_create_export_artifact(self) -> None:
        r = self.session.create_export_artifact("src-1", "prompt", "content here")
        self.assertIsInstance(r.ok, bool)
        self.assertTrue(r.ok, r.message)

    def test_create_export_artifact_with_provider(self) -> None:
        r = self.session.create_export_artifact("src-1", "prompt", "content", "runwayml")
        self.assertTrue(r.ok)

    def test_create_export_artifact_payload_has_id(self) -> None:
        r = self.session.create_export_artifact("src-1", "prompt", "content")
        self.assertIsNotNone(r.payload)
        self.assertIn("artifact_id", r.payload or {})

    def test_mark_export_ready(self) -> None:
        r1 = self.session.create_export_artifact("src-1", "prompt", "c")
        artifact_id = (r1.payload or {}).get("artifact_id", "")
        r2 = self.session.mark_export_ready(artifact_id)
        self.assertIsInstance(r2.ok, bool)

    def test_mark_export_failed(self) -> None:
        r1 = self.session.create_export_artifact("src-1", "prompt", "c")
        artifact_id = (r1.payload or {}).get("artifact_id", "")
        r2 = self.session.mark_export_failed(artifact_id)
        self.assertIsInstance(r2.ok, bool)

    def test_mark_export_failed_with_message(self) -> None:
        r1 = self.session.create_export_artifact("src-1", "prompt", "c")
        artifact_id = (r1.payload or {}).get("artifact_id", "")
        r2 = self.session.mark_export_failed(artifact_id, "provider timeout")
        self.assertIsInstance(r2.ok, bool)

    def test_list_export_artifacts(self) -> None:
        r = self.session.list_export_artifacts()
        self.assertIsInstance(r.ok, bool)

    def test_list_export_artifacts_after_create(self) -> None:
        self.session.create_export_artifact("src-x", "render", "data")
        r = self.session.list_export_artifacts()
        self.assertTrue(r.ok)
        self.assertGreaterEqual(len(r.payload or []), 1)

    def test_export_payload_json_serializable(self) -> None:
        r = self.session.create_export_artifact("src-1", "prompt", "c")
        if r.payload:
            json.dumps(r.payload)


# ---------------------------------------------------------------------------
# 9. UISession Plugin actions
# ---------------------------------------------------------------------------

class TestUISessionPluginActions(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.actions import UISession
        self.session = UISession()

    def test_register_plugin(self) -> None:
        r = self.session.register_plugin("smoke-plugin", "1.0.0")
        self.assertIsInstance(r.ok, bool)
        self.assertTrue(r.ok, r.message)

    def test_register_plugin_with_caps(self) -> None:
        r = self.session.register_plugin("cap-plugin", "1.0.0", "gen,render", "read,write")
        self.assertTrue(r.ok)

    def test_register_plugin_payload_has_id(self) -> None:
        r = self.session.register_plugin("id-plugin", "1.0.0")
        self.assertIn("plugin_id", r.payload or {})

    def test_enable_plugin(self) -> None:
        r1 = self.session.register_plugin("en-plugin", "1.0.0")
        plugin_id = (r1.payload or {}).get("plugin_id", "")
        r2 = self.session.enable_plugin(plugin_id)
        self.assertIsInstance(r2.ok, bool)

    def test_disable_plugin(self) -> None:
        r1 = self.session.register_plugin("dis-plugin", "1.0.0")
        plugin_id = (r1.payload or {}).get("plugin_id", "")
        r2 = self.session.disable_plugin(plugin_id)
        self.assertIsInstance(r2.ok, bool)

    def test_list_plugins(self) -> None:
        r = self.session.list_plugins()
        self.assertIsInstance(r.ok, bool)

    def test_list_plugins_after_register(self) -> None:
        self.session.register_plugin("list-plugin", "1.0.0")
        r = self.session.list_plugins()
        self.assertTrue(r.ok)
        self.assertGreaterEqual(len(r.payload or []), 1)

    def test_plugin_payload_json_serializable(self) -> None:
        r = self.session.register_plugin("json-plugin", "1.0.0")
        if r.payload:
            json.dumps(r.payload)

    def test_caps_parsed(self) -> None:
        r = self.session.register_plugin("caps-plugin", "1.0.0", "gen, render, export")
        self.assertTrue(r.ok)

    def test_empty_caps(self) -> None:
        r = self.session.register_plugin("no-caps-plugin", "1.0.0", "", "")
        self.assertTrue(r.ok)


# ---------------------------------------------------------------------------
# 10. get_app_state includes AFL/Export/Plugin
# ---------------------------------------------------------------------------

class TestGetAppStateExtended(unittest.TestCase):

    def setUp(self) -> None:
        import tempfile
        from aurora_studio.ui.actions import UISession
        self.session = UISession()
        self._tmpdir = tempfile.mkdtemp(prefix="aurora_st_")
        self.session.create_project(self._tmpdir, "State Test")

    def test_get_app_state_ok(self) -> None:
        r = self.session.get_app_state()
        self.assertTrue(r.ok)

    def test_get_app_state_has_afl_reports(self) -> None:
        r = self.session.get_app_state()
        self.assertIn("afl_reports", r.payload or {})

    def test_get_app_state_has_export_artifacts(self) -> None:
        r = self.session.get_app_state()
        self.assertIn("export_artifacts", r.payload or {})

    def test_get_app_state_has_plugins(self) -> None:
        r = self.session.get_app_state()
        self.assertIn("plugins", r.payload or {})

    def test_get_app_state_json_serializable(self) -> None:
        r = self.session.get_app_state()
        json.dumps(r.payload)

    def test_afl_reports_list_after_validate(self) -> None:
        self.session.validate_afl_structure("t", '{"k": 1}')
        r = self.session.get_app_state()
        reports = (r.payload or {}).get("afl_reports", [])
        self.assertGreaterEqual(len(reports), 1)

    def test_export_artifacts_list_after_create(self) -> None:
        self.session.create_export_artifact("s", "prompt", "c")
        r = self.session.get_app_state()
        arts = (r.payload or {}).get("export_artifacts", [])
        self.assertGreaterEqual(len(arts), 1)

    def test_plugins_list_after_register(self) -> None:
        self.session.register_plugin("p", "1.0")
        r = self.session.get_app_state()
        plugins = (r.payload or {}).get("plugins", [])
        self.assertGreaterEqual(len(plugins), 1)


# ---------------------------------------------------------------------------
# 11. DesktopShell exposes public method names
# ---------------------------------------------------------------------------

class TestDesktopShellMethodNames(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.DS = DesktopShell

    def _has(self, name: str) -> None:
        self.assertTrue(callable(getattr(self.DS, name, None)),
                        f"DesktopShell.{name} is not callable")

    def test_validate_afl_structure(self) -> None:
        self._has("validate_afl_structure")

    def test_on_afl_report_selected(self) -> None:
        self._has("on_afl_report_selected")

    def test_create_export_artifact(self) -> None:
        self._has("create_export_artifact")

    def test_mark_export_ready(self) -> None:
        self._has("mark_export_ready")

    def test_mark_export_failed(self) -> None:
        self._has("mark_export_failed")

    def test_on_export_artifact_selected(self) -> None:
        self._has("on_export_artifact_selected")

    def test_register_plugin(self) -> None:
        self._has("register_plugin")

    def test_enable_plugin(self) -> None:
        self._has("enable_plugin")

    def test_disable_plugin(self) -> None:
        self._has("disable_plugin")

    def test_on_plugin_selected(self) -> None:
        self._has("on_plugin_selected")

    # Carry-over from TASK-000040
    def test_create_timeline(self) -> None:
        self._has("create_timeline")

    def test_import_asset(self) -> None:
        self._has("import_asset")

    def test_create_character(self) -> None:
        self._has("create_character")

    def test_get_state_snapshot(self) -> None:
        self._has("get_state_snapshot")

    def test_refresh(self) -> None:
        self._has("refresh")


# ---------------------------------------------------------------------------
# 12. get_state_snapshot contract (via UISession — no display needed)
# ---------------------------------------------------------------------------

class TestStateSnapshotContract(unittest.TestCase):
    """Verify snapshot keys by inspecting UISession output (no GUI)."""

    REQUIRED_KEYS = [
        "project",
        "workspace",
        "scene_count",
        "shot_count",
        "timeline_count",
        "asset_count",
        "character_count",
        "afl_report_count",
        "export_artifact_count",
        "plugin_count",
        "selected_scene_id",
        "selected_shot_id",
        "selected_timeline_id",
        "selected_timeline_item_id",
        "selected_asset_id",
        "selected_character_id",
        "selected_afl_report_id",
        "selected_export_artifact_id",
        "selected_plugin_id",
        "status",
    ]

    def test_get_state_snapshot_has_required_keys(self) -> None:
        """Build a minimal mock shell to call get_state_snapshot without display."""
        from aurora_studio.ui.actions import UISession
        from aurora_studio.ui.desktop_shell import DesktopShell

        # Build a no-display proxy: create DesktopShell attributes manually
        session = UISession()
        shell = object.__new__(DesktopShell)
        shell.session = session

        # Inject all required private fields
        for field in (
            "_selected_scene_id", "_selected_shot_id",
            "_selected_timeline_id", "_selected_timeline_item_id",
            "_selected_asset_id", "_selected_character_id",
            "_selected_afl_report_id", "_selected_export_artifact_id",
            "_selected_plugin_id",
        ):
            setattr(shell, field, None)
        shell._status_var = None
        shell._log_count = 0

        snapshot = shell.get_state_snapshot()
        for key in self.REQUIRED_KEYS:
            self.assertIn(key, snapshot, f"Missing key in snapshot: {key}")

    def test_get_state_snapshot_json_serializable(self) -> None:
        from aurora_studio.ui.actions import UISession
        from aurora_studio.ui.desktop_shell import DesktopShell

        session = UISession()
        shell = object.__new__(DesktopShell)
        shell.session = session
        for field in (
            "_selected_scene_id", "_selected_shot_id",
            "_selected_timeline_id", "_selected_timeline_item_id",
            "_selected_asset_id", "_selected_character_id",
            "_selected_afl_report_id", "_selected_export_artifact_id",
            "_selected_plugin_id",
        ):
            setattr(shell, field, None)
        shell._status_var = None
        shell._log_count = 0
        snapshot = shell.get_state_snapshot()
        json.dumps(snapshot)


# ---------------------------------------------------------------------------
# 13. headless_smoke --headless-smoke CLI flag
# ---------------------------------------------------------------------------

class TestHeadlessSmokeCLI(unittest.TestCase):

    def test_main_headless_returns_zero(self) -> None:
        from aurora_studio.ui.desktop_shell import main
        code = main(["--headless-smoke"])
        self.assertEqual(code, 0)


# ---------------------------------------------------------------------------
# 14. Existing panels still intact (regression)
# ---------------------------------------------------------------------------

class TestExistingPanelsIntact(unittest.TestCase):

    def test_desktop_shell_has_scene_method(self) -> None:
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(callable(getattr(DesktopShell, "create_scene", None)))

    def test_desktop_shell_has_shot_method(self) -> None:
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(callable(getattr(DesktopShell, "create_shot", None)))

    def test_desktop_shell_has_save_bundle(self) -> None:
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(callable(getattr(DesktopShell, "save_bundle", None)))

    def test_desktop_shell_has_load_bundle(self) -> None:
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(callable(getattr(DesktopShell, "load_bundle", None)))

    def test_ui_session_get_app_state_has_scenes(self) -> None:
        from aurora_studio.ui.actions import UISession
        s = UISession()
        s.create_project("/tmp/reg-test", "Reg")
        r = s.get_app_state()
        self.assertIn("scenes", r.payload or {})

    def test_ui_session_get_app_state_has_timelines(self) -> None:
        from aurora_studio.ui.actions import UISession
        s = UISession()
        s.create_project("/tmp/reg-test2", "Reg2")
        r = s.get_app_state()
        self.assertIn("timelines", r.payload or {})


if __name__ == "__main__":
    unittest.main()
