"""Tests for TASK-000064: Project Search and Filters."""

import tempfile
import unittest


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    svc = ApplicationService()
    sess = UISession(svc)
    with tempfile.TemporaryDirectory() as tmp:
        pass
    tmp = tempfile.mkdtemp()
    sess.create_project(tmp, "Search Project")
    return sess


class TestSearchScenes(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()
        self.sess.create_scene("Forest Battle", "action")
        self.sess.create_scene("City Romance", "romance")
        self.sess.create_scene("Mountain Chase", "action")

    def test_empty_query_returns_all(self):
        r = self.sess.search_scenes()
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["scenes"]), 3)

    def test_search_by_title_substring(self):
        r = self.sess.search_scenes(query="Battle")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["scenes"]), 1)
        self.assertIn("Battle", r.payload["scenes"][0]["title"])

    def test_search_case_insensitive(self):
        r = self.sess.search_scenes(query="forest")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["scenes"]), 1)

    def test_filter_by_status(self):
        scenes = self.sess.search_scenes().payload["scenes"]
        first_id = scenes[0]["scene_id"]
        self.sess.service.scene_manager._scenes[first_id] = \
            self.sess.service.scene_manager._scenes[first_id].with_updates(state="archived")
        r = self.sess.search_scenes(status="archived")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["scenes"]), 1)

    def test_no_match_returns_empty(self):
        r = self.sess.search_scenes(query="ZZZnonexistent")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["scenes"]), 0)

    def test_search_does_not_mutate(self):
        self.sess.search_scenes(query="Forest")
        r2 = self.sess.search_scenes()
        self.assertEqual(len(r2.payload["scenes"]), 3)


class TestSearchShots(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()
        rs = self.sess.create_scene("Scene A", "x")
        self.sid_a = rs.payload["scene_id"]
        rs2 = self.sess.create_scene("Scene B", "y")
        self.sid_b = rs2.payload["scene_id"]
        self.sess.create_shot(self.sid_a, "Wide Angle")
        self.sess.create_shot(self.sid_a, "Close Up")
        self.sess.create_shot(self.sid_b, "Pan Shot")

    def test_empty_query_returns_all(self):
        r = self.sess.search_shots()
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["shots"]), 3)

    def test_search_by_title(self):
        r = self.sess.search_shots(query="Wide")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["shots"]), 1)

    def test_filter_by_scene_id(self):
        r = self.sess.search_shots(scene_id=self.sid_a)
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["shots"]), 2)

    def test_search_case_insensitive(self):
        r = self.sess.search_shots(query="close up")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["shots"]), 1)

    def test_filter_by_scene_id_and_query(self):
        r = self.sess.search_shots(query="Pan", scene_id=self.sid_b)
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["shots"]), 1)


class TestSearchAssets(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()
        self.sess.import_asset("location", "Dark Forest", "/a/b.png")
        self.sess.import_asset("prop", "Shiny Sword", "/a/c.png")
        self.sess.import_asset("location", "Mountain Peak", "/a/d.png")

    def test_empty_query_returns_all(self):
        r = self.sess.search_assets()
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["assets"]), 3)

    def test_search_by_display_name(self):
        r = self.sess.search_assets(query="Forest")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["assets"]), 1)

    def test_filter_by_type(self):
        r = self.sess.search_assets(asset_type="location")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["assets"]), 2)

    def test_filter_by_type_and_query(self):
        r = self.sess.search_assets(query="Dark", asset_type="location")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["assets"]), 1)

    def test_search_case_insensitive(self):
        r = self.sess.search_assets(query="shiny sword")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["assets"]), 1)

    def test_filter_by_state(self):
        assets = self.sess.search_assets().payload["assets"]
        aid = assets[0]["asset_id"]
        self.sess.service.asset_manager._assets[aid] = \
            self.sess.service.asset_manager._assets[aid].with_updates(state="archived")
        r = self.sess.search_assets(state="archived")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["assets"]), 1)

    def test_filter_by_tag(self):
        assets = self.sess.search_assets().payload["assets"]
        aid = assets[0]["asset_id"]
        self.sess.service.asset_manager._assets[aid] = \
            self.sess.service.asset_manager._assets[aid].with_updates(tags=("exterior", "dark"))
        r = self.sess.search_assets(tag="exterior")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["assets"]), 1)


class TestSearchCharacters(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()
        self.sess.create_character("Hero Max", "The brave one")
        self.sess.create_character("Villain Rex", "The evil one")
        self.sess.create_character("Side Kick", "The helpful one")

    def test_empty_query_returns_all(self):
        r = self.sess.search_characters()
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["characters"]), 3)

    def test_search_by_name(self):
        r = self.sess.search_characters(query="Hero")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["characters"]), 1)

    def test_search_case_insensitive(self):
        r = self.sess.search_characters(query="villain")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["characters"]), 1)

    def test_filter_by_status(self):
        chars = self.sess.search_characters().payload["characters"]
        cid = chars[0]["character_id"]
        self.sess.service.character_manager._characters[cid] = \
            self.sess.service.character_manager._characters[cid].with_updates(state="archived")
        r = self.sess.search_characters(status="archived")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["characters"]), 1)


class TestSearchExports(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()
        rs = self.sess.create_scene("Export Scene", "x")
        self.scene_id = rs.payload["scene_id"]
        self.sess.create_export_artifact(self.scene_id, "prompt", "a prompt for day")
        self.sess.create_export_artifact(self.scene_id, "storyboard", "a storyboard description")

    def test_empty_query_returns_all(self):
        r = self.sess.search_exports()
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["exports"]), 2)

    def test_filter_by_artifact_type(self):
        r = self.sess.search_exports(artifact_type="prompt")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["exports"]), 1)

    def test_search_by_content(self):
        r = self.sess.search_exports(query="storyboard")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["exports"]), 1)

    def test_filter_by_status(self):
        r = self.sess.search_exports(status="draft")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["exports"]), 2)

    def test_search_case_insensitive(self):
        r = self.sess.search_exports(query="PROMPT")
        self.assertTrue(r.ok)
        self.assertGreater(len(r.payload["exports"]), 0)


class TestSearchPlugins(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()
        self.sess.register_plugin("AlphaRenderer", "1.0", "", "")
        self.sess.register_plugin("BetaExporter", "2.0", "", "")

    def test_empty_query_returns_all(self):
        r = self.sess.search_plugins()
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["plugins"]), 2)

    def test_search_by_name(self):
        r = self.sess.search_plugins(query="Alpha")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["plugins"]), 1)

    def test_search_case_insensitive(self):
        r = self.sess.search_plugins(query="betaexporter")
        self.assertTrue(r.ok)
        self.assertEqual(len(r.payload["plugins"]), 1)


if __name__ == "__main__":
    unittest.main()
