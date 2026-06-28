"""Tests for TASK-000081: Prompt Execution Queue."""

import json
import unittest


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


def _make_queue():
    from aurora_studio.modules.prompt_execution_queue import PromptExecutionQueue
    return PromptExecutionQueue()


def _make_request(prompt="Test prompt.", source_type="scene", source_id="s1"):
    import uuid
    from datetime import datetime, timezone
    from aurora_studio.contracts.prompt_execution import PromptExecutionRequest
    return PromptExecutionRequest(
        request_id=f"req-{uuid.uuid4().hex[:8]}",
        project_id="proj-1",
        provider_id="dry-run-local",
        source_type=source_type,
        source_id=source_id,
        prompt_text=prompt,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


class TestPromptExecutionRequestSerialization(unittest.TestCase):
    def test_to_dict_json_serializable(self):
        req = _make_request()
        json.dumps(req.to_dict())

    def test_from_dict_roundtrip(self):
        from aurora_studio.contracts.prompt_execution import PromptExecutionRequest
        req = _make_request()
        restored = PromptExecutionRequest.from_dict(req.to_dict())
        self.assertEqual(restored.request_id, req.request_id)
        self.assertEqual(restored.prompt_text, req.prompt_text)


class TestQueueItemSerialization(unittest.TestCase):
    def test_queue_item_to_dict_json_serializable(self):
        q = _make_queue()
        req = _make_request()
        item = q.enqueue_request(req)
        json.dumps(item.to_dict())

    def test_queue_status_to_dict_json_serializable(self):
        q = _make_queue()
        req = _make_request()
        q.enqueue_request(req)
        status = q.queue_status()
        json.dumps(status.to_dict())


class TestEnqueue(unittest.TestCase):
    def test_enqueue_returns_item(self):
        q = _make_queue()
        req = _make_request()
        item = q.enqueue_request(req)
        self.assertEqual(item.status, "queued")
        self.assertEqual(item.request_id, req.request_id)

    def test_enqueue_empty_provider_raises(self):
        from aurora_studio.core.errors import ValidationError
        import uuid
        from aurora_studio.contracts.prompt_execution import PromptExecutionRequest
        q = _make_queue()
        req = PromptExecutionRequest(
            request_id=f"req-{uuid.uuid4().hex[:8]}",
            project_id="",
            provider_id="",
            source_type="scene",
            source_id="s1",
            prompt_text="Test.",
        )
        with self.assertRaises(ValidationError):
            q.enqueue_request(req)

    def test_enqueue_empty_source_type_raises(self):
        from aurora_studio.core.errors import ValidationError
        import uuid
        from aurora_studio.contracts.prompt_execution import PromptExecutionRequest
        q = _make_queue()
        req = PromptExecutionRequest(
            request_id=f"req-{uuid.uuid4().hex[:8]}",
            project_id="",
            provider_id="dry-run-local",
            source_type="",
            source_id="s1",
            prompt_text="Test.",
        )
        with self.assertRaises(ValidationError):
            q.enqueue_request(req)

    def test_enqueue_empty_prompt_raises(self):
        from aurora_studio.core.errors import ValidationError
        import uuid
        from aurora_studio.contracts.prompt_execution import PromptExecutionRequest
        q = _make_queue()
        req = PromptExecutionRequest(
            request_id=f"req-{uuid.uuid4().hex[:8]}",
            project_id="",
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s1",
            prompt_text="   ",
        )
        with self.assertRaises(ValidationError):
            q.enqueue_request(req)


class TestListItems(unittest.TestCase):
    def test_list_all(self):
        q = _make_queue()
        q.enqueue_request(_make_request("P1."))
        q.enqueue_request(_make_request("P2."))
        self.assertEqual(len(q.list_items()), 2)

    def test_filter_by_status(self):
        q = _make_queue()
        item = q.enqueue_request(_make_request("P."))
        q.mark_completed(item.queue_item_id)
        queued = q.list_items(status="queued")
        completed = q.list_items(status="completed")
        self.assertEqual(len(queued), 0)
        self.assertEqual(len(completed), 1)

    def test_filter_by_provider(self):
        q = _make_queue()
        q.enqueue_request(_make_request("P."))
        items = q.list_items(provider_id="dry-run-local")
        self.assertEqual(len(items), 1)

    def test_filter_by_source_type(self):
        q = _make_queue()
        q.enqueue_request(_make_request(source_type="shot"))
        items = q.list_items(source_type="scene")
        self.assertEqual(len(items), 0)
        items = q.list_items(source_type="shot")
        self.assertEqual(len(items), 1)


class TestStateTransitions(unittest.TestCase):
    def test_mark_running(self):
        q = _make_queue()
        item = q.enqueue_request(_make_request())
        updated = q.mark_running(item.queue_item_id)
        self.assertEqual(updated.status, "running")

    def test_mark_completed(self):
        q = _make_queue()
        item = q.enqueue_request(_make_request())
        q.mark_running(item.queue_item_id)
        updated = q.mark_completed(item.queue_item_id)
        self.assertEqual(updated.status, "completed")
        self.assertEqual(updated.attempt_count, 1)

    def test_mark_failed(self):
        q = _make_queue()
        item = q.enqueue_request(_make_request())
        updated = q.mark_failed(item.queue_item_id, "Something went wrong")
        self.assertEqual(updated.status, "failed")
        self.assertEqual(updated.error_message, "Something went wrong")

    def test_mark_blocked(self):
        q = _make_queue()
        item = q.enqueue_request(_make_request())
        updated = q.mark_blocked(item.queue_item_id, "Blocked by policy")
        self.assertEqual(updated.status, "blocked")

    def test_cancel_item(self):
        q = _make_queue()
        item = q.enqueue_request(_make_request())
        updated = q.cancel_item(item.queue_item_id)
        self.assertEqual(updated.status, "cancelled")

    def test_clear_completed(self):
        q = _make_queue()
        item = q.enqueue_request(_make_request())
        q.mark_completed(item.queue_item_id)
        count = q.clear_completed()
        self.assertEqual(count, 1)
        self.assertEqual(len(q.list_items()), 0)


class TestExecuteNextDryRun(unittest.TestCase):
    def test_execute_next_returns_none_when_empty(self):
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        q = _make_queue()
        result = q.execute_next_with_dry_run(ProviderDryRunAdapter())
        self.assertIsNone(result)

    def test_execute_next_completes_item(self):
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        q = _make_queue()
        req = _make_request("Execute this prompt.")
        q.enqueue_request(req)
        result = q.execute_next_with_dry_run(ProviderDryRunAdapter())
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "completed")

    def test_execute_next_json_serializable(self):
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        q = _make_queue()
        q.enqueue_request(_make_request("JSON check."))
        result = q.execute_next_with_dry_run(ProviderDryRunAdapter())
        json.dumps(result)

    def test_no_background_thread_created(self):
        import threading
        before = threading.active_count()
        q = _make_queue()
        q.enqueue_request(_make_request("Thread check."))
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        q.execute_next_with_dry_run(ProviderDryRunAdapter())
        after = threading.active_count()
        self.assertEqual(before, after)


class TestUISessionQueueMethods(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_enqueue_ok(self):
        r = self.sess.enqueue_prompt_execution(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s1",
            prompt_text="A scene description.",
        )
        self.assertTrue(r.ok, r.message)
        self.assertIn("item", r.payload)

    def test_enqueue_json_serializable(self):
        r = self.sess.enqueue_prompt_execution(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s1",
            prompt_text="Serializable.",
        )
        self.assertTrue(r.ok)
        json.dumps(r.payload)

    def test_enqueue_empty_prompt_fails(self):
        r = self.sess.enqueue_prompt_execution(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s1",
            prompt_text="   ",
        )
        self.assertFalse(r.ok)

    def test_enqueue_empty_source_type_fails(self):
        r = self.sess.enqueue_prompt_execution(
            provider_id="dry-run-local",
            source_type="",
            source_id="s1",
            prompt_text="Prompt.",
        )
        self.assertFalse(r.ok)

    def test_enqueue_unknown_provider_fails(self):
        r = self.sess.enqueue_prompt_execution(
            provider_id="nonexistent-provider",
            source_type="scene",
            source_id="s1",
            prompt_text="Should fail.",
        )
        self.assertFalse(r.ok)

    def test_list_queue(self):
        self.sess.enqueue_prompt_execution("dry-run-local", "scene", "s1", "Prompt.")
        r = self.sess.list_prompt_execution_queue()
        self.assertTrue(r.ok)
        self.assertIn("items", r.payload)
        self.assertIn("status", r.payload)

    def test_cancel_item(self):
        r_enq = self.sess.enqueue_prompt_execution("dry-run-local", "scene", "s1", "Cancel me.")
        qid = r_enq.payload["item"]["queue_item_id"]
        r_cancel = self.sess.cancel_prompt_execution(qid)
        self.assertTrue(r_cancel.ok)
        self.assertEqual(r_cancel.payload["status"], "cancelled")

    def test_run_next_dry_run_no_items(self):
        r = self.sess.run_next_prompt_execution_dry_run()
        self.assertTrue(r.ok)
        self.assertFalse(r.payload.get("ran"))

    def test_run_next_dry_run_executes(self):
        self.sess.enqueue_prompt_execution("dry-run-local", "scene", "s1", "Run this.")
        r = self.sess.run_next_prompt_execution_dry_run()
        self.assertTrue(r.ok, r.message)
        self.assertTrue(r.payload.get("ran"))


class TestDesktopQueueMethods(unittest.TestCase):
    def test_enqueue_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "enqueue_prompt_execution"))

    def test_run_next_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "run_next_prompt_execution_dry_run"))

    def test_cancel_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "cancel_selected_queue_item"))

    def test_refresh_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "refresh_prompt_queue"))


if __name__ == "__main__":
    unittest.main()
