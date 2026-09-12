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
    get_game_roster as get_roster
)
import math
import re
import time
import bauiv1 as bui
from babase import app

SIGNATURE = "By Mahyar"
CREATOR = "Creat By Mahyar\nTEL: @Mahyar015"

# ============================================
# ⚙️ قیمت‌های پیش‌فرض Auto Buyer
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

DEFAULT_UNKNOWN = 999999

DEFAULT_REACTIONS = {
    'fr': 'u',
    'cu': 'h',
    'fl': 'fl',
}

DEFAULT_COOLDOWNS = {
    'fr': 5.0,
    'cu': 5.0,
    'fl': 5.0,
}
DEFAULT_COOLDOWN = 5.0

auto_react_enabled = True


def get_limits():
    try:
        saved = app.config.get('mahyar_limits', None)
        if saved:
            d = dict(DEFAULT_LIMITS)
            d.update(saved)
            return d
    except:
        pass
    return dict(DEFAULT_LIMITS)


def save_limits(limits):
    try:
        app.config['mahyar_limits'] = dict(limits)
        app.config.commit()
    except:
        pass


def get_reactions():
    try:
        saved = app.config.get('mahyar_reactions_v12', None)
        if saved:
            d = dict(DEFAULT_REACTIONS)
            d.update(saved)
            return d
    except:
        pass
    return dict(DEFAULT_REACTIONS)


def save_reactions(reactions):
    try:
        app.config['mahyar_reactions_v12'] = dict(reactions)
        app.config.commit()
    except:
        pass


def get_cooldowns():
    try:
        saved = app.config.get('mahyar_cooldowns_v12', None)
        if saved:
            d = dict(DEFAULT_COOLDOWNS)
            d.update(saved)
            return d
    except:
        pass
    return dict(DEFAULT_COOLDOWNS)


def save_cooldowns(cooldowns):
    try:
        app.config['mahyar_cooldowns_v12'] = dict(cooldowns)
        app.config.commit()
    except:
        pass


LIMITS = get_limits()
REACTIONS = get_reactions()
COOLDOWNS = get_cooldowns()
auto_buyer_enabled = True

# ✅ ردیابی پیام‌ها با زمان
seen_messages = []
seen_messages_time = {}

processed_buy_ids = set()
processed_bids = set()

# ✅ cooldown storage
react_cooldown = {}

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
            parent=window,
            size=(28, 28),
            position=position,
            label='X',
            color=(0.6, 0.15, 0.25),
            textcolor=(1, 1, 1),
            on_activate_call=Call(c.swish, t=window)
        )

    @classmethod
    def bw(c, **k):
        return bw(**k, textcolor=(1, 1, 1), enable_sound=False, button_type='square')

    @classmethod
    def cw(c, source, ps=0, **k):
        o = source.get_screen_space_center() if source else None
        r = cw(
            **k,
            scale=c.UIS() + ps,
            transition='in_scale',
            color=(0.12, 0.14, 0.2),
            parent=gsw('overlay_stack'),
            scale_origin_stack_offset=o
        )
        cw(r, on_outside_click_call=Call(c.swish, t=r))
        return r

    swish = lambda c=0, t=0: (gs('swish').play(), cw(t, transition='out_scale') if t else t)
    err = lambda t: (gs('block').play(), push(t, color=(1, 1, 0)))


# ============================================
# 🎯 گرفتن IDs خودمون
# ============================================
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
                    if name_full and ' ' in name_full:
                        try:
                            my_own_display_num = int(name_full.split(' ')[0])
                        except:
                            my_own_display_num = None

                return my_own_client_id, my_own_display_num

        return None, None
    except Exception as e:
        print(f"Error getting IDs: {e}")
        return None, None


# ============================================
# 🎯 ارسال امن به چت
# ============================================
def safe_chat_send(message):
    CM(message)


# ============================================
# 🧮 Calculator
# ============================================
class Calculator:
    def __init__(s, source):
        s.w = AR.cw(source=source, size=(300, 400), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(275, 365))

        tw(parent=s.w, text='Math Engine', scale=0.85,
           position=(150, 360), h_align='center', color=(1, 0.5, 0.9))

        tw(parent=s.w, text=SIGNATURE, scale=0.45,
           position=(150, 345), h_align='center', color=(0.6, 0.6, 0.8))

        s.display = tw(parent=s.w, text='0', scale=1.1,
                       position=(150, 315), h_align='center',
                       color=(0.3, 1, 0.7), maxwidth=270)

        s.expression = tw(parent=s.w, text='', scale=0.5,
                          position=(150, 295), h_align='center',
                          color=(0.9, 0.7, 1), maxwidth=270)

        s.current_input = '0'
        s.previous_input = ''
        s.operation = None
        s.reset_next_input = False
        s.last_expression = ''

        bw(parent=s.w, label='Copy', size=(130, 25),
           position=(15, 262), on_activate_call=Call(s.copy_result),
           color=(0.4, 0.3, 0.7), textcolor=(1, 1, 1), button_type='square',
           text_scale=0.7)
        bw(parent=s.w, label='Send', size=(130, 25),
           position=(155, 262), on_activate_call=Call(s.send_to_chat),
           color=(0.7, 0.4, 0.2), textcolor=(1, 1, 1), button_type='square',
           text_scale=0.7)

        row_y = 225
        row_gap = 32
        btn_h = 27

        rows = [
            [('AC', s.clear_all, (15, row_y), (42, btn_h), (0.7, 0.2, 0.3)),
             ('+/-', s.toggle_sign, (63, row_y), (42, btn_h), (0.3, 0.4, 0.7)),
             ('%', s.percentage, (111, row_y), (42, btn_h), (0.3, 0.4, 0.7)),
             ('R', s.square_root, (159, row_y), (42, btn_h), (0.3, 0.4, 0.7)),
             ('x2', s.square, (207, row_y), (42, btn_h), (0.3, 0.4, 0.7)),
             ('/', lambda: s.set_operation('/'), (255, row_y), (30, btn_h), (0.8, 0.6, 0.1))],
            [('7', lambda: s.append_number('7'), (15, row_y-row_gap), (42, btn_h), (0.25, 0.3, 0.45)),
             ('8', lambda: s.append_number('8'), (63, row_y-row_gap), (42, btn_h), (0.25, 0.3, 0.45)),
             ('9', lambda: s.append_number('9'), (111, row_y-row_gap), (42, btn_h), (0.25, 0.3, 0.45)),
             ('×', lambda: s.set_operation('*'), (159, row_y-row_gap), (42, btn_h), (0.8, 0.6, 0.1)),
             ('DEL', s.backspace, (207, row_y-row_gap), (42, btn_h), (0.6, 0.15, 0.25)),
             ('1/x', s.reciprocal, (255, row_y-row_gap), (30, btn_h), (0.3, 0.4, 0.7))],
            [('4', lambda: s.append_number('4'), (15, row_y-row_gap*2), (42, btn_h), (0.25, 0.3, 0.45)),
             ('5', lambda: s.append_number('5'), (63, row_y-row_gap*2), (42, btn_h), (0.25, 0.3, 0.45)),
             ('6', lambda: s.append_number('6'), (111, row_y-row_gap*2), (42, btn_h), (0.25, 0.3, 0.45)),
             ('-', lambda: s.set_operation('-'), (159, row_y-row_gap*2), (42, btn_h), (0.8, 0.6, 0.1)),
             ('n!', s.factorial, (207, row_y-row_gap*2), (42, btn_h), (0.3, 0.4, 0.7)),
             ('log', s.logarithm, (255, row_y-row_gap*2), (30, btn_h), (0.3, 0.4, 0.7))],
            [('1', lambda: s.append_number('1'), (15, row_y-row_gap*3), (42, btn_h), (0.25, 0.3, 0.45)),
             ('2', lambda: s.append_number('2'), (63, row_y-row_gap*3), (42, btn_h), (0.25, 0.3, 0.45)),
             ('3', lambda: s.append_number('3'), (111, row_y-row_gap*3), (42, btn_h), (0.25, 0.3, 0.45)),
             ('+', lambda: s.set_operation('+'), (159, row_y-row_gap*3), (42, btn_h), (0.8, 0.6, 0.1)),
             ('^', s.power, (207, row_y-row_gap*3), (42, btn_h), (0.3, 0.4, 0.7)),
             ('pi', s.pi_value, (255, row_y-row_gap*3), (30, btn_h), (0.5, 0.3, 0.7))],
            [('0', lambda: s.append_number('0'), (15, row_y-row_gap*4), (90, btn_h), (0.25, 0.3, 0.45)),
             ('.', s.add_decimal, (111, row_y-row_gap*4), (42, btn_h), (0.25, 0.3, 0.45)),
             ('=', s.calculate, (159, row_y-row_gap*4), (42, btn_h), (0.15, 0.65, 0.35)),
             ('e', s.e_value, (207, row_y-row_gap*4), (42, btn_h), (0.5, 0.3, 0.7)),
             ('!', s.factorial, (255, row_y-row_gap*4), (30, btn_h), (0.3, 0.4, 0.7))],
        ]

        for row in rows:
            for label, callback, pos, size, color in row:
                bw(parent=s.w, label=label, size=size, position=pos,
                   on_activate_call=callback, color=color,
                   textcolor=(1, 1, 1), button_type='square', text_scale=0.7)

        AR.swish()

    def append_number(s, number):
        if s.reset_next_input:
            s.current_input = '0'
            s.reset_next_input = False
        current = s.current_input
        s.current_input = number if current == '0' else current + number
        s.update_display()
        gs('click01').play()

    def add_decimal(s):
        if s.reset_next_input:
            s.current_input = '0'
            s.reset_next_input = False
        current = s.current_input
        if '.' not in current:
            s.current_input = current + '.'
            s.update_display()
            gs('click01').play()

    def backspace(s):
        current = s.current_input
        if current != '0' and len(current) > 1:
            current = current[:-1]
        else:
            current = '0'
        s.current_input = current
        s.update_display()
        gs('swish').play()

    def update_display(s):
        if s.display.exists():
            tw(s.display, text=s.current_input)

    def set_operation(s, op):
        if s.operation and not s.reset_next_input:
            s.calculate()
        s.previous_input = s.current_input
        s.operation = op
        s.reset_next_input = True
        op_symbol = {'+': '+', '-': '-', '*': '×', '/': '/', '**': '^'}.get(op, op)
        if s.expression.exists():
            tw(s.expression, text=f"{s.current_input} {op_symbol}")
        gs('click01').play()

    def calculate(s):
        try:
            if not s.operation or s.reset_next_input:
                return
            num1 = float(s.previous_input)
            num2 = float(s.current_input)

            op_symbol = {'+': '+', '-': '-', '*': '×', '/': '/', '**': '^'}.get(s.operation, s.operation)
            s.last_expression = f"{s.previous_input} {op_symbol} {s.current_input}"

            if s.operation == '+':
                result = num1 + num2
            elif s.operation == '-':
                result = num1 - num2
            elif s.operation == '*':
                result = num1 * num2
            elif s.operation == '/':
                if num2 == 0:
                    raise ZeroDivisionError
                result = num1 / num2
            elif s.operation == '**':
                result = num1 ** num2
            else:
                return

            result_str = str(int(result)) if result == int(result) else str(round(result, 10))
            s.current_input = result_str
            s.last_expression += f" = {result_str}"

            if s.expression.exists():
                tw(s.expression, text=s.last_expression)

            s.operation = None
            s.reset_next_input = True
            s.update_display()
            gs('dingSmallHigh').play()
        except ZeroDivisionError:
            s.current_input = 'Error'
            s.update_display()
            gs('error').play()
            teck(2.0, s.clear_all)
        except Exception:
            s.current_input = 'Error'
            s.update_display()
            gs('error').play()
            teck(2.0, s.clear_all)

    def clear_all(s):
        s.current_input = '0'
        s.previous_input = ''
        s.operation = None
        s.reset_next_input = False
        s.last_expression = ''
        s.update_display()
        if s.expression.exists():
            tw(s.expression, text='')
        gs('swish').play()

    def toggle_sign(s):
        if s.current_input != '0':
            if s.current_input.startswith('-'):
                s.current_input = s.current_input[1:]
            else:
                s.current_input = '-' + s.current_input
            s.update_display()
            gs('click01').play()

    def percentage(s):
        try:
            s.current_input = str(float(s.current_input) / 100)
            s.update_display()
            gs('dingSmall').play()
        except:
            s.current_input = '0'
            s.update_display()

    def square(s):
        try:
            v = float(s.current_input)
            result = v ** 2
            s.current_input = str(int(result)) if result == int(result) else str(round(result, 10))
            s.update_display()
            gs('dingSmall').play()
        except:
            AR.err('Error!')

    def square_root(s):
        try:
            v = float(s.current_input)
            if v < 0:
                raise ValueError
            result = math.sqrt(v)
            s.current_input = str(int(result)) if result == int(result) else str(round(result, 10))
            s.update_display()
            gs('dingSmall').play()
        except:
            AR.err('Error!')

    def reciprocal(s):
        try:
            v = float(s.current_input)
            if v == 0:
                raise ZeroDivisionError
            result = 1 / v
            s.current_input = str(int(result)) if result == int(result) else str(round(result, 10))
            s.update_display()
            gs('dingSmall').play()
        except:
            AR.err('Error!')

    def factorial(s):
        try:
            v = int(float(s.current_input))
            if v < 0 or v > 170:
                raise ValueError
            result = math.factorial(v)
            s.current_input = str(result)
            s.update_display()
            gs('dingSmall').play()
        except:
            AR.err('Error!')

    def logarithm(s):
        try:
            v = float(s.current_input)
            if v <= 0:
                raise ValueError
            result = math.log10(v)
            s.current_input = str(round(result, 6))
            s.update_display()
            gs('dingSmall').play()
        except:
            AR.err('Error!')

    def power(s):
        s.set_operation('**')

    def pi_value(s):
        s.current_input = str(round(math.pi, 10))
        s.reset_next_input = True
        s.update_display()
        gs('dingSmall').play()

    def e_value(s):
        s.current_input = str(round(math.e, 10))
        s.reset_next_input = True
        s.update_display()
        gs('dingSmall').play()

    def copy_result(s):
        try:
            if CIS():
                from babase import clipboard_set_text
                text = s.last_expression if s.last_expression else s.current_input
                clipboard_set_text(text)
                bui.screenmessage(f'Copied: {text}', color=(0, 1, 0))
                gs('dingSmall').play()
            else:
                AR.err('Clipboard not supported!')
        except Exception as e:
            AR.err(f'Copy error: {str(e)}')

    def send_to_chat(s):
        try:
            if s.last_expression:
                message = f"⚖️ {s.last_expression}"
            else:
                message = f"⚖️ {s.current_input}"
            safe_chat_send(message)
            bui.screenmessage(f'Sent: {message}', color=(0, 1, 0))
            gs('dingSmall').play()
        except Exception as e:
            AR.err(f'Send error: {str(e)}')


# ============================================
# ⚙️ Edit Reaction Window
# ============================================
class EditReactionWindow:
    def __init__(s, source, trigger_code, parent_window=None):
        s.trigger_code = trigger_code
        s.parent_window = parent_window

        s.w = AR.cw(source=source, size=(320, 240), ps=AR.UIS() * 0.4)
        AR.add_close_button(s.w, position=(290, 200))

        current = REACTIONS.get(trigger_code, '')
        current_cd = COOLDOWNS.get(trigger_code, DEFAULT_COOLDOWN)

        tw(parent=s.w, text=f'Edit "%{trigger_code}"', scale=0.85,
           position=(160, 195), h_align='center', color=(1, 1, 0))

        tw(parent=s.w, text='Reply with:', scale=0.6,
           position=(160, 170), h_align='center', color=(0.8, 0.8, 1))

        s.input = tw(
            parent=s.w, text=current, editable=True, scale=0.9,
            position=(40, 130), size=(240, 32), h_align='center',
            color=(0.9, 0.9, 0.9)
        )

        tw(parent=s.w, text='Cooldown (seconds):', scale=0.6,
           position=(160, 100), h_align='center', color=(0.8, 0.8, 1))

        s.cd_input = tw(
            parent=s.w, text=str(current_cd), editable=True, scale=0.9,
            position=(40, 65), size=(240, 32), h_align='center',
            color=(0.9, 0.9, 0.9)
        )

        tw(parent=s.w, text='(هر چند ثانیه یک بار جواب بده)',
           position=(160, 42), scale=0.45,
           h_align='center', color=(0.7, 0.7, 1))

        bw(parent=s.w, label='Save', size=(140, 35),
           position=(90, 5), on_activate_call=Call(s.save),
           color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square')

        gs('swish').play()

    def save(s):
        value = tw(query=s.input).strip().lower()

        if value:
            REACTIONS[s.trigger_code] = value
        else:
            if s.trigger_code in REACTIONS:
                del REACTIONS[s.trigger_code]
            if s.trigger_code in COOLDOWNS:
                del COOLDOWNS[s.trigger_code]
            bui.screenmessage(f'%{s.trigger_code} disabled', color=(1, 0.5, 0))
            save_reactions(REACTIONS)
            save_cooldowns(COOLDOWNS)
            gs('dingSmallHigh').play()
            if s.parent_window:
                try:
                    s.parent_window.build_grid()
                except:
                    pass
            AR.swish(s.w)
            return

        try:
            cd_value = float(tw(query=s.cd_input).strip())
            if cd_value < 0:
                cd_value = 0
        except:
            cd_value = DEFAULT_COOLDOWN

        COOLDOWNS[s.trigger_code] = cd_value

        save_reactions(REACTIONS)
        save_cooldowns(COOLDOWNS)
        bui.screenmessage(f'%{s.trigger_code} → {value} ({cd_value}s)', color=(0, 1, 0))
        gs('dingSmallHigh').play()

        if s.parent_window:
            try:
                s.parent_window.build_grid()
            except:
                pass

        AR.swish(s.w)


# ============================================
# ⚙️ Add New Reaction Window
# ============================================
class AddReactionWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window

        s.w = AR.cw(source=source, size=(320, 260), ps=AR.UIS() * 0.4)
        AR.add_close_button(s.w, position=(290, 220))

        tw(parent=s.w, text='Add New Reaction', scale=0.9,
           position=(160, 215), h_align='center', color=(1, 1, 0))

        tw(parent=s.w, text='When someone uses %:', scale=0.6,
           position=(160, 185), h_align='center', color=(1, 1, 1))
        s.trigger_input = tw(
            parent=s.w, text='', editable=True, scale=0.9,
            position=(40, 150), size=(240, 32), h_align='center',
            color=(0.9, 0.9, 0.9)
        )

        tw(parent=s.w, text='I reply with:', scale=0.6,
           position=(160, 120), h_align='center', color=(1, 1, 1))
        s.response_input = tw(
            parent=s.w, text='', editable=True, scale=0.9,
            position=(40, 85), size=(240, 32), h_align='center',
            color=(0.9, 0.9, 0.9)
        )

        tw(parent=s.w, text='Cooldown (seconds):', scale=0.6,
           position=(160, 55), h_align='center', color=(1, 1, 1))
        s.cd_input = tw(
            parent=s.w, text=str(DEFAULT_COOLDOWN), editable=True, scale=0.9,
            position=(40, 20), size=(240, 32), h_align='center',
            color=(0.9, 0.9, 0.9)
        )

        bw(parent=s.w, label='Add', size=(100, 30),
           position=(110, -15) if False else (110, -5),
           on_activate_call=Call(s.save),
           color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square')

        gs('swish').play()

    def save(s):
        trigger = tw(query=s.trigger_input).strip().lower()
        response = tw(query=s.response_input).strip().lower()

        if not trigger or not response:
            AR.err('Both fields required!')
            return

        try:
            cd_value = float(tw(query=s.cd_input).strip())
            if cd_value < 0:
                cd_value = 0
        except:
            cd_value = DEFAULT_COOLDOWN

        REACTIONS[trigger] = response
        COOLDOWNS[trigger] = cd_value
        save_reactions(REACTIONS)
        save_cooldowns(COOLDOWNS)
        bui.screenmessage(f'%{trigger} → {response} ({cd_value}s)', color=(0, 1, 0))
        gs('dingSmallHigh').play()

        if s.parent_window:
            try:
                s.parent_window.build_grid()
            except:
                pass

        AR.swish(s.w)


# ============================================
# ⚙️ Reaction Editor Window
# ============================================
class ReactionEditorWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(340, 440), ps=AR.UIS() * 0.35)
        AR.add_close_button(s.w, position=(310, 400))

        tw(parent=s.w, text='Auto React', scale=1.0,
           position=(170, 395), h_align='center', color=(0, 1, 1))

        tw(parent=s.w, text=SIGNATURE, scale=0.45,
           position=(170, 378), h_align='center', color=(0.6, 0.6, 0.8))

        s.id_text = tw(parent=s.w, text=f'cid={my_own_client_id or "?"} num={my_own_display_num if my_own_display_num is not None else "?"}',
                       position=(170, 360), scale=0.45,
                       h_align='center', color=(0, 1, 1))

        s.scroll = sw(parent=s.w, size=(300, 180), position=(20, 170))
        s.container = cw(parent=s.scroll, size=(280, 300), background=False)
        s.item_buttons = {}

        s.build_grid()

        bw(parent=s.w, label='+ Add', size=(85, 32),
           position=(20, 130), on_activate_call=Call(s.add_new),
           color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.65)

        bw(parent=s.w, label='Reset', size=(85, 32),
           position=(115, 130), on_activate_call=Call(s.reset_all),
           color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.65)

        bw(parent=s.w, label='Refresh IDs', size=(85, 32),
           position=(210, 130), on_activate_call=Call(s.refresh_ids),
           color=(0.4, 0.3, 0.7), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.65)

        s.toggle_btn = bw(parent=s.w,
                          label='ON' if auto_react_enabled else 'OFF',
                          size=(300, 35), position=(20, 85),
                          on_activate_call=Call(s.toggle),
                          color=(0.2, 0.7, 0.2) if auto_react_enabled else (0.7, 0.2, 0.2),
                          textcolor=(1, 1, 1), button_type='square', text_scale=0.8)

        tw(parent=s.w, text='Auto React is ' + ('ON' if auto_react_enabled else 'OFF'),
           position=(170, 60), scale=0.5, h_align='center', color=(1, 1, 0.8))

        tw(parent=s.w, text='روی هر trigger بزن تا cooldownش رو تنظیم کنی',
           position=(170, 35), scale=0.45, h_align='center', color=(0.7, 0.7, 1))

        gs('swish').play()

    def build_grid(s):
        for child in s.container.get_children():
            child.delete()

        s.item_buttons.clear()

        items = list(REACTIONS.items())
        row_height = 34
        total_h = len(items) * row_height + 20

        for i, (trigger, response) in enumerate(items):
            y = total_h - (i + 1) * row_height

            cd = COOLDOWNS.get(trigger, DEFAULT_COOLDOWN)
            label_text = f'%{trigger} → {response} ({cd}s)'

            btn = bw(parent=s.container, label=label_text,
                     size=(185, 28), position=(5, y),
                     on_activate_call=Call(s.edit_item, trigger),
                     color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1),
                     button_type='square', text_scale=0.55)
            s.item_buttons[trigger] = btn

            bw(parent=s.container, label='X', size=(30, 28), position=(195, y),
               on_activate_call=Call(s.delete_item, trigger),
               color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1),
               button_type='square', text_scale=0.7)

        cw(s.container, size=(280, total_h))

    def refresh_ids(s):
        cid, num = get_my_ids()
        display_num = num if num is not None else "?"
        tw(s.id_text, text=f'cid={cid or "?"} num={display_num}', color=(0, 1, 0))
        bui.screenmessage(f'cid={cid}, num={display_num}', color=(0, 1, 0))
        gs('dingSmallHigh').play()

    def add_new(s):
        AddReactionWindow(s.w, parent_window=s)

    def edit_item(s, trigger):
        EditReactionWindow(s.w, trigger_code=trigger, parent_window=s)

    def delete_item(s, trigger):
        if trigger in REACTIONS:
            del REACTIONS[trigger]
        if trigger in COOLDOWNS:
            del COOLDOWNS[trigger]
        save_reactions(REACTIONS)
        save_cooldowns(COOLDOWNS)
        bui.screenmessage(f'Deleted: %{trigger}', color=(1, 0.5, 0))
        gs('dingSmallLow').play()
        s.build_grid()

    def reset_all(s):
        global REACTIONS, COOLDOWNS
        REACTIONS = dict(DEFAULT_REACTIONS)
        COOLDOWNS = dict(DEFAULT_COOLDOWNS)
        save_reactions(REACTIONS)
        save_cooldowns(COOLDOWNS)
        bui.screenmessage('Reset to defaults!', color=(0, 1, 1))
        gs('dingSmallHigh').play()
        s.build_grid()

    def toggle(s):
        global auto_react_enabled
        auto_react_enabled = not auto_react_enabled

        if auto_react_enabled:
            bw(s.toggle_btn, label='ON', color=(0.2, 0.7, 0.2))
            bui.screenmessage('Auto React ON', color=(0, 1, 0))
        else:
            bw(s.toggle_btn, label='OFF', color=(0.7, 0.2, 0.2))
            bui.screenmessage('Auto React OFF', color=(1, 0.5, 0))
        gs('dingSmall').play()


# ============================================
# 🤖 Auto Buyer Window
# ============================================
class AutoBuyerWindow:
    def __init__(s, source):
        s.source = source
        s.item_buttons = {}

        s.w = AR.cw(source=source, size=(380, 480), ps=AR.UIS() * 0.4)
        AR.add_close_button(s.w, position=(350, 440))

        tw(parent=s.w, text='Auto Buyer', scale=1.1,
           position=(190, 435), h_align='center', color=(0, 1, 1))

        tw(parent=s.w, text=SIGNATURE, scale=0.5,
           position=(190, 415), h_align='center', color=(0.6, 0.6, 0.8))

        status = "ON" if auto_buyer_enabled else "OFF"
        status_color = (0, 1, 0) if auto_buyer_enabled else (1, 0, 0)

        s.status_text = tw(parent=s.w, text=f'Status: {status}',
                           position=(190, 385), h_align='center',
                           scale=0.8, color=status_color)

        s.toggle_btn = bw(parent=s.w,
                          label='Turn OFF' if auto_buyer_enabled else 'Turn ON',
                          size=(140, 30), position=(20, 345),
                          on_activate_call=Call(s.toggle),
                          color=(0.7, 0.2, 0.2) if auto_buyer_enabled else (0.2, 0.7, 0.2),
                          textcolor=(1, 1, 1), button_type='square')

        bw(parent=s.w, label='Reset All', size=(140, 30),
           position=(180, 345), on_activate_call=Call(s.reset_all),
           color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)

        tw(parent=s.w, text='─── Item Limits ───',
           position=(190, 310), h_align='center',
           scale=0.6, color=(1, 1, 0.8))

        s.scroll = sw(parent=s.w, size=(340, 240), position=(20, 40))
        s.container = cw(parent=s.scroll, size=(320, 700), background=False)

        s.build_grid()

        gs('swish').play()

    def build_grid(s):
        for child in s.container.get_children():
            child.delete()

        s.item_buttons.clear()

        items = list(LIMITS.items())
        col_width = 160
        row_height = 34

        num_rows = (len(items) + 1) // 2
        total_h = num_rows * row_height + 80

        for i, (name, limit) in enumerate(items):
            col = i % 2
            row = i // 2

            x = 5 + col * col_width
            y = total_h - (row + 1) * row_height

            if limit == int(limit):
                limit_str = str(int(limit))
            else:
                limit_str = f"{limit:.2f}".rstrip('0').rstrip('.')

            btn = bw(parent=s.container, label=f'{name}: {limit_str}',
                     size=(150, 30), position=(x, y),
                     on_activate_call=Call(s.edit_item, name),
                     color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1),
                     button_type='square', text_scale=0.6)

            s.item_buttons[name] = btn

        cw(s.container, size=(320, total_h))

    def refresh_list(s):
        for name, btn in s.item_buttons.items():
            try:
                if btn and btn.exists():
                    limit = LIMITS.get(name, 0)
                    if limit == int(limit):
                        limit_str = str(int(limit))
                    else:
                        limit_str = f"{limit:.2f}".rstrip('0').rstrip('.')
                    bw(btn, label=f'{name}: {limit_str}')
            except:
                pass

    def toggle(s):
        global auto_buyer_enabled
        auto_buyer_enabled = not auto_buyer_enabled

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
        global LIMITS
        LIMITS = dict(DEFAULT_LIMITS)
        save_limits(LIMITS)
        bui.screenmessage('Reset to defaults!', color=(0, 1, 1))
        gs('dingSmallHigh').play()
        s.refresh_list()


# ============================================
# ⚙️ Edit Limits Window
# ============================================
class EditLimitsWindow:
    def __init__(s, source, item_name, parent_window=None):
        s.item_name = item_name
        s.parent_window = parent_window

        s.w = AR.cw(source=source, size=(300, 180), ps=AR.UIS() * 0.4)
        AR.add_close_button(s.w, position=(270, 140))

        current = str(LIMITS.get(item_name, 0))

        tw(parent=s.w, text=f'Set _ {item_name}', scale=0.9,
           position=(150, 135), h_align='center', color=(1, 1, 0))

        s.input = tw(
            parent=s.w, text=current, editable=True, scale=1.0,
            position=(50, 85), size=(200, 35), h_align='center',
            color=(0.9, 0.9, 0.9)
        )

        tw(parent=s.w, text='(decimal allowed: e.g. 3.5)',
           position=(150, 60), scale=0.5,
           h_align='center', color=(0.7, 0.7, 1))

        bw(parent=s.w, label='Save', size=(120, 35),
           position=(90, 15), on_activate_call=Call(s.save),
           color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1), button_type='square')

        gs('swish').play()

    def save(s):
        try:
            value = float(tw(query=s.input).strip())
        except:
            AR.err('Invalid number!')
            return

        LIMITS[s.item_name] = value
        save_limits(LIMITS)
        bui.screenmessage(f'_{s.item_name} = {value}', color=(0, 1, 0))
        gs('dingSmallHigh').play()

        if s.parent_window:
            try:
                s.parent_window.refresh_list()
            except:
                pass

        AR.swish(s.w)


# ============================================
# 🤖 Auto Buyer Logic
# ============================================
SELL_PATTERN = re.compile(r'💰Sell ID:\s*(\w+)')

# ✅ پترن اصلاح شده (با پشتیبانی از ? Ok=1)
BUY_PATTERN = re.compile(
    r'(\w+):\s*💳Buy\s*<\s*([\d,]+)\s+(\w+)\s*\([^)]+\)\s*>\s*for\s*([\d,]+)\s*coins(?:\?.*)?'
)

BID_PATTERN = re.compile(r'\bb\s+(s\d+)\b', re.IGNORECASE)


def process_sell(item_id):
    safe_chat_send(f"b {item_id}")


def process_buy(item_id, count, item_name, total_price):
    # ✅ اگه آیتم ناشناخته بود، 0 بفرست
    if item_name not in LIMITS:
        safe_chat_send("0 ")
        return

    bid_key = f"{item_id}_{item_name}_{count}_{total_price}"
    if bid_key in processed_buy_ids:
        return
    processed_buy_ids.add(bid_key)

    if len(processed_buy_ids) > 200:
        processed_buy_ids.clear()

    if count <= 0:
        safe_chat_send("0 ")
        return

    unit_price = total_price / count
    limit = LIMITS[item_name]

    if unit_price <= limit:
        safe_chat_send("1 ")
        gs('dingSmallHigh').play()
    else:
        safe_chat_send("0 ")


def process_bid(item_id):
    if not auto_buyer_enabled:
        return

    try:
        key = f"bid_{item_id}"
        if key in processed_bids:
            return
        processed_bids.add(key)

        safe_chat_send(f"b {item_id}")
        gs('dingSmall').play()
    except Exception as e:
        print(f"Bid error: {e}")


# ============================================
# 🎯 Auto-React Logic
# ============================================
def check_reaction(msg):
    global my_own_client_id, my_own_display_num

    if not auto_react_enabled:
        return

    if my_own_client_id is None and my_own_display_num is None:
        get_my_ids()

    try:
        sender = None
        content = msg
        if ': ' in msg:
            parts = msg.split(': ', 1)
            sender = parts[0].strip()
            content = parts[1].strip()

        content_lower = content.lower()

        for trigger, response in REACTIONS.items():
            trigger_lower = trigger.lower()

            is_target_me = False

            if my_own_client_id:
                pattern1 = rf'%\s*{re.escape(trigger_lower)}\s+(\d+)'
                m1 = re.search(pattern1, content_lower)
                if m1 and int(m1.group(1)) == my_own_client_id:
                    is_target_me = True

            if not is_target_me and my_own_display_num is not None:
                pattern2 = rf'\b{re.escape(trigger_lower)}\s+(\d+)'
                m2 = re.search(pattern2, content_lower)
                if m2 and int(m2.group(1)) == my_own_display_num:
                    is_target_me = True

            if is_target_me:
                cd_time = COOLDOWNS.get(trigger, DEFAULT_COOLDOWN)
                current_time = time.time()
                cd_key = f"{trigger_lower}_{sender or 'unknown'}"
                last_time = react_cooldown.get(cd_key, 0)

                if current_time - last_time < cd_time:
                    break

                react_cooldown[cd_key] = current_time

                if len(react_cooldown) > 50:
                    now = time.time()
                    to_del = [k for k, v in react_cooldown.items() if now - v > 300]
                    for k in to_del:
                        del react_cooldown[k]

                safe_chat_send(response)
                gs('dingSmall').play()
                break

    except Exception as e:
        print(f"React error: {e}")


# ============================================
# 🎯 Check Chat
# ============================================
def check_chat():
    try:
        messages = GCM()

        if messages:
            # ✅ 5 پیام آخر
            for msg in messages[-5:]:
                if msg in seen_messages_time:
                    continue

                seen_messages.append(msg)
                seen_messages_time[msg] = time.time()

                # چک واکنش
                check_reaction(msg)

                if not auto_buyer_enabled:
                    continue

                # چک پیام فروش
                m = SELL_PATTERN.search(msg)
                if m:
                    process_sell(m.group(1))
                    continue

                # چک b sXXX
                is_mine = False
                if my_own_name:
                    if msg.startswith(f"{my_own_name}:") or msg.startswith(f"{my_own_name} :"):
                        is_mine = True

                if not is_mine:
                    m2 = BID_PATTERN.search(msg)
                    if m2:
                        item_id = m2.group(1)
                        process_bid(item_id)
                        continue

                # چک پیام خرید
                m = BUY_PATTERN.search(msg)
                if m:
                    process_buy(
                        m.group(1),
                        int(m.group(2).replace(',', '')),
                        m.group(3).lower(),
                        int(m.group(4).replace(',', ''))
                    )
                    continue

            # ✅ پاکسازی پیام‌های قدیمی (بیشتر از 30 ثانیه)
            now = time.time()
            to_del = [m for m, t in seen_messages_time.items() if now - t > 30]
            for m in to_del:
                del seen_messages_time[m]
                try:
                    seen_messages.remove(m)
                except:
                    pass

    except Exception as e:
        print(f"Chat error: {e}")

    teck(0.05, check_chat)


# ============================================
# 🧮 Calculator Chat Detection
# ============================================
CALC_PATTERN = re.compile(
    r'^(\d+(?:\.\d+)?)\s*([\+\-\*\/\^×÷xX])\s*(\d+(?:\.\d+)?)$'
)


def detect_calculation(message):
    expression = message.replace('×', '*').replace('÷', '/')
    expression = expression.replace('x', '*').replace('X', '*')

    match = CALC_PATTERN.match(expression.strip())
    if not match:
        return None

    num1 = float(match.group(1))
    op = match.group(2)
    num2 = float(match.group(3))

    try:
        if op == '+':
            result = num1 + num2
        elif op == '-':
            result = num1 - num2
        elif op == '*':
            result = num1 * num2
        elif op == '/':
            if num2 == 0:
                return None
            result = num1 / num2
        elif op == '^':
            result = num1 ** num2
        else:
            return None

        result_str = str(int(result)) if result == int(result) else str(round(result, 10))
        op_display = {'+': '+', '-': '-', '*': '×', '/': '÷', '^': '^'}.get(op, op)
        return f"⚖️ {match.group(1)} {op_display} {match.group(3)} = {result_str}"
    except:
        return None


# ============================================
# 🎯 Main Plugin
# ============================================
# ba_meta require api 9
# ba_meta export babase.Plugin
class byMahyar(Plugin):
    def __init__(s):
        global my_own_name, my_own_client_id, my_own_display_num
        s.seen_calc = []
        s.seen_calc_set = set()

        try:
            my_own_name = APP.plus.get_v1_account_name()
        except:
            my_own_name = None

        from bauiv1lib import party
        o = party.PartyWindow.__init__

        def e(self, *a, **k):
            r = o(self, *a, **k)

            teck(0.5, get_my_ids)

            b_react = AR.bw(
                position=(self._width - 100, self._height - 100),
                parent=self._root_widget,
                size=(80, 25),
                label='React',
                color=(0.8, 0.5, 0.2)
            )
            bw(b_react, on_activate_call=Call(ReactionEditorWindow, b_react))

            b_calc = AR.bw(
                position=(self._width - 100, self._height - 140),
                parent=self._root_widget,
                size=(80, 25),
                label='Math',
                color=(0.8, 0.2, 0.7)
            )
            bw(b_calc, on_activate_call=Call(Calculator, b_calc))

            b_auto = AR.bw(
                position=(self._width - 100, self._height - 180),
                parent=self._root_widget,
                size=(80, 25),
                label='AutoBuy',
                color=(0.2, 0.6, 0.8)
            )
            bw(b_auto, on_activate_call=Call(AutoBuyerWindow, b_auto))

            return r

        party.PartyWindow.__init__ = e

        teck(3.0, lambda: bui.screenmessage(CREATOR, color=(0, 1, 1)))

        teck(0.05, check_chat)
        teck(0.1, s.check_calc)
        teck(20.0, s.update_ids_loop)

    def update_ids_loop(s):
        get_my_ids()
        teck(20.0, s.update_ids_loop)

    def check_calc(s):
        try:
            messages = GCM()
            if messages:
                for msg in messages[-5:]:
                    if msg in s.seen_calc_set:
                        continue
                    s.seen_calc_set.add(msg)
                    s.seen_calc.append(msg)

                    if ': ' in msg:
                        _, content = msg.split(': ', 1)
                        content = content.strip()

                        result = detect_calculation(content)
                        if result:
                            safe_chat_send(result)

                if len(s.seen_calc) > 50:
                    old = s.seen_calc[:-50]
                    for o in old:
                        s.seen_calc_set.discard(o)
                    s.seen_calc[:] = s.seen_calc[-50:]
        except Exception:
            pass

        teck(0.1, s.check_calc)
