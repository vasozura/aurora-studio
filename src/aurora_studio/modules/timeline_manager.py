"""Timeline Manager first minimal implementation."""

from __future__ import annotations

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

    This class manages only in-memory Timeline records.

    It does not implement:
    - Actual timeline rendering
    - Scene existence validation
    - Shot existence validation
    - Audio tracks
    - Rendered clips
    - Database persistence
    - Provider integration
    - Plugin execution
    - GUI behavior
    """

    module_name = "Timeline Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._timelines: dict[str, TimelineRecord] = {}

    def get_readiness(self) -> Readiness:
        """Return module readiness."""

        return self.readiness

    def describe(self) -> str:
        """Return a short implementation description."""

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

        This does not validate whether target Scene or Shot exists.
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

        remaining = tuple(item for item in timeline.items if item.item_id != clean_item_id)
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
        for item in timeline.items:
            if item.item_id == clean_item_id:
                new_items.append(item.with_updates(order_index=clean_order) if hasattr(item, "with_updates") else TimelineItem(
                    item_id=item.item_id,
                    item_type=item.item_type,
                    target_id=item.target_id,
                    order_index=clean_order,
                ))
                found = True
            else:
                new_items.append(item)

        if not found:
            raise ValidationError(f"Timeline item not found: {clean_item_id}")

        updated = timeline.with_updates(items=tuple(new_items), modified_at=utc_now_iso())
        self._timelines[updated.timeline_id] = updated
        return updated

    def _resolve_order_index(self, timeline: TimelineRecord, order_index: int | None) -> int:
        """Resolve explicit or next order index for a Timeline."""

        if order_index is not None:
            return self._validate_order_index(order_index)

        if not timeline.items:
            return 0
        return max(item.order_index for item in timeline.items) + 1

    def _validate_order_index(self, order_index: int) -> int:
        """Validate order index."""

        if not isinstance(order_index, int):
            raise ValidationError("order_index must be an integer.")
        if order_index < 0:
            raise ValidationError("order_index must not be negative.")
        return order_index

    def _validate_required_ref(self, value: str, field_name: str) -> str:
        """Validate a required reference-like string."""

        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean_value
