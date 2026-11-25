from babase import Plugin, pushcall
from bauiv1 import (
    containerwidget as cw,
    buttonwidget as bw,
    textwidget as tw,
    get_special_widget as gsw,
    getsound as gs,
    apptimer as teck,
    UIScale as uis,
    app as APP,
    Call,
    clipboard_is_supported as CIS,
    scrollwidget as sw
)
from bascenev1 import (
    chatmessage as CM,
    screenmessage as push,
    get_chat_messages as GCM,
    get_game_roster as get_roster,
    connect_to_party as original_connect,
    disconnect_from_host as original_disconnect,
    get_connection_to_host_info_2 as get_connection_info
)
import math
import re
import time
import datetime
import threading
import queue
import urllib.parse
import urllib.request
import json
from html.parser import HTMLParser
import bauiv1 as bui
import bascenev1
from babase import app
from bascenev1lib.mainmenu import MainMenuSession

SIGNATURE = "By Mahyar"

DEFAULT_LIMITS = {
    'vip': 2000.0, 'cbb': 3000.0, 'cba': 50.0, 'h': 1.0,
    'pun': 1.0, 'sh': 1.0, 'sl': 2.0, 'fr': 2.0,
    'u': 0.5, 'sp': 50.0, 'z': 100.0, 'g': 100.0,
    'd': 1.0, 'cu': 3.0, 'k': 1000.0, 're': 200.0,
    'sm': 500.0, 'fly': 1.0, 'fl': 1.0, 'e': 10.0,
    'hug': 2.0, 'bot': 1.0, 'spin': 1000.0, 'fire': 50.0,
    'efs': 1.0, 'spike': 10.0, 'spidy': 100.0, 'rich': 20.0,
    'fish': 100.0, 'sol': 10.0, 'plasma': 500.0, 'hat': 50.0,
    'tag': 20.0, 'sig': 1000.0,
}

DEFAULT_REACTIONS = {'fr': 'u', 'cu': 'h', 'fl': 'fl'}
DEFAULT_COOLDOWNS = {'fr': 5.0, 'cu': 5.0, 'fl': 5.0}
DEFAULT_COOLDOWN = 5.0
DEFAULT_AUTO_REPLIES = {}


def get_limits():
    try:
        saved = app.config.get('mahyar_limits', None)
        if saved:
            d = dict(DEFAULT_LIMITS); d.update(saved); return d
    except: pass
    return dict(DEFAULT_LIMITS)


def save_limits(limits):
    try:
        app.config['mahyar_limits'] = dict(limits); app.config.commit()
    except: pass


def get_reactions():
    try:
        saved = app.config.get('mahyar_reactions_v18', None)
        if isinstance(saved, dict):
            return dict(saved)
    except: pass
    return dict(DEFAULT_REACTIONS)


def save_reactions(reactions):
    try:
        app.config['mahyar_reactions_v18'] = dict(reactions); app.config.commit()
    except: pass


def get_cooldowns():
    try:
        saved = app.config.get('mahyar_cooldowns_v18', None)
        if isinstance(saved, dict):
            return dict(saved)
    except: pass
    return dict(DEFAULT_COOLDOWNS)


def save_cooldowns(cooldowns):
    try:
        app.config['mahyar_cooldowns_v18'] = dict(cooldowns); app.config.commit()
    except: pass


def get_auto_replies():
    try:
        saved = app.config.get('mahyar_auto_replies', None)
        if saved:
            d = dict(DEFAULT_AUTO_REPLIES); d.update(saved); return d
    except: pass
    return dict(DEFAULT_AUTO_REPLIES)


def save_auto_replies(replies):
    try:
        app.config['mahyar_auto_replies'] = dict(replies); app.config.commit()
    except: pass


def get_spam_settings():
    try:
        msg = app.config.get('mahyar_spam_msg', '')
        delay = app.config.get('mahyar_spam_delay', 2.0)
        return msg, float(delay)
    except: return '', 2.0


def save_spam_settings(msg, delay):
    try:
        app.config['mahyar_spam_msg'] = msg
        app.config['mahyar_spam_delay'] = float(delay)
        app.config.commit()
    except: pass


def get_enabled_state(key, default=True):
    try:
        return app.config.get(f'mahyar_enabled_{key}', default)
    except: return default


def save_enabled_state(key, value):
    try:
        app.config[f'mahyar_enabled_{key}'] = value
        app.config.commit()
    except: pass


def get_saved_server():
    try:
        ip = app.config.get('mahyar_server_ip', '127.0.0.1')
        port = app.config.get('mahyar_server_port', 43210)
        return ip, int(port)
    except:
        return "127.0.0.1", 43210


def save_server(ip, port):
    try:
        app.config['mahyar_server_ip'] = ip
        app.config['mahyar_server_port'] = int(port)
        app.config.commit()
    except: pass


# Keep a live in-memory copy as well as the persistent app config.
# The in-memory value also protects position changes if a config commit is delayed.
_mods_button_position_memory = None

def get_mods_button_position(default_x=None, default_y=None):
    global _mods_button_position_memory
    try:
        if _mods_button_position_memory is not None:
            return (float(_mods_button_position_memory[0]),
                    float(_mods_button_position_memory[1]))
    except Exception:
        _mods_button_position_memory = None
    try:
        x = app.config.get('mahyar_mods_btn_x', default_x)
        y = app.config.get('mahyar_mods_btn_y', default_y)
        if x is not None and y is not None:
            _mods_button_position_memory = (float(x), float(y))
            return _mods_button_position_memory
    except Exception:
        pass
    return default_x, default_y


def save_mods_button_position(x, y):
    global _mods_button_position_memory
    try:
        x, y = float(x), float(y)
        _mods_button_position_memory = (x, y)
    except Exception:
        return
    try:
        app.config['mahyar_mods_btn_x'] = x
        app.config['mahyar_mods_btn_y'] = y
        app.config.commit()
    except Exception as exc:
        print('Mods position config save error: %s' % exc)


def get_filter_words():
    try:
        return list(app.config.get('mahyar_filter_words', []))
    except:
        return []


def save_filter_words(words):
    try:
        app.config['mahyar_filter_words'] = list(words)
        app.config.commit()
    except:
        pass


def get_filter_reply():
    try:
        return app.config.get('mahyar_filter_reply', 'u')
    except:
        return 'u'


def save_filter_reply(value):
    try:
        app.config['mahyar_filter_reply'] = str(value)
        app.config.commit()
    except:
        pass


auto_react_enabled = get_enabled_state('react', True)
auto_reply_enabled = get_enabled_state('reply', True)
auto_buyer_enabled = get_enabled_state('buyer', True)
filter_enabled = get_enabled_state('filter', True)

processed_sell_ids = set()
processed_buy_ids = set()
react_cooldown = {}
auto_reply_cooldown = {}
filter_cooldown = {}

spam_active = False
spam_message = ""
spam_delay = 2.0
spam_counter = 0
spam_timer = None

server_ip, server_port = get_saved_server()

auto_reconnect_enabled = False
auto_reconnect_busy = False

my_own_name = None
my_own_client_id = None
my_own_display_num = None

_limits_cache = None
_limits_cache_time = 0


def _get_cached_limits():
    global _limits_cache, _limits_cache_time
    now = time.time()
    if _limits_cache is None or (now - _limits_cache_time) > 1.0:
        try:
            _limits_cache = get_limits()
            _limits_cache_time = now
        except:
            return get_limits()
    return _limits_cache


class AR:
    @classmethod
    def UIS(c=0):
        i = APP.ui_v1.uiscale
        return [1.5, 1.1, 0.8][0 if i == uis.SMALL else 1 if i == uis.MEDIUM else 2]

    @classmethod
    def add_close_button(c, window, position=(10, 10)):
        return bw(
            parent=window, size=(24, 24), position=position, label='X',
            color=(0.6, 0.15, 0.25), textcolor=(1, 1, 1),
            on_activate_call=Call(c.swish, t=window)
        )

    @classmethod
    def bw(c, **k):
        return bw(**k, textcolor=(1, 1, 1), enable_sound=False, button_type='square')

    @classmethod
    def cw(c, source, ps=0, **k):
        o = source.get_screen_space_center() if source else None
        r = cw(
            **k, scale=c.UIS() + ps, transition='in_scale',
            color=(0.12, 0.14, 0.2), parent=gsw('overlay_stack'),
            scale_origin_stack_offset=o
        )
        cw(r, on_outside_click_call=Call(c.swish, t=r))
        return r

    swish = lambda c=0, t=0: (gs('swish').play(), cw(t, transition='out_scale') if t else t)
    err = lambda t: (gs('block').play(), push(t, color=(1, 1, 0)))


def get_my_ids():
    global my_own_client_id, my_own_display_num, my_own_name
    try:
        roster = get_roster()
        if not my_own_name:
            return None, None
        for entry in roster:
            display = entry.get('display_string', '')
            if display.endswith(my_own_name):
                my_own_client_id = entry.get('client_id')
                players = entry.get('players', [])
                if players:
                    name_full = players[0].get('name_full', '')
                    m = re.match(r'^\s*(\d+)', name_full)
                    if m:
                        my_own_display_num = int(m.group(1))
                    else:
                        my_own_display_num = None
                return my_own_client_id, my_own_display_num
        return None, None
    except Exception as e:
        print(f"Error getting IDs: {e}")
        return None, None


def safe_chat_send(message):
    try:
        CM(message)
    except Exception as e:
        print(f"Chat send error: {e}")


# ---------------------------------------------------------------------------
# Translate outgoing messages typed in the game's party chat.
# The request runs in a worker thread so the game UI never freezes.
# ---------------------------------------------------------------------------
TRANSLATE_CONFIG_KEY = 'mahyar_translate_enabled'
TRANSLATE_LANGUAGE_KEY = 'mahyar_translate_target_language'
translate_enabled = bool(app.config.get(TRANSLATE_CONFIG_KEY, False))
translate_target_language = str(app.config.get(TRANSLATE_LANGUAGE_KEY, 'en'))
_translate_original_chat = None
_translate_lock = threading.Lock()
_translate_queue = queue.Queue()
_translate_worker_active = False
_translate_pending = 0

TRANSLATE_LANGUAGES = [
    ('Afrikaans', 'af'), ('Albanian', 'sq'), ('Amharic', 'am'), ('Arabic', 'ar'),
    ('Armenian', 'hy'), ('Azerbaijani', 'az'), ('Basque', 'eu'), ('Belarusian', 'be'),
    ('Bengali', 'bn'), ('Bosnian', 'bs'), ('Bulgarian', 'bg'), ('Burmese', 'my'),
    ('Catalan', 'ca'), ('Cebuano', 'ceb'), ('Chinese (Simplified)', 'zh-CN'),
    ('Chinese (Traditional)', 'zh-TW'), ('Corsican', 'co'), ('Croatian', 'hr'),
    ('Czech', 'cs'), ('Danish', 'da'), ('Dutch', 'nl'), ('English', 'en'),
    ('Esperanto', 'eo'), ('Estonian', 'et'), ('Filipino', 'tl'), ('Finnish', 'fi'),
    ('French', 'fr'), ('Frisian', 'fy'), ('Galician', 'gl'), ('Georgian', 'ka'),
    ('German', 'de'), ('Greek', 'el'), ('Gujarati', 'gu'), ('Haitian Creole', 'ht'),
    ('Hausa', 'ha'), ('Hawaiian', 'haw'), ('Hebrew', 'iw'), ('Hindi', 'hi'),
    ('Hmong', 'hmn'), ('Hungarian', 'hu'), ('Icelandic', 'is'), ('Igbo', 'ig'),
    ('Indonesian', 'id'), ('Irish', 'ga'), ('Italian', 'it'), ('Japanese', 'ja'),
    ('Javanese', 'jw'), ('Kannada', 'kn'), ('Kazakh', 'kk'), ('Khmer', 'km'),
    ('Korean', 'ko'), ('Kurdish', 'ku'), ('Kyrgyz', 'ky'), ('Lao', 'lo'),
    ('Latin', 'la'), ('Latvian', 'lv'), ('Lithuanian', 'lt'), ('Luxembourgish', 'lb'),
    ('Macedonian', 'mk'), ('Malagasy', 'mg'), ('Malay', 'ms'), ('Malayalam', 'ml'),
    ('Maltese', 'mt'), ('Maori', 'mi'), ('Marathi', 'mr'), ('Mongolian', 'mn'),
    ('Nepali', 'ne'), ('Norwegian', 'no'), ('Pashto', 'ps'), ('Persian', 'fa'),
    ('Polish', 'pl'), ('Portuguese', 'pt'), ('Punjabi', 'pa'), ('Romanian', 'ro'),
    ('Russian', 'ru'), ('Samoan', 'sm'), ('Serbian', 'sr'), ('Sesotho', 'st'),
    ('Sinhala', 'si'), ('Slovak', 'sk'), ('Slovenian', 'sl'), ('Somali', 'so'),
    ('Spanish', 'es'), ('Sundanese', 'su'), ('Swahili', 'sw'), ('Swedish', 'sv'),
    ('Tamil', 'ta'), ('Telugu', 'te'), ('Thai', 'th'), ('Turkish', 'tr'),
    ('Ukrainian', 'uk'), ('Urdu', 'ur'), ('Uzbek', 'uz'), ('Vietnamese', 'vi'),
    ('Welsh', 'cy'), ('Xhosa', 'xh'), ('Yiddish', 'yi'), ('Yoruba', 'yo'),
    ('Zulu', 'zu')
]


def _translate_to_language(message):
    """Translate chat text into the currently selected target language."""
    target = translate_target_language or 'en'
    query = urllib.parse.urlencode({
        'client': 'gtx', 'sl': 'auto', 'tl': target, 'dt': 't', 'q': message
    })
    url = 'https://translate.googleapis.com/translate_a/single?' + query
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request, timeout=12) as response:
        data = json.loads(response.read().decode('utf-8'))
    translated = ''.join(part[0] for part in data[0] if part and part[0])
    return translated.strip() or message


def _translate_send_result(message, args, kwargs):
    global _translate_pending
    try:
        _translate_original_chat(message, *args, **kwargs)
    except Exception as exc:
        print('Translate send error: %s' % exc)
    finally:
        with _translate_lock:
            _translate_pending = max(0, _translate_pending - 1)


def _translate_worker_loop():
    global _translate_pending, _translate_worker_active
    while True:
        try:
            message, args, kwargs = _translate_queue.get_nowait()
        except queue.Empty:
            with _translate_lock:
                if _translate_queue.empty():
                    _translate_worker_active = False
                    return
            continue
        try:
            try:
                translated = _translate_to_language(message) or message
            except Exception as exc:
                print('Translate failed; sending original: %s' % exc)
                translated = message
            import babase as _translate_babase
            _translate_babase.pushcall(
                lambda m=translated, a=args, k=kwargs: _translate_send_result(m, a, k),
                from_other_thread=True)
        except Exception as exc:
            print('Translate callback error: %s' % exc)
            try:
                import babase as _translate_babase
                _translate_babase.pushcall(
                    lambda m=message, a=args, k=kwargs: _translate_send_result(m, a, k),
                    from_other_thread=True)
            except Exception:
                with _translate_lock:
                    _translate_pending = max(0, _translate_pending - 1)
        finally:
            _translate_queue.task_done()


def _translated_chatmessage(message, *args, **kwargs):
    global _translate_pending, _translate_worker_active
    if not translate_enabled or not isinstance(message, str) or not message.strip():
        return _translate_original_chat(message, *args, **kwargs)
    with _translate_lock:
        _translate_queue.put((message, args, kwargs))
        _translate_pending += 1
        should_start = not _translate_worker_active
        if should_start:
            _translate_worker_active = True
    if should_start:
        try:
            threading.Thread(target=_translate_worker_loop, daemon=True).start()
        except Exception as exc:
            print('Translate worker start error: %s' % exc)
            with _translate_lock:
                _translate_worker_active = False
            try:
                _translate_original_chat(message, *args, **kwargs)
            except Exception:
                pass
            with _translate_lock:
                _translate_pending = max(0, _translate_pending - 1)
    return None


def _install_translate_hook():
    global _translate_original_chat
    if _translate_original_chat is None:
        _translate_original_chat = bascenev1.chatmessage
        bascenev1.chatmessage = _translated_chatmessage


def _set_translate_enabled(value):
    global translate_enabled
    translate_enabled = bool(value)
    try:
        app.config[TRANSLATE_CONFIG_KEY] = translate_enabled
        app.config.commit()
    except Exception:
        pass
    push('Translate ON' if translate_enabled else 'Translate OFF',
         color=(0.25, 1.0, 0.4) if translate_enabled else (1.0, 0.55, 0.25))


def _set_translate_language(code):
    global translate_target_language
    translate_target_language = str(code or 'en')
    try:
        app.config[TRANSLATE_LANGUAGE_KEY] = translate_target_language
        app.config.commit()
    except Exception:
        pass
    name = next((n for n, c in TRANSLATE_LANGUAGES if c == translate_target_language), translate_target_language)
    push('Translate language: ' + name, color=(0.3, 0.9, 1.0))


class TranslateLanguageWindow:
    def __init__(self, source):
        self.w = AR.cw(source=source, size=(330, 430), ps=AR.UIS() * 0.3)
        AR.add_close_button(self.w, position=(300, 395))
        tw(parent=self.w, text='SELECT LANGUAGE', scale=0.85,
           position=(165, 395), h_align='center', color=(1, 0.45, 0.78))
        self.scroll = sw(parent=self.w, size=(290, 350), position=(20, 25))
        self.container = cw(parent=self.scroll, size=(280, len(TRANSLATE_LANGUAGES) * 34), background=False)
        total_h = len(TRANSLATE_LANGUAGES) * 34
        for index, (name, code) in enumerate(TRANSLATE_LANGUAGES):
            y = total_h - (index + 1) * 34
            selected = code == translate_target_language
            bw(parent=self.container, label=(('✓ ' if selected else '') + name),
               size=(270, 30), position=(5, y),
               on_activate_call=Call(self.choose, code),
               color=(0.35, 0.18, 0.35) if selected else (0.16, 0.19, 0.27),
               textcolor=(1, 1, 1), button_type='square', text_scale=0.58)
        gs('swish').play()

    def choose(self, code):
        _set_translate_language(code)
        AR.swish(self.w)


class TranslateWindow:
    def __init__(self, source):
        self.w = AR.cw(source=source, size=(310, 225), ps=AR.UIS() * 0.3)
        AR.add_close_button(self.w, position=(280, 190))
        tw(parent=self.w, text='TRANSLATE', scale=0.9,
           position=(155, 190), h_align='center', color=(1, 0.45, 0.78))
        tw(parent=self.w, text='Choose target language:', scale=0.53,
           position=(155, 157), h_align='center', color=(0.88, 0.82, 0.92))
        self.language_btn = bw(
            parent=self.w, label=self._language_label(), size=(250, 35),
            position=(30, 112), on_activate_call=Call(self.open_languages),
            color=(0.28, 0.22, 0.42), textcolor=(1, 1, 1),
            button_type='square', text_scale=0.65)
        self.toggle_btn = bw(
            parent=self.w, label='ON' if translate_enabled else 'OFF',
            size=(250, 42), position=(30, 48),
            on_activate_call=Call(self.toggle),
            color=(0.12, 0.62, 0.25) if translate_enabled else (0.62, 0.16, 0.22),
            textcolor=(1, 1, 1), button_type='square', text_scale=0.85)
        gs('swish').play()

    def _language_label(self):
        name = next((n for n, c in TRANSLATE_LANGUAGES if c == translate_target_language), 'English')
        return 'Language: ' + name

    def open_languages(self):
        TranslateLanguageWindow(self.w)

    def toggle(self):
        _set_translate_enabled(not translate_enabled)
        bw(self.toggle_btn, label='ON' if translate_enabled else 'OFF',
           color=(0.12, 0.62, 0.25) if translate_enabled else (0.62, 0.16, 0.22))
        gs('dingSmall').play()


original_connect_to_party = original_connect

def new_connect_to_party(address, port=43210, print_progress=False):
    global server_ip, server_port
    server_ip = address
    server_port = port
    save_server(address, port)
    push(f'Saved server: {address}:{port}', color=(0, 1, 1))
    return original_connect_to_party(address, port, print_progress)


bascenev1.connect_to_party = new_connect_to_party


def check_auto_reply(msg):
    if not auto_reply_enabled: return False
    try:
        sender = None; content = msg
        if ': ' in msg:
            parts = msg.split(': ', 1)
            sender = parts[0].strip(); content = parts[1].strip()
        if sender and my_own_name:
            if sender == my_own_name: return False

        content_stripped = content.strip().lower()

        for keyword, response in get_auto_replies().items():
            kw_lower = keyword.lower().strip()

            if content_stripped == kw_lower:
                cd_key = f"{keyword}_{sender or 'unknown'}"
                current_time = time.time()
                last_time = auto_reply_cooldown.get(cd_key, 0)
                if current_time - last_time < 2.0: continue
                auto_reply_cooldown[cd_key] = current_time
                if len(auto_reply_cooldown) > 50:
                    now = time.time()
                    to_del = [k for k, v in auto_reply_cooldown.items() if now - v > 60]
                    for k in to_del: del auto_reply_cooldown[k]
                safe_chat_send(response)
                try: gs('dingSmall').play()
                except: pass
                return True
    except Exception as e:
        print(f"Auto-Reply error: {e}")
    return False


def check_filter(msg):
    if not filter_enabled: return False
    try:
        sender = None; content = msg
        if ': ' in msg:
            parts = msg.split(': ', 1)
            sender = parts[0].strip(); content = parts[1].strip()

        if sender and my_own_name and sender == my_own_name:
            return False

        words = get_filter_words()
        if not words:
            return False

        content_lower = content.lower()
        for word in words:
            if word and word in content_lower:
                reply = get_filter_reply()
                cd_key = f"filter_{sender or 'unknown'}"
                current_time = time.time()
                last_time = filter_cooldown.get(cd_key, 0)
                if current_time - last_time < 2.0:
                    continue
                filter_cooldown[cd_key] = current_time
                if len(filter_cooldown) > 50:
                    now = time.time()
                    to_del = [k for k, v in filter_cooldown.items() if now - v > 60]
                    for k in to_del: del filter_cooldown[k]
                safe_chat_send(reply)
                try: gs('dingSmall').play()
                except: pass
                return True
    except Exception as e:
        print(f"Filter error: {e}")
    return False


INVISIBLE_CHARS = ['', '\u200b', '\u200c', '\u200d', '\u2060', '\u180e', '\ufeff', '\u200e', '\u200f', '\u2061']


def spam_send():
    global spam_active, spam_message, spam_delay, spam_timer, spam_counter
    if not spam_active: return
    try:
        suffix = INVISIBLE_CHARS[spam_counter % len(INVISIBLE_CHARS)]
        spam_counter += 1
        if spam_counter >= 100: spam_counter = 0
        safe_chat_send(spam_message + suffix)
        spam_timer = teck(spam_delay, spam_send)
    except:
        spam_active = False


def start_spam(message, delay=2.0):
    global spam_active, spam_message, spam_delay, spam_counter
    if spam_active: return
    spam_active = True
    spam_message = message
    spam_delay = float(delay)
    spam_counter = 0
    save_spam_settings(message, delay)
    spam_send()
    push(f"Spam Started: {message}", color=(0, 1, 0))


def stop_spam():
    global spam_active, spam_timer
    if spam_timer:
        try: spam_timer.cancel()
        except: pass
        spam_timer = None
    spam_active = False
    push("Spam Stopped", color=(1, 0.5, 0))


class Calculator:
    def __init__(s, source):
        s.w = AR.cw(source=source, size=(260, 350), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(235, 320))
        tw(parent=s.w, text='Math Engine', scale=0.8, position=(130, 315), h_align='center', color=(1, 0.5, 0.9))
        s.display = tw(parent=s.w, text='0', scale=1.0, position=(130, 275), h_align='center', color=(0.3, 1, 0.7), maxwidth=230)
        s.expression = tw(parent=s.w, text='', scale=0.45, position=(130, 255), h_align='center', color=(0.9, 0.7, 1), maxwidth=230)
        s.current_input = '0'
        s.previous_input = ''
        s.operation = None
        s.reset_next_input = False
        s.last_expression = ''
        bw(parent=s.w, label='Copy', size=(110, 22), position=(15, 225), on_activate_call=Call(s.copy_result), color=(0.4, 0.3, 0.7), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        bw(parent=s.w, label='Send', size=(110, 22), position=(135, 225), on_activate_call=Call(s.send_to_chat), color=(0.7, 0.4, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        row_y = 195
        row_gap = 27
        btn_h = 22
        rows = [
            [('AC', s.clear_all, (15, row_y), (35, btn_h), (0.7, 0.2, 0.3)), ('+/-', s.toggle_sign, (55, row_y), (35, btn_h), (0.3, 0.4, 0.7)), ('%', s.percentage, (95, row_y), (35, btn_h), (0.3, 0.4, 0.7)), ('R', s.square_root, (135, row_y), (35, btn_h), (0.3, 0.4, 0.7)), ('x2', s.square, (175, row_y), (35, btn_h), (0.3, 0.4, 0.7)), ('÷', lambda: s.set_operation('/'), (215, row_y), (30, btn_h), (0.8, 0.6, 0.1))],
            [('7', lambda: s.append_number('7'), (15, row_y-row_gap), (35, btn_h), (0.25, 0.3, 0.45)), ('8', lambda: s.append_number('8'), (55, row_y-row_gap), (35, btn_h), (0.25, 0.3, 0.45)), ('9', lambda: s.append_number('9'), (95, row_y-row_gap), (35, btn_h), (0.25, 0.3, 0.45)), ('×', lambda: s.set_operation('*'), (135, row_y-row_gap), (35, btn_h), (0.8, 0.6, 0.1)), ('DEL', s.backspace, (175, row_y-row_gap), (35, btn_h), (0.6, 0.15, 0.25)), ('1/x', s.reciprocal, (215, row_y-row_gap), (30, btn_h), (0.3, 0.4, 0.7))],
            [('4', lambda: s.append_number('4'), (15, row_y-row_gap*2), (35, btn_h), (0.25, 0.3, 0.45)), ('5', lambda: s.append_number('5'), (55, row_y-row_gap*2), (35, btn_h), (0.25, 0.3, 0.45)), ('6', lambda: s.append_number('6'), (95, row_y-row_gap*2), (35, btn_h), (0.25, 0.3, 0.45)), ('-', lambda: s.set_operation('-'), (135, row_y-row_gap*2), (35, btn_h), (0.8, 0.6, 0.1)), ('n!', s.factorial, (175, row_y-row_gap*2), (35, btn_h), (0.3, 0.4, 0.7)), ('log', s.logarithm, (215, row_y-row_gap*2), (30, btn_h), (0.3, 0.4, 0.7))],
            [('1', lambda: s.append_number('1'), (15, row_y-row_gap*3), (35, btn_h), (0.25, 0.3, 0.45)), ('2', lambda: s.append_number('2'), (55, row_y-row_gap*3), (35, btn_h), (0.25, 0.3, 0.45)), ('3', lambda: s.append_number('3'), (95, row_y-row_gap*3), (35, btn_h), (0.25, 0.3, 0.45)), ('+', lambda: s.set_operation('+'), (135, row_y-row_gap*3), (35, btn_h), (0.8, 0.6, 0.1)), ('^', s.power, (175, row_y-row_gap*3), (35, btn_h), (0.3, 0.4, 0.7)), ('pi', s.pi_value, (215, row_y-row_gap*3), (30, btn_h), (0.5, 0.3, 0.7))],
            [('0', lambda: s.append_number('0'), (15, row_y-row_gap*4), (75, btn_h), (0.25, 0.3, 0.45)), ('.', s.add_decimal, (95, row_y-row_gap*4), (35, btn_h), (0.25, 0.3, 0.45)), ('=', s.calculate, (135, row_y-row_gap*4), (35, btn_h), (0.15, 0.65, 0.35)), ('e', s.e_value, (175, row_y-row_gap*4), (35, btn_h), (0.5, 0.3, 0.7)), ('!', s.factorial, (215, row_y-row_gap*4), (30, btn_h), (0.3, 0.4, 0.7))],
        ]
        for row in rows:
            for label, callback, pos, size, color in row:
                bw(parent=s.w, label=label, size=size, position=pos, on_activate_call=callback, color=color, textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        AR.swish()

    def append_number(s, number):
        if s.reset_next_input:
            s.current_input = '0'; s.reset_next_input = False
        current = s.current_input
        s.current_input = number if current == '0' else current + number
        s.update_display(); gs('click01').play()
    def add_decimal(s):
        if s.reset_next_input:
            s.current_input = '0'; s.reset_next_input = False
        current = s.current_input
        if '.' not in current:
            s.current_input = current + '.'; s.update_display(); gs('click01').play()
    def backspace(s):
        current = s.current_input
        if current != '0' and len(current) > 1: current = current[:-1]
        else: current = '0'
        s.current_input = current; s.update_display(); gs('swish').play()
    def update_display(s):
        try:
            if s.display.exists(): tw(s.display, text=s.current_input)
        except: pass
    def set_operation(s, op):
        if s.operation and not s.reset_next_input: s.calculate()
        s.previous_input = s.current_input; s.operation = op; s.reset_next_input = True
        op_symbol = {'+': '+', '-': '-', '*': '×', '/': '÷', '**': '^'}.get(op, op)
        try:
            if s.expression.exists(): tw(s.expression, text=f"{s.current_input} {op_symbol}")
        except: pass
        gs('click01').play()
    def calculate(s):
        try:
            if not s.operation or s.reset_next_input: return
            num1 = float(s.previous_input); num2 = float(s.current_input)
            op_symbol = {'+': '+', '-': '-', '*': '×', '/': '÷', '**': '^'}.get(s.operation, s.operation)
            s.last_expression = f"{s.previous_input} {op_symbol} {s.current_input}"
            if s.operation == '+': result = num1 + num2
            elif s.operation == '-': result = num1 - num2
            elif s.operation == '*': result = num1 * num2
            elif s.operation == '/':
                if num2 == 0: raise ZeroDivisionError
                result = num1 / num2
            elif s.operation == '**': result = num1 ** num2
            else: return
            result_str = str(int(result)) if result == int(result) else str(round(result, 10))
            s.current_input = result_str; s.last_expression += f" = {result_str}"
            try:
                if s.expression.exists(): tw(s.expression, text=s.last_expression)
            except: pass
            s.operation = None; s.reset_next_input = True; s.update_display(); gs('dingSmallHigh').play()
        except: s.current_input = 'Error'; s.update_display(); gs('error').play(); teck(2.0, s.clear_all)
    def clear_all(s):
        s.current_input = '0'; s.previous_input = ''; s.operation = None; s.reset_next_input = False; s.last_expression = ''
        s.update_display()
        try:
            if s.expression.exists(): tw(s.expression, text='')
        except: pass
        gs('swish').play()
    def toggle_sign(s):
        if s.current_input != '0':
            if s.current_input.startswith('-'): s.current_input = s.current_input[1:]
            else: s.current_input = '-' + s.current_input
            s.update_display(); gs('click01').play()
    def percentage(s):
        try: s.current_input = str(float(s.current_input) / 100); s.update_display(); gs('dingSmall').play()
        except: s.current_input = '0'; s.update_display()
    def square(s):
        try:
            v = float(s.current_input); result = v ** 2
            s.current_input = str(int(result)) if result == int(result) else str(round(result, 10))
            s.update_display(); gs('dingSmall').play()
        except: AR.err('Error!')
    def square_root(s):
        try:
            v = float(s.current_input)
            if v < 0: raise ValueError
            result = math.sqrt(v)
            s.current_input = str(int(result)) if result == int(result) else str(round(result, 10))
            s.update_display(); gs('dingSmall').play()
        except: AR.err('Error!')
    def reciprocal(s):
        try:
            v = float(s.current_input)
            if v == 0: raise ZeroDivisionError
            result = 1 / v
            s.current_input = str(int(result)) if result == int(result) else str(round(result, 10))
            s.update_display(); gs('dingSmall').play()
        except: AR.err('Error!')
    def factorial(s):
        try:
            v = int(float(s.current_input))
            if v < 0 or v > 170: raise ValueError
            result = math.factorial(v); s.current_input = str(result)
            s.update_display(); gs('dingSmall').play()
        except: AR.err('Error!')
    def logarithm(s):
        try:
            v = float(s.current_input)
            if v <= 0: raise ValueError
            result = math.log10(v); s.current_input = str(round(result, 6))
            s.update_display(); gs('dingSmall').play()
        except: AR.err('Error!')
    def power(s): s.set_operation('**')
    def pi_value(s):
        s.current_input = str(round(math.pi, 10)); s.reset_next_input = True
        s.update_display(); gs('dingSmall').play()
    def e_value(s):
        s.current_input = str(round(math.e, 10)); s.reset_next_input = True
        s.update_display(); gs('dingSmall').play()
    def copy_result(s):
        try:
            if CIS():
                from babase import clipboard_set_text
                text = s.last_expression if s.last_expression else s.current_input
                clipboard_set_text(text); bui.screenmessage(f'Copied: {text}', color=(0, 1, 0)); gs('dingSmall').play()
            else: AR.err('Clipboard not supported!')
        except Exception as e: AR.err(f'Copy error: {str(e)}')
    def send_to_chat(s):
        try:
            message = f"{s.last_expression}" if s.last_expression else f"{s.current_input}"
            safe_chat_send(message); bui.screenmessage(f'Sent: {message}', color=(0, 1, 0)); gs('dingSmall').play()
        except Exception as e: AR.err(f'Send error: {str(e)}')


class EditReactionWindow:
    def __init__(s, source, trigger_code, parent_window=None):
        s.trigger_code = trigger_code
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(260, 200), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(230, 165))
        current = get_reactions().get(trigger_code, '')
        current_cd = get_cooldowns().get(trigger_code, DEFAULT_COOLDOWN)
        tw(parent=s.w, text=f'Edit "%{trigger_code}"', scale=0.75, position=(130, 160), h_align='center', color=(1, 1, 0))
        tw(parent=s.w, text='Reply with:', scale=0.5, position=(130, 140), h_align='center', color=(0.8, 0.8, 1))
        s.input = tw(parent=s.w, text=current, editable=True, scale=0.8, position=(25, 105), size=(210, 28), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Cooldown (sec):', scale=0.5, position=(130, 80), h_align='center', color=(0.8, 0.8, 1))
        s.cd_input = tw(parent=s.w, text=str(current_cd), editable=True, scale=0.8, position=(25, 50), size=(210, 28), h_align='center', color=(0.9, 0.9, 0.9))
        bw(parent=s.w, label='Save', size=(110, 28), position=(75, 10), on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        gs('swish').play()
    def save(s):
        value = tw(query=s.input).strip().lower()
        current_reactions = get_reactions()
        current_cooldowns = get_cooldowns()
        if value:
            current_reactions[s.trigger_code] = value
        else:
            if s.trigger_code in current_reactions: del current_reactions[s.trigger_code]
            if s.trigger_code in current_cooldowns: del current_cooldowns[s.trigger_code]
            save_reactions(current_reactions); save_cooldowns(current_cooldowns)
            bui.screenmessage(f'%{s.trigger_code} disabled', color=(1, 0.5, 0))
            gs('dingSmallHigh').play()
            if s.parent_window:
                try: s.parent_window.build_grid()
                except: pass
            AR.swish(s.w); return
        try: cd_value = float(tw(query=s.cd_input).strip())
        except: cd_value = DEFAULT_COOLDOWN
        if cd_value < 0: cd_value = 0
        current_reactions[s.trigger_code] = value
        current_cooldowns[s.trigger_code] = cd_value
        save_reactions(current_reactions); save_cooldowns(current_cooldowns)
        bui.screenmessage(f'%{s.trigger_code} -> {value}', color=(0, 1, 0))
        gs('dingSmallHigh').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class AddReactionWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(260, 240), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(230, 205))
        tw(parent=s.w, text='Add New', scale=0.8, position=(130, 200), h_align='center', color=(1, 1, 0))
        tw(parent=s.w, text='When %:', scale=0.5, position=(130, 172), h_align='center', color=(1, 1, 1))
        s.trigger_input = tw(parent=s.w, text='', editable=True, scale=0.8, position=(25, 142), size=(210, 28), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Reply:', scale=0.5, position=(130, 115), h_align='center', color=(1, 1, 1))
        s.response_input = tw(parent=s.w, text='', editable=True, scale=0.8, position=(25, 85), size=(210, 28), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Cooldown (sec):', scale=0.5, position=(130, 58), h_align='center', color=(1, 1, 1))
        s.cd_input = tw(parent=s.w, text=str(DEFAULT_COOLDOWN), editable=True, scale=0.8, position=(25, 28), size=(210, 28), h_align='center', color=(0.9, 0.9, 0.9))
        bw(parent=s.w, label='Add', size=(120, 30), position=(70, -5), on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        gs('swish').play()
    def save(s):
        trigger = tw(query=s.trigger_input).strip().lower()
        response = tw(query=s.response_input).strip().lower()
        if not trigger or not response:
            AR.err('Both required!'); return
        try: cd_value = float(tw(query=s.cd_input).strip())
        except: cd_value = DEFAULT_COOLDOWN
        if cd_value < 0: cd_value = 0
        current_reactions = get_reactions()
        current_cooldowns = get_cooldowns()
        current_reactions[trigger] = response
        current_cooldowns[trigger] = cd_value
        save_reactions(current_reactions); save_cooldowns(current_cooldowns)
        bui.screenmessage(f'%{trigger} -> {response}', color=(0, 1, 0))
        gs('dingSmallHigh').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class ReactionEditorWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(300, 380), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(270, 345))
        tw(parent=s.w, text='Auto React', scale=0.9, position=(150, 340), h_align='center', color=(0, 1, 1))
        s.id_text = tw(parent=s.w, text=f'cid={my_own_client_id or "?"} num={my_own_display_num if my_own_display_num is not None else "?"}', position=(150, 308), scale=0.35, h_align='center', color=(0, 1, 1))
        s.scroll = sw(parent=s.w, size=(260, 160), position=(20, 145))
        s.container = cw(parent=s.scroll, size=(240, 300), background=False)
        s.item_buttons = {}
        s.build_grid()
        bw(parent=s.w, label='+ Add', size=(75, 26), position=(20, 108), on_activate_call=Call(s.add_new), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.55)
        bw(parent=s.w, label='Reset', size=(75, 26), position=(105, 108), on_activate_call=Call(s.reset_all), color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.55)
        bw(parent=s.w, label='IDs', size=(75, 26), position=(190, 108), on_activate_call=Call(s.refresh_ids), color=(0.4, 0.3, 0.7), textcolor=(1, 1, 1), button_type='square', text_scale=0.55)
        s.toggle_btn = bw(parent=s.w, label='ON' if auto_react_enabled else 'OFF', size=(260, 28), position=(20, 72), on_activate_call=Call(s.toggle), color=(0.2, 0.7, 0.2) if auto_react_enabled else (0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        gs('swish').play()
    def build_grid(s):
        current_reactions = get_reactions()
        current_cooldowns = get_cooldowns()
        for child in s.container.get_children():
            try: child.delete()
            except Exception: pass
        s.item_buttons.clear()
        items = list(current_reactions.items())
        row_height = 30
        total_h = len(items) * row_height + 20
        for i, (trigger, response) in enumerate(items):
            y = total_h - (i + 1) * row_height
            cd = current_cooldowns.get(trigger, DEFAULT_COOLDOWN)
            btn = bw(parent=s.container, label=f'%{trigger} -> {response} ({cd}s)', size=(165, 24), position=(5, y), on_activate_call=Call(s.edit_item, trigger), color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1), button_type='square', text_scale=0.45)
            s.item_buttons[trigger] = btn
            bw(parent=s.container, label='X', size=(25, 24), position=(175, y), on_activate_call=Call(s.delete_item, trigger), color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        cw(s.container, size=(240, total_h))
    def refresh_ids(s):
        cid, num = get_my_ids()
        display_num = num if num is not None else "?"
        tw(s.id_text, text=f'cid={cid or "?"} num={display_num}', color=(0, 1, 0))
        bui.screenmessage(f'cid={cid}, num={display_num}', color=(0, 1, 0))
        gs('dingSmallHigh').play()
    def add_new(s): AddReactionWindow(s.w, parent_window=s)
    def edit_item(s, trigger): EditReactionWindow(s.w, trigger_code=trigger, parent_window=s)
    def delete_item(s, trigger):
        current_reactions = get_reactions()
        current_cooldowns = get_cooldowns()
        if trigger in current_reactions: del current_reactions[trigger]
        if trigger in current_cooldowns: del current_cooldowns[trigger]
        save_reactions(current_reactions); save_cooldowns(current_cooldowns)
        # Re-read persisted config; deleted defaults must not be reinserted.
        s.build_grid()
        bui.screenmessage(f'Deleted: %{trigger}', color=(1, 0.5, 0)); gs('dingSmallLow').play()
    def reset_all(s):
        save_reactions(dict(DEFAULT_REACTIONS))
        save_cooldowns(dict(DEFAULT_COOLDOWNS))
        bui.screenmessage('Reset!', color=(0, 1, 1)); gs('dingSmallHigh').play()
        s.build_grid()
    def toggle(s):
        global auto_react_enabled
        auto_react_enabled = not auto_react_enabled
        save_enabled_state('react', auto_react_enabled)
        if auto_react_enabled:
            bw(s.toggle_btn, label='ON', color=(0.2, 0.7, 0.2)); bui.screenmessage('React ON', color=(0, 1, 0))
        else:
            bw(s.toggle_btn, label='OFF', color=(0.7, 0.2, 0.2)); bui.screenmessage('React OFF', color=(1, 0.5, 0))
        gs('dingSmall').play()


class EditAutoReplyWindow:
    def __init__(s, source, keyword, parent_window=None):
        s.keyword = keyword; s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(260, 180), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(230, 145))
        current = get_auto_replies().get(keyword, '')
        tw(parent=s.w, text=f'Edit "{keyword}"', scale=0.75, position=(130, 140), h_align='center', color=(1, 1, 0))
        tw(parent=s.w, text='Reply:', scale=0.5, position=(130, 118), h_align='center', color=(0.8, 0.8, 1))
        s.input = tw(parent=s.w, text=current, editable=True, scale=0.8, position=(25, 82), size=(210, 28), h_align='center', color=(0.9, 0.9, 0.9))
        bw(parent=s.w, label='Save', size=(80, 28), position=(35, 30), on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        bw(parent=s.w, label='Delete', size=(80, 28), position=(145, 30), on_activate_call=Call(s.delete), color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        gs('swish').play()
    def save(s):
        value = tw(query=s.input).strip()
        if not value: AR.err('Required!'); return
        current = get_auto_replies()
        current[s.keyword] = value
        save_auto_replies(current)
        bui.screenmessage(f'Saved!', color=(0, 1, 0)); gs('dingSmallHigh').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)
    def delete(s):
        current = get_auto_replies()
        if s.keyword in current: del current[s.keyword]
        save_auto_replies(current)
        bui.screenmessage(f'Deleted!', color=(1, 0.5, 0)); gs('dingSmallLow').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class AddAutoReplyWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(260, 210), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(230, 175))
        tw(parent=s.w, text='Add Auto Reply', scale=0.8, position=(130, 170), h_align='center', color=(1, 1, 0))
        tw(parent=s.w, text='When contains:', scale=0.5, position=(130, 142), h_align='center', color=(1, 1, 1))
        s.keyword_input = tw(parent=s.w, text='', editable=True, scale=0.8, position=(25, 112), size=(210, 28), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Reply:', scale=0.5, position=(130, 85), h_align='center', color=(1, 1, 1))
        s.response_input = tw(parent=s.w, text='', editable=True, scale=0.8, position=(25, 55), size=(210, 28), h_align='center', color=(0.9, 0.9, 0.9))
        bw(parent=s.w, label='Add', size=(120, 30), position=(70, 10), on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        gs('swish').play()
    def save(s):
        keyword = tw(query=s.keyword_input).strip()
        response = tw(query=s.response_input).strip()
        if not keyword or not response: AR.err('Both required!'); return
        current = get_auto_replies()
        current[keyword] = response
        save_auto_replies(current)
        bui.screenmessage(f'Saved!', color=(0, 1, 0)); gs('dingSmallHigh').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class AutoReplyEditorWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(300, 380), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(270, 345))
        tw(parent=s.w, text='Auto Reply', scale=0.9, position=(150, 340), h_align='center', color=(0, 1, 1))
        s.scroll = sw(parent=s.w, size=(260, 160), position=(20, 145))
        s.container = cw(parent=s.scroll, size=(240, 300), background=False)
        s.item_buttons = {}
        s.build_grid()
        bw(parent=s.w, label='+ Add', size=(75, 26), position=(20, 108), on_activate_call=Call(s.add_new), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.55)
        bw(parent=s.w, label='Clear', size=(75, 26), position=(105, 108), on_activate_call=Call(s.clear_all), color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.55)
        s.toggle_btn = bw(parent=s.w, label='ON' if auto_reply_enabled else 'OFF', size=(75, 26), position=(190, 108), on_activate_call=Call(s.toggle), color=(0.2, 0.7, 0.2) if auto_reply_enabled else (0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        gs('swish').play()
    def build_grid(s):
        current = get_auto_replies()
        for child in s.container.get_children(): child.delete()
        s.item_buttons.clear()
        items = list(current.items())
        row_height = 30
        total_h = len(items) * row_height + 20
        for i, (keyword, response) in enumerate(items):
            y = total_h - (i + 1) * row_height
            btn = bw(parent=s.container, label=f'{keyword} -> {response}', size=(165, 24), position=(5, y), on_activate_call=Call(s.edit_item, keyword), color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1), button_type='square', text_scale=0.45)
            s.item_buttons[keyword] = btn
            bw(parent=s.container, label='X', size=(25, 24), position=(175, y), on_activate_call=Call(s.delete_item, keyword), color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        cw(s.container, size=(240, total_h))
    def add_new(s): AddAutoReplyWindow(s.w, parent_window=s)
    def edit_item(s, keyword): EditAutoReplyWindow(s.w, keyword=keyword, parent_window=s)
    def delete_item(s, keyword):
        current = get_auto_replies()
        if keyword in current: del current[keyword]
        save_auto_replies(current)
        bui.screenmessage(f'Deleted!', color=(1, 0.5, 0)); gs('dingSmallLow').play()
        s.build_grid()
    def clear_all(s):
        save_auto_replies({})
        bui.screenmessage('Cleared!', color=(1, 0.5, 0)); gs('dingSmallLow').play()
        s.build_grid()
    def toggle(s):
        global auto_reply_enabled
        auto_reply_enabled = not auto_reply_enabled
        save_enabled_state('reply', auto_reply_enabled)
        if auto_reply_enabled:
            bw(s.toggle_btn, label='ON', color=(0.2, 0.7, 0.2)); bui.screenmessage('Reply ON', color=(0, 1, 0))
        else:
            bw(s.toggle_btn, label='OFF', color=(0.7, 0.2, 0.2)); bui.screenmessage('Reply OFF', color=(1, 0.5, 0))
        gs('dingSmall').play()


class SpamWindow:
    def __init__(s, source):
        saved_msg, saved_delay = get_spam_settings()
        s.w = AR.cw(source=source, size=(280, 250), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(255, 215))
        tw(parent=s.w, text='Spam', scale=0.9, position=(140, 210), h_align='center', color=(1, 0.5, 0.5))
        s.status = tw(parent=s.w, text='Not Spamming', position=(140, 175), h_align='center', scale=0.6, color=(1, 1, 0))
        tw(parent=s.w, text='Message:', scale=0.5, position=(140, 155), h_align='center', color=(1, 1, 1))
        s.msg_input = tw(parent=s.w, text=saved_msg, editable=True, scale=0.8, position=(25, 125), size=(230, 28), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Delay (seconds):', scale=0.5, position=(140, 100), h_align='center', color=(1, 1, 1))
        s.delay_input = tw(parent=s.w, text=str(saved_delay), editable=True, scale=0.8, position=(25, 70), size=(230, 28), h_align='center', color=(0.9, 0.9, 0.9))
        s.toggle_btn = bw(parent=s.w, label='START', size=(110, 28), position=(20, 35), on_activate_call=Call(s.start), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        bw(parent=s.w, label='STOP', size=(110, 28), position=(150, 35), on_activate_call=Call(s.stop), color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        gs('swish').play()
    def start(s):
        if spam_active: AR.err('Already!'); return
        msg = tw(query=s.msg_input).strip()
        if not msg: AR.err('Enter message!'); return
        try:
            delay = float(tw(query=s.delay_input).strip())
            if delay <= 0: raise ValueError
        except: AR.err('Invalid delay!'); return
        start_spam(msg, delay)
        tw(s.status, text=f'Spamming: {msg}', color=(0, 1, 0))
        bw(s.toggle_btn, label='ON', color=(0.2, 0.7, 0.2))
    def stop(s):
        stop_spam(); tw(s.status, text='Stopped', color=(1, 1, 0))
        bw(s.toggle_btn, label='START', color=(0.2, 0.7, 0.3))


class ReconnectWindow:
    def __init__(s, source):
        global server_ip, server_port
        server_ip, server_port = get_saved_server()

        s.w = AR.cw(source=source, size=(300, 270), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(270, 235))
        tw(parent=s.w, text='Server Manager', scale=0.9, position=(150, 230), h_align='center', color=(0, 1, 1))

        s.ip_text = tw(parent=s.w, text=f'IP: {server_ip}', position=(150, 195), h_align='center', scale=0.5, color=(0.8, 0.8, 1))
        s.port_text = tw(parent=s.w, text=f'Port: {server_port}', position=(150, 178), h_align='center', scale=0.5, color=(0.8, 0.8, 1))

        s.auto_btn = bw(parent=s.w, label='Auto Reconnect: ' + ('ON' if auto_reconnect_enabled else 'OFF'), size=(260, 32), position=(20, 138), on_activate_call=Call(s.toggle_auto), color=(0.2, 0.7, 0.2) if auto_reconnect_enabled else (0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.75)
        tw(parent=s.w, text='Auto rejoin if disconnected', position=(150, 118), scale=0.35, h_align='center', color=(0.7, 0.7, 1))

        tw(parent=s.w, text='Manual Connect:', scale=0.5, position=(150, 95), h_align='center', color=(1, 1, 1))
        s.ip_input = tw(parent=s.w, text=server_ip, editable=True, scale=0.7, position=(25, 68), size=(115, 24), h_align='center', color=(0.9, 0.9, 0.9))
        s.port_input = tw(parent=s.w, text=str(server_port), editable=True, scale=0.7, position=(160, 68), size=(115, 24), h_align='center', color=(0.9, 0.9, 0.9))

        bw(parent=s.w, label='Connect', size=(120, 28), position=(90, 30), on_activate_call=Call(s.manual_connect), color=(0.3, 0.5, 0.8), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        bw(parent=s.w, label='Disconnect', size=(120, 28), position=(90, -3), on_activate_call=Call(s.disconnect), color=(0.7, 0.3, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)

        s.status = tw(parent=s.w, text='Ready', position=(150, 158), h_align='center', scale=0.45, color=(0.8, 0.8, 1))

        gs('swish').play()

    def disconnect(s):
        try:
            conn = get_connection_info()
            if conn:
                original_disconnect()
                bui.screenmessage('Disconnected', color=(1, 0.5, 0))
                tw(s.status, text='Disconnected', color=(1, 0.5, 0))
            else:
                AR.err('Not connected!')
        except Exception as e:
            AR.err(f'Failed: {e}')

    def manual_connect(s):
        global server_ip, server_port
        try:
            ip = tw(query=s.ip_input).strip()
            port = int(tw(query=s.port_input).strip())
            server_ip = ip
            server_port = port
            save_server(ip, port)
            tw(s.ip_text, text=f'IP: {server_ip}')
            tw(s.port_text, text=f'Port: {server_port}')

            conn = get_connection_info()
            if conn:
                try: original_disconnect()
                except: pass
                tw(s.status, text='Disconnecting...', color=(1, 1, 0))

                def do_connect(attempt=0):
                    if attempt > 60:
                        tw(s.status, text='Failed', color=(1, 0, 0))
                        return
                    try:
                        foreground = bascenev1.get_foreground_host_session()
                        if isinstance(foreground, MainMenuSession):
                            original_connect_to_party(ip, port)
                            bui.screenmessage(f'Connected to {ip}:{port}', color=(0, 1, 0))
                            tw(s.status, text='Connected', color=(0, 1, 0))
                        else:
                            teck(0.15, lambda: do_connect(attempt + 1))
                    except Exception as e:
                        teck(0.2, lambda: do_connect(attempt + 1))

                teck(0.2, do_connect)
            else:
                original_connect_to_party(ip, port)
                bui.screenmessage(f'Connected to {ip}:{port}', color=(0, 1, 0))
                tw(s.status, text='Connected', color=(0, 1, 0))
        except Exception as e:
            AR.err(f'Failed: {e}')

    def toggle_auto(s):
        if auto_reconnect_enabled:
            stop_auto_reconnect()
            bw(s.auto_btn, label='Auto Reconnect: OFF', color=(0.7, 0.2, 0.2))
        else:
            start_auto_reconnect()
            bw(s.auto_btn, label='Auto Reconnect: ON', color=(0.2, 0.7, 0.2))


class AutoBuyerWindow:
    def __init__(s, source):
        s.w = AR.cw(source=source, size=(340, 360), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(310, 325))
        tw(parent=s.w, text='Auto Buyer', scale=0.95, position=(170, 320), h_align='center', color=(0, 1, 1))
        status = "ON" if auto_buyer_enabled else "OFF"
        status_color = (0, 1, 0) if auto_buyer_enabled else (1, 0, 0)
        s.status_text = tw(parent=s.w, text=f'Status: {status}', position=(170, 290), h_align='center', scale=0.7, color=status_color)
        s.toggle_btn = bw(parent=s.w, label='Turn OFF' if auto_buyer_enabled else 'Turn ON', size=(120, 26), position=(20, 258), on_activate_call=Call(s.toggle), color=(0.7, 0.2, 0.2) if auto_buyer_enabled else (0.2, 0.7, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.65)
        bw(parent=s.w, label='Reset', size=(120, 26), position=(160, 258), on_activate_call=Call(s.reset_all), color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        tw(parent=s.w, text='Item Limits', position=(170, 232), h_align='center', scale=0.5, color=(1, 1, 0.8))
        s.scroll = sw(parent=s.w, size=(300, 180), position=(20, 40))
        s.container = cw(parent=s.scroll, size=(280, 700), background=False)
        s.item_buttons = {}
        s.build_grid()
        gs('swish').play()
    def build_grid(s):
        current_limits = get_limits()
        for child in s.container.get_children(): child.delete()
        s.item_buttons.clear()
        items = list(current_limits.items())
        col_width = 140
        row_height = 30
        num_rows = (len(items) + 1) // 2
        total_h = num_rows * row_height + 60
        for i, (name, limit) in enumerate(items):
            col = i % 2
            row = i // 2
            x = 5 + col * col_width
            y = total_h - (row + 1) * row_height
            limit_str = str(int(limit)) if limit == int(limit) else f"{limit:.2f}".rstrip('0').rstrip('.')
            btn = bw(parent=s.container, label=f'{name}: {limit_str}', size=(130, 26), position=(x, y), on_activate_call=Call(s.edit_item, name), color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1), button_type='square', text_scale=0.5)
            s.item_buttons[name] = btn
        cw(s.container, size=(280, total_h))
    def refresh_list(s):
        current_limits = get_limits()
        for name, btn in s.item_buttons.items():
            try:
                if btn and btn.exists():
                    limit = current_limits.get(name, 0)
                    limit_str = str(int(limit)) if limit == int(limit) else f"{limit:.2f}".rstrip('.')
                    bw(btn, label=f'{name}: {limit_str}')
            except: pass
    def toggle(s):
        global auto_buyer_enabled
        auto_buyer_enabled = not auto_buyer_enabled
        save_enabled_state('buyer', auto_buyer_enabled)
        if auto_buyer_enabled:
            bw(s.toggle_btn, label='Turn OFF', color=(0.7, 0.2, 0.2))
            tw(s.status_text, text='Status: ON', color=(0, 1, 0))
            bui.screenmessage('Auto Buyer ON', color=(0, 1, 0))
        else:
            bw(s.toggle_btn, label='Turn ON', color=(0.2, 0.7, 0.2))
            tw(s.status_text, text='Status: OFF', color=(1, 0, 0))
            bui.screenmessage('Auto Buyer OFF', color=(1, 0.5, 0))
        gs('dingSmall').play()
    def edit_item(s, name):
        EditLimitsWindow(s.w, item_name=name, parent_window=s)
    def reset_all(s):
        global _limits_cache
        save_limits(dict(DEFAULT_LIMITS))
        _limits_cache = None
        bui.screenmessage('Reset!', color=(0, 1, 1)); gs('dingSmallHigh').play()
        s.build_grid()


class EditLimitsWindow:
    def __init__(s, source, item_name, parent_window=None):
        s.item_name = item_name; s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(260, 150), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(230, 115))
        current = str(get_limits().get(item_name, 0))
        tw(parent=s.w, text=f'Set _ {item_name}', scale=0.8, position=(130, 110), h_align='center', color=(1, 1, 0))
        s.input = tw(parent=s.w, text=current, editable=True, scale=0.9, position=(35, 70), size=(190, 28), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='(decimal allowed)', position=(130, 48), scale=0.4, h_align='center', color=(0.7, 0.7, 1))
        bw(parent=s.w, label='Save', size=(100, 28), position=(80, 12), on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        gs('swish').play()
    def save(s):
        global _limits_cache
        try: value = float(tw(query=s.input).strip())
        except: AR.err('Invalid!'); return
        current_limits = get_limits()
        current_limits[s.item_name] = value
        save_limits(current_limits)
        _limits_cache = None
        bui.screenmessage(f'Saved!', color=(0, 1, 0)); gs('dingSmallHigh').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class FilterWindow:
    def __init__(s, source):
        s.w = AR.cw(source=source, size=(340, 280), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(310, 245))

        tw(parent=s.w, text='Word Filter', scale=1.0, position=(170, 240),
           h_align='center', color=(0, 1, 1))

        s.status_text = tw(parent=s.w, text='Filter: ON' if filter_enabled else 'Filter: OFF',
                           scale=0.6, position=(170, 218),
                           h_align='center',
                           color=(0, 1, 0) if filter_enabled else (1, 0.5, 0))

        tw(parent=s.w, text='Banned Words:', scale=0.55, position=(170, 195),
           h_align='center', color=(1, 1, 1))

        s.scroll = sw(parent=s.w, size=(300, 140), position=(20, 40))
        s.container = cw(parent=s.scroll, size=(280, 400), background=False)
        s.item_buttons = []
        s.build_grid()

        bw(parent=s.w, label='+ Add', size=(90, 28), position=(20, 5),
           on_activate_call=s.add_word,
           color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)

        bw(parent=s.w, label='Clear All', size=(90, 28), position=(125, 5),
           on_activate_call=s.clear_all,
           color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)

        s.toggle_btn = bw(parent=s.w, label='ON' if filter_enabled else 'OFF', size=(90, 28), position=(230, 5),
                          on_activate_call=s.toggle,
                          color=(0.2, 0.7, 0.2) if filter_enabled else (0.7, 0.2, 0.2),
                          textcolor=(1, 1, 1), button_type='square', text_scale=0.75)

        gs('swish').play()

    def build_grid(s):
        for child in s.container.get_children(): child.delete()
        s.item_buttons.clear()

        words = get_filter_words()
        row_height = 30
        total_h = len(words) * row_height + 20

        if not words:
            tw(parent=s.container, text='No banned words',
               position=(140, 60), scale=0.7, color=(1, 0.5, 0),
               h_align='center')
        else:
            for i, word in enumerate(words):
                y = total_h - (i + 1) * row_height
                tw(parent=s.container, text=f'{i+1}. {word}',
                   position=(10, y), scale=0.6, color=(1, 1, 1),
                   maxwidth=220, h_align='left')
                bw(parent=s.container, label='X', size=(28, 24), position=(240, y),
                   on_activate_call=lambda w=word: s.delete_word(w),
                   color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1),
                   button_type='square', text_scale=0.6)

        cw(s.container, size=(280, max(60, total_h)))

    def add_word(s):
        def _save():
            w = tw(query=word_input).strip().lower()
            if not w:
                AR.err('Enter a word!')
                return
            words = get_filter_words()
            if w in words:
                AR.err('Word already exists!')
                return
            words.append(w)
            save_filter_words(words)
            bui.screenmessage(f'Added: {w}', color=(0, 1, 0))
            gs('dingSmallHigh').play()
            AR.swish(win)
            s.build_grid()

        win = AR.cw(source=s.w, size=(300, 160), ps=AR.UIS() * 0.3)
        AR.add_close_button(win, position=(270, 125))
        tw(parent=win, text='New Banned Word:', scale=0.7, position=(150, 120),
           h_align='center', color=(1, 1, 1))
        word_input = tw(parent=win, text='', editable=True, scale=0.85,
                        position=(30, 75), size=(240, 30),
                        h_align='center', color=(0.9, 0.9, 0.9))
        bw(parent=win, label='Save', size=(100, 30), position=(100, 20),
           on_activate_call=_save,
           color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)

    def delete_word(s, word):
        words = get_filter_words()
        if word in words:
            words.remove(word)
            save_filter_words(words)
            bui.screenmessage(f'Removed: {word}', color=(1, 0.5, 0))
            gs('dingSmallLow').play()
            s.build_grid()

    def clear_all(s):
        save_filter_words([])
        bui.screenmessage('Cleared!', color=(1, 0.5, 0))
        gs('dingSmallLow').play()
        s.build_grid()

    def toggle(s):
        global filter_enabled
        filter_enabled = not filter_enabled
        save_enabled_state('filter', filter_enabled)
        if filter_enabled:
            bw(s.toggle_btn, label='ON', color=(0.2, 0.7, 0.2))
            tw(s.status_text, text='Filter: ON', color=(0, 1, 0))
        else:
            bw(s.toggle_btn, label='OFF', color=(0.7, 0.2, 0.2))
            tw(s.status_text, text='Filter: OFF', color=(1, 0.5, 0))
        gs('dingSmall').play()


class EditPlaceWindow:
    def __init__(s, source, mods_button):
        s.mods_button = mods_button
        s.step = 10

        try:
            pos = mods_button.get_position()
            s.current_x, s.current_y = float(pos[0]), float(pos[1])
        except:
            s.current_x, s.current_y = 0.0, 0.0

        s.parent_w, s.parent_h = 1920.0, 1080.0
        try:
            parent = mods_button.get_parent()
            if parent:
                psize = parent.get_size()
                s.parent_w, s.parent_h = float(psize[0]), float(psize[1])
        except:
            pass

        s.w = AR.cw(source=source, size=(340, 320), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(310, 285))

        tw(parent=s.w, text='Edit Button Place', scale=0.95, position=(170, 280),
           h_align='center', color=(0, 1, 1))

        s.pos_text = tw(parent=s.w, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}',
                        position=(170, 235), h_align='center', scale=0.7,
                        color=(1, 1, 0))

        tw(parent=s.w, text=f'Step: {s.step}px',
           position=(170, 215), h_align='center', scale=0.45,
           color=(0.7, 0.7, 1))

        arrow_size = (55, 45)
        arrow_color = (0.3, 0.5, 0.8)
        cx = 170

        bw(parent=s.w, label='^', size=arrow_size,
           position=(cx - 27, 155),
           on_activate_call=s.move_up,
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.2)

        bw(parent=s.w, label='<', size=arrow_size,
           position=(cx - 110, 100),
           on_activate_call=s.move_left,
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.2)

        bw(parent=s.w, label='>', size=arrow_size,
           position=(cx + 55, 100),
           on_activate_call=s.move_right,
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.2)

        bw(parent=s.w, label='v', size=arrow_size,
           position=(cx - 27, 45),
           on_activate_call=s.move_down,
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.2)

        bw(parent=s.w, label='Reset to Default', size=(200, 32),
           position=(70, 5),
           on_activate_call=s.reset,
           color=(0.7, 0.3, 0.2),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.7)

        gs('swish').play()

    def move_up(s):
        s.current_y += s.step
        s.apply_position()

    def move_down(s):
        s.current_y -= s.step
        s.apply_position()

    def move_left(s):
        s.current_x -= s.step
        s.apply_position()

    def move_right(s):
        s.current_x += s.step
        s.apply_position()

    def apply_position(s):
        try:
            max_x = max(0, s.parent_w - 90)
            max_y = max(0, s.parent_h - 35)
            if s.current_x < 0: s.current_x = 0
            if s.current_y < 0: s.current_y = 0
            if s.current_x > max_x: s.current_x = max_x
            if s.current_y > max_y: s.current_y = max_y

            bw(s.mods_button, position=(s.current_x, s.current_y))
            tw(s.pos_text, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}')
            save_mods_button_position(s.current_x, s.current_y)
            gs('click01').play()
        except Exception as e:
            print(f"Move error: {e}")

    def reset(s):
        try:
            default_x = s.parent_w - 110
            default_y = s.parent_h - 155
        except:
            default_x, default_y = 0, 0

        # Restore a visible default position and persist it for the next launch.
        default_x = max(0, min(float(default_x), max(0.0, s.parent_w - 90.0)))
        default_y = max(0, min(float(default_y), max(0.0, s.parent_h - 35.0)))
        s.current_x, s.current_y = float(default_x), float(default_y)
        try:
            if not s.mods_button or not s.mods_button.exists():
                bui.screenmessage('Reopen the Party window to restore Mods.', color=(1, 0.6, 0))
                return
        except Exception:
            pass
        s.apply_position()

        bui.screenmessage('Mods position restored!', color=(0, 1, 1))
        gs('dingSmallHigh').play()


class _RankingTableParser(HTMLParser):
    """Extract rows from the RankingReset page without depending on its styling."""
    def __init__(self):
        super().__init__()
        self.rows = []
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == 'tr':
            self._row = []
        elif tag in ('td', 'th') and self._row is not None:
            self._cell = []

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ('td', 'th') and self._cell is not None:
            value = ' '.join(''.join(self._cell).split())
            self._row.append(value)
            self._cell = None
        elif tag == 'tr' and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


class RankingWindow:
    URL = 'https://bslife.ir/index.php?post=RankingReset'

    def __init__(s, source):
        s.w = AR.cw(source=source, size=(390, 570), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(360, 535))

        tw(parent=s.w, text='SERVER RANKING', scale=0.95,
           position=(195, 530), h_align='center', color=(0.35, 0.9, 1))
        tw(parent=s.w, text='BSLIFE  •  RESET SCHEDULE',
           scale=0.45, position=(195, 506), h_align='center',
           color=(0.65, 0.75, 0.9))

        s.status = tw(parent=s.w, text='Connecting to BSLIFE...',
                      scale=0.55, position=(195, 480),
                      h_align='center', color=(1, 0.82, 0.35))

        s.scroll = sw(parent=s.w, size=(350, 410), position=(20, 55))
        s.container = cw(parent=s.scroll, size=(330, 100), background=False)

        s.rows = []
        s.mode = 'list'
        s.selected = None
        s.countdown_text = None
        s.countdown_timer_running = False
        s.countdown_token = 0

        s.back_btn = bw(
            parent=s.w, label='BACK', size=(105, 28), position=(25, 12),
            on_activate_call=Call(s.show_list),
            color=(0.25, 0.32, 0.45), textcolor=(1, 1, 1),
            button_type='square', text_scale=0.62
        )
        s.refresh_btn = bw(
            parent=s.w, label='REFRESH', size=(105, 28), position=(260, 12),
            on_activate_call=Call(s.refresh),
            color=(0.12, 0.52, 0.58), textcolor=(1, 1, 1),
            button_type='square', text_scale=0.62
        )
        bw(
            parent=s.w, label='CLOSE', size=(105, 28), position=(142, 12),
            on_activate_call=Call(AR.swish, t=s.w),
            color=(0.45, 0.22, 0.28), textcolor=(1, 1, 1),
            button_type='square', text_scale=0.62
        )

        s._update_footer_buttons()
        s.refresh()
        gs('swish').play()

    def _update_footer_buttons(s):
        try:
            bw(s.back_btn, color=(0.25, 0.32, 0.45) if s.mode == 'detail'
               else (0.18, 0.25, 0.34))
            bw(s.refresh_btn, label='REFRESH',
               color=(0.12, 0.52, 0.58))
        except Exception:
            pass

    def _clear_content(s):
        try:
            for child in s.container.get_children():
                child.delete()
        except Exception:
            pass

    def refresh(s):
        s.mode = 'list'
        s.selected = None
        s._update_footer_buttons()
        tw(s.status, text='Connecting to BSLIFE...', color=(1, 0.82, 0.35))
        s._clear_content()
        tw(parent=s.container, text='Loading server schedule...',
           position=(165, 45), scale=0.58, h_align='center',
           color=(0.8, 0.87, 1))
        cw(s.container, size=(330, 100))

        def fetch():
            try:
                request = urllib.request.Request(
                    s.URL,
                    headers={'User-Agent': 'Mozilla/5.0 (compatible; BSLifeRanking/1.0)'}
                )
                with urllib.request.urlopen(request, timeout=15) as response:
                    html = response.read().decode('utf-8', errors='replace')

                parser = _RankingTableParser()
                parser.feed(html)
                rows = []
                for row in parser.rows:
                    if len(row) < 3:
                        continue
                    name, reset_time, reset_date = row[0], row[1], row[2]
                    if name.lower() in ('نام سرور', 'server name'):
                        continue
                    if not name.strip():
                        continue
                    rows.append((name.strip(), reset_time.strip(), reset_date.strip()))

                if not rows:
                    raise ValueError('No server schedule rows were found.')

                pushcall(lambda: s.show_rows(rows), from_other_thread=True)
            except Exception as exc:
                error = str(exc)
                pushcall(lambda: s.show_error(error), from_other_thread=True)

        threading.Thread(
            target=fetch, name='BSLifeRankingFetch', daemon=True
        ).start()

    def show_error(s, error):
        try:
            if not s.w.exists():
                return
            s.mode = 'list'
            s._clear_content()
            cw(s.container, size=(330, 280))
            tw(s.status, text='Unable to load server schedule',
               color=(1, 0.38, 0.38))
            cw(parent=s.container, size=(310, 135), position=(10, 120),
               color=(0.18, 0.12, 0.17))
            tw(parent=s.container, text='CONNECTION FAILED',
               position=(165, 205), scale=0.72, h_align='center',
               color=(1, 0.55, 0.55))
            tw(parent=s.container,
               text='Check your internet connection\nand press REFRESH.',
               position=(165, 165), scale=0.53, h_align='center',
               color=(0.85, 0.85, 0.9))
            print('RankingReset error: ' + error)
        except Exception:
            pass

    def show_rows(s, rows):
        try:
            if not s.w.exists():
                return
            s.rows = rows
            s.show_list()
            tw(s.status, text=f'{len(rows)} SERVERS  •  LIVE DATA',
               color=(0.35, 1, 0.68))
            gs('dingSmall').play()
        except Exception as exc:
            s.show_error(str(exc))

    def _days_remaining_label(s, reset_date, reset_time):
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', reset_date)
        if not match:
            return 'OPEN SERVER DETAILS'
        try:
            target_day = datetime.date(*map(int, match.groups()))
            days = (target_day - datetime.date.today()).days
            if days < 0:
                return 'Passed'
            if days == 0:
                return 'Today'
            if days == 1:
                return '1 Day'
            return f'{days} Days'
        except Exception:
            return 'OPEN SERVER DETAILS'

    def show_list(s):
        if not s.w.exists():
            return
        s.mode = 'list'
        s.selected = None
        s.countdown_timer_running = False
        s.countdown_token += 1
        s._update_footer_buttons()
        s._clear_content()

        if not s.rows:
            tw(parent=s.container, text='No server data available.',
               position=(165, 45), scale=0.58, h_align='center',
               color=(0.85, 0.85, 0.9))
            cw(s.container, size=(330, 100))
            return

        # Clean server cards: only show the server and days remaining.
        row_h = 68
        total_h = max(110, len(s.rows) * row_h + 12)
        palette = [
            (0.10, 0.27, 0.34),
            (0.17, 0.23, 0.38),
            (0.12, 0.31, 0.27),
            (0.29, 0.20, 0.34),
        ]
        for i, row in enumerate(s.rows):
            name, reset_time, reset_date = row
            y = total_h - (i + 1) * row_h
            remaining_label = s._days_remaining_label(reset_date, reset_time)
            bw(
                parent=s.container,
                label=f'{name}\n{remaining_label}',
                size=(316, 60), position=(7, y),
                on_activate_call=Call(s.show_detail, i),
                color=palette[i % len(palette)],
                textcolor=(0.94, 0.97, 1),
                button_type='square', text_scale=0.68
            )
        cw(s.container, size=(330, total_h))
        tw(s.status, text=f'{len(s.rows)} SERVERS  •  SELECT A SERVER',
           color=(0.35, 1, 0.68))

    def show_detail(s, index):
        if not s.w.exists() or index < 0 or index >= len(s.rows):
            return
        s.mode = 'detail'
        s.selected = s.rows[index]
        s._update_footer_buttons()
        s._clear_content()
        cw(s.container, size=(330, 390))

        name, reset_time, reset_date = s.selected
        cw(parent=s.container, size=(310, 330), position=(10, 35),
           color=(0.09, 0.16, 0.25))
        tw(parent=s.container, text='SERVER DETAILS',
           position=(165, 335), scale=0.55, h_align='center',
           color=(0.35, 0.92, 1))
        tw(parent=s.container, text=name,
           position=(165, 285), scale=0.88, h_align='center',
           color=(0.95, 0.96, 1), maxwidth=285)
        tw(parent=s.container, text='RANKING RESET',
           position=(165, 240), scale=0.48, h_align='center',
           color=(0.65, 0.75, 0.9))
        tw(parent=s.container, text='RESET DATE',
           position=(165, 195), scale=0.43, h_align='center',
           color=(0.6, 0.75, 0.9))
        tw(parent=s.container, text=reset_date,
           position=(165, 170), scale=0.72, h_align='center',
           color=(1, 0.78, 0.34))
        tw(parent=s.container, text='SCHEDULED TIME',
           position=(165, 125), scale=0.43, h_align='center',
           color=(0.6, 0.75, 0.9))
        tw(parent=s.container, text=reset_time,
           position=(165, 100), scale=0.65, h_align='center',
           color=(0.9, 0.94, 1), maxwidth=285)
        s.countdown_text = tw(
            parent=s.container, text='Calculating countdown...',
            position=(165, 55), scale=0.58, h_align='center',
            color=(0.35, 1, 0.68), maxwidth=290
        )
        tw(s.status, text='SELECTED SERVER',
           color=(0.35, 1, 0.68))
        s.countdown_token += 1
        s.countdown_timer_running = True
        s.update_countdown(s.countdown_token)

    def update_countdown(s, token=None):
        if token is None:
            token = s.countdown_token
        if (not s.countdown_timer_running or s.mode != 'detail'
                or token != s.countdown_token):
            return
        try:
            if not s.w.exists() or s.selected is None:
                s.countdown_timer_running = False
                return

            _name, reset_time, reset_date = s.selected
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', reset_date)
            if not date_match:
                tw(s.countdown_text,
                   text='Countdown unavailable\nDate format not recognized.',
                   color=(1, 0.65, 0.45))
                teck(5.0, Call(s.update_countdown, token))
                return

            year, month, day = map(int, date_match.groups())
            reset_day = datetime.date(year, month, day)
            now = datetime.datetime.now()
            time_match = re.search(r'(\d{1,2}):(\d{2})', reset_time)

            if time_match:
                hour, minute = map(int, time_match.groups())
                target = datetime.datetime.combine(
                    reset_day, datetime.time(hour, minute)
                )
                remaining = int((target - now).total_seconds())
                if remaining <= 0:
                    message = 'RESET TIME HAS ARRIVED'
                    color = (1, 0.55, 0.4)
                else:
                    days, rem = divmod(remaining, 86400)
                    hours, rem = divmod(rem, 3600)
                    minutes, seconds = divmod(rem, 60)
                    message = f'{days}d  {hours:02d}h  {minutes:02d}m  {seconds:02d}s'
                    color = (0.35, 1, 0.68)
                tw(s.countdown_text, text='TIME LEFT\n' + message,
                   color=color)
            else:
                # The site provides a date but no exact clock time for these rows.
                days_left = (reset_day - now.date()).days
                if days_left > 0:
                    target = datetime.datetime.combine(
                        reset_day, datetime.time(0, 0)
                    )
                    remaining = max(0, int((target - now).total_seconds()))
                    days, rem = divmod(remaining, 86400)
                    hours, rem = divmod(rem, 3600)
                    minutes, seconds = divmod(rem, 60)
                    message = (
                        f'{days}d  {hours:02d}h  {minutes:02d}m  {seconds:02d}s'
                        '\nExact reset hour not provided by BSLIFE'
                    )
                    color = (1, 0.82, 0.4)
                elif days_left == 0:
                    message = 'TODAY  •  EXACT HOUR NOT PROVIDED'
                    color = (1, 0.82, 0.4)
                else:
                    message = 'SCHEDULED DATE HAS PASSED'
                    color = (1, 0.55, 0.4)
                tw(s.countdown_text, text='DATE COUNTDOWN\n' + message,
                   color=color)

            teck(1.0, Call(s.update_countdown, token))
        except Exception as exc:
            try:
                tw(s.countdown_text, text=f'Countdown error: {exc}',
                   color=(1, 0.5, 0.4))
            except Exception:
                pass


class ModsMenu:
    def __init__(s, source):
        s.mods_button_ref = source
        s.w = AR.cw(source=source, size=(400, 620), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(370, 580))

        tw(parent=s.w, text='Mods Menu', scale=1.2, position=(200, 575), h_align='center', color=(0, 1, 1))

        s.scroll = sw(parent=s.w, size=(340, 520), position=(30, 25))

        buttons = [
            ('Calculator', Calculator, (0, 0.3, 0.8)),
            ('Auto Buyer', AutoBuyerWindow, (0.2, 0.6, 0.8)),
            ('Auto React', ReactionEditorWindow, (0.8, 0.5, 0.2)),
            ('Auto Reply', AutoReplyEditorWindow, (0.3, 0.7, 0.4)),
            ('Spam', SpamWindow, (0.8, 0.3, 0.3)),
            ('Reconnect', ReconnectWindow, (0.4, 0.6, 0.4)),
            ('Filter', FilterWindow, (0.7, 0.4, 0.9)),
            ('Radar', 'RADAR', (0.72, 0.06, 0.36)),
            ('File Manager', 'FILE_MANAGER', (0.48, 0.035, 0.25)),
            ('Translate', 'TRANSLATE', (0.72, 0.12, 0.42)),
            ('Ranking', RankingWindow, (0.12, 0.62, 0.55)),
            ('Edit Place', None, (0.6, 0.4, 0.7)),
        ]

        num_buttons = len(buttons)
        row_h = 65
        buttons_h = num_buttons * row_h

        top_padding = 380
        bottom_padding = 380

        total_h = top_padding + buttons_h + bottom_padding

        s.container = cw(parent=s.scroll, size=(320, total_h), background=False)

        s.item_buttons = []
        y_pos = total_h - top_padding - row_h

        for label, cls, color in buttons:
            btn = bw(
                parent=s.container,
                label=label,
                size=(300, 55),
                position=(10, y_pos),
                on_activate_call=lambda c=cls: s.open_window(c),
                color=color,
                textcolor=(1, 1, 1),
                button_type='square',
                text_scale=0.8
            )
            s.item_buttons.append(btn)
            y_pos -= row_h

        gs('swish').play()

    def open_window(s, cls):
        gs('swish').play()
        try:
            AR.swish(s.w)
            if cls == 'RADAR':
                teck(0.15, _open_radar)
            elif cls == 'FILE_MANAGER':
                teck(0.15, _open_file_manager)
            elif cls == 'TRANSLATE':
                teck(0.15, lambda: TranslateWindow(s.w))
            elif cls is None:
                if s.mods_button_ref is not None:
                    teck(0.15, lambda: EditPlaceWindow(s.w, s.mods_button_ref))
                else:
                    bui.screenmessage('Mods button not found!', color=(1, 0, 0))
            else:
                teck(0.15, lambda: cls(s.w))
        except Exception as e:
            print(f"Open window error: {e}")


SELL_PATTERN = re.compile(r'Sell ID:\s*(\w+)')
BUY_PATTERN = re.compile(r'(\w+):\s*Buy\s*<\s*([\d,]+)\s+(\w+)\s*\([^)]+\)\s*>\s*for\s*([\d,]+)\s*coins(?:\?.*)?')
FAST_BUY_MAX_TOTAL = 100000
_fast_buy_last_message = ''
_fast_buy_last_count = 0
_fast_buy_seen_messages = set()
_fast_buy_initialized = False
_fast_buy_pending_code = None
_fast_buy_listing_allowed = False
_fast_buy_seen_ids = set()


def process_sell(item_id):
    if item_id in processed_sell_ids:
        return
    processed_sell_ids.add(item_id)
    if len(processed_sell_ids) > 150:
        processed_sell_ids.clear()
    safe_chat_send('b ' + str(item_id))


def process_buy(item_id, count, item_name, total_price):
    """Validate the server's final buy prompt and answer immediately."""
    current_limits = _get_cached_limits()
    allowed = False
    try:
        if count > 0 and total_price <= FAST_BUY_MAX_TOTAL:
            allowed = total_price / float(count) <= float(current_limits.get(item_name, -1))
    except Exception:
        allowed = False
    safe_chat_send('1 ' if allowed else '0 ')


def _fast_buy_listing_is_allowed(message):
    """Use the fastBuy_V2 listing price check, with current editable limits."""
    try:
        if '💰Sell <' not in message:
            return False
        body = message.split('💰Sell <', 1)[1].replace(',', '')
        parts = body.split()
        count = int(parts[0])
        item_name = parts[1].lower()
        # The source fast-buy format puts the total amount at token 4.
        total = int(parts[4][:-1])
        limits = _get_cached_limits()
        return (count > 0 and total <= FAST_BUY_MAX_TOTAL and
                total / float(count) <= float(limits.get(item_name, -1)))
    except Exception:
        # Fallback for the alternate server line format already handled by the mod.
        try:
            match = re.search(r'💰Sell\s*<\s*([\d,]+)\s+(\w+).*?>\s*for\s*([\d,]+)\s*coins', message)
            if not match:
                return False
            count = int(match.group(1).replace(',', ''))
            item_name = match.group(2).lower()
            total = int(match.group(3).replace(',', ''))
            return (count > 0 and total <= FAST_BUY_MAX_TOTAL and
                    total / float(count) <= float(_get_cached_limits().get(item_name, -1)))
        except Exception:
            return False


def _fast_buy_handle_message(message):
    global _fast_buy_pending_code, _fast_buy_listing_allowed
    if not isinstance(message, str) or 'Server' not in message:
        return
    if '💰Sell <' in message:
        _fast_buy_listing_allowed = _fast_buy_listing_is_allowed(message)
        return
    if '💰Sell ID: ' in message and _fast_buy_listing_allowed:
        item_id = message.split('💰Sell ID: ', 1)[1].strip().split()[0]
        if item_id not in _fast_buy_seen_ids:
            _fast_buy_seen_ids.add(item_id)
            if len(_fast_buy_seen_ids) > 150:
                _fast_buy_seen_ids.clear()
            _fast_buy_pending_code = item_id
            safe_chat_send('b ' + item_id)
        _fast_buy_listing_allowed = False
        return
    if '💳Buy < ' in message and _fast_buy_pending_code:
        try:
            # Same server response parsing/order used by fastBuy_V2_16.py.
            parts = message.split(': ')
            code = parts[1].strip()
            details = parts[2].replace(',', '')
            if code != _fast_buy_pending_code:
                return
            tokens = details.split()
            count = int(tokens[2])
            item_name = tokens[3].lower()
            total = int(tokens[7])
            process_buy(code, count, item_name, total)
            _fast_buy_pending_code = None
        except Exception as exc:
            print('Fast buyer parse error: %s' % exc)
            _fast_buy_pending_code = None


def _fast_buy_loop():
    global _fast_buy_last_message, _fast_buy_last_count, _fast_buy_seen_messages, _fast_buy_initialized
    try:
        if auto_buyer_enabled:
            messages = GCM() or []
            # Establish a baseline first so old chat history is never purchased on plugin load.
            if not _fast_buy_initialized:
                _fast_buy_seen_messages.update(str(m) for m in messages)
                _fast_buy_initialized = True
                _fast_buy_last_count = len(messages)
                return
            # Scan a recent tail in order; remember each processed line to avoid repeats.
            for message in messages[-12:]:
                fingerprint = str(message)
                if fingerprint in _fast_buy_seen_messages:
                    continue
                _fast_buy_seen_messages.add(fingerprint)
                _fast_buy_handle_message(fingerprint)
                _fast_buy_last_message = fingerprint
            if len(_fast_buy_seen_messages) > 500:
                _fast_buy_seen_messages.clear()
                _fast_buy_seen_messages.update(str(m) for m in messages[-30:])
            _fast_buy_last_count = len(messages)
    except Exception as exc:
        print('Fast buyer loop error: %s' % exc)
    finally:
        teck(0.15, _fast_buy_loop)


def check_reaction(msg):
    global my_own_client_id, my_own_display_num
    if not auto_react_enabled: return
    try:
        if my_own_client_id is None and my_own_display_num is None:
            get_my_ids()
        current_reactions = get_reactions()
        current_cooldowns = get_cooldowns()
        sender = None; content = msg
        if ': ' in msg:
            parts = msg.split(': ', 1)
            sender = parts[0].strip(); content = parts[1].strip()
        content_lower = content.lower()

        for trigger, response in current_reactions.items():
            trigger_lower = trigger.lower()
            esc_trigger = re.escape(trigger_lower)

            pattern = rf'(?:^|[\s/])%?\s*{esc_trigger}\s*%?\s*(\d+)'
            m = re.search(pattern, content_lower)
            if not m:
                continue

            try:
                target_num = int(m.group(1))
            except:
                continue

            is_target_me = False
            if my_own_client_id is not None and target_num == my_own_client_id:
                is_target_me = True
            elif my_own_display_num is not None and target_num == my_own_display_num:
                is_target_me = True

            if is_target_me:
                cd_time = current_cooldowns.get(trigger, DEFAULT_COOLDOWN)
                current_time = time.time()
                cd_key = f"{trigger_lower}_{sender or 'unknown'}"
                last_time = react_cooldown.get(cd_key, 0)
                if current_time - last_time < cd_time: break
                react_cooldown[cd_key] = current_time
                if len(react_cooldown) > 50:
                    now = time.time()
                    to_del = [k for k, v in react_cooldown.items() if now - v > 300]
                    for k in to_del: del react_cooldown[k]
                safe_chat_send(response)
                try: gs('dingSmall').play()
                except: pass
                break
    except Exception as e:
        print(f"React error: {e}")


CALC_PATTERN = re.compile(r'^(\d+(?:\.\d+)?)\s*([\+\-\*\/\^×÷xX])\s*(\d+(?:\.\d+)?)$')


def detect_calculation(message):
    expression = message.replace('×', '*').replace('÷', '/')
    expression = expression.replace('x', '*').replace('X', '*')
    match = CALC_PATTERN.match(expression.strip())
    if not match: return None
    num1 = float(match.group(1)); op = match.group(2); num2 = float(match.group(3))
    try:
        if op == '+': result = num1 + num2
        elif op == '-': result = num1 - num2
        elif op == '*': result = num1 * num2
        elif op == '/':
            if num2 == 0: return None
            result = num1 / num2
        elif op == '^': result = num1 ** num2
        else: return None
        result_str = str(int(result)) if result == int(result) else str(round(result, 10))
        op_display = {'+': '+', '-': '-', '*': '×', '/': '÷', '^': '^'}.get(op, op)
        return f"{match.group(1)} {op_display} {match.group(3)} = {result_str}"
    except: return None


def check_spam_command(msg):
    global spam_active
    try:
        content = msg
        if ': ' in msg:
            _, content = msg.split(': ', 1)
        content = content.strip()
        content_lower = content.lower()

        if content_lower in ('spam on',):
            start_spam(spam_message if spam_message else 'spam', spam_delay)
            return True

        if content_lower in ('spam off', 'stop spam'):
            stop_spam()
            return True

        match = re.match(r'^spam\s+(.+?)\s+([\d.]+)\s*$', content_lower)
        if match:
            message = match.group(1).strip()
            try: delay = float(match.group(2))
            except: return False
            if delay <= 0: delay = 2.0
            if spam_active: stop_spam()
            start_spam(message, delay); return True
    except Exception as e: print(f"Spam command error: {e}")
    return False


def auto_reconnect_check():
    global auto_reconnect_enabled, server_ip, server_port, auto_reconnect_busy

    if not auto_reconnect_enabled:
        return

    try:
        conn = get_connection_info()

        if not conn and server_ip and server_ip != "127.0.0.1" and not auto_reconnect_busy:
            auto_reconnect_busy = True
            push("Auto Reconnecting...", color=(1, 1, 0))

            def try_connect(attempt=0):
                global auto_reconnect_busy
                try:
                    if not auto_reconnect_enabled:
                        auto_reconnect_busy = False
                        return

                    if get_connection_info():
                        push("Reconnected!", color=(0, 1, 0))
                        auto_reconnect_busy = False
                        return

                    if attempt > 40:
                        auto_reconnect_busy = False
                        return

                    foreground = bascenev1.get_foreground_host_session()
                    if isinstance(foreground, MainMenuSession):
                        push(f"Connecting... (try {attempt+1})", color=(1, 1, 0))
                        try:
                            original_connect_to_party(server_ip, server_port)
                        except Exception as e:
                            print(f"Auto connect attempt {attempt} error: {e}")

                        teck(0.5, lambda: try_connect(attempt + 1))
                    else:
                        teck(0.3, lambda: try_connect(attempt))
                except Exception as e:
                    print(f"Auto reconnect error: {e}")
                    teck(0.5, lambda: try_connect(attempt + 1))

            try_connect()
    except Exception as e:
        print(f"Auto reconnect check error: {e}")


def start_auto_reconnect():
    global auto_reconnect_enabled, auto_reconnect_busy
    auto_reconnect_enabled = True
    auto_reconnect_busy = False
    push("Auto Reconnect: ON", color=(0, 1, 0))


def stop_auto_reconnect():
    global auto_reconnect_enabled, auto_reconnect_busy
    auto_reconnect_enabled = False
    auto_reconnect_busy = False
    push("Auto Reconnect: OFF", color=(1, 0.5, 0))


def _show_mahyar_credit():
    message = 'Create By Mahyar\nChannel Tel : @Horn_Ch'
    try:
        push(message, color=(1.0, 0.30, 0.72), top=True)
    except TypeError:
        try:
            push(message, color=(1.0, 0.30, 0.72))
        except Exception:
            pass
    except Exception:
        pass


# ba_meta require api 9
# ba_meta export babase.Plugin
class byMahyar(Plugin):
    def __init__(s):
        global my_own_name
        try: _install_translate_hook()
        except Exception as exc: print('Translate hook install error: %s' % exc)
        try: my_own_name = APP.plus.get_v1_account_name()
        except: my_own_name = None

        s.last_msg_hash = ""
        s.last_calc_hash = ""

        teck(0.5, s.ear)
        teck(0.5, s.calc_ear)
        teck(1, s.reconnect_ear)
        teck(2.0, _sb_check_enemy_roster)
        teck(0.15, _fast_buy_loop)
        teck(2.5, _show_mahyar_credit)

        from bauiv1lib import party
        o = party.PartyWindow.__init__

        def e(self, *a, **k):
            r = o(self, *a, **k)
            teck(0.5, get_my_ids)

            default_x = self._width - 110
            default_y = self._height - 155
            saved_x, saved_y = get_mods_button_position(default_x, default_y)

            try:
                saved_x = float(saved_x)
                saved_y = float(saved_y)
                # Ignore stale/off-screen coordinates left by older window sizes.
                if not (0 <= saved_x <= max(0, self._width - 90) and
                        0 <= saved_y <= max(0, self._height - 35)):
                    saved_x, saved_y = float(default_x), float(default_y)
            except:
                saved_x, saved_y = float(default_x), float(default_y)
            saved_x = min(max(0.0, saved_x), max(0.0, float(self._width) - 90.0))
            saved_y = min(max(0.0, saved_y), max(0.0, float(self._height) - 35.0))

            b_mods = AR.bw(
                position=(saved_x, saved_y),
                parent=self._root_widget,
                size=(85, 25),
                label='Mods',
                color=(0.3, 0.5, 0.8)
            )
            bw(b_mods, on_activate_call=lambda: s.delayed_open(ModsMenu, b_mods))

            # Re-apply after the PartyWindow has completed its layout. Some game UI
            # versions reset child positions during the first layout pass.
            def _restore_mods_button_position():
                try:
                    if b_mods.exists():
                        px, py = get_mods_button_position(default_x, default_y)
                        px = min(max(0.0, float(px)), max(0.0, float(self._width) - 90.0))
                        py = min(max(0.0, float(py)), max(0.0, float(self._height) - 35.0))
                        bw(b_mods, position=(px, py))
                except Exception as exc:
                    print('Mods position restore error: %s' % exc)
            teck(0.1, _restore_mods_button_position)

            return r

        party.PartyWindow.__init__ = e

    def ear(s):
        try:
            z = GCM()
            teck(0.15, s.ear)

            if not z:
                s.last_msg_hash = ""
                return

            current_count = len(z)
            last_msg = z[-1]
            current_hash = f"{current_count}_{len(last_msg)}_{last_msg}"

            if current_hash == s.last_msg_hash:
                return

            s.last_msg_hash = current_hash
            msg = last_msg

            try:
                if check_spam_command(msg): return
            except: pass
            try:
                if check_auto_reply(msg): return
            except: pass
            try:
                if check_filter(msg): return
            except: pass
            try:
                check_reaction(msg)
            except: pass

        except Exception as e:
            try:
                teck(0.15, s.ear)
            except:
                pass
            print(f"Error in ear: {e}")

    def calc_ear(s):
        try:
            z = GCM()
            teck(0.5, s.calc_ear)

            if not z:
                s.last_calc_hash = ""
                return

            current_count = len(z)
            last_msg = z[-1]
            current_hash = f"{current_count}_{len(last_msg)}_{last_msg}"

            if current_hash == s.last_calc_hash:
                return

            s.last_calc_hash = current_hash

            try:
                content = last_msg
                if ': ' in last_msg:
                    _, content = last_msg.split(': ', 1)
                content = content.strip()
                result = detect_calculation(content)
                if result:
                    safe_chat_send(result)
            except: pass
        except Exception as e:
            try:
                teck(0.5, s.calc_ear)
            except:
                pass
            print(f"Error in calc_ear: {e}")

    def reconnect_ear(s):
        try:
            teck(2.0, s.reconnect_ear)
            auto_reconnect_check()
        except Exception as e:
            try:
                teck(2.0, s.reconnect_ear)
            except:
                pass
            print(f"Error in reconnect_ear: {e}")

    def delayed_open(s, cls, btn):
        teck(0.05, lambda: cls(btn))

# ---------------------------------------------------------------------------
# MAHYAR PINK RADAR + FILE MANAGER (merged into the original test.py)
# ---------------------------------------------------------------------------
import os as _sb_os
import babase
import bascenev1 as bs

_SB_ACCENT = (1.0, 0.28, 0.68)
_SB_PANEL_BG = (0.055, 0.018, 0.060)
_SB_PANEL_INNER = (0.12, 0.035, 0.095)
_SB_TEXT = (1.0, 0.82, 0.93)


def _sb_config_get(key, default=None):
    try:
        value = babase.app.config.get(key, default)
        return value if value is not None else default
    except Exception:
        return default


def _sb_config_set(key, value):
    try:
        babase.app.config[key] = value
        babase.app.config.commit()
        return True
    except Exception:
        return False


def _sb_roster():
    """Read the online players and their raw server-provided roster fields."""
    try:
        raw = bs.get_game_roster() or []
    except Exception:
        raw = []
    result = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        players = [p for p in (entry.get("players") or []) if isinstance(p, dict)]
        if not players:
            continue
        cid = entry.get("client_id", entry.get("clientID", entry.get("clientid", -1)))
        try:
            cid = int(cid)
        except Exception:
            cid = -1
        names = []
        for player in players:
            name = (player.get("name_full") or player.get("nameFull") or
                    player.get("name") or player.get("name_full_raw"))
            if name:
                names.append(str(name))
        result.append({"client_id": cid, "name": names[0] if names else "Player",
                       "names": names, "account_id": entry.get("account_id", entry.get("accountID")),
                       "raw": entry})
    return result


class _SBPanel:
    def __init__(self, title, accent=_SB_ACCENT, width=980, height=680):
        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = width, height
        self._width = min(width, max(420, int(sw - 30)))
        self._height = min(height, max(440, int(sh - 30)))
        x = max(10, (sw - self._width) * 0.5)
        y = max(10, (sh - self._height) * 0.5)
        self._closed = False
        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"), position=(x, y),
            size=(self._width, self._height), transition="in_scale",
            scale=1.0, color=_SB_PANEL_BG)
        bui.textwidget(parent=self.root_widget,
                       position=(18, self._height - 62),
                       size=(self._width - 90, 42), text=title,
                       h_align="left", v_align="center", scale=1.15,
                       color=accent, shadow=1.0, flatness=0.2)
        bui.textwidget(parent=self.root_widget,
                       position=(18, self._height - 88),
                       size=(self._width - 36, 20),
                       text="",
                       h_align="left", v_align="center", scale=0.55,
                       color=(1.0, 0.42, 0.76))
        bw(parent=self.root_widget,
           position=(self._width - 58, self._height - 66), size=(38, 38),
           button_type="square", label="✕", text_scale=0.9,
           color=(0.62, 0.06, 0.30), textcolor=(1, 1, 1),
           on_activate_call=bui.WeakCall(self.close))

    def make_scroll(self, content_height):
        margin = 18
        sy = 54
        sh = self._height - 160
        sw = self._width - 2 * margin
        scroll = bui.scrollwidget(parent=self.root_widget,
                                  position=(margin, sy), size=(sw, sh),
                                  highlight=False, capture_arrows=True)
        content = bui.containerwidget(parent=scroll,
                                      size=(sw, max(sh, int(content_height))),
                                      background=False)
        return content, sw, max(sh, int(content_height))

    def close(self):
        self._closed = True
        try:
            bui.containerwidget(edit=self.root_widget, transition="out_scale")
        except Exception:
            try:
                bui.widget(edit=self.root_widget, delete=True)
            except Exception:
                pass



_SB_CONFIG_ENEMIES = "Mahyar Saved Enemies"
_sb_enemies = []
_sb_enemy_announced_this_session = set()


def _sb_load_enemies():
    global _sb_enemies
    # Migrate the previous internal setting name without showing old branding.
    raw = _sb_config_get(_SB_CONFIG_ENEMIES, None)
    if raw is None:
        raw = _sb_config_get("StudioBon Radar Enemies", [])
    cleaned = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                ident = str(item.get("id", "")).strip()[:100]
                label = str(item.get("name", "Player")).strip()[:60]
                if ident and not any(x.get("id", "").casefold() == ident.casefold() for x in cleaned):
                    cleaned.append({"id": ident, "name": label or "Player"})
    _sb_enemies = cleaned


def _sb_save_enemies():
    _sb_config_set(_SB_CONFIG_ENEMIES, _sb_enemies)


def _sb_person_device_id(person):
    """Read V2/device/account display identity from nested server roster data."""
    if not isinstance(person, dict):
        return None
    raw = person.get("raw", person)
    wanted = (
        "account_display_string", "account_display_name", "account_name",
        "device_name", "device_display_string", "device_display_name",
        "v2_name", "v2name", "v2_alias", "device_alias", "device",
        "device_id", "deviceid", "display_string", "account_id_string", "account_id", "accountid",
    )
    values = []
    def walk(obj, depth=0):
        if depth > 6:
            return
        if isinstance(obj, dict):
            for key in wanted:
                for actual_key, value in obj.items():
                    if str(actual_key).casefold() == key.casefold() and value is not None:
                        values.append((key, value))
            for value in obj.values():
                if isinstance(value, (dict, list, tuple)):
                    walk(value, depth + 1)
        elif isinstance(obj, (list, tuple)):
            for value in obj:
                if isinstance(value, (dict, list, tuple)):
                    walk(value, depth + 1)
    walk(raw)
    for key in wanted:
        value = person.get(key)
        if value is not None:
            values.append((key, value))
    visible_name = str(person.get("name", "")).strip().casefold()
    for key, value in values:
        try:
            ident = str(value).strip()
        except Exception:
            continue
        if not ident or ident.casefold() in ("none", "unknown", "player", "server"):
            continue
        if ident.casefold() == visible_name:
            continue
        # Short numeric roster IDs (e.g. 137) are not Device/V2 identities.
        if ident.isdigit() and len(ident) < 6:
            continue
        if re.search(r"(?i)(android|pc)\d{3,}|^[0-9a-f]{12,}$|^pb-[a-z0-9-]{6,}$", ident):
            return ident
        # Alias-like strings such as Ostokhon are accepted only from a device/account field.
        if key.casefold() not in ("account_id", "accountid") and len(ident) >= 4 and re.search(r"[A-Za-z]", ident):
            return ident
    return None


def _sb_person_stable_id(person):
    """Identity used by the enemy list: the server-provided device/V2 identity."""
    return _sb_person_device_id(person)


def _sb_add_enemy(person):
    try:
        ident = _sb_person_stable_id(person)
        if not ident:
            push("Device/V2 این بازیکن از اطلاعات سرور پیدا نشد؛ چیزی ذخیره نشد.", color=(1, 0.25, 0.25))
            return
        if any(str(item.get("id", "")).casefold() == ident.casefold() for item in _sb_enemies):
            push("این Device/V2 از قبل در لیست دشمنان است", color=(1, 0.4, 0.25))
            return
        player_name = str(person.get("name", "Player"))[:60] if isinstance(person, dict) else "Player"
        _sb_enemies.append({"id": ident, "name": player_name})
        _sb_save_enemies()
        push("Enemy saved", color=(1.0, 0.30, 0.72))
        _open_radar()
    except Exception as exc:
        try: push("Radar add error: %s" % str(exc)[:100], color=(1, 0.2, 0.2))
        except Exception: pass


def _sb_remove_enemy(ident):
    global _sb_enemies
    _sb_enemies = [item for item in _sb_enemies if item.get("id", "").casefold() != str(ident).casefold()]
    _sb_save_enemies()
    _open_enemy_list()


_enemy_list_window = None

def _open_enemy_list():
    global _enemy_list_window
    try:
        if _enemy_list_window is not None:
            _enemy_list_window.close()
        _enemy_list_window = _EnemyListWindow()
    except Exception as exc:
        try: push("Enemy list error: %s" % exc, color=(1, 0.3, 0.3))
        except Exception: pass


def _sb_enemy_match_key(enemy, roster_person):
    """Match a saved enemy by stable identity, with exact-name fallback."""
    saved_id = str(enemy.get("id", "")).strip().casefold()
    live_id = str(_sb_person_stable_id(roster_person) or "").strip().casefold()
    if saved_id and live_id and saved_id == live_id:
        return "id:" + saved_id
    saved_name = str(enemy.get("name", "")).strip().casefold()
    live_name = str(roster_person.get("name", "")).strip().casefold()
    if saved_name and live_name and saved_name == live_name:
        return "name:" + saved_name
    return None


def _sb_check_enemy_roster():
    """Show a local alert whenever a saved enemy appears in the current roster."""
    global _sb_enemy_announced_this_session
    try:
        roster = _sb_roster()
        present_now = set()
        for person in roster:
            for enemy in _sb_enemies:
                match_key = _sb_enemy_match_key(enemy, person)
                if not match_key:
                    continue
                present_now.add(match_key)
                if match_key not in _sb_enemy_announced_this_session:
                    _sb_enemy_announced_this_session.add(match_key)
                    enemy_name = str(person.get("name") or enemy.get("name") or "Player")
                    push("Enemy (%s) is here" % enemy_name,
                         color=(0.25, 1.0, 0.42), top=True)
                break
        # Clear departed enemies so a later rejoin triggers another alert.
        _sb_enemy_announced_this_session.intersection_update(present_now)
    except Exception as exc:
        print("Enemy roster check error: " + str(exc))
    try:
        teck(2.0, _sb_check_enemy_roster)
    except Exception:
        pass


_sb_load_enemies()


class _EnemyListWindow(_SBPanel):
    def __init__(self):
        # A larger, brighter custom panel with clear online status.
        super().__init__("ENEMYS", accent=(1.0, 0.38, 0.78), width=1120, height=820)
        try:
            bui.containerwidget(edit=self.root_widget, color=(0.13, 0.035, 0.15))
        except Exception:
            pass
        total = len(_sb_enemies)
        try:
            roster = _sb_roster()
        except Exception:
            roster = []
        online_by_enemy = {}
        for item in _sb_enemies:
            for person in roster:
                if _sb_enemy_match_key(item, person):
                    online_by_enemy[str(item.get("id", "")).casefold()] = str(
                        person.get("name") or item.get("name") or "Player")
                    break

        bui.textwidget(parent=self.root_widget,
            position=(24, self._height - 132), size=(self._width - 220, 38),
            text="SAVED ENEMIES  •  %d     |     ONLINE  •  %d" % (total, len(online_by_enemy)),
            h_align="left", v_align="center", scale=0.82,
            color=(1.0, 0.76, 0.92), shadow=0.8)
        bw(parent=self.root_widget, position=(self._width - 176, self._height - 136),
           size=(150, 42), button_type="square", label="REFRESH",
           text_scale=0.66, color=(0.82, 0.12, 0.49), textcolor=(1, 1, 1),
           on_activate_call=_open_enemy_list)

        margin = 22
        view_y = 58
        view_h = self._height - 212
        inner_w = self._width - 2 * margin
        scroll = bui.scrollwidget(parent=self.root_widget,
            position=(margin, view_y), size=(inner_w, view_h),
            highlight=False, capture_arrows=True)
        row_h = 94
        content_h = max(view_h, total * row_h + 20)
        content = bui.containerwidget(parent=scroll,
            size=(inner_w, content_h), background=False)
        if not _sb_enemies:
            bui.textwidget(parent=content, position=(12, content_h - 100),
                size=(inner_w - 24, 68), text="NO SAVED ENEMIES",
                h_align="center", v_align="center", scale=1.0,
                color=(1.0, 0.78, 0.93))
        for idx, item in enumerate(_sb_enemies):
            y = content_h - 86 - idx * row_h
            ident_key = str(item.get("id", "")).casefold()
            online_name = online_by_enemy.get(ident_key)
            card_color = (0.19, 0.12, 0.22) if idx % 2 == 0 else (0.23, 0.10, 0.22)
            bw(parent=content, position=(5, y - 2), size=(inner_w - 10, 82),
               button_type="square", label="", color=card_color, enable_sound=False)
            bui.textwidget(parent=content, position=(22, y + 43),
                size=(inner_w - 260, 30), text=str(item.get("name", "Player"))[:46],
                h_align="left", v_align="center", scale=0.82,
                color=(1.0, 0.82, 0.94))
            bui.textwidget(parent=content, position=(22, y + 15),
                size=(inner_w - 270, 24), text=str(item.get("id", ""))[:86],
                h_align="left", v_align="center", scale=0.57,
                color=(1.0, 0.52, 0.82))
            if online_name:
                bui.textwidget(parent=content, position=(inner_w - 250, y + 37),
                    size=(150, 28), text="IS HERE", h_align="center",
                    v_align="center", scale=0.78,
                    color=(0.25, 1.0, 0.42), shadow=1.0)
                bui.textwidget(parent=content, position=(inner_w - 250, y + 13),
                    size=(150, 20), text="ONLINE", h_align="center",
                    v_align="center", scale=0.52,
                    color=(0.55, 1.0, 0.65))
            else:
                bui.textwidget(parent=content, position=(inner_w - 250, y + 25),
                    size=(150, 26), text="OFFLINE", h_align="center",
                    v_align="center", scale=0.65,
                    color=(0.72, 0.65, 0.76))
            # Slightly larger action target for easier tapping.
            bw(parent=content, position=(inner_w - 112, y + 17), size=(94, 48),
               button_type="square", label="REMOVE", text_scale=0.58,
               color=(0.78, 0.10, 0.39), textcolor=(1, 1, 1),
               on_activate_call=lambda ident=item["id"]: _sb_remove_enemy(ident))


_radar_window = None


def _open_radar():
    global _radar_window
    try:
        if _radar_window is not None:
            _radar_window.close()
        _radar_window = _MahyarRadarWindow()
    except Exception as exc:
        try: push("Radar error: %s" % exc, color=(1, 0.3, 0.3))
        except Exception: pass


class _MahyarRadarWindow(_SBPanel):
    """Radar uses the same roster fields as the reference PlayerInfo manager."""
    def __init__(self):
        super().__init__("RADAR",
                         accent=(1.0, 0.30, 0.72), height=720)
        try: bui.containerwidget(edit=self.root_widget, color=(0.075, 0.018, 0.12))
        except Exception: pass
        # Dedicated Enemys section opens the user's saved enemy list.
        bw(parent=self.root_widget, position=(20, self._height - 116), size=(150, 42),
            button_type="square", label="ENEMYS", text_scale=0.72,
            color=(0.72, 0.045, 0.34), textcolor=(1, 1, 1),
            on_activate_call=_open_enemy_list)
        try:
            roster = _sb_roster()
        except Exception:
            roster = []
        bui.textwidget(parent=self.root_widget, position=(190, self._height - 112),
            size=(self._width - 212, 36), text="ONLINE PLAYERS  •  %d" % len(roster),
            h_align="left", v_align="center", scale=0.78, color=(1.0, 0.72, 0.88))
        margin = 18
        viewport_y = 54
        viewport_h = max(180, self._height - 178)
        inner_w = self._width - 2 * margin
        scroll = bui.scrollwidget(parent=self.root_widget, position=(margin, viewport_y),
            size=(inner_w, viewport_h), highlight=False, capture_arrows=True)
        content_h = max(viewport_h, len(roster) * 76 + 48)
        content = bui.containerwidget(parent=scroll, size=(inner_w, content_h), background=False)
        known = {item["id"].casefold() for item in _sb_enemies}
        headers = (("PLAYER NAME", 12), ("CLIENT ID", 270), ("DEVICE ID", 390))
        for title, x in headers:
            bui.textwidget(parent=content, position=(x, content_h - 28), size=(160, 22),
                text=title, h_align="left", v_align="center", scale=0.58,
                color=(1.0, 0.48, 0.80))
        for idx, person in enumerate(roster):
            y = content_h - 78 - idx * 76
            name = str(person.get("name", "Player"))
            cid = str(person.get("client_id", -1))
            ident = _sb_person_stable_id(person)
            is_enemy = bool(ident and ident.casefold() in known)
            bg = (0.24, 0.06, 0.10) if is_enemy else ((0.06, 0.12, 0.22) if idx % 2 == 0 else (0.035, 0.085, 0.17))
            bw(parent=content, position=(5, y), size=(inner_w - 10, 62),
                button_type="square", label="", color=bg, enable_sound=False)
            bui.textwidget(parent=content, position=(12, y + 16), size=(240, 36),
                text=name[:36], h_align="left", v_align="center", scale=0.7,
                color=(1.0, 0.35, 0.72) if is_enemy else (1, 1, 1))
            bui.textwidget(parent=content, position=(270, y + 16), size=(100, 36),
                text=cid, h_align="left", v_align="center", scale=0.65,
                color=(1.0, 0.72, 0.88))
            bui.textwidget(parent=content, position=(390, y + 16), size=(inner_w - 610, 36),
                text=ident or "ID unavailable", h_align="left", v_align="center",
                scale=0.62, color=(1.0, 0.35, 0.72) if is_enemy else (0.6, 1.0, 0.68))
            # Preserve the existing add-to-enemy action; no PlayerInfo management
            # controls such as Kick All are imported into this panel.
            bw(parent=content, position=(inner_w - 205, y + 13), size=(190, 36),
                button_type="square",
                label="ADDED" if is_enemy else "ADD ENEMY",
                text_scale=0.54, color=(0.32, 0.035, 0.20) if is_enemy else (0.62, 0.025, 0.06),
                textcolor=(1, 1, 1), on_activate_call=lambda p=person: _sb_add_enemy(p))
        if not roster:
            bui.textwidget(parent=content, position=(10, content_h - 90), size=(inner_w - 20, 60),
                text="No players online",
                h_align="center", v_align="center", scale=0.8, color=_SB_TEXT)
        bw(parent=self.root_widget, position=(20, 12), size=(self._width - 40, 34),
            button_type="square", label="REFRESH RADAR", text_scale=0.7,
            color=(0.025, 0.16, 0.48), textcolor=(1, 1, 1),
            on_activate_call=_open_radar)



_file_manager_window = None


def _open_file_manager():
    global _file_manager_window
    try:
        if _file_manager_window is not None:
            _file_manager_window.close()
        _file_manager_window = _MahyarFileManagerWindow()
    except Exception as exc:
        try:
            push("File Manager error: %s" % str(exc)[:100], color=(1, 0.3, 0.3))
        except Exception:
            pass


class _MahyarFileManagerWindow(_SBPanel):
    def __init__(self):
        super().__init__("FILE MANAGER", accent=(1.0, 0.30, 0.72),
                         width=760, height=560)
        try:
            bui.containerwidget(edit=self.root_widget, color=(0.065, 0.018, 0.095))
        except Exception:
            pass
        try:
            env = babase.env()
            self.mod_path = str(env.get("python_directory_user") or "")
        except Exception:
            self.mod_path = ""
        if not self.mod_path:
            self.mod_path = _sb_os.path.dirname(_sb_os.path.abspath(__file__))
        bui.textwidget(parent=self.root_widget,
            position=(18, self._height - 125), size=(self._width - 36, 24),
            text="INSTALLED MOD FILES  •  Tap a row's trash icon to remove a file",
            h_align="left", v_align="center", scale=0.58,
            color=(1.0, 0.72, 0.89))
        self._status = bui.textwidget(parent=self.root_widget,
            position=(18, 18), size=(self._width - 210, 26),
            text="Ready", h_align="left", v_align="center", scale=0.58,
            color=(1.0, 0.48, 0.80))
        bw(parent=self.root_widget, position=(self._width - 180, 14), size=(88, 32),
           button_type="square", label="↻ Refresh", text_scale=0.55,
           color=(0.68, 0.06, 0.34), textcolor=(1, 1, 1),
           on_activate_call=self.refresh_files)
        bw(parent=self.root_widget, position=(self._width - 88, 14), size=(70, 32),
           button_type="square", label="PYC", text_scale=0.58,
           color=(0.48, 0.035, 0.22), textcolor=(1, 1, 1),
           on_activate_call=self.confirm_delete_all_pyc)
        self._scroll = bui.scrollwidget(parent=self.root_widget,
            position=(16, 56), size=(self._width - 32, self._height - 194),
            highlight=False, capture_arrows=True)
        self._scroll_w = self._width - 32
        self._scroll_h = self._height - 194
        self._content = bui.containerwidget(parent=self._scroll,
            size=(self._scroll_w, self._scroll_h), background=False)
        self.refresh_files()

    def refresh_files(self):
        try:
            for child in self._content.get_children():
                child.delete()
        except Exception:
            pass
        try:
            files = []
            for name in _sb_os.listdir(self.mod_path):
                path = _sb_os.path.join(self.mod_path, name)
                if _sb_os.path.isfile(path):
                    files.append({"name": name, "path": path,
                                  "size": _sb_os.path.getsize(path)})
            files.sort(key=lambda item: item["name"].casefold())
            if not files:
                bui.textwidget(parent=self._content,
                    position=(12, self._scroll_h - 55),
                    size=(self._scroll_w - 24, 42), text="No files found in the mods folder",
                    h_align="center", v_align="center", scale=0.72,
                    color=(1.0, 0.78, 0.25))
                bui.textwidget(edit=self._status, text="0 files")
                return
            row_h = 34
            content_h = max(self._scroll_h, len(files) * row_h + 20)
            bui.containerwidget(edit=self._content, size=(self._scroll_w, content_h))
            for idx, item in enumerate(files):
                y = content_h - row_h - 8 - idx * row_h
                row_bg = (0.055, 0.12, 0.27) if idx % 2 == 0 else (0.04, 0.085, 0.21)
                bw(parent=self._content, position=(5, y - 2),
                   size=(self._scroll_w - 10, row_h - 2), button_type="square",
                   label="", color=row_bg, enable_sound=False)
                name = item["name"]
                if len(name) > 42:
                    name = name[:39] + "..."
                if item["name"].endswith(".py"):
                    file_color = (1.0, 0.48, 0.80)
                elif item["name"].endswith(".pyc"):
                    file_color = (1.0, 0.32, 0.68)
                elif item["name"].endswith(".json"):
                    file_color = (1.0, 0.68, 0.84)
                else:
                    file_color = (1.0, 0.85, 0.94)
                bui.textwidget(parent=self._content,
                    position=(14, y + 2), size=(self._scroll_w - 230, 24),
                    text=name, h_align="left", v_align="center", scale=0.59,
                    color=file_color)
                size = item["size"]
                size_text = ("%0.1f MB" % (size / 1048576.0) if size >= 1048576
                             else ("%0.1f KB" % (size / 1024.0) if size >= 1024
                                   else "%d B" % size))
                bui.textwidget(parent=self._content,
                    position=(self._scroll_w - 195, y + 2), size=(90, 24),
                    text=size_text, h_align="right", v_align="center", scale=0.52,
                    color=(1.0, 0.62, 0.84))
                bw(parent=self._content, position=(self._scroll_w - 88, y + 1),
                   size=(32, 25), button_type="square", label="🗑",
                   text_scale=0.55, color=(0.68, 0.035, 0.28),
                   textcolor=(1, 1, 1),
                   on_activate_call=lambda p=item["path"], n=item["name"]: self.confirm_delete_file(p, n))
            bui.textwidget(edit=self._status, text="%d files • mods folder" % len(files))
        except Exception as exc:
            try:
                bui.textwidget(parent=self._content,
                    position=(12, self._scroll_h - 55),
                    size=(self._scroll_w - 24, 42),
                    text="Error: " + str(exc)[:100],
                    h_align="center", v_align="center", scale=0.65,
                    color=(1.0, 0.5, 0.5))
                bui.textwidget(edit=self._status, text="Could not read mods folder")
            except Exception:
                pass

    def _confirm_window(self, title, confirm_label, callback):
        width, height = 360, 150
        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = 800, 600
        x, y = max(10, (sw - width) * 0.5), max(10, (sh - height) * 0.5)
        win = bui.containerwidget(parent=gsw("overlay_stack"),
            position=(x, y), size=(width, height), transition="in_scale",
            scale=1.0, color=(0.10, 0.018, 0.075))
        bui.textwidget(parent=win, position=(18, 82), size=(width - 36, 42),
            text=title, h_align="center", v_align="center", scale=0.68,
            color=(1.0, 0.68, 0.86))
        bw(parent=win, position=(width - 48, height - 48), size=(32, 32),
           button_type="square", label="✕", text_scale=0.7,
           color=(0.4, 0.08, 0.12), textcolor=(1, 1, 1),
           on_activate_call=lambda: bui.containerwidget(edit=win, transition="out_scale"))
        def confirmed():
            try:
                callback()
            finally:
                try: bui.containerwidget(edit=win, transition="out_scale")
                except Exception: pass
        bw(parent=win, position=(width / 2 - 65, 22), size=(130, 36),
           button_type="square", label=confirm_label, text_scale=0.65,
           color=(0.68, 0.035, 0.28), textcolor=(1, 1, 1),
           on_activate_call=confirmed)

    def confirm_delete_file(self, file_path, file_name):
        def delete():
            try:
                _sb_os.remove(file_path)
                push("Deleted: " + file_name, color=(0.35, 1.0, 0.55))
                self.refresh_files()
            except Exception as exc:
                push("Delete failed: " + str(exc)[:80], color=(1, 0.3, 0.3))
        self._confirm_window('Delete "%s"?' % file_name[:36], "🗑 DELETE", delete)

    def confirm_delete_all_pyc(self):
        def delete_all():
            deleted = 0
            try:
                for name in _sb_os.listdir(self.mod_path):
                    if name.endswith(".pyc"):
                        try:
                            _sb_os.remove(_sb_os.path.join(self.mod_path, name))
                            deleted += 1
                        except Exception:
                            pass
                push("Deleted %d .pyc files" % deleted, color=(0.35, 1.0, 0.55))
                self.refresh_files()
            except Exception as exc:
                push("Delete failed: " + str(exc)[:80], color=(1, 0.3, 0.3))
        self._confirm_window("Delete all .pyc cache files?", "DELETE PYC", delete_all)



