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
DEFAULT_COOLDOWNS = {'fr': 0.15, 'cu': 0.15, 'fl': 0.15}
DEFAULT_COOLDOWN = 0.15
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


def get_mods_button_position(default_x=None, default_y=None):
    try:
        x = app.config.get('mahyar_mods_btn_x', default_x)
        y = app.config.get('mahyar_mods_btn_y', default_y)
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

# ============================================================
# AutoBuyer - دقیقاً منطق fastBuy_V2_16
# ============================================================
_sod = False
_lasch = ""
_max_price = 100000

# Snapshotهای جداگانه برای جلوگیری از جا افتادن پیام‌ها در burstهای چت
_last_seen_messages = None
_buyer_seen_messages = None
_buyer_pending_id = None
_buyer_pending_since = 0.0
_buyer_queue = []

_limits_cache = None
_limits_cache_time = 0


def _get_cached_limits():
    global _limits_cache, _limits_cache_time
    now = time.time()
    if _limits_cache is None or (now - _limits_cache_time) > 0.1:
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
        for child in s.container.get_children(): child.delete()
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
            max_x = max(0, s.parent_w - 85)
            max_y = max(0, s.parent_h - 25)
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

        s.current_x, s.current_y = float(default_x), float(default_y)
        s.apply_position()

        bui.screenmessage('Reset!', color=(0, 1, 1))
        gs('dingSmallHigh').play()


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
            ('BSLife', 'BSLIFE', (0.12, 0.48, 0.72)),
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
            if cls == 'BSLIFE':
                teck(0.15, open_ally_manager)
            elif cls is None:
                if s.mods_button_ref is not None:
                    teck(0.15, lambda: EditPlaceWindow(s.w, s.mods_button_ref))
                else:
                    bui.screenmessage('Mods button not found!', color=(1, 0, 0))
            else:
                teck(0.15, lambda: cls(s.w))
        except Exception as e:
            print(f"Open window error: {e}")


# ============================================================
# AutoBuyer - دقیقاً منطق fastBuy_V2_16 با رفع باگ تکرار
# ============================================================

def fast_send(message):
    """ارسال کوتاه و سریع پاسخ خرید به چت سرور."""
    try:
        CM(message)
    except Exception:
        pass


def _collect_new_messages(current, previous):
    """Return messages appended since the previous snapshot, including rolling buffers."""
    current = list(current or [])
    if previous is None:
        return current
    previous = list(previous or [])
    if not current:
        return []
    if current == previous:
        return []

    # Works for both an ever-growing history and a fixed-size/rolling chat history.
    max_overlap = min(len(previous), len(current))
    for overlap in range(max_overlap, 0, -1):
        if previous[-overlap:] == current[:overlap]:
            return current[overlap:]

    # No overlap means the history was reset/replaced or more messages arrived than
    # fit in the old window. Process the visible window rather than silently missing it.
    return current


def _buysel(message=None):
    """Evaluate the server's Buy prompt for the currently pending sell ID."""
    global _lasch, _buyer_pending_id, _buyer_pending_since

    try:
        if message is None:
            z = GCM()
            candidates = list(z[-5:]) if z else []
        else:
            candidates = [message]

        for line in candidates:
            if "💳Buy < " not in line:
                continue

            # Expected protocol: Server: <sell-id>: 💳Buy < ...
            parts = line.split(": ", 2)
            if len(parts) < 3:
                continue
            cod = parts[1].strip()
            if str(_lasch).strip() != cod:
                continue

            words = parts[2].replace(",", "").split()
            if len(words) < 8:
                continue

            count = int(words[2])
            item_name = words[3]
            price_match = re.search(r"-?\d+", words[7])
            if not price_match or count <= 0:
                continue
            total_price = int(price_match.group(0))
            unit_price = total_price / count

            current_limits = _get_cached_limits()
            limit = current_limits.get(item_name, 0)
            answer = "1 " if total_price <= _max_price and unit_price <= limit else "0 "

            _lasch = answer
            _buyer_pending_id = None
            _buyer_pending_since = 0.0
            fast_send(answer)
            _dispatch_next_buy()
            return True
    except Exception as e:
        print(f"AutoBuyer response error: {e}")
    return False


def _send_buy_request(sell_id):
    """Send one buy request and remember its response ID."""
    global _lasch, _buyer_pending_id, _buyer_pending_since
    _lasch = str(sell_id).strip()
    _buyer_pending_id = _lasch
    _buyer_pending_since = time.monotonic()
    fast_send(f"b {_lasch}")


def _dispatch_next_buy():
    """Start the next queued eligible listing as soon as the current one completes."""
    global _buyer_queue
    if _buyer_pending_id is not None:
        return
    now = time.monotonic()
    while _buyer_queue:
        sell_id, queued_at = _buyer_queue.pop(0)
        if now - queued_at > 5.0:
            continue  # Do not buy an offer that sat in the queue too long.
        _send_buy_request(sell_id)
        return


def _process_buyer_message(message):
    """Process one unseen server line immediately; no delayed retry timers needed."""
    global _sod, _lasch, _buyer_pending_id, _buyer_pending_since

    if not isinstance(message, str):
        return

    if "💳Buy < " in message:
        _buysel(message)
        return

    if "Server" not in message:
        return

    if "💰Sell <" in message:
        try:
            body = message.split("💰Sell <", 1)[1].replace(",", "")
            parts = body.split()
            if len(parts) < 5:
                _sod = False
                return

            count = int(parts[0])
            item_name = parts[1]
            price_match = re.search(r"-?\d+", parts[4])
            if not price_match or count <= 0:
                _sod = False
                return
            total_price = int(price_match.group(0))
            unit_price = total_price / count
            limit = _get_cached_limits().get(item_name, 0)
            _sod = total_price <= _max_price and unit_price <= limit
        except Exception:
            _sod = False
        return

    if "💰Sell ID: " in message and _sod:
        try:
            sell_id = message.split("💰Sell ID: ", 1)[1].strip()
            if not sell_id:
                return

            now = time.monotonic()
            _sod = False
            if _buyer_pending_id is not None:
                # Preserve rapid incoming listings instead of losing their IDs
                # while another Buy prompt is being answered.
                already_queued = any(queued_id == sell_id for queued_id, _ in _buyer_queue)
                if sell_id != _buyer_pending_id and not already_queued and len(_buyer_queue) < 20:
                    _buyer_queue.append((sell_id, now))
                return

            _send_buy_request(sell_id)
        except Exception as e:
            print(f"AutoBuyer sell-ID error: {e}")


def _dls():
    """Compatibility helper for older scheduled callbacks."""
    if _buyer_pending_id is not None:
        _buysel()


def sellcek():
    """Poll quickly, but process every unseen chat message instead of only z[-1]."""
    global _buyer_seen_messages, _buyer_pending_id, _buyer_pending_since, _lasch, _sod, _buyer_queue

    if not auto_buyer_enabled:
        # Keep the cursor current while disabled so old listings are not bought
        # immediately after the feature is enabled again.
        try:
            _buyer_seen_messages = list(GCM() or [])
        except Exception:
            pass
        _buyer_pending_id = None
        _buyer_pending_since = 0.0
        _buyer_queue[:] = []
        _sod = False
        _lasch = "0 "
        teck(0.2, sellcek)
        return

    try:
        z = GCM()
        current = list(z or [])
        if _buyer_seen_messages is None:
            # Preserve the old startup behavior: inspect only the newest line once.
            new_messages = current[-1:]
        else:
            new_messages = _collect_new_messages(current, _buyer_seen_messages)
        _buyer_seen_messages = current

        # Process newly-arrived responses before timing out a pending ID, so a
        # delayed server reply in this same batch still gets matched correctly.
        for message in new_messages:
            _process_buyer_message(message)

        now = time.monotonic()
        if _buyer_pending_id is not None and now - _buyer_pending_since >= 3.0:
            _buyer_pending_id = None
            _buyer_pending_since = 0.0
            _lasch = "0 "
            _dispatch_next_buy()
    except Exception as e:
        print(f"AutoBuyer loop error: {e}")

    teck(0.01, sellcek)


# ============================================================
# بقیه توابع
# ============================================================

def check_reaction(msg):
    """Respond to every matching FR/FL-style command that targets this player."""
    global my_own_client_id, my_own_display_num
    if not auto_react_enabled:
        return

    try:
        if my_own_client_id is None or my_own_display_num is None:
            get_my_ids()

        # Convert Persian/Arabic numerals (e.g. ۱۲۱) to ASCII so ID parsing is stable.
        digit_map = str.maketrans(
            "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
            "01234567890123456789",
        )
        normalized_msg = str(msg).translate(digit_map)
        sender = None
        content = normalized_msg
        if ": " in normalized_msg:
            sender, content = normalized_msg.split(": ", 1)
            sender = sender.strip()
            content = content.strip()

        if sender and my_own_name and sender == my_own_name:
            return

        content_lower = content.lower()
        current_reactions = get_reactions()
        current_cooldowns = get_cooldowns()
        now = time.time()

        for trigger, response in current_reactions.items():
            trigger_lower = str(trigger).lower().strip()
            if not trigger_lower:
                continue

            pattern = re.compile(
                rf"(?:^|[\s/])%?\s*{re.escape(trigger_lower)}\s*%?\s*(\d+)"
            )
            target_is_me = False
            for match in pattern.finditer(content_lower):
                try:
                    target_num = int(match.group(1))
                except (TypeError, ValueError):
                    continue
                if (
                    (my_own_client_id is not None and target_num == my_own_client_id)
                    or (my_own_display_num is not None and target_num == my_own_display_num)
                ):
                    target_is_me = True
                    break

            if not target_is_me:
                continue

            cd_time = max(0.0, float(current_cooldowns.get(trigger, DEFAULT_COOLDOWN)))
            cd_key = f"{trigger_lower}_{sender or 'unknown'}"
            last_time = react_cooldown.get(cd_key, 0.0)
            if now - last_time < cd_time:
                # Do not stop checking other triggers; FR cooling down must not
                # prevent FL (or another configured trigger) from replying.
                continue

            react_cooldown[cd_key] = now
            if len(react_cooldown) > 100:
                cutoff = now - 300
                for key, timestamp in list(react_cooldown.items()):
                    if timestamp < cutoff:
                        del react_cooldown[key]

            safe_chat_send(response)
            try:
                gs('dingSmall').play()
            except Exception:
                pass
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


# ba_meta require api 9
# BSLIFE Ally Manager — v10 (BetterParty-style UI)
# Made with Tajer and Windows an Taha
# api 9 — mod is Free
# BsRush/Tajer


import colorsys
import http.cookiejar
import json
import math
import os
import random
import ssl
import threading
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

import babase
import bauiv1 as bui

# ═══════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════

BASE_URL = "https://bslife.ir"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".bslife_ally")
os.makedirs(DATA_DIR, exist_ok=True)
SESSION_FILE = os.path.join(DATA_DIR, "session.json")
LOG_FILE = os.path.join(DATA_DIR, "bslife_debug.log")

_CFG_THEME = 'BetterParty_Theme'
_CFG_FX = 'BetterParty_FX'
_CFG_SPEED = 'BetterParty_Speed'
_FX_T0 = time.time()

TXT = (0.94, 0.96, 1.0)
DIM = (0.72, 0.82, 0.95)
GOLD = (1.0, 0.86, 0.35)
GREEN = (0.5, 1.0, 0.6)
RED = (1.0, 0.5, 0.45)

MyCall = getattr(bui, 'CallPartial', bui.Call)

# ═══════════════════════════════════════════════════════════════
# LANGUAGE
# ═══════════════════════════════════════════════════════════════


def get_is_persian():
    try:
        lang = bui.app.lang.language
        return lang == "Persian" or lang == "fa" or lang == "Farsi"
    except Exception:
        return False


IS_FA = get_is_persian()

T = {
    "login": {"fa": "ورود", "en": "Login"},
    "logout": {"fa": "خروج", "en": "Logout"},
    "cancel": {"fa": "انصراف", "en": "Cancel"},
    "overview": {"fa": "مرور کلی", "en": "Overview"},
    "members": {"fa": "اعضا", "en": "Members"},
    "requests": {"fa": "درخواست‌ها", "en": "Requests"},
    "vault": {"fa": "خزانه", "en": "Vault"},
    "settings": {"fa": "تنظیمات", "en": "Settings"},
    "ranking": {"fa": "رنکینگ", "en": "Ranking"},
    "chat": {"fa": "چت", "en": "Chat"},
    "news": {"fa": "اخبار", "en": "News"},
    "manage": {"fa": "مدیریت", "en": "Manage"},
    "title": {"fa": "عنوان", "en": "Title"},
    "color": {"fa": "رنگ", "en": "Color"},
    "apply_title": {"fa": "اعمال عنوان", "en": "Apply Title"},
    "role": {"fa": "نقش", "en": "Role"},
    "change_role": {"fa": "تغییر نقش", "en": "Change Role"},
    "mute": {"fa": "سکوت", "en": "Mute"},
    "unmute": {"fa": "رفع سکوت", "en": "Unmute"},
    "kick": {"fa": "اخراج", "en": "Kick"},
    "leader": {"fa": "لیدر", "en": "Leader"},
    "general": {"fa": "جنرال", "en": "General"},
    "spy": {"fa": "جاسوس", "en": "Spy"},
    "member": {"fa": "عضو", "en": "Member"},
    "deposit": {"fa": "واریز", "en": "Deposit"},
    "split": {"fa": "تقسیم خزانه", "en": "Split Vault"},
    "capacity": {"fa": "ظرفیت", "en": "Capacity"},
    "buy_1": {"fa": "خرید +۱", "en": "Buy +1"},
    "new": {"fa": "جدید", "en": "New"},
    "accepted": {"fa": "تایید شده", "en": "Accepted"},
    "rejected": {"fa": "رد شده", "en": "Rejected"},
    "yes": {"fa": "قبول", "en": "Accept"},
    "no": {"fa": "رد", "en": "Reject"},
    "yes2": {"fa": "بله", "en": "Yes"},
    "no2": {"fa": "خیر", "en": "No"},
    "ready": {"fa": "آماده", "en": "Ready"},
    "loading": {"fa": "در حال لود...", "en": "Loading..."},
    "session_expired": {"fa": "سشن منقضی شده", "en": "Session expired"},
    "session_retry": {"fa": "سشن منقضی شده، در حال بازیابی...", "en": "Session expired, recovering..."},
    "not_ranked": {"fa": "هنوز رتبه‌بندی نشده", "en": "Not ranked yet"},
    "alliance_name": {"fa": "نام اتحاد", "en": "Alliance Name"},
    "your_role": {"fa": "نقش شما", "en": "Your Role"},
    "members_count": {"fa": "تعداد اعضا", "en": "Members Count"},
    "coins": {"fa": "سکه", "en": "Coins"},
    "message": {"fa": "پیام...", "en": "Message..."},
    "send": {"fa": "ارسال", "en": "Send"},
    "error_fill": {"fa": "لطفا هر دو فیلد را پر کنید!", "en": "Please fill both fields!"},
    "logging_in": {"fa": "در حال ورود", "en": "Logging in"},
    "success_loading": {"fa": "موفق! در حال لود...", "en": "Success! Loading..."},
    "error": {"fa": "خطا", "en": "Error"},
    "hub_title": {"fa": "مرکز اتحادها", "en": "Alliance Hub"},
    "not_in_ally": {"fa": "شما عضو هیچ اتحادی نیستید.", "en": "You are not in an alliance."},
    "create_ally": {"fa": "ساخت اتحاد", "en": "Create Ally"},
    "join_ally": {"fa": "پیوستن به اتحاد", "en": "Join Ally"},
    "search": {"fa": "جستجو", "en": "Search"},
    "cost": {"fa": "هزینه", "en": "Cost"},
    "user": {"fa": "کاربر", "en": "User"},
    "no_ally": {"fa": "بدون اتحاد", "en": "No Ally"},
    "request_sent": {"fa": "درخواست ارسال شد", "en": "Request sent"},
    "ok": {"fa": "باشه", "en": "OK"},
    "request_btn": {"fa": "درخواست", "en": "Request"},
    "join_btn": {"fa": "عضویت", "en": "Join"},
    "confirm": {"fa": "تایید", "en": "Confirm"},
    "success": {"fa": "موفق", "en": "Success"},
    "fail": {"fa": "ناموفق", "en": "Failed"},
    "enter_amount": {"fa": "مقدار را وارد کنید", "en": "Enter amount"},
    "equal_all": {"fa": "مساوی بین همه", "en": "Equal: All"},
    "equal_ranking": {"fa": "مساوی بین ۲۰ برتر", "en": "Equal: Top 20"},
    "ranking_points": {"fa": "متناسب با امتیاز", "en": "By points"},
    "remove_role": {"fa": "حذف نقش", "en": "Remove role"},
    "create_fail": {"fa": "خطا در ساخت اتحاد", "en": "Create failed"},
    "already_in_ally": {"fa": "شما در اتحاد دیگری هستید", "en": "Already in another ally"},
    "not_enough_coins": {"fa": "سکه کافی نیست", "en": "Not enough coins"},
    "select_type": {"fa": "نوع را انتخاب کنید", "en": "Select type"},
    "select_role": {"fa": "نقش را انتخاب کنید", "en": "Select role"},
    "vault_split_ok": {"fa": "خزانه تقسیم شد", "en": "Vault split successful"},
    "deposit_ok": {"fa": "واریز موفق", "en": "Deposit successful"},
    "role_changed": {"fa": "نقش تغییر کرد", "en": "Role changed"},
    "leave_ally": {"fa": "خروج از اتحاد", "en": "Leave Ally"},
    "leave_confirm": {"fa": "مطمئنید می‌خواهید از اتحاد خارج شوید؟", "en": "Are you sure you want to leave?"},
    "vault_news": {"fa": "تاریخچه خزانه", "en": "Vault History"},
    "vault_shares": {"fa": "لیست سهام", "en": "Vault Shares"},
    "shares_btn": {"fa": "سهام", "en": "Shares"},
    "history": {"fa": "تاریخچه", "en": "History"},
    "more": {"fa": "بیشتر", "en": "More"},
    "no_news": {"fa": "خبری وجود ندارد", "en": "No news available"},
    "gkick": {"fa": "حذف مجاز جنرال", "en": "General Kick Limit"},
    "spynet": {"fa": "بودجه Spynet", "en": "Spynet Budget"},
    "tag_status": {"fa": "وضعیت تگ", "en": "Tag Status"},
    "tag_active": {"fa": "فعال", "en": "Active"},
    "tag_inactive": {"fa": "غیرفعال", "en": "Inactive"},
    "sale_price": {"fa": "فروش اتحاد", "en": "Ally Sale Price"},
    "enrol_settings": {"fa": "تنظیمات عضوگیری", "en": "Enrolment Settings"},
    "mode_direct": {"fa": "مستقیم", "en": "Direct"},
    "mode_request": {"fa": "درخواستی", "en": "Request"},
    "mode_closed": {"fa": "بسته", "en": "Closed"},
    "min_coin": {"fa": "حداقل سکه", "en": "Min Coins"},
    "req_top": {"fa": "رتبه تاپ", "en": "Required Top"},
    "min_score": {"fa": "حداقل امتیاز", "en": "Min Score"},
    "saved": {"fa": "ذخیره شد", "en": "Saved"},
    "order_rank": {"fa": "رتبه", "en": "Rank"},
    "order_new": {"fa": "جدیدترین", "en": "Newest"},
    "order_old": {"fa": "قدیمی‌ترین", "en": "Oldest"},
    "order_count": {"fa": "بیشترین عضو", "en": "Most Members"},
    "style": {"fa": "ظاهر", "en": "Style"},
    "set": {"fa": "تنظیم", "en": "Set"},
    "change": {"fa": "تغییر", "en": "Change"},
    "toggle": {"fa": "تغییر وضعیت", "en": "Toggle"},
    "forced": {"fa": "اجباری", "en": "Forced"},
    "off": {"fa": "خاموش", "en": "Off"},
    "bot_link": {"fa": "اتصال به ربات تلگرام", "en": "Telegram Bot Link"},
    "join_mode": {"fa": "حالت ورود", "en": "Join Mode"},
    "not_set": {"fa": "تنظیم نشده", "en": "Not set"},
    "role_full": {"fa": "ظرفیت نقش پر است", "en": "Role capacity is full"},
    "no_bot": {"fa": "اکانت به بات متصل نیست", "en": "Account not linked to bot"},
    "no_ranking": {"fa": "اطلاعات رنکینگ موجود نیست", "en": "No ranking data"},
    "enter_name": {"fa": "نام را وارد کنید", "en": "Enter a name"},
    "req_rejected": {"fa": "درخواست شما قبلا رد شده است.", "en": "Your request was rejected before."},
    "req_pending": {"fa": "درخواست شما در انتظار بررسی است.", "en": "Your request is pending."},
    "left_recent": {"fa": "اخیرا از این اتحاد خارج شده‌اید. ۲۴ ساعت صبر کنید.", "en": "You left this ally recently. Wait 24 hours."},
    "no_requirements": {"fa": "شما شرایط لازم برای ورود را ندارید.", "en": "You don't meet the requirements."},
    "needed": {"fa": "شرایط مورد نیاز", "en": "Required"},
    "min_deposit": {"fa": "حداقل واریز ۱۰۰ سکه است", "en": "Minimum deposit is 100 coins"},
    "select_mode": {"fa": "انتخاب حالت", "en": "Select Mode"},
    "empty": {"fa": "موردی وجود ندارد", "en": "Nothing here"},
    "username": {"fa": "اسم خاص", "en": "Username"},
    "otp": {"fa": "کد لاگین", "en": "Login code"},
    "login_h1": {"fa": "• در چت بازی تایپ کنید: login", "en": "• In BombSquad chat, type: login"},
    "login_h2": {"fa": "• یا در بات @BslifeBot: login", "en": "• Or message @BslifeBot: login"},
    "login_sub": {"fa": "مدیریت اتحاد از داخل بازی", "en": "Manage your alliance in-game"},
    "theme": {"fa": "تم", "en": "Theme"},
    "channels": {"fa": "Channels", "en": "Channels"},
}


def L(key):
    lang = "fa" if IS_FA else "en"
    return T.get(key, {}).get(lang, key)


# ═══════════════════════════════════════════════════════════════
# LOGGING / UTILS
# ═══════════════════════════════════════════════════════════════

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def fmt(n):
    try:
        return f"{int(n):,}"
    except Exception:
        return str(n)


def role_name(rid):
    return L({1: "leader", 2: "general", 3: "spy"}.get(rid, "member"))


def role_color(rid):
    return {1: (1.0, 0.8, 0.25), 2: (0.55, 0.75, 1.0), 3: (0.85, 0.6, 1.0)}.get(rid, (0.85, 0.9, 1.0))


# ═══════════════════════════════════════════════════════════════
# API CLIENT (unchanged logic)
# ═══════════════════════════════════════════════════════════════

class BslifeAPI:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        try:
            ctx = ssl.create_default_context()
        except Exception:
            try:
                ctx = ssl._create_unverified_context()
            except Exception:
                ctx = None
        handlers = [urllib.request.HTTPCookieProcessor(self.jar)]
        try:
            handlers.append(urllib.request.HTTPSHandler(context=ctx))
        except Exception:
            pass
        self.opener = urllib.request.build_opener(*handlers)
        self.headers = {"User-Agent": "BombSquad/1.7.x (Modded Ally Manager)",
                        "Accept": "application/json", "Content-Type": "application/json"}
        self.user = None
        self.ally = None
        self.roleid = None
        self.memberid = None
        self._load_cookies()

    def _load_cookies(self):
        if not os.path.exists(SESSION_FILE):
            return
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in data.get("cookies", {}).items():
                c = http.cookiejar.Cookie(
                    version=0, name=k, value=v, port=None, port_specified=False,
                    domain="bslife.ir", domain_specified=True, domain_initial_dot=False,
                    path="/", path_specified=True, secure=True,
                    expires=None, discard=True, comment=None, comment_url=None,
                    rest={"HttpOnly": None}, rfc2109=False)
                self.jar.set_cookie(c)
            self.user = data.get("user")
            log(f"Loaded session for: {self.user}")
        except Exception as e:
            log(f"Load cookies failed: {e}")

    def _save_cookies(self):
        data = {"cookies": {c.name: c.value for c in self.jar}, "user": self.user}
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log(f"Save cookies failed: {e}")

    def post(self, path, payload):
        url = BASE_URL + path
        try:
            data = json.dumps(payload).encode("utf-8")
            cookies = self.jar._cookies
            cookie_str = "".join(f"{n}={cookies[d][p][n].value}; "
                                 for d in cookies for p in cookies[d] for n in cookies[d][p])
            headers = self.headers.copy()
            if cookie_str:
                headers["Cookie"] = cookie_str
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with self.opener.open(req, timeout=20) as resp:
                result = resp.read().decode("utf-8", errors="replace").strip()
                self._save_cookies()
                return result
        except urllib.error.HTTPError as e:
            return f"__HTTPERROR__:{e.code}"
        except Exception as e:
            return f"__ERROR__:{e}"

    def post_json(self, path, payload):
        t = self.post(path, payload)
        if t in ("3", "", "-1"):
            return t
        if t.startswith("__"):
            return {"error": t}
        try:
            return json.loads(t)
        except Exception:
            return t

    def login(self, name, otp):
        r = self.post("/Head.php", {"fu": "login", "n": name, "p": otp})
        if r == "1":
            self.user = name
            self._save_cookies()
            return True, L("success_loading")
        return False, {"0": "Wrong Username/OTP", "ban": "Blocked", "banned": "Banned",
                       "-1": "Server Error"}.get(r, "Unknown Error")

    def whoami(self):
        r = self.post("/Head.php", {"fu": "load"})
        if r in ("3", ""):
            log("Session expired, retrying...")
            r = self.post("/Head.php", {"fu": "load"})
        return None if r in ("3", "") else r

    def logout(self):
        try:
            self.post("/Head.php", {"fu": "account_logout"})
        except Exception:
            pass
        self.jar.clear()
        if os.path.exists(SESSION_FILE):
            try:
                os.remove(SESSION_FILE)
            except Exception:
                pass
        self.user = None
        self.ally = None
        self.roleid = None
        self.memberid = None

    def ally_status(self): return self.post_json("/post/Ally.php", {"fu": "status"})
    def ally_members(self): return self.post_json("/post/Ally.php", {"fu": "members"})
    def ally_leave(self): return self.post("/post/Ally.php", {"fu": "leave_ally"})
    def ally_requests(self, rtype="new"): return self.post_json("/post/Ally.php", {"fu": "get_requests", "type": rtype, "offset": None})
    def ally_handle_request(self, req_id, mode): return self.post("/post/Ally.php", {"fu": "handle_request", "request": req_id, "mode": mode})
    def ally_change_role(self, member_id, roleid): return self.post("/post/Ally.php", {"fu": "change_role", "id": member_id, "roleid": roleid})
    def ally_change_title(self, member_id, title, color): return self.post("/post/Ally.php", {"fu": "change_title", "id": member_id, "title": title, "color": color})
    def ally_mute(self, target, typ): return self.post("/post/Ally.php", {"fu": "mute_unmute", "target": target, "type": typ})
    def ally_kick(self, member_id): return self.post("/post/Ally.php", {"fu": "delete_member", "id": member_id})
    def ally_settings(self): return self.post_json("/post/Ally.php", {"fu": "settings"})
    def ally_save_setting(self, key, val): return self.post_json("/post/Ally.php", {"fu": "settings", "key": key, "val": val})
    def ally_capacity(self): return self.post("/post/Ally.php", {"fu": "capacity"})
    def ally_chat_history(self, offset=None): return self.post_json("/post/Ally.php", {"fu": "chat_history", "offset": offset})
    def ally_chat_send(self, text): return self.post("/post/Ally.php", {"fu": "chat_send", "chat": text})
    def ally_ranking(self, date=None): return self.post_json("/post/Ally.php", {"fu": "ranking_info", "date": date})
    def ally_vault_status(self): return self.post_json("/post/Ally.php", {"fu": "vault_status"})
    def ally_vault_add(self, amount): return self.post("/post/Ally.php", {"fu": "vault_add", "amount": amount})
    def ally_vault_clear(self, typ): return self.post("/post/Ally.php", {"fu": "vault_clear", "type": typ})
    def ally_vault_news(self, offset=None): return self.post_json("/post/Ally.php", {"fu": "vault_news", "offset": offset})
    def ally_vault_shares(self, trans_id): return self.post_json("/post/Ally.php", {"fu": "vault_shares", "id": trans_id})
    def ally_enrol(self): return self.post_json("/post/Ally.php", {"fu": "enrol_settings"})
    def ally_set_enrol(self, key, val): return self.post_json("/post/Ally.php", {"fu": "enrol_settings", "key": key, "val": val})
    def ally_news(self, offset=None): return self.post_json("/post/Ally.php", {"fu": "news", "offset": offset})
    def create_status(self): return self.post_json("/post/AllyCreate.php", {"fu": "status"})
    def create_ally(self, name, confirm=0): return self.post_json("/post/AllyCreate.php", {"fu": "create", "name": name, "confirm": confirm})
    def list_allies(self, search="", order="rank"): return self.post_json("/post/AllyList.php", {"fu": "get_allys", "offset": None, "order": order, "search": search, "filter": "[]"})
    def join_ally(self, ally_id): return self.post("/post/AllyList.php", {"fu": "join_ally", "ally": ally_id})


class Network:
    @classmethod
    def fetch(cls, api, method_name, args=(), callback=None):
        def worker():
            try:
                result = getattr(api, method_name)(*args)
            except Exception as e:
                result = {"error": str(e)}
            if callback:
                try:
                    bui.pushcall(MyCall(callback, result), from_other_thread=True)
                except Exception as e:
                    log(f"Pushcall error: {e}")
        threading.Thread(target=worker, daemon=True).start()


# ═══════════════════════════════════════════════════════════════
# SKIN  (rounded cards, themes, FX — from the BetterParty style)
# ═══════════════════════════════════════════════════════════════

THEMES: Dict[str, Dict[str, Any]] = {
    'Aurora': dict(a=(0.16, 0.38, 0.92), b=(0.16, 0.75, 0.35), mode='wave', tex=('circleSoft', 'star'), dir=1),
    'Neon Pink': dict(a=(1.0, 0.12, 0.62), b=(0.55, 0.15, 1.0), mode='wave', tex=('heart', 'star', 'circleSoft'), dir=1),
    'Lava': dict(a=(1.0, 0.28, 0.05), b=(0.75, 0.05, 0.12), mode='wave', tex=('star', 'circleSoft'), dir=1),
    'Ocean': dict(a=(0.05, 0.40, 0.95), b=(0.02, 0.78, 0.80), mode='wave', tex=('circleOutline', 'circleSoft'), dir=1),
    'Toxic': dict(a=(0.25, 0.95, 0.12), b=(0.75, 0.90, 0.10), mode='wave', tex=('circleSoft', 'star'), dir=1),
    'Galaxy': dict(a=(0.40, 0.10, 0.85), b=(0.08, 0.15, 0.55), mode='wave', tex=('star', 'star', 'circleSoft'), dir=1),
    'Candy': dict(a=(1.0, 0.55, 0.80), b=(0.50, 0.80, 1.0), mode='wave', tex=('heart', 'circleSoft'), dir=1),
    'Gold Rush': dict(a=(1.0, 0.78, 0.12), b=(0.95, 0.45, 0.05), mode='wave', tex=('star', 'circleSoft'), dir=1),
    'Frost': dict(a=(0.55, 0.85, 1.0), b=(0.85, 0.93, 1.0), mode='wave', tex=('circleSoft', 'star'), dir=-1),
    'Sunset': dict(a=(1.0, 0.35, 0.25), b=(0.65, 0.20, 0.90), mode='wave', tex=('circleSoft', 'star'), dir=1),
    'Matrix': dict(a=(0.05, 0.80, 0.25), b=(0.0, 0.45, 0.15), mode='wave', tex=('circleSoft',), dir=-1),
    'Midnight': dict(a=(0.08, 0.10, 0.30), b=(0.22, 0.12, 0.48), mode='wave', tex=('star', 'circleSoft'), dir=1),
    'Rainbow': dict(a=(1.0, 0.2, 0.2), b=(0.2, 0.2, 1.0), mode='rainbow', tex=('star', 'heart', 'circleSoft'), dir=1),
}
THEME_ORDER = list(THEMES.keys())


def _get_theme(name: str) -> Dict[str, Any]:
    th = THEMES.get(name)
    if th is not None:
        return th
    a, b = THEMES['Aurora']['a'], THEMES['Aurora']['b']
    try:
        saved = babase.app.config.get('PartyWindow_Wave_Colors')
        if (isinstance(saved, (list, tuple)) and len(saved) == 2
                and all(isinstance(c, (list, tuple)) and len(c) == 3 for c in saved)):
            a = tuple(float(x) for x in saved[0])
            b = tuple(float(x) for x in saved[1])
    except Exception:
        pass
    return dict(a=a, b=b, mode='wave', tex=('star', 'circleSoft'), dir=1)


def _theme_rgb(theme, elapsed: float, speed: float = 1.0):
    period = 4.0 / max(0.25, speed)
    if theme.get('mode') == 'rainbow':
        h = (elapsed / (period * 2.5)) % 1.0
        s, v = 0.80, 0.95
    else:
        phase = (elapsed % period) / period
        t = (1 - math.cos(phase * 2 * math.pi)) / 2
        h_a, s_a, v_a = colorsys.rgb_to_hsv(*theme['a'])
        h_b, s_b, v_b = colorsys.rgb_to_hsv(*theme['b'])
        dh = h_b - h_a
        if dh > 0.5:
            dh -= 1.0
        elif dh < -0.5:
            dh += 1.0
        h = (h_a + dh * t) % 1.0
        s = s_a + (s_b - s_a) * t
        v = v_a + (v_b - v_a) * t
    v = min(1.0, v * (0.94 + 0.06 * math.sin(elapsed * 2.3)))
    return colorsys.hsv_to_rgb(h, s, v)


def _accent(rgb, sat: float = 0.55, val: float = 0.88):
    h, s, _v = colorsys.rgb_to_hsv(*rgb)
    return colorsys.hsv_to_rgb(h, min(1.0, 0.25 + s * sat), val)


def _light(rgb, k: float = 0.5):
    h, s, _v = colorsys.rgb_to_hsv(*rgb)
    return colorsys.hsv_to_rgb(h, s * k, 1.0)


def _hsv(h: float, s: float, v: float):
    return colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))


def _palette(rgb) -> Dict[str, Any]:
    h, s, _v = colorsys.rgb_to_hsv(*rgb)
    s = min(1.0, 0.15 + s * 0.8)
    return dict(
        body=_hsv(h, s * 0.9, 0.13), card=_hsv(h, s * 0.8, 0.21),
        head=_hsv(h, s * 0.8, 0.29), field=_hsv(h, s * 0.8, 0.10),
        edge=_hsv(h, s * 0.65, 0.72), edge_dim=_hsv(h, s * 0.65, 0.46),
        accent=_accent(rgb), light=_light(rgb, 0.45), text=_light(rgb, 0.16))


def _kind_colors(pal):
    return {'body': (pal['body'], pal['edge']), 'card': (pal['card'], pal['edge_dim']),
            'head': (pal['head'], pal['edge']), 'field': (pal['field'], pal['edge_dim'])}


def _join_color(rgb):
    h, s, _v = colorsys.rgb_to_hsv(*rgb)
    return _hsv(h, 0.35 + s * 0.7, 1.0)


def _danger_color(rgb):
    h, s, _v = colorsys.rgb_to_hsv(*rgb)
    return _hsv(h, 0.3 + s * 0.5, 0.58)


class _RRect:
    def __init__(self, parent, x, y, w, h, r, color=(1, 1, 1)) -> None:
        r = max(1.0, min(r, w / 2.0, h / 2.0))
        white = bui.gettexture('white')
        disc = bui.gettexture('circle')
        self.parts: List[Any] = []

        def add(px, py, pw, ph, tex):
            self.parts.append(bui.imagewidget(
                parent=parent, position=(px, py), size=(pw, ph),
                texture=tex, color=color, opacity=1.0))

        add(x + r, y, w - 2 * r, h, white)
        add(x, y + r, r, h - 2 * r, white)
        add(x + w - r, y + r, r, h - 2 * r, white)
        tile = 2 * r / 0.97
        for cx, cy in ((x + r, y + r), (x + w - r, y + r), (x + r, y + h - r), (x + w - r, y + h - r)):
            add(cx - tile / 2, cy - tile / 2, tile, tile, disc)

    def recolor(self, rgb) -> None:
        for p in self.parts:
            bui.imagewidget(edit=p, color=rgb)


class _Card:
    def __init__(self, parent, x, y, w, h, r, bw: float = 1.6) -> None:
        self.edge = _RRect(parent, x, y, w, h, r)
        self.fill = _RRect(parent, x + bw, y + bw, w - 2 * bw, h - 2 * bw, max(1.0, r - bw))

    def recolor(self, edge, fill) -> None:
        self.edge.recolor(edge)
        self.fill.recolor(fill)


def _rounded_rim(w, h, radius, inset, spacing=18.0):
    rr = max(2.0, radius - inset)
    x0, x1, y0, y1 = inset, w - inset, inset, h - inset
    lh = (x1 - x0) - 2 * rr
    lv = (y1 - y0) - 2 * rr
    arc = math.pi * rr / 2
    total = 2 * lh + 2 * lv + 4 * arc
    n = max(24, int(round(total / spacing)))
    pts = []
    for k in range(n):
        d = total * k / n
        if d < lh:
            p = (x0 + rr + d, y0)
        else:
            d -= lh
            if d < arc:
                a = -math.pi / 2 + d / rr
                p = (x1 - rr + rr * math.cos(a), y0 + rr + rr * math.sin(a))
            else:
                d -= arc
                if d < lv:
                    p = (x1, y0 + rr + d)
                else:
                    d -= lv
                    if d < arc:
                        a = d / rr
                        p = (x1 - rr + rr * math.cos(a), y1 - rr + rr * math.sin(a))
                    else:
                        d -= arc
                        if d < lh:
                            p = (x1 - rr - d, y1)
                        else:
                            d -= lh
                            if d < arc:
                                a = math.pi / 2 + d / rr
                                p = (x0 + rr + rr * math.cos(a), y1 - rr + rr * math.sin(a))
                            else:
                                d -= arc
                                if d < lv:
                                    p = (x0, y1 - rr - d)
                                else:
                                    d -= lv
                                    a = math.pi + d / rr
                                    p = (x0 + rr + rr * math.cos(a), y0 + rr + rr * math.sin(a))
        pts.append((p[0] / w, p[1] / h))
    return pts


class _FXLayer:
    N_PART = 14
    N_ORB = 5
    N_TWINKLE = 16
    N_RING = 3
    N_BURST = 14
    TAIL = 0.20

    def __init__(self, root, width, height, level, theme, halos=None, rim=None) -> None:
        self._w = float(width)
        self._h = float(height)
        self._level = level
        self._theme = theme
        self._n = 0
        self._rnd = random.Random()
        self._last_pulse = -9.0
        w, h = self._w, self._h
        rnd = random.Random(7)
        soft = bui.gettexture('circleSoft')
        star = bui.gettexture('star')

        def img(tex, size=(10, 10)):
            return bui.imagewidget(parent=root, position=(0, 0), size=size, texture=tex,
                                   color=(1, 1, 1), opacity=0.0)

        self._orbs: List[Dict[str, Any]] = []
        for i in range(self.N_ORB):
            self._orbs.append(dict(
                x=rnd.uniform(0.15, 0.85) * w, y=rnd.uniform(0.2, 0.8) * h,
                r=rnd.uniform(50, 100), fx=rnd.uniform(0.12, 0.3),
                fy=rnd.uniform(0.1, 0.25), ph=rnd.uniform(0, 6.28), w=img(soft)))
        self._twk: List[Dict[str, Any]] = []
        for i in range(self.N_TWINKLE):
            self._twk.append(dict(
                x=rnd.uniform(0.06, 0.94) * w, y=rnd.uniform(0.08, 0.92) * h,
                s=rnd.uniform(5, 10), f=rnd.uniform(0.6, 1.8),
                ph=rnd.uniform(0, 6.28), op=-1.0, w=img(star)))

        self._glow = bui.imagewidget(
            parent=root, position=(w * 0.12, h - 80), size=(w * 0.76, 90),
            texture=soft, color=(1, 1, 1), opacity=0.0)
        self._shine = bui.imagewidget(
            parent=root, position=(-80, 6), size=(46, h - 12),
            texture=bui.gettexture('softRectVertical'), color=(1, 1, 1), opacity=0.0)
        self._tshine = bui.imagewidget(
            parent=root, position=(-80, h - 62), size=(30, 46),
            texture=bui.gettexture('softRectVertical'), color=(1, 1, 1), opacity=0.0)
        self._tshine_on = False

        self._halos: List[Dict[str, Any]] = []
        for cx, cy, sz in (halos or []):
            self._halos.append(dict(x=cx, y=cy, s=sz, w=img(soft, (sz, sz))))

        self._dots: List[Dict[str, Any]] = []
        for i, (u, v) in enumerate(rim or []):
            x, y = u * w, v * h
            bloom = None
            if i % 2 == 0:
                bloom = bui.imagewidget(
                    parent=root, position=(x - 9, y - 9), size=(18, 18),
                    texture=soft, color=(1, 1, 1), opacity=0.0)
            self._dots.append(dict(x=x, y=y, op=-1.0, bloom=bloom, w=None))
        for d in self._dots:
            d['w'] = bui.imagewidget(
                parent=root, position=(d['x'] - 3, d['y'] - 3), size=(6, 6),
                texture=soft, color=(1, 1, 1), opacity=0.0)

        self._parts: List[Dict[str, Any]] = []
        for i in range(self.N_PART):
            self._parts.append(dict(
                x=rnd.uniform(0.07, 0.93) * w, speed=rnd.uniform(0.035, 0.10), off=rnd.random(),
                amp=rnd.uniform(4, 18), freq=rnd.uniform(0.6, 1.8), ph=rnd.uniform(0, 6.28),
                size=rnd.uniform(9, 22), maxop=rnd.uniform(0.35, 0.8), tex_i=i, w=img(soft, (12, 12))))

        self._shoot_w = [img(star, (14, 14)), img(soft, (10, 10)), img(soft, (8, 8)), img(soft, (6, 6))]
        self._shoot: Optional[Dict[str, float]] = None
        self._next_shoot = 3.0

        self._rings = [dict(t0=None, x=0.0, y=0.0,
                            w=bui.imagewidget(parent=root, position=(0, 0), size=(20, 20),
                                              texture=bui.gettexture('circleOutline'),
                                              color=(1, 1, 1), opacity=0.0))
                       for _ in range(self.N_RING)]
        self._bursts = [dict(t0=None, x=0.0, y=0.0, vx=0.0, vy=0.0, col=(1, 1, 1),
                             w=img(star if i % 2 else soft, (12, 12)))
                        for i in range(self.N_BURST)]
        self.set_theme(theme)
        self.set_level(level)

    def set_theme(self, theme) -> None:
        self._theme = theme
        texs = theme.get('tex') or ('circleSoft',)
        for p in self._parts:
            try:
                bui.imagewidget(edit=p['w'], texture=bui.gettexture(texs[p['tex_i'] % len(texs)]))
            except Exception:
                pass

    def _hi_widgets(self):
        wl = [o['w'] for o in self._orbs] + [t['w'] for t in self._twk]
        wl += [hh['w'] for hh in self._halos] + list(self._shoot_w)
        wl += [d['bloom'] for d in self._dots if d['bloom'] is not None]
        wl.append(self._tshine)
        return wl

    def _active_count(self) -> int:
        return 0 if self._level <= 0 else (6 if self._level == 1 else self.N_PART)

    def set_level(self, level: int) -> None:
        self._level = level
        hide = []
        if level <= 0:
            hide += self._hi_widgets() + [self._glow, self._shine]
            hide += [p['w'] for p in self._parts] + [d['w'] for d in self._dots]
            hide += [r['w'] for r in self._rings] + [b['w'] for b in self._bursts]
            self._shoot = None
            for r in self._rings:
                r['t0'] = None
            for b in self._bursts:
                b['t0'] = None
        else:
            if level < 2:
                hide += self._hi_widgets()
                self._shoot = None
                self._tshine_on = False
                for b in self._bursts:
                    b['t0'] = None
                hide += [b['w'] for b in self._bursts]
            hide += [p['w'] for p in self._parts[self._active_count():]]
        for d in self._dots:
            d['op'] = -1.0
        for t in self._twk:
            t['op'] = -1.0
        for wd in hide:
            try:
                bui.imagewidget(edit=wd, opacity=0.0)
            except Exception:
                pass

    def pulse(self, x=None, y=None) -> None:
        if self._level <= 0:
            return
        now = time.time() - _FX_T0
        if now - self._last_pulse < 0.35:
            return
        self._last_pulse = now
        ring = min(self._rings, key=lambda r: -1.0 if r['t0'] is None else r['t0'])
        ring.update(t0=now, x=self._w / 2 if x is None else x, y=self._h / 2 if y is None else y)

    def burst(self, x=None, y=None) -> None:
        if self._level < 2:
            return
        now = time.time() - _FX_T0
        cx = self._w / 2 if x is None else x
        cy = self._h * 0.6 if y is None else y
        rnd = self._rnd
        for b in self._bursts:
            a = rnd.uniform(0, 6.283)
            sp = rnd.uniform(70, 200)
            b.update(t0=now, x=cx, y=cy, vx=math.cos(a) * sp, vy=math.sin(a) * sp,
                     col=colorsys.hsv_to_rgb(rnd.random(), 0.55, 1.0))

    def tick(self, elapsed: float, rgb, speed: float) -> None:
        if self._level <= 0:
            return
        self._n += 1
        n = self._n
        w, h = self._w, self._h
        hi = self._level >= 2
        light = _light(rgb, 0.45)
        pulse = (1 + math.sin(elapsed * 1.6 * speed)) / 2

        bui.imagewidget(edit=self._glow, color=light, opacity=0.12 + 0.22 * pulse)
        sx = ((elapsed * 0.13 * speed) % 1.6 - 0.3) * w
        bui.imagewidget(edit=self._shine, position=(sx, 6), opacity=0.07)

        if n % (2 if hi else 3) == 0:
            cnt = len(self._dots)
            base = 0.30 + 0.10 * pulse
            h1 = (elapsed * 0.10 * speed) % 1.0
            h2 = (h1 + 0.5) % 1.0
            recolor = (n % 12 == 0)
            for i, d in enumerate(self._dots):
                t = i / cnt
                k = 0.0
                for head in (h1, h2):
                    dist = (head - t) % 1.0
                    if dist < self.TAIL:
                        k = max(k, (1.0 - dist / self.TAIL) ** 1.6)
                op = base + (0.98 - base) * k
                if k > 0.0 or abs(op - d['op']) > 0.02 or recolor:
                    sz = 6.0 + 5.0 * k
                    col = tuple(c + (1.0 - c) * 0.75 * k for c in light)
                    bui.imagewidget(edit=d['w'], position=(d['x'] - sz / 2, d['y'] - sz / 2),
                                    size=(sz, sz), color=col, opacity=op)
                    if hi and d['bloom'] is not None:
                        bs_ = 16.0 + 16.0 * k
                        bui.imagewidget(edit=d['bloom'],
                                        position=(d['x'] - bs_ / 2, d['y'] - bs_ / 2),
                                        size=(bs_, bs_), color=light, opacity=0.05 + 0.30 * k)
                    d['op'] = op

        direction = self._theme.get('dir', 1)
        span = h - 2 * 17 - 20
        for p in self._parts[:self._active_count()]:
            prog = (p['off'] + elapsed * p['speed'] * speed) % 1.0
            if direction < 0:
                prog = 1.0 - prog
            sz = p['size'] * (0.75 + 0.25 * math.sin(elapsed * 2 + p['ph']))
            x = p['x'] + math.sin(elapsed * p['freq'] + p['ph']) * p['amp']
            y = 17 + 10 + prog * span
            op = math.sin(math.pi * min(1.0, max(0.0, prog))) * p['maxop']
            bui.imagewidget(edit=p['w'], position=(x - sz / 2, y - sz / 2),
                            size=(sz, sz), opacity=op, color=light)

        for r in self._rings:
            if r['t0'] is None:
                continue
            age = elapsed - r['t0']
            if age >= 1.2:
                r['t0'] = None
                bui.imagewidget(edit=r['w'], opacity=0.0)
                continue
            f = age / 1.2
            sz = 30 + f * max(w, h) * 0.95
            bui.imagewidget(edit=r['w'], position=(r['x'] - sz / 2, r['y'] - sz / 2),
                            size=(sz, sz), color=light, opacity=0.65 * (1 - f) ** 1.5)

        if not hi:
            return

        if n % 2 == 0:
            for i, o in enumerate(self._orbs):
                x = o['x'] + math.sin(elapsed * o['fx'] + o['ph']) * 45
                y = o['y'] + math.cos(elapsed * o['fy'] + o['ph']) * 30
                sz = o['r'] * (1 + 0.08 * math.sin(elapsed * 0.9 + o['ph']))
                hh, ss, _vv = colorsys.rgb_to_hsv(*light)
                col = colorsys.hsv_to_rgb((hh + 0.07 * i) % 1.0, min(1.0, ss + 0.3), 1.0)
                bui.imagewidget(edit=o['w'], position=(x - sz / 2, y - sz / 2), size=(sz, sz),
                                color=col,
                                opacity=0.05 + 0.05 * (1 + math.sin(elapsed * 0.6 + o['ph'])) / 2)
            for t in self._twk:
                k = max(0.0, math.sin(elapsed * t['f'] + t['ph'])) ** 3
                op = 0.05 + 0.75 * k
                if abs(op - t['op']) > 0.04:
                    sz = t['s'] * (0.7 + 0.5 * k)
                    bui.imagewidget(edit=t['w'], position=(t['x'] - sz / 2, t['y'] - sz / 2),
                                    size=(sz, sz), color=light, opacity=op)
                    t['op'] = op

        for i, hl in enumerate(self._halos):
            ph = math.sin(elapsed * 2.2 * speed + i * 1.3)
            sz = hl['s'] * (1 + 0.10 * ph)
            bui.imagewidget(edit=hl['w'], position=(hl['x'] - sz / 2, hl['y'] - sz / 2),
                            size=(sz, sz), color=light, opacity=0.10 + 0.14 * (1 + ph) / 2)

        cyc = ((elapsed * speed) % 7.0) / 7.0
        if cyc < 0.22:
            f = cyc / 0.22
            bui.imagewidget(edit=self._tshine, position=(w * 0.2 + f * w * 0.6, h - 62),
                            color=(1, 1, 1), opacity=0.30 * math.sin(math.pi * f))
            self._tshine_on = True
        elif self._tshine_on:
            bui.imagewidget(edit=self._tshine, opacity=0.0)
            self._tshine_on = False

        sh = self._shoot
        if sh is None:
            if elapsed >= self._next_shoot:
                rn = self._rnd
                self._shoot = dict(t0=elapsed, x=rn.uniform(0.08, 0.5) * w, y=rn.uniform(0.7, 0.95) * h,
                                   vx=rn.uniform(260, 340), vy=-rn.uniform(120, 190))
        else:
            age = elapsed - sh['t0']
            if age > 1.0:
                for wd in self._shoot_w:
                    bui.imagewidget(edit=wd, opacity=0.0)
                self._shoot = None
                self._next_shoot = elapsed + self._rnd.uniform(5.0, 10.0)
            else:
                for j, wd in enumerate(self._shoot_w):
                    a = age - 0.05 * j
                    if a < 0:
                        continue
                    x = sh['x'] + sh['vx'] * a
                    y = sh['y'] + sh['vy'] * a
                    sz = (14, 10, 8, 6)[j]
                    bui.imagewidget(edit=wd, position=(x - sz / 2, y - sz / 2), color=light,
                                    opacity=(1 - age) * (0.95, 0.55, 0.35, 0.2)[j])

        for b in self._bursts:
            if b['t0'] is None:
                continue
            age = elapsed - b['t0']
            if age >= 1.1:
                b['t0'] = None
                bui.imagewidget(edit=b['w'], opacity=0.0)
                continue
            x = b['x'] + b['vx'] * age
            y = b['y'] + b['vy'] * age - 70.0 * age * age
            sz = 16 * (1 - 0.4 * age / 1.1)
            bui.imagewidget(edit=b['w'], position=(x - sz / 2, y - sz / 2), size=(sz, sz),
                            color=b['col'], opacity=0.9 * (1 - age / 1.1) ** 1.2)


class _Skin:
    def __init__(self, root, w, h, theme, level, cards, halos=None, radius=18.0) -> None:
        self._items: List[Tuple[_Card, str]] = []
        self._items.append((_Card(root, 0, 0, w, h, radius, bw=2.0), 'body'))
        for x, y, cw, ch, r, kind in cards:
            self._items.append((_Card(root, x, y, cw, ch, r), kind))
        self.fx = _FXLayer(root, w, h, level, theme, halos, rim=_rounded_rim(w, h, radius, 5.0))
        self.pal: Dict[str, Any] = _palette(theme['a'])
        self.recolor(theme['a'])

    def recolor(self, rgb) -> None:
        pal = _palette(rgb)
        self.pal = pal
        kinds = _kind_colors(pal)
        for card, kind in self._items:
            fill, edge = kinds[kind]
            card.recolor(edge, fill)


def _scale() -> float:
    ui = bui.app.ui_v1.uiscale
    return 1.7 if ui is bui.UIScale.SMALL else 1.3 if ui is bui.UIScale.MEDIUM else 1.0


def _win_h() -> int:
    ui = bui.app.ui_v1.uiscale
    return 360 if ui is bui.UIScale.SMALL else 440 if ui is bui.UIScale.MEDIUM else 520


# ═══════════════════════════════════════════════════════════════
# BASE WINDOW
# ═══════════════════════════════════════════════════════════════

_top: Any = None          # the currently open top-level window (login / main / hub)
_api: Any = None
_is_opening = False
_NOSEL = object()


class _Win:
    FX = False

    def __init__(self, W, H, cards, halos=None, outside=False) -> None:
        cfg = babase.app.config
        self.W, self.H = W, H
        self.theme_name = cfg.get(_CFG_THEME, 'Aurora')
        self.theme = _get_theme(self.theme_name)
        self.speed = float(cfg.get(_CFG_SPEED, 1.0))
        lvl = cfg.get(_CFG_FX, 2)
        lvl = lvl if lvl in (0, 1, 2) else 2
        self._btns: List[List[Any]] = []
        self._dcards: List[Tuple[_Card, str]] = []
        self._blend_from: Any = None
        self._blend_t0 = 0.0
        self._n = 0
        ui = bui.app.ui_v1.uiscale
        kw = dict(size=(W, H), transition='in_scale',
                  parent=bui.get_special_widget('overlay_stack'),
                  scale=_scale(), background=False,
                  stack_offset=(0, -10) if ui is bui.UIScale.SMALL else (0, 0))
        if outside:
            kw['on_outside_click_call'] = self.close_sound
        self.root = bui.containerwidget(**kw)
        self.color = _theme_rgb(self.theme, time.time() - _FX_T0, self.speed)
        self.skin = None
        self.fx = None
        self._cards: List[Tuple[_Card, str]] = []
        if self.FX:
            self.skin = _Skin(self.root, W, H, self.theme, lvl, cards, halos)
            self.fx = self.skin.fx
        else:
            self._cards.append((_Card(self.root, 0, 0, W, H, 16, bw=2.0), 'body'))
            for x, y, cw, ch, r, kind in cards:
                self._cards.append((_Card(self.root, x, y, cw, ch, r), kind))
        self.pal = _palette(self.color)
        self._paint(self.color)
        self._timer: Any = bui.AppTimer(
            0.05 if self.FX else 0.2, bui.WeakCallStrict(self._tick), repeat=True)

    # ─── painting ───
    def _paint(self, rgb) -> None:
        if self.skin is not None:
            self.skin.recolor(rgb)
            self.pal = self.skin.pal
        else:
            self.pal = _palette(rgb)
            kinds = _kind_colors(self.pal)
            for card, kind in self._cards:
                fill, edge = kinds[kind]
                card.recolor(edge, fill)
        kinds = _kind_colors(self.pal)
        keep = []
        for card, kind in self._dcards:
            try:
                fill, edge = kinds[kind]
                card.recolor(edge, fill)
                keep.append((card, kind))
            except Exception:
                pass
        self._dcards = keep

    def _kcol(self, kind, rgb):
        pal = self.pal
        if kind == 'join':
            return _join_color(rgb), (1, 1, 1)
        if kind == 'danger':
            return _danger_color(rgb), pal['text']
        return pal['accent'], pal['text']

    def _accents(self, rgb) -> None:
        keep = []
        for e in self._btns:
            try:
                c, t = self._kcol(e[1], rgb)
                bui.buttonwidget(edit=e[0], color=c, textcolor=t)
                keep.append(e)
            except Exception:
                pass
        self._btns = keep

    def on_tick(self, el: float) -> None:
        t = getattr(self, 'title', None)
        if t is not None:
            try:
                bui.textwidget(edit=t, color=_light(self.color, 0.3), scale=0.95 + 0.03 * math.sin(el * 2.2))
            except Exception:
                pass

    def _tick(self) -> None:
        try:
            if not self.root.exists():
                self._timer = None
                return
            el = time.time() - _FX_T0
            color = _theme_rgb(self.theme, el, self.speed)
            bf = self._blend_from
            if bf is not None:
                k = (time.time() - self._blend_t0) / 1.2
                if k >= 1.0:
                    self._blend_from = None
                else:
                    k = k * k * (3 - 2 * k)
                    color = tuple(bf[i] + (color[i] - bf[i]) * k for i in range(3))
            self.color = color
            self._n += 1
            if self.fx is not None:
                self.fx.tick(el, color, self.speed)
            if self._n % 4 == 0 or not self.FX:
                self._paint(color)
            if self._n % 3 == 0 or not self.FX:
                self._accents(color)
                self.on_tick(el)
        except Exception:
            pass

    # ─── widget helpers ───
    def btn(self, parent, pos, size, label, call, kind='accent', ts=0.8, key=None, **kw):
        c, t = self._kcol(kind, self.color)
        b = bui.buttonwidget(parent=parent, position=pos, size=size, label=label,
                             button_type='square', autoselect=True, color=c, textcolor=t,
                             text_scale=ts, on_activate_call=call, **kw)
        self._btns.append([b, kind, key])
        return b

    def setkind(self, key, kind) -> None:
        for e in self._btns:
            if e[2] == key:
                e[1] = kind

    def lbl(self, parent, pos, text, scale=0.7, color=TXT, h='left', maxwidth=None, v='center'):
        kw = dict(parent=parent, position=pos, size=(0, 0), text=str(text) if text is not None else '',
                  scale=scale, color=color, h_align=h, v_align=v)
        if maxwidth:
            kw['maxwidth'] = maxwidth
        return bui.textwidget(**kw)

    def field(self, parent, pos, size, text='', max_chars=60, desc=''):
        x, y = pos
        w, h = size
        card = _Card(parent, x, y, w, h, 8)
        self._dcards.append((card, 'field'))
        fill, edge = _kind_colors(self.pal)['field']
        card.recolor(edge, fill)
        return bui.textwidget(parent=parent, position=(x + 8, y), size=(w - 16, h), editable=True,
                              text=str(text if text is not None else ''), autoselect=True,
                              h_align='left', v_align='center', maxwidth=w - 24, max_chars=max_chars,
                              description=desc, shadow=0.3, flatness=1.0, color=(1, 1, 1))

    def bar(self, parent, x, y, w, h, me=False):
        return bui.imagewidget(parent=parent, position=(x, y), size=(w, h), texture=bui.gettexture('white'),
                               color=(1, 1, 1) if me else (0, 0, 0), opacity=0.14 if me else 0.30)

    def scroll(self, parent, pos, size, n, row_h):
        sc = bui.scrollwidget(parent=parent, position=pos, size=size, color=(0.4, 0.6, 0.3), border_opacity=0.0)
        hh = max(n * row_h + 6, size[1])
        cont = bui.containerwidget(parent=sc, size=(size[0] - 12, hh), background=False)
        return sc, cont, hh

    # ─── style cycling (shared with BetterParty config) ───
    def cycle_style(self) -> None:
        cfg = babase.app.config
        cur = self.theme_name
        i = (THEME_ORDER.index(cur) + 1) % len(THEME_ORDER) if cur in THEME_ORDER else 0
        name = THEME_ORDER[i]
        self._blend_from = self.color
        self._blend_t0 = time.time()
        self.theme_name = name
        self.theme = _get_theme(name)
        cfg[_CFG_THEME] = name
        try:
            cfg.commit()
        except Exception:
            pass
        if self.fx is not None:
            self.fx.set_theme(self.theme)
            self.fx.pulse()
            self.fx.burst()
        bui.getsound('ding').play()
        bui.screenmessage(f"{L('theme')}: {name}", color=_accent(self.color))

    def close(self) -> None:
        global _top
        if _top is self:
            _top = None
        try:
            if self.root and not self.root.transitioning_out:
                bui.containerwidget(edit=self.root, transition='out_scale')
        except Exception:
            pass
        self._timer = None

    def close_sound(self) -> None:
        try:
            bui.getsound('swish').play()
        except Exception:
            pass
        self.close()


class _Dialog(_Win):
    def __init__(self, W, H, title, extra=(), tcolor=None, outside=False) -> None:
        cards = [(12, H - 58, W - 24, 46, 12, 'head')] + list(extra)
        super().__init__(W, H, cards, outside=outside)
        self._tcolor = tcolor
        self.title = bui.textwidget(parent=self.root, position=(W / 2 + 14, H - 35), size=(0, 0), scale=0.95,
                                    text=str(title), maxwidth=W - 130, h_align='center', v_align='center',
                                    color=tcolor or TXT)
        self.close_btn = self.btn(self.root, (18, H - 52), (38, 38), bui.charstr(bui.SpecialChar.CLOSE),
                                  self.close_sound, ts=0.9)
        bui.containerwidget(edit=self.root, cancel_button=self.close_btn)

    def on_tick(self, el):
        if self._tcolor is None:
            super().on_tick(el)


def _later(delay, call):
    try:
        bui.apptimer(delay, call)
    except Exception:
        call()


# ═══════════════════════════════════════════════════════════════
# DIALOGS
# ═══════════════════════════════════════════════════════════════

class Popup(_Dialog):
    def __init__(self, title, text, on_ok=None, kind="info"):
        self._on_ok = on_ok
        col = GREEN if kind == "success" else RED if kind == "error" else GOLD
        W = 380
        lines = str(text).split("\n")
        H = 150 + 20 * max(1, min(len(lines), 8))
        super().__init__(W, H, title, extra=[(12, 70, W - 24, H - 140, 12, 'card')], tcolor=col)
        y = H - 70 - 20
        for ln in lines[:8]:
            self.lbl(self.root, (W / 2, y), ln, 0.65, TXT, 'center', maxwidth=W - 50)
            y -= 20
        ok = self.btn(self.root, (W / 2 - 70, 16), (140, 40), L("ok"), self._ok, kind='join')
        bui.containerwidget(edit=self.root, start_button=ok)

    def _ok(self):
        self.close()
        if self._on_ok:
            _later(0.25, MyCall(self._on_ok))


class ConfirmDialog(_Dialog):
    def __init__(self, title, text, on_yes, danger=True):
        W, H = 400, 200
        super().__init__(W, H, title, extra=[(12, 70, W - 24, H - 140, 12, 'card')],
                         tcolor=RED if danger else GOLD)
        self._on_yes = on_yes
        self.lbl(self.root, (W / 2, H / 2 - 5), text, 0.65, TXT, 'center', maxwidth=W - 50)
        self.btn(self.root, (24, 16), (170, 40), L("yes2"), self._yes, kind='danger' if danger else 'join')
        self.btn(self.root, (W - 194, 16), (170, 40), L("no2"), self.close_sound)

    def _yes(self):
        self.close()
        _later(0.2, MyCall(self._on_yes))


class NumberInputPopup(_Dialog):
    def __init__(self, title, initial_val, on_submit):
        W, H = 380, 210
        super().__init__(W, H, title, extra=[(12, 70, W - 24, H - 140, 12, 'card')])
        self._on_submit = on_submit
        self.inp = self.field(self.root, (50, 90), (W - 100, 38), str(initial_val if initial_val is not None else ""),
                              max_chars=12, desc=title)
        self.btn(self.root, (24, 16), (160, 40), L("confirm"), self._confirm, kind='join')
        self.btn(self.root, (W - 184, 16), (160, 40), L("cancel"), self.close_sound)

    def _confirm(self):
        txt = (bui.textwidget(query=self.inp) or '').strip()
        if txt == "":
            val = None
        else:
            try:
                val = int(txt)
            except Exception:
                bui.screenmessage(L("error"), color=(1, 0.3, 0.3))
                bui.getsound('error').play()
                return
        self.close()
        _later(0.2, MyCall(self._on_submit, val))


class SelectDialog(_Dialog):
    def __init__(self, title, options, on_confirm):
        W = 380
        n = len(options)
        H = 140 + n * 46
        super().__init__(W, H, title)
        self._on = on_confirm
        self._sel = _NOSEL
        self._keys = []
        y = H - 68
        for i, (val, label) in enumerate(options):
            y -= 44
            key = f"opt{i}"
            self._keys.append((key, val))
            self.btn(self.root, (24, y), (W - 48, 38), label, MyCall(self._pick, key, val), ts=0.85, key=key)
            y -= 2
        self.btn(self.root, (24, 16), (160, 40), L("confirm"), self._confirm, kind='join')
        self.btn(self.root, (W - 184, 16), (160, 40), L("cancel"), self.close_sound)

    def _pick(self, key, val):
        self._sel = val
        for k, _v in self._keys:
            self.setkind(k, 'join' if k == key else 'accent')

    def _confirm(self):
        if self._sel is _NOSEL:
            bui.getsound('error').play()
            return
        self.close()
        _later(0.2, MyCall(self._on, self._sel))


class VaultSharesWindow(_Dialog):
    def __init__(self, api, trans_id):
        W, H = 380, 360
        super().__init__(W, H, L("vault_shares"), extra=[(12, 12, W - 24, H - 82, 12, 'card')])
        self._box = bui.containerwidget(parent=self.root, position=(20, 20), size=(W - 40, H - 98), background=False)
        self.lbl(self._box, ((W - 40) / 2, (H - 98) / 2), L("loading"), 0.7, DIM, 'center')

        def cb(shares):
            if not self.root.exists():
                return
            try:
                for c in self._box.get_children():
                    c.delete()
            except Exception:
                pass
            if not isinstance(shares, list) or not shares:
                self.lbl(self._box, ((W - 40) / 2, (H - 98) / 2), L("empty"), 0.7, DIM, 'center')
                return
            sc, cont, hh = self.scroll(self._box, (0, 0), (W - 40, H - 98), len(shares), 28)
            rw = W - 52
            y = hh
            for s in shares:
                y -= 28
                self.bar(cont, 0, y + 2, rw, 24)
                self.lbl(cont, (10, y + 14), s.get("name", "?"), 0.6, TXT, maxwidth=rw - 110)
                self.lbl(cont, (rw - 10, y + 14), fmt(s.get("val", 0)), 0.6, GREEN, 'right')
        Network.fetch(api, "ally_vault_shares", (trans_id,), callback=cb)


class VaultHistoryWindow(_Dialog):
    def __init__(self, api):
        W, H = 520, 380
        super().__init__(W, H, L("vault_news"), extra=[(12, 12, W - 24, H - 82, 12, 'card')])
        self.api = api
        self._box = bui.containerwidget(parent=self.root, position=(20, 20), size=(W - 40, H - 98), background=False)
        self.lbl(self._box, ((W - 40) / 2, (H - 98) / 2), L("loading"), 0.7, DIM, 'center')

        def cb(news):
            if not self.root.exists():
                return
            try:
                for c in self._box.get_children():
                    c.delete()
            except Exception:
                pass
            if not isinstance(news, list) or not news:
                self.lbl(self._box, ((W - 40) / 2, (H - 98) / 2), L("no_news"), 0.7, DIM, 'center')
                return
            sc, cont, hh = self.scroll(self._box, (0, 0), (W - 40, H - 98), len(news), 32)
            rw = W - 52
            y = hh
            for n in news:
                y -= 32
                self.bar(cont, 0, y + 2, rw, 28)
                self.lbl(cont, (10, y + 16), n.get("text", ""), 0.55, TXT, maxwidth=rw - 110)
                if n.get("is_parent"):
                    self.btn(cont, (rw - 92, y + 5), (84, 22), L("shares_btn"),
                             MyCall(VaultSharesWindow, api, n.get("id")), ts=0.55)
        Network.fetch(api, "ally_vault_news", (None,), callback=cb)


class MemberActionWindow(_Dialog):
    COLORS = [("white", (1, 1, 1)), ("red", (1, 0.3, 0.3)), ("blue", (0.3, 0.6, 1)),
              ("green", (0.3, 1, 0.3)), ("yellow", (1, 1, 0.2)), ("orange", (1, 0.6, 0.2))]

    def __init__(self, api, member, on_refresh):
        W, H = 400, 340
        super().__init__(W, H, f"{L('manage')}: {member.get('name', '?')}",
                         extra=[(12, 12, W - 24, H - 82, 12, 'card')])
        self.api, self.member, self.on_refresh = api, member, on_refresh
        self.color_choice = {"name": "white"}
        r = self.root
        self.lbl(r, (28, H - 100), L('title') + ":", 0.65, DIM)
        self.inp_title = self.field(r, (100, H - 118), (W - 130, 38), (member.get("title") or {}).get("t", ""),
                                    max_chars=20, desc=L('title'))
        self.lbl(r, (28, H - 152), L('color') + ":", 0.65, DIM)
        self._sw = []
        x = 100
        for cname, crgb in self.COLORS:
            b = bui.buttonwidget(parent=r, position=(x, H - 166), size=(40, 28), label="*" if cname == "white" else "",
                                 color=crgb, textcolor=(0, 0, 0), button_type="square", autoselect=True,
                                 on_activate_call=MyCall(self._pick_color, cname))
            self._sw.append((b, cname))
            x += 46
        self.btn(r, (28, H - 218), (W - 56, 36), L("apply_title"), self._apply_title, kind='join')
        self.btn(r, (28, H - 262), (W - 56, 36), L("change_role"), self._open_role_menu)
        muted = member.get("muted")
        self.btn(r, (28, 24), (160, 38), L("unmute") if muted else L("mute"), self._toggle_mute)
        self.btn(r, (W - 188, 24), (160, 38), L("kick"), self._kick, kind='danger')

    def _pick_color(self, name):
        self.color_choice["name"] = name
        for b, n in self._sw:
            try:
                bui.buttonwidget(edit=b, label="*" if n == name else "")
            except Exception:
                pass

    def _done(self, _r=None):
        self.close()
        try:
            self.on_refresh()
        except Exception:
            pass

    def _apply_title(self):
        title = (bui.textwidget(query=self.inp_title) or '').strip()
        Network.fetch(self.api, "ally_change_title", (self.member["id"], title, self.color_choice["name"]),
                      callback=self._done)

    def _open_role_menu(self):
        opts = [(2, L("general")), (3, L("spy")), (None, L("remove_role"))]

        def picked(role):
            def cb(r):
                if r == "1":
                    Popup(L("success"), L("role_changed"), kind="success", on_ok=self._done)
                else:
                    Popup(L("fail"), {"too_many": L("role_full"), "no_bot": L("no_bot")}.get(r, L("fail")),
                          kind="error")
            Network.fetch(self.api, "ally_change_role", (self.member["id"], role), callback=cb)
        SelectDialog(L("select_role"), opts, picked)

    def _toggle_mute(self):
        typ = "unmute" if self.member.get("muted") else "mute"
        Network.fetch(self.api, "ally_mute", (self.member.get("name"), typ), callback=self._done)

    def _kick(self):
        ConfirmDialog(L("kick"), f"{L('kick')}: {self.member.get('name', '?')} ?",
                      lambda: Network.fetch(self.api, "ally_kick", (self.member["id"],), callback=self._done))


# ═══════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════

class LoginWindow(_Win):
    FX = True

    def __init__(self, api, on_success):
        global _top
        W, H, P = 500, 340, 10
        hy = H - P - 54
        cards = [(P, hy, W - 2 * P, 54, 14, 'head'),
                 (P, 196, W - 2 * P, 78, 12, 'card'),
                 (130, 150, W - 150, 36, 8, 'field'),
                 (130, 106, W - 150, 36, 8, 'field')]
        super().__init__(W, H, cards, halos=[(W / 2, hy + 27, 120)])
        _top = self
        self.api, self.on_success = api, on_success
        self._busy = False
        self._status_base = ""
        r = self.root
        close = self.btn(r, (P + 6, hy + 7), (40, 40), bui.charstr(bui.SpecialChar.CLOSE), self.close_sound)
        bui.containerwidget(edit=r, cancel_button=close)
        self.title = self.lbl(r, (W / 2, hy + 37), u"\ue010 BSLIFE Ally", 0.95, GOLD, 'center', 300)
        self.lbl(r, (W / 2, hy + 15), L("login_sub"), 0.45, (0.85, 0.93, 1.0), 'center', 300)
        self.lbl(r, (W / 2, 252), L("login"), 0.8, GOLD, 'center')
        self.lbl(r, (W / 2, 228), L("login_h1"), 0.55, TXT, 'center', W - 60)
        self.lbl(r, (W / 2, 208), L("login_h2"), 0.55, TXT, 'center', W - 60)
        self.lbl(r, (116, 168), L("username") + ":", 0.65, DIM, 'right')
        self.lbl(r, (116, 124), L("otp") + ":", 0.65, DIM, 'right')
        self.inp_user = bui.textwidget(parent=r, position=(138, 150), size=(W - 166, 36), editable=True, text="",
                                       autoselect=True, h_align='left', v_align='center', max_chars=30,
                                       maxwidth=W - 174, shadow=0.3, flatness=1.0, color=(1, 1, 1),
                                       description=L("username"))
        self.inp_otp = bui.textwidget(parent=r, position=(138, 106), size=(W - 166, 36), editable=True, text="",
                                      autoselect=True, h_align='left', v_align='center', max_chars=8,
                                      maxwidth=W - 174, shadow=0.3, flatness=1.0, color=(1, 1, 1),
                                      description=L("otp"))
        self.status = self.lbl(r, (W / 2, 82), "", 0.55, DIM, 'center', W - 60)
        b = self.btn(r, (W / 2 - 160, 22), (150, 42), L("login"), self.do_login, kind='join')
        self.btn(r, (W / 2 + 10, 22), (150, 42), L("cancel"), self.close_sound)
        bui.containerwidget(edit=r, start_button=b)

    def on_tick(self, el):
        super().on_tick(el)
        if self._busy:
            self.set_status(self._status_base + "." * (int(el * 3) % 4), DIM)

    def set_status(self, text, color=DIM):
        try:
            bui.textwidget(edit=self.status, text=text, color=color)
        except Exception:
            pass

    def do_login(self):
        if self._busy:
            return
        name = (bui.textwidget(query=self.inp_user) or '').strip()
        otp = (bui.textwidget(query=self.inp_otp) or '').strip()
        if not name or not otp:
            self.set_status(L("error_fill"), RED)
            bui.getsound('error').play()
            return
        self._busy = True
        self._status_base = L("logging_in")

        def worker():
            ok, msg = self.api.login(name, otp)
            bui.pushcall(MyCall(self._login_done, ok, msg), from_other_thread=True)
        threading.Thread(target=worker, daemon=True).start()

    def _login_done(self, ok, msg):
        self._busy = False
        if not self.root.exists():
            return
        if ok:
            self.set_status(L("success_loading"), GREEN)
            if self.fx:
                self.fx.burst()
            _later(0.5, MyCall(self._go_next))
        else:
            self.set_status(f"{L('error')}: {msg}", RED)
            bui.getsound('error').play()

    def _go_next(self):
        self.close()
        _later(0.3, MyCall(self.on_success))


# ═══════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════

class AllyMainWindow(_Win):
    FX = True
    TABS = ["overview", "members", "requests", "vault", "settings", "ranking", "news", "chat", "channels"]

    def __init__(self, api):
        global _top
        W, H, P = 620, _win_h(), 10
        hy = H - P - 54
        y0 = P + 34 + 6
        y1 = hy - 8
        ch = y1 - y0
        side_w = 118
        cx = P + side_w + 8
        cw = W - P - cx
        cards = [(P, hy, W - 2 * P, 54, 14, 'head'),
                 (P, y0, side_w, ch, 12, 'card'),
                 (cx, y0, cw, ch, 12, 'card'),
                 (P, P, W - 2 * P, 34, 10, 'head')]
        super().__init__(W, H, cards, halos=[(W - 90, hy + 27, 100), (P + side_w / 2, y0 + ch / 2, 90)])
        _top = self
        self.api = api
        self.current_tab = "overview"
        self._req_filter = "new"
        self._tok = 0
        self._closing = False
        self._news: List[Any] = []
        self._chat_sig = None
        self._geo = (P, y0, ch, side_w)
        self.CW, self.CH = cw - 16, ch - 16
        self._cx, self._cy = cx + 8, y0 + 8
        r = self.root

        close = self.btn(r, (P + 6, hy + 7), (40, 40), bui.charstr(bui.SpecialChar.CLOSE), self.close_sound)
        bui.containerwidget(edit=r, cancel_button=close)
        self.title = self.lbl(r, (W / 2, hy + 37), u"\ue010 BSLIFE Ally", 0.95, GOLD, 'center', 300)
        self.head_sub = self.lbl(r, (W / 2, hy + 15), f"{L('user')}: ...", 0.45, (0.85, 0.93, 1.0), 'center', 300)
        self.btn(r, (W - P - 6 - 74, hy + 9), (74, 36), L("logout"), self._do_logout, kind='danger', ts=0.8)
        self.btn(r, (W - P - 6 - 74 - 8 - 64, hy + 9), (64, 36), L("style"), self.cycle_style, ts=0.8)
        self.status_line = self.lbl(r, (W / 2, P + 17), "", 0.55, DIM, 'center', W - 60)

        self.tab_buttons: Dict[str, Any] = {}
        self.content = None
        self._new_content()
        self._render_sidebar()
        self.refresh()

    # ─── plumbing ───
    def _alive(self, tok):
        try:
            return (not self._closing) and tok == self._tok and self.root.exists()
        except Exception:
            return False

    def _new_content(self):
        if self.content is not None:
            try:
                self.content.delete()
            except Exception:
                pass
        self.content = bui.containerwidget(parent=self.root, position=(self._cx, self._cy),
                                           size=(self.CW, self.CH), background=False)
        self._tok += 1
        return self.content

    def _reload(self, *_a):
        if self._closing or not self.root.exists():
            return
        self._new_content()
        self._render_current()

    def set_status(self, text, color=DIM):
        try:
            bui.textwidget(edit=self.status_line, text=text, color=color)
        except Exception:
            pass

    def close(self):
        self._closing = True
        self._tok += 1
        super().close()

    def _do_logout(self):
        self.api.logout()
        self.close()
        LoginWindow(self.api, _route_after_login)

    def _render_sidebar(self):
        for b in self.tab_buttons.values():
            try:
                b.delete()
            except Exception:
                pass
        self._btns = [e for e in self._btns if not (isinstance(e[2], str) and e[2].startswith("tab:"))]
        self.tab_buttons = {}
        P, y0, ch, side_w = self._geo
        tabs = [k for k in self.TABS if not (k in ("requests", "settings") and self.api.roleid not in (1, 2))]
        n = len(tabs)
        gap = 3
        th = min(32, (ch - 12 - (n - 1) * gap) / n)
        y = y0 + ch - 6 - th
        for key in tabs:
            self.tab_buttons[key] = self.btn(
                self.root, (P + 7, y), (side_w - 14, th), L(key), MyCall(self.switch_tab, key),
                kind='join' if key == self.current_tab else 'accent', ts=0.8, key="tab:" + key)
            y -= th + gap

    def switch_tab(self, key):
        if self._closing:
            return
        self.current_tab = key
        for k in self.tab_buttons:
            self.setkind("tab:" + k, 'join' if k == key else 'accent')
        if self.fx:
            self.fx.pulse()
        self._reload()

    def refresh(self):
        self.set_status(L("loading"), DIM)
        Network.fetch(self.api, "ally_status", callback=self._on_status)

    def _on_status(self, st):
        if self._closing or not self.root.exists():
            return
        if st in ("3", "0", "", None):
            self.set_status(L("session_retry"), DIM)

            def check(who):
                if who:
                    self.refresh()
                else:
                    self.set_status(L("session_expired"), RED)
                    self._do_logout()
            Network.fetch(self.api, "whoami", callback=check)
            return
        if not isinstance(st, dict):
            self.close()
            HubWindow(self.api)
            return
        if "error" in st and "name" not in st:
            self.set_status(f"{L('error')}: {st['error']}", RED)
            return
        self.api.ally = st.get("name")
        self.api.roleid = st.get("roleid")
        self.api.memberid = st.get("memberid")
        try:
            bui.textwidget(edit=self.title, text=u"\ue010 " + f"{st.get('name') or L('no_ally')} ({role_name(st.get('roleid'))})")
            bui.textwidget(edit=self.head_sub, text=f"{L('user')}: {self.api.user or '?'}")
        except Exception:
            pass
        self.set_status(L("ready"), GREEN)
        self._render_sidebar()
        self._reload()

    def _render_current(self):
        handler = getattr(self, "_tab_" + self.current_tab, None)
        if handler:
            try:
                handler()
            except Exception as e:
                log(f"Render EXCEPTION {self.current_tab}: {e}")

    # ─── tabs ───
    def _tab_overview(self):
        c, tok, CW, CH = self.content, self._tok, self.CW, self.CH

        def cb(st):
            if not self._alive(tok) or not isinstance(st, dict):
                return
            self.lbl(c, (CW / 2, CH - 16), L("overview"), 0.95, GOLD, 'center')
            rows = [(L('alliance_name'), str(st.get("name")), TXT),
                    (L('your_role'), role_name(st.get("roleid")), role_color(st.get("roleid"))),
                    (L('members_count'), str(st.get("count", "?")), TXT)]
            y = CH - 40
            for k, v, col in rows:
                y -= 44
                self.bar(c, 0, y, CW, 38)
                self.lbl(c, (14, y + 19), k + ":", 0.7, DIM)
                self.lbl(c, (CW - 14, y + 19), v, 0.75, col, 'right', CW / 2)
            if self.api.roleid != 1:
                self.btn(c, (CW / 2 - 90, 4), (180, 38), L("leave_ally"), self._confirm_leave, kind='danger')
        Network.fetch(self.api, "ally_status", callback=cb)

    def _confirm_leave(self):
        def do_leave():
            def cb(r):
                if r == "1":
                    self.close()
                    _later(0.5, MyCall(_route_after_login))
            Network.fetch(self.api, "ally_leave", callback=cb)
        ConfirmDialog(L("leave_ally"), L("leave_confirm"), do_leave)

    def _tab_members(self):
        c, tok, CW, CH = self.content, self._tok, self.CW, self.CH

        def cb(members):
            if not self._alive(tok):
                return
            if not isinstance(members, list):
                if members in ("3", "", "-1"):
                    self._on_status("3")
                return
            if not members:
                self.lbl(c, (CW / 2, CH / 2), L("empty"), 0.8, DIM, 'center')
                return
            sc, cont, hh = self.scroll(c, (0, 0), (CW, CH), len(members), 32)
            rw = CW - 12
            y = hh
            for m in members:
                y -= 32
                is_me = m.get("id") == self.api.memberid
                self.bar(cont, 0, y + 2, rw, 28, me=is_me)
                self.lbl(cont, (10, y + 16), role_name(m.get("roleid")), 0.6, role_color(m.get("roleid")), maxwidth=80)
                self.lbl(cont, (96, y + 16), m.get("name", "?"), 0.65, TXT, maxwidth=rw - 240)
                if m.get("muted"):
                    self.lbl(cont, (rw - 64, y + 16), L("mute"), 0.5, RED, 'right')
                if self.api.roleid in (1, 2) and not is_me:
                    self.btn(cont, (rw - 54, y + 5), (46, 22), "...", MyCall(self._open_member, m), ts=0.7)
        Network.fetch(self.api, "ally_members", callback=cb)

    def _open_member(self, m):
        MemberActionWindow(self.api, m, self._reload)

    def _tab_requests(self):
        c, tok, CW, CH = self.content, self._tok, self.CW, self.CH
        bw = (CW - 12) / 3
        for i, key in enumerate(["new", "accepted", "rejected"]):
            self.btn(c, (i * (bw + 6), CH - 30), (bw, 30), L(key), MyCall(self._set_req_filter, key),
                     kind='join' if key == self._req_filter else 'accent')

        def cb(reqs):
            if not self._alive(tok):
                return
            if not isinstance(reqs, list):
                return
            if not reqs:
                self.lbl(c, (CW / 2, (CH - 36) / 2), L("empty"), 0.8, DIM, 'center')
                return
            sc, cont, hh = self.scroll(c, (0, 0), (CW, CH - 38), len(reqs), 34)
            rw = CW - 12
            y = hh
            for r in reqs:
                y -= 34
                self.bar(cont, 0, y + 2, rw, 30)
                self.lbl(cont, (10, y + 17), r.get("name", "?"), 0.65, TXT, maxwidth=rw - 150)
                if self._req_filter == "new":
                    self.btn(cont, (rw - 140, y + 5), (64, 24), L("yes"), MyCall(self._handle_req, r, "accept"),
                             kind='join', ts=0.6)
                    self.btn(cont, (rw - 70, y + 5), (64, 24), L("no"), MyCall(self._handle_req, r, "reject"),
                             kind='danger', ts=0.6)
        Network.fetch(self.api, "ally_requests", (self._req_filter,), callback=cb)

    def _set_req_filter(self, key):
        self._req_filter = key
        self._reload()

    def _handle_req(self, r, mode):
        Network.fetch(self.api, "ally_handle_request", (r.get("id"), mode), callback=self._reload)

    def _tab_vault(self):
        c, tok, CW, CH = self.content, self._tok, self.CW, self.CH

        def cb(v):
            if not self._alive(tok) or not isinstance(v, dict):
                return
            self.bar(c, 0, CH - 110, CW, 100)
            self.lbl(c, (CW / 2, CH - 52), fmt(v.get("coin", 0)), 1.6, GOLD, 'center', CW - 30)
            self.lbl(c, (CW / 2, CH - 86), L("coins"), 0.65, DIM, 'center')
            btns = [(L("deposit"), self._open_deposit, 'join'),
                    (L("history"), self._open_vault_history, 'accent')]
            if self.api.roleid in (1, 2):
                btns.append((L("split"), self._open_split, 'accent'))
            bw = min(150, (CW - 10 * (len(btns) - 1)) / len(btns))
            x = (CW - (bw * len(btns) + 10 * (len(btns) - 1))) / 2
            for label, call, kind in btns:
                self.btn(c, (x, CH - 170), (bw, 44), label, call, kind=kind)
                x += bw + 10
        Network.fetch(self.api, "ally_vault_status", callback=cb)

    def _open_vault_history(self):
        VaultHistoryWindow(self.api)

    def _open_deposit(self):
        def do_deposit(amount):
            if amount is None:
                return
            if amount < 100:
                Popup(L("fail"), L("min_deposit"), kind="error")
                return

            def cb(r):
                if r == "1":
                    Popup(L("success"), L("deposit_ok"), kind="success", on_ok=self._reload)
                else:
                    Popup(L("fail"), L("not_enough_coins") if r == "coin_not_enough" else L("fail"), kind="error")
            Network.fetch(self.api, "ally_vault_add", (amount,), callback=cb)
        NumberInputPopup(L("enter_amount"), "", do_deposit)

    def _open_split(self):
        opts = [("equal_all", L("equal_all")), ("equal_ranking", L("equal_ranking")),
                ("ranking_points", L("ranking_points"))]

        def picked(typ):
            def cb(r):
                if r == "1":
                    Popup(L("success"), L("vault_split_ok"), kind="success", on_ok=self._reload)
                else:
                    Popup(L("fail"), {"coin_not_enough": L("not_enough_coins"),
                                      "no_ranking_info": L("no_ranking")}.get(r, L("fail")), kind="error")
            Network.fetch(self.api, "ally_vault_clear", (typ,), callback=cb)
        SelectDialog(L("select_type"), opts, picked)

    def _tab_settings(self):
        c, tok, CW, CH = self.content, self._tok, self.CW, self.CH

        def cb_settings(st):
            if not self._alive(tok) or not isinstance(st, dict):
                return

            def cb_enrol(en):
                if not self._alive(tok) or not isinstance(en, dict):
                    return
                taghide = st.get("taghide")
                mode_txt = {None: L("mode_direct"), 1: L("mode_request"), -1: L("mode_closed")}.get(en.get("request"), "?")
                rows = [
                    (f"{L('capacity')}: {st.get('capacity', '?')}", TXT, L("buy_1"), self._buy_capacity),
                    (f"{L('gkick')}: {st.get('gkick', 1)}", TXT, L("set"), MyCall(self._set_gkick, st.get('gkick', 1))),
                    (f"{L('spynet')}: {fmt(st.get('spynet', 0))}", TXT, L("set"), MyCall(self._set_spynet, st.get('spynet', 0))),
                    (f"{L('tag_status')}: {L('tag_active') if taghide is None else L('tag_inactive')}",
                     GREEN if taghide is None else RED, None, None),
                    (f"{L('sale_price')}: {fmt(st.get('price')) if st.get('price') else L('not_set')}", TXT,
                     L("set"), MyCall(self._set_price, st.get('price'))),
                    ('__h__', L("enrol_settings")),
                    (f"{L('join_mode')}: {mode_txt}", TXT, L("change"), self._change_join_mode),
                    (f"{L('min_coin')}: {en.get('coin', '-')}", TXT, L("set"), MyCall(self._set_enrol, "coin", en.get("coin"))),
                    (f"{L('req_top')}: {en.get('top', '-')}", TXT, L("set"), MyCall(self._set_enrol, "top", en.get("top"))),
                    (f"{L('min_score')}: {en.get('score', '-')}", TXT, L("set"), MyCall(self._set_enrol, "score", en.get("score"))),
                    (f"{L('bot_link')}: {L('forced') if en.get('bot') == 1 else L('off')}", TXT, L("toggle"),
                     MyCall(self._toggle_enrol_bot, en.get("bot"))),
                ]
                RH = 38
                sc, cont, hh = self.scroll(c, (0, 0), (CW, CH), len(rows), RH)
                rw = CW - 12
                y = hh
                for row in rows:
                    y -= RH
                    if row[0] == '__h__':
                        self.lbl(cont, (rw / 2, y + RH / 2), row[1], 0.8, GOLD, 'center')
                        continue
                    text, col, blabel, call = row
                    self.bar(cont, 0, y + 2, rw, RH - 4)
                    self.lbl(cont, (10, y + RH / 2), text, 0.62, col, maxwidth=rw - 130)
                    if blabel:
                        self.btn(cont, (rw - 110, y + 6), (102, RH - 12), blabel, call, ts=0.65)
            Network.fetch(self.api, "ally_enrol", callback=cb_enrol)
        Network.fetch(self.api, "ally_settings", callback=cb_settings)

    def _save_setting(self, key, val):
        def cb(r):
            if isinstance(r, dict) and "err" in r:
                Popup(L("fail"), str(r["err"]), kind="error")
            else:
                Popup(L("success"), L("saved"), kind="success", on_ok=self._reload)
        Network.fetch(self.api, "ally_save_setting", (key, val), callback=cb)

    def _set_gkick(self, cur): NumberInputPopup(L("gkick"), cur, lambda v: self._save_setting("gkick", v))
    def _set_spynet(self, cur): NumberInputPopup(L("spynet"), cur, lambda v: self._save_setting("spynet", v))
    def _set_price(self, cur): NumberInputPopup(L("sale_price"), cur, lambda v: self._save_setting("price", v))

    def _buy_capacity(self):
        Network.fetch(self.api, "ally_capacity",
                      callback=lambda r: Popup(L("success") if r == "1" else L("fail"), "",
                                               kind="success" if r == "1" else "error", on_ok=self._reload))

    def _change_join_mode(self):
        opts = [(None, L("mode_direct")), (1, L("mode_request")), (-1, L("mode_closed"))]

        def picked(req):
            def res_cb(r):
                name = L("mode_direct") if req is None else L("mode_request") if req == 1 else L("mode_closed")
                Popup(L("success"), f"{L('join_mode')}: {name}", kind="success", on_ok=self._reload)
            Network.fetch(self.api, "ally_set_enrol", ("request", req), callback=res_cb)
        SelectDialog(L("select_mode"), opts, picked)

    def _set_enrol(self, key, cur):
        def cb(val):
            def res_cb(r):
                if isinstance(r, dict) and "err" in r:
                    Popup(L("fail"), str(r["err"]), kind="error")
                else:
                    Popup(L("success"), L("saved"), kind="success", on_ok=self._reload)
            Network.fetch(self.api, "ally_set_enrol", (key, val), callback=res_cb)
        NumberInputPopup({"coin": L("min_coin"), "top": L("req_top"), "score": L("min_score")}.get(key, key), cur, cb)

    def _toggle_enrol_bot(self, cur):
        val = None if cur == 1 else 1

        def res_cb(r):
            Popup(L("success"), f"{L('bot_link')}: {L('forced') if val == 1 else L('off')}",
                  kind="success", on_ok=self._reload)
        Network.fetch(self.api, "ally_set_enrol", ("bot", val), callback=res_cb)

    def _tab_ranking(self):
        c, tok, CW, CH = self.content, self._tok, self.CW, self.CH

        def cb(r):
            if not self._alive(tok) or not isinstance(r, dict):
                return
            self.lbl(c, (CW / 2, CH - 16), L("ranking"), 0.95, GOLD, 'center')
            if not r.get("rank"):
                self.lbl(c, (CW / 2, CH / 2), L("not_ranked"), 0.85, DIM, 'center')
                return
            self.bar(c, 0, CH - 70, CW, 36)
            self.lbl(c, (CW / 2, CH - 52), f"#{r.get('rank')}  |  {float(r.get('score', 0)):.2f} pts", 0.9, GREEN, 'center')
            effective = [m for m in (r.get("m_data") or {}).values() if m.get("c") == 1]
            if not effective:
                return
            sc, cont, hh = self.scroll(c, (0, 0), (CW, CH - 78), len(effective), 28)
            rw = CW - 12
            y = hh
            for m in effective:
                y -= 28
                self.bar(cont, 0, y + 2, rw, 24)
                self.lbl(cont, (10, y + 14), f"#{m.get('r', '?')}  {m.get('n', '?')}", 0.6, TXT, maxwidth=rw - 100)
                self.lbl(cont, (rw - 10, y + 14), f"{float(m.get('s', 0)):.1f}", 0.6, GREEN, 'right')
        Network.fetch(self.api, "ally_ranking", callback=cb)

    def _tab_news(self):
        self._news = []
        self._load_news(None)

    def _load_news(self, offset):
        tok = self._tok

        def cb(page):
            if not self._alive(tok):
                return
            if isinstance(page, list):
                self._news.extend(page)
            self._render_news(tok, isinstance(page, list) and len(page) == 10)
        Network.fetch(self.api, "ally_news", (offset,), callback=cb)

    def _render_news(self, tok, has_more):
        c, CW, CH = self.content, self.CW, self.CH
        try:
            for ch in c.get_children():
                ch.delete()
        except Exception:
            pass
        news = self._news
        if not news:
            self.lbl(c, (CW / 2, CH / 2), L("no_news"), 0.85, DIM, 'center')
            return
        bottom = 36 if has_more else 0
        sc, cont, hh = self.scroll(c, (0, bottom), (CW, CH - bottom), len(news), 42)
        rw = CW - 12
        y = hh
        for n in news:
            y -= 42
            self.bar(cont, 0, y + 2, rw, 38)
            self.lbl(cont, (10, y + 26), n.get("text", ""), 0.55, TXT, maxwidth=rw - 20)
            self.lbl(cont, (10, y + 10), n.get("time", ""), 0.42, DIM, maxwidth=rw - 20)
        if has_more:
            self.btn(c, (CW / 2 - 60, 2), (120, 30), L("more"),
                     MyCall(self._load_news, news[-1].get("id")), kind='join', ts=0.7)

    def _tab_chat(self):
        c, tok, CW, CH = self.content, self._tok, self.CW, self.CH
        self._chat_sig = None
        self.chat_scroll = bui.scrollwidget(parent=c, position=(0, 42), size=(CW, CH - 42),
                                            color=(0.4, 0.6, 0.3), border_opacity=0.0)
        self.chat_container = bui.containerwidget(parent=self.chat_scroll, size=(CW - 12, CH - 42), background=False)
        self.chat_inp = self.field(c, (0, 0), (CW - 90, 36), "", max_chars=200, desc=L("message"))
        self.btn(c, (CW - 84, 0), (84, 36), L("send"), self._send_chat, kind='join', ts=0.8)
        self._refresh_chat(tok, True)

    def _refresh_chat(self, tok, loop):
        def cb(history):
            if not self._alive(tok) or self.current_tab != "chat":
                return
            if isinstance(history, list):
                sig = (len(history), str(history[-1]) if history else "")
                if sig != self._chat_sig:
                    self._chat_sig = sig
                    try:
                        self._render_chat(history[-50:])
                    except Exception as e:
                        log(f"chat render: {e}")
            if loop:
                _later(3.0, MyCall(self._refresh_chat, tok, True))
        Network.fetch(self.api, "ally_chat_history", callback=cb)

    def _render_chat(self, msgs):
        CW, CH = self.CW, self.CH
        for ch in self.chat_container.get_children():
            ch.delete()
        rh = 24
        hh = max(rh * len(msgs) + 6, CH - 42)
        bui.containerwidget(edit=self.chat_container, size=(CW - 12, hh))
        y = hh
        for m in msgs:
            y -= rh
            mine = m.get('name') == self.api.user
            self.lbl(self.chat_container, (6, y + rh / 2), f"{m.get('name')}: {m.get('chat')}", 0.6,
                     GREEN if mine else TXT, maxwidth=CW - 30)
        try:
            bui.scrollwidget(edit=self.chat_scroll, vertical_scroll=0.0)
        except Exception:
            pass

    def _send_chat(self):
        try:
            msg = (bui.textwidget(query=self.chat_inp) or '').strip()
        except Exception:
            return
        if not msg:
            return
        bui.textwidget(edit=self.chat_inp, text="")
        tok = self._tok
        Network.fetch(self.api, "ally_chat_send", (msg,), callback=lambda r: self._refresh_chat(tok, False))

    def _tab_channels(self):
        c, CW, CH = self.content, self.CW, self.CH
        self.lbl(c, (CW / 2, CH - 18), "Channels :", 0.95, GOLD, 'center')
        self.bar(c, 0, CH - 190, CW, 150)
        bw = min(300, CW - 40)
        x = (CW - bw) / 2
        self.btn(c, (x, CH - 100), (bw, 48), u"\u26a1BsRush",
                 MyCall(self._open_link, "https://t.me/bsrush_mod"), kind='join', ts=1.0)
        self.btn(c, (x, CH - 170), (bw, 48), "Tajer",
                 MyCall(self._open_link, "https://t.me/Tajerbetbot"), ts=1.0)

    def _open_link(self, url):
        try:
            bui.open_url(url)
        except Exception as e:
            log(f"open_url failed: {e}")
            try:
                if bui.clipboard_is_supported():
                    bui.clipboard_set_text(url)
                    bui.screenmessage(url, color=(0.5, 1, 0.7))
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════
# HUB (not in an alliance)
# ═══════════════════════════════════════════════════════════════

class HubWindow(_Win):
    FX = True

    def __init__(self, api):
        global _top
        W, H, P = 620, _win_h(), 10
        hy = H - P - 54
        ty = hy - 6 - 34
        top = ty - 6
        ch = top - P
        cards = [(P, hy, W - 2 * P, 54, 14, 'head'), (P, P, W - 2 * P, ch, 12, 'card')]
        super().__init__(W, H, cards, halos=[(W - 90, hy + 27, 100)])
        _top = self
        self.api = api
        self.IW, self.IH = W - 2 * P - 16, ch - 16
        self._ix, self._iy = P + 8, P + 8
        self.sub = None
        self.order_type = "rank"
        self._tab = "join"
        r = self.root
        close = self.btn(r, (P + 6, hy + 7), (40, 40), bui.charstr(bui.SpecialChar.CLOSE), self.close_sound)
        bui.containerwidget(edit=r, cancel_button=close)
        self.title = self.lbl(r, (W / 2, hy + 37), u"\ue010 " + L("hub_title"), 0.95, GOLD, 'center', 300)
        self.lbl(r, (W / 2, hy + 15), L("not_in_ally"), 0.45, (0.85, 0.93, 1.0), 'center', 300)
        self.btn(r, (W - P - 6 - 74, hy + 9), (74, 36), L("logout"), self._do_logout, kind='danger')
        self.btn(r, (W - P - 6 - 74 - 8 - 64, hy + 9), (64, 36), L("style"), self.cycle_style)
        self.btn(r, (P + 4, ty), (170, 34), L("create_ally"), self._tab_create, key="t:create", ts=0.85)
        self.btn(r, (P + 4 + 178, ty), (170, 34), L("join_ally"), self._tab_join, kind='join', key="t:join", ts=0.85)
        self._tab_join()

    def _do_logout(self):
        self.api.logout()
        self.close()
        LoginWindow(self.api, _route_after_login)

    def _clear_sub(self, which):
        self._tab = which
        self.setkind("t:create", 'join' if which == "create" else 'accent')
        self.setkind("t:join", 'join' if which == "join" else 'accent')
        if self.sub is not None:
            try:
                self.sub.delete()
            except Exception:
                pass
        self.sub = bui.containerwidget(parent=self.root, position=(self._ix, self._iy),
                                       size=(self.IW, self.IH), background=False)
        return self.sub

    def _tab_create(self):
        s = self._clear_sub("create")
        IW, IH = self.IW, self.IH

        def cb_status(st):
            if self._tab != "create" or not self.root.exists():
                return
            if not isinstance(st, dict) or "price" not in st:
                if st == "0":
                    Popup(L("error"), L("already_in_ally"), kind="error")
                else:
                    Popup(L("error"), str(st), kind="error")
                return
            self.bar(s, IW / 2 - 170, IH - 70, 340, 46)
            self.lbl(s, (IW / 2, IH - 47), f"{L('cost')}: {fmt(st['price'])} {L('coins')}", 0.9, GOLD, 'center', 320)
            self.inp_name = self.field(s, (IW / 2 - 150, IH - 130), (300, 40), "", max_chars=15, desc=L("alliance_name"))
            self.btn(s, (IW / 2 - 100, IH - 190), (200, 44), L("create_ally"), self._do_create, kind='join')
        Network.fetch(self.api, "create_status", callback=cb_status)

    def _do_create(self):
        name = (bui.textwidget(query=self.inp_name) or '').strip()
        if not name:
            Popup(L("error"), L("enter_name"), kind="error")
            return

        def cb(r1):
            if r1 == "confirm_needed":
                def cb2(r2):
                    if isinstance(r2, dict) and "url" in r2:
                        self._go_to_main()
                    elif isinstance(r2, dict) and "err" in r2:
                        Popup(L("error"), str(r2["err"]), kind="error")
                    else:
                        Popup(L("error"), L("create_fail"), kind="error")
                Network.fetch(self.api, "create_ally", (name, 1), callback=cb2)
            elif r1 == "already_in_ally":
                Popup(L("error"), L("already_in_ally"), kind="error")
            elif isinstance(r1, dict) and "err" in r1:
                Popup(L("error"), str(r1["err"]), kind="error")
            else:
                Popup(L("error"), L("create_fail"), kind="error")
        Network.fetch(self.api, "create_ally", (name, 0), callback=cb)

    def _tab_join(self):
        s = self._clear_sub("join")
        IW, IH = self.IW, self.IH
        self.order_type = "rank"
        self.inp_search = self.field(s, (0, IH - 38), (IW - 110, 36), "", max_chars=30, desc=L("search"))
        self.btn(s, (IW - 102, IH - 38), (102, 36), L("search"), self._do_join_search, kind='join')
        orders = [("rank", L("order_rank")), ("new", L("order_new")), ("old", L("order_old")),
                  ("count", L("order_count"))]
        bw = (IW - 3 * 6) / 4
        for i, (code, name) in enumerate(orders):
            self.btn(s, (i * (bw + 6), IH - 38 - 6 - 30), (bw, 30), name, MyCall(self._set_order, code),
                     kind='join' if code == "rank" else 'accent', key="o:" + code, ts=0.7)
        self.join_h = IH - 38 - 6 - 30 - 8
        self.join_box = bui.containerwidget(parent=s, position=(0, 0), size=(IW, self.join_h), background=False)
        self._do_join_search()

    def _set_order(self, code):
        self.order_type = code
        for k in ("rank", "new", "old", "count"):
            self.setkind("o:" + k, 'join' if k == code else 'accent')
        self._do_join_search()

    def _do_join_search(self):
        search = (bui.textwidget(query=self.inp_search) or '').strip()
        order = self.order_type
        box, IW, bh = self.join_box, self.IW, self.join_h

        def cb(allies):
            if self._tab != "join" or not self.root.exists() or order != self.order_type:
                return
            try:
                for c in box.get_children():
                    c.delete()
            except Exception:
                pass
            if not isinstance(allies, list):
                return
            visible = [a for a in allies if a.get("request") != -1]
            if not visible:
                self.lbl(box, (IW / 2, bh / 2), L("empty"), 0.8, DIM, 'center')
                return
            sc, cont, hh = self.scroll(box, (0, 0), (IW, bh), len(visible), 36)
            rw = IW - 12
            y = hh
            for a in visible:
                y -= 36
                is_req = a.get("request") == 1
                self.bar(cont, 0, y + 2, rw, 32)
                self.lbl(cont, (10, y + 18), f"#{a.get('rank') or '-'}   {a.get('name')}", 0.7, TXT, maxwidth=rw - 130)
                self.btn(cont, (rw - 108, y + 6), (100, 24), L("request_btn") if is_req else L("join_btn"),
                         MyCall(self._do_join, a), kind='accent' if is_req else 'join', ts=0.65)
        Network.fetch(self.api, "list_allies", (search, order), callback=cb)

    def _do_join(self, a):
        def cb(r):
            if r == "requested":
                Popup(L("success"), L("request_sent"), kind="success")
            elif (r in ("./post/Ally", "./post.php?post=Ally") or (isinstance(r, str) and "post=Ally" in r)
                  or r == "already_in_ally"):
                self._go_to_main(1.0)
            elif r == "request_rejected":
                Popup(L("fail"), L("req_rejected"), kind="error")
            elif r == "request_unseen":
                Popup(L("fail"), L("req_pending"), kind="error")
            elif r == "already_left":
                Popup(L("fail"), L("left_recent"), kind="error")
            else:
                reason = L("no_requirements")
                reqs = []
                if a.get("coin"):
                    reqs.append(f"{L('min_coin')}: {a['coin']}")
                if a.get("top"):
                    reqs.append(f"{L('req_top')}: {a['top']}")
                if a.get("score"):
                    reqs.append(f"{L('min_score')}: {a['score']}")
                if a.get("bot"):
                    reqs.append(L("bot_link"))
                if reqs:
                    reason += f"\n{L('needed')}:\n- " + "\n- ".join(reqs)
                Popup(L("fail"), reason, kind="error")
        Network.fetch(self.api, "join_ally", (a["id"],), callback=cb)

    def _go_to_main(self, delay=0.8):
        self.close()
        _later(delay, MyCall(_route_after_login))


# ═══════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════

def _ensure_api():
    global _api
    if _api is None:
        _api = BslifeAPI()
    return _api


def open_ally_manager():
    global _is_opening
    try:
        if _top is not None and _top.root.exists():
            return
    except Exception:
        pass
    if _is_opening:
        return
    _is_opening = True
    api = _ensure_api()

    def check(who):
        global _is_opening
        _is_opening = False
        if not who:
            LoginWindow(api, _route_after_login)
        else:
            _route_after_login()
    Network.fetch(api, "whoami", callback=check)


def _route_after_login():
    global _top, _is_opening
    _is_opening = False
    api = _ensure_api()
    if _top is not None:
        try:
            _top.close()
        except Exception:
            pass
        _top = None

    def check_status(st):
        if st in ("3", "0", "", None):
            api.logout()
            LoginWindow(api, _route_after_login)
            return
        if isinstance(st, dict) and "name" in st:
            AllyMainWindow(api)
        elif isinstance(st, dict) and "error" in st:
            Popup(L("error"), str(st["error"]), kind="error")
        else:
            HubWindow(api)
    Network.fetch(api, "ally_status", callback=check_status)


# ============================================================
# Plugin
# ============================================================

# ba_meta require api 9
# ba_meta export babase.Plugin
class byMahyar(Plugin):
    def __init__(s):
        global my_own_name
        try: my_own_name = APP.plus.get_v1_account_name()
        except: my_own_name = None

        s.last_msg_hash = ""
        s.last_calc_hash = ""

        # Creator credit shown each time BombSquad loads this mod.
        teck(2.5, lambda: push("Create By Mahyar\nChannel: @Horn_Ch", color=(0.4, 0.8, 1.0)))

        teck(0.1, s.ear)
        teck(0.5, s.calc_ear)
        teck(0.05, sellcek)
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

            return r

        party.PartyWindow.__init__ = e

    def ear(s):
        global _last_seen_messages
        try:
            z = GCM()
            teck(0.02, s.ear)
            current = list(z or [])
            new_msgs = _collect_new_messages(current, _last_seen_messages)
            _last_seen_messages = current

            for msg in new_msgs:
                try:
                    if check_spam_command(msg):
                        continue
                except Exception:
                    pass
                try:
                    if check_auto_reply(msg):
                        continue
                except Exception:
                    pass
                try:
                    if check_filter(msg):
                        continue
                except Exception:
                    pass
                try:
                    check_reaction(msg)
                except Exception:
                    pass
        except Exception as e:
            try:
                teck(0.05, s.ear)
            except Exception:
                pass
            print(f"Error in ear: {e}")

    def calc_ear(s):
        try:
            z = GCM()
            teck(0.3, s.calc_ear)

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
                teck(0.3, s.calc_ear)
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