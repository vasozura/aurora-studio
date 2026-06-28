"""Tests for TASK-000095: Undo/Redo Minimal Command Stack Pack."""

import json
import unittest


def _stack():
    from aurora_studio.modules.command_stack import CommandStack
    return CommandStack()


def _cmd(command_type="update_scene_detail", target_id="s1",
         before=None, after=None):
    from aurora_studio.modules.command_stack import make_command
    return make_command(
        command_type=command_type,
        target_type=command_type.split("_")[1],
        target_id=target_id,
        before_state=before or {"title": "Old"},
        after_state=after or {"title": "New"},
        description=f"Test {command_type}",
    )


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


class TestCommandContracts(unittest.TestCase):
    def test_command_record_serializes(self):
        cmd = _cmd()
        json.dumps(cmd.to_dict())

    def test_command_record_from_dict(self):
        from aurora_studio.contracts.command import CommandRecord
        cmd = _cmd()
        restored = CommandRecord.from_dict(cmd.to_dict())
        self.assertEqual(restored.command_id, cmd.command_id)

    def test_command_result_serializes(self):
        from aurora_studio.contracts.command import CommandResult
        r = CommandResult(ok=True, command_id="x", message="done")
        json.dumps(r.to_dict())

    def test_stack_state_serializes(self):
        s = _stack().get_state()
        json.dumps(s.to_dict())


class TestPushAndState(unittest.TestCase):
    def test_push_command(self):
        stack = _stack()
        stack.push(_cmd())
        self.assertEqual(stack.get_state().undo_count, 1)

    def test_can_undo_after_push(self):
        stack = _stack()
        stack.push(_cmd())
        self.assertTrue(stack.can_undo())

    def test_cannot_redo_after_push(self):
        stack = _stack()
        stack.push(_cmd())
        self.assertFalse(stack.can_redo())

    def test_redo_count_zero_initially(self):
        self.assertEqual(_stack().get_state().redo_count, 0)

    def test_last_command_id_set_after_push(self):
        stack = _stack()
        cmd = _cmd()
        stack.push(cmd)
        self.assertEqual(stack.get_state().last_command_id, cmd.command_id)


class TestUndoSceneDetail(unittest.TestCase):
    def test_undo_update_scene_detail(self):
        stack = _stack()
        stack.push(_cmd("update_scene_detail", "s1", {"title": "Old"}, {"title": "New"}))
        result = stack.undo()
        self.assertTrue(result.ok)
        self.assertIn("Old", result.applied_state)

    def test_redo_update_scene_detail(self):
        stack = _stack()
        stack.push(_cmd("update_scene_detail", "s1", {"title": "Old"}, {"title": "New"}))
        stack.undo()
        result = stack.redo()
        self.assertTrue(result.ok)
        self.assertIn("New", result.applied_state)


class TestUndoShotDetail(unittest.TestCase):
    def test_undo_update_shot_detail(self):
        stack = _stack()
        stack.push(_cmd("update_shot_detail", "sh1", {"title": "Old Shot"}, {"title": "New Shot"}))
        result = stack.undo()
        self.assertTrue(result.ok)
        self.assertIn("Old Shot", result.applied_state)

    def test_redo_update_shot_detail(self):
        stack = _stack()
        stack.push(_cmd("update_shot_detail", "sh1", {"title": "Old"}, {"title": "New"}))
        stack.undo()
        result = stack.redo()
        self.assertTrue(result.ok)
        self.assertIn("New", result.applied_state)


class TestUnsupportedCommand(unittest.TestCase):
    def test_unsupported_returns_not_supported(self):
        stack = _stack()
        stack.push(_cmd("delete_scene", "s1"))
        result = stack.undo()
        self.assertFalse(result.ok)
        self.assertEqual(result.applied_state, "not_supported")

    def test_unsupported_does_not_corrupt_stack(self):
        stack = _stack()
        stack.push(_cmd("update_scene_detail", "s1"))
        stack.push(_cmd("delete_scene", "s2"))  # unsupported
        # Undo unsupported — should stay on stack
        stack.undo()
        self.assertEqual(stack.get_state().undo_count, 2)
        # Undo supported one should work
        stack._undo_stack.pop()  # manually remove unsupported
        result = stack.undo()
        self.assertTrue(result.ok)


class TestClearStack(unittest.TestCase):
    def test_clear_stack(self):
        stack = _stack()
        for _ in range(5):
            stack.push(_cmd())
        stack.clear()
        self.assertEqual(stack.get_state().undo_count, 0)
        self.assertEqual(stack.get_state().redo_count, 0)

    def test_cannot_undo_after_clear(self):
        stack = _stack()
        stack.push(_cmd())
        stack.clear()
        self.assertFalse(stack.can_undo())


class TestMaxStackSize(unittest.TestCase):
    def test_stack_max_size_enforced(self):
        from aurora_studio.modules.command_stack import MAX_STACK_SIZE
        stack = _stack()
        for i in range(MAX_STACK_SIZE + 10):
            stack.push(_cmd(target_id=f"s{i}"))
        self.assertLessEqual(stack.get_state().undo_count, MAX_STACK_SIZE)


class TestNoPersistence(unittest.TestCase):
    def test_stack_not_persisted_across_new_session(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        sess1 = UISession(ApplicationService())
        sess1._get_command_stack().push(_cmd())
        # New session starts fresh
        sess2 = UISession(ApplicationService())
        state = sess2.get_command_stack_state()
        self.assertTrue(state.ok)
        self.assertEqual(state.payload["undo_count"], 0)


class TestUISessionUndo(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_get_stack_state_ok(self):
        r = self.sess.get_command_stack_state()
        self.assertTrue(r.ok)
        self.assertFalse(r.payload["can_undo"])

    def test_undo_nothing_returns_ok_with_message(self):
        r = self.sess.undo_last_action()
        self.assertTrue(r.ok)
        self.assertFalse(r.payload["ok"])

    def test_redo_nothing_returns_ok_with_message(self):
        r = self.sess.redo_last_action()
        self.assertTrue(r.ok)
        self.assertFalse(r.payload["ok"])

    def test_undo_redo_serializable(self):
        self.sess._get_command_stack().push(_cmd())
        r = self.sess.undo_last_action()
        self.assertTrue(r.ok)
        json.dumps(r.payload)
        r2 = self.sess.redo_last_action()
        json.dumps(r2.payload)

    def test_stack_state_serializable(self):
        r = self.sess.get_command_stack_state()
        json.dumps(r.payload)


if __name__ == "__main__":
    unittest.main()
