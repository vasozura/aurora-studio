"""AFL contract — v0.2 expanded validation issue and report fields (TASK-000060)."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

AFL_STATUS_VALID = "valid"
AFL_STATUS_INVALID = "invalid"
AFL_STATUS_NOT_CHECKED = "not_checked"

# v0.2 report statuses
AFL_REPORT_PASS = "pass"
AFL_REPORT_WARN = "warn"
AFL_REPORT_FAIL = "fail"

# v0.2 issue levels
AFL_LEVEL_INFO = "INFO"
AFL_LEVEL_WARN = "WARN"
AFL_LEVEL_ERROR = "ERROR"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AFLValidationIssue:
    """AFL validation issue — v0.2 adds level, target_type, target_id."""

    code: str
    message: str
    # v0.1 used severity; v0.2 uses level — keep both for compat
    severity: str = "error"
    target_ref: str = ""
    # v0.2 fields
    level: str = "ERROR"
    target_type: str = ""
    target_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AFLValidationIssue":
        # level falls back to severity if not present
        level = str(data.get("level", data.get("severity", "ERROR"))).upper()
        severity = str(data.get("severity", level.lower()))
        return cls(
            code=str(data.get("code", "")),
            message=str(data.get("message", "")),
            severity=severity,
            target_ref=str(data.get("target_ref", "")),
            level=level,
            target_type=str(data.get("target_type", "")),
            target_id=str(data.get("target_id", "")),
        )


@dataclass(frozen=True)
class AFLValidationReport:
    """AFL validation report — v0.2 adds issue_count."""

    report_id: str
    target_ref: str
    status: str = AFL_STATUS_NOT_CHECKED
    issues: tuple[AFLValidationIssue, ...] = ()
    created_at: str = ""
    # v0.2 field
    issue_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["issues"] = [i for i in d["issues"]]
        return d

    def with_updates(self, **changes: Any) -> "AFLValidationReport":
        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AFLValidationReport":
        required = ("report_id", "target_ref", "status", "created_at")
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"AFLValidationReport missing required keys: {', '.join(missing)}")

        raw_issues = data.get("issues", [])
        issues = tuple(
            AFLValidationIssue.from_dict(i) if isinstance(i, dict) else i
            for i in raw_issues
        )

        try:
            ic = int(data.get("issue_count", len(issues)))
        except (TypeError, ValueError):
            ic = len(issues)

        return cls(
            report_id=str(data["report_id"]),
            target_ref=str(data["target_ref"]),
            status=str(data["status"]),
            issues=issues,
            created_at=str(data["created_at"]),
            issue_count=ic,
        )
