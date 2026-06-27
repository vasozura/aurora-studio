"""Tests for TASK-000043: Desktop Usability Hardening.

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
        import aurora_studio.ui.desktop_shell  # noqa

    def test_normalize_ui_error_importable(self) -> None:
        from aurora_studio.ui.desktop_shell import normalize_ui_error
        self.assertTrue(callable(normalize_ui_error))

    def test_shortcuts_constant_importable(self) -> None:
        from aurora_studio.ui.desktop_shell import SHORTCUTS
        self.assertIsInstance(SHORTCUTS, dict)

    def test_import_does_not_open_window(self) -> None:
        from aurora_studio.ui import desktop_shell
        self.assertTrue(hasattr(desktop_shell, "DesktopShell"))


# ---------------------------------------------------------------------------
# 2. normalize_ui_error
# ---------------------------------------------------------------------------

class TestNormalizeUIError(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.desktop_shell import normalize_ui_error
        self.fn = normalize_ui_error

    def test_none_returns_unknown(self) -> None:
        self.assertEqual(self.fn(None), "Unknown error")

    def test_empty_string_returns_unknown(self) -> None:
        self.assertEqual(self.fn(""), "Unknown error")

    def test_whitespace_only_returns_unknown(self) -> None:
        self.assertEqual(self.fn("   "), "Unknown error")

    def test_normal_message_returned(self) -> None:
        self.assertEqual(self.fn("something went wrong"), "something went wrong")

    def test_multiline_collapsed(self) -> None:
        result = self.fn("line one\nline two\nline three")
        self.assertNotIn("\n", result)
        self.assertIn("line one", result)
        self.assertIn("line two", result)

    def test_long_message_trimmed(self) -> None:
        long_msg = "x" * 300
        result = self.fn(long_msg)
        self.assertLessEqual(len(result), 210)

    def test_long_message_ends_with_ellipsis(self) -> None:
        result = self.fn("a" * 300)
        self.assertTrue(result.endswith("..."))

    def test_exception_object(self) -> None:
        result = self.fn(ValueError("bad value"))
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_integer_input(self) -> None:
        result = self.fn(42)
        self.assertIsInstance(result, str)

    def test_dict_input(self) -> None:
        result = self.fn({"error": "oops"})
        self.assertIsInstance(result, str)

    def test_tabs_collapsed(self) -> None:
        result = self.fn("col1\tcol2\tcol3")
        self.assertNotIn("\t", result)


# ---------------------------------------------------------------------------
# 3. headless_smoke includes shortcuts
# ---------------------------------------------------------------------------

class TestHeadlessSmoke(unittest.TestCase):

    def test_headless_smoke_ok(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        self.assertTrue(headless_smoke().get("ok"))

    def test_headless_smoke_has_shortcuts(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertIn("shortcuts", result)
        self.assertIsInstance(result["shortcuts"], dict)

    def test_headless_smoke_json_serializable(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        json.dumps(headless_smoke())

    def test_headless_smoke_shortcuts_keys(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        shortcuts = headless_smoke()["shortcuts"]
        for key in ("Ctrl+N", "Ctrl+O", "Ctrl+S", "Ctrl+R", "Ctrl+L", "F5", "Escape"):
            self.assertIn(key, shortcuts, f"Missing shortcut: {key}")


# ---------------------------------------------------------------------------
# 4. get_layout_snapshot includes shortcuts
# ---------------------------------------------------------------------------

class TestLayoutSnapshotShortcuts(unittest.TestCase):

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

    def test_layout_snapshot_has_shortcuts(self) -> None:
        shell = self._make_shell()
        snap = shell.get_layout_snapshot()
        self.assertIn("shortcuts", snap)

    def test_layout_snapshot_shortcuts_is_dict(self) -> None:
        shell = self._make_shell()
        snap = shell.get_layout_snapshot()
        self.assertIsInstance(snap["shortcuts"], dict)

    def test_layout_snapshot_shortcuts_json_serializable(self) -> None:
        shell = self._make_shell()
        json.dumps(shell.get_layout_snapshot())

    def test_layout_snapshot_shortcut_ctrl_n(self) -> None:
        shell = self._make_shell()
        shortcuts = shell.get_layout_snapshot()["shortcuts"]
        self.assertIn("Ctrl+N", shortcuts)

    def test_layout_snapshot_shortcut_ctrl_s(self) -> None:
        shell = self._make_shell()
        self.assertIn("Ctrl+S", shell.get_layout_snapshot()["shortcuts"])

    def test_layout_snapshot_shortcut_f5(self) -> None:
        shell = self._make_shell()
        self.assertIn("F5", shell.get_layout_snapshot()["shortcuts"])

    def test_layout_snapshot_shortcut_escape(self) -> None:
        shell = self._make_shell()
        self.assertIn("Escape", shell.get_layout_snapshot()["shortcuts"])

    def test_layout_snapshot_no_tkinter_objects(self) -> None:
        shell = self._make_shell()
        snap_str = json.dumps(shell.get_layout_snapshot())
        self.assertNotIn("tkinter", snap_str)


# ---------------------------------------------------------------------------
# 5. get_state_snapshot includes log_count
# ---------------------------------------------------------------------------

class TestStateSnapshotLogCount(unittest.TestCase):

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

    def test_state_snapshot_has_log_count(self) -> None:
        shell = self._make_shell()
        self.assertIn("log_count", shell.get_state_snapshot())

    def test_state_snapshot_log_count_is_int(self) -> None:
        shell = self._make_shell()
        self.assertIsInstance(shell.get_state_snapshot()["log_count"], int)

    def test_state_snapshot_log_count_initial_zero(self) -> None:
        shell = self._make_shell()
        self.assertEqual(shell.get_state_snapshot()["log_count"], 0)

    def test_state_snapshot_json_serializable(self) -> None:
        shell = self._make_shell()
        json.dumps(shell.get_state_snapshot())


# ---------------------------------------------------------------------------
# 6. DesktopShell public API — new methods
# ---------------------------------------------------------------------------

class TestDesktopShellNewMethods(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.DS = DesktopShell

    def _has(self, name: str) -> None:
        self.assertTrue(callable(getattr(self.DS, name, None)),
                        f"DesktopShell.{name} not callable")

    def test_clear_status(self) -> None: self._has("clear_status")
    def test_append_log(self) -> None: self._has("append_log")
    def test_clear_log(self) -> None: self._has("clear_log")
    def test_get_project_path_input(self) -> None: self._has("get_project_path_input")
    def test_get_project_title_input(self) -> None: self._has("get_project_title_input")
    def test_browse_project_path(self) -> None: self._has("browse_project_path")
    def test_get_layout_snapshot(self) -> None: self._has("get_layout_snapshot")
    def test_get_state_snapshot(self) -> None: self._has("get_state_snapshot")
    def test_normalize_importable(self) -> None:
        from aurora_studio.ui.desktop_shell import normalize_ui_error
        self.assertTrue(callable(normalize_ui_error))


# ---------------------------------------------------------------------------
# 7. UISession validation failures return UIActionResult with ok=False
# ---------------------------------------------------------------------------

class TestUISessionValidationFailures(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.actions import UISession, UIActionResult
        self.session = UISession()
        self.UIActionResult = UIActionResult

    def test_create_project_empty_path(self) -> None:
        r = self.session.create_project("", "Test")
        self.assertIsInstance(r, self.UIActionResult)
        self.assertFalse(r.ok)

    def test_validate_afl_invalid_json(self) -> None:
        r = self.session.validate_afl_structure("t", "not json")
        self.assertIsInstance(r, self.UIActionResult)
        self.assertFalse(r.ok)

    def test_validate_afl_not_dict(self) -> None:
        r = self.session.validate_afl_structure("t", "[1,2,3]")
        self.assertFalse(r.ok)

    def test_create_scene_no_project(self) -> None:
        r = self.session.create_scene("Scene X")
        self.assertIsInstance(r, self.UIActionResult)
        self.assertFalse(r.ok)

    def test_validation_payload_json_serializable(self) -> None:
        r = self.session.create_project("", "")
        if r.payload is not None:
            json.dumps(r.payload)

    def test_error_message_is_string(self) -> None:
        r = self.session.create_project("", "")
        self.assertIsInstance(r.message, str)


# ---------------------------------------------------------------------------
# 8. AppStateViewModel handles empty collections
# ---------------------------------------------------------------------------

class TestAppStateViewModelEmpty(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.view_models import AppStateViewModel, WorkspaceViewModel

        class FakeWS:
            active_project_id = None
            active_scene_id = None
            active_shot_id = None
            mode = "idle"

        self.ws = WorkspaceViewModel.from_state(FakeWS())
        self.AppStateViewModel = AppStateViewModel

    def test_to_dict_no_project(self) -> None:
        vm = self.AppStateViewModel(project=None, workspace=self.ws,
                                    scenes=(), shots=())
        d = vm.to_dict()
        self.assertIsNone(d["project"])

    def test_to_dict_empty_collections_json(self) -> None:
        vm = self.AppStateViewModel(project=None, workspace=self.ws,
                                    scenes=(), shots=(),
                                    timelines=(), assets=(), characters=(),
                                    afl_reports=(), export_artifacts=(), plugins=())
        json.dumps(vm.to_dict())

    def test_to_dict_all_lists_empty(self) -> None:
        vm = self.AppStateViewModel(project=None, workspace=self.ws,
                                    scenes=(), shots=())
        d = vm.to_dict()
        for key in ("scenes", "shots", "timelines", "assets", "characters",
                    "afl_reports", "export_artifacts", "plugins"):
            self.assertIsInstance(d[key], list)
            self.assertEqual(len(d[key]), 0)


# ---------------------------------------------------------------------------
# 9. UISession Scene/Shot regression
# ---------------------------------------------------------------------------

class TestUISessionSceneShotRegression(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.actions import UISession
        self._tmpdir = tempfile.mkdtemp(prefix="aurora_h_")
        self.session = UISession()
        self.session.create_project(self._tmpdir, "Hardening Test")

    def test_create_scene_ok(self) -> None:
        r = self.session.create_scene("Scene A")
        self.assertTrue(r.ok)

    def test_create_shot_ok(self) -> None:
        r1 = self.session.create_scene("Scene B")
        scene_id = (r1.payload or {}).get("scene_id", "")
        r2 = self.session.create_shot(scene_id, "Shot 1")
        self.assertTrue(r2.ok)

    def test_set_active_scene_ok(self) -> None:
        r1 = self.session.create_scene("Scene C")
        scene_id = (r1.payload or {}).get("scene_id", "")
        r2 = self.session.set_active_scene(scene_id)
        self.assertIsInstance(r2.ok, bool)


# ---------------------------------------------------------------------------
# 10. UISession Timeline/Asset/Character regression
# ---------------------------------------------------------------------------

class TestUISessionTACRegression(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.actions import UISession
        self._tmpdir = tempfile.mkdtemp(prefix="aurora_tach_")
        self.session = UISession()
        self.session.create_project(self._tmpdir, "TAC Hardening")

    def test_create_timeline_ok(self) -> None:
        r = self.session.create_timeline("Main")
        self.assertTrue(r.ok)

    def test_import_asset_ok(self) -> None:
        r = self.session.import_asset("video", "clip.mp4", "/tmp/clip.mp4")
        self.assertTrue(r.ok)

    def test_create_character_ok(self) -> None:
        r = self.session.create_character("Hero", "Protagonist")
        self.assertTrue(r.ok)


# ---------------------------------------------------------------------------
# 11. UISession AFL/Export/Plugin regression
# ---------------------------------------------------------------------------

class TestUISessionAEPRegression(unittest.TestCase):

    def setUp(self) -> None:
        from aurora_studio.ui.actions import UISession
        self._tmpdir = tempfile.mkdtemp(prefix="aurora_aeph_")
        self.session = UISession()
        self.session.create_project(self._tmpdir, "AEP Hardening")

    def test_validate_afl_valid(self) -> None:
        r = self.session.validate_afl_structure("scene:s1", '{"kind": "smoke"}')
        self.assertTrue(r.ok)

    def test_validate_afl_empty_payload(self) -> None:
        r = self.session.validate_afl_structure("t", "")
        self.assertFalse(r.ok)

    def test_create_export_ok(self) -> None:
        r = self.session.create_export_artifact("src", "prompt", "content")
        self.assertTrue(r.ok)

    def test_register_plugin_ok(self) -> None:
        r = self.session.register_plugin("plug", "0.1.0")
        self.assertTrue(r.ok)

    def test_list_plugins_ok(self) -> None:
        r = self.session.list_plugins()
        self.assertTrue(r.ok)


# ---------------------------------------------------------------------------
# 12. headless-smoke CLI
# ---------------------------------------------------------------------------

class TestHeadlessSmokeCLI(unittest.TestCase):

    def test_main_headless_returns_zero(self) -> None:
        from aurora_studio.ui.desktop_shell import main
        self.assertEqual(main(["--headless-smoke"]), 0)

    def test_main_headless_output_has_shortcuts(self) -> None:
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertIn("shortcuts", result)
        self.assertGreaterEqual(len(result["shortcuts"]), 7)


# ---------------------------------------------------------------------------
# 13. normalize_ui_error doesn't expose tracebacks
# ---------------------------------------------------------------------------

class TestNormalizeUIErrorSafety(unittest.TestCase):

    def test_traceback_string_collapsed(self) -> None:
        from aurora_studio.ui.desktop_shell import normalize_ui_error
        tb = "Traceback (most recent call last):\n  File \"foo.py\", line 10\nValueError: bad"
        result = normalize_ui_error(tb)
        self.assertNotIn("\n", result)
        self.assertLessEqual(len(result), 210)

    def test_result_always_string(self) -> None:
        from aurora_studio.ui.desktop_shell import normalize_ui_error
        for val in (None, "", 0, [], {}, Exception("x"), "normal", "a" * 500):
            result = normalize_ui_error(val)
            self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
