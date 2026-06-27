"""Tests for the first minimal AFL Engine implementation."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.afl import (
    AFL_STATUS_INVALID,
    AFL_STATUS_VALID,
    AFLValidationReport,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness
from aurora_studio.modules.afl_engine import AFLEngine


class AFLEngineImplementationTests(unittest.TestCase):
    def test_validate_structure_valid_payload(self) -> None:
        engine = AFLEngine()

        report = engine.validate_structure("scene-1", {"title": "Opening Scene"})

        self.assertIsInstance(report, AFLValidationReport)
        self.assertEqual(report.target_ref, "scene-1")
        self.assertEqual(report.status, AFL_STATUS_VALID)
        self.assertEqual(report.issues, ())

    def test_validate_structure_rejects_empty_target_ref(self) -> None:
        engine = AFLEngine()

        with self.assertRaises(ValidationError):
            engine.validate_structure("   ", {"title": "Opening Scene"})

    def test_validate_structure_invalid_non_dict_payload(self) -> None:
        engine = AFLEngine()

        report = engine.validate_structure("scene-1", "not a dict")

        self.assertEqual(report.status, AFL_STATUS_INVALID)
        self.assertTrue(len(report.issues) > 0)

    def test_validate_structure_invalid_empty_payload(self) -> None:
        engine = AFLEngine()

        report = engine.validate_structure("scene-1", {})

        self.assertEqual(report.status, AFL_STATUS_INVALID)
        self.assertTrue(len(report.issues) > 0)

    def test_validate_structure_stores_report(self) -> None:
        engine = AFLEngine()

        report = engine.validate_structure("scene-1", {"title": "Opening"})
        fetched = engine.get_validation_report(report.report_id)

        self.assertEqual(fetched.report_id, report.report_id)

    def test_validate_project_returns_reports_per_structure(self) -> None:
        engine = AFLEngine()

        structures = [
            {"target_ref": "scene-1", "payload": {"title": "Scene One"}},
            {"target_ref": "scene-2", "payload": {"title": "Scene Two"}},
        ]
        reports = engine.validate_project("project-123", structures)

        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0].target_ref, "scene-1")
        self.assertEqual(reports[1].target_ref, "scene-2")

    def test_validate_project_rejects_empty_project_id(self) -> None:
        engine = AFLEngine()

        with self.assertRaises(ValidationError):
            engine.validate_project("   ", [])

    def test_get_validation_report_rejects_missing(self) -> None:
        engine = AFLEngine()

        with self.assertRaises(ValidationError):
            engine.get_validation_report("report-missing")

    def test_list_validation_reports_all_and_filtered(self) -> None:
        engine = AFLEngine()
        engine.validate_structure("scene-1", {"title": "Opening"})
        engine.validate_structure("scene-2", {"title": "Middle"})

        all_reports = engine.list_validation_reports()
        scene_one_reports = engine.list_validation_reports("scene-1")

        self.assertEqual(len(all_reports), 2)
        self.assertEqual(len(scene_one_reports), 1)
        self.assertEqual(scene_one_reports[0].target_ref, "scene-1")

    def test_detect_conflicts_returns_empty_list(self) -> None:
        engine = AFLEngine()

        conflicts = engine.detect_conflicts([{"target_ref": "scene-1", "payload": {}}])

        self.assertEqual(conflicts, [])

    def test_detect_conflicts_rejects_non_list(self) -> None:
        engine = AFLEngine()

        with self.assertRaises(ValidationError):
            engine.detect_conflicts("not a list")

    def test_report_to_dict(self) -> None:
        engine = AFLEngine()
        report = engine.validate_structure("scene-1", {"title": "Opening"})

        data = report.to_dict()

        self.assertEqual(data["report_id"], report.report_id)
        self.assertEqual(data["target_ref"], "scene-1")
        self.assertEqual(data["status"], AFL_STATUS_VALID)

    def test_report_from_dict(self) -> None:
        engine = AFLEngine()
        report = engine.validate_structure("scene-1", {"title": "Opening"})

        restored = AFLValidationReport.from_dict(report.to_dict())

        self.assertEqual(restored.report_id, report.report_id)
        self.assertEqual(restored.target_ref, "scene-1")
        self.assertEqual(restored.status, AFL_STATUS_VALID)

    def test_afl_engine_still_reports_not_ready(self) -> None:
        engine = AFLEngine()

        self.assertEqual(engine.get_readiness(), Readiness.NOT_READY)
        self.assertIn("not ready", engine.describe().lower())


if __name__ == "__main__":
    unittest.main()
