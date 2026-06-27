"""Aurora Studio desktop shell — usability hardening (TASK-000043).

Structure:
  Top bar    : project controls (path, title, Create, Open, Save Bundle, Load Bundle, Refresh)
  Main area  : Workspace summary (left) + ttk.Notebook tabs (right)
  Bottom bar : Status label + append-only Log panel + Clear Log button

Tabs:
  Scenes & Shots | Timeline | Assets | Characters | AFL | Exports | Plugins

Keyboard shortcuts (bound when window opens):
  Ctrl+N -> create_project   Ctrl+O -> open_project
  Ctrl+S -> save_bundle      Ctrl+R -> refresh
  Ctrl+L -> clear_log        F5     -> refresh
  Escape -> clear_status

Importing this module NEVER opens a window.
tkinter / tkinter.ttk are imported lazily only inside DesktopShell.__init__.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from aurora_studio.ui.actions import UISession


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

TABS = ["Scenes & Shots", "Timeline", "Assets", "Characters", "AFL", "Exports", "Plugins"]
SECTIONS = ["Project", "Workspace", "Status"]
SHORTCUTS: dict[str, str] = {
    "Ctrl+N": "create_project",
    "Ctrl+O": "open_project",
    "Ctrl+S": "save_bundle",
    "Ctrl+R": "refresh",
    "Ctrl+L": "clear_log",
    "F5": "refresh",
    "Escape": "clear_status",
}

_MAX_LOG_MSG_LEN = 200


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def normalize_ui_error(message: Any) -> str:
    """Convert any value to a compact, safe UI error string.

    - None or empty -> 'Unknown error'
    - Newlines collapsed to spaces
    - Trimmed to _MAX_LOG_MSG_LEN characters
    - No Python traceback text reaches the GUI status bar through this helper
    """
    if message is None:
        return "Unknown error"
    msg = str(message).strip()
    if not msg:
        return "Unknown error"
    # Collapse all whitespace (including newlines) to single spaces
    msg = " ".join(msg.split())
    if len(msg) > _MAX_LOG_MSG_LEN:
        msg = msg[:_MAX_LOG_MSG_LEN - 3] + "..."
    return msg


# ---------------------------------------------------------------------------
# Headless smoke (never touches tkinter)
# ---------------------------------------------------------------------------

def headless_smoke() -> dict[str, Any]:
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
        "shortcuts": SHORTCUTS,
    }


# ---------------------------------------------------------------------------
# DesktopShell
# ---------------------------------------------------------------------------

class DesktopShell:
    """Consolidated tkinter desktop shell with usability hardening.

    All UI actions go through UISession. tkinter/ttk imported lazily.
    """

    def __init__(self, root: Any = None, session: UISession | None = None) -> None:
        try:
            import tkinter as tk
            import tkinter.ttk as ttk
            self._tk = tk
            self._ttk = ttk
        except ImportError as exc:
            raise RuntimeError("tkinter is not available.") from exc

        self.session: UISession = session or UISession()

        # Selection state
        self._selected_scene_id: str | None = None
        self._selected_shot_id: str | None = None
        self._selected_timeline_id: str | None = None
        self._selected_timeline_item_id: str | None = None
        self._selected_asset_id: str | None = None
        self._selected_character_id: str | None = None
        self._selected_afl_report_id: str | None = None
        self._selected_export_artifact_id: str | None = None
        self._selected_plugin_id: str | None = None

        # Index maps
        self._scene_index_map: list[str] = []
        self._shot_index_map: list[str] = []
        self._timeline_index_map: list[str] = []
        self._timeline_item_index_map: list[str] = []
        self._asset_index_map: list[str] = []
        self._character_index_map: list[str] = []
        self._afl_report_index_map: list[str] = []
        self._export_artifact_index_map: list[str] = []
        self._plugin_index_map: list[str] = []

        # Listbox widget refs
        self._scene_listbox: Any = None
        self._shot_listbox: Any = None
        self._timeline_listbox: Any = None
        self._tl_item_listbox: Any = None
        self._asset_listbox: Any = None
        self._character_listbox: Any = None
        self._afl_report_listbox: Any = None
        self._export_listbox: Any = None
        self._plugin_listbox: Any = None
        self._log_text: Any = None

        # Log count
        self._log_count: int = 0
        # Inspector state (TASK-000053)
        self._scene_form_loaded: bool = False
        self._shot_form_loaded: bool = False
        self._scene_dirty: bool = False
        self._shot_dirty: bool = False
        self._last_validation_error: str = ""

        if root is None:
            self._root = self._tk.Tk()
        else:
            self._root = root

        self._root.title("Aurora Studio")
        self._root.geometry("1160x720")
        self._root.resizable(True, True)

        self._init_vars()
        self._build_layout()
        self._bind_shortcuts()
        self.refresh()

    # ------------------------------------------------------------------
    # StringVar init
    # ------------------------------------------------------------------

    def _init_vars(self) -> None:
        tk = self._tk
        self._project_path_var = tk.StringVar()
        self._project_title_var = tk.StringVar()
        self._scene_title_var = tk.StringVar()
        self._shot_title_var = tk.StringVar()
        self._timeline_title_var = tk.StringVar()
        self._tl_item_type_var = tk.StringVar()
        self._tl_item_target_var = tk.StringVar()
        self._tl_item_order_var = tk.StringVar()
        self._asset_type_var = tk.StringVar()
        self._asset_name_var = tk.StringVar()
        self._asset_location_var = tk.StringVar()
        self._char_name_var = tk.StringVar()
        self._char_desc_var = tk.StringVar()
        self._char_ref_asset_var = tk.StringVar()
        self._afl_target_var = tk.StringVar()
        self._afl_payload_var = tk.StringVar(value='{"kind": "smoke"}')
        self._export_source_var = tk.StringVar()
        self._export_type_var = tk.StringVar()
        self._export_provider_var = tk.StringVar()
        self._export_content_var = tk.StringVar()
        self._plugin_name_var = tk.StringVar()
        self._plugin_version_var = tk.StringVar()
        self._plugin_caps_var = tk.StringVar()
        self._plugin_perms_var = tk.StringVar()
        # Workspace summary
        self._ws_project_var = tk.StringVar(value="—")
        self._ws_scene_var = tk.StringVar(value="—")
        self._ws_shot_var = tk.StringVar(value="—")
        self._ws_mode_var = tk.StringVar(value="—")
        self._cnt_scenes_var = tk.StringVar(value="0")
        self._cnt_shots_var = tk.StringVar(value="0")
        self._cnt_timelines_var = tk.StringVar(value="0")
        self._cnt_assets_var = tk.StringVar(value="0")
        self._cnt_characters_var = tk.StringVar(value="0")
        self._cnt_afl_var = tk.StringVar(value="0")
        self._cnt_exports_var = tk.StringVar(value="0")
        self._cnt_plugins_var = tk.StringVar(value="0")
        # Scene detail form vars (TASK-000051)
        self._scene_desc_var = tk.StringVar()
        self._scene_purpose_var = tk.StringVar()
        self._scene_location_var = tk.StringVar()
        self._scene_time_of_day_var = tk.StringVar()
        self._scene_mood_var = tk.StringVar()
        self._scene_conflict_var = tk.StringVar()
        self._scene_narrative_beat_var = tk.StringVar()
        self._scene_notes_var = tk.StringVar()
        # Shot detail form vars (TASK-000052)
        self._shot_desc_var = tk.StringVar()
        self._shot_purpose_var = tk.StringVar()
        self._shot_type_var2 = tk.StringVar()
        self._shot_camera_angle_var = tk.StringVar()
        self._shot_camera_movement_var = tk.StringVar()
        self._shot_framing_var = tk.StringVar()
        self._shot_lens_var = tk.StringVar()
        self._shot_duration_var = tk.StringVar()
        self._shot_emotion_target_var = tk.StringVar()
        self._shot_visual_focus_var = tk.StringVar()
        self._shot_notes_var = tk.StringVar()
        # Timeline summary vars (TASK-000055)
        self._tl_duration_var = tk.StringVar(value="0.0s")
        self._tl_count_var = tk.StringVar(value="0 items")
        self._tl_scene_count_var = tk.StringVar(value="0 scenes")
        self._tl_shot_count_var = tk.StringVar(value="0 shots")
        # Status
        self._status_var = tk.StringVar(value="Ready.")
        # Selected scene display
        self._sel_scene_var = tk.StringVar(value="—")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        tk = self._tk
        ttk = self._ttk

        top = tk.Frame(self._root, bd=1, relief="raised", pady=3)
        top.pack(fill="x", side="top", padx=2, pady=(2, 0))
        self._build_top_bar(top)

        bot = tk.Frame(self._root, bd=1, relief="sunken")
        bot.pack(fill="x", side="bottom", padx=2, pady=(0, 2))
        self._build_bottom_bar(bot)

        main = tk.Frame(self._root)
        main.pack(fill="both", expand=True, padx=2, pady=2)

        ws_outer = tk.Frame(main, width=210)
        ws_outer.pack(side="left", fill="y", padx=(0, 4))
        ws_outer.pack_propagate(False)
        self._build_workspace_summary(ws_outer)

        nb_frame = tk.Frame(main)
        nb_frame.pack(side="left", fill="both", expand=True)
        self._notebook = ttk.Notebook(nb_frame)
        self._notebook.pack(fill="both", expand=True)
        self._build_tabs()

    def _build_top_bar(self, parent: Any) -> None:
        tk = self._tk
        r = tk.Frame(parent)
        r.pack(fill="x")
        tk.Label(r, text="Path:", width=5, anchor="w").pack(side="left")
        tk.Entry(r, textvariable=self._project_path_var, width=26).pack(side="left", padx=(0, 2))
        tk.Button(r, text="Browse…", command=self.browse_project_path,
                  padx=2, font=("Helvetica", 8)).pack(side="left", padx=(0, 6))
        tk.Label(r, text="Title:", width=4, anchor="w").pack(side="left")
        tk.Entry(r, textvariable=self._project_title_var, width=18).pack(side="left", padx=(0, 8))
        for label, cmd in [
            ("Create (Ctrl+N)", self.create_project),
            ("Open (Ctrl+O)", self.open_project),
            ("Save Bundle (Ctrl+S)", self.save_bundle),
            ("Load Bundle", self.load_bundle),
            ("Refresh (F5)", self.refresh),
        ]:
            tk.Button(r, text=label, command=cmd, padx=3,
                      font=("Helvetica", 8)).pack(side="left", padx=1)

    def _build_workspace_summary(self, parent: Any) -> None:
        tk = self._tk
        ttk = self._ttk
        f = ttk.LabelFrame(parent, text="Workspace")
        f.pack(fill="both", expand=True, padx=2, pady=2)

        for label, var in [
            ("Project:", self._ws_project_var),
            ("Scene:", self._ws_scene_var),
            ("Shot:", self._ws_shot_var),
            ("Mode:", self._ws_mode_var),
        ]:
            r = tk.Frame(f); r.pack(fill="x", pady=1)
            tk.Label(r, text=label, width=8, anchor="w",
                     font=("Helvetica", 8)).pack(side="left")
            tk.Label(r, textvariable=var, fg="navy", anchor="w",
                     font=("Helvetica", 8), wraplength=120).pack(side="left", fill="x", expand=True)

        ttk.Separator(f, orient="horizontal").pack(fill="x", pady=4)

        for label, var in [
            ("Scenes", self._cnt_scenes_var),
            ("Shots", self._cnt_shots_var),
            ("Timelines", self._cnt_timelines_var),
            ("Assets", self._cnt_assets_var),
            ("Characters", self._cnt_characters_var),
            ("AFL Reports", self._cnt_afl_var),
            ("Exports", self._cnt_exports_var),
            ("Plugins", self._cnt_plugins_var),
        ]:
            r = tk.Frame(f); r.pack(fill="x", pady=1)
            tk.Label(r, text=label + ":", width=11, anchor="w",
                     font=("Helvetica", 8)).pack(side="left")
            tk.Label(r, textvariable=var, fg="darkgreen", anchor="w",
                     font=("Helvetica", 8, "bold")).pack(side="left")

    def _build_bottom_bar(self, parent: Any) -> None:
        tk = self._tk
        sf = tk.Frame(parent)
        sf.pack(fill="x")
        tk.Label(sf, text="Status:", font=("Helvetica", 8, "bold")).pack(side="left", padx=4)
        tk.Label(sf, textvariable=self._status_var, anchor="w",
                 font=("Helvetica", 8), fg="darkblue").pack(side="left", fill="x", expand=True)
        tk.Button(sf, text="Clear Status (Esc)", font=("Helvetica", 8),
                  command=self.clear_status).pack(side="right", padx=4)
        lf = tk.Frame(parent)
        lf.pack(fill="x")
        tk.Label(lf, text="Log:", font=("Helvetica", 8, "bold")).pack(side="left", padx=4)
        tk.Button(lf, text="Clear Log (Ctrl+L)", font=("Helvetica", 8),
                  command=self.clear_log).pack(side="right", padx=4)
        sb = tk.Scrollbar(lf, orient="vertical")
        self._log_text = tk.Text(lf, height=4, state="disabled",
                                  yscrollcommand=sb.set, wrap="word",
                                  font=("Courier", 8), relief="flat", bg="#f8f8f8")
        sb.config(command=self._log_text.yview)
        self._log_text.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------

    def _build_tabs(self) -> None:
        for title, builder in [
            ("Scenes & Shots", self._build_scenes_shots_tab),
            ("Timeline", self._build_timeline_tab),
            ("Assets", self._build_assets_tab),
            ("Characters", self._build_characters_tab),
            ("AFL", self._build_afl_tab),
            ("Exports", self._build_exports_tab),
            ("Plugins", self._build_plugins_tab),
        ]:
            frame = self._ttk.Frame(self._notebook)
            self._notebook.add(frame, text=title)
            builder(frame)

    def _entry_row(self, parent: Any, label: str, var: Any, width: int = 24) -> None:
        r = self._tk.Frame(parent); r.pack(fill="x", pady=1)
        self._tk.Label(r, text=label, width=10, anchor="w").pack(side="left")
        self._tk.Entry(r, textvariable=var, width=width).pack(side="left", fill="x", expand=True)

    def _listbox_with_sb(self, parent: Any, height: int = 6) -> Any:
        f = self._tk.Frame(parent); f.pack(fill="both", expand=True, pady=2)
        sb = self._tk.Scrollbar(f, orient="vertical")
        lb = self._tk.Listbox(f, yscrollcommand=sb.set, height=height,
                               font=("Courier", 8))
        sb.config(command=lb.yview)
        lb.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return lb

    def _btn_row(self, parent: Any, buttons: list[tuple[str, Any]]) -> None:
        r = self._tk.Frame(parent); r.pack(pady=2)
        for label, cmd in buttons:
            self._tk.Button(r, text=label, command=cmd, padx=4).pack(side="left", padx=2)

    def _build_scenes_shots_tab(self, parent: Any) -> None:
        pane = self._tk.Frame(parent)
        pane.pack(fill="both", expand=True, padx=4, pady=4)

        sl = self._ttk.LabelFrame(pane, text="Scenes")
        sl.pack(side="left", fill="both", expand=True, padx=(0, 2))
        self._entry_row(sl, "Title:", self._scene_title_var)
        r = self._tk.Frame(sl); r.pack(fill="x")
        self._tk.Label(r, text="Selected:", width=10, anchor="w").pack(side="left")
        self._tk.Label(r, textvariable=self._sel_scene_var, fg="darkgreen",
                        anchor="w").pack(side="left")
        self._btn_row(sl, [("Create Scene", self.create_scene)])
        self._scene_listbox = self._listbox_with_sb(sl, height=5)
        self._scene_listbox.bind("<<ListboxSelect>>", self._on_scene_lb)
        # Scene detail panel (TASK-000051)
        sd = self._ttk.LabelFrame(sl, text="Scene Detail")
        sd.pack(fill="x", padx=2, pady=2)
        self._entry_row(sd, "Desc:", self._scene_desc_var, width=20)
        self._entry_row(sd, "Purpose:", self._scene_purpose_var, width=20)
        self._entry_row(sd, "Location:", self._scene_location_var, width=20)
        self._entry_row(sd, "Time:", self._scene_time_of_day_var, width=20)
        self._entry_row(sd, "Mood:", self._scene_mood_var, width=20)
        self._entry_row(sd, "Conflict:", self._scene_conflict_var, width=20)
        self._entry_row(sd, "Beat:", self._scene_narrative_beat_var, width=20)
        self._entry_row(sd, "Notes:", self._scene_notes_var, width=20)
        self._btn_row(sd, [
            ("Load Detail", self.load_selected_scene_detail),
            ("Apply", self.apply_scene_detail_changes),
            ("Clear", self.clear_scene_detail_form),
        ])

        sh = self._ttk.LabelFrame(pane, text="Shots")
        sh.pack(side="left", fill="both", expand=True, padx=(0, 2))
        self._entry_row(sh, "Title:", self._shot_title_var)
        self._btn_row(sh, [("Create Shot", self.create_shot)])
        self._shot_listbox = self._listbox_with_sb(sh, height=5)
        self._shot_listbox.bind("<<ListboxSelect>>", self._on_shot_lb)
        # Shot detail panel (TASK-000052)
        shd = self._ttk.LabelFrame(sh, text="Shot Detail")
        shd.pack(fill="x", padx=2, pady=2)
        self._entry_row(shd, "Desc:", self._shot_desc_var, width=20)
        self._entry_row(shd, "Purpose:", self._shot_purpose_var, width=20)
        self._entry_row(shd, "Type:", self._shot_type_var2, width=20)
        self._entry_row(shd, "Angle:", self._shot_camera_angle_var, width=20)
        self._entry_row(shd, "Movement:", self._shot_camera_movement_var, width=20)
        self._entry_row(shd, "Framing:", self._shot_framing_var, width=20)
        self._entry_row(shd, "Lens:", self._shot_lens_var, width=20)
        self._entry_row(shd, "Duration:", self._shot_duration_var, width=20)
        self._entry_row(shd, "Emotion:", self._shot_emotion_target_var, width=20)
        self._entry_row(shd, "Focus:", self._shot_visual_focus_var, width=20)
        self._entry_row(shd, "Notes:", self._shot_notes_var, width=20)
        self._btn_row(shd, [
            ("Load Detail", self.load_selected_shot_detail),
            ("Apply", self.apply_shot_detail_changes),
            ("Clear", self.clear_shot_detail_form),
        ])

    def _build_timeline_tab(self, parent: Any) -> None:
        pane = self._tk.Frame(parent)
        pane.pack(fill="both", expand=True, padx=4, pady=4)

        tl = self._ttk.LabelFrame(pane, text="Timelines")
        tl.pack(side="left", fill="both", expand=True, padx=(0, 4))
        self._entry_row(tl, "Title:", self._timeline_title_var)
        self._btn_row(tl, [("Create Timeline", self.create_timeline)])
        self._timeline_listbox = self._listbox_with_sb(tl, height=5)
        self._timeline_listbox.bind("<<ListboxSelect>>", self._on_timeline_lb)
        # Timeline summary (TASK-000055)
        tsf = self._ttk.LabelFrame(tl, text="Summary")
        tsf.pack(fill="x", padx=2, pady=2)
        for label, var in [
            ("Duration:", self._tl_duration_var),
            ("Items:", self._tl_count_var),
            ("Scenes:", self._tl_scene_count_var),
            ("Shots:", self._tl_shot_count_var),
        ]:
            rr = self._tk.Frame(tsf); rr.pack(fill="x")
            self._tk.Label(rr, text=label, width=9, anchor="w",
                           font=("Helvetica", 8)).pack(side="left")
            self._tk.Label(rr, textvariable=var, fg="navy", anchor="w",
                           font=("Helvetica", 8, "bold")).pack(side="left")
        self._btn_row(tl, [("Refresh Summary", self.refresh_timeline_summary)])

        it = self._ttk.LabelFrame(pane, text="Timeline Items")
        it.pack(side="left", fill="both", expand=True)
        self._entry_row(it, "Type:", self._tl_item_type_var)
        self._entry_row(it, "Target:", self._tl_item_target_var)
        self._entry_row(it, "Order:", self._tl_item_order_var)
        self._btn_row(it, [
            ("Add Item", self.add_timeline_item),
            ("Remove", self.remove_timeline_item),
            ("Move", self.move_timeline_item),
        ])
        # TASK-000054: scene/shot add + up/down
        self._btn_row(it, [
            ("Add Scene", self.add_selected_scene_to_timeline),
            ("Add Shot", self.add_selected_shot_to_timeline),
        ])
        self._btn_row(it, [
            ("Move Up", self.move_timeline_item_up),
            ("Move Down", self.move_timeline_item_down),
            ("Refresh", self._refresh_timeline_item_list),
        ])
        self._tl_item_listbox = self._listbox_with_sb(it, height=7)
        self._tl_item_listbox.bind("<<ListboxSelect>>", self._on_tl_item_lb)

    def _build_assets_tab(self, parent: Any) -> None:
        f = self._ttk.LabelFrame(parent, text="Assets")
        f.pack(fill="both", expand=True, padx=4, pady=4)
        self._entry_row(f, "Type:", self._asset_type_var)
        self._entry_row(f, "Name:", self._asset_name_var)
        self._entry_row(f, "Location:", self._asset_location_var)
        self._btn_row(f, [
            ("Import Asset", self.import_asset),
            ("Mark Missing", self.mark_asset_missing),
            ("Archive", self.archive_asset),
        ])
        self._asset_listbox = self._listbox_with_sb(f, height=10)
        self._asset_listbox.bind("<<ListboxSelect>>", self._on_asset_lb)

    def _build_characters_tab(self, parent: Any) -> None:
        f = self._ttk.LabelFrame(parent, text="Characters")
        f.pack(fill="both", expand=True, padx=4, pady=4)
        self._entry_row(f, "Name:", self._char_name_var)
        self._entry_row(f, "Desc:", self._char_desc_var)
        self._btn_row(f, [("Create Character", self.create_character)])
        self._character_listbox = self._listbox_with_sb(f, height=6)
        self._character_listbox.bind("<<ListboxSelect>>", self._on_character_lb)
        self._entry_row(f, "Ref Asset:", self._char_ref_asset_var)
        self._btn_row(f, [
            ("Add Ref", self.add_character_reference_asset),
            ("Remove Ref", self.remove_character_reference_asset),
            ("Archive", self.archive_character),
        ])

    def _build_afl_tab(self, parent: Any) -> None:
        f = self._ttk.LabelFrame(parent, text="AFL Validation")
        f.pack(fill="both", expand=True, padx=4, pady=4)
        self._entry_row(f, "Target Ref:", self._afl_target_var)
        self._entry_row(f, "Payload:", self._afl_payload_var)
        self._btn_row(f, [("Validate AFL", self.validate_afl_structure)])
        self._afl_report_listbox = self._listbox_with_sb(f, height=10)
        self._afl_report_listbox.bind("<<ListboxSelect>>", self._on_afl_lb)

    def _build_exports_tab(self, parent: Any) -> None:
        f = self._ttk.LabelFrame(parent, text="Export Artifacts")
        f.pack(fill="both", expand=True, padx=4, pady=4)
        self._entry_row(f, "Source ID:", self._export_source_var)
        self._entry_row(f, "Type:", self._export_type_var)
        self._entry_row(f, "Provider:", self._export_provider_var)
        self._entry_row(f, "Content:", self._export_content_var)
        self._btn_row(f, [
            ("Create Export", self.create_export_artifact),
            ("Mark Ready", self.mark_export_ready),
            ("Mark Failed", self.mark_export_failed),
        ])
        self._export_listbox = self._listbox_with_sb(f, height=8)
        self._export_listbox.bind("<<ListboxSelect>>", self._on_export_lb)

    def _build_plugins_tab(self, parent: Any) -> None:
        f = self._ttk.LabelFrame(parent, text="Plugins")
        f.pack(fill="both", expand=True, padx=4, pady=4)
        self._entry_row(f, "Name:", self._plugin_name_var)
        self._entry_row(f, "Version:", self._plugin_version_var)
        self._entry_row(f, "Caps:", self._plugin_caps_var)
        self._entry_row(f, "Perms:", self._plugin_perms_var)
        self._btn_row(f, [
            ("Register", self.register_plugin),
            ("Enable", self.enable_plugin),
            ("Disable", self.disable_plugin),
        ])
        self._plugin_listbox = self._listbox_with_sb(f, height=8)
        self._plugin_listbox.bind("<<ListboxSelect>>", self._on_plugin_lb)

    # ------------------------------------------------------------------
    # Keyboard shortcuts
    # ------------------------------------------------------------------

    def _bind_shortcuts(self) -> None:
        root = self._root
        root.bind_all("<Control-n>", lambda e: self.create_project())
        root.bind_all("<Control-N>", lambda e: self.create_project())
        root.bind_all("<Control-o>", lambda e: self.open_project())
        root.bind_all("<Control-O>", lambda e: self.open_project())
        root.bind_all("<Control-s>", lambda e: self.save_bundle())
        root.bind_all("<Control-S>", lambda e: self.save_bundle())
        root.bind_all("<Control-r>", lambda e: self.refresh())
        root.bind_all("<Control-R>", lambda e: self.refresh())
        root.bind_all("<Control-l>", lambda e: self.clear_log())
        root.bind_all("<Control-L>", lambda e: self.clear_log())
        root.bind_all("<F5>", lambda e: self.refresh())
        root.bind_all("<Escape>", lambda e: self.clear_status())

    # ------------------------------------------------------------------
    # Listbox callbacks
    # ------------------------------------------------------------------

    def _on_scene_lb(self, event: Any = None) -> None:
        self.on_scene_selected(event)

    def _on_shot_lb(self, event: Any = None) -> None:
        self.on_shot_selected(event)

    def _on_timeline_lb(self, event: Any = None) -> None:
        self.on_timeline_selected(event)

    def _on_tl_item_lb(self, event: Any = None) -> None:
        self.on_timeline_item_selected(event)

    def _on_asset_lb(self, event: Any = None) -> None:
        self.on_asset_selected(event)

    def _on_character_lb(self, event: Any = None) -> None:
        self.on_character_selected(event)

    def _on_afl_lb(self, event: Any = None) -> None:
        self.on_afl_report_selected(event)

    def _on_export_lb(self, event: Any = None) -> None:
        self.on_export_artifact_selected(event)

    def _on_plugin_lb(self, event: Any = None) -> None:
        self.on_plugin_selected(event)

    # ------------------------------------------------------------------
    # Public selection handlers
    # ------------------------------------------------------------------

    def on_scene_selected(self, event: Any = None) -> None:
        if self._scene_listbox is None:
            return
        sel = self._scene_listbox.curselection()
        if sel and sel[0] < len(self._scene_index_map):
            self._selected_scene_id = self._scene_index_map[sel[0]]
            self._sel_scene_var.set(self._selected_scene_id[:18])
            self.session.set_active_scene(self._selected_scene_id)
            self._refresh_shot_list()
            self.append_log(f"Selected scene: {self._selected_scene_id[:16]}")
            try:
                self.load_selected_scene_detail()
            except Exception:
                pass

    def on_shot_selected(self, event: Any = None) -> None:
        if self._shot_listbox is None:
            return
        sel = self._shot_listbox.curselection()
        if sel and sel[0] < len(self._shot_index_map):
            self._selected_shot_id = self._shot_index_map[sel[0]]
            self.session.set_active_shot(self._selected_shot_id)
            self.append_log(f"Selected shot: {self._selected_shot_id[:16]}")

    def on_timeline_selected(self, event: Any = None) -> None:
        if self._timeline_listbox is None:
            return
        sel = self._timeline_listbox.curselection()
        if sel and sel[0] < len(self._timeline_index_map):
            self._selected_timeline_id = self._timeline_index_map[sel[0]]
            self._refresh_timeline_item_list()
            self.append_log(f"Selected timeline: {self._selected_timeline_id[:16]}")
            try:
                self.refresh_timeline_summary()
            except Exception:
                pass

    def on_timeline_item_selected(self, event: Any = None) -> None:
        if self._tl_item_listbox is None:
            return
        sel = self._tl_item_listbox.curselection()
        if sel and sel[0] < len(self._timeline_item_index_map):
            self._selected_timeline_item_id = self._timeline_item_index_map[sel[0]]
            self.append_log(f"Selected tl item: {self._selected_timeline_item_id[:16]}")

    def on_asset_selected(self, event: Any = None) -> None:
        if self._asset_listbox is None:
            return
        sel = self._asset_listbox.curselection()
        if sel and sel[0] < len(self._asset_index_map):
            self._selected_asset_id = self._asset_index_map[sel[0]]
            self.append_log(f"Selected asset: {self._selected_asset_id[:16]}")

    def on_character_selected(self, event: Any = None) -> None:
        if self._character_listbox is None:
            return
        sel = self._character_listbox.curselection()
        if sel and sel[0] < len(self._character_index_map):
            self._selected_character_id = self._character_index_map[sel[0]]
            self.append_log(f"Selected character: {self._selected_character_id[:16]}")

    def on_afl_report_selected(self, event: Any = None) -> None:
        if self._afl_report_listbox is None:
            return
        sel = self._afl_report_listbox.curselection()
        if sel and sel[0] < len(self._afl_report_index_map):
            self._selected_afl_report_id = self._afl_report_index_map[sel[0]]
            self.append_log(f"Selected AFL report: {self._selected_afl_report_id[:16]}")

    def on_export_artifact_selected(self, event: Any = None) -> None:
        if self._export_listbox is None:
            return
        sel = self._export_listbox.curselection()
        if sel and sel[0] < len(self._export_artifact_index_map):
            self._selected_export_artifact_id = self._export_artifact_index_map[sel[0]]
            self.append_log(f"Selected export: {self._selected_export_artifact_id[:16]}")

    def on_plugin_selected(self, event: Any = None) -> None:
        if self._plugin_listbox is None:
            return
        sel = self._plugin_listbox.curselection()
        if sel and sel[0] < len(self._plugin_index_map):
            self._selected_plugin_id = self._plugin_index_map[sel[0]]
            self.append_log(f"Selected plugin: {self._selected_plugin_id[:16]}")

    # ------------------------------------------------------------------
    # Refresh (hardened)
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        try:
            result = self.session.get_app_state()
            if not result.ok:
                self.set_status(normalize_ui_error(result.message))
                return
            state = result.payload or {}
        except Exception as exc:
            self.set_status(normalize_ui_error(exc))
            return

        ws = state.get("workspace") or {}
        self._ws_project_var.set(ws.get("active_project_id") or "—")
        self._ws_scene_var.set(ws.get("active_scene_id") or "—")
        self._ws_shot_var.set(ws.get("active_shot_id") or "—")
        self._ws_mode_var.set(ws.get("mode") or "—")

        scenes = state.get("scenes") or []
        shots = state.get("shots") or []
        timelines = state.get("timelines") or []
        assets = state.get("assets") or []
        characters = state.get("characters") or []
        afl_reports = state.get("afl_reports") or []
        exports = state.get("export_artifacts") or []
        plugins = state.get("plugins") or []

        self._cnt_scenes_var.set(str(len(scenes)))
        self._cnt_shots_var.set(str(len(shots)))
        self._cnt_timelines_var.set(str(len(timelines)))
        self._cnt_assets_var.set(str(len(assets)))
        self._cnt_characters_var.set(str(len(characters)))
        self._cnt_afl_var.set(str(len(afl_reports)))
        self._cnt_exports_var.set(str(len(exports)))
        self._cnt_plugins_var.set(str(len(plugins)))

        self._refresh_scene_list(scenes)
        self._refresh_shot_list(shots)
        self._refresh_timeline_list(timelines)
        self._refresh_asset_list(assets)
        self._refresh_character_list(characters)
        self._refresh_afl_report_list(afl_reports)
        self._refresh_export_list(exports)
        self._refresh_plugin_list(plugins)

        # Clear stale selections
        self._clear_stale_selection("_selected_scene_id", self._scene_index_map,
                                    "_sel_scene_var", "—")
        self._clear_stale_selection("_selected_shot_id", self._shot_index_map)
        self._clear_stale_selection("_selected_timeline_id", self._timeline_index_map)
        self._clear_stale_selection("_selected_timeline_item_id",
                                    self._timeline_item_index_map)
        self._clear_stale_selection("_selected_asset_id", self._asset_index_map)
        self._clear_stale_selection("_selected_character_id", self._character_index_map)
        self._clear_stale_selection("_selected_afl_report_id", self._afl_report_index_map)
        self._clear_stale_selection("_selected_export_artifact_id",
                                    self._export_artifact_index_map)
        self._clear_stale_selection("_selected_plugin_id", self._plugin_index_map)

    def _clear_stale_selection(self, attr: str, index_map: list[str],
                                display_attr: str | None = None,
                                display_reset: str = "—") -> None:
        current = getattr(self, attr, None)
        if current is not None and current not in index_map:
            setattr(self, attr, None)
            if display_attr and hasattr(self, display_attr):
                getattr(self, display_attr).set(display_reset)

    # ------------------------------------------------------------------
    # List refresh helpers
    # ------------------------------------------------------------------

    def _refresh_scene_list(self, scenes: list) -> None:
        if self._scene_listbox is None:
            return
        self._scene_listbox.delete(0, "end")
        self._scene_index_map = []
        for s in scenes:
            self._scene_index_map.append(s["scene_id"])
            self._scene_listbox.insert("end", f"{s['title']}  [{s['scene_id'][:10]}]")

    def _refresh_shot_list(self, shots: list | None = None) -> None:
        if self._shot_listbox is None:
            return
        if shots is None:
            try:
                r = self.session.get_app_state()
                shots = (r.payload or {}).get("shots", []) if r.ok else []
            except Exception:
                shots = []
        if self._selected_scene_id:
            shots = [s for s in shots if s.get("scene_id") == self._selected_scene_id]
        self._shot_listbox.delete(0, "end")
        self._shot_index_map = []
        for s in shots:
            self._shot_index_map.append(s["shot_id"])
            self._shot_listbox.insert(
                "end", f"[{s['order_index']}] {s['title']}  [{s['shot_id'][:10]}]")

    def _refresh_timeline_list(self, timelines: list) -> None:
        if self._timeline_listbox is None:
            return
        self._timeline_listbox.delete(0, "end")
        self._timeline_index_map = []
        for t in timelines:
            self._timeline_index_map.append(t["timeline_id"])
            self._timeline_listbox.insert(
                "end", f"{t['title']}  [{t['timeline_id'][:10]}] ({t['item_count']} items)")

    def _refresh_timeline_item_list(self) -> None:
        if self._tl_item_listbox is None or not self._selected_timeline_id:
            return
        try:
            rec = self.session.service.timeline_manager.get_timeline(
                self._selected_timeline_id)
            items = rec.items
        except Exception:
            items = []
        self._tl_item_listbox.delete(0, "end")
        self._timeline_item_index_map = []
        for it in items:
            self._timeline_item_index_map.append(it.item_id)
            self._tl_item_listbox.insert(
                "end",
                f"[{it.order_index}] {it.item_type}→{it.target_id[:12]}  [{it.item_id[:10]}]")

    def _refresh_asset_list(self, assets: list) -> None:
        if self._asset_listbox is None:
            return
        self._asset_listbox.delete(0, "end")
        self._asset_index_map = []
        for a in assets:
            self._asset_index_map.append(a["asset_id"])
            self._asset_listbox.insert(
                "end",
                f"{a['display_name']} ({a['asset_type']}) [{a['asset_id'][:10]}] {a['state']}")

    def _refresh_character_list(self, characters: list) -> None:
        if self._character_listbox is None:
            return
        self._character_listbox.delete(0, "end")
        self._character_index_map = []
        for c in characters:
            self._character_index_map.append(c["character_id"])
            self._character_listbox.insert(
                "end", f"{c['display_name']}  [{c['character_id'][:10]}] {c['state']}")

    def _refresh_afl_report_list(self, reports: list) -> None:
        if self._afl_report_listbox is None:
            return
        self._afl_report_listbox.delete(0, "end")
        self._afl_report_index_map = []
        for r in reports:
            self._afl_report_index_map.append(r["report_id"])
            self._afl_report_listbox.insert(
                "end",
                f"{r['target_ref'][:16]}  [{r['report_id'][:10]}] {r['status']} ({r['issue_count']} issues)")

    def _refresh_export_list(self, artifacts: list) -> None:
        if self._export_listbox is None:
            return
        self._export_listbox.delete(0, "end")
        self._export_artifact_index_map = []
        for a in artifacts:
            self._export_artifact_index_map.append(a["artifact_id"])
            self._export_listbox.insert(
                "end", f"{a['artifact_type']} [{a['artifact_id'][:10]}] {a['status']}")

    def _refresh_plugin_list(self, plugins: list) -> None:
        if self._plugin_listbox is None:
            return
        self._plugin_listbox.delete(0, "end")
        self._plugin_index_map = []
        for p in plugins:
            self._plugin_index_map.append(p["plugin_id"])
            self._plugin_listbox.insert(
                "end", f"{p['name']} v{p['version']}  [{p['plugin_id'][:10]}] {p['state']}")

    # ------------------------------------------------------------------
    # Status / Log public API
    # ------------------------------------------------------------------

    def set_status(self, message: str) -> None:
        """Update current status label."""
        if hasattr(self, "_status_var") and self._status_var is not None:
            self._status_var.set(normalize_ui_error(message) if not message else str(message))

    def clear_status(self) -> None:
        """Clear the status label only (does not affect app state or log)."""
        if hasattr(self, "_status_var") and self._status_var is not None:
            self._status_var.set("")

    def append_log(self, message: str, level: str = "info") -> None:
        """Append a compact log entry. Never prints to stdout."""
        self._log_count += 1
        level_tag = level.upper()[:5]
        entry = f"[{level_tag}] {normalize_ui_error(message)}"
        if self._log_text is None:
            return
        self._log_text.config(state="normal")
        self._log_text.insert("end", entry + "\n")
        self._log_text.see("end")
        self._log_text.config(state="disabled")

    def _log(self, message: str) -> None:
        """Private helper — delegates to append_log (INFO level)."""
        self.append_log(message, level="info")

    def clear_log(self) -> None:
        """Clear the UI log panel (does not affect app state)."""
        if self._log_text is None:
            return
        self._log_text.config(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.config(state="disabled")
        self.set_status("Log cleared.")

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def get_project_path_input(self) -> str:
        """Return trimmed project path from input field."""
        return self._project_path_var.get().strip()

    def get_project_title_input(self) -> str:
        """Return trimmed project title from input field."""
        return self._project_title_var.get().strip()

    def browse_project_path(self) -> None:
        """Open a folder-picker dialog and set project path input.

        Uses tkinter.filedialog only. Safe if cancelled (no path set).
        Not used by automated tests.
        """
        try:
            from tkinter import filedialog
            path = filedialog.askdirectory(title="Select project folder")
            if path:
                self._project_path_var.set(path)
        except Exception:
            pass  # Headless / display-less environment — silently skip

    # ------------------------------------------------------------------
    # Project
    # ------------------------------------------------------------------

    def create_project(self) -> None:
        path = self.get_project_path_input()
        title = self.get_project_title_input()
        if not path:
            msg = "Project path is required."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.create_project(path, title)
        if r.ok:
            msg = f"Project created: {(r.payload or {}).get('project_id', '')}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    def open_project(self) -> None:
        path = self.get_project_path_input()
        if not path:
            msg = "Project path is required."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.open_project(path)
        if r.ok:
            msg = f"Project opened: {(r.payload or {}).get('project_id', '')}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    # ------------------------------------------------------------------
    # Scene / Shot
    # ------------------------------------------------------------------

    def create_scene(self) -> None:
        r = self.session.create_scene(self._scene_title_var.get().strip())
        if r.ok:
            self._scene_title_var.set("")
            msg = f"Scene created: {(r.payload or {}).get('scene_id', '')}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    def create_shot(self) -> None:
        title = self._shot_title_var.get().strip()
        scene_id = self._selected_scene_id
        if not scene_id:
            try:
                sr = self.session.get_app_state()
                if sr.ok and sr.payload:
                    scene_id = (sr.payload.get("workspace") or {}).get("active_scene_id") or ""
            except Exception:
                scene_id = ""
        if not scene_id:
            msg = "No scene selected or active — select a scene first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.create_shot(scene_id, title)
        if r.ok:
            self._shot_title_var.set("")
            msg = f"Shot created: {(r.payload or {}).get('shot_id', '')}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    # ------------------------------------------------------------------
    # Bundle
    # ------------------------------------------------------------------

    def save_bundle(self) -> None:
        path = self.get_project_path_input()
        if not path:
            msg = "Project path is required to save bundle."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.save_bundle(path)
        if r.ok:
            msg = f"Bundle saved: {(r.payload or {}).get('bundle_path', '')}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")

    def load_bundle(self) -> None:
        path = self.get_project_path_input()
        if not path:
            msg = "Project path is required to load bundle."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.load_and_rehydrate_bundle(path)
        if r.ok:
            for attr in ("_selected_scene_id", "_selected_shot_id",
                         "_selected_timeline_id", "_selected_asset_id",
                         "_selected_character_id", "_selected_afl_report_id",
                         "_selected_export_artifact_id", "_selected_plugin_id"):
                setattr(self, attr, None)
            self._sel_scene_var.set("—")
            msg = "Bundle loaded."
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    def create_timeline(self) -> None:
        r = self.session.create_timeline(self._timeline_title_var.get().strip())
        if r.ok:
            self._timeline_title_var.set("")
            msg = f"Timeline created: {(r.payload or {}).get('timeline_id', '')}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    def add_timeline_item(self) -> None:
        if not self._selected_timeline_id:
            msg = "No timeline selected — select a timeline first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        order_raw = self._tl_item_order_var.get().strip()
        order = int(order_raw) if order_raw.isdigit() else None
        r = self.session.add_timeline_item(
            self._selected_timeline_id,
            self._tl_item_type_var.get().strip(),
            self._tl_item_target_var.get().strip(), order)
        msg = "Item added." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")
        self._refresh_timeline_item_list()

    def remove_timeline_item(self) -> None:
        if not self._selected_timeline_id:
            msg = "No timeline selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        if not self._selected_timeline_item_id:
            msg = "No timeline item selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.remove_timeline_item(
            self._selected_timeline_id, self._selected_timeline_item_id)
        if r.ok:
            self._selected_timeline_item_id = None; msg = "Item removed."
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")
        self._refresh_timeline_item_list()

    def move_timeline_item(self) -> None:
        if not self._selected_timeline_id:
            msg = "No timeline selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        if not self._selected_timeline_item_id:
            msg = "No timeline item selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        order_raw = self._tl_item_order_var.get().strip()
        if not order_raw.isdigit():
            msg = "Order must be a non-negative integer."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.move_timeline_item(
            self._selected_timeline_id, self._selected_timeline_item_id, int(order_raw))
        msg = "Item moved." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")
        self._refresh_timeline_item_list()

    # ------------------------------------------------------------------
    # Asset
    # ------------------------------------------------------------------

    def import_asset(self) -> None:
        r = self.session.import_asset(
            self._asset_type_var.get().strip(),
            self._asset_name_var.get().strip(),
            self._asset_location_var.get().strip())
        if r.ok:
            self._asset_type_var.set(""); self._asset_name_var.set("")
            msg = f"Asset imported: {(r.payload or {}).get('asset_id', '')}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    def mark_asset_missing(self) -> None:
        if not self._selected_asset_id:
            msg = "No asset selected — select an asset first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.mark_asset_missing(self._selected_asset_id)
        msg = "Asset marked missing." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    def archive_asset(self) -> None:
        if not self._selected_asset_id:
            msg = "No asset selected — select an asset first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.archive_asset(self._selected_asset_id)
        if r.ok:
            self._selected_asset_id = None; msg = "Asset archived."
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    # ------------------------------------------------------------------
    # Character
    # ------------------------------------------------------------------

    def create_character(self) -> None:
        r = self.session.create_character(
            self._char_name_var.get().strip(), self._char_desc_var.get().strip())
        if r.ok:
            self._char_name_var.set(""); self._char_desc_var.set("")
            msg = f"Character created: {(r.payload or {}).get('character_id', '')}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    def add_character_reference_asset(self) -> None:
        if not self._selected_character_id:
            msg = "No character selected — select a character first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.add_character_reference_asset(
            self._selected_character_id, self._char_ref_asset_var.get().strip())
        msg = "Ref added." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")

    def remove_character_reference_asset(self) -> None:
        if not self._selected_character_id:
            msg = "No character selected — select a character first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.remove_character_reference_asset(
            self._selected_character_id, self._char_ref_asset_var.get().strip())
        msg = "Ref removed." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")

    def archive_character(self) -> None:
        if not self._selected_character_id:
            msg = "No character selected — select a character first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.archive_character(self._selected_character_id)
        if r.ok:
            self._selected_character_id = None; msg = "Character archived."
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    # ------------------------------------------------------------------
    # AFL
    # ------------------------------------------------------------------

    def validate_afl_structure(self) -> None:
        target = self._afl_target_var.get().strip()
        payload = self._afl_payload_var.get().strip()
        r = self.session.validate_afl_structure(target, payload)
        if r.ok:
            p = r.payload or {}
            msg = f"AFL validated: {p.get('report_id', '')[:16]} status={p.get('status', '')}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def create_export_artifact(self) -> None:
        r = self.session.create_export_artifact(
            self._export_source_var.get().strip(),
            self._export_type_var.get().strip(),
            self._export_content_var.get().strip(),
            self._export_provider_var.get().strip() or None)
        if r.ok:
            msg = f"Export created: {(r.payload or {}).get('artifact_id', '')[:16]}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    def mark_export_ready(self) -> None:
        if not self._selected_export_artifact_id:
            msg = "No export artifact selected — select one first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.mark_export_ready(self._selected_export_artifact_id)
        msg = (f"Export ready: {self._selected_export_artifact_id[:16]}"
               if r.ok else normalize_ui_error(r.message))
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    def mark_export_failed(self) -> None:
        if not self._selected_export_artifact_id:
            msg = "No export artifact selected — select one first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.mark_export_failed(self._selected_export_artifact_id)
        msg = "Export marked failed." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    # ------------------------------------------------------------------
    # Plugin
    # ------------------------------------------------------------------

    def register_plugin(self) -> None:
        r = self.session.register_plugin(
            self._plugin_name_var.get().strip(),
            self._plugin_version_var.get().strip(),
            self._plugin_caps_var.get().strip(),
            self._plugin_perms_var.get().strip())
        if r.ok:
            self._plugin_name_var.set(""); self._plugin_version_var.set("")
            msg = f"Plugin registered: {(r.payload or {}).get('plugin_id', '')[:16]}"
        else:
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    def enable_plugin(self) -> None:
        if not self._selected_plugin_id:
            msg = "No plugin selected — select a plugin first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.enable_plugin(self._selected_plugin_id)
        msg = "Plugin enabled." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    def disable_plugin(self) -> None:
        if not self._selected_plugin_id:
            msg = "No plugin selected — select a plugin first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.disable_plugin(self._selected_plugin_id)
        msg = "Plugin disabled." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error"); self.refresh()

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Scene Detail Inspector (TASK-000051 / TASK-000053)
    # ------------------------------------------------------------------

    def load_selected_scene_detail(self) -> None:
        """Load selected scene detail into the detail form."""
        if not self._selected_scene_id:
            msg = "No scene selected — select a scene first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.get_scene_detail(self._selected_scene_id)
        if not r.ok:
            msg = normalize_ui_error(r.message)
            self.set_status(msg); self.append_log(msg, "error")
            self._last_validation_error = msg; return
        p = r.payload or {}
        self._scene_title_var.set(p.get("title", ""))
        self._scene_desc_var.set(p.get("description", ""))
        self._scene_purpose_var.set(p.get("purpose", ""))
        self._scene_location_var.set(p.get("location", ""))
        self._scene_time_of_day_var.set(p.get("time_of_day", ""))
        self._scene_mood_var.set(p.get("mood", ""))
        self._scene_conflict_var.set(p.get("conflict", ""))
        self._scene_narrative_beat_var.set(p.get("narrative_beat", ""))
        self._scene_notes_var.set(p.get("notes", ""))
        self._scene_form_loaded = True
        self._last_validation_error = ""
        self.set_status(f"Scene detail loaded: {self._selected_scene_id[:16]}")

    def apply_scene_detail_changes(self) -> None:
        """Apply scene detail form values to the selected scene."""
        if not self._selected_scene_id:
            msg = "No scene selected — select a scene first."
            self.set_status(msg); self.append_log(msg, "warn")
            self._last_validation_error = msg; return
        fields = {
            "title": self._scene_title_var.get().strip(),
            "description": self._scene_desc_var.get(),
            "purpose": self._scene_purpose_var.get(),
            "location": self._scene_location_var.get(),
            "time_of_day": self._scene_time_of_day_var.get(),
            "mood": self._scene_mood_var.get(),
            "conflict": self._scene_conflict_var.get(),
            "narrative_beat": self._scene_narrative_beat_var.get(),
            "notes": self._scene_notes_var.get(),
        }
        # Filter out None; keep empty strings
        fields = {k: v for k, v in fields.items() if v is not None}
        r = self.session.update_scene_detail(self._selected_scene_id, fields)
        if r.ok:
            self._last_validation_error = ""
            msg = f"Scene updated: {self._selected_scene_id[:16]}"
        else:
            self._last_validation_error = r.message
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")
        self.refresh()

    def clear_scene_detail_form(self) -> None:
        """Clear scene detail form without deleting records."""
        for var in (self._scene_title_var, self._scene_desc_var, self._scene_purpose_var,
                    self._scene_location_var, self._scene_time_of_day_var, self._scene_mood_var,
                    self._scene_conflict_var, self._scene_narrative_beat_var, self._scene_notes_var):
            var.set("")
        self._scene_form_loaded = False
        self._last_validation_error = ""
        self.set_status("Scene detail form cleared.")

    # ------------------------------------------------------------------
    # Shot Detail Inspector (TASK-000052 / TASK-000053)
    # ------------------------------------------------------------------

    def load_selected_shot_detail(self) -> None:
        """Load selected shot detail into the detail form."""
        if not self._selected_shot_id:
            msg = "No shot selected — select a shot first."
            self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.get_shot_detail(self._selected_shot_id)
        if not r.ok:
            msg = normalize_ui_error(r.message)
            self.set_status(msg); self.append_log(msg, "error")
            self._last_validation_error = msg; return
        p = r.payload or {}
        self._shot_title_var.set(p.get("title", ""))
        self._shot_desc_var.set(p.get("description", ""))
        self._shot_purpose_var.set(p.get("purpose", ""))
        self._shot_type_var2.set(p.get("shot_type", ""))
        self._shot_camera_angle_var.set(p.get("camera_angle", ""))
        self._shot_camera_movement_var.set(p.get("camera_movement", ""))
        self._shot_framing_var.set(p.get("framing", ""))
        self._shot_lens_var.set(p.get("lens", ""))
        self._shot_duration_var.set(str(p.get("duration_seconds", "")))
        self._shot_emotion_target_var.set(p.get("emotion_target", ""))
        self._shot_visual_focus_var.set(p.get("visual_focus", ""))
        self._shot_notes_var.set(p.get("notes", ""))
        self._shot_form_loaded = True
        self._last_validation_error = ""
        self.set_status(f"Shot detail loaded: {self._selected_shot_id[:16]}")

    def apply_shot_detail_changes(self) -> None:
        """Apply shot detail form values to the selected shot."""
        if not self._selected_shot_id:
            msg = "No shot selected — select a shot first."
            self.set_status(msg); self.append_log(msg, "warn")
            self._last_validation_error = msg; return
        duration_raw = self._shot_duration_var.get().strip()
        fields: dict = {
            "title": self._shot_title_var.get().strip(),
            "description": self._shot_desc_var.get(),
            "purpose": self._shot_purpose_var.get(),
            "shot_type": self._shot_type_var2.get(),
            "camera_angle": self._shot_camera_angle_var.get(),
            "camera_movement": self._shot_camera_movement_var.get(),
            "framing": self._shot_framing_var.get(),
            "lens": self._shot_lens_var.get(),
            "emotion_target": self._shot_emotion_target_var.get(),
            "visual_focus": self._shot_visual_focus_var.get(),
            "notes": self._shot_notes_var.get(),
        }
        if duration_raw:
            fields["duration_seconds"] = duration_raw
        r = self.session.update_shot_detail(self._selected_shot_id, fields)
        if r.ok:
            self._last_validation_error = ""
            msg = f"Shot updated: {self._selected_shot_id[:16]}"
        else:
            self._last_validation_error = r.message
            msg = normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")
        self.refresh()

    def clear_shot_detail_form(self) -> None:
        """Clear shot detail form without deleting records."""
        for var in (self._shot_title_var, self._shot_desc_var, self._shot_purpose_var,
                    self._shot_type_var2, self._shot_camera_angle_var,
                    self._shot_camera_movement_var, self._shot_framing_var,
                    self._shot_lens_var, self._shot_duration_var,
                    self._shot_emotion_target_var, self._shot_visual_focus_var,
                    self._shot_notes_var):
            var.set("")
        self._shot_form_loaded = False
        self._last_validation_error = ""
        self.set_status("Shot detail form cleared.")

    # ------------------------------------------------------------------
    # Inspector snapshot (TASK-000053)
    # ------------------------------------------------------------------

    def get_inspector_snapshot(self) -> dict:
        """Return JSON-serializable inspector state snapshot."""
        return {
            "selected_scene_id": self._selected_scene_id,
            "selected_shot_id": self._selected_shot_id,
            "scene_form_loaded": self._scene_form_loaded,
            "shot_form_loaded": self._shot_form_loaded,
            "scene_dirty": self._scene_dirty,
            "shot_dirty": self._shot_dirty,
            "last_validation_error": self._last_validation_error,
        }

    # ------------------------------------------------------------------
    # Timeline extended actions (TASK-000054 / TASK-000055)
    # ------------------------------------------------------------------

    def add_selected_scene_to_timeline(self) -> None:
        """Add selected scene to selected timeline."""
        if not self._selected_timeline_id:
            msg = "No timeline selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        if not self._selected_scene_id:
            msg = "No scene selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.add_scene_to_timeline(self._selected_timeline_id, self._selected_scene_id)
        msg = "Scene added to timeline." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")
        self._refresh_timeline_item_list()
        self.refresh_timeline_summary()

    def add_selected_shot_to_timeline(self) -> None:
        """Add selected shot to selected timeline."""
        if not self._selected_timeline_id:
            msg = "No timeline selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        if not self._selected_shot_id:
            msg = "No shot selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.add_shot_to_timeline(self._selected_timeline_id, self._selected_shot_id)
        msg = "Shot added to timeline." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")
        self._refresh_timeline_item_list()
        self.refresh_timeline_summary()

    def move_timeline_item_up(self) -> None:
        """Move selected timeline item up."""
        if not self._selected_timeline_id:
            msg = "No timeline selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        if not self._selected_timeline_item_id:
            msg = "No item selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.move_timeline_item_up(
            self._selected_timeline_id, self._selected_timeline_item_id)
        msg = "Item moved up." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")
        self._refresh_timeline_item_list()
        self.refresh_timeline_summary()

    def move_timeline_item_down(self) -> None:
        """Move selected timeline item down."""
        if not self._selected_timeline_id:
            msg = "No timeline selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        if not self._selected_timeline_item_id:
            msg = "No item selected."; self.set_status(msg); self.append_log(msg, "warn"); return
        r = self.session.move_timeline_item_down(
            self._selected_timeline_id, self._selected_timeline_item_id)
        msg = "Item moved down." if r.ok else normalize_ui_error(r.message)
        self.set_status(msg); self.append_log(msg, "info" if r.ok else "error")
        self._refresh_timeline_item_list()
        self.refresh_timeline_summary()

    def refresh_timeline_summary(self) -> None:
        """Refresh timeline summary labels for selected timeline."""
        if not self._selected_timeline_id:
            self._tl_duration_var.set("0.0s")
            self._tl_count_var.set("0 items")
            self._tl_scene_count_var.set("0 scenes")
            self._tl_shot_count_var.set("0 shots")
            return
        r = self.session.get_timeline_summary(self._selected_timeline_id)
        if r.ok:
            p = r.payload or {}
            self._tl_duration_var.set(f"{p.get('total_duration_seconds', 0.0):.1f}s")
            self._tl_count_var.set(f"{p.get('item_count', 0)} items")
            self._tl_scene_count_var.set(f"{p.get('scene_item_count', 0)} scenes")
            self._tl_shot_count_var.set(f"{p.get('shot_item_count', 0)} shots")
        else:
            self._tl_duration_var.set("error")

    def get_state_snapshot(self) -> dict[str, Any]:
        result = self.session.get_app_state()
        state = result.payload or {}
        return {
            "project": state.get("project"),
            "workspace": state.get("workspace"),
            "scene_count": len(state.get("scenes") or []),
            "shot_count": len(state.get("shots") or []),
            "timeline_count": len(state.get("timelines") or []),
            "asset_count": len(state.get("assets") or []),
            "character_count": len(state.get("characters") or []),
            "afl_report_count": len(state.get("afl_reports") or []),
            "export_artifact_count": len(state.get("export_artifacts") or []),
            "plugin_count": len(state.get("plugins") or []),
            "selected_scene_id": self._selected_scene_id,
            "selected_shot_id": self._selected_shot_id,
            "selected_timeline_id": self._selected_timeline_id,
            "selected_timeline_item_id": self._selected_timeline_item_id,
            "selected_asset_id": self._selected_asset_id,
            "selected_character_id": self._selected_character_id,
            "selected_afl_report_id": self._selected_afl_report_id,
            "selected_export_artifact_id": self._selected_export_artifact_id,
            "selected_plugin_id": self._selected_plugin_id,
            "status": self._status_var.get() if hasattr(self, "_status_var") and self._status_var is not None else "",
            "log_count": self._log_count,
        }

    def get_layout_snapshot(self) -> dict[str, Any]:
        """Return JSON-serializable layout metadata including keyboard shortcuts."""
        return {
            "tabs": list(TABS),
            "sections": list(SECTIONS),
            "has_status": True,
            "has_log": True,
            "has_project_bar": True,
            "shortcuts": dict(SHORTCUTS),
        }

    def run(self) -> None:
        self._root.mainloop()


# ---------------------------------------------------------------------------
# Factory & entry point
# ---------------------------------------------------------------------------

def build_desktop_shell(session: UISession | None = None) -> DesktopShell:
    return DesktopShell(root=None, session=session)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m aurora_studio.ui.desktop_shell",
        description="Aurora Studio desktop shell.",
    )
    parser.add_argument("--headless-smoke", action="store_true")
    parser.add_argument("--no-mainloop", action="store_true")
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
        print(json.dumps({"ok": False, "error": str(exc)},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"Unexpected: {exc}"},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
