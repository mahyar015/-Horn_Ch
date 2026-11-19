# ba_meta require api 9
# ba_meta export babase.Plugin
"""Mahyar Watch - custom replay browser/player controls for BombSquad API 9.

Important engine limitation:
BombSquad's .brp replays are simulation streams, not ordinary video files.
The engine's new_replay_session() replaces the current foreground session.
Therefore starting a replay necessarily leaves/disconnects a remote party session.
This plugin does not attempt to fake an in-session video player.
"""

from __future__ import annotations

import os

import babase
import bauiv1 as bui
import bascenev1 as bs


class MahyarWatchWindow(bui.MainWindow):
    """Replay browser with a custom dark/cyan interface."""

    def __init__(self, transition: str = 'in_right',
                 origin_widget: bui.Widget | None = None):
        self._selected: str | None = None
        self._rows: list[bui.Widget] = []
        self._width = 760
        self._height = 540
        self._scale = (1.35 if bui.app.ui_v1.uiscale is bui.UIScale.SMALL
                       else 1.0)
        root = bui.containerwidget(
            size=(self._width, self._height),
            scale=self._scale,
            transition=transition,
            toolbar_visibility='menu_minimal',
        )
        super().__init__(root_widget=root, transition=transition)
        bui.containerwidget(edit=root, on_cancel_call=self._back)

        bui.textwidget(
            parent=root, position=(self._width * 0.5, self._height - 48),
            size=(0, 0), text='MAHYAR  WATCH', scale=1.45,
            color=(0.25, 0.9, 1.0), h_align='center', v_align='center')
        bui.textwidget(
            parent=root, position=(self._width * 0.5, self._height - 78),
            size=(0, 0), text='Saved replays', scale=0.8,
            color=(0.75, 0.85, 0.9), h_align='center', v_align='center')

        self._scroll = bui.scrollwidget(
            parent=root, position=(35, 105), size=(690, 340),
            border_opacity=0.35)
        self._column = bui.columnwidget(
            parent=self._scroll, border=2, margin=8)
        bui.widget(edit=self._scroll, autoselect=True)

        self._play_btn = bui.buttonwidget(
            parent=root, position=(495, 35), size=(220, 54),
            label='PLAY REPLAY', color=(0.08, 0.48, 0.58),
            textcolor=(1, 1, 1), on_activate_call=self._play)
        self._refresh_btn = bui.buttonwidget(
            parent=root, position=(265, 35), size=(210, 54),
            label='REFRESH', color=(0.16, 0.22, 0.3),
            textcolor=(0.8, 0.95, 1), on_activate_call=self._refresh)
        self._back_btn = bui.buttonwidget(
            parent=root, position=(35, 35), size=(200, 54),
            label='BACK', button_type='back', on_activate_call=self._back)
        bui.containerwidget(edit=root, cancel_button=self._back_btn,
                            selected_child=self._refresh_btn)
        self._refresh()

    def _back(self) -> None:
        bui.app.ui_v1.get_main_window().main_window_back()

    def _refresh(self) -> None:
        for child in self._column.get_children():
            child.delete()
        self._rows = []
        self._selected = None
        try:
            import _bascenev1 as _ba
            replay_dir = _ba.get_replays_dir()
            names = [n for n in os.listdir(replay_dir) if n.lower().endswith('.brp')]
            names.sort(key=lambda n: (n != '__lastReplay.brp', n.lower()))
        except Exception:
            babase.print_exception('Mahyar Watch: could not read replay folder.')
            names = []

        if not names:
            bui.textwidget(
                parent=self._column, size=(630, 45),
                text='No saved replays found.', color=(0.8, 0.8, 0.85),
                h_align='center', v_align='center')
            return

        for index, name in enumerate(names):
            label = ('▶  LAST REPLAY' if name == '__lastReplay.brp'
                     else '▶  ' + name[:-4])
            row = bui.buttonwidget(
                parent=self._column, size=(630, 48), label=label,
                color=(0.08, 0.28, 0.34) if index == 0
                else (0.12, 0.15, 0.2),
                textcolor=(0.65, 0.95, 1.0) if index == 0
                else (0.92, 0.94, 1.0),
                on_activate_call=bui.Call(self._select, name))
            self._rows.append(row)
            if index == 0:
                bui.widget(edit=row, up_widget=self._refresh_btn)

    def _select(self, name: str) -> None:
        self._selected = name
        bui.screenmessage('Selected: ' + name[:-4], color=(0.25, 0.9, 1.0))

    def _play(self) -> None:
        if self._selected is None:
            bui.screenmessage('Select a replay first.', color=(1, 0.3, 0.25))
            bui.getsound('error').play()
            return

        # Replays are engine sessions, not video textures. Starting one
        # replaces the current session; remote party connection cannot remain.
        try:
            import _bascenev1 as _ba
            replay_path = os.path.join(_ba.get_replays_dir(), self._selected)
            bui.containerwidget(edit=self._root_widget, transition='out_left')

            def launch() -> None:
                _ba.set_replay_speed_exponent(0)
                _ba.fade_screen(True)
                _ba.new_replay_session(replay_path)

            _ba.fade_screen(False, endcall=bui.Call(bui.pushcall, launch))
        except Exception:
            babase.print_exception('Mahyar Watch: replay launch failed.')
            bui.screenmessage('Could not start this replay.', color=(1, 0.25, 0.25))

    def get_main_window_state(self) -> bui.MainWindowState:
        return bui.BasicMainWindowState(
            create_call=lambda transition, origin_widget: MahyarWatchWindow(
                transition=transition, origin_widget=origin_widget))


class MahyarReplayHUD:
    """Compact custom playback controls shown during replay sessions."""

    def __init__(self) -> None:
        self._root: bui.Widget | None = None
        self._speed = 0
        self._paused = False
        self._show()

    def _show(self) -> None:
        try:
            self._root = bui.containerwidget(
                size=(680, 92), scale=0.78,
                stack_offset=(0, 0), transition='in_bottom',
                background=True)
            bui.textwidget(
                parent=self._root, position=(310, 72), size=(0, 0),
                text='MAHYAR REPLAY PLAYER', color=(0.25, 0.9, 1),
                scale=0.78, h_align='center', v_align='center')
            buttons = [
                ('-10s', 12, lambda: self._seek(-10.0)),
                ('-5s', 112, lambda: self._seek(-5.0)),
                ('PLAY / PAUSE', 212, self._toggle_pause),
                ('+5s', 362, lambda: self._seek(5.0)),
                ('+10s', 462, lambda: self._seek(10.0)),
                ('SPEED', 562, self._next_speed),
            ]
            for label, x, call in buttons:
                bui.buttonwidget(
                    parent=self._root, position=(x, 12), size=(92, 42),
                    label=label, color=(0.08, 0.36, 0.44),
                    textcolor=(1, 1, 1), on_activate_call=call)
        except Exception:
            babase.print_exception('Mahyar Watch: could not create replay HUD.')

    def _seek(self, delta: float) -> None:
        try:
            import _bascenev1 as _ba
            _ba.seek_replay(delta)
        except Exception:
            babase.print_exception('Mahyar Watch: seek failed.')

    def _toggle_pause(self) -> None:
        try:
            import _bascenev1 as _ba
            if _ba.is_replay_paused():
                _ba.resume_replay()
                self._paused = False
            else:
                _ba.pause_replay()
                self._paused = True
        except Exception:
            babase.print_exception('Mahyar Watch: pause toggle failed.')

    def _next_speed(self) -> None:
        try:
            import _bascenev1 as _ba
            # Exponents -1, 0, 1, 2, 3 = 0.5x, 1x, 2x, 4x, 8x.
            self._speed += 1
            if self._speed > 3:
                self._speed = -1
            _ba.set_replay_speed_exponent(self._speed)
            speed = 2 ** self._speed
            bui.screenmessage('Replay speed: ' + str(speed) + 'x',
                              color=(0.25, 0.9, 1.0))
        except Exception:
            babase.print_exception('Mahyar Watch: speed change failed.')


class MahyarWatchPlugin(babase.Plugin):
    """Adds a custom Watch page to the Mods/settings menu."""

    def __init__(self) -> None:
        self._hud: MahyarReplayHUD | None = None

    def on_app_running(self) -> None:
        self._check_replay_state()

    def _check_replay_state(self) -> None:
        try:
            if bs.is_in_replay():
                if self._hud is None:
                    self._hud = MahyarReplayHUD()
            elif self._hud is not None:
                if self._hud._root is not None:
                    self._hud._root.delete()
                self._hud = None
        except Exception:
            babase.print_exception('Mahyar Watch: replay state check failed.')
        bui.apptimer(0.5, self._check_replay_state)

    def has_settings_ui(self) -> bool:
        return True

    def show_settings_ui(self, source_widget: bui.Widget | None) -> None:
        main_window = bui.app.ui_v1.get_main_window()
        if not main_window.main_window_has_control():
            return
        main_window.main_window_replace(
            MahyarWatchWindow(origin_widget=source_widget))
