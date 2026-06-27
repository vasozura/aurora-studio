"""AFL Engine first minimal implementation."""

from __future__ import annotations

from aurora_studio.contracts.afl import (
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


class AFLEngine:
    """Minimal AFL Engine implementation.

    This class performs minimal structural checks only.

    It does not implement:
    - Full AFL semantic validation
    - Scene/Shot consistency checks
    - Real conflict detection
    - Provider calls
    - Prompt generation
    - Database persistence
    - GUI behavior
    """

    module_name = "AFL Engine"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._reports: dict[str, AFLValidationReport] = {}

    def get_readiness(self) -> Readiness:
        """Return module readiness."""

        return self.readiness

    def describe(self) -> str:
        """Return a short implementation description."""

        return (
            "AFL Engine supports minimal structural validation checks "
            "and remains not ready for full product implementation."
        )

    def validate_structure(self, target_ref: str, payload: object) -> AFLValidationReport:
        """Perform minimal structural validation on a payload.

        Only checks that target_ref is non-empty and payload is a non-empty dict.
        Does not perform full AFL semantic validation.
        """

        clean_target_ref = target_ref.strip() if isinstance(target_ref, str) else ""
        if not clean_target_ref:
            raise ValidationError("target_ref must not be empty.")

        issues: list[AFLValidationIssue] = []

        if not isinstance(payload, dict):
            issues.append(AFLValidationIssue(
                code="AFL-001",
                message="Payload must be a dict.",
                severity="error",
                target_ref=clean_target_ref,
            ))
        elif not payload:
            issues.append(AFLValidationIssue(
                code="AFL-002",
                message="Payload must not be empty.",
                severity="error",
                target_ref=clean_target_ref,
            ))

        status = AFL_STATUS_VALID if not issues else AFL_STATUS_INVALID
        report = AFLValidationReport(
            report_id=new_id("report"),
            target_ref=clean_target_ref,
            status=status,
            issues=tuple(issues),
            created_at=utc_now_iso(),
        )
        self._reports[report.report_id] = report
        return report

    def validate_project(self, project_id: str, structures: list[dict]) -> list[AFLValidationReport]:
        """Validate a list of structures for a project.

        Each structure dict must have 'target_ref' and 'payload' keys.
        """

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

    def get_validation_report(self, report_id: str) -> AFLValidationReport:
        """Return a stored validation report by ID."""

        clean_report_id = report_id.strip() if isinstance(report_id, str) else ""
        if not clean_report_id:
            raise ValidationError("report_id must not be empty.")

        try:
            return self._reports[clean_report_id]
        except KeyError as exc:
            raise ValidationError(f"Validation report not found: {clean_report_id}") from exc

    def list_validation_reports(self, target_ref: str | None = None) -> list[AFLValidationReport]:
        """List stored validation reports, optionally filtered by target reference."""

        reports = list(self._reports.values())
        if target_ref is not None:
            clean_target_ref = target_ref.strip()
            reports = [r for r in reports if r.target_ref == clean_target_ref]
        return reports

    def detect_conflicts(self, structures: list) -> list:
        """Detect structural conflicts across a list of structures.

        Returns an empty list in this minimal implementation.
        Validates input shape only.
        """

        if not isinstance(structures, list):
            raise ValidationError("structures must be a list.")

        return []

    def replace_validation_reports(self, records: list) -> None:
        """Replace in-memory report store. Used by bundle rehydration.

        Accepts only AFLValidationReport instances. Does not change module readiness.
        """

        from aurora_studio.contracts.afl import AFLValidationReport as _AFLValidationReport
        for item in records:
            if not isinstance(item, _AFLValidationReport):
                raise ValidationError("replace_validation_reports requires AFLValidationReport instances.")
        self._reports = {r.report_id: r for r in records}
