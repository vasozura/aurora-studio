@echo off
cd /d "%~dp0"
git add -A
git commit -m "TASK-000051-055: v0.2 Scene/Shot/Timeline Editor Pack

- TASK-000051: SceneRecord +7 detail fields; update_scene_details(); SceneDetailViewModel; UISession get/update_scene_detail; desktop scene detail form
- TASK-000052: ShotRecord +11 fields incl duration_seconds; update_shot_details(); ShotDetailViewModel; UISession get/update_shot_detail; duration validation; desktop shot detail form
- TASK-000053: Inspector UX - load/apply/clear scene+shot; get_inspector_snapshot(); validate_scene/shot_detail_fields()
- TASK-000054: timeline move_item_up/down, list_items, add_scene/shot_to_timeline; desktop Add Scene/Shot + Move Up/Down buttons; TimelineItemViewModel exposes timeline_id
- TASK-000055: get_timeline_summary, normalize_timeline_order, repair_duplicate_order_indexes; TimelineSummaryViewModel; desktop timeline summary panel; UISession get_timeline_summary/normalize

Tests: 1327 pass (0 fail, 15 skip)
Docs: docs/pipeline/V0_2_PIPELINE_PROGRESS.md created"
git push
