"""Tests for TASK-000083: Prompt Run History."""

import json
import unittest


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


def _make_provider_req_resp(prompt="Test prompt."):
    from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
    req = ProviderDryRunAdapter.build_request("dry-run-local", "scene", "s1", prompt)
    resp = ProviderDryRunAdapter().execute(req)
    return req, resp


def _make_batch_req_result():
    import uuid
    from aurora_studio.contracts.prompt_execution import (
        BatchPromptExportRequest, BatchPromptExportResult, BatchPromptExportItemResult
    )
    req = BatchPromptExportRequest(
        batch_id=f"b-{uuid.uuid4().hex[:8]}",
        project_id="proj-1",
        source_type="scene",
        source_ids=("s1", "s2"),
        template_id="default-scene-basic",
    )
    result = BatchPromptExportResult(
        batch_id=req.batch_id,
        status="completed",
        total_count=2,
        success_count=2,
        failed_count=0,
        items=(
            BatchPromptExportItemResult("s1", "completed", "art-1"),
            BatchPromptExportItemResult("s2", "completed", "art-2"),
        ),
    )
    return req, result


class TestSanitizePreview(unittest.TestCase):
    def test_normal_text_preserved(self):
        from aurora_studio.modules.prompt_run_history import sanitize_preview
        result = sanitize_preview("Beautiful mountain at dawn.")
        self.assertIn("mountain", result)

    def test_secret_line_redacted(self):
        from aurora_studio.modules.prompt_run_history import sanitize_preview
        result = sanitize_preview("api_key: abc123")
        self.assertIn("[REDACTED]", result)
        self.assertNotIn("abc123", result)

    def test_long_text_truncated(self):
        from aurora_studio.modules.prompt_run_history import sanitize_preview
        result = sanitize_preview("A" * 200)
        self.assertLessEqual(len(result), 120)

    def test_multiline_text_collapses(self):
        from aurora_studio.modules.prompt_run_history import sanitize_preview
        result = sanitize_preview("Line one.\nLine two.\nLine three.")
        self.assertNotIn("\n", result)


class TestRecordDryRun(unittest.TestCase):
    def test_record_dry_run(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, resp = _make_provider_req_resp("Dry run history test.")
        record = h.record_dry_run(req, resp)
        self.assertEqual(record.run_type, "dry_run")
        self.assertEqual(record.provider_id, "dry-run-local")
        self.assertEqual(record.status, "dry_run")

    def test_dry_run_preview_non_empty(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, resp = _make_provider_req_resp("Visible prompt.")
        record = h.record_dry_run(req, resp)
        self.assertTrue(record.prompt_preview.strip())

    def test_dry_run_preview_truncated(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, resp = _make_provider_req_resp("W " * 100)
        record = h.record_dry_run(req, resp)
        self.assertLessEqual(len(record.prompt_preview), 120)

    def test_no_secrets_in_preview(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, resp = _make_provider_req_resp("api_key: sk-secret123")
        record = h.record_dry_run(req, resp)
        self.assertNotIn("sk-secret123", record.prompt_preview)


class TestRecordBatchResult(unittest.TestCase):
    def test_record_batch_result(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, result = _make_batch_req_result()
        records = h.record_batch_result(req, result)
        self.assertEqual(len(records), 2)

    def test_batch_record_run_type(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, result = _make_batch_req_result()
        records = h.record_batch_result(req, result)
        self.assertTrue(all(r.run_type == "batch_export" for r in records))

    def test_batch_record_artifact_ids(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, result = _make_batch_req_result()
        records = h.record_batch_result(req, result)
        self.assertTrue(all(r.artifact_id for r in records))


class TestRecordManualExport(unittest.TestCase):
    def test_record_manual_export(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        record = h.record_manual_export("scene", "s1", "art-99", profile_id="prof-1")
        self.assertEqual(record.run_type, "manual_export")
        self.assertEqual(record.status, "completed")
        self.assertEqual(record.artifact_id, "art-99")


class TestListHistory(unittest.TestCase):
    def test_list_all(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, resp = _make_provider_req_resp("Entry 1.")
        h.record_dry_run(req, resp)
        h.record_manual_export("scene", "s1", "art-1")
        self.assertEqual(len(h.list_history()), 2)

    def test_filter_by_run_type(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, resp = _make_provider_req_resp("Dry run entry.")
        h.record_dry_run(req, resp)
        h.record_manual_export("scene", "s1", "art-1")
        results = h.list_history(run_type="dry_run")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].run_type, "dry_run")

    def test_filter_by_status(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, resp = _make_provider_req_resp("Status filter.")
        h.record_dry_run(req, resp)
        h.record_manual_export("scene", "s1", "art-1")
        completed = h.list_history(status="completed")
        self.assertTrue(all(r.status == "completed" for r in completed))

    def test_history_json_serializable(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, resp = _make_provider_req_resp("JSON check.")
        h.record_dry_run(req, resp)
        records = h.list_history()
        json.dumps([r.to_dict() for r in records])

    def test_clear_history(self):
        from aurora_studio.modules.prompt_run_history import PromptRunHistory
        h = PromptRunHistory()
        req, resp = _make_provider_req_resp("Clear this.")
        h.record_dry_run(req, resp)
        count = h.clear_history()
        self.assertEqual(count, 1)
        self.assertEqual(h.count(), 0)


class TestUISessionHistoryMethods(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_list_history_initially_empty(self):
        r = self.sess.list_prompt_run_history()
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 0)

    def test_dry_run_creates_history_entry(self):
        self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s1",
            prompt_text="History integration test.",
        )
        r = self.sess.list_prompt_run_history()
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 1)

    def test_history_json_serializable(self):
        self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text="JSON history.",
        )
        r = self.sess.list_prompt_run_history()
        self.assertTrue(r.ok)
        json.dumps(r.payload)

    def test_clear_history(self):
        self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text="Clear me.",
        )
        r = self.sess.clear_prompt_run_history()
        self.assertTrue(r.ok)

    def test_filter_by_run_type(self):
        self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s1",
            prompt_text="Typed.",
        )
        r = self.sess.list_prompt_run_history(run_type="dry_run")
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 1)


class TestDesktopHistoryMethods(unittest.TestCase):
    def test_refresh_run_history_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "refresh_run_history"))

    def test_clear_run_history_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "clear_run_history"))


if __name__ == "__main__":
    unittest.main()
