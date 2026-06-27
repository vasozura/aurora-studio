"""Placeholder module: PluginManager."""

from aurora_studio.core.readiness import Readiness


class PluginManager:
    """Minimal placeholder for the Plugin Manager module.

    This class establishes the module boundary only.
    It does not implement product behavior.
    """

    module_name = "Plugin Manager"
    readiness = Readiness.NOT_READY

    def get_readiness(self) -> Readiness:
        """Return module readiness."""

        return self.readiness

    def describe(self) -> str:
        """Return a short placeholder description."""

        return f"{self.module_name} is a skeleton placeholder and is not ready."
