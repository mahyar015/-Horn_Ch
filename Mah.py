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


# ✅ ذخیره IP/Port در config (دائمی)
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


LIMITS = get_limits()
REACTIONS = get_reactions()
COOLDOWNS = get_cooldowns()
AUTO_REPLIES = get_auto_replies()

auto_react_enabled = get_enabled_state('react', True)
auto_reply_enabled = get_enabled_state('reply', True)
auto_buyer_enabled = get_enabled_state('buyer', True)

last_msg_count = 0
processed_sell_ids = set()
processed_buy_ids = set()
processed_bids = set()
react_cooldown = {}
auto_reply_cooldown = {}

spam_active = False
spam_message = ""
spam_delay = 2.0
spam_counter = 0
spam_timer = None

# ✅ IP/Port ذخیره شده
server_ip, server_port = get_saved_server()

auto_reconnect_enabled = False
auto_reconnect_timer = None

my_own_name = None
my_own_client_id = None
my_own_display_num = None


class AR:
    @classmethod
    def UIS(c=0):
        i = APP.ui_v1.uiscale
        return [1.5, 1.1, 0.8][0 if i == uis.SMALL else 1 if i == uis.MEDIUM else 2]

    @classmethod
    def add_close_button(c, window, position=(10, 10)):
        return bw(
            parent=window, size=(28, 28), position=position, label='X',
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
    CM(message)


# ============================================
# ✅ Connection override برای ذخیره IP/Port
# ============================================
original_connect_to_party = original_connect

def new_connect_to_party(address, port=43210, print_progress=False):
    global server_ip, server_port
    server_ip = address
    server_port = port
    save_server(address, port)
    push(f'Saved server: {address}:{port}', color=(0, 1, 1))
    return original_connect_to_party(address, port, print_progress)


# ✅ جایگزینی تابع
bascenev1.connect_to_party = new_connect_to_party


# ============================================
# 🎯 Auto-Reply
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
        content_lower = content.lower()
        for keyword, response in AUTO_REPLIES.items():
            if keyword.lower() in content_lower:
                cd_key = f"{keyword}_{sender or 'unknown'}"
                current_time = time.time()
                last_time = auto_reply_cooldown.get(cd_key, 0)
                if current_time - last_time < 2.0: continue
                auto_reply_cooldown[cd_key] = current_time
                if len(auto_reply_cooldown) > 50:
                    now = time.time()
                    to_del = [k for k, v in auto_reply_cooldown.items() if now - v > 60]
                    for k in to_del: del auto_reply_cooldown[k]
                safe_chat_send(response); gs('dingSmall').play()
                return True
    except Exception as e: print(f"Auto-Reply error: {e}")
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
# 🔄 Auto Reconnect Logic
# ============================================
def auto_reconnect_check():
    global auto_reconnect_enabled, auto_reconnect_timer, server_ip, server_port
    
    if not auto_reconnect_enabled:
        return
    
    try:
        conn = get_connection_info()
        
        if not conn:
            if server_ip != "127.0.0.1":
                push("Auto Reconnecting...", color=(1, 1, 0))
                try:
                    foreground = bascenev1.get_foreground_host_session()
                    if isinstance(foreground, MainMenuSession):
                        original_connect_to_party(server_ip, server_port)
                except Exception as e:
                    print(f"Auto reconnect failed: {e}")
    except Exception as e:
        print(f"Auto reconnect check error: {e}")
    
    auto_reconnect_timer = teck(3.0, auto_reconnect_check)


def start_auto_reconnect():
    global auto_reconnect_enabled, auto_reconnect_timer
    auto_reconnect_enabled = True
    if auto_reconnect_timer:
        try: auto_reconnect_timer.cancel()
        except: pass
    auto_reconnect_timer = teck(3.0, auto_reconnect_check)
    push("Auto Reconnect: ON", color=(0, 1, 0))


def stop_auto_reconnect():
    global auto_reconnect_enabled, auto_reconnect_timer
    auto_reconnect_enabled = False
    if auto_reconnect_timer:
        try: auto_reconnect_timer.cancel()
        except: pass
        auto_reconnect_timer = None
    push("Auto Reconnect: OFF", color=(1, 0.5, 0))


# ============================================
# 🧮 Calculator
# ============================================
class Calculator:
    def __init__(s, source):
        s.w = AR.cw(source=source, size=(280, 380), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(255, 345))
        tw(parent=s.w, text='Math Engine', scale=0.85, position=(140, 340), h_align='center', color=(1, 0.5, 0.9))
        tw(parent=s.w, text=SIGNATURE, scale=0.45, position=(140, 325), h_align='center', color=(0.6, 0.6, 0.8))
        s.display = tw(parent=s.w, text='0', scale=1.1, position=(140, 295), h_align='center', color=(0.3, 1, 0.7), maxwidth=250)
        s.expression = tw(parent=s.w, text='', scale=0.5, position=(140, 275), h_align='center', color=(0.9, 0.7, 1), maxwidth=250)
        s.current_input = '0'
        s.previous_input = ''
        s.operation = None
        s.reset_next_input = False
        s.last_expression = ''
        bw(parent=s.w, label='Copy', size=(120, 25), position=(15, 242), on_activate_call=Call(s.copy_result), color=(0.4, 0.3, 0.7), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        bw(parent=s.w, label='Send', size=(120, 25), position=(145, 242), on_activate_call=Call(s.send_to_chat), color=(0.7, 0.4, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        row_y = 210
        row_gap = 30
        btn_h = 25
        rows = [
            [('AC', s.clear_all, (15, row_y), (40, btn_h), (0.7, 0.2, 0.3)), ('+/-', s.toggle_sign, (60, row_y), (40, btn_h), (0.3, 0.4, 0.7)), ('%', s.percentage, (105, row_y), (40, btn_h), (0.3, 0.4, 0.7)), ('R', s.square_root, (150, row_y), (40, btn_h), (0.3, 0.4, 0.7)), ('x2', s.square, (195, row_y), (40, btn_h), (0.3, 0.4, 0.7)), ('/', lambda: s.set_operation('/'), (240, row_y), (30, btn_h), (0.8, 0.6, 0.1))],
            [('7', lambda: s.append_number('7'), (15, row_y-row_gap), (40, btn_h), (0.25, 0.3, 0.45)), ('8', lambda: s.append_number('8'), (60, row_y-row_gap), (40, btn_h), (0.25, 0.3, 0.45)), ('9', lambda: s.append_number('9'), (105, row_y-row_gap), (40, btn_h), (0.25, 0.3, 0.45)), ('×', lambda: s.set_operation('*'), (150, row_y-row_gap), (40, btn_h), (0.8, 0.6, 0.1)), ('DEL', s.backspace, (195, row_y-row_gap), (40, btn_h), (0.6, 0.15, 0.25)), ('1/x', s.reciprocal, (240, row_y-row_gap), (30, btn_h), (0.3, 0.4, 0.7))],
            [('4', lambda: s.append_number('4'), (15, row_y-row_gap*2), (40, btn_h), (0.25, 0.3, 0.45)), ('5', lambda: s.append_number('5'), (60, row_y-row_gap*2), (40, btn_h), (0.25, 0.3, 0.45)), ('6', lambda: s.append_number('6'), (105, row_y-row_gap*2), (40, btn_h), (0.25, 0.3, 0.45)), ('-', lambda: s.set_operation('-'), (150, row_y-row_gap*2), (40, btn_h), (0.8, 0.6, 0.1)), ('n!', s.factorial, (195, row_y-row_gap*2), (40, btn_h), (0.3, 0.4, 0.7)), ('log', s.logarithm, (240, row_y-row_gap*2), (30, btn_h), (0.3, 0.4, 0.7))],
            [('1', lambda: s.append_number('1'), (15, row_y-row_gap*3), (40, btn_h), (0.25, 0.3, 0.45)), ('2', lambda: s.append_number('2'), (60, row_y-row_gap*3), (40, btn_h), (0.25, 0.3, 0.45)), ('3', lambda: s.append_number('3'), (105, row_y-row_gap*3), (40, btn_h), (0.25, 0.3, 0.45)), ('+', lambda: s.set_operation('+'), (150, row_y-row_gap*3), (40, btn_h), (0.8, 0.6, 0.1)), ('^', s.power, (195, row_y-row_gap*3), (40, btn_h), (0.3, 0.4, 0.7)), ('pi', s.pi_value, (240, row_y-row_gap*3), (30, btn_h), (0.5, 0.3, 0.7))],
            [('0', lambda: s.append_number('0'), (15, row_y-row_gap*4), (85, btn_h), (0.25, 0.3, 0.45)), ('.', s.add_decimal, (105, row_y-row_gap*4), (40, btn_h), (0.25, 0.3, 0.45)), ('=', s.calculate, (150, row_y-row_gap*4), (40, btn_h), (0.15, 0.65, 0.35)), ('e', s.e_value, (195, row_y-row_gap*4), (40, btn_h), (0.5, 0.3, 0.7)), ('!', s.factorial, (240, row_y-row_gap*4), (30, btn_h), (0.3, 0.4, 0.7))],
        ]
        for row in rows:
            for label, callback, pos, size, color in row:
                bw(parent=s.w, label=label, size=size, position=pos, on_activate_call=callback, color=color, textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
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
        if s.display.exists(): tw(s.display, text=s.current_input)
    def set_operation(s, op):
        if s.operation and not s.reset_next_input: s.calculate()
        s.previous_input = s.current_input; s.operation = op; s.reset_next_input = True
        op_symbol = {'+': '+', '-': '-', '*': '×', '/': '/', '**': '^'}.get(op, op)
        if s.expression.exists(): tw(s.expression, text=f"{s.current_input} {op_symbol}")
        gs('click01').play()
    def calculate(s):
        try:
            if not s.operation or s.reset_next_input: return
            num1 = float(s.previous_input); num2 = float(s.current_input)
            op_symbol = {'+': '+', '-': '-', '*': '×', '/': '/', '**': '^'}.get(s.operation, s.operation)
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
            if s.expression.exists(): tw(s.expression, text=s.last_expression)
            s.operation = None; s.reset_next_input = True; s.update_display(); gs('dingSmallHigh').play()
        except: s.current_input = 'Error'; s.update_display(); gs('error').play(); teck(2.0, s.clear_all)
    def clear_all(s):
        s.current_input = '0'; s.previous_input = ''; s.operation = None; s.reset_next_input = False; s.last_expression = ''
        s.update_display()
        if s.expression.exists(): tw(s.expression, text='')
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
# ⚙️ Edit Reaction
# ============================================
class EditReactionWindow:
    def __init__(s, source, trigger_code, parent_window=None):
        s.trigger_code = trigger_code
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(280, 220), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(250, 180))
        current = REACTIONS.get(trigger_code, '')
        current_cd = COOLDOWNS.get(trigger_code, DEFAULT_COOLDOWN)
        tw(parent=s.w, text=f'Edit "%{trigger_code}"', scale=0.8, position=(140, 175), h_align='center', color=(1, 1, 0))
        tw(parent=s.w, text='Reply with:', scale=0.55, position=(140, 152), h_align='center', color=(0.8, 0.8, 1))
        s.input = tw(parent=s.w, text=current, editable=True, scale=0.85, position=(30, 115), size=(220, 30), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Cooldown (sec):', scale=0.55, position=(140, 88), h_align='center', color=(0.8, 0.8, 1))
        s.cd_input = tw(parent=s.w, text=str(current_cd), editable=True, scale=0.85, position=(30, 55), size=(220, 30), h_align='center', color=(0.9, 0.9, 0.9))
        bw(parent=s.w, label='Save', size=(120, 32), position=(80, 10), on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square')
        gs('swish').play()
    def save(s):
        value = tw(query=s.input).strip().lower()
        if value: REACTIONS[s.trigger_code] = value
        else:
            if s.trigger_code in REACTIONS: del REACTIONS[s.trigger_code]
            if s.trigger_code in COOLDOWNS: del COOLDOWNS[s.trigger_code]
            save_reactions(REACTIONS); save_cooldowns(COOLDOWNS)
            bui.screenmessage(f'%{s.trigger_code} disabled', color=(1, 0.5, 0))
            gs('dingSmallHigh').play()
            if s.parent_window:
                try: s.parent_window.build_grid()
                except: pass
            AR.swish(s.w); return
        try: cd_value = float(tw(query=s.cd_input).strip())
        except: cd_value = DEFAULT_COOLDOWN
        if cd_value < 0: cd_value = 0
        COOLDOWNS[s.trigger_code] = cd_value
        save_reactions(REACTIONS); save_cooldowns(COOLDOWNS)
        bui.screenmessage(f'%{s.trigger_code} → {value}', color=(0, 1, 0))
        gs('dingSmallHigh').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class AddReactionWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(280, 240), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(250, 200))
        tw(parent=s.w, text='Add New', scale=0.85, position=(140, 195), h_align='center', color=(1, 1, 0))
        tw(parent=s.w, text='When %:', scale=0.55, position=(140, 168), h_align='center', color=(1, 1, 1))
        s.trigger_input = tw(parent=s.w, text='', editable=True, scale=0.85, position=(30, 135), size=(220, 30), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Reply:', scale=0.55, position=(140, 108), h_align='center', color=(1, 1, 1))
        s.response_input = tw(parent=s.w, text='', editable=True, scale=0.85, position=(30, 75), size=(220, 30), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Cooldown (sec):', scale=0.55, position=(140, 48), h_align='center', color=(1, 1, 1))
        s.cd_input = tw(parent=s.w, text=str(DEFAULT_COOLDOWN), editable=True, scale=0.85, position=(30, 15), size=(220, 30), h_align='center', color=(0.9, 0.9, 0.9))
        bw(parent=s.w, label='Add', size=(90, 28), position=(95, -20), on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square')
        gs('swish').play()
    def save(s):
        trigger = tw(query=s.trigger_input).strip().lower()
        response = tw(query=s.response_input).strip().lower()
        if not trigger or not response:
            AR.err('Both required!'); return
        try: cd_value = float(tw(query=s.cd_input).strip())
        except: cd_value = DEFAULT_COOLDOWN
        if cd_value < 0: cd_value = 0
        REACTIONS[trigger] = response; COOLDOWNS[trigger] = cd_value
        save_reactions(REACTIONS); save_cooldowns(COOLDOWNS)
        bui.screenmessage(f'%{trigger} → {response}', color=(0, 1, 0))
        gs('dingSmallHigh').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class ReactionEditorWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(320, 400), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(290, 360))
        tw(parent=s.w, text='Auto React', scale=0.95, position=(160, 355), h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.4, position=(160, 340), h_align='center', color=(0.6, 0.6, 0.8))
        s.id_text = tw(parent=s.w, text=f'cid={my_own_client_id or "?"} num={my_own_display_num if my_own_display_num is not None else "?"}', position=(160, 322), scale=0.4, h_align='center', color=(0, 1, 1))
        s.scroll = sw(parent=s.w, size=(280, 160), position=(20, 150))
        s.container = cw(parent=s.scroll, size=(260, 300), background=False)
        s.item_buttons = {}
        s.build_grid()
        bw(parent=s.w, label='+ Add', size=(80, 30), position=(20, 110), on_activate_call=Call(s.add_new), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        bw(parent=s.w, label='Reset', size=(80, 30), position=(110, 110), on_activate_call=Call(s.reset_all), color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        bw(parent=s.w, label='IDs', size=(80, 30), position=(200, 110), on_activate_call=Call(s.refresh_ids), color=(0.4, 0.3, 0.7), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        s.toggle_btn = bw(parent=s.w, label='ON' if auto_react_enabled else 'OFF', size=(280, 32), position=(20, 70), on_activate_call=Call(s.toggle), color=(0.2, 0.7, 0.2) if auto_react_enabled else (0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.75)
        gs('swish').play()
    def build_grid(s):
        for child in s.container.get_children(): child.delete()
        s.item_buttons.clear()
        items = list(REACTIONS.items())
        row_height = 32
        total_h = len(items) * row_height + 20
        for i, (trigger, response) in enumerate(items):
            y = total_h - (i + 1) * row_height
            cd = COOLDOWNS.get(trigger, DEFAULT_COOLDOWN)
            btn = bw(parent=s.container, label=f'%{trigger} → {response} ({cd}s)', size=(175, 26), position=(5, y), on_activate_call=Call(s.edit_item, trigger), color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1), button_type='square', text_scale=0.5)
            s.item_buttons[trigger] = btn
            bw(parent=s.container, label='X', size=(28, 26), position=(185, y), on_activate_call=Call(s.delete_item, trigger), color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.65)
        cw(s.container, size=(260, total_h))
    def refresh_ids(s):
        cid, num = get_my_ids()
        display_num = num if num is not None else "?"
        tw(s.id_text, text=f'cid={cid or "?"} num={display_num}', color=(0, 1, 0))
        bui.screenmessage(f'cid={cid}, num={display_num}', color=(0, 1, 0))
        gs('dingSmallHigh').play()
    def add_new(s): AddReactionWindow(s.w, parent_window=s)
    def edit_item(s, trigger): EditReactionWindow(s.w, trigger_code=trigger, parent_window=s)
    def delete_item(s, trigger):
        if trigger in REACTIONS: del REACTIONS[trigger]
        if trigger in COOLDOWNS: del COOLDOWNS[trigger]
        save_reactions(REACTIONS); save_cooldowns(COOLDOWNS)
        bui.screenmessage(f'Deleted: %{trigger}', color=(1, 0.5, 0)); gs('dingSmallLow').play()
        s.build_grid()
    def reset_all(s):
        global REACTIONS, COOLDOWNS
        REACTIONS = dict(DEFAULT_REACTIONS); COOLDOWNS = dict(DEFAULT_COOLDOWNS)
        save_reactions(REACTIONS); save_cooldowns(COOLDOWNS)
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
        s.w = AR.cw(source=source, size=(280, 180), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(250, 140))
        current = AUTO_REPLIES.get(keyword, '')
        tw(parent=s.w, text=f'Edit "{keyword}"', scale=0.8, position=(140, 135), h_align='center', color=(1, 1, 0))
        tw(parent=s.w, text='Reply:', scale=0.55, position=(140, 112), h_align='center', color=(0.8, 0.8, 1))
        s.input = tw(parent=s.w, text=current, editable=True, scale=0.85, position=(30, 75), size=(220, 30), h_align='center', color=(0.9, 0.9, 0.9))
        bw(parent=s.w, label='Save', size=(90, 30), position=(40, 20), on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square')
        bw(parent=s.w, label='Delete', size=(90, 30), position=(150, 20), on_activate_call=Call(s.delete), color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square')
        gs('swish').play()
    def save(s):
        value = tw(query=s.input).strip()
        if not value: AR.err('Required!'); return
        AUTO_REPLIES[s.keyword] = value; save_auto_replies(AUTO_REPLIES)
        bui.screenmessage(f'Saved!', color=(0, 1, 0)); gs('dingSmallHigh').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)
    def delete(s):
        if s.keyword in AUTO_REPLIES: del AUTO_REPLIES[s.keyword]
        save_auto_replies(AUTO_REPLIES)
        bui.screenmessage(f'Deleted!', color=(1, 0.5, 0)); gs('dingSmallLow').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class AddAutoReplyWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(280, 200), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(250, 160))
        tw(parent=s.w, text='Add Auto Reply', scale=0.85, position=(140, 155), h_align='center', color=(1, 1, 0))
        tw(parent=s.w, text='When contains:', scale=0.55, position=(140, 128), h_align='center', color=(1, 1, 1))
        s.keyword_input = tw(parent=s.w, text='', editable=True, scale=0.85, position=(30, 95), size=(220, 30), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Reply:', scale=0.55, position=(140, 68), h_align='center', color=(1, 1, 1))
        s.response_input = tw(parent=s.w, text='', editable=True, scale=0.85, position=(30, 35), size=(220, 30), h_align='center', color=(0.9, 0.9, 0.9))
        bw(parent=s.w, label='Add', size=(90, 28), position=(95, 0), on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square')
        gs('swish').play()
    def save(s):
        keyword = tw(query=s.keyword_input).strip()
        response = tw(query=s.response_input).strip()
        if not keyword or not response: AR.err('Both required!'); return
        AUTO_REPLIES[keyword] = response; save_auto_replies(AUTO_REPLIES)
        bui.screenmessage(f'Saved!', color=(0, 1, 0)); gs('dingSmallHigh').play()
        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class AutoReplyEditorWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(320, 400), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(290, 360))
        tw(parent=s.w, text='Auto Reply', scale=0.95, position=(160, 355), h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.4, position=(160, 340), h_align='center', color=(0.6, 0.6, 0.8))
        s.scroll = sw(parent=s.w, size=(280, 160), position=(20, 150))
        s.container = cw(parent=s.scroll, size=(260, 300), background=False)
        s.item_buttons = {}
        s.build_grid()
        bw(parent=s.w, label='+ Add', size=(80, 30), position=(20, 110), on_activate_call=Call(s.add_new), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        bw(parent=s.w, label='Clear', size=(80, 30), position=(110, 110), on_activate_call=Call(s.clear_all), color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.6)
        s.toggle_btn = bw(parent=s.w, label='ON' if auto_reply_enabled else 'OFF', size=(80, 30), position=(200, 110), on_activate_call=Call(s.toggle), color=(0.2, 0.7, 0.2) if auto_reply_enabled else (0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.75)
        tw(parent=s.w, text='Everywhere keyword matches → reply', position=(160, 85), scale=0.4, h_align='center', color=(0.7, 0.7, 1))
        gs('swish').play()
    def build_grid(s):
        for child in s.container.get_children(): child.delete()
        s.item_buttons.clear()
        items = list(AUTO_REPLIES.items())
        row_height = 32
        total_h = len(items) * row_height + 20
        for i, (keyword, response) in enumerate(items):
            y = total_h - (i + 1) * row_height
            btn = bw(parent=s.container, label=f'{keyword} → {response}', size=(175, 26), position=(5, y), on_activate_call=Call(s.edit_item, keyword), color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1), button_type='square', text_scale=0.5)
            s.item_buttons[keyword] = btn
            bw(parent=s.container, label='X', size=(28, 26), position=(185, y), on_activate_call=Call(s.delete_item, keyword), color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.65)
        cw(s.container, size=(260, total_h))
    def add_new(s): AddAutoReplyWindow(s.w, parent_window=s)
    def edit_item(s, keyword): EditAutoReplyWindow(s.w, keyword=keyword, parent_window=s)
    def delete_item(s, keyword):
        if keyword in AUTO_REPLIES: del AUTO_REPLIES[keyword]
        save_auto_replies(AUTO_REPLIES)
        bui.screenmessage(f'Deleted!', color=(1, 0.5, 0)); gs('dingSmallLow').play()
        s.build_grid()
    def clear_all(s):
        global AUTO_REPLIES
        AUTO_REPLIES = {}; save_auto_replies(AUTO_REPLIES)
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
        s.w = AR.cw(source=source, size=(300, 280), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(270, 240))
        tw(parent=s.w, text='Spam', scale=0.95, position=(150, 235), h_align='center', color=(1, 0.5, 0.5))
        tw(parent=s.w, text=SIGNATURE, scale=0.4, position=(150, 220), h_align='center', color=(0.6, 0.6, 0.8))
        s.status = tw(parent=s.w, text='Not Spamming', position=(150, 198), h_align='center', scale=0.65, color=(1, 1, 0))
        tw(parent=s.w, text='Message:', scale=0.55, position=(150, 175), h_align='center', color=(1, 1, 1))
        s.msg_input = tw(parent=s.w, text=saved_msg, editable=True, scale=0.85, position=(30, 145), size=(240, 30), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='Delay (seconds):', scale=0.55, position=(150, 118), h_align='center', color=(1, 1, 1))
        s.delay_input = tw(parent=s.w, text=str(saved_delay), editable=True, scale=0.85, position=(30, 85), size=(240, 30), h_align='center', color=(0.9, 0.9, 0.9))
        s.toggle_btn = bw(parent=s.w, label='START', size=(120, 32), position=(20, 40), on_activate_call=Call(s.start), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.75)
        bw(parent=s.w, label='STOP', size=(120, 32), position=(160, 40), on_activate_call=Call(s.stop), color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.75)
        tw(parent=s.w, text='Chat: "spam on/off"', position=(150, 15), scale=0.4, h_align='center', color=(0.7, 0.7, 1))
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
        
        s.w = AR.cw(source=source, size=(320, 320), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(290, 280))
        tw(parent=s.w, text='Server Manager', scale=0.95, position=(160, 275), h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.4, position=(160, 260), h_align='center', color=(0.6, 0.6, 0.8))
        
        s.ip_text = tw(parent=s.w, text=f'IP: {server_ip}', position=(160, 238), h_align='center', scale=0.55, color=(0.8, 0.8, 1))
        s.port_text = tw(parent=s.w, text=f'Port: {server_port}', position=(160, 220), h_align='center', scale=0.55, color=(0.8, 0.8, 1))
        
        bw(parent=s.w, label='RE (Rejoin)', size=(130, 32), position=(20, 175), on_activate_call=Call(s.re_button), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        bw(parent=s.w, label='Disconnect', size=(130, 32), position=(170, 175), on_activate_call=Call(s.disconnect), color=(0.7, 0.3, 0.3), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        
        tw(parent=s.w, text='Manual Connect:', scale=0.55, position=(160, 148), h_align='center', color=(1, 1, 1))
        s.ip_input = tw(parent=s.w, text=server_ip, editable=True, scale=0.75, position=(30, 120), size=(120, 26), h_align='center', color=(0.9, 0.9, 0.9))
        s.port_input = tw(parent=s.w, text=str(server_port), editable=True, scale=0.75, position=(170, 120), size=(120, 26), h_align='center', color=(0.9, 0.9, 0.9))
        
        bw(parent=s.w, label='Connect', size=(130, 30), position=(95, 80), on_activate_call=Call(s.manual_connect), color=(0.3, 0.5, 0.8), textcolor=(1, 1, 1), button_type='square', text_scale=0.65)
        
        s.auto_btn = bw(parent=s.w, label='Auto Reconnect: ' + ('ON' if auto_reconnect_enabled else 'OFF'), size=(280, 32), position=(20, 35), on_activate_call=Call(s.toggle_auto), color=(0.2, 0.7, 0.2) if auto_reconnect_enabled else (0.7, 0.2, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)
        
        tw(parent=s.w, text='Auto rejoin if disconnected', position=(160, 12), scale=0.4, h_align='center', color=(0.7, 0.7, 1))
        
        s.status = tw(parent=s.w, text='Ready', position=(160, 198), h_align='center', scale=0.5, color=(0.8, 0.8, 1))
        
        gs('swish').play()

    def re_button(s):
        global server_ip, server_port
        server_ip, server_port = get_saved_server()
        
        try:
            foreground = bascenev1.get_foreground_host_session()
            if isinstance(foreground, MainMenuSession):
                push('اینجا؟ چطور؟', color=(0, 1, 1))
                return
            
            if server_ip == "127.0.0.1":
                AR.err('No server saved!')
                return
            
            tw(s.status, text='Disconnecting...', color=(1, 1, 0))
            
            try:
                original_disconnect()
            except:
                pass
            
            push('Disconnected, reconnecting...', color=(1, 0.5, 0))
            
            def reconnect():
                try:
                    foreground = bascenev1.get_foreground_host_session()
                    
                    if isinstance(foreground, MainMenuSession):
                        tw(s.status, text='Connecting...', color=(1, 1, 0))
                        original_connect_to_party(server_ip, server_port)
                        bui.screenmessage(f'Rejoined {server_ip}:{server_port}', color=(0, 1, 0))
                        tw(s.status, text='Connected', color=(0, 1, 0))
                    else:
                        tw(s.status, text='Waiting...', color=(1, 1, 0))
                        teck(1.5, reconnect)
                except Exception as e:
                    bui.screenmessage(f'Rejoin failed: {e}', color=(1, 0, 0))
                    tw(s.status, text='Failed', color=(1, 0, 0))
            
            teck(3.0, reconnect)
            
        except Exception as e:
            AR.err(f'RE failed: {e}')

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
                original_disconnect()
                tw(s.status, text='Disconnecting...', color=(1, 1, 0))
                
                def do_connect():
                    try:
                        foreground = bascenev1.get_foreground_host_session()
                        if isinstance(foreground, MainMenuSession):
                            original_connect_to_party(ip, port)
                            bui.screenmessage(f'Connected to {ip}:{port}', color=(0, 1, 0))
                            tw(s.status, text='Connected', color=(0, 1, 0))
                        else:
                            teck(1.5, do_connect)
                    except Exception as e:
                        bui.screenmessage(f'Connect failed: {e}', color=(1, 0, 0))
                
                teck(3.0, do_connect)
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
        s.w = AR.cw(source=source, size=(360, 440), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(330, 400))
        tw(parent=s.w, text='Auto Buyer', scale=1.0, position=(180, 395), h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.45, position=(180, 378), h_align='center', color=(0.6, 0.6, 0.8))
        status = "ON" if auto_buyer_enabled else "OFF"
        status_color = (0, 1, 0) if auto_buyer_enabled else (1, 0, 0)
        s.status_text = tw(parent=s.w, text=f'Status: {status}', position=(180, 355), h_align='center', scale=0.75, color=status_color)
        s.toggle_btn = bw(parent=s.w, label='Turn OFF' if auto_buyer_enabled else 'Turn ON', size=(130, 28), position=(20, 320), on_activate_call=Call(s.toggle), color=(0.7, 0.2, 0.2) if auto_buyer_enabled else (0.2, 0.7, 0.2), textcolor=(1, 1, 1), button_type='square')
        bw(parent=s.w, label='Reset', size=(130, 28), position=(170, 320), on_activate_call=Call(s.reset_all), color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1), button_type='square', text_scale=0.65)
        tw(parent=s.w, text='─── Item Limits ───', position=(180, 288), h_align='center', scale=0.55, color=(1, 1, 0.8))
        s.scroll = sw(parent=s.w, size=(320, 230), position=(20, 40))
        s.container = cw(parent=s.scroll, size=(300, 700), background=False)
        s.item_buttons = {}
        s.build_grid()
        gs('swish').play()
    def build_grid(s):
        for child in s.container.get_children(): child.delete()
        s.item_buttons.clear()
        items = list(LIMITS.items())
        col_width = 150
        row_height = 32
        num_rows = (len(items) + 1) // 2
        total_h = num_rows * row_height + 60
        for i, (name, limit) in enumerate(items):
            col = i % 2
            row = i // 2
            x = 5 + col * col_width
            y = total_h - (row + 1) * row_height
            limit_str = str(int(limit)) if limit == int(limit) else f"{limit:.2f}".rstrip('0').rstrip('.')
            btn = bw(parent=s.container, label=f'{name}: {limit_str}', size=(140, 28), position=(x, y), on_activate_call=Call(s.edit_item, name), color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1), button_type='square', text_scale=0.55)
            s.item_buttons[name] = btn
        cw(s.container, size=(300, total_h))
    def refresh_list(s):
        for name, btn in s.item_buttons.items():
            try:
                if btn and btn.exists():
                    limit = LIMITS.get(name, 0)
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
    def edit_item(s, name): EditLimitsWindow(s.w, item_name=name, parent_window=s)
    def reset_all(s):
        global LIMITS
        LIMITS = dict(DEFAULT_LIMITS); save_limits(LIMITS)
        bui.screenmessage('Reset!', color=(0, 1, 1)); gs('dingSmallHigh').play()
        s.refresh_list()


class EditLimitsWindow:
    def __init__(s, source, item_name, parent_window=None):
        s.item_name = item_name; s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(280, 160), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(250, 120))
        current = str(LIMITS.get(item_name, 0))
        tw(parent=s.w, text=f'Set _ {item_name}', scale=0.85, position=(140, 115), h_align='center', color=(1, 1, 0))
        s.input = tw(parent=s.w, text=current, editable=True, scale=0.95, position=(40, 75), size=(200, 30), h_align='center', color=(0.9, 0.9, 0.9))
        tw(parent=s.w, text='(decimal allowed)', position=(140, 52), scale=0.45, h_align='center', color=(0.7, 0.7, 1))
        bw(parent=s.w, label='Save', size=(110, 30), position=(85, 15), on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square')
        gs('swish').play()
    def save(s):
        try: value = float(tw(query=s.input).strip())
        except: AR.err('Invalid!'); return
        LIMITS[s.item_name] = value; save_limits(LIMITS)
        bui.screenmessage(f'Saved!', color=(0, 1, 0)); gs('dingSmallHigh').play()
        if s.parent_window:
            try: s.parent_window.refresh_list()
            except: pass
        AR.swish(s.w)


# ============================================
# 🤖 Auto Buyer Logic
# ============================================
SELL_PATTERN = re.compile(r'💰Sell ID:\s*(\w+)')
BUY_PATTERN = re.compile(r'(\w+):\s*💳Buy\s*<\s*([\d,]+)\s+(\w+)\s*\([^)]+\)\s*>\s*for\s*([\d,]+)\s*coins(?:\?.*)?')
BID_PATTERN = re.compile(r'\bb\s+(s\d+)\b', re.IGNORECASE)


def process_sell(item_id):
    if item_id in processed_sell_ids: return
    processed_sell_ids.add(item_id)
    if len(processed_sell_ids) > 100: processed_sell_ids.clear()
    safe_chat_send(f"b {item_id}")


def process_buy(item_id, count, item_name, total_price):
    if item_name not in LIMITS:
        safe_chat_send("0 "); return
    bid_key = f"{item_id}_{item_name}_{count}_{total_price}"
    if bid_key in processed_buy_ids: return
    processed_buy_ids.add(bid_key)
    if len(processed_buy_ids) > 200: processed_buy_ids.clear()
    if count <= 0: safe_chat_send("0 "); return
    unit_price = total_price / count
    limit = LIMITS[item_name]
    if unit_price <= limit:
        safe_chat_send("1 "); gs('dingSmallHigh').play()
    else:
        safe_chat_send("0 ")


def process_bid(item_id):
    if not auto_buyer_enabled: return
    try:
        key = f"bid_{item_id}"
        if key in processed_bids: return
        processed_bids.add(key)
        safe_chat_send(f"b {item_id}"); gs('dingSmall').play()
    except Exception as e: print(f"Bid error: {e}")


# ============================================
# 🎯 Auto-React Logic
# ============================================
def check_reaction(msg):
    global my_own_client_id, my_own_display_num
    if not auto_react_enabled: return
    if my_own_client_id is None and my_own_display_num is None:
        get_my_ids()
    try:
        sender = None; content = msg
        if ': ' in msg:
            parts = msg.split(': ', 1)
            sender = parts[0].strip(); content = parts[1].strip()
        content_lower = content.lower()
        for trigger, response in REACTIONS.items():
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
                cd_time = COOLDOWNS.get(trigger, DEFAULT_COOLDOWN)
                current_time = time.time()
                cd_key = f"{trigger_lower}_{sender or 'unknown'}"
                last_time = react_cooldown.get(cd_key, 0)
                if current_time - last_time < cd_time: break
                react_cooldown[cd_key] = current_time
                if len(react_cooldown) > 50:
                    now = time.time()
                    to_del = [k for k, v in react_cooldown.items() if now - v > 300]
                    for k in to_del: del react_cooldown[k]
                safe_chat_send(response); gs('dingSmall').play()
                break
    except Exception as e: print(f"React error: {e}")


# ============================================
# 🎯 Check Chat
# ============================================
def check_chat():
    global last_msg_count, server_ip, server_port
    try:
        # ✅ چک کن که به سرور وصل هستیم و IP/Port ذخیره کنیم
        try:
            conn = get_connection_info()
            if conn:
                addr = getattr(conn, 'address', None)
                if addr and isinstance(addr, str) and ':' in addr:
                    parts = addr.rsplit(':', 1)
                    new_ip = parts[0]
                    new_port = int(parts[1])
                    
                    if new_ip != server_ip or new_port != server_port:
                        server_ip = new_ip
                        server_port = new_port
                        save_server(server_ip, server_port)
                        push(f'Server saved: {server_ip}:{server_port}', color=(0, 1, 1))
        except:
            pass
        
        messages = GCM()
        if messages:
            current_count = len(messages)
            if current_count < last_msg_count: last_msg_count = current_count
            if current_count > last_msg_count:
                new_messages = messages[last_msg_count:current_count]
                for msg in new_messages:
                    if check_spam_command(msg): continue
                    if check_auto_reply(msg): continue
                    check_reaction(msg)
                    if not auto_buyer_enabled: continue
                    m = SELL_PATTERN.search(msg)
                    if m: process_sell(m.group(1)); continue
                    is_mine = False
                    if my_own_name:
                        if msg.startswith(f"{my_own_name}:") or msg.startswith(f"{my_own_name} :"): is_mine = True
                    if not is_mine:
                        m2 = BID_PATTERN.search(msg)
                        if m2:
                            item_id = m2.group(1); process_bid(item_id); continue
                    m = BUY_PATTERN.search(msg)
                    if m:
                        process_buy(m.group(1), int(m.group(2).replace(',', '')), m.group(3).lower(), int(m.group(4).replace(',', '')))
                        continue
                last_msg_count = current_count
    except Exception as e: print(f"Chat error: {e}")
    teck(0.05, check_chat)


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
def check_spam_command(msg):
    global spam_active
    try:
        content = msg
        if ': ' in msg:
            _, content = msg.split(': ', 1)
        content = content.strip()
        content_lower = content.lower()

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
    except Exception as e: print(f"Spam command error: {e}")
    return False


# ============================================
# 🎯 Main Plugin
# ============================================
# ba_meta require api 9
# ba_meta export babase.Plugin
class byMahyar(Plugin):
    def __init__(s):
        global my_own_name, my_own_client_id, my_own_display_num, last_msg_count
        s.seen_calc = []
        s.seen_calc_set = set()
        try: my_own_name = APP.plus.get_v1_account_name()
        except: my_own_name = None
        try:
            initial_messages = GCM()
            last_msg_count = len(initial_messages) if initial_messages else 0
        except: last_msg_count = 0

        from bauiv1lib import party
        o = party.PartyWindow.__init__

        def e(self, *a, **k):
            r = o(self, *a, **k)

            teck(0.5, get_my_ids)

            b_calc = AR.bw(
                position=(self._width - 100, self._height - 100),
                parent=self._root_widget,
                size=(85, 25),
                label='Math',
                color=(0.3, 0.5, 0.8)
            )
            bw(b_calc, on_activate_call=Call(s.delayed_open, Calculator, b_calc))

            b_auto = AR.bw(
                position=(self._width - 100, self._height - 130),
                parent=self._root_widget,
                size=(85, 25),
                label='AutoBuy',
                color=(0.2, 0.6, 0.8)
            )
            bw(b_auto, on_activate_call=Call(s.delayed_open, AutoBuyerWindow, b_auto))

            b_react = AR.bw(
                position=(self._width - 100, self._height - 160),
                parent=self._root_widget,
                size=(85, 25),
                label='React',
                color=(0.8, 0.5, 0.2)
            )
            bw(b_react, on_activate_call=Call(s.delayed_open, ReactionEditorWindow, b_react))

            b_reply = AR.bw(
                position=(self._width - 100, self._height - 190),
                parent=self._root_widget,
                size=(85, 25),
                label='Reply',
                color=(0.3, 0.7, 0.4)
            )
            bw(b_reply, on_activate_call=Call(s.delayed_open, AutoReplyEditorWindow, b_reply))

            b_spam = AR.bw(
                position=(self._width - 100, self._height - 220),
                parent=self._root_widget,
                size=(85, 25),
                label='Spam',
                color=(0.8, 0.3, 0.3)
            )
            bw(b_spam, on_activate_call=Call(s.delayed_open, SpamWindow, b_spam))

            b_recon = AR.bw(
                position=(self._width - 100, self._height - 250),
                parent=self._root_widget,
                size=(85, 25),
                label='Reconnect',
                color=(0.4, 0.6, 0.4)
            )
            bw(b_recon, on_activate_call=Call(s.delayed_open, ReconnectWindow, b_recon))

            return r

        party.PartyWindow.__init__ = e

        teck(3.0, lambda: bui.screenmessage(CREATOR, color=(0, 1, 1)))
        teck(0.05, check_chat)
        teck(0.1, s.check_calc)
        teck(20.0, s.update_ids_loop)

    def delayed_open(s, cls, btn):
        teck(0.05, lambda: cls(btn))

    def update_ids_loop(s):
        get_my_ids()
        teck(20.0, s.update_ids_loop)

    def check_calc(s):
        try:
            messages = GCM()
            if messages:
                for msg in messages[-5:]:
                    if msg in s.seen_calc_set: continue
                    s.seen_calc_set.add(msg)
                    s.seen_calc.append(msg)
                    if ': ' in msg:
                        _, content = msg.split(': ', 1)
                        content = content.strip()
                        result = detect_calculation(content)
                        if result: safe_chat_send(result)
                if len(s.seen_calc) > 50:
                    old = s.seen_calc[:-50]
                    for o in old: s.seen_calc_set.discard(o)
                    s.seen_calc[:] = s.seen_calc[-50:]
        except Exception: pass
        teck(0.1, s.check_calc)
