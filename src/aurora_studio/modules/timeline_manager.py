"""Timeline Manager implementation (v0.2: move_up/down, list_items, summary added)."""

from __future__ import annotations

from typing import Any

from aurora_studio.contracts.timeline import (
    TIMELINE_STATE_ARCHIVED,
    TIMELINE_STATE_DRAFT,
    TimelineItem,
    TimelineRecord,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id
from aurora_studio.core.readiness import Readiness


class TimelineManager:
    """Minimal Timeline Manager implementation.

    Does not implement: Actual timeline rendering, Scene/Shot existence
    validation, Audio tracks, Rendered clips, Database persistence,
    Provider integration, Plugin execution, GUI behavior.
    """

    module_name = "Timeline Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._timelines: dict[str, TimelineRecord] = {}

    def get_readiness(self) -> Readiness:
        return self.readiness

    def describe(self) -> str:
        return (
            "Timeline Manager supports minimal in-memory Timeline records "
            "and remains not ready for full product implementation."
        )

    def create_timeline(self, project_id: str, title: str) -> TimelineRecord:
        """Create an in-memory Timeline record."""

        clean_project_id = self._validate_required_ref(project_id, "project_id")
        clean_title = self._validate_required_ref(title, "title")
        now = utc_now_iso()

        timeline = TimelineRecord(
            timeline_id=new_id("timeline"),
            project_id=clean_project_id,
            title=clean_title,
            items=(),
            state=TIMELINE_STATE_DRAFT,
            created_at=now,
            modified_at=now,
        )
        self._timelines[timeline.timeline_id] = timeline
        return timeline

    def list_timelines(self, project_id: str | None = None) -> list[TimelineRecord]:
        """List Timeline records, optionally filtered by project reference."""

        if project_id is None:
            return list(self._timelines.values())

        clean_project_id = self._validate_required_ref(project_id, "project_id")
        return [t for t in self._timelines.values() if t.project_id == clean_project_id]

    def get_timeline(self, timeline_id: str) -> TimelineRecord:
        """Return a Timeline record by ID."""

        clean_timeline_id = self._validate_required_ref(timeline_id, "timeline_id")
        try:
            return self._timelines[clean_timeline_id]
        except KeyError as exc:
            raise ValidationError(f"Timeline not found: {clean_timeline_id}") from exc

    def update_timeline(self, timeline_id: str, *, title: str | None = None) -> TimelineRecord:
        """Update minimal Timeline-owned fields."""

        timeline = self.get_timeline(timeline_id)
        changes: dict = {"modified_at": utc_now_iso()}

        if title is not None:
            changes["title"] = self._validate_required_ref(title, "title")

        updated = timeline.with_updates(**changes)
        self._timelines[updated.timeline_id] = updated
        return updated

    def archive_timeline(self, timeline_id: str) -> TimelineRecord:
        """Archive a Timeline record. Items are preserved."""

        timeline = self.get_timeline(timeline_id)
        now = utc_now_iso()
        archived = timeline.with_updates(
            state=TIMELINE_STATE_ARCHIVED,
            modified_at=now,
            archived_at=now,
        )
        self._timelines[archived.timeline_id] = archived
        return archived

    def add_item(
        self,
        timeline_id: str,
        item_type: str,
        target_id: str,
        order_index: int | None = None,
    ) -> TimelineRecord:
        """Add an item reference to a Timeline.

        Does not validate whether target Scene or Shot exists.
        """

        timeline = self.get_timeline(timeline_id)
        clean_item_type = self._validate_required_ref(item_type, "item_type")
        clean_target_id = self._validate_required_ref(target_id, "target_id")
        resolved_order = self._resolve_order_index(timeline, order_index)

        item = TimelineItem(
            item_id=new_id("item"),
            item_type=clean_item_type,
            target_id=clean_target_id,
            order_index=resolved_order,
        )
        updated = timeline.with_updates(
            items=timeline.items + (item,),
            modified_at=utc_now_iso(),
        )
        self._timelines[updated.timeline_id] = updated
        return updated

    def remove_item(self, timeline_id: str, item_id: str) -> TimelineRecord:
        """Remove an item from a Timeline by item ID."""

        timeline = self.get_timeline(timeline_id)
        clean_item_id = self._validate_required_ref(item_id, "item_id")

        remaining = tuple(it for it in timeline.items if it.item_id != clean_item_id)
        if len(remaining) == len(timeline.items):
            raise ValidationError(f"Timeline item not found: {clean_item_id}")

        updated = timeline.with_updates(items=remaining, modified_at=utc_now_iso())
        self._timelines[updated.timeline_id] = updated
        return updated

    def move_item(self, timeline_id: str, item_id: str, order_index: int) -> TimelineRecord:
        """Update the order index of a Timeline item."""

        timeline = self.get_timeline(timeline_id)
        clean_item_id = self._validate_required_ref(item_id, "item_id")
        clean_order = self._validate_order_index(order_index)

        found = False
        new_items = []
        for it in timeline.items:
            if it.item_id == clean_item_id:
                new_items.append(TimelineItem(
                    item_id=it.item_id,
                    item_type=it.item_type,
                    target_id=it.target_id,
                    order_index=clean_order,
                ))
                found = True
            else:
                new_items.append(it)

        if not found:
            raise ValidationError(f"Timeline item not found: {clean_item_id}")

        updated = timeline.with_updates(items=tuple(new_items), modified_at=utc_now_iso())
        self._timelines[updated.timeline_id] = updated
        return updated

    def list_items(self, timeline_id: str) -> list[TimelineItem]:
        """Return timeline items sorted by order_index."""

        timeline = self.get_timeline(timeline_id)
        return sorted(timeline.items, key=lambda it: (it.order_index, it.item_id))

    def move_item_up(self, timeline_id: str, item_id: str) -> TimelineRecord:
        """Swap item with the item that has the next-lower order_index.

        If already at minimum order, returns timeline unchanged.
        """

        timeline = self.get_timeline(timeline_id)
        clean_item_id = self._validate_required_ref(item_id, "item_id")
        items = sorted(timeline.items, key=lambda it: (it.order_index, it.item_id))

        idx = next((i for i, it in enumerate(items) if it.item_id == clean_item_id), None)
        if idx is None:
            raise ValidationError(f"Timeline item not found: {clean_item_id}")
        if idx == 0:
            return timeline  # already first

        # Swap order indexes with previous item
        a = items[idx - 1]
        b = items[idx]
        new_a = TimelineItem(item_id=a.item_id, item_type=a.item_type, target_id=a.target_id, order_index=b.order_index)
        new_b = TimelineItem(item_id=b.item_id, item_type=b.item_type, target_id=b.target_id, order_index=a.order_index)

        new_items = list(items)
        new_items[idx - 1] = new_a
        new_items[idx] = new_b

        updated = timeline.with_updates(items=tuple(new_items), modified_at=utc_now_iso())
        self._timelines[updated.timeline_id] = updated
        return updated

    def move_item_down(self, timeline_id: str, item_id: str) -> TimelineRecord:
        """Swap item with the item that has the next-higher order_index.

        If already at maximum order, returns timeline unchanged.
        """

        timeline = self.get_timeline(timeline_id)
        clean_item_id = self._validate_required_ref(item_id, "item_id")
        items = sorted(timeline.items, key=lambda it: (it.order_index, it.item_id))

        idx = next((i for i, it in enumerate(items) if it.item_id == clean_item_id), None)
        if idx is None:
            raise ValidationError(f"Timeline item not found: {clean_item_id}")
        if idx == len(items) - 1:
            return timeline  # already last

        # Swap order indexes with next item
        a = items[idx]
        b = items[idx + 1]
        new_a = TimelineItem(item_id=a.item_id, item_type=a.item_type, target_id=a.target_id, order_index=b.order_index)
        new_b = TimelineItem(item_id=b.item_id, item_type=b.item_type, target_id=b.target_id, order_index=a.order_index)

        new_items = list(items)
        new_items[idx] = new_a
        new_items[idx + 1] = new_b

        updated = timeline.with_updates(items=tuple(new_items), modified_at=utc_now_iso())
        self._timelines[updated.timeline_id] = updated
        return updated

    def normalize_timeline_order(self, timeline_id: str) -> TimelineRecord:
        """Assign contiguous order indexes (0, 1, 2, ...) sorted by current order_index.

        Deterministic: stable sort by (order_index, item_id).
        """

        timeline = self.get_timeline(timeline_id)
        sorted_items = sorted(timeline.items, key=lambda it: (it.order_index, it.item_id))
        new_items = tuple(
            TimelineItem(
                item_id=it.item_id,
                item_type=it.item_type,
                target_id=it.target_id,
                order_index=i,
            )
            for i, it in enumerate(sorted_items)
        )
        updated = timeline.with_updates(items=new_items, modified_at=utc_now_iso())
        self._timelines[updated.timeline_id] = updated
        return updated

    def repair_duplicate_order_indexes(self, timeline_id: str) -> TimelineRecord:
        """Ensure no two items share the same order_index.

        Sorts by (order_index, item_id) and re-assigns contiguous indexes
        only if duplicates exist. Returns unchanged timeline if clean.
        """

        timeline = self.get_timeline(timeline_id)
        order_indexes = [it.order_index for it in timeline.items]
        if len(order_indexes) == len(set(order_indexes)):
            return timeline  # no duplicates

        return self.normalize_timeline_order(timeline_id)

    def get_timeline_summary(
        self, timeline_id: str, shot_manager: Any = None
    ) -> dict[str, Any]:
        """Return a summary dict for a Timeline.

        Duration is summed from shot_manager if provided.
        Scene items contribute 0 to duration.
        Missing or invalid shot duration counts as 0.
        """

        timeline = self.get_timeline(timeline_id)
        items = sorted(timeline.items, key=lambda it: (it.order_index, it.item_id))

        total_duration = 0.0
        scene_count = 0
        shot_count = 0

        for it in items:
            if it.item_type == "scene":
                scene_count += 1
            elif it.item_type == "shot":
                shot_count += 1
                if shot_manager is not None:
                    try:
                        shot = shot_manager.get_shot(it.target_id)
                        d = getattr(shot, "duration_seconds", 0)
                        try:
                            total_duration += float(d) if d else 0.0
                        except (TypeError, ValueError):
                            pass
                    except Exception:
                        pass

        ordered_items = [
            {
                "item_id": it.item_id,
                "timeline_id": timeline_id,
                "item_type": it.item_type,
                "target_id": it.target_id,
                "order_index": it.order_index,
            }
            for it in items
        ]

        return {
            "timeline_id": timeline_id,
            "item_count": len(items),
            "scene_item_count": scene_count,
            "shot_item_count": shot_count,
            "total_duration_seconds": total_duration,
            "ordered_items": ordered_items,
        }

    def _resolve_order_index(self, timeline: TimelineRecord, order_index: int | None) -> int:
        if order_index is not None:
            return self._validate_order_index(order_index)
        if not timeline.items:
            return 0
        return max(it.order_index for it in timeline.items) + 1

    def _validate_order_index(self, order_index: int) -> int:
        if not isinstance(order_index, int):
            raise ValidationError("order_index must be an integer.")
        if order_index < 0:
            raise ValidationError("order_index must not be negative.")
        return order_index

    def _validate_required_ref(self, value: str, field_name: str) -> str:
        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean_value

    def replace_timelines(self, records: list) -> None:
        """Replace in-memory timeline store. Used by bundle rehydration."""

        from aurora_studio.contracts.timeline import TimelineRecord as _TimelineRecord
        for item in records:
            if not isinstance(item, _TimelineRecord):
                raise ValidationError("replace_timelines requires TimelineRecord instances.")
        self._timelines = {r.timeline_id: r for r in records}
