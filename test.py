# ba_meta require api 9
"""
Mahyar Advanced Replay Player
Standalone plugin for BombSquad 1.8.7 / API 9.

Adds an "ADVANCED PLAYER" button to the official Watch window.
The replay itself is rendered by BombSquad's replay engine; this plugin
adds a replay library window and an in-replay control panel.

Controls available during playback:
- Pause / Resume
- Rewind 5 seconds / Forward 5 seconds
- Slower / Faster playback
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from babase import Plugin
import babase
import bascenev1 as bs
import bauiv1 as bui


_LOG = logging.getLogger("MahyarReplayPlayer")
_PLUGIN_INSTANCE: "MahyarReplayPlayer | None" = None


def _replay_dir() -> str:
    """Return the official BombSquad replay directory."""
    return bui.get_replays_dir()


def _replay_names() -> list[str]:
    """Return replay files in the official replay directory."""
    try:
        names = [
            name for name in os.listdir(_replay_dir())
            if name.lower().endswith(".brp")
        ]
        names.sort(key=lambda value: value.lower())
        # Keep the latest replay easy to find.
        if "__lastReplay.brp" in names:
            names.remove("__lastReplay.brp")
            names.insert(0, "__lastReplay.brp")
        return names
    except Exception:
        _LOG.exception("Could not read replay directory.")
        return []


def _display_name(name: str) -> str:
    if name == "__lastReplay.brp":
        return "Last Game Replay"
    return name[:-4] if name.lower().endswith(".brp") else name


class AdvancedReplayWindow:
    """Large replay-library window opened from the official Watch page."""

    def __init__(self, source_widget: bui.Widget | None = None):
        self._selected: str | None = None
        self._busy = False
        self._row_widgets: list[bui.Widget] = []

        width = 900
        height = 620
        self._root = bui.containerwidget(
            parent=bui.get_special_widget("overlay_stack"),
            size=(width, height),
            scale=0.82,
            stack_offset=(0.0, 0.0),
            transition="in_scale",
            background=True,
            darken_behind=True,
        )

        bui.textwidget(
            parent=self._root,
            position=(width * 0.5, height - 48),
            size=(0, 0),
            text="MAHYAR  |  ADVANCED REPLAY PLAYER",
            color=(0.75, 0.9, 1.0),
            scale=1.15,
            h_align="center",
            v_align="center",
        )

        bui.textwidget(
            parent=self._root,
            position=(width * 0.5, height - 82),
            size=(0, 0),
            text="Saved replays",
            color=(0.7, 1.0, 0.72),
            scale=0.75,
            h_align="center",
            v_align="center",
        )

        self._selected_text = bui.textwidget(
            parent=self._root,
            position=(width * 0.5, 78),
            size=(width - 80, 25),
            text="Select a replay from the list",
            color=(1.0, 0.9, 0.45),
            scale=0.65,
            h_align="center",
            v_align="center",
        )

        self._scroll = bui.scrollwidget(
            parent=self._root,
            position=(45, 135),
            size=(width - 90, height - 245),
            capture_arrows=True,
        )
        self._column = bui.columnwidget(
            parent=self._scroll,
            border=2,
            margin=8,
        )

        self._play_button = bui.buttonwidget(
            parent=self._root,
            position=(width - 245, 24),
            size=(190, 46),
            label="PLAY SELECTED",
            color=(0.12, 0.55, 0.30),
            textcolor=(1, 1, 1),
            text_scale=0.8,
            on_activate_call=self._play_selected,
        )

        self._refresh_button = bui.buttonwidget(
            parent=self._root,
            position=(width - 455, 24),
            size=(190, 46),
            label="REFRESH",
            color=(0.22, 0.36, 0.62),
            textcolor=(1, 1, 1),
            text_scale=0.75,
            on_activate_call=self._refresh,
        )

        self._close_button = bui.buttonwidget(
            parent=self._root,
            position=(45, 24),
            size=(110, 46),
            label="×",
            color=(0.48, 0.20, 0.22),
            textcolor=(1, 1, 1),
            text_scale=0.75,
            on_activate_call=self.close,
        )

        bui.containerwidget(
            edit=self._root,
            cancel_button=self._close_button,
            selected_child=self._scroll,
        )
        self._refresh()

    def close(self) -> None:
        try:
            if self._root and self._root.exists():
                bui.containerwidget(edit=self._root, transition="out_scale")
        except Exception:
            pass

    def _refresh(self) -> None:
        for child in self._column.get_children():
            child.delete()
        self._row_widgets.clear()

        names = _replay_names()
        if not names:
            bui.textwidget(
                parent=self._column,
                text="No saved .brp replay files were found.",
                scale=0.75,
                color=(1.0, 0.7, 0.55),
                size=(700, 45),
            )
            self._selected = None
            bui.textwidget(
                edit=self._selected_text,
                text="No replay files found",
            )
            return

        for index, name in enumerate(names):
            label = _display_name(name)
            button = bui.buttonwidget(
                parent=self._column,
                size=(700, 44),
                label=label,
                color=(0.18, 0.28, 0.25),
                textcolor=(1.0, 1.0, 1.0),
                text_scale=0.72,
                button_type="square",
                on_activate_call=bui.Call(self._select, name),
            )
            self._row_widgets.append(button)

        self._select(names[0])

    def _select(self, name: str) -> None:
        self._selected = name
        bui.textwidget(
            edit=self._selected_text,
            text="Selected: " + _display_name(name),
        )
        for button in self._row_widgets:
            try:
                bui.buttonwidget(
                    edit=button,
                    color=(0.18, 0.28, 0.25),
                )
            except Exception:
                pass
        # Highlight the selected row.
        try:
            names = _replay_names()
            index = names.index(name)
            bui.buttonwidget(
                edit=self._row_widgets[index],
                color=(0.12, 0.48, 0.34),
            )
        except Exception:
            pass

    def _play_selected(self) -> None:
        if self._selected is None:
            bui.screenmessage("Select a replay first.", color=(1, 0.3, 0.3))
            return
        if self._busy:
            return
        path = os.path.join(_replay_dir(), self._selected)
        if not os.path.isfile(path):
            bui.screenmessage("Replay file no longer exists.", color=(1, 0.3, 0.3))
            self._refresh()
            return
        self._busy = True
        bui.app.create_async_task(self._prepare_and_play(path))

    async def _prepare_and_play(self, path: str) -> None:
        try:
            # Resolve required assets before leaving the menu.
            if not await bs.prepare_replay(path):
                self._busy = False
                return

            if bui.app.classic is not None:
                bui.app.classic.save_ui_state()

            def launch() -> None:
                try:
                    bs.set_replay_speed_exponent(0)
                    bui.fade_screen(True)
                    bs.launch_replay(path)
                except Exception:
                    _LOG.exception("Could not launch replay.")
                    from bascenev1lib import mainmenu
                    bs.new_host_session(mainmenu.MainMenuSession)

            bui.fade_screen(
                False,
                endcall=bui.CallStrict(bui.pushcall, launch),
            )
            self.close()
        except Exception:
            self._busy = False
            _LOG.exception("Replay preparation failed.")
            bui.screenmessage("Could not prepare this replay.", color=(1, 0.3, 0.3))


class ReplayControlOverlay:
    """Compact controls shown over the replay while it is playing."""

    def __init__(self):
        self._root: bui.Widget | None = None
        self._speed = 0
        self._paused = False
        self._make_widgets()

    def _make_widgets(self) -> None:
        width = 560
        height = 92
        try:
            screen_w, _screen_h = bui.get_virtual_screen_size()
            x = max(10.0, (screen_w - width) * 0.5)
        except Exception:
            x = 180.0

        self._root = bui.containerwidget(
            parent=bui.get_special_widget("overlay_stack"),
            position=(x, 35),
            size=(width, height),
            background=True,
            color=(0.08, 0.10, 0.16),
            opacity=0.92,
            scale=0.85,
            stack_offset=(0, 0),
            transition="in_scale",
        )

        bui.textwidget(
            parent=self._root,
            position=(width * 0.5, height - 18),
            size=(0, 0),
            text="REPLAY CONTROLS",
            color=(0.65, 0.9, 1.0),
            scale=0.55,
            h_align="center",
        )

        controls = [
            ("-5s", 10, 42, lambda: self._seek(-5.0)),
            ("PAUSE", 88, 42, self._toggle_pause),
            ("+5s", 166, 42, lambda: self._seek(5.0)),
            ("SLOWER", 244, 42, lambda: self._change_speed(-1)),
            ("FASTER", 340, 42, lambda: self._change_speed(1)),
            ("HIDE", 436, 42, self.close),
        ]
        self._pause_button = None
        for label, px, py, callback in controls:
            button = bui.buttonwidget(
                parent=self._root,
                position=(px, py),
                size=(88, 34),
                label=label,
                color=(0.18, 0.35, 0.52),
                textcolor=(1, 1, 1),
                text_scale=0.58,
                button_type="square",
                on_activate_call=callback,
            )
            if label == "PAUSE":
                self._pause_button = button

        self._speed_text = bui.textwidget(
            parent=self._root,
            position=(width * 0.5, 8),
            size=(0, 0),
            text="Speed: 1x",
            color=(0.85, 0.9, 1.0),
            scale=0.48,
            h_align="center",
        )

    def _seek(self, seconds: float) -> None:
        try:
            bs.seek_replay(seconds)
        except Exception:
            _LOG.exception("Replay seek failed.")

    def _toggle_pause(self) -> None:
        try:
            if bs.is_replay_paused():
                bs.resume_replay()
                self._paused = False
            else:
                bs.pause_replay()
                self._paused = True
            if self._pause_button is not None:
                bui.buttonwidget(
                    edit=self._pause_button,
                    label="RESUME" if self._paused else "PAUSE",
                )
        except Exception:
            _LOG.exception("Could not pause/resume replay.")

    def _change_speed(self, delta: int) -> None:
        try:
            current = bs.get_replay_speed_exponent()
            self._speed = max(-3, min(3, current + delta))
            bs.set_replay_speed_exponent(self._speed)
            speed = 2 ** self._speed
            bui.textwidget(
                edit=self._speed_text,
                text=f"Speed: {speed:g}x",
            )
        except Exception:
            _LOG.exception("Could not change replay speed.")

    def close(self) -> None:
        try:
            if self._root is not None and self._root.exists():
                self._root.delete()
        except Exception:
            pass
        self._root = None

    def exists(self) -> bool:
        try:
            return self._root is not None and self._root.exists()
        except Exception:
            return False


# ba_meta export babase.Plugin
class MahyarReplayPlayer(Plugin):
    """Plugin entry point."""

    def __init__(self):
        global _PLUGIN_INSTANCE
        _PLUGIN_INSTANCE = self
        self._overlay: ReplayControlOverlay | None = None
        self._overlay_hidden_for_current_replay = False
        self._last_replay_state = False
        self._poll_replay_state()

        # Add the launcher button using the same __init__ wrapping pattern
        # used by Spam.py for PartyWindow.
        try:
            from bauiv1lib import watch
            original_init = watch.WatchWindow.__init__

            if not getattr(original_init, "_mahyar_replay_wrapped", False):
                def enhanced_init(window: Any, *args: Any, **kwargs: Any) -> Any:
                    result = original_init(window, *args, **kwargs)
                    try:
                        root = getattr(window, "_root_widget", None)
                        if root is None:
                            return result

                        existing = getattr(window, "_mahyar_advanced_button", None)
                        if existing is not None and existing.exists():
                            return result

                        width = float(getattr(window, "_width", 600))
                        y_offset = float(getattr(window, "yoffs", 100))
                        button = bui.buttonwidget(
                            parent=root,
                            position=(width - 245, y_offset - 58),
                            size=(190, 42),
                            label="ADVANCED PLAYER",
                            color=(0.12, 0.48, 0.34),
                            textcolor=(1, 1, 1),
                            text_scale=0.65,
                            on_activate_call=bui.Call(_open_advanced_window),
                        )
                        window._mahyar_advanced_button = button
                    except Exception:
                        _LOG.exception("Could not add Advanced Player button.")
                    return result

                enhanced_init._mahyar_replay_wrapped = True  # type: ignore[attr-defined]
                watch.WatchWindow.__init__ = enhanced_init
        except Exception:
            _LOG.exception("Could not hook the official Watch window.")

    def _poll_replay_state(self) -> None:
        try:
            in_replay = bool(bs.is_in_replay())
            if in_replay and not self._last_replay_state:
                self._overlay_hidden_for_current_replay = False
            if in_replay:
                if (
                    not self._overlay_hidden_for_current_replay
                    and (self._overlay is None or not self._overlay.exists())
                ):
                    self._overlay = ReplayControlOverlay()
            else:
                if self._overlay is not None:
                    self._overlay.close()
                    self._overlay = None
                self._overlay_hidden_for_current_replay = False
            self._last_replay_state = in_replay
        except Exception:
            _LOG.exception("Replay state check failed.")
        bui.apptimer(0.5, self._poll_replay_state)


def _open_advanced_window() -> None:
    try:
        AdvancedReplayWindow()
    except Exception:
        _LOG.exception("Could not open Advanced Replay Player.")
        bui.screenmessage(
            "Advanced Replay Player could not be opened.",
            color=(1, 0.3, 0.3),
        )


# Patch overlay close behavior so HIDE stays hidden until this replay ends.
_original_overlay_close = ReplayControlOverlay.close


def _hide_overlay(self: ReplayControlOverlay) -> None:
    try:
        if _PLUGIN_INSTANCE is not None:
            _PLUGIN_INSTANCE._overlay_hidden_for_current_replay = True
    except Exception:
        pass
    _original_overlay_close(self)


ReplayControlOverlay.close = _hide_overlay
