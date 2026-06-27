"""AFL contract placeholders and first minimal AFL validation contract."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

AFL_STATUS_VALID = "valid"
AFL_STATUS_INVALID = "invalid"
AFL_STATUS_NOT_CHECKED = "not_checked"


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AFLValidationIssue:
    """Minimal AFL validation issue contract."""

    code: str
    message: str
    severity: str
    target_ref: str = ""


@dataclass(frozen=True)
class AFLValidationReport:
    """Minimal AFL validation report contract.

    This is a structural check report only.
    It does not implement full AFL semantic validation.
    """

    report_id: str
    target_ref: str
    status: str = AFL_STATUS_NOT_CHECKED
    issues: tuple[AFLValidationIssue, ...] = ()
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable validation report."""

        return asdict(self)

    def with_updates(self, **changes: Any) -> "AFLValidationReport":
        """Return a new report with selected fields changed."""

        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AFLValidationReport":
        """Create a validation report from JSON-like data."""

        required = ("report_id", "target_ref", "status", "created_at")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"AFLValidationReport missing required keys: {', '.join(missing)}")

        raw_issues = data.get("issues", [])
        issues = tuple(
            AFLValidationIssue(
                code=str(i["code"]),
                message=str(i["message"]),
                severity=str(i["severity"]),
                target_ref=str(i.get("target_ref", "")),
            )
            for i in raw_issues
        )

        return cls(
            report_id=str(data["report_id"]),
            target_ref=str(data["target_ref"]),
            status=str(data["status"]),
            issues=issues,
            created_at=str(data["created_at"]),
        )
