"""Tests for TASK-000042: Desktop Layout Consolidation.

All tests are headless-safe. No display required.
"""

import json
import sys
import tempfile
import unittest


def _src_on_path() -> None:
    import pathlib
    src = str(pathlib.Path(__file__).parent.parent / "src")
    if src not in sys.path:
        sys.path.insert(0, src)


_src_on_path()


# ---------------------------------------------------------------------------
# 1. Import safety
# ---------------------------------------------------------------------------

class TestImportSafety(unittest.TestCase):

    def test_desktop_shell_importable(self) -> None:
        import aurora_studio.ui.desktop_shell  # noqa: F401

    def test_import_does_not_open_window(self) -> None:
        from aurora_studio.ui import desktop_shell
        self.assertTrue(hasattr(desktop_shell, "DesktopShell"))
        self.assertTrue(hasattr(desktop_shell, "headless_smoke"))
        self.assertTrue(hasattr(desktop_shell, "TABS"))
        self.assertTrue(hasattr(desktop_shell, "SECTIONS"))

    def test_tabs_constant(self) -> None:
        from aurora_studio.ui.desktop_shell import TABS
        self.assertIsInstance(TABS, list)
        self.assertGreater(len(TABS), 0)

    def test_sections_constant(self) -> None:
        from aurora_studio.ui.desktop_shell import SECTIONS
        self.assertIsInstance(SECTIONS, list)


# ---------------------------------------------------------------------------
# 2. headless_smoke
# ---------------------------------------------------------------------------

class TestHeadlessSmoke(unittest.TestCase):

    def test_headless_smoke_returns_dict(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        self.assertIsInstance(headless_smoke(), dict)

    def test_headless_smoke_ok_true(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        self.assertTrue(headless_smoke().get("ok"))

    def test_headless_smoke_json_serializable(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        json.dumps(headless_smoke())

    def test_headless_smoke_has_app_state(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertIn("app_state", result)
        self.assertIsInstance(result["app_state"], dict)


# ---------------------------------------------------------------------------
# 3. get_layout_snapshot contract
# ---------------------------------------------------------------------------

class TestLayoutSnapshot(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.desktop_shell import DesktopShell, TABS, SECTIONS
        from aurora_studio.ui.actions import UISession

        # Construct shell without display
        shell = object.__new__(DesktopShell)
        shell.session = UISession()
        for attr in (
            "_selected_scene_id", "_selected_shot_id",
            "_selected_timeline_id", "_selected_timeline_item_id",
            "_selected_asset_id", "_selected_character_id",
            "_selected_afl_report_id", "_selected_export_artifact_id",
            "_selected_plugin_id",
        ):
            setattr(shell, attr, None)
        shell._status_var = None
        self.shell = shell
        self.TABS = TABS
        self.SECTIONS = SECTIONS

    def test_get_layout_snapshot_callable(self) -> None:
        self.assertTrue(callable(getattr(self.shell, "get_layout_snapshot")))

    def test_get_layout_snapshot_returns_dict(self) -> None:
        snap = self.shell.get_layout_snapshot()
        self.assertIsInstance(snap, dict)

    def test_get_layout_snapshot_json_serializable(self) -> None:
        json.dumps(self.shell.get_layout_snapshot())

    def test_layout_snapshot_has_tabs(self) -> None:
        snap = self.shell.get_layout_snapshot()
        self.assertIn("tabs", snap)
        self.assertIsInstance(snap["tabs"], list)

    def test_layout_snapshot_has_sections(self) -> None:
        snap = self.shell.get_layout_snapshot()
        self.assertIn("sections", snap)

    def test_layout_snapshot_has_status(self) -> None:
        snap = self.shell.get_layout_snapshot()
        self.assertIn("has_status", snap)
        self.assertTrue(snap["has_status"])

    def test_layout_snapshot_has_log(self) -> None:
        snap = self.shell.get_layout_snapshot()
        self.assertIn("has_log", snap)
        self.assertTrue(snap["has_log"])

    def test_layout_snapshot_has_project_bar(self) -> None:
        snap = self.shell.get_layout_snapshot()
        self.assertIn("has_project_bar", snap)
        self.assertTrue(snap["has_project_bar"])

    def test_layout_snapshot_tabs_includes_scenes_shots(self) -> None:
        tabs = self.shell.get_layout_snapshot()["tabs"]
        self.assertIn("Scenes & Shots", tabs)

    def test_layout_snapshot_tabs_includes_timeline(self) -> None:
        tabs = self.shell.get_layout_snapshot()["tabs"]
        self.assertIn("Timeline", tabs)

    def test_layout_snapshot_tabs_includes_assets(self) -> None:
        tabs = self.shell.get_layout_snapshot()["tabs"]
        self.assertIn("Assets", tabs)

    def test_layout_snapshot_tabs_includes_characters(self) -> None:
        tabs = self.shell.get_layout_snapshot()["tabs"]
        self.assertIn("Characters", tabs)

    def test_layout_snapshot_tabs_includes_afl(self) -> None:
        tabs = self.shell.get_layout_snapshot()["tabs"]
        self.assertIn("AFL", tabs)

    def test_layout_snapshot_tabs_includes_exports(self) -> None:
        tabs = self.shell.get_layout_snapshot()["tabs"]
        self.assertIn("Exports", tabs)

    def test_layout_snapshot_tabs_includes_plugins(self) -> None:
        tabs = self.shell.get_layout_snapshot()["tabs"]
        self.assertIn("Plugins", tabs)

    def test_layout_snapshot_has_seven_tabs(self) -> None:
        tabs = self.shell.get_layout_snapshot()["tabs"]
        self.assertEqual(len(tabs), 7)


# ---------------------------------------------------------------------------
# 4. get_state_snapshot contract (no display needed)
# ---------------------------------------------------------------------------

class TestStateSnapshotContract(unittest.TestCase):

    REQUIRED_KEYS = [
        "project", "workspace",
        "scene_count", "shot_count", "timeline_count",
        "asset_count", "character_count",
        "afl_report_count", "export_artifact_count", "plugin_count",
        "selected_scene_id", "selected_shot_id",
        "selected_timeline_id", "selected_timeline_item_id",
        "selected_asset_id", "selected_character_id",
        "selected_afl_report_id", "selected_export_artifact_id",
        "selected_plugin_id", "status",
    ]

    def _make_shell(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        from aurora_studio.ui.actions import UISession
        shell = object.__new__(DesktopShell)
        shell.session = UISession()
        for attr in (
            "_selected_scene_id", "_selected_shot_id",
            "_selected_timeline_id", "_selected_timeline_item_id",
            "_selected_asset_id", "_selected_character_id",
            "_selected_afl_report_id", "_selected_export_artifact_id",
            "_selected_plugin_id",
        ):
            setattr(shell, attr, None)
        shell._status_var = None
        shell._log_count = 0
        return shell

    def test_state_snapshot_has_required_keys(self) -> None:
        shell = self._make_shell()
        snap = shell.get_state_snapshot()
        for key in self.REQUIRED_KEYS:
            self.assertIn(key, snap, f"Missing: {key}")

    def test_state_snapshot_json_serializable(self) -> None:
        shell = self._make_shell()
        json.dumps(shell.get_state_snapshot())

    def test_state_snapshot_counts_are_ints(self) -> None:
        shell = self._make_shell()
        snap = shell.get_state_snapshot()
        for key in ("scene_count", "shot_count", "timeline_count",
                    "asset_count", "character_count", "afl_report_count",
                    "export_artifact_count", "plugin_count"):
            self.assertIsInstance(snap[key], int, f"{key} not int")


# ---------------------------------------------------------------------------
# 5. DesktopShell exposes all public methods
# ---------------------------------------------------------------------------

class TestDesktopShellPublicAPI(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.DS = DesktopShell

    def _has(self, name: str) -> None:
        self.assertTrue(callable(getattr(self.DS, name, None)),
                        f"DesktopShell.{name} not callable")

    # New in TASK-000042
    def test_clear_log(self) -> None: self._has("clear_log")
    def test_get_layout_snapshot(self) -> None: self._has("get_layout_snapshot")

    # From TASK-000039
    def test_create_project(self) -> None: self._has("create_project")
    def test_open_project(self) -> None: self._has("open_project")
    def test_create_scene(self) -> None: self._has("create_scene")
    def test_create_shot(self) -> None: self._has("create_shot")
    def test_save_bundle(self) -> None: self._has("save_bundle")
    def test_load_bundle(self) -> None: self._has("load_bundle")
    def test_refresh(self) -> None: self._has("refresh")
    def test_get_state_snapshot(self) -> None: self._has("get_state_snapshot")
    def test_on_scene_selected(self) -> None: self._has("on_scene_selected")
    def test_on_shot_selected(self) -> None: self._has("on_shot_selected")

    # From TASK-000040
    def test_create_timeline(self) -> None: self._has("create_timeline")
    def test_add_timeline_item(self) -> None: self._has("add_timeline_item")
    def test_remove_timeline_item(self) -> None: self._has("remove_timeline_item")
    def test_move_timeline_item(self) -> None: self._has("move_timeline_item")
    def test_on_timeline_selected(self) -> None: self._has("on_timeline_selected")
    def test_on_timeline_item_selected(self) -> None: self._has("on_timeline_item_selected")
    def test_import_asset(self) -> None: self._has("import_asset")
    def test_mark_asset_missing(self) -> None: self._has("mark_asset_missing")
    def test_archive_asset(self) -> None: self._has("archive_asset")
    def test_on_asset_selected(self) -> None: self._has("on_asset_selected")
    def test_create_character(self) -> None: self._has("create_character")
    def test_add_character_reference_asset(self) -> None: self._has("add_character_reference_asset")
    def test_remove_character_reference_asset(self) -> None: self._has("remove_character_reference_asset")
    def test_archive_character(self) -> None: self._has("archive_character")
    def test_on_character_selected(self) -> None: self._has("on_character_selected")

    # From TASK-000041
    def test_validate_afl_structure(self) -> None: self._has("validate_afl_structure")
    def test_on_afl_report_selected(self) -> None: self._has("on_afl_report_selected")
    def test_create_export_artifact(self) -> None: self._has("create_export_artifact")
    def test_mark_export_ready(self) -> None: self._has("mark_export_ready")
    def test_mark_export_failed(self) -> None: self._has("mark_export_failed")
    def test_on_export_artifact_selected(self) -> None: self._has("on_export_artifact_selected")
    def test_register_plugin(self) -> None: self._has("register_plugin")
    def test_enable_plugin(self) -> None: self._has("enable_plugin")
    def test_disable_plugin(self) -> None: self._has("disable_plugin")
    def test_on_plugin_selected(self) -> None: self._has("on_plugin_selected")


# ---------------------------------------------------------------------------
# 6. UISession get_app_state includes all collections
# ---------------------------------------------------------------------------

class TestGetAppStateCollections(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.actions import UISession
        self.session = UISession()
        self._tmpdir = tempfile.mkdtemp(prefix="aurora_lay_")
        r = self.session.create_project(self._tmpdir, "Layout Test")
        self.assertTrue(r.ok, r.message)

    def test_get_app_state_ok(self) -> None:
        self.assertTrue(self.session.get_app_state().ok)

    def test_has_scenes(self) -> None:
        self.assertIn("scenes", self.session.get_app_state().payload or {})

    def test_has_shots(self) -> None:
        self.assertIn("shots", self.session.get_app_state().payload or {})

    def test_has_timelines(self) -> None:
        self.assertIn("timelines", self.session.get_app_state().payload or {})

    def test_has_assets(self) -> None:
        self.assertIn("assets", self.session.get_app_state().payload or {})

    def test_has_characters(self) -> None:
        self.assertIn("characters", self.session.get_app_state().payload or {})

    def test_has_afl_reports(self) -> None:
        self.assertIn("afl_reports", self.session.get_app_state().payload or {})

    def test_has_export_artifacts(self) -> None:
        self.assertIn("export_artifacts", self.session.get_app_state().payload or {})

    def test_has_plugins(self) -> None:
        self.assertIn("plugins", self.session.get_app_state().payload or {})

    def test_json_serializable(self) -> None:
        json.dumps(self.session.get_app_state().payload)


# ---------------------------------------------------------------------------
# 7. UISession regression — Scene/Shot actions
# ---------------------------------------------------------------------------

class TestUISessionSceneShot(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.actions import UISession
        self.session = UISession()
        self._tmpdir = tempfile.mkdtemp(prefix="aurora_ss_")
        self.session.create_project(self._tmpdir, "SS Test")

    def test_create_scene(self) -> None:
        r = self.session.create_scene("Act I")
        self.assertTrue(r.ok)

    def test_create_shot(self) -> None:
        r1 = self.session.create_scene("Act I")
        scene_id = (r1.payload or {}).get("scene_id", "")
        r2 = self.session.create_shot(scene_id, "Opening")
        self.assertTrue(r2.ok)

    def test_set_active_scene(self) -> None:
        r1 = self.session.create_scene("Act II")
        scene_id = (r1.payload or {}).get("scene_id", "")
        r2 = self.session.set_active_scene(scene_id)
        self.assertIsInstance(r2.ok, bool)


# ---------------------------------------------------------------------------
# 8. UISession regression — Timeline/Asset/Character actions
# ---------------------------------------------------------------------------

class TestUISessionTAC(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.actions import UISession
        self.session = UISession()
        self._tmpdir = tempfile.mkdtemp(prefix="aurora_tac_")
        self.session.create_project(self._tmpdir, "TAC Test")

    def test_create_timeline(self) -> None:
        r = self.session.create_timeline("Main Timeline")
        self.assertTrue(r.ok)

    def test_import_asset(self) -> None:
        r = self.session.import_asset("image", "Hero Shot", "/tmp/hero.png")
        self.assertTrue(r.ok)

    def test_create_character(self) -> None:
        r = self.session.create_character("Aurora", "Lead character")
        self.assertTrue(r.ok)


# ---------------------------------------------------------------------------
# 9. UISession regression — AFL/Export/Plugin actions
# ---------------------------------------------------------------------------

class TestUISessionAEP(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.actions import UISession
        self.session = UISession()
        self._tmpdir = tempfile.mkdtemp(prefix="aurora_aep_")
        self.session.create_project(self._tmpdir, "AEP Test")

    def test_validate_afl_valid(self) -> None:
        r = self.session.validate_afl_structure("t", '{"kind": "smoke"}')
        self.assertTrue(r.ok)

    def test_validate_afl_invalid(self) -> None:
        r = self.session.validate_afl_structure("t", "bad json")
        self.assertFalse(r.ok)

    def test_create_export_artifact(self) -> None:
        r = self.session.create_export_artifact("src", "prompt", "content")
        self.assertTrue(r.ok)

    def test_register_plugin(self) -> None:
        r = self.session.register_plugin("test-plugin", "1.0.0")
        self.assertTrue(r.ok)

    def test_enable_plugin(self) -> None:
        r1 = self.session.register_plugin("en-plugin", "1.0.0")
        pid = (r1.payload or {}).get("plugin_id", "")
        r2 = self.session.enable_plugin(pid)
        self.assertIsInstance(r2.ok, bool)


# ---------------------------------------------------------------------------
# 10. headless-smoke CLI
# ---------------------------------------------------------------------------

class TestHeadlessSmokeCLI(unittest.TestCase):

    def test_main_headless_returns_zero(self) -> None:
        from aurora_studio.ui.desktop_shell import main
        self.assertEqual(main(["--headless-smoke"]), 0)


if __name__ == "__main__":
    unittest.main()
