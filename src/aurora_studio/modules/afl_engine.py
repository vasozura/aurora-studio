"""AFL Engine — v0.2 expanded structural validation (TASK-000060)."""

from __future__ import annotations

from typing import Any

from aurora_studio.contracts.afl import (
    AFL_LEVEL_ERROR,
    AFL_LEVEL_INFO,
    AFL_LEVEL_WARN,
    AFL_REPORT_FAIL,
    AFL_REPORT_PASS,
    AFL_REPORT_WARN,
    AFL_STATUS_INVALID,
    AFL_STATUS_NOT_CHECKED,
    AFL_STATUS_VALID,
    AFLValidationIssue,
    AFLValidationReport,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id
from aurora_studio.core.readiness import Readiness


def _issue(code: str, message: str, level: str, target_type: str = "",
           target_id: str = "", target_ref: str = "") -> AFLValidationIssue:
    return AFLValidationIssue(
        code=code,
        message=message,
        severity=level.lower(),
        target_ref=target_ref or f"{target_type}:{target_id}",
        level=level,
        target_type=target_type,
        target_id=target_id,
    )


def _calc_report_status(issues: list[AFLValidationIssue]) -> str:
    if any(i.level == AFL_LEVEL_ERROR for i in issues):
        return AFL_REPORT_FAIL
    if any(i.level == AFL_LEVEL_WARN for i in issues):
        return AFL_REPORT_WARN
    return AFL_REPORT_PASS


def _make_report(target_ref: str, issues: list[AFLValidationIssue]) -> AFLValidationReport:
    status = _calc_report_status(issues)
    return AFLValidationReport(
        report_id=new_id("report"),
        target_ref=target_ref,
        status=status,
        issues=tuple(issues),
        created_at=utc_now_iso(),
        issue_count=len(issues),
    )


class AFLEngine:
    """AFL Engine — structural validation only. No AI, no providers, no media."""

    module_name = "AFL Engine"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._reports: dict[str, AFLValidationReport] = {}

    def get_readiness(self) -> Readiness:
        return self.readiness

    def describe(self) -> str:
        return (
            "AFL Engine supports local structural validation checks "
            "and remains not ready for full product implementation."
        )

    # ------------------------------------------------------------------
    # v0.1 methods (backward compat)
    # ------------------------------------------------------------------

    def validate_structure(self, target_ref: str, payload: object) -> AFLValidationReport:
        """v0.1 minimal structural check."""
        clean_target_ref = target_ref.strip() if isinstance(target_ref, str) else ""
        if not clean_target_ref:
            raise ValidationError("target_ref must not be empty.")

        issues: list[AFLValidationIssue] = []
        if not isinstance(payload, dict):
            issues.append(_issue("AFL-001", "Payload must be a dict.", AFL_LEVEL_ERROR,
                                 target_ref=clean_target_ref))
        elif not payload:
            issues.append(_issue("AFL-002", "Payload must not be empty.", AFL_LEVEL_ERROR,
                                 target_ref=clean_target_ref))

        # Use legacy status for v0.1 compat
        legacy_status = AFL_STATUS_VALID if not issues else AFL_STATUS_INVALID
        report = AFLValidationReport(
            report_id=new_id("report"),
            target_ref=clean_target_ref,
            status=legacy_status,
            issues=tuple(issues),
            created_at=utc_now_iso(),
            issue_count=len(issues),
        )
        self._reports[report.report_id] = report
        return report

    def validate_project(self, project_id: str, structures: list[dict]) -> list[AFLValidationReport]:
        clean_project_id = project_id.strip() if isinstance(project_id, str) else ""
        if not clean_project_id:
            raise ValidationError("project_id must not be empty.")
        if not isinstance(structures, list):
            raise ValidationError("structures must be a list.")
        reports = []
        for structure in structures:
            if not isinstance(structure, dict):
                raise ValidationError("Each structure must be a dict.")
            target_ref = str(structure.get("target_ref", ""))
            payload = structure.get("payload", {})
            report = self.validate_structure(target_ref, payload)
            reports.append(report)
        return reports

    # ------------------------------------------------------------------
    # TASK-000060: v0.2 structural validation
    # ------------------------------------------------------------------

    def validate_scene(self, scene: Any) -> AFLValidationReport:
        """Validate a SceneRecord or dict for structural completeness."""
        if hasattr(scene, "scene_id"):
            sid = scene.scene_id
            title = getattr(scene, "title", "")
            target_ref = f"scene:{sid}"
        elif isinstance(scene, dict):
            sid = scene.get("scene_id", "")
            title = scene.get("title", "")
            target_ref = f"scene:{sid}"
        else:
            raise ValidationError("scene must be a SceneRecord or dict.")

        issues: list[AFLValidationIssue] = []
        if not title or not title.strip():
            issues.append(_issue("S-001", "Scene has no title.", AFL_LEVEL_ERROR,
                                 target_type="scene", target_id=sid))
        report = _make_report(target_ref, issues)
        self._reports[report.report_id] = report
        return report

    def validate_shot(self, shot: Any, known_scene_ids: set[str] | None = None) -> AFLValidationReport:
        """Validate a ShotRecord or dict."""
        if hasattr(shot, "shot_id"):
            shot_id = shot.shot_id
            title = getattr(shot, "title", "")
            scene_id = getattr(shot, "scene_id", "")
            target_ref = f"shot:{shot_id}"
        elif isinstance(shot, dict):
            shot_id = shot.get("shot_id", "")
            title = shot.get("title", "")
            scene_id = shot.get("scene_id", "")
            target_ref = f"shot:{shot_id}"
        else:
            raise ValidationError("shot must be a ShotRecord or dict.")

        issues: list[AFLValidationIssue] = []
        if not title or not title.strip():
            issues.append(_issue("SH-001", "Shot has no title.", AFL_LEVEL_ERROR,
                                 target_type="shot", target_id=shot_id))
        if not scene_id or not scene_id.strip():
            issues.append(_issue("SH-002", "Shot has no scene reference.", AFL_LEVEL_ERROR,
                                 target_type="shot", target_id=shot_id))
        elif known_scene_ids is not None and scene_id not in known_scene_ids:
            issues.append(_issue("SH-003",
                                 f"Shot references non-existent scene: {scene_id}",
                                 AFL_LEVEL_ERROR,
                                 target_type="shot", target_id=shot_id))

        report = _make_report(target_ref, issues)
        self._reports[report.report_id] = report
        return report

    def validate_timeline(
        self, timeline: Any, known_scene_ids: set[str] | None = None,
        known_shot_ids: set[str] | None = None
    ) -> AFLValidationReport:
        """Validate a TimelineRecord or dict."""
        if hasattr(timeline, "timeline_id"):
            tid = timeline.timeline_id
            items = getattr(timeline, "items", ())
            target_ref = f"timeline:{tid}"
        elif isinstance(timeline, dict):
            tid = timeline.get("timeline_id", "")
            items = timeline.get("items", [])
            target_ref = f"timeline:{tid}"
        else:
            raise ValidationError("timeline must be a TimelineRecord or dict.")

        issues: list[AFLValidationIssue] = []
        for item in items:
            if hasattr(item, "item_type"):
                item_id = item.item_id
                item_type = item.item_type
                target_id = item.target_id
            elif isinstance(item, dict):
                item_id = item.get("item_id", "")
                item_type = item.get("item_type", "")
                target_id = item.get("target_id", "")
            else:
                continue

            if item_type == "scene" and known_scene_ids is not None:
                if target_id not in known_scene_ids:
                    issues.append(_issue("TL-001",
                                         f"Timeline item references missing scene: {target_id}",
                                         AFL_LEVEL_ERROR,
                                         target_type="timeline_item", target_id=item_id))
            elif item_type == "shot" and known_shot_ids is not None:
                if target_id not in known_shot_ids:
                    issues.append(_issue("TL-002",
                                         f"Timeline item references missing shot: {target_id}",
                                         AFL_LEVEL_ERROR,
                                         target_type="timeline_item", target_id=item_id))

        report = _make_report(target_ref, issues)
        self._reports[report.report_id] = report
        return report

    def validate_character(
        self, character: Any, known_asset_ids: set[str] | None = None
    ) -> AFLValidationReport:
        """Validate a CharacterRecord or dict."""
        if hasattr(character, "character_id"):
            cid = character.character_id
            display_name = getattr(character, "display_name", "")
            ref_ids = list(getattr(character, "reference_asset_ids", ()))
            target_ref = f"character:{cid}"
        elif isinstance(character, dict):
            cid = character.get("character_id", "")
            display_name = character.get("display_name", "")
            ref_ids = list(character.get("reference_asset_ids", []))
            target_ref = f"character:{cid}"
        else:
            raise ValidationError("character must be a CharacterRecord or dict.")

        issues: list[AFLValidationIssue] = []
        if not display_name or not display_name.strip():
            issues.append(_issue("CH-001", "Character has no display name.", AFL_LEVEL_ERROR,
                                 target_type="character", target_id=cid))

        if known_asset_ids is not None:
            for aid in ref_ids:
                if aid not in known_asset_ids:
                    issues.append(_issue("CH-002",
                                         f"Character references missing asset: {aid}",
                                         AFL_LEVEL_WARN,
                                         target_type="character", target_id=cid))

        report = _make_report(target_ref, issues)
        self._reports[report.report_id] = report
        return report

    def validate_project_structure(self, service_state: dict[str, Any]) -> AFLValidationReport:
        """Validate full project structure from a service state dict.

        service_state keys: scenes, shots, timelines, characters, assets
        Each value is a list of record objects or dicts.
        """
        scenes = service_state.get("scenes", [])
        shots = service_state.get("shots", [])
        timelines = service_state.get("timelines", [])
        characters = service_state.get("characters", [])
        assets = service_state.get("assets", [])

        def _id(rec: Any, field: str) -> str:
            if hasattr(rec, field):
                return getattr(rec, field, "")
            if isinstance(rec, dict):
                return rec.get(field, "")
            return ""

        known_scene_ids = {_id(s, "scene_id") for s in scenes}
        known_shot_ids = {_id(s, "shot_id") for s in shots}
        known_asset_ids = {_id(a, "asset_id") for a in assets}

        all_issues: list[AFLValidationIssue] = []

        for scene in scenes:
            r = self.validate_scene(scene)
            all_issues.extend(r.issues)

        for shot in shots:
            r = self.validate_shot(shot, known_scene_ids=known_scene_ids)
            all_issues.extend(r.issues)

        for tl in timelines:
            r = self.validate_timeline(tl, known_scene_ids=known_scene_ids,
                                       known_shot_ids=known_shot_ids)
            all_issues.extend(r.issues)

        for char in characters:
            r = self.validate_character(char, known_asset_ids=known_asset_ids)
            all_issues.extend(r.issues)

        project_ref = service_state.get("project_id", "project")
        report = _make_report(f"project:{project_ref}", all_issues)
        self._reports[report.report_id] = report
        return report

    def get_validation_report(self, report_id: str) -> AFLValidationReport:
        clean = report_id.strip() if isinstance(report_id, str) else ""
        if not clean:
            raise ValidationError("report_id must not be empty.")
        try:
            return self._reports[clean]
        except KeyError as exc:
            raise ValidationError(f"Validation report not found: {clean}") from exc

    def list_validation_reports(self, target_ref: str | None = None) -> list[AFLValidationReport]:
        reports = list(self._reports.values())
        if target_ref is not None:
            clean = target_ref.strip()
            reports = [r for r in reports if r.target_ref == clean]
        return reports

    def detect_conflicts(self, structures: list) -> list:
        if not isinstance(structures, list):
            raise ValidationError("structures must be a list.")
        return []

    def replace_validation_reports(self, records: list) -> None:
        from aurora_studio.contracts.afl import AFLValidationReport as _R
        for item in records:
            if not isinstance(item, _R):
                raise ValidationError("replace_validation_reports requires AFLValidationReport instances.")
        self._reports = {r.report_id: r for r in records}
