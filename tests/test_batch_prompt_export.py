"""Tests for TASK-000082: Batch Prompt Export."""

import json
import unittest


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


def _make_batch_manager():
    from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
    return BatchPromptExportManager()


def _make_batch_request(source_ids=("s1", "s2"), template_id="default-scene-basic", profile_id=""):
    import uuid
    from datetime import datetime, timezone
    from aurora_studio.contracts.prompt_execution import BatchPromptExportRequest
    return BatchPromptExportRequest(
        batch_id=f"batch-{uuid.uuid4().hex[:8]}",
        project_id="proj-1",
        source_type="scene",
        source_ids=tuple(source_ids),
        template_id=template_id,
        profile_id=profile_id,
        artifact_type="prompt",
        created_at=datetime.now(timezone.utc).isoformat(),
    )


class TestBatchRequestSerialization(unittest.TestCase):
    def test_to_dict_json_serializable(self):
        req = _make_batch_request()
        json.dumps(req.to_dict())

    def test_from_dict_roundtrip(self):
        from aurora_studio.contracts.prompt_execution import BatchPromptExportRequest
        req = _make_batch_request()
        restored = BatchPromptExportRequest.from_dict(req.to_dict())
        self.assertEqual(restored.batch_id, req.batch_id)
        self.assertEqual(restored.source_ids, req.source_ids)


class TestBatchResultSerialization(unittest.TestCase):
    def test_result_to_dict_json_serializable(self):
        from aurora_studio.contracts.prompt_execution import (
            BatchPromptExportResult, BatchPromptExportItemResult
        )
        result = BatchPromptExportResult(
            batch_id="batch-1",
            status="completed",
            total_count=2,
            success_count=2,
            failed_count=0,
            items=(
                BatchPromptExportItemResult("s1", "completed", "art-1"),
                BatchPromptExportItemResult("s2", "completed", "art-2"),
            ),
        )
        json.dumps(result.to_dict())


class TestBatchValidation(unittest.TestCase):
    def test_empty_source_ids_invalid(self):
        import uuid
        from aurora_studio.contracts.prompt_execution import BatchPromptExportRequest
        req = BatchPromptExportRequest(
            batch_id=f"b-{uuid.uuid4().hex[:8]}",
            project_id="",
            source_type="scene",
            source_ids=(),
            template_id="default-scene-basic",
        )
        mgr = _make_batch_manager()
        errors = mgr.validate_batch_request(req)
        self.assertTrue(len(errors) > 0)

    def test_empty_source_type_invalid(self):
        import uuid
        from aurora_studio.contracts.prompt_execution import BatchPromptExportRequest
        req = BatchPromptExportRequest(
            batch_id=f"b-{uuid.uuid4().hex[:8]}",
            project_id="",
            source_type="",
            source_ids=("s1",),
            template_id="default-scene-basic",
        )
        mgr = _make_batch_manager()
        errors = mgr.validate_batch_request(req)
        self.assertTrue(len(errors) > 0)

    def test_neither_template_nor_profile_invalid(self):
        import uuid
        from aurora_studio.contracts.prompt_execution import BatchPromptExportRequest
        req = BatchPromptExportRequest(
            batch_id=f"b-{uuid.uuid4().hex[:8]}",
            project_id="",
            source_type="scene",
            source_ids=("s1",),
            template_id="",
            profile_id="",
        )
        mgr = _make_batch_manager()
        errors = mgr.validate_batch_request(req)
        self.assertTrue(len(errors) > 0)

    def test_valid_request_no_errors(self):
        req = _make_batch_request()
        mgr = _make_batch_manager()
        errors = mgr.validate_batch_request(req)
        self.assertEqual(errors, [])


class TestRenderBatch(unittest.TestCase):
    def test_render_batch_returns_dict(self):
        from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
        mgr = BatchPromptExportManager()
        req = _make_batch_request(source_ids=("s1", "s2", "s3"))
        rendered = mgr.render_batch(req)
        self.assertEqual(set(rendered.keys()), {"s1", "s2", "s3"})

    def test_render_batch_text_non_empty(self):
        from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
        mgr = BatchPromptExportManager()
        req = _make_batch_request(source_ids=("s1",))
        rendered = mgr.render_batch(req)
        self.assertTrue(rendered["s1"].strip())

    def test_render_batch_with_template_manager(self):
        from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
        from aurora_studio.modules.prompt_template_manager import PromptTemplateManager
        mgr = BatchPromptExportManager()
        tmgr = PromptTemplateManager()
        req = _make_batch_request(source_ids=("s1",), template_id="default-scene-basic")
        rendered = mgr.render_batch(req, template_manager=tmgr)
        self.assertIn("s1", rendered)


class TestCreateExportArtifactsForBatch(unittest.TestCase):
    def test_batch_export_multiple_scenes(self):
        from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
        from aurora_studio.modules.prompt_export_manager import PromptExportManager
        mgr = BatchPromptExportManager()
        emgr = PromptExportManager()
        req = _make_batch_request(source_ids=("s1", "s2"))
        result = mgr.create_export_artifacts_for_batch(req, emgr)
        self.assertEqual(result.total_count, 2)
        self.assertEqual(result.success_count, 2)
        self.assertEqual(result.status, "completed")

    def test_batch_export_multiple_shots(self):
        import uuid
        from datetime import datetime, timezone
        from aurora_studio.contracts.prompt_execution import BatchPromptExportRequest
        from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
        from aurora_studio.modules.prompt_export_manager import PromptExportManager
        mgr = BatchPromptExportManager()
        emgr = PromptExportManager()
        req = BatchPromptExportRequest(
            batch_id=f"b-{uuid.uuid4().hex[:8]}",
            project_id="",
            source_type="shot",
            source_ids=("sh1", "sh2", "sh3"),
            template_id="default-scene-basic",
        )
        result = mgr.create_export_artifacts_for_batch(req, emgr)
        self.assertEqual(result.total_count, 3)

    def test_batch_artifacts_have_ids(self):
        from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
        from aurora_studio.modules.prompt_export_manager import PromptExportManager
        mgr = BatchPromptExportManager()
        emgr = PromptExportManager()
        req = _make_batch_request(source_ids=("s1",))
        result = mgr.create_export_artifacts_for_batch(req, emgr)
        self.assertTrue(result.items[0].artifact_id)

    def test_batch_export_with_profile(self):
        import uuid
        from datetime import datetime, timezone
        from aurora_studio.contracts.prompt_execution import BatchPromptExportRequest
        from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
        from aurora_studio.modules.prompt_export_manager import PromptExportManager
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        mgr = BatchPromptExportManager()
        emgr = PromptExportManager()
        pmgr = ExportProfileManager()
        req = BatchPromptExportRequest(
            batch_id=f"b-{uuid.uuid4().hex[:8]}",
            project_id="",
            source_type="scene",
            source_ids=("s1",),
            template_id="",
            profile_id="default-profile-cinematic",
        )
        result = mgr.create_export_artifacts_for_batch(req, emgr, profile_manager=pmgr)
        self.assertEqual(result.total_count, 1)

    def test_empty_source_ids_returns_failed(self):
        import uuid
        from aurora_studio.contracts.prompt_execution import BatchPromptExportRequest
        from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
        from aurora_studio.modules.prompt_export_manager import PromptExportManager
        mgr = BatchPromptExportManager()
        emgr = PromptExportManager()
        req = BatchPromptExportRequest(
            batch_id=f"b-{uuid.uuid4().hex[:8]}",
            project_id="",
            source_type="scene",
            source_ids=(),
            template_id="default-scene-basic",
        )
        result = mgr.create_export_artifacts_for_batch(req, emgr)
        self.assertEqual(result.status, "failed")

    def test_result_json_serializable(self):
        from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
        from aurora_studio.modules.prompt_export_manager import PromptExportManager
        mgr = BatchPromptExportManager()
        emgr = PromptExportManager()
        req = _make_batch_request(source_ids=("s1", "s2"))
        result = mgr.create_export_artifacts_for_batch(req, emgr)
        json.dumps(result.to_dict())

    def test_no_provider_execution(self):
        """Batch export must not call any provider or network."""
        import sys
        from aurora_studio.modules.batch_prompt_export import BatchPromptExportManager
        from aurora_studio.modules.prompt_export_manager import PromptExportManager
        mgr = BatchPromptExportManager()
        emgr = PromptExportManager()
        req = _make_batch_request(source_ids=("s1",))
        mgr.create_export_artifacts_for_batch(req, emgr)
        self.assertNotIn("openai", sys.modules)
        self.assertNotIn("anthropic", sys.modules)


class TestUISessionBatchExport(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_create_batch_export_ok(self):
        r = self.sess.create_batch_prompt_export(
            source_type="scene",
            source_ids=["s1", "s2"],
            template_id="default-scene-basic",
        )
        self.assertTrue(r.ok, r.message)

    def test_create_batch_export_csv_source_ids(self):
        r = self.sess.create_batch_prompt_export(
            source_type="scene",
            source_ids="s1,s2,s3",
            template_id="default-scene-basic",
        )
        self.assertTrue(r.ok, r.message)
        self.assertEqual(r.payload["total_count"], 3)

    def test_create_batch_export_empty_ids_fails(self):
        r = self.sess.create_batch_prompt_export(
            source_type="scene",
            source_ids=[],
            template_id="default-scene-basic",
        )
        self.assertFalse(r.ok)

    def test_create_batch_export_empty_source_type_fails(self):
        r = self.sess.create_batch_prompt_export(
            source_type="",
            source_ids=["s1"],
            template_id="default-scene-basic",
        )
        self.assertFalse(r.ok)

    def test_create_batch_no_template_or_profile_fails(self):
        r = self.sess.create_batch_prompt_export(
            source_type="scene",
            source_ids=["s1"],
            template_id="",
            profile_id="",
        )
        self.assertFalse(r.ok)

    def test_create_batch_export_json_serializable(self):
        r = self.sess.create_batch_prompt_export(
            source_type="scene",
            source_ids=["s1"],
            template_id="default-scene-basic",
        )
        self.assertTrue(r.ok)
        json.dumps(r.payload)


class TestDesktopBatchMethods(unittest.TestCase):
    def test_create_batch_prompt_export_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "create_batch_prompt_export"))


if __name__ == "__main__":
    unittest.main()
