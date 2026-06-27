"""Aurora Studio desktop shell — minimal tkinter window.

Public API:
  headless_smoke()            — headless JSON check, no display needed.
  build_desktop_shell(...)    — lazily build a DesktopShell (requires display).
  main(argv=None)             — CLI entrypoint.

Importing this module NEVER opens a window.
tkinter is imported lazily only inside build_desktop_shell() and DesktopShell.
Unit tests must only exercise headless_smoke() or --headless-smoke flag.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from aurora_studio.ui.actions import UISession


# ---------------------------------------------------------------------------
# Headless smoke — no tkinter needed
# ---------------------------------------------------------------------------

def headless_smoke() -> dict[str, Any]:
    """Return a JSON-serializable health dict. Never opens a window."""

    session = UISession()
    state_result = session.get_app_state()
    return {
        "ok": True,
        "application": "aurora-studio",
        "ui": "desktop-shell",
        "mode": "headless-smoke",
        "ui_session": "ready",
        "app_state_ok": state_result.ok,
        "app_state": state_result.payload,
    }


# ---------------------------------------------------------------------------
# DesktopShell — lazy tkinter; never instantiate at import time
# ---------------------------------------------------------------------------

class DesktopShell:
    """Minimal tkinter desktop shell for Aurora Studio.

    Do not instantiate unless a display is available.
    tkinter is imported inside __init__.
    All UI actions go through UISession — never call managers directly.
    """

    def __init__(self, root: Any = None, session: UISession | None = None) -> None:
        try:
            import tkinter as tk
            import tkinter.simpledialog as sd
            import tkinter.messagebox as mb
            self._tk = tk
            self._sd = sd
            self._mb = mb
        except ImportError as exc:
            raise RuntimeError(
                "tkinter is not available in this Python installation."
            ) from exc

        self.session: UISession = session or UISession()

        if root is None:
            self._root = self._tk.Tk()
        else:
            self._root = root

        self._root.title("Aurora Studio")
        self._root.geometry("720x560")
        self._root.resizable(True, True)

        # StringVars for inputs
        self._project_path_var = self._tk.StringVar()
        self._project_title_var = self._tk.StringVar()
        self._scene_title_var = self._tk.StringVar()
        self._shot_title_var = self._tk.StringVar()
        self._bundle_path_var = self._tk.StringVar()

        # StringVars for display labels
        self._active_project_var = self._tk.StringVar(value="—")
        self._active_scene_var = self._tk.StringVar(value="—")
        self._active_shot_var = self._tk.StringVar(value="—")
        self._status_var = self._tk.StringVar(value="Ready.")

        # Listbox references populated by refresh()
        self._scene_listbox: Any = None
        self._shot_listbox: Any = None

        self._build_layout()
        self.refresh()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        tk = self._tk

        top = tk.Frame(self._root)
        top.pack(fill="both", expand=True, padx=6, pady=4)

        # Left column
        left = tk.Frame(top)
        left.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self._build_project_section(left)
        self._build_workspace_section(left)
        self._build_bundle_section(left)

        # Right column
        right = tk.Frame(top)
        right.pack(side="left", fill="both", expand=True)

        self._build_scene_section(right)
        self._build_shot_section(right)

        # Status bar
        status_frame = tk.Frame(self._root, relief="sunken", bd=1)
        status_frame.pack(fill="x", side="bottom", padx=6, pady=(0, 4))
        tk.Label(status_frame, textvariable=self._status_var, anchor="w",
                 font=("Helvetica", 9)).pack(fill="x", padx=4)

    def _build_project_section(self, parent: Any) -> None:
        tk = self._tk
        f = tk.LabelFrame(parent, text="Project", padx=4, pady=4)
        f.pack(fill="x", pady=2)

        tk.Label(f, text="Path:").grid(row=0, column=0, sticky="w")
        tk.Entry(f, textvariable=self._project_path_var, width=22).grid(row=0, column=1, sticky="ew")

        tk.Label(f, text="Title:").grid(row=1, column=0, sticky="w")
        tk.Entry(f, textvariable=self._project_title_var, width=22).grid(row=1, column=1, sticky="ew")

        btn_row = tk.Frame(f)
        btn_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=2)
        tk.Button(btn_row, text="Create Project", command=self.create_project).pack(side="left", padx=2)
        tk.Button(btn_row, text="Open Project", command=self.open_project).pack(side="left", padx=2)

        f.columnconfigure(1, weight=1)

    def _build_workspace_section(self, parent: Any) -> None:
        tk = self._tk
        f = tk.LabelFrame(parent, text="Workspace", padx=4, pady=4)
        f.pack(fill="x", pady=2)

        tk.Label(f, text="Active project:").grid(row=0, column=0, sticky="w")
        tk.Label(f, textvariable=self._active_project_var, fg="blue").grid(row=0, column=1, sticky="w")

        tk.Label(f, text="Active scene:").grid(row=1, column=0, sticky="w")
        tk.Label(f, textvariable=self._active_scene_var, fg="blue").grid(row=1, column=1, sticky="w")

        tk.Label(f, text="Active shot:").grid(row=2, column=0, sticky="w")
        tk.Label(f, textvariable=self._active_shot_var, fg="blue").grid(row=2, column=1, sticky="w")

        tk.Button(f, text="Refresh", command=self.refresh).grid(row=3, column=0, columnspan=2, pady=2)

    def _build_bundle_section(self, parent: Any) -> None:
        tk = self._tk
        f = tk.LabelFrame(parent, text="Bundle", padx=4, pady=4)
        f.pack(fill="x", pady=2)

        tk.Label(f, text="Path:").grid(row=0, column=0, sticky="w")
        tk.Entry(f, textvariable=self._bundle_path_var, width=22).grid(row=0, column=1, sticky="ew")

        btn_row = tk.Frame(f)
        btn_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)
        tk.Button(btn_row, text="Save Bundle", command=self.save_bundle).pack(side="left", padx=2)
        tk.Button(btn_row, text="Load Bundle", command=self.load_bundle).pack(side="left", padx=2)

        f.columnconfigure(1, weight=1)

    def _build_scene_section(self, parent: Any) -> None:
        tk = self._tk
        f = tk.LabelFrame(parent, text="Scenes", padx=4, pady=4)
        f.pack(fill="both", expand=True, pady=2)

        tk.Label(f, text="Title:").pack(anchor="w")
        tk.Entry(f, textvariable=self._scene_title_var).pack(fill="x")
        tk.Button(f, text="Create Scene", command=self.create_scene).pack(pady=2)

        self._scene_listbox = tk.Listbox(f, height=6)
        self._scene_listbox.pack(fill="both", expand=True)

    def _build_shot_section(self, parent: Any) -> None:
        tk = self._tk
        f = tk.LabelFrame(parent, text="Shots", padx=4, pady=4)
        f.pack(fill="both", expand=True, pady=2)

        tk.Label(f, text="Title:").pack(anchor="w")
        tk.Entry(f, textvariable=self._shot_title_var).pack(fill="x")
        tk.Button(f, text="Create Shot", command=self.create_shot).pack(pady=2)

        self._shot_listbox = tk.Listbox(f, height=6)
        self._shot_listbox.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Update visible labels and lists from UISession.get_app_state()."""

        result = self.session.get_app_state()
        if not result.ok:
            self.set_status(f"Refresh failed: {result.message}")
            return

        state = result.payload or {}
        workspace = state.get("workspace") or {}
        scenes = state.get("scenes") or []
        shots = state.get("shots") or []

        self._active_project_var.set(workspace.get("active_project_id") or "—")
        self._active_scene_var.set(workspace.get("active_scene_id") or "—")
        self._active_shot_var.set(workspace.get("active_shot_id") or "—")

        if self._scene_listbox is not None:
            self._scene_listbox.delete(0, "end")
            for s in scenes:
                self._scene_listbox.insert("end", f"{s['scene_id'][:12]}  {s['title']}")

        if self._shot_listbox is not None:
            self._shot_listbox.delete(0, "end")
            for sh in shots:
                self._shot_listbox.insert("end",
                    f"{sh['shot_id'][:12]}  [{sh['order_index']}] {sh['title']}")

    def create_project(self) -> None:
        path = self._project_path_var.get().strip()
        title = self._project_title_var.get().strip()
        result = self.session.create_project(path, title)
        if result.ok:
            pid = (result.payload or {}).get("project_id", "")
            self._bundle_path_var.set(path)
            self.set_status(f"Project created: {pid}")
        else:
            self.set_status(f"Error: {result.message}")
        self.refresh()

    def open_project(self) -> None:
        path = self._project_path_var.get().strip()
        result = self.session.open_project(path)
        if result.ok:
            pid = (result.payload or {}).get("project_id", "")
            self._bundle_path_var.set(path)
            self.set_status(f"Project opened: {pid}")
        else:
            self.set_status(f"Error: {result.message}")
        self.refresh()

    def create_scene(self) -> None:
        title = self._scene_title_var.get().strip()
        result = self.session.create_scene(title)
        if result.ok:
            sid = (result.payload or {}).get("scene_id", "")
            self._scene_title_var.set("")
            self.set_status(f"Scene created: {sid}")
        else:
            self.set_status(f"Error: {result.message}")
        self.refresh()

    def create_shot(self) -> None:
        title = self._shot_title_var.get().strip()
        state = self.session.get_app_state()
        scene_id = ""
        if state.ok and state.payload:
            ws = state.payload.get("workspace") or {}
            scene_id = ws.get("active_scene_id") or ""
        if not scene_id:
            self.set_status("No active scene. Create a scene first.")
            return
        result = self.session.create_shot(scene_id, title)
        if result.ok:
            shid = (result.payload or {}).get("shot_id", "")
            self._shot_title_var.set("")
            self.set_status(f"Shot created: {shid}")
        else:
            self.set_status(f"Error: {result.message}")
        self.refresh()

    def save_bundle(self) -> None:
        path = self._bundle_path_var.get().strip()
        result = self.session.save_bundle(path)
        if result.ok:
            bp = (result.payload or {}).get("bundle_path", path)
            self.set_status(f"Bundle saved: {bp}")
        else:
            self.set_status(f"Error: {result.message}")

    def load_bundle(self) -> None:
        path = self._bundle_path_var.get().strip()
        result = self.session.load_and_rehydrate_bundle(path)
        if result.ok:
            scenes = (result.payload or {}).get("scenes", 0)
            shots = (result.payload or {}).get("shots", 0)
            self.set_status(f"Bundle loaded: {scenes} scenes, {shots} shots")
        else:
            self.set_status(f"Error: {result.message}")
        self.refresh()

    def set_status(self, message: str) -> None:
        """Update the status bar message."""
        self._status_var.set(str(message))

    def get_state_snapshot(self) -> dict[str, Any]:
        """Return JSON-serializable snapshot of current UI state."""
        result = self.session.get_app_state()
        return {
            "ok": result.ok,
            "app_state": result.payload,
            "status": self._status_var.get(),
        }

    def run(self) -> None:
        """Enter tkinter mainloop."""
        self._root.mainloop()


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_desktop_shell(session: UISession | None = None) -> DesktopShell:
    """Lazily import tkinter and build a DesktopShell. Requires a display."""
    # tkinter import happens inside DesktopShell.__init__
    return DesktopShell(root=None, session=session)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m aurora_studio.ui.desktop_shell",
        description="Aurora Studio desktop shell.",
    )
    parser.add_argument("--headless-smoke", action="store_true",
                        help="Run headless smoke check; print JSON.")
    parser.add_argument("--no-mainloop", action="store_true",
                        help="Build shell but skip mainloop (for testing).")
    args = parser.parse_args(argv)

    if args.headless_smoke:
        print(json.dumps(headless_smoke(), ensure_ascii=False, indent=2))
        return 0

    try:
        shell = build_desktop_shell()
        if not args.no_mainloop:
            shell.run()
        return 0
    except RuntimeError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2),
              file=sys.stderr)
        return 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"Unexpected error: {exc}"},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
