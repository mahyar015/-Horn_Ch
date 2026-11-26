# ba_meta require api 9
# ba_meta export babase.Plugin
"""BSLife Auto Server Switch - standalone BombSquad API 9 mod."""

import base64
import json
import threading
import urllib.parse
import urllib.request

import babase
import bauiv1 as bui
import bascenev1 as bs
from bauiv1lib import mainmenu, ingamemenu

API = 'https://api.bslife.ir'
BOOTSTRAP_URL = 'http://bslife.ir/mod.php'
POLL_SECONDS = 3.0

_servers = []
_stats = {}
_selected = None
_waiting = False
_poll_busy = False
_zero_hits = 0
_window = None
_status_widget = None
_main_refresh = mainmenu.MainMenuWindow._refresh
_game_refresh = ingamemenu.InGameMenuWindow._refresh


def _http(url, data=None, timeout=10):
    headers = {'User-Agent': 'BSLifeMod/3.14', 'Accept': '*/*'}
    if data is not None:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read(), response.headers


def _decode_json(raw):
    try:
        return json.loads(raw.decode('utf-8'))
    except Exception:
        try:
            return json.loads(base64.b64decode(raw).decode('utf-8'))
        except Exception:
            return json.loads(base64.b64decode(raw).decode('utf-8-sig'))


def _fetch_server_data():
    env = bui.app.env
    version = getattr(env, 'version', getattr(env, 'engine_version', 0))
    payload = urllib.parse.urlencode({
        'v': '3.14', 'bv': str(version), 'sv': '0', 'cv': '0'
    }).encode('utf-8')
    raw, _headers = _http(BOOTSTRAP_URL, payload, timeout=12)
    data = _decode_json(raw)
    if not isinstance(data, dict) or 's' not in data or 'i' not in data:
        raise RuntimeError('پاسخ فهرست سرورهای BSLife معتبر نیست.')
    def nested(value):
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return json.loads(base64.b64decode(value).decode('utf-8'))
        raise RuntimeError('داده سرورها قابل خواندن نیست.')
    server_map = nested(data['s'])
    ip_map = nested(data['i'])
    if isinstance(ip_map, list):
        ip_map = {str(i): value for i, value in enumerate(ip_map)}
    result = []
    for name, info in server_map.items():
        try:
            ip = ip_map[str(info['i'])]
            port = int(info['p'])
            result.append({'name': str(name), 'ip': str(ip), 'port': port})
        except Exception:
            continue
    if not result:
        raise RuntimeError('هیچ سروری از پاسخ BSLife استخراج نشد.')
    return result


def _fetch_stats():
    raw, _headers = _http(API + '/mod/stats', timeout=8)
    data = _decode_json(raw)
    if not isinstance(data, list):
        raise RuntimeError('ساختار آمار سرورها نامعتبر است.')
    result = {}
    for item in data:
        try:
            ip, port, field2, field3 = item[:4]
            # BSLife's own UI renders stats as field3/field2.
            result[(str(ip), int(port))] = (int(field3), int(field2))
        except Exception:
            continue
    return result


def _load_servers(done=None):
    def worker():
        try:
            servers = _fetch_server_data()
            stats = _fetch_stats()
            error = None
        except Exception as exc:
            servers, stats, error = None, None, str(exc)
        def apply():
            global _servers, _stats
            if error is None:
                _servers, _stats = servers, stats
            if done is not None:
                done(error)
        bui.pushcall(apply, from_other_thread=True)
    threading.Thread(target=worker, daemon=True).start()


def _update_status(text):
    global _status_widget
    try:
        if _status_widget is not None and _status_widget.exists():
            bui.textwidget(edit=_status_widget, text=text)
    except Exception:
        pass
    try:
        bui.screenmessage(text, color=(0.7, 1.0, 0.7))
    except Exception:
        pass


def _stop_waiting():
    global _waiting, _selected, _zero_hits
    _waiting = False
    _selected = None
    _zero_hits = 0
    _update_status('انتظار تعویض سرور لغو شد.')


def _check_target():
    global _poll_busy, _zero_hits, _waiting
    if not _waiting or _selected is None or _poll_busy:
        return
    _poll_busy = True
    target = dict(_selected)
    def worker():
        try:
            stats = _fetch_stats()
            value = stats.get((target['ip'], target['port']))
            error = None if value is not None else 'اطلاعات این سرور در پاسخ آمار پیدا نشد.'
        except Exception as exc:
            value, error = None, str(exc)
        def apply():
            global _poll_busy, _zero_hits, _waiting
            _poll_busy = False
            if not _waiting or _selected is None:
                return
            if error is not None:
                _update_status('خطای دریافت وضعیت؛ همچنان در انتظار...')
                return
            players, maximum = value
            _update_status('سرور %s: %d/%d بازیکن' % (target['name'], players, maximum))
            if players == 0:
                _zero_hits += 1
            else:
                _zero_hits = 0
            # Two valid zero readings protect against a transient/stale sample.
            if _zero_hits >= 2:
                _waiting = False
                _update_status('سرور خالی شد؛ در حال اتصال...')
                try:
                    bs.connect_to_party(target['ip'], target['port'])
                except Exception as exc:
                    _update_status('اتصال ناموفق: ' + str(exc))
        bui.pushcall(apply, from_other_thread=True)
    threading.Thread(target=worker, daemon=True).start()


class ServerSwitchWindow:
    def __init__(self):
        global _window, _status_widget
        _window = self
        self._width, self._height = 560, 440
        self._root = bui.containerwidget(size=(self._width, self._height),
            transition='in_scale', scale=1.0,
            toolbar_visibility='menu_minimal')
        bui.textwidget(parent=self._root, position=(25, 395), size=(510, 30),
            text='BSLife Auto Server Switch', color=(1, 0.85, 0.25),
            scale=1.1, h_align='center')
        _status_widget = bui.textwidget(parent=self._root, position=(25, 355),
            size=(510, 25), text='در حال دریافت لیست سرورها...',
            color=(0.7, 0.9, 1), scale=0.8, h_align='center')
        self._rows = []
        self._rendering = False
        self._refresh_button = bui.buttonwidget(parent=self._root,
            position=(30, 20), size=(130, 45), label='Refresh',
            on_activate_call=self.refresh)
        self._cancel_button = bui.buttonwidget(parent=self._root,
            position=(215, 20), size=(130, 45), label='لغو انتظار',
            on_activate_call=_stop_waiting)
        self._close_button = bui.buttonwidget(parent=self._root,
            position=(400, 20), size=(130, 45), label='بستن',
            on_activate_call=self.close)
        self.refresh()

    def close(self):
        global _window
        try:
            bui.containerwidget(edit=self._root, transition='out_scale')
        except Exception:
            pass
        _window = None

    def refresh(self):
        for widget in self._rows:
            try:
                widget.delete()
            except Exception:
                pass
        self._rows = []
        _update_status('در حال دریافت اطلاعات سرورها...')
        def done(error):
            if error:
                _update_status('دریافت اطلاعات ناموفق بود: ' + error[:90])
                return
            self._draw_rows()
        _load_servers(done)

    def _draw_rows(self):
        global _stats
        for widget in self._rows:
            try: widget.delete()
            except Exception: pass
        self._rows = []
        y = 315
        for server in _servers[:9]:
            count = _stats.get((server['ip'], server['port']))
            label = server['name'] + '   |   ' + ('?/?' if count is None else '%d/%d' % count)
            button = bui.buttonwidget(parent=self._root,
                position=(55, y), size=(450, 31), label=label,
                color=(0.15, 0.24, 0.34), textcolor=(1, 1, 1),
                on_activate_call=bui.Call(self.select, server))
            self._rows.append(button)
            y -= 34
        _update_status('یک سرور را انتخاب کن؛ مود در پس‌زمینه منتظر می‌ماند.')

    def select(self, server):
        global _selected, _waiting, _zero_hits
        _selected = dict(server)
        _waiting = True
        _zero_hits = 0
        _update_status('در انتظار خالی شدن: ' + server['name'])
        bui.screenmessage('سرور مقصد انتخاب شد: ' + server['name'],
                          color=(0.4, 1.0, 0.4))


def _open_window():
    try:
        ServerSwitchWindow()
    except Exception as exc:
        bui.screenmessage('Auto Switch: ' + str(exc), color=(1, 0.2, 0.2))


def _add_main_button(window):
    try:
        root = window.get_root_widget()
        bui.buttonwidget(parent=root, position=(-110, -20), size=(100, 45),
            label='AUTO SWITCH', color=(0.15, 0.38, 0.22),
            textcolor=(1, 1, 1), on_activate_call=_open_window)
    except Exception:
        pass


def _main_refresh(self, *args, **kwargs):
    _main_refresh_original(self, *args, **kwargs)
    _add_main_button(self)


def _game_refresh(self, *args, **kwargs):
    _game_refresh_original(self, *args, **kwargs)
    try:
        root = self.get_root_widget()
        bui.buttonwidget(parent=root, position=(-110, -135), size=(115, 42),
            label='AUTO SWITCH', color=(0.15, 0.38, 0.22),
            textcolor=(1, 1, 1), on_activate_call=_open_window)
    except Exception:
        pass


_main_refresh_original = _main_refresh
_game_refresh_original = _game_refresh


class AutoServerSwitchPlugin(babase.Plugin):
    def __init__(self):
        mainmenu.MainMenuWindow._refresh = _main_refresh
        ingamemenu.InGameMenuWindow._refresh = _game_refresh
        self._timer = bs.AppTimer(POLL_SECONDS, _check_target, repeat=True)

    def on_app_shutdown(self):
        global _waiting
        _waiting = False
        try:
            mainmenu.MainMenuWindow._refresh = _main_refresh_original
            ingamemenu.InGameMenuWindow._refresh = _game_refresh_original
        except Exception:
            pass
