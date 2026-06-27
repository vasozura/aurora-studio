"""Aurora Studio desktop shell entrypoint.

Provides:
  headless_smoke()  — headless JSON health check, no display needed.
  main(argv=None)   — CLI entrypoint; --headless-smoke for headless mode,
                       otherwise attempts to launch a minimal tkinter window.

Import of this module never opens a window.
tkinter is imported lazily only when a real window is requested.
Unit tests must only call headless_smoke() or pass --headless-smoke.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from aurora_studio.ui.actions import UISession


# ---------------------------------------------------------------------------
# Headless smoke
# ---------------------------------------------------------------------------

def headless_smoke() -> dict[str, Any]:
    """Run a headless smoke check of the UI session. Returns a JSON-serializable dict."""

    session = UISession()
    state_result = session.get_app_state()
    return {
        "ok": True,
        "mode": "headless-smoke",
        "ui_session": "ready",
        "app_state_ok": state_result.ok,
        "app_state": state_result.payload,
    }


# ---------------------------------------------------------------------------
# Minimal tkinter shell (lazy import — never runs during normal test suite)
# ---------------------------------------------------------------------------

class DesktopShell:
    """Minimal tkinter desktop shell.

    Instantiated only when a display is available and the user requests GUI mode.
    tkinter is imported lazily here so that importing this module never requires a display.
    """

    def __init__(self, session: UISession | None = None) -> None:
        try:
            import tkinter as tk  # noqa: PLC0415
            self._tk = tk
        except ImportError as exc:
            raise RuntimeError(
                "tkinter is not available in this Python installation."
            ) from exc

        self.session = session or UISession()
        self._root: Any = None

    def build(self) -> None:
        tk = self._tk
        self._root = tk.Tk()
        self._root.title("Aurora Studio")
        self._root.geometry("600x400")

        tk.Label(self._root, text="Aurora Studio", font=("Helvetica", 16, "bold")).pack(pady=10)

        frame = tk.Frame(self._root)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        state_result = self.session.get_app_state()
        state = state_result.payload or {}
        project = state.get("project") or {}
        workspace = state.get("workspace") or {}

        tk.Label(frame, text=f"Project: {project.get('title', 'None')}", anchor="w").pack(fill="x")
        tk.Label(frame, text=f"Active project: {workspace.get('active_project_id', 'None')}", anchor="w").pack(fill="x")
        tk.Label(frame, text=f"Scenes: {len(state.get('scenes', []))}", anchor="w").pack(fill="x")
        tk.Label(frame, text=f"Shots: {len(state.get('shots', []))}", anchor="w").pack(fill="x")

    def run(self) -> None:
        self.build()
        self._root.mainloop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m aurora_studio.ui.desktop_shell",
        description="Aurora Studio desktop shell. Use --headless-smoke for CI.",
    )
    parser.add_argument(
        "--headless-smoke",
        action="store_true",
        help="Run headless smoke check and print JSON. No window opened.",
    )
    args = parser.parse_args(argv)

    if args.headless_smoke:
        result = headless_smoke()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    # GUI mode — attempt to open a tkinter window
    try:
        shell = DesktopShell()
        shell.run()
        return 0
    except RuntimeError as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2),
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(
            json.dumps({"ok": False, "error": f"Unexpected error: {exc}"}, ensure_ascii=False, indent=2),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
