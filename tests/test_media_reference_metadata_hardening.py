"""Tests for TASK-000092: Media Reference Metadata Hardening."""

import json
import unittest

ASSET_FIELDS = dict(
    asset_id="a1", project_id="p1", asset_type="image",
    display_name="Hero Shot", location="/assets/hero.png",
    state="active", created_at="2026-01-01T00:00:00+00:00",
    modified_at="2026-01-01T00:00:00+00:00",
)


def _make_asset(**overrides):
    from aurora_studio.contracts.asset import AssetRecord
    return AssetRecord(**{**ASSET_FIELDS, **overrides})


def _make_mgr():
    from aurora_studio.modules.asset_manager import AssetManager
    from aurora_studio.contracts.asset import AssetRecord
    mgr = AssetManager()
    asset = AssetRecord(**ASSET_FIELDS)
    mgr._assets["a1"] = asset
    return mgr


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    svc = ApplicationService()
    from aurora_studio.contracts.asset import AssetRecord
    svc.asset_manager._assets["a1"] = AssetRecord(**ASSET_FIELDS)
    return UISession(svc)


class TestAssetMediaMetadataSerializes(unittest.TestCase):
    def test_default_media_kind_unknown(self):
        a = _make_asset()
        self.assertEqual(a.media_kind, "unknown")

    def test_default_preview_status(self):
        a = _make_asset()
        self.assertEqual(a.preview_status, "not_generated")

    def test_asset_serializes_media_fields(self):
        a = _make_asset(media_kind="image", mime_hint="image/png",
                        extension_hint="png", size_hint_bytes=1024,
                        checksum_hint="abc123", preview_status="not_generated")
        d = a.to_dict()
        self.assertEqual(d["media_kind"], "image")
        self.assertEqual(d["mime_hint"], "image/png")
        self.assertEqual(d["extension_hint"], "png")
        self.assertEqual(d["size_hint_bytes"], 1024)

    def test_asset_dict_json_serializable(self):
        a = _make_asset(media_kind="video", size_hint_bytes=999)
        json.dumps(a.to_dict())

    def test_from_dict_restores_media_kind(self):
        from aurora_studio.contracts.asset import AssetRecord
        d = _make_asset(media_kind="audio").to_dict()
        restored = AssetRecord.from_dict(d)
        self.assertEqual(restored.media_kind, "audio")

    def test_from_dict_unknown_media_kind_normalized(self):
        from aurora_studio.contracts.asset import AssetRecord
        d = _make_asset().to_dict()
        d["media_kind"] = "hologram"
        restored = AssetRecord.from_dict(d)
        self.assertEqual(restored.media_kind, "unknown")

    def test_from_dict_invalid_preview_status_normalized(self):
        from aurora_studio.contracts.asset import AssetRecord
        d = _make_asset().to_dict()
        d["preview_status"] = "magic_preview"
        restored = AssetRecord.from_dict(d)
        self.assertEqual(restored.preview_status, "not_generated")

    def test_from_dict_valid_preview_status_kept(self):
        from aurora_studio.contracts.asset import AssetRecord
        d = _make_asset().to_dict()
        d["preview_status"] = "planned"
        restored = AssetRecord.from_dict(d)
        self.assertEqual(restored.preview_status, "planned")

    def test_from_dict_missing_media_fields_defaults(self):
        from aurora_studio.contracts.asset import AssetRecord
        d = {**ASSET_FIELDS}
        restored = AssetRecord.from_dict(d)
        self.assertEqual(restored.media_kind, "unknown")
        self.assertEqual(restored.preview_status, "not_generated")
        self.assertIsNone(restored.size_hint_bytes)


class TestUpdateMediaMetadata(unittest.TestCase):
    def test_update_media_kind(self):
        mgr = _make_mgr()
        updated = mgr.update_media_reference_metadata("a1", media_kind="image")
        self.assertEqual(updated.media_kind, "image")

    def test_update_invalid_media_kind_normalized(self):
        mgr = _make_mgr()
        updated = mgr.update_media_reference_metadata("a1", media_kind="hologram")
        self.assertEqual(updated.media_kind, "unknown")

    def test_update_preview_status(self):
        mgr = _make_mgr()
        updated = mgr.update_media_reference_metadata("a1", preview_status="planned")
        self.assertEqual(updated.preview_status, "planned")

    def test_update_invalid_preview_status_normalized(self):
        mgr = _make_mgr()
        updated = mgr.update_media_reference_metadata("a1", preview_status="magic")
        self.assertEqual(updated.preview_status, "not_generated")

    def test_update_size_hint_bytes_positive(self):
        mgr = _make_mgr()
        updated = mgr.update_media_reference_metadata("a1", size_hint_bytes=2048)
        self.assertEqual(updated.size_hint_bytes, 2048)

    def test_update_size_hint_bytes_zero_ok(self):
        mgr = _make_mgr()
        updated = mgr.update_media_reference_metadata("a1", size_hint_bytes=0)
        self.assertEqual(updated.size_hint_bytes, 0)

    def test_update_size_hint_bytes_negative_raises(self):
        mgr = _make_mgr()
        with self.assertRaises(ValueError):
            mgr.update_media_reference_metadata("a1", size_hint_bytes=-1)

    def test_update_checksum_hint_string(self):
        mgr = _make_mgr()
        updated = mgr.update_media_reference_metadata("a1", checksum_hint="sha256:abc")
        self.assertEqual(updated.checksum_hint, "sha256:abc")


class TestExtensionHintInference(unittest.TestCase):
    def test_infer_extension_hint_from_location(self):
        mgr = _make_mgr()
        hint = mgr.infer_extension_hint_from_location("a1")
        self.assertEqual(hint, "png")

    def test_infer_extension_stores_on_record(self):
        mgr = _make_mgr()
        mgr.infer_extension_hint_from_location("a1")
        self.assertEqual(mgr.get_asset("a1").extension_hint, "png")

    def test_infer_extension_no_file_opened(self):
        """Inferring extension must not open any file."""
        import sys
        mgr = _make_mgr()
        open_calls = []
        real_open = open

        def patched_open(path, *a, **kw):
            if "hero.png" in str(path):
                open_calls.append(path)
            return real_open(path, *a, **kw)

        import builtins
        original = builtins.open
        builtins.open = patched_open
        try:
            mgr.infer_extension_hint_from_location("a1")
        finally:
            builtins.open = original

        self.assertEqual(open_calls, [], "Must not open asset file")

    def test_infer_extension_no_extension(self):
        from aurora_studio.modules.asset_manager import AssetManager
        from aurora_studio.contracts.asset import AssetRecord
        mgr = AssetManager()
        asset = AssetRecord(**{**ASSET_FIELDS, "location": "/assets/README"})
        mgr._assets["a1"] = asset
        hint = mgr.infer_extension_hint_from_location("a1")
        self.assertEqual(hint, "")


class TestSetPreviewStatus(unittest.TestCase):
    def test_set_valid_preview_status(self):
        mgr = _make_mgr()
        updated = mgr.set_preview_status("a1", "error", "Could not load file.")
        self.assertEqual(updated.preview_status, "error")
        self.assertEqual(updated.preview_error, "Could not load file.")

    def test_set_invalid_preview_status_normalized(self):
        mgr = _make_mgr()
        updated = mgr.set_preview_status("a1", "bad_value")
        self.assertEqual(updated.preview_status, "not_generated")

    def test_set_preview_status_clears_error(self):
        mgr = _make_mgr()
        mgr.set_preview_status("a1", "error", "something")
        updated = mgr.set_preview_status("a1", "not_generated", "")
        self.assertEqual(updated.preview_error, "")


class TestBundleSaveLoadPreservesMediaMetadata(unittest.TestCase):
    def test_bundle_save_load_roundtrip(self):
        """Bundle save/load must preserve media metadata fields."""
        import tempfile, os, json
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        from aurora_studio.contracts.asset import AssetRecord
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = os.path.join(tmp, "aurora_project.json")
            svc = ApplicationService()
            sess = UISession(svc)

            # Create project
            r = sess.create_project(path=tmp, title="MediaTest")
            self.assertTrue(r.ok, r.message)

            # Register asset via manager directly
            from aurora_studio.contracts.asset import AssetRecord
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            aid = "a-media-001"
            asset = AssetRecord(
                asset_id=aid, project_id="p1", asset_type="image",
                display_name="Test", location="/assets/test.jpg",
                state="active", created_at=now, modified_at=now,
            )
            svc.asset_manager._assets[aid] = asset

            # Set media metadata
            svc.asset_manager.update_media_reference_metadata(
                aid, media_kind="image", mime_hint="image/jpeg",
                extension_hint="jpg", size_hint_bytes=512, preview_status="planned",
            )

            # Save bundle
            r3 = sess.save_bundle(path=bundle_path)
            self.assertTrue(r3.ok, r3.message)

            # Load bundle in new service
            svc2 = ApplicationService()
            sess2 = UISession(svc2)
            r4 = sess2.load_and_rehydrate_bundle(path=bundle_path)
            self.assertTrue(r4.ok, r4.message)

            asset2 = svc2.asset_manager.get_asset(aid)
            self.assertEqual(asset2.media_kind, "image")
            self.assertEqual(asset2.mime_hint, "image/jpeg")
            self.assertEqual(asset2.size_hint_bytes, 512)
            self.assertEqual(asset2.preview_status, "planned")


class TestUISessionMediaMethods(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_update_asset_media_metadata_ok(self):
        r = self.sess.update_asset_media_metadata("a1", {"media_kind": "image", "mime_hint": "image/png"})
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["media_kind"], "image")

    def test_update_negative_size_hint_fails(self):
        r = self.sess.update_asset_media_metadata("a1", {"size_hint_bytes": -5})
        self.assertFalse(r.ok)

    def test_set_asset_preview_status_ok(self):
        r = self.sess.set_asset_preview_status("a1", "planned")
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["preview_status"], "planned")

    def test_set_asset_preview_status_payload_serializable(self):
        r = self.sess.set_asset_preview_status("a1", "error", "msg")
        self.assertTrue(r.ok)
        json.dumps(r.payload)

    def test_no_file_content_inspection(self):
        """update_asset_media_metadata must not open any file."""
        import builtins
        open_calls = []
        real_open = builtins.open
        def patched(path, *a, **kw):
            if "hero.png" in str(path):
                open_calls.append(path)
            return real_open(path, *a, **kw)
        builtins.open = patched
        try:
            self.sess.update_asset_media_metadata("a1", {"media_kind": "image"})
        finally:
            builtins.open = real_open
        self.assertEqual(open_calls, [])


if __name__ == "__main__":
    unittest.main()
