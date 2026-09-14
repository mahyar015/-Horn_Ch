from babase import Plugin
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
import bauiv1 as bui
import bascenev1
from babase import app
from bascenev1lib.mainmenu import MainMenuSession

SIGNATURE = "By Mahyar"
CREATOR = "Creat By Mahyar\nTEL: @Mahyar015"

# ============================================
# ⚙️ تنظیمات پیش‌فرض
# ============================================
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
        if saved:
            d = dict(DEFAULT_REACTIONS); d.update(saved); return d
    except: pass
    return dict(DEFAULT_REACTIONS)


def save_reactions(reactions):
    try:
        app.config['mahyar_reactions_v18'] = dict(reactions); app.config.commit()
    except: pass


def get_cooldowns():
    try:
        saved = app.config.get('mahyar_cooldowns_v18', None)
        if saved:
            d = dict(DEFAULT_COOLDOWNS); d.update(saved); return d
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


# ============================================
# 📍 Mods Button Position
# ============================================
def get_mods_button_position(default_x=None, default_y=None):
    try:
        x = app.config.get('mahyar_mods_btn_x', default_x)
        y = app.config.get('mahyar_mods_btn_y', default_y)
        if x is None or y is None:
            return default_x, default_y
        return float(x), float(y)
    except:
        return default_x, default_y


def save_mods_button_position(x, y):
    try:
        app.config['mahyar_mods_btn_x'] = float(x)
        app.config['mahyar_mods_btn_y'] = float(y)
        app.config.commit()
    except:
        pass


def clear_mods_button_position():
    """پاک کردن موقعیت ذخیره شده دکمه Mods"""
    try:
        if 'mahyar_mods_btn_x' in app.config:
            del app.config['mahyar_mods_btn_x']
        if 'mahyar_mods_btn_y' in app.config:
            del app.config['mahyar_mods_btn_y']
        app.config.commit()
        return True
    except Exception as e:
        print(f"Clear position error: {e}")
        return False


# ============================================
# ✅ Global state
# ============================================
auto_react_enabled = get_enabled_state('react', True)
auto_reply_enabled = get_enabled_state('reply', True)
auto_buyer_enabled = get_enabled_state('buyer', True)
auto_b_enabled = get_enabled_state('auto_b', True)

processed_sell_ids = set()
processed_buy_ids = set()
processed_b_ids = set()
react_cooldown = {}
auto_reply_cooldown = {}

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
    if _limits_cache is None or (now - _limits_cache_time) > 2:
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
            on_activate_call=lambda: c.swish(window)
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
        cw(r, on_outside_click_call=lambda: c.swish(r))
        return r

    @staticmethod
    def swish(*a, **k):
        try: gs('swish').play()
        except: pass
        t = k.get('t', None)
        if t is None and len(a) > 0:
            t = a[0]
        if t:
            try: cw(t, transition='out_scale')
            except: pass

    @staticmethod
    def err(t):
        try: gs('block').play()
        except: pass
        push(t, color=(1, 1, 0))


def get_my_ids():
    global my_own_client_id, my_own_display_num, my_own_name
    try:
        roster = get_roster()
        if not my_own_name: return None, None
        for entry in roster:
            display = entry.get('display_string', '')
            if display.endswith(my_own_name):
                my_own_client_id = entry.get('client_id')
                players = entry.get('players', [])
                if players:
                    name_full = players[0].get('name_full', '')
                    if name_full and ' ' in name_full:
                        try: my_own_display_num = int(name_full.split(' ')[0])
                        except: my_own_display_num = None
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


# ============================================
# ✅ Connection override
# ============================================
original_connect_to_party = original_connect

def new_connect_to_party(address, port=43210, print_progress=False):
    global server_ip, server_port
    server_ip = address
    server_port = port
    save_server(address, port)
    push(f'Saved server: {address}:{port}', color=(0, 1, 1))
    return original_connect_to_party(address, port, print_progress)


bascenev1.connect_to_party = new_connect_to_party


# ============================================
# 🎯 Auto-Reply (فقط کلمه کامل)
# ============================================
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


# ============================================
# 🎯 Spam Logic
# ============================================
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


# ============================================
# 🔤 Fonts
# ============================================
FONTS = {
    'Normal': {},
    'Bold': {
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠',
        'h': '𝐡', 'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧',
        'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭', 'u': '𝐮',
        'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆',
        'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍',
        'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔',
        'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
        '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒',
        '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗',
    },
    'Italic': {
        'a': '𝑎', 'b': '𝑏', 'c': '𝑐', 'd': '𝑑', 'e': '𝑒', 'f': '𝑓', 'g': '𝑔',
        'h': 'ℎ', 'i': '𝑖', 'j': '𝑗', 'k': '𝑘', 'l': '𝑙', 'm': '𝑚', 'n': '𝑛',
        'o': '𝑜', 'p': '𝑝', 'q': '𝑞', 'r': '𝑟', 's': '𝑠', 't': '𝑡', 'u': '𝑢',
        'v': '𝑣', 'w': '𝑤', 'x': '𝑥', 'y': '𝑦', 'z': '𝑧',
        'A': '𝐴', 'B': '𝐵', 'C': '𝐶', 'D': '𝐷', 'E': '𝐸', 'F': '𝐹', 'G': '𝐺',
        'H': '𝐻', 'I': '𝐼', 'J': '𝐽', 'K': '𝐾', 'L': '𝐿', 'M': '𝑀', 'N': '𝑁',
        'O': '𝑂', 'P': '𝑃', 'Q': '𝑄', 'R': '𝑅', 'S': '𝑆', 'T': '𝑇', 'U': '𝑈',
        'V': '𝑉', 'W': '𝑊', 'X': '𝑋', 'Y': '𝑌', 'Z': '𝑍',
    },
    'Bold-Italic': {
        'a': '𝒂', 'b': '𝒃', 'c': '𝒄', 'd': '𝒅', 'e': '𝒆', 'f': '𝒇', 'g': '𝒈',
        'h': '𝒉', 'i': '𝒊', 'j': '𝒋', 'k': '𝒌', 'l': '𝒍', 'm': '𝒎', 'n': '𝒏',
        'o': '𝒐', 'p': '𝒑', 'q': '𝒒', 'r': '𝒓', 's': '𝒔', 't': '𝒕', 'u': '𝒖',
        'v': '𝒗', 'w': '𝒘', 'x': '𝒙', 'y': '𝒚', 'z': '𝒛',
        'A': '𝑨', 'B': '𝑩', 'C': '𝑪', 'D': '𝑫', 'E': '𝑬', 'F': '𝑭', 'G': '𝑮',
        'H': '𝑯', 'I': '𝑰', 'J': '𝑱', 'K': '𝑲', 'L': '𝑳', 'M': '𝑴', 'N': '𝑵',
        'O': '𝑶', 'P': '𝑷', 'Q': '𝑸', 'R': '𝑹', 'S': '𝑺', 'T': '𝑻', 'U': '𝑼',
        'V': '𝑽', 'W': '𝑾', 'X': '𝑿', 'Y': '𝒀', 'Z': '𝒁',
    },
    'Script': {
        'a': '𝒶', 'b': '𝒷', 'c': '𝒸', 'd': '𝒹', 'e': 'ℯ', 'f': '𝒻', 'g': 'ℊ',
        'h': '𝒽', 'i': '𝒾', 'j': '𝒿', 'k': '𝓀', 'l': '𝓁', 'm': '𝓂', 'n': '𝓃',
        'o': 'ℴ', 'p': '𝓅', 'q': '𝓆', 'r': '𝓇', 's': '𝓈', 't': '𝓉', 'u': '𝓊',
        'v': '𝓋', 'w': '𝓌', 'x': '𝓍', 'y': '𝓎', 'z': '𝓏',
        'A': '𝒜', 'B': 'ℬ', 'C': '𝒞', 'D': '𝒟', 'E': 'ℰ', 'F': 'ℱ', 'G': '𝒢',
        'H': 'ℋ', 'I': 'ℐ', 'J': '𝒥', 'K': '𝒦', 'L': 'ℒ', 'M': 'ℳ', 'N': '𝒩',
        'O': '𝒪', 'P': '𝒫', 'Q': '𝒬', 'R': 'ℛ', 'S': '𝒮', 'T': '𝒯', 'U': '𝒰',
        'V': '𝒱', 'W': '𝒲', 'X': '𝒳', 'Y': '𝒴', 'Z': '𝒵',
    },
    'Bold-Script': {
        'a': '𝓪', 'b': '𝓫', 'c': '𝓬', 'd': '𝓭', 'e': '𝓮', 'f': '𝓯', 'g': '𝓰',
        'h': '𝓱', 'i': '𝓲', 'j': '𝓳', 'k': '𝓴', 'l': '𝓵', 'm': '𝓶', 'n': '𝓷',
        'o': '𝓸', 'p': '𝓹', 'q': '𝓺', 'r': '𝓻', 's': '𝓼', 't': '𝓽', 'u': '𝓾',
        'v': '𝓿', 'w': '𝔀', 'x': '𝔁', 'y': '𝔂', 'z': '𝔃',
        'A': '𝓐', 'B': '𝓑', 'C': '𝓒', 'D': '𝓓', 'E': '𝓔', 'F': '𝓕', 'G': '𝓖',
        'H': '𝓗', 'I': '𝓘', 'J': '𝓙', 'K': '𝓚', 'L': '𝓛', 'M': '𝓜', 'N': '𝓝',
        'O': '𝓞', 'P': '𝓟', 'Q': '𝓠', 'R': '𝓡', 'S': '𝓢', 'T': '𝓣', 'U': '𝓤',
        'V': '𝓥', 'W': '𝓦', 'X': '𝓧', 'Y': '𝓨', 'Z': '𝓩',
    },
    'Double': {
        'a': '𝕒', 'b': '𝕓', 'c': '𝕔', 'd': '𝕕', 'e': '𝕖', 'f': '𝕗', 'g': '𝕘',
        'h': '𝕙', 'i': '𝕚', 'j': '𝕛', 'k': '𝕜', 'l': '𝕝', 'm': '𝕞', 'n': '𝕟',
        'o': '𝕠', 'p': '𝕡', 'q': '𝕢', 'r': '𝕣', 's': '𝕤', 't': '𝕥', 'u': '𝕦',
        'v': '𝕧', 'w': '𝕨', 'x': '𝕩', 'y': '𝕪', 'z': '𝕫',
        'A': '𝔸', 'B': '𝔹', 'C': 'ℂ', 'D': '𝔻', 'E': '𝔼', 'F': '𝔽', 'G': '𝔾',
        'H': 'ℍ', 'I': '𝕀', 'J': '𝕁', 'K': '𝕂', 'L': '𝕃', 'M': '𝕄', 'N': 'ℕ',
        'O': '𝕆', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'S': '𝕊', 'T': '𝕋', 'U': '𝕌',
        'V': '𝕍', 'W': '𝕎', 'X': '𝕏', 'Y': '𝕐', 'Z': 'ℤ',
        '0': '𝟘', '1': '𝟙', '2': '𝟚', '3': '𝟛', '4': '𝟜',
        '5': '𝟝', '6': '𝟞', '7': '𝟟', '8': '𝟠', '9': '𝟡',
    },
    'Monospace': {
        'a': '𝚊', 'b': '𝚋', 'c': '𝚌', 'd': '𝚍', 'e': '𝚎', 'f': '𝚏', 'g': '𝚐',
        'h': '𝚑', 'i': '𝚒', 'j': '𝚓', 'k': '𝚔', 'l': '𝚕', 'm': '𝚖', 'n': '𝚗',
        'o': '𝚘', 'p': '𝚙', 'q': '𝚚', 'r': '𝚛', 's': '𝚜', 't': '𝚝', 'u': '𝚞',
        'v': '𝚟', 'w': '𝚠', 'x': '𝚡', 'y': '𝚢', 'z': '𝚣',
        'A': '𝙰', 'B': '𝙱', 'C': '𝙲', 'D': '𝙳', 'E': '𝙴', 'F': '𝙵', 'G': '𝙶',
        'H': '𝙷', 'I': '𝙸', 'J': '𝙹', 'K': '𝙺', 'L': '𝙻', 'M': '𝙼', 'N': '𝙽',
        'O': '𝙾', 'P': '𝙿', 'Q': '𝚀', 'R': '𝚁', 'S': '𝚂', 'T': '𝚃', 'U': '𝚄',
        'V': '𝚅', 'W': '𝚆', 'X': '𝚇', 'Y': '𝚈', 'Z': '𝚉',
        '0': '𝟶', '1': '𝟷', '2': '𝟸', '3': '𝟹', '4': '𝟺',
        '5': '𝟻', '6': '𝟼', '7': '𝟽', '8': '𝟾', '9': '𝟿',
    },
    'Circled': {
        'a': 'ⓐ', 'b': 'ⓑ', 'c': 'ⓒ', 'd': 'ⓓ', 'e': 'ⓔ', 'f': 'ⓕ', 'g': 'ⓖ',
        'h': 'ⓗ', 'i': 'ⓘ', 'j': 'ⓙ', 'k': 'ⓚ', 'l': 'ⓛ', 'm': 'ⓜ', 'n': 'ⓝ',
        'o': 'ⓞ', 'p': 'ⓟ', 'q': 'ⓠ', 'r': 'ⓡ', 's': 'ⓢ', 't': 'ⓣ', 'u': 'ⓤ',
        'v': 'ⓥ', 'w': 'ⓦ', 'x': 'ⓧ', 'y': 'ⓨ', 'z': 'ⓩ',
        'A': 'Ⓐ', 'B': 'Ⓑ', 'C': 'Ⓒ', 'D': 'Ⓓ', 'E': 'Ⓔ', 'F': 'Ⓕ', 'G': 'Ⓖ',
        'H': 'Ⓗ', 'I': 'Ⓘ', 'J': 'Ⓙ', 'K': 'Ⓚ', 'L': 'Ⓛ', 'M': 'Ⓜ', 'N': 'Ⓝ',
        'O': 'Ⓞ', 'P': 'Ⓟ', 'Q': 'Ⓠ', 'R': 'Ⓡ', 'S': 'Ⓢ', 'T': 'Ⓣ', 'U': 'Ⓤ',
        'V': 'Ⓥ', 'W': 'Ⓦ', 'X': 'Ⓧ', 'Y': 'Ⓨ', 'Z': 'Ⓩ',
        '0': '⓪', '1': '①', '2': '②', '3': '③', '4': '④',
        '5': '⑤', '6': '⑥', '7': '⑦', '8': '⑧', '9': '⑨',
    },
    'Squared': {
        'A': '🄰', 'B': '🄱', 'C': '🄲', 'D': '🄳', 'E': '🄴', 'F': '🄵', 'G': '🄶',
        'H': '🄷', 'I': '🄸', 'J': '🄹', 'K': '🄺', 'L': '🄻', 'M': '🄼', 'N': '🄽',
        'O': '🄾', 'P': '🄿', 'Q': '🅀', 'R': '🅁', 'S': '🅂', 'T': '🅃', 'U': '🅄',
        'V': '🅅', 'W': '🅆', 'X': '🅇', 'Y': '🅈', 'Z': '🅉',
    },
    'Fullwidth': {
        'a': 'ａ', 'b': 'ｂ', 'c': 'ｃ', 'd': 'ｄ', 'e': 'ｅ', 'f': 'ｆ', 'g': 'ｇ',
        'h': 'ｈ', 'i': 'ｉ', 'j': 'ｊ', 'k': 'ｋ', 'l': 'ｌ', 'm': 'ｍ', 'n': 'ｎ',
        'o': 'ｏ', 'p': 'ｐ', 'q': 'ｑ', 'r': 'ｒ', 's': 'ｓ', 't': 'ｔ', 'u': 'ｕ',
        'v': 'ｖ', 'w': 'ｗ', 'x': 'ｘ', 'y': 'ｙ', 'z': 'ｚ',
        'A': 'Ａ', 'B': 'Ｂ', 'C': 'Ｃ', 'D': 'Ｄ', 'E': 'Ｅ', 'F': 'Ｆ', 'G': 'Ｇ',
        'H': 'Ｈ', 'I': 'Ｉ', 'J': 'Ｊ', 'K': 'Ｋ', 'L': 'Ｌ', 'M': 'Ｍ', 'N': 'Ｎ',
        'O': 'Ｏ', 'P': 'Ｐ', 'Q': 'Ｑ', 'R': 'Ｒ', 'S': 'Ｓ', 'T': 'Ｔ', 'U': 'Ｕ',
        'V': 'Ｖ', 'W': 'Ｗ', 'X': 'Ｘ', 'Y': 'Ｙ', 'Z': 'Ｚ',
        '0': '０', '1': '１', '2': '２', '3': '３', '4': '４',
        '5': '５', '6': '６', '7': '７', '8': '８', '9': '９',
    },
}


def apply_font(text, font_name):
    """اعمال فونت روی متن"""
    if font_name == 'Normal' or font_name not in FONTS:
        return text
    mapping = FONTS[font_name]
    result = []
    for ch in text:
        result.append(mapping.get(ch, ch))
    return ''.join(result)


# ============================================
# 🧮 Calculator
# ============================================
class Calculator:
    def __init__(s, source):
        s.w = AR.cw(source=source, size=(260, 350), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(235, 320))
        tw(parent=s.w, text='Math Engine', scale=0.8, position=(130, 315), h_align='center', color=(1, 0.5, 0.9))
        tw(parent=s.w, text=SIGNATURE, scale=0.4, position=(130, 300), h_align='center', color=(0.6, 0.6, 0.8))
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
            message = f"⚖️ {s.last_expression}" if s.last_expression else f"⚖️ {s.current_input}"
            safe_chat_send(message); bui.screenmessage(f'Sent: {message}', color=(0, 1, 0)); gs('dingSmall').play()
        except Exception as e: AR.err(f'Send error: {str(e)}')


# ============================================
# 🔤 Fonts Window
# ============================================
class FontsWindow:
    def __init__(s, source):
        s.selected_font = 'Normal'

        s.w = AR.cw(source=source, size=(360, 500), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(330, 465))

        tw(parent=s.w, text='🔤 Fonts', scale=0.95, position=(180, 460),
           h_align='center', color=(1, 0.5, 0.9))
        tw(parent=s.w, text=SIGNATURE, scale=0.35, position=(180, 445),
           h_align='center', color=(0.6, 0.6, 0.8))

        tw(parent=s.w, text='Select Font:', scale=0.55, position=(180, 420),
           h_align='center', color=(1, 1, 0))

        # لیست فونت‌ها
        s.font_buttons = {}
        font_names = list(FONTS.keys())
        y_start = 390
        col_w = 105
        row_h = 30

        for i, fname in enumerate(font_names):
            col = i % 3
            row = i // 3
            x = 15 + col * col_w
            y = y_start - row * row_h

            btn = bw(
                parent=s.w, label=fname, size=(95, 26),
                position=(x, y),
                on_activate_call=lambda f=fname: s.select_font(f),
                color=(0.3, 0.6, 0.3) if fname == 'Normal' else (0.35, 0.35, 0.5),
                textcolor=(1, 1, 1), button_type='square', text_scale=0.5
            )
            s.font_buttons[fname] = btn

        s.selected_text = tw(
            parent=s.w, text='Selected: Normal',
            position=(180, 145), h_align='center', scale=0.5,
            color=(0, 1, 0)
        )

        tw(parent=s.w, text='Enter text:', scale=0.5, position=(180, 122),
           h_align='center', color=(1, 1, 1))

        s.text_input = tw(
            parent=s.w, text='', editable=True, scale=0.8,
            position=(30, 88), size=(300, 28),
            h_align='center', color=(0.9, 0.9, 0.9)
        )

        tw(parent=s.w, text='Preview:', scale=0.4, position=(180, 66),
           h_align='center', color=(0.8, 0.8, 1))

        s.preview = tw(
            parent=s.w, text='(type something)', scale=0.65,
            position=(180, 42), h_align='center',
            color=(0.3, 1, 0.7), maxwidth=320
        )

        bw(parent=s.w, label='📤 Send', size=(140, 30),
           position=(30, 5), on_activate_call=s.send_to_chat,
           color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.65)

        bw(parent=s.w, label='📋 Copy', size=(140, 30),
           position=(190, 5), on_activate_call=s.copy_text,
           color=(0.4, 0.3, 0.7), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.65)

        gs('swish').play()

    def select_font(s, font_name):
        s.selected_font = font_name
        for fname, btn in s.font_buttons.items():
            try:
                color = (0.3, 0.6, 0.3) if fname == font_name else (0.35, 0.35, 0.5)
                bw(btn, color=color)
            except: pass

        tw(s.selected_text, text=f'Selected: {font_name}', color=(0, 1, 0))
        s.update_preview()
        gs('click01').play()

    def update_preview(s):
        try:
            raw = tw(query=s.text_input).strip()
            if not raw:
                tw(s.preview, text='(type something)')
                return
            styled = apply_font(raw, s.selected_font)
            tw(s.preview, text=styled)
        except:
            pass

    def send_to_chat(s):
        try:
            raw = tw(query=s.text_input).strip()
            if not raw:
                AR.err('Enter text first!')
                return
            styled = apply_font(raw, s.selected_font)
            safe_chat_send(styled)
            bui.screenmessage(f'Sent!', color=(0, 1, 0))
            gs('dingSmallHigh').play()
        except Exception as e:
            AR.err(f'Send error: {e}')

    def copy_text(s):
        try:
            if not CIS():
                AR.err('Clipboard not supported!')
                return
            from babase import clipboard_set_text
            raw = tw(query=s.text_input).strip()
            if not raw:
                AR.err('Enter text first!')
                return
            styled = apply_font(raw, s.selected_font)
            clipboard_set_text(styled)
            bui.screenmessage(f'Copied!', color=(0, 1, 0))
            gs('dingSmallHigh').play()
        except Exception as e:
            AR.err(f'Copy error: {e}')


# ============================================
# ⚙️ Edit Reaction
# ============================================
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
        bui.screenmessage(f'%{s.trigger_code} → {value}', color=(0, 1, 0))
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
        bui.screenmessage(f'%{trigger} → {response}', color=(0, 1, 0))
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
        tw(parent=s.w, text=SIGNATURE, scale=0.35, position=(150, 325), h_align='center', color=(0.6, 0.6, 0.8))
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
        for child in s.container.get_children(): child.delete()
        s.item_buttons.clear()
        items = list(current_reactions.items())
        row_height = 30
        total_h = len(items) * row_height + 20
        for i, (trigger, response) in enumerate(items):
            y = total_h - (i + 1) * row_height
            cd = current_cooldowns.get(trigger, DEFAULT_COOLDOWN)
            btn = bw(parent=s.container, label=f'%{trigger} → {response} ({cd}s)', size=(165, 24), position=(5, y), on_activate_call=Call(s.edit_item, trigger), color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1), button_type='square', text_scale=0.45)
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
        bui.screenmessage(f'Deleted: %{trigger}', color=(1, 0.5, 0)); gs('dingSmallLow').play()
        s.build_grid()
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


# ============================================
# ⚙️ Auto-Reply Editor
# ============================================
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
        tw(parent=s.w, text=SIGNATURE, scale=0.35, position=(150, 325), h_align='center', color=(0.6, 0.6, 0.8))
        s.scroll = sw(parent=s.w, size=(260, 160), position=(20, 145))
        s.container = cw(parent=s.scroll, size=(240, 300), background=False)
        s.item_buttons = {}
        s.build_grid()
        bw(parent=s.w, label='+ Add', size=(75, 26), position=(20, 108), on_activate_call=Call(s.add_new), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.55)
        bw(parent=s.w, label='Clear', size=(75, 26), position=(105, 108), on_activate_call=Call(s.clear_all), color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.55)
        s.toggle_btn = bw(parent=s.w, label='ON' if auto_reply_enabled else 'OFF', size=(75, 26), position=(190, 108), on_activate_call=Call(s.toggle), color=(0.2, 0.7, 0.2) if auto_reply_enabled else (0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        tw(parent=s.w, text='Everywhere keyword matches → reply', position=(150, 85), scale=0.35, h_align='center', color=(0.7, 0.7, 1))
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
            btn = bw(parent=s.container, label=f'{keyword} → {response}', size=(165, 24), position=(5, y), on_activate_call=Call(s.edit_item, keyword), color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1), button_type='square', text_scale=0.45)
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


# ============================================
# 🤖 Spam Window
# ============================================
class SpamWindow:
    def __init__(s, source):
        saved_msg, saved_delay = get_spam_settings()
        s.w = AR.cw(source=source, size=(280, 250), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(255, 215))
        tw(parent=s.w, text='Spam', scale=0.9, position=(140, 210), h_align='center', color=(1, 0.5, 0.5))
        tw(parent=s.w, text=SIGNATURE, scale=0.35, position=(140, 195), h_align='center', color=(0.6, 0.6, 0.8))
        s.status = tw(parent=s.w, text='Not Spamming', position=(140, 175), h_align='center', scale=0.6, color=(1, 1, 0))
        tw(parent=s.w, text='Message:', scale=0.5, position=(140, 155), h_align='center', color=(1, 1, 1))
        s.msg_input = tw(parent=s.w, text=saved_msg, editable=True, scale=0.8, position=(25, 125), size=(230, 28), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Delay (seconds):', scale=0.5, position=(140, 100), h_align='center', color=(1, 1, 1))
        s.delay_input = tw(parent=s.w, text=str(saved_delay), editable=True, scale=0.8, position=(25, 70), size=(230, 28), h_align='center', color=(0.9, 0.9, 0.9))
        s.toggle_btn = bw(parent=s.w, label='START', size=(110, 28), position=(20, 35), on_activate_call=Call(s.start), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        bw(parent=s.w, label='STOP', size=(110, 28), position=(150, 35), on_activate_call=Call(s.stop), color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        tw(parent=s.w, text='Chat: "spam on/off"', position=(140, 12), scale=0.35, h_align='center', color=(0.7, 0.7, 1))
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


# ============================================
# 🔄 Reconnect Window
# ============================================
class ReconnectWindow:
    def __init__(s, source):
        global server_ip, server_port
        server_ip, server_port = get_saved_server()

        s.w = AR.cw(source=source, size=(300, 270), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(270, 235))
        tw(parent=s.w, text='Server Manager', scale=0.9, position=(150, 230), h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.35, position=(150, 215), h_align='center', color=(0.6, 0.6, 0.8))

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


# ============================================
# 🤖 Auto Buyer Window
# ============================================
class AutoBuyerWindow:
    def __init__(s, source):
        s.w = AR.cw(source=source, size=(340, 450), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(310, 415))
        tw(parent=s.w, text='Auto Buyer', scale=0.95, position=(170, 410), h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.4, position=(170, 395), h_align='center', color=(0.6, 0.6, 0.8))

        status = "ON" if auto_buyer_enabled else "OFF"
        status_color = (0, 1, 0) if auto_buyer_enabled else (1, 0, 0)
        s.status_text = tw(parent=s.w, text=f'Buy Status: {status}', position=(170, 372), h_align='center', scale=0.65, color=status_color)
        s.toggle_btn = bw(parent=s.w, label='Turn OFF' if auto_buyer_enabled else 'Turn ON', size=(120, 26), position=(20, 342), on_activate_call=Call(s.toggle), color=(0.7, 0.2, 0.2) if auto_buyer_enabled else (0.2, 0.7, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.65)
        bw(parent=s.w, label='Reset', size=(120, 26), position=(160, 342), on_activate_call=Call(s.reset_all), color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)

        # ─── B Auto (مسابقه b XXX) ───
        b_status = "ON" if auto_b_enabled else "OFF"
        b_color = (0, 1, 0) if auto_b_enabled else (1, 0, 0)
        s.b_status_text = tw(parent=s.w, text=f'B Race: {b_status}', position=(170, 315), h_align='center', scale=0.65, color=b_color)
        s.b_toggle_btn = bw(parent=s.w, label='B OFF' if auto_b_enabled else 'B ON', size=(120, 26), position=(20, 285), on_activate_call=Call(s.toggle_b), color=(0.7, 0.2, 0.2) if auto_b_enabled else (0.2, 0.7, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.65)

        tw(parent=s.w, text='Race: when someone sends "b xxx"', position=(170, 265), scale=0.3, h_align='center', color=(0.8, 0.8, 1))

        tw(parent=s.w, text='─── Item Limits ───', position=(170, 240), h_align='center', scale=0.5, color=(1, 1, 0.8))
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
            tw(s.status_text, text='Buy Status: ON', color=(0, 1, 0))
            bui.screenmessage('Auto Buyer ON', color=(0, 1, 0))
        else:
            bw(s.toggle_btn, label='Turn ON', color=(0.2, 0.7, 0.2))
            tw(s.status_text, text='Buy Status: OFF', color=(1, 0, 0))
            bui.screenmessage('Auto Buyer OFF', color=(1, 0.5, 0))
        gs('dingSmall').play()

    def toggle_b(s):
        global auto_b_enabled
        auto_b_enabled = not auto_b_enabled
        save_enabled_state('auto_b', auto_b_enabled)
        if auto_b_enabled:
            bw(s.b_toggle_btn, label='B OFF', color=(0.7, 0.2, 0.2))
            tw(s.b_status_text, text='B Race: ON', color=(0, 1, 0))
            bui.screenmessage('B Race ON', color=(0, 1, 0))
        else:
            bw(s.b_toggle_btn, label='B ON', color=(0.2, 0.7, 0.2))
            tw(s.b_status_text, text='B Race: OFF', color=(1, 0, 0))
            bui.screenmessage('B Race OFF', color=(1, 0.5, 0))
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


# ============================================
# 📍 Edit Place Window
# ============================================
class EditPlaceWindow:
    def __init__(s, source, mods_button):
        s.mods_button = mods_button
        s.step = 5

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

        s.w = AR.cw(source=source, size=(320, 380), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(290, 345))

        tw(parent=s.w, text='📍 Edit Button Place', scale=0.9, position=(160, 340),
           h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.35, position=(160, 325),
           h_align='center', color=(0.6, 0.6, 0.8))

        s.pos_text = tw(parent=s.w, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}',
                        position=(160, 298), h_align='center', scale=0.6,
                        color=(1, 1, 0))
        tw(parent=s.w, text=f'Parent: {int(s.parent_w)} x {int(s.parent_h)}  |  Step: 5px',
           position=(160, 280), h_align='center', scale=0.4,
           color=(0.7, 0.7, 1))

        arrow_size = (60, 45)
        arrow_color = (0.3, 0.5, 0.8)
        cx = 160

        bw(parent=s.w, label='▲', size=arrow_size,
           position=(cx - 30, 220),
           on_activate_call=lambda: s.move(0, s.step),
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.2)

        bw(parent=s.w, label='◀', size=arrow_size,
           position=(cx - 100, 165),
           on_activate_call=lambda: s.move(-s.step, 0),
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.2)

        bw(parent=s.w, label='▶', size=arrow_size,
           position=(cx + 40, 165),
           on_activate_call=lambda: s.move(s.step, 0),
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.2)

        bw(parent=s.w, label='▼', size=arrow_size,
           position=(cx - 30, 110),
           on_activate_call=lambda: s.move(0, -s.step),
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.2)

        bw(parent=s.w, label='💾 Save', size=(130, 30), position=(cx - 140, 35),
           on_activate_call=s.save, color=(0.2, 0.7, 0.3),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.7)

        bw(parent=s.w, label='↺ Reset', size=(130, 30), position=(cx + 10, 35),
           on_activate_call=s.reset, color=(0.7, 0.3, 0.2),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.7)

        tw(parent=s.w, text='Changes apply immediately',
           position=(cx, 12), scale=0.35, h_align='center',
           color=(0.6, 1, 0.6))

        gs('swish').play()

    def move(s, dx, dy):
        try:
            new_x = s.current_x + dx
            new_y = s.current_y + dy

            max_x = max(0.0, s.parent_w - 85)
            max_y = max(0.0, s.parent_h - 25)

            if new_x < 0: new_x = 0.0
            if new_y < 0: new_y = 0.0
            if new_x > max_x: new_x = max_x
            if new_y > max_y: new_y = max_y

            s.current_x = new_x
            s.current_y = new_y

            bw(s.mods_button, position=(s.current_x, s.current_y))
            tw(s.pos_text, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}')
            gs('click01').play()
        except Exception as e:
            print(f"Move error: {e}")

    def save(s):
        save_mods_button_position(s.current_x, s.current_y)
        bui.screenmessage(
            f'Saved! X={int(s.current_x)} Y={int(s.current_y)}',
            color=(0, 1, 0)
        )
        gs('dingSmallHigh').play()

    def reset(s):
        try:
            parent = s.mods_button.get_parent()
            if parent:
                psize = parent.get_size()
                s.parent_w, s.parent_h = float(psize[0]), float(psize[1])
        except:
            pass

        default_x = s.parent_w - 110
        default_y = s.parent_h - 155

        s.current_x, s.current_y = float(default_x), float(default_y)
        bw(s.mods_button, position=(s.current_x, s.current_y))
        tw(s.pos_text, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}')
        save_mods_button_position(s.current_x, s.current_y)
        bui.screenmessage(f'Reset! X={int(s.current_x)} Y={int(s.current_y)}', color=(0, 1, 1))
        gs('dingSmallHigh').play()


# ============================================
# 🎯 Mods Menu
# ============================================
class ModsMenu:
    def __init__(s, source, mods_button=None):
        s.mods_button_ref = mods_button
        s.w = AR.cw(source=source, size=(400, 570), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(370, 530))

        tw(parent=s.w, text='⚙️ Mods Menu', scale=1.2, position=(200, 525), h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.4, position=(200, 505), h_align='center', color=(0.6, 0.6, 0.8))

        s.scroll = sw(parent=s.w, size=(340, 470), position=(30, 25))
        s.container = cw(parent=s.scroll, size=(320, 850), background=False)

        buttons = [
            ('🧮 Calculator', Calculator, (0, 0.3, 0.8)),
            ('🛒 Auto Buyer', AutoBuyerWindow, (0.2, 0.6, 0.8)),
            ('⚡ Auto React', ReactionEditorWindow, (0.8, 0.5, 0.2)),
            ('💬 Auto Reply', AutoReplyEditorWindow, (0.3, 0.7, 0.4)),
            ('📢 Spam', SpamWindow, (0.8, 0.3, 0.3)),
            ('🔄 Reconnect', ReconnectWindow, (0.4, 0.6, 0.4)),
            ('🔤 Fonts', FontsWindow, (0.7, 0.4, 0.8)),
            ('📍 Edit Place', None, (0.6, 0.4, 0.7)),
        ]

        s.item_buttons = []
        y_pos = 800
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
            y_pos -= 65

        cw(s.container, size=(320, 850))

        gs('swish').play()

    def open_window(s, cls):
        gs('swish').play()
        try:
            AR.swish(s.w)
            if cls is None:
                if s.mods_button_ref is not None:
                    teck(0.15, lambda: EditPlaceWindow(s.w, s.mods_button_ref))
                else:
                    bui.screenmessage('Mods button not found!', color=(1, 0, 0))
            else:
                teck(0.15, lambda: cls(s.w))
        except Exception as e:
            print(f"Open window error: {e}")


# ============================================
# 🤖 Auto Buyer Logic
# ============================================
SELL_PATTERN = re.compile(r'💰Sell ID:\s*(\w+)')
BUY_PATTERN = re.compile(r'(\w+):\s*💳Buy\s*<\s*([\d,]+)\s+(\w+)\s*\([^)]+\)\s*>\s*for\s*([\d,]+)\s*coins(?:\?.*)?')
B_RACE_PATTERN = re.compile(r'^b\s+([a-zA-Z]+\d+)\s*$')


def process_sell(item_id):
    if item_id in processed_sell_ids: return
    processed_sell_ids.add(item_id)
    if len(processed_sell_ids) > 100: processed_sell_ids.clear()
    safe_chat_send(f"b {item_id}")


def process_buy(item_id, count, item_name, total_price):
    current_limits = _get_cached_limits()
    if item_name not in current_limits:
        safe_chat_send("0 "); return
    bid_key = f"{item_id}_{item_name}_{count}_{total_price}"
    if bid_key in processed_buy_ids: return
    processed_buy_ids.add(bid_key)
    if len(processed_buy_ids) > 200: processed_buy_ids.clear()
    if count <= 0: safe_chat_send("0 "); return
    unit_price = total_price / count
    limit = current_limits[item_name]
    if unit_price <= limit:
        safe_chat_send("1 ")
    else:
        safe_chat_send("0 ")


def process_b_race(item_id, sender):
    """مسابقه b XXX - سریع همون رو می‌فرستیم"""
    if sender and my_own_name and sender == my_own_name:
        return False
    race_key = item_id
    if race_key in processed_b_ids:
        return False
    processed_b_ids.add(race_key)
    if len(processed_b_ids) > 100:
        processed_b_ids.clear()
    safe_chat_send(f"b {item_id}")
    return True


# ============================================
# 🎯 Auto-React Logic
# ============================================
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
            is_target_me = False
            if my_own_client_id:
                pattern1 = rf'%\s*{re.escape(trigger_lower)}\s+(\d+)'
                m1 = re.search(pattern1, content_lower)
                if m1 and int(m1.group(1)) == my_own_client_id: is_target_me = True
            if not is_target_me and my_own_display_num is not None:
                pattern2 = rf'\b{re.escape(trigger_lower)}\s+(\d+)'
                m2 = re.search(pattern2, content_lower)
                if m2 and int(m2.group(1)) == my_own_display_num: is_target_me = True
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
    except Exception as e: print(f"React error: {e}")


# ============================================
# 🧮 Calculator Chat Detection
# ============================================
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
        return f"⚖️ {match.group(1)} {op_display} {match.group(3)} = {result_str}"
    except: return None


# ============================================
# 🧮 Chat Commands
# ============================================
_plugin_instance = None


def check_chat_commands(msg):
    global spam_active
    try:
        content = msg
        sender = None
        if ': ' in msg:
            parts = msg.split(': ', 1)
            sender = parts[0].strip()
            content = parts[1].strip()
        content = content.strip()
        content_lower = content.lower()

        # ─── تشخیص سریع b XXX (مسابقه) ───
        if auto_b_enabled:
            m_b = B_RACE_PATTERN.match(content)
            if m_b:
                item_id = m_b.group(1)
                if process_b_race(item_id, sender):
                    return True

        # ─── دستور Mods Reset ───
        if content_lower in ('mods reset', 'modsreset', 'ریست مودز', 'مودز ریست'):
            try:
                clear_mods_button_position()

                moved = False
                if _plugin_instance is not None:
                    btn = getattr(_plugin_instance, 'mods_button_ref', None)
                    if btn is not None:
                        try:
                            new_x = 0.0
                            new_y = 0.0
                            try:
                                parent = btn.get_parent()
                                if parent:
                                    psize = parent.get_size()
                                    new_x = float(psize[0]) - 110
                                    new_y = float(psize[1]) - 155
                            except:
                                new_x = 1810.0
                                new_y = 925.0

                            if new_x < 0: new_x = 0.0
                            if new_y < 0: new_y = 0.0

                            bw(btn, position=(new_x, new_y))
                            push(f"✅ Mods → X={int(new_x)} Y={int(new_y)}", color=(0, 1, 0))
                            moved = True
                        except Exception as ee:
                            print(f"Move on reset error: {ee}")

                if not moved:
                    push("✅ Mods reset! Reopen Party window.", color=(0, 1, 0))

                gs('dingSmallHigh').play()
            except Exception as e:
                push(f"Reset error: {e}", color=(1, 0, 0))
            return True

        # ─── Spam Commands ───
        if content_lower in ('spam on', 'اسپم روشن'):
            start_spam(spam_message if spam_message else 'spam', spam_delay)
            return True

        if content_lower in ('spam off', 'اسپم خاموش', 'توقف اسپم', 'stop spam'):
            stop_spam()
            return True

        match = re.match(r'^اسپم\s+(.+?)\s+([\d.]+)\s*$', content_lower)
        if match:
            message = match.group(1).strip()
            try: delay = float(match.group(2))
            except: return False
            if delay <= 0: delay = 2.0
            if spam_active: stop_spam()
            start_spam(message, delay); return True

    except Exception as e:
        print(f"Chat command error: {e}")
    return False


# ============================================
# 🎯 Auto Reconnect Logic
# ============================================
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


# ============================================
# 🎯 Main Plugin
# ============================================
# ba_meta require api 9
# ba_meta export babase.Plugin
class byMahyar(Plugin):
    def __init__(s):
        global _plugin_instance, my_own_name
        _plugin_instance = s

        try: my_own_name = APP.plus.get_v1_account_name()
        except: my_own_name = None

        s.last_msg_hash = ""
        s.last_calc_hash = ""

        s.mods_button_ref = None

        teck(1, s.ear)
        teck(1, s.calc_ear)
        teck(1, s.reconnect_ear)

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
            except:
                saved_x, saved_y = float(default_x), float(default_y)

            b_mods = AR.bw(
                position=(saved_x, saved_y),
                parent=self._root_widget,
                size=(85, 25),
                label='Mods',
                color=(0.3, 0.5, 0.8)
            )
            bw(b_mods, on_activate_call=lambda: s.delayed_open(ModsMenu, b_mods))

            s.mods_button_ref = b_mods

            return r

        party.PartyWindow.__init__ = e

        teck(3.0, lambda: bui.screenmessage(CREATOR, color=(0, 1, 1)))

    def ear(s):
        try:
            z = GCM()
            teck(0.005, s.ear)

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
                if auto_buyer_enabled:
                    m = SELL_PATTERN.search(msg)
                    if m:
                        process_sell(m.group(1))
                        return
                    m = BUY_PATTERN.search(msg)
                    if m:
                        process_buy(m.group(1), int(m.group(2).replace(',', '')), m.group(3).lower(), int(m.group(4).replace(',', '')))
                        return
            except: pass

            try:
                if check_chat_commands(msg): return
            except: pass
            try:
                if check_auto_reply(msg): return
            except: pass
            try:
                check_reaction(msg)
            except: pass

        except Exception as e:
            try:
                teck(0.005, s.ear)
            except:
                pass
            print(f"Error in ear: {e}")

    def calc_ear(s):
        try:
            z = GCM()
            teck(0.2, s.calc_ear)

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
                teck(0.2, s.calc_ear)
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
        if cls is ModsMenu:
            teck(0.05, lambda: cls(btn, btn))
        else:
            teck(0.05, lambda: cls(btn))
