"""Tests for TASK-000080: Provider Request/Response Log."""

import json
import unittest


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


def _make_log():
    from aurora_studio.modules.provider_log import ProviderLog
    return ProviderLog()


def _make_req_resp(prompt="Test prompt."):
    from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
    req = ProviderDryRunAdapter.build_request(
        provider_id="dry-run-local",
        source_type="scene",
        source_id="s1",
        prompt_text=prompt,
    )
    adapter = ProviderDryRunAdapter()
    resp = adapter.execute(req)
    return req, resp


class TestSanitizePreview(unittest.TestCase):
    def test_normal_text_preserved(self):
        from aurora_studio.modules.provider_log import _sanitize_preview
        result = _sanitize_preview("A beautiful mountain landscape.")
        self.assertIn("mountain", result)

    def test_secret_line_redacted(self):
        from aurora_studio.modules.provider_log import _sanitize_preview
        result = _sanitize_preview("api_key: sk-abc123def456")
        self.assertIn("[REDACTED]", result)
        self.assertNotIn("sk-abc123", result)

    def test_token_line_redacted(self):
        from aurora_studio.modules.provider_log import _sanitize_preview
        result = _sanitize_preview("token: mySecretToken")
        self.assertIn("[REDACTED]", result)

    def test_long_text_truncated(self):
        from aurora_studio.modules.provider_log import _sanitize_preview
        result = _sanitize_preview("A" * 200)
        self.assertLessEqual(len(result), 120)


class TestProviderLogRecord(unittest.TestCase):
    def test_record_entry(self):
        log = _make_log()
        req, resp = _make_req_resp()
        entry = log.record(req, resp)
        self.assertEqual(entry.request_id, req.request_id)
        self.assertEqual(entry.response_id, resp.response_id)
        self.assertEqual(entry.provider_id, "dry-run-local")
        self.assertEqual(entry.status, "dry_run")

    def test_record_increments_count(self):
        log = _make_log()
        req, resp = _make_req_resp("First.")
        log.record(req, resp)
        req2, resp2 = _make_req_resp("Second.")
        log.record(req2, resp2)
        self.assertEqual(log.count(), 2)

    def test_entry_has_prompt_preview(self):
        log = _make_log()
        req, resp = _make_req_resp("Visible prompt text.")
        entry = log.record(req, resp)
        self.assertTrue(entry.prompt_preview.strip())

    def test_entry_does_not_contain_full_prompt(self):
        log = _make_log()
        long_prompt = "Word " * 100
        req, resp = _make_req_resp(long_prompt)
        entry = log.record(req, resp)
        self.assertLessEqual(len(entry.prompt_preview), 120)

    def test_entry_to_dict_json_serializable(self):
        log = _make_log()
        req, resp = _make_req_resp("JSON check.")
        entry = log.record(req, resp)
        json.dumps(entry.to_dict())


class TestProviderLogList(unittest.TestCase):
    def test_list_returns_most_recent_first(self):
        log = _make_log()
        for i in range(3):
            req, resp = _make_req_resp(f"Prompt {i}.")
            log.record(req, resp)
        entries = log.list_entries()
        self.assertEqual(len(entries), 3)
        # Most recent first — last prompt recorded is "Prompt 2."
        self.assertIn("2", entries[0].prompt_preview)

    def test_list_filter_by_provider(self):
        log = _make_log()
        req, resp = _make_req_resp("Filter test.")
        log.record(req, resp)
        entries = log.list_entries(provider_id="dry-run-local")
        self.assertEqual(len(entries), 1)

    def test_list_filter_by_nonexistent_provider(self):
        log = _make_log()
        req, resp = _make_req_resp("Another.")
        log.record(req, resp)
        entries = log.list_entries(provider_id="other-provider")
        self.assertEqual(len(entries), 0)

    def test_list_limit(self):
        log = _make_log()
        for i in range(5):
            req, resp = _make_req_resp(f"Entry {i}.")
            log.record(req, resp)
        entries = log.list_entries(limit=3)
        self.assertEqual(len(entries), 3)


class TestProviderLogClear(unittest.TestCase):
    def test_clear_returns_count(self):
        log = _make_log()
        for _ in range(4):
            req, resp = _make_req_resp("Clear test.")
            log.record(req, resp)
        count = log.clear()
        self.assertEqual(count, 4)

    def test_clear_empties_log(self):
        log = _make_log()
        req, resp = _make_req_resp("Before clear.")
        log.record(req, resp)
        log.clear()
        self.assertEqual(log.count(), 0)


class TestUISessionLogMethods(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_list_logs_initially_empty(self):
        r = self.sess.list_provider_logs()
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 0)

    def test_dry_run_creates_log_entry(self):
        self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s1",
            prompt_text="Logging test prompt.",
        )
        r = self.sess.list_provider_logs()
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 1)

    def test_list_logs_json_serializable(self):
        self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text="Serialization prompt.",
        )
        r = self.sess.list_provider_logs()
        self.assertTrue(r.ok)
        json.dumps(r.payload)

    def test_clear_logs(self):
        self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text="Clear me.",
        )
        r_clear = self.sess.clear_provider_logs()
        self.assertTrue(r_clear.ok)
        self.assertEqual(r_clear.payload["cleared"], 1)

    def test_clear_then_list_empty(self):
        self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text="Clear then list.",
        )
        self.sess.clear_provider_logs()
        r = self.sess.list_provider_logs()
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 0)

    def test_log_entry_has_dry_run_status(self):
        self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s2",
            prompt_text="Status check.",
        )
        r = self.sess.list_provider_logs()
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["logs"][0]["status"], "dry_run")

    def test_log_entry_prompt_preview_not_full_text(self):
        long_prompt = "X " * 100
        self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text=long_prompt,
        )
        r = self.sess.list_provider_logs()
        preview = r.payload["logs"][0]["prompt_preview"]
        self.assertLessEqual(len(preview), 120)


class TestDesktopLogMethods(unittest.TestCase):
    def test_refresh_provider_logs_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "refresh_provider_logs"))

    def test_clear_provider_logs_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "clear_provider_logs"))


if __name__ == "__main__":
    unittest.main()
