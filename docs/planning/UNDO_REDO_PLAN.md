# Undo/Redo Plan — Aurora Studio

## Purpose

This document describes the planned undo/redo system for Aurora Studio.
Undo/redo is not implemented in TASK-000067.
This document is planning only.

## Current Action Behavior

All manager actions (create, update, archive) are applied immediately in memory.
There is no command history.
Manager action semantics are not changed in TASK-000067.
Actions are irreversible without a full reload from disk.

## Non-goals

- Undo/redo is not implemented in TASK-000067.
- No command history is added.
- Manager action semantics are not changed.
- Save/load operations are not automatically undoable.
- Packaging operations are not undoable.
- Undo/redo requires later command-model work.

## Command Model (Future)

A Command pattern should be used:

- Each user action is represented as a Command object.
- Commands implement `execute()` and `undo()`.
- A CommandHistory stack stores executed commands.
- Undo pops from history and calls `undo()`.
- Redo re-executes the undone command.

## Undoable Actions (Future)

Candidates for undo support:

- create scene
- update scene detail
- create shot
- update shot detail
- add timeline item
- remove timeline item
- move timeline item
- update asset metadata
- link/unlink asset
- update character detail
- add/remove character reference

## Non-undoable Actions

The following should NOT be undoable:

- Save bundle
- Load bundle
- Export bundle copy
- Import bundle copy
- Plugin registration
- Provider execution (future)
- Autosave recovery

## Transaction Boundaries

- A transaction groups related actions into a single undo step.
- Example: "Create shot with timeline item" is one undo step, not two.
- Transaction boundaries must be defined at the UISession level.

## State Snapshots (Future)

Alternative to command objects:

- Snapshot the full bundle before each action.
- Undo restores the previous snapshot.
- More memory-intensive but simpler to implement.
- Suitable for MVP; command model preferred long-term.

## Persistence Interaction

- Undo history is not persisted to the bundle.
- Closing and reopening a project resets undo history.
- Save does not clear undo history (user may want to undo after a failed save).
- Load clears undo history (the loaded state is the new baseline).

## UI Controls (Future)

- Ctrl+Z / Cmd+Z for undo.
- Ctrl+Y / Ctrl+Shift+Z for redo.
- Undo/Redo buttons in toolbar.
- Undo/Redo menu items with action descriptions.
- Greyed out when history is empty.

## Failure Handling

- If undo fails, show a warning and leave state unchanged.
- Do not attempt partial undo.
- Log the failure.

## Testing Strategy

- Unit tests for each undoable command.
- Round-trip tests: execute then undo returns to original state.
- Edge cases: undo at empty history, redo at end of history.
- Transaction grouping tests.

## Future Implementation Tasks

- TASK-UNDO-001: Define Command interface and CommandHistory.
- TASK-UNDO-002: Wrap UISession actions in command objects.
- TASK-UNDO-003: Implement undo/redo keyboard shortcuts.
- TASK-UNDO-004: Add undo/redo UI controls.
- TASK-UNDO-005: Define transaction boundaries.
- TASK-UNDO-006: Write comprehensive undo unit tests.

## Risks

- Command model adds complexity to all manager interactions.
- Memory usage grows with history depth.
- Deep undo can produce unexpected results if external state changed.
- Snapshot approach may be too slow for large bundles.

## Acceptance Criteria (Future)

- Undo reverses the last user action.
- Redo re-applies the last undone action.
- Non-undoable actions do not appear in history.
- All undoable actions are covered by tests.
- Undo history is not persisted to bundle.
