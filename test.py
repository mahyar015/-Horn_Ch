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
import socket
import threading
import os
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
_reaction_pattern_cache = {}
auto_reply_cooldown = {}
filter_cooldown = {}

spam_active = False
spam_message = ""
spam_delay = 2.0
spam_counter = 0
spam_timer = None

server_ip, server_port = get_saved_server()
current_ping = 0.0
ping_thread = None

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
            max_x = max(0, s.parent_w - 128)
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
            default_x = s.parent_w - 150
            default_y = s.parent_h - 155
        except:
            default_x, default_y = 0, 0

        s.current_x, s.current_y = float(default_x), float(default_y)
        s.apply_position()

        bui.screenmessage('Reset!', color=(0, 1, 1))
        gs('dingSmallHigh').play()



# ============================================================
# Ping (integrated into the Mods menu)
# ============================================================
def get_ping_icon(ping):
    if ping == 0 or ping >= 999:
        return "❓"
    if ping < 100:
        return "🔵"
    if ping < 200:
        return "⚪"
    if ping < 350:
        return "🟠"
    return "🔴"


class RealPingThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.running = True

    def run(self):
        global current_ping
        while self.running:
            try:
                # Only attempt a real ping when a non-default server is selected.
                if server_ip != "127.0.0.1" or server_port != 43210:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0.8)
                    started = time.monotonic()
                    try:
                        sock.sendto(b'\x0b', (server_ip, int(server_port)))
                        data, _ = sock.recvfrom(16)
                        if data == b'\x0c':
                            current_ping = round((time.monotonic() - started) * 1000.0, 2)
                        else:
                            current_ping = 999
                    except socket.timeout:
                        current_ping = 999
                    except OSError:
                        current_ping = 0
                    finally:
                        sock.close()
                else:
                    current_ping = 0
            except Exception as exc:
                current_ping = 0
                print(f"[Ping] error: {exc}")
            time.sleep(1.0)


class PingWindow:
    def __init__(self, source):
        self.w = AR.cw(source=source, size=(280, 235), ps=AR.UIS() * 0.3)
        AR.add_close_button(self.w, position=(250, 200))
        tw(parent=self.w, text='Ping', scale=0.9, position=(140, 195),
           h_align='center', color=(0, 1, 1))
        self.ping_text = tw(
            parent=self.w, text=f'Current: {current_ping:.2f} ms' if 0 < current_ping < 999 else 'Current: ? ms',
            position=(140, 155), h_align='center', scale=0.75,
            color=(1, 1, 0)
        )
        tw(parent=self.w, text='Server:', position=(140, 120),
           h_align='center', scale=0.45, color=(0.8, 0.8, 1))
        self.server_text = tw(
            parent=self.w, text=f'{server_ip}:{server_port}',
            position=(140, 98), h_align='center', scale=0.45,
            color=(0.8, 0.8, 1)
        )
        AR.bw(
            parent=self.w, label='Send Ping to Chat',
            size=(190, 34), position=(45, 45),
            on_activate_call=self.send_ping,
            color=(0.2, 0.7, 0.3), text_scale=0.65
        )
        self.update_ping()

    def update_ping(self):
        try:
            if not self.w.exists():
                return
            ping_value = f'{current_ping:.2f}' if 0 < current_ping < 999 else '?'
            tw(self.ping_text, text=f'Current: {ping_value} ms')
            tw(self.server_text, text=f'{server_ip}:{server_port}')
            teck(0.5, self.update_ping)
        except Exception:
            pass

    def send_ping(self):
        try:
            icon = get_ping_icon(current_ping)
            value = '?' if current_ping <= 0 or current_ping >= 999 else f'{current_ping:.2f}'
            message = f'My Ping : {icon} {value} ms'
            CM(message)
            push(f'Sent: {message}', color=(0, 1, 0))
            try:
                gs('dingSmallHigh').play()
            except Exception:
                pass
        except Exception as exc:
            push(f'Ping error: {exc}', color=(1, 0, 0))



# ============================================================
# Mahyar Dashboard: player, chat, alerts and server telemetry
# ============================================================
_PLAYER_HISTORY = {}
_CHAT_STATS = {'messages': 0, 'senders': {}, 'recent': []}
_ANALYTICS_LAST_MESSAGES = None
_PING_HISTORY = []
_ALERT_LOG = []
_SESSION_STARTED = time.time()
_SESSION_CONNECTIONS = 0
_SESSION_CONNECTED = False
_SESSION_PING_TOTAL = 0.0
_SESSION_PING_COUNT = 0
_LAST_ALERT_PING_STATE = None
_LAST_ALERT_CONNECTION = None
_ALERT_KEYWORDS = ['bslife', 'event', 'shop', 'giveaway']
_FAVORITE_PLAYERS = set()
_TELEMETRY_STARTED = False


def _player_name(entry):
    try:
        players = entry.get('players', [])
        if players:
            return str(players[0].get('name_full') or players[0].get('name', '')).strip()
        return str(entry.get('display_string', '')).strip()
    except Exception:
        return ''


def _add_alert(message, color=(0.3, 0.9, 0.5)):
    stamp = time.strftime('%H:%M:%S')
    _ALERT_LOG.append(f'[{stamp}] {message}')
    del _ALERT_LOG[:-40]
    try:
        push(f'Mahyar Alert: {message}', color=color)
        gs('dingSmall').play()
    except Exception:
        pass


def _telemetry_tick():
    global _SESSION_CONNECTED, _SESSION_CONNECTIONS, _SESSION_PING_TOTAL, _ANALYTICS_LAST_MESSAGES
    global _SESSION_PING_COUNT, _LAST_ALERT_PING_STATE, _LAST_ALERT_CONNECTION
    try:
        now = time.time()
        try:
            roster = get_roster() or []
        except Exception:
            roster = []
        for entry in roster:
            name = _player_name(entry)
            if not name:
                continue
            rec = _PLAYER_HISTORY.setdefault(name, {'first': now, 'last': now, 'seen': 0})
            rec['last'] = now
            rec['seen'] += 1

        connected = bool(get_connection_info())
        if connected and not _SESSION_CONNECTED:
            _SESSION_CONNECTIONS += 1
            _add_alert('Connection established', (0.2, 0.9, 0.4))
        elif not connected and _SESSION_CONNECTED:
            _add_alert('Server disconnected', (1.0, 0.45, 0.2))
        _SESSION_CONNECTED = connected
        if _LAST_ALERT_CONNECTION is None:
            _LAST_ALERT_CONNECTION = connected

        ping = float(current_ping or 0)
        if 0 < ping < 999:
            _PING_HISTORY.append((now, ping))
            del _PING_HISTORY[:-180]
            _SESSION_PING_TOTAL += ping
            _SESSION_PING_COUNT += 1
            state = 'high' if ping >= 300 else 'normal'
            if state == 'high' and _LAST_ALERT_PING_STATE != 'high':
                _add_alert(f'High ping detected: {ping:.0f} ms', (1.0, 0.65, 0.15))
            _LAST_ALERT_PING_STATE = state
        else:
            _PING_HISTORY.append((now, 999))
            del _PING_HISTORY[:-180]

        try:
            messages = list(GCM() or [])
            new_messages = _collect_new_messages(messages, _ANALYTICS_LAST_MESSAGES)
            _ANALYTICS_LAST_MESSAGES = messages
            for msg in new_messages:
                if not isinstance(msg, str):
                    continue
                _CHAT_STATS['recent'].append(msg)
                del _CHAT_STATS['recent'][:-30]
                _CHAT_STATS['messages'] += 1
                sender = msg.split(': ', 1)[0][:32] if ': ' in msg else 'Unknown'
                _CHAT_STATS['senders'][sender] = _CHAT_STATS['senders'].get(sender, 0) + 1
                body = msg.split(': ', 1)[-1].lower()
                for keyword in _ALERT_KEYWORDS:
                    if keyword and keyword.lower() in body:
                        _add_alert(f'Keyword "{keyword}" in chat', (0.3, 0.8, 1.0))
                        break
        except Exception:
            pass
    except Exception as exc:
        print(f'[Mahyar telemetry] {exc}')
    teck(3.0, _telemetry_tick)


def _start_telemetry():
    global _TELEMETRY_STARTED, _ANALYTICS_LAST_MESSAGES
    if not _TELEMETRY_STARTED:
        _TELEMETRY_STARTED = True
        try:
            _ANALYTICS_LAST_MESSAGES = list(GCM() or [])
        except Exception:
            _ANALYTICS_LAST_MESSAGES = []
        teck(1.0, _telemetry_tick)


class _InfoPanel:
    title = 'Mahyar'
    def __init__(self, source):
        self.w = AR.cw(source=source, size=(370, 440), ps=AR.UIS() * 0.25)
        AR.add_close_button(self.w, position=(338, 405))
        tw(parent=self.w, text=self.title, scale=0.95, position=(185, 408), h_align='center', color=(0.2, 1.0, 0.55))
        self.body = tw(parent=self.w, text='Loading...', position=(18, 365), size=(334, 330), h_align='left', v_align='top', scale=0.58, color=(0.9, 0.94, 1.0))
        AR.bw(parent=self.w, label='Refresh', size=(150, 32), position=(110, 18), on_activate_call=self.refresh, color=(0.08, 0.55, 0.34), text_scale=0.7)
        self.refresh()
    def refresh(self):
        pass
    def show(self, value):
        try: tw(self.body, text=value)
        except Exception: pass


class PlayerIntelligenceWindow(_InfoPanel):
    title = 'PLAYER INTELLIGENCE'
    def __init__(self, source):
        super().__init__(source)
        self.favorite_input = tw(parent=self.w, text='', editable=True, position=(18, 72), size=(220, 26), scale=0.55, h_align='left', color=(1, 1, 1))
        AR.bw(parent=self.w, label='Toggle Favorite', size=(120, 28), position=(245, 70), on_activate_call=self.toggle_favorite, color=(0.42, 0.32, 0.08), text_scale=0.55)
        self.refresh()
    def toggle_favorite(self):
        name = tw(query=self.favorite_input).strip()
        if not name:
            AR.err('Enter player name first')
            return
        if name in _FAVORITE_PLAYERS:
            _FAVORITE_PLAYERS.remove(name)
            push(f'Removed favorite: {name}', color=(1, 0.7, 0.2))
        else:
            _FAVORITE_PLAYERS.add(name)
            push(f'Added favorite: {name}', color=(0.2, 1, 0.5))
        self.refresh()
    def refresh(self):
        try:
            roster = get_roster() or []
            lines = [f'ONLINE NOW: {len(roster)}', '']
            online = set()
            for entry in roster:
                name = _player_name(entry)
                if not name: continue
                online.add(name)
                lines.append(('★ ' if name in _FAVORITE_PLAYERS else '• ') + name[:35])
            lines += ['', f'PLAYERS SEEN THIS SESSION: {len(_PLAYER_HISTORY)}', 'RECENTLY SEEN:']
            recent = sorted(_PLAYER_HISTORY.items(), key=lambda x: x[1]['last'], reverse=True)[:8]
            for name, rec in recent:
                age = max(0, int(time.time() - rec['last']))
                lines.append(f'{name[:23]}  |  {age}s ago  |  {rec["seen"]} scans')
            lines += ['', 'Tip: favorite list is local to this game session.']
            self.show('\n'.join(lines))
        except Exception as e: self.show(f'Could not read roster: {e}')


class ChatAnalyticsWindow(_InfoPanel):
    title = 'CHAT ANALYTICS'
    def refresh(self):
        senders = sorted(_CHAT_STATS['senders'].items(), key=lambda x: x[1], reverse=True)[:12]
        lines = [f'MESSAGES OBSERVED: {_CHAT_STATS["messages"]}', '', 'MOST ACTIVE SENDERS:']
        lines += [f'{i+1}. {name[:26]}  —  {count}' for i, (name, count) in enumerate(senders)]
        lines += ['', 'RECENT CHAT:']
        lines += [str(x)[:58] for x in _CHAT_STATS['recent'][-8:]]
        self.show('\n'.join(lines))


class SmartAlertsWindow(_InfoPanel):
    title = 'SMART NOTIFICATIONS'
    def __init__(self, source):
        super().__init__(source)
        self.keyword_input = tw(parent=self.w, text=', '.join(_ALERT_KEYWORDS), editable=True, position=(18, 75), size=(334, 28), scale=0.58, h_align='left', color=(1, 1, 1))
        AR.bw(parent=self.w, label='Save Keywords', size=(150, 30), position=(110, 43), on_activate_call=self.save_keywords, color=(0.1, 0.45, 0.7), text_scale=0.62)
        self.refresh()
    def save_keywords(self):
        global _ALERT_KEYWORDS
        try:
            value = tw(query=self.keyword_input).strip()
            _ALERT_KEYWORDS = [x.strip()[:24] for x in value.split(',') if x.strip()][:10]
            push('Alert keywords saved', color=(0.2, 1, 0.5))
        except Exception as e: AR.err(f'Keyword error: {e}')
    def refresh(self):
        lines = ['ALERT HISTORY', ''] + (_ALERT_LOG[-14:] or ['No alerts yet.'])
        lines += ['', 'Automatic alerts: disconnect / reconnect, ping >= 300 ms, chat keywords.']
        self.show('\n'.join(lines))


class PersonalStatsWindow(_InfoPanel):
    title = 'PERSONAL STATISTICS'
    def refresh(self):
        elapsed = int(time.time() - _SESSION_STARTED)
        avg = (_SESSION_PING_TOTAL / _SESSION_PING_COUNT) if _SESSION_PING_COUNT else 0
        valid = [p for _, p in _PING_HISTORY if p < 999]
        best = min(valid) if valid else 0
        worst = max(valid) if valid else 0
        lines = [f'SESSION TIME: {elapsed//3600:02d}:{(elapsed%3600)//60:02d}:{elapsed%60:02d}',
                 f'CONNECTIONS THIS SESSION: {_SESSION_CONNECTIONS}',
                 f'PLAYERS SEEN: {len(_PLAYER_HISTORY)}',
                 f'CHAT MESSAGES OBSERVED: {_CHAT_STATS["messages"]}', '',
                 f'AVERAGE PING: {avg:.1f} ms' if avg else 'AVERAGE PING: unavailable',
                 f'BEST PING: {best:.1f} ms' if best else 'BEST PING: unavailable',
                 f'WORST PING: {worst:.1f} ms' if worst else 'WORST PING: unavailable',
                 f'PING SAMPLES: {len(_PING_HISTORY)}', '',
                 'Statistics are local and reset when the game restarts.']
        self.show('\n'.join(lines))


class ServerIntelligenceWindow(_InfoPanel):
    title = 'SERVER INTELLIGENCE'
    def refresh(self):
        vals = [p for _, p in _PING_HISTORY if p < 999]
        lost = sum(1 for _, p in _PING_HISTORY if p >= 999)
        avg = sum(vals)/len(vals) if vals else 0
        lines = [f'SERVER: {server_ip}:{server_port}',
                 f'CONNECTION: {"ONLINE" if _SESSION_CONNECTED else "OFFLINE"}',
                 f'SAMPLES: {len(_PING_HISTORY)}', f'LOST / TIMEOUT: {lost}', '',
                 f'AVERAGE: {avg:.1f} ms' if avg else 'AVERAGE: unavailable',
                 f'MIN: {min(vals):.1f} ms' if vals else 'MIN: unavailable',
                 f'MAX: {max(vals):.1f} ms' if vals else 'MAX: unavailable', '',
                 'RECENT PING (newest last):']
        recent = _PING_HISTORY[-18:]
        lines += [f'{p:.0f} ms' if p < 999 else 'timeout' for _, p in recent]
        lines += ['', 'History is collected while this mod is running.']
        self.show('\n'.join(lines))


# ============================================================
# Mods folder manager (restricted to the official user mods dir)
# ============================================================
def _mods_directory():
    path = getattr(APP, 'python_directory_user', None)
    if not path:
        try:
            from babase import app as _app
            path = getattr(_app, 'python_directory_user', None)
        except Exception:
            path = None
    if not path:
        raise RuntimeError('BombSquad user mods directory is unavailable')
    path = os.path.realpath(path)
    os.makedirs(path, exist_ok=True)
    return path


class ModsFileManagerWindow:
    def __init__(self, source):
        self.w = AR.cw(source=source, size=(410, 560), ps=AR.UIS() * 0.2)
        AR.add_close_button(self.w, position=(378, 525))
        tw(parent=self.w, text='MODS FILE MANAGER', position=(205, 530), scale=0.9, h_align='center', color=(0.2, 1, 0.55))
        try: self.directory = _mods_directory()
        except Exception as e: self.directory = ''; AR.err(str(e))
        self.path_text = tw(parent=self.w, text=self.directory or 'Mods folder unavailable', position=(15, 495), size=(380, 30), scale=0.38, h_align='left', color=(0.7, 0.85, 1))
        self.file_input = tw(parent=self.w, text='new_mod.py', editable=True, position=(18, 450), size=(180, 27), scale=0.6, h_align='left', color=(1, 1, 1))
        self.selected_text = tw(parent=self.w, text='Selected: none', position=(210, 455), size=(180, 22), scale=0.48, h_align='left', color=(1, 0.85, 0.3))
        self.list_text = tw(parent=self.w, text='', position=(18, 410), size=(374, 140), scale=0.55, h_align='left', v_align='top', color=(0.9, 0.95, 1))
        self.code_input = tw(parent=self.w, text='# Paste or write Python code here', editable=True, position=(18, 235), size=(374, 165), scale=0.52, h_align='left', v_align='top', color=(1, 1, 1))
        AR.bw(parent=self.w, label='Load File', size=(175, 32), position=(18, 190), on_activate_call=self.select_file, color=(0.12, 0.42, 0.68), text_scale=0.6)
        AR.bw(parent=self.w, label='Save / Add .py', size=(175, 32), position=(207, 190), on_activate_call=self.save_file, color=(0.08, 0.58, 0.32), text_scale=0.6)
        AR.bw(parent=self.w, label='Delete selected', size=(175, 32), position=(18, 148), on_activate_call=self.delete_file, color=(0.72, 0.18, 0.2), text_scale=0.6)
        AR.bw(parent=self.w, label='Refresh Files', size=(175, 32), position=(207, 148), on_activate_call=self.refresh, color=(0.35, 0.38, 0.55), text_scale=0.6)
        AR.bw(parent=self.w, label='Copy folder path', size=(175, 30), position=(18, 108), on_activate_call=self.copy_path, color=(0.35, 0.38, 0.55), text_scale=0.58)
        tw(parent=self.w, text='Only files directly inside the Mods folder are managed. Restart game after changes.', position=(18, 76), size=(374, 28), scale=0.4, h_align='left', color=(1, 0.75, 0.35))
        self.selected = None
        self.delete_armed_until = 0
        self.refresh()

    def refresh(self):
        try:
            names = sorted(n for n in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, n)) and not n.startswith('.'))
            py_names = [n for n in names if n.lower().endswith('.py')]
            shown = py_names[:18]
            tw(self.list_text, text='FILES (type a filename above, then Load File):\n' + ('\n'.join(f'{i+1}. {n}' for i, n in enumerate(shown)) if shown else 'No Python mods found.'))
            if self.selected and self.selected in py_names:
                tw(self.selected_text, text=f'Selected: {self.selected}')
            else:
                self.selected = None
                tw(self.selected_text, text='Selected: none')
            push(f'{len(py_names)} Python files found', color=(0.2, 1, 0.5))
        except Exception as e: AR.err(f'List error: {e}')

    def select_file(self):
        # Selection is driven by the filename field for compatibility with the game UI.
        name = tw(query=self.file_input).strip()
        if not name.lower().endswith('.py'): name += '.py'
        if not name or os.path.basename(name) != name: AR.err('Invalid filename'); return
        path = os.path.join(self.directory, name)
        if not os.path.isfile(path): AR.err('File not found'); return
        self.selected = name
        try:
            with open(path, 'r', encoding='utf-8') as f: tw(self.code_input, text=f.read()[:12000])
            tw(self.selected_text, text=f'Selected: {name}')
        except Exception as e: AR.err(f'Read error: {e}')

    def save_file(self):
        try:
            name = tw(query=self.file_input).strip()
            if not name: raise ValueError('Enter a file name')
            if not name.lower().endswith('.py'): name += '.py'
            if os.path.basename(name) != name or name in ('.py', '..py') or name.startswith('.'): raise ValueError('Invalid filename')
            code = tw(query=self.code_input)
            if not code.strip(): raise ValueError('Code is empty')
            path = os.path.realpath(os.path.join(self.directory, name))
            if os.path.dirname(path) != os.path.realpath(self.directory): raise ValueError('Invalid path')
            if os.path.exists(path) and name != self.selected:
                raise ValueError('File exists; select it first to overwrite')
            with open(path, 'w', encoding='utf-8') as f: f.write(code)
            self.selected = name
            tw(self.selected_text, text=f'Selected: {name}')
            push(f'Saved {name}. Restart BombSquad to load changes.', color=(0.2, 1, 0.5))
            self.refresh()
        except Exception as e: AR.err(f'Save error: {e}')

    def delete_file(self):
        try:
            if not self.selected:
                # first action loads/selects the filename entered in the top field
                self.select_file(); return
            if time.time() > self.delete_armed_until:
                self.delete_armed_until = time.time() + 5
                push('Tap Delete selected again within 5 seconds to confirm.', color=(1, 0.75, 0.2))
                return
            path = os.path.realpath(os.path.join(self.directory, self.selected))
            if os.path.dirname(path) != os.path.realpath(self.directory) or not os.path.isfile(path): raise ValueError('Invalid file')
            os.remove(path)
            old = self.selected; self.selected = None; self.delete_armed_until = 0
            tw(self.selected_text, text='Selected: none')
            tw(self.code_input, text='')
            push(f'Deleted {old}. Restart BombSquad if it was loaded.', color=(1, 0.5, 0.2))
            self.refresh()
        except Exception as e: AR.err(f'Delete error: {e}')

    def copy_path(self):
        try:
            from babase import clipboard_set_text
            clipboard_set_text(self.directory)
            push('Mods folder path copied', color=(0.2, 1, 0.5))
        except Exception as e: AR.err(f'Clipboard error: {e}')


class ModsMenu:
    def __init__(s, source):
        s.mods_button_ref = source
        s.w = AR.cw(source=source, size=(430, 640), ps=AR.UIS() * 0.25)
        AR.add_close_button(s.w, position=(398, 605))
        tw(parent=s.w, text='MAHYAR MODS', scale=1.08, position=(215, 604), h_align='center', color=(0.15, 1.0, 0.52))
        tw(parent=s.w, text='Create By Mahyar', scale=0.52, position=(215, 580), h_align='center', color=(0.75, 0.9, 1.0))

        s.scroll = sw(parent=s.w, size=(390, 520), position=(20, 42))
        buttons = [
            ('Calculator', Calculator, (0.08, 0.35, 0.72)),
            ('Ping Monitor', PingWindow, (0.08, 0.48, 0.62)),
            ('Auto Buyer', AutoBuyerWindow, (0.08, 0.52, 0.32)),
            ('Auto React', ReactionEditorWindow, (0.55, 0.32, 0.72)),
            ('Auto Reply', AutoReplyEditorWindow, (0.12, 0.48, 0.48)),
            ('Spam Settings', SpamWindow, (0.65, 0.22, 0.24)),
            ('Reconnect', ReconnectWindow, (0.22, 0.48, 0.28)),
            ('Chat Filter', FilterWindow, (0.42, 0.3, 0.68)),
            ('Edit Button Place', None, (0.35, 0.34, 0.48)),
            ('Player Intelligence', PlayerIntelligenceWindow, (0.05, 0.48, 0.48)),
            ('Chat Analytics', ChatAnalyticsWindow, (0.08, 0.42, 0.68)),
            ('Smart Alerts', SmartAlertsWindow, (0.58, 0.38, 0.08)),
            ('My Statistics', PersonalStatsWindow, (0.12, 0.48, 0.34)),
            ('Server Intelligence', ServerIntelligenceWindow, (0.12, 0.34, 0.62)),
            ('Mods File Manager', ModsFileManagerWindow, (0.48, 0.25, 0.58)),
        ]
        cols = 2
        row_h = 62
        rows = (len(buttons) + cols - 1) // cols
        total_h = rows * row_h + 16
        s.container = cw(parent=s.scroll, size=(370, total_h), background=False)
        s.item_buttons = []
        for i, (label, cls, color) in enumerate(buttons):
            col = i % 2
            row = i // 2
            x = 5 + col * 185
            y = total_h - 58 - row * row_h
            btn = bw(parent=s.container, label=label, size=(175, 48), position=(x, y),
                     on_activate_call=lambda c=cls: s.open_window(c), color=color,
                     textcolor=(1, 1, 1), button_type='square', text_scale=0.62)
            s.item_buttons.append(btn)
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

    teck(0.05, sellcek)


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

            pattern = _reaction_pattern_cache.get(trigger_lower)
            if pattern is None:
                pattern = re.compile(
                    rf"(?:^|[\s/])%?\s*{re.escape(trigger_lower)}\s*%?\s*(\d+)"
                )
                _reaction_pattern_cache[trigger_lower] = pattern
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


# ============================================================
# Plugin
# ============================================================

# ba_meta require api 9
# ba_meta export babase.Plugin
class byMahyar(Plugin):
    def __init__(s):
        global my_own_name, ping_thread
        if ping_thread is None or not ping_thread.is_alive():
            ping_thread = RealPingThread()
            ping_thread.start()
        try: my_own_name = APP.plus.get_v1_account_name()
        except: my_own_name = None

        _start_telemetry()
        s.last_msg_hash = ""
        s.last_calc_hash = ""

        teck(0.01, s.ear)
        teck(0.5, s.calc_ear)
        teck(0.05, sellcek)
        teck(1, s.reconnect_ear)

        from bauiv1lib import party
        o = party.PartyWindow.__init__

        def e(self, *a, **k):
            r = o(self, *a, **k)
            teck(0.5, get_my_ids)

            default_x = self._width - 150
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
                size=(128, 28),
                label='Create By Mahyar',
                color=(0.05, 0.62, 0.32),
                text_scale=0.58
            )
            bw(b_mods, on_activate_call=lambda: s.delayed_open(ModsMenu, b_mods))

            return r

        party.PartyWindow.__init__ = e

    def ear(s):
        global _last_seen_messages
        try:
            z = GCM()
            teck(0.01, s.ear)
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