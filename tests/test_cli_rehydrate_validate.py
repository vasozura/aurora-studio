"""Tests for CLI validate-bundle and rehydrate-bundle commands — TASK-000035."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"


def _run(*args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": "/tmp/pycache"}
    return subprocess.run(
        [sys.executable, "-m", "aurora_studio.cli", *args],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )


def _create_demo(tmp: str) -> dict:
    result = _run("create-demo", "--path", tmp, "--title", "Test Project")
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# validate-bundle tests
# ---------------------------------------------------------------------------

class TestValidateBundle(unittest.TestCase):

    def test_validate_exits_zero_after_demo(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("validate-bundle", "--path", tmp)
            self.assertEqual(result.returncode, 0)

    def test_validate_outputs_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("validate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertIsInstance(data, dict)

    def test_validate_ok_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("validate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertTrue(data["valid"])

    def test_validate_includes_schema_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("validate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertIn("schema_version", data)
            self.assertEqual(data["schema_version"], "0.1.0")

    def test_validate_includes_all_count_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("validate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            for key in ("scene_count", "shot_count", "timeline_count",
                        "asset_count", "character_count", "afl_report_count",
                        "export_artifact_count", "plugin_count"):
                self.assertIn(key, data)

    def test_validate_counts_match_demo(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("validate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertGreaterEqual(data["scene_count"], 1)
            self.assertGreaterEqual(data["shot_count"], 1)

    def test_validate_rejects_missing_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = str(Path(tmp) / "nonexistent")
            result = _run("validate-bundle", "--path", bad)
            self.assertNotEqual(result.returncode, 0)

    def test_validate_error_is_json_to_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = str(Path(tmp) / "nonexistent")
            result = _run("validate-bundle", "--path", bad)
            err = json.loads(result.stderr)
            self.assertFalse(err["ok"])
            self.assertIn("error", err)

    def test_validate_does_not_rehydrate(self):
        """validate-bundle must not write or change anything."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            before = set(Path(tmp).iterdir())
            _run("validate-bundle", "--path", tmp)
            after = set(Path(tmp).iterdir())
            self.assertEqual(before, after)


# ---------------------------------------------------------------------------
# rehydrate-bundle tests
# ---------------------------------------------------------------------------

class TestRehydrateBundle(unittest.TestCase):

    def test_rehydrate_exits_zero_after_demo(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("rehydrate-bundle", "--path", tmp)
            self.assertEqual(result.returncode, 0)

    def test_rehydrate_outputs_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("rehydrate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertIsInstance(data, dict)

    def test_rehydrate_ok_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("rehydrate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])

    def test_rehydrate_rehydrated_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("rehydrate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertTrue(data["rehydrated"])

    def test_rehydrate_includes_all_required_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("rehydrate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            for key in ("ok", "schema_version", "rehydrated", "workspace_restored",
                        "scenes", "shots", "timelines", "assets", "characters",
                        "afl_reports", "export_artifacts", "plugins",
                        "active_project_id", "active_scene_id", "active_shot_id"):
                self.assertIn(key, data, f"Missing key: {key}")

    def test_rehydrate_scene_and_shot_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("rehydrate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertGreaterEqual(data["scenes"], 1)
            self.assertGreaterEqual(data["shots"], 1)

    def test_rehydrate_workspace_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("rehydrate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertTrue(data["workspace_restored"])

    def test_rehydrate_active_project_id_not_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            demo = _create_demo(tmp)
            result = _run("rehydrate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertIsNotNone(data["active_project_id"])
            self.assertNotEqual(data["active_project_id"], "")
            self.assertEqual(data["active_project_id"], demo["project_id"])

    def test_rehydrate_active_scene_id_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            demo = _create_demo(tmp)
            result = _run("rehydrate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertEqual(data["active_scene_id"], demo["scene_id"])

    def test_rehydrate_rejects_missing_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = str(Path(tmp) / "nonexistent")
            result = _run("rehydrate-bundle", "--path", bad)
            self.assertNotEqual(result.returncode, 0)

    def test_rehydrate_error_is_json_to_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = str(Path(tmp) / "nonexistent")
            result = _run("rehydrate-bundle", "--path", bad)
            err = json.loads(result.stderr)
            self.assertFalse(err["ok"])
            self.assertIn("error", err)

    def test_rehydrate_schema_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("rehydrate-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertEqual(data["schema_version"], "0.1.0")


# ---------------------------------------------------------------------------
# Compatibility: existing commands still work
# ---------------------------------------------------------------------------

class TestExistingCommandsStillWork(unittest.TestCase):

    def test_smoke_still_works(self):
        result = _run("smoke")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])

    def test_inspect_bundle_still_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            _create_demo(tmp)
            result = _run("inspect-bundle", "--path", tmp)
            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertIn("scene_count", data)

    def test_help_includes_new_commands(self):
        result = _run("--help")
        self.assertIn("validate-bundle", result.stdout)
        self.assertIn("rehydrate-bundle", result.stdout)


if __name__ == "__main__":
    unittest.main()
