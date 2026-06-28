"""Plugin sandbox policy for Aurora Studio v0.3.

Plugin execution is disabled in v0.3.
is_execution_allowed() always returns False.
No plugin code is ever imported or run here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SandboxPolicyResult:
    allowed: bool
    reason: str
    policy_version: str = "v0.3"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PluginSandbox:
    """Sandbox policy gate. All execution blocked in v0.3."""

    POLICY_VERSION = "v0.3"
    POLICY_STATEMENT = "Plugin execution is disabled in v0.3."

    def is_execution_allowed(self, plugin_id: str = "") -> bool:
        """Always returns False. Plugin execution is disabled in v0.3."""
        return False

    def get_policy(self, plugin_id: str = "") -> SandboxPolicyResult:
        """Returns policy result for display/audit. Never enables execution."""
        return SandboxPolicyResult(
            allowed=False,
            reason=self.POLICY_STATEMENT,
            policy_version=self.POLICY_VERSION,
        )
