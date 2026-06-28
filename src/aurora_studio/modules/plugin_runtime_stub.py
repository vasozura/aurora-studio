"""Plugin runtime stub for Aurora Studio v0.3.

Plugin execution is disabled by default.
execute() always returns a blocked/disabled result.
No plugin code is ever imported, loaded or run.
No subprocess is spawned.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

_BLOCKED_STATUS = "blocked"
_DISABLED_REASON = "Plugin runtime is disabled in v0.3. No plugin code is executed."


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class PluginExecutionRequest:
    plugin_id: str
    action: str = ""
    payload: str = ""
    requested_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "PluginExecutionRequest":
        return cls(
            plugin_id=str(data.get("plugin_id", "")),
            action=str(data.get("action", "")),
            payload=str(data.get("payload", "")),
            requested_at=str(data.get("requested_at", "")),
        )


@dataclass(frozen=True)
class PluginExecutionResult:
    plugin_id: str
    status: str
    message: str
    payload: str = ""
    executed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PluginRuntimeStub:
    """Runtime stub. All execution blocked in v0.3.

    Never imports plugin modules.
    Never calls subprocess.
    Never accesses secrets or provider APIs.
    """

    def is_runtime_enabled(self) -> bool:
        """Always returns False in v0.3."""
        return False

    def execute(self, request: PluginExecutionRequest) -> PluginExecutionResult:
        """Always returns a blocked result. Never executes plugin code."""
        return PluginExecutionResult(
            plugin_id=request.plugin_id,
            status=_BLOCKED_STATUS,
            message=_DISABLED_REASON,
            payload="",
            executed_at=_utc_now(),
        )
