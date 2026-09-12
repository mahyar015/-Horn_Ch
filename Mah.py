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
    get_chat_messages as GCM
)
import math
import re
import time
import bauiv1 as bui
from babase import app

SIGNATURE = "By Mahyar"

# ============================================
# ⚙️ لیست کامل آیتم‌ها
# ============================================
DEFAULT_LIMITS = {
    'vip': 6.0, 'cbb': 3.0, 'cba': 3.0, 'h': 2.0,
    'pun': 2.0, 'sh': 2.0, 'sl': 2.0, 'fr': 2.0,
    'u': 2.0, 'sp': 1.0, 'z': 1.0, 'g': 2.0,
    'd': 2.0, 'cu': 2.0, 'k': 3.0, 're': 2.0,
    'sm': 2.0, 'fly': 2.0, 'fl': 2.0, 'e': 1.0,
    'hug': 2.0, 'bot': 3.0, 'spin': 4.0, 'fire': 3.0,
    'efs': 2.0, 'spike': 3.0, 'spidy': 3.0, 'rich': 1.0,
    'fish': 5.0, 'sol': 3.0, 'plasma': 5.0, 'hat': 2.0,
    'tag': 2.0, 'sig': 2.0,
}

DEFAULT_UNKNOWN = 999999


# ============================================
# ⚙️ ذخیره/بازیابی مکان دکمه‌ها
# ============================================
def get_pos(key, default):
    try:
        return app.config.get(f'mahyar_btn_{key}', default)
    except:
        return default


def save_pos(key, pos):
    try:
        app.config[f'mahyar_btn_{key}'] = pos
        app.config.commit()
    except:
        pass


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


LIMITS = get_limits()
_default = DEFAULT_UNKNOWN
auto_buyer_enabled = True

seen_messages = []
seen_messages_set = set()
processed_buy_ids = set()

# رفرنس دکمه‌های اصلی برای جابجایی لحظه‌ای
LIVE_BUTTONS = {}  # {'math': widget, 'auto': widget}


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
# 🎯 Position Editor
# ============================================
class PositionEditor:
    def __init__(s, source, btn_key, btn_name):
        s.btn_key = btn_key
        s.btn_name = btn_name

        s.w = AR.cw(source=source, size=(340, 380), ps=AR.UIS() * 0.4)
        AR.add_close_button(s.w, position=(310, 340))

        tw(parent=s.w, text=f'Move: {btn_name}', scale=1.0,
           position=(170, 335), h_align='center', color=(1, 1, 0))

        tw(parent=s.w, text='Use arrows to move - live update',
           position=(170, 310), scale=0.55,
           h_align='center', color=(0.8, 0.8, 1))

        s.pos_x, s.pos_y = get_pos(btn_key, (-100, -80))

        s.pos_text = tw(parent=s.w, text=f'X: {s.pos_x}   Y: {s.pos_y}',
                        position=(170, 275), scale=0.8,
                        h_align='center', color=(0, 1, 1))

        bw(parent=s.w, label='↑', size=(70, 50), position=(135, 215),
           on_activate_call=Call(s.move, 'up'),
           color=(0.3, 0.5, 0.8), textcolor=(1, 1, 1),
           button_type='square', text_scale=1.5)

        bw(parent=s.w, label='←', size=(70, 50), position=(55, 155),
           on_activate_call=Call(s.move, 'left'),
           color=(0.3, 0.5, 0.8), textcolor=(1, 1, 1),
           button_type='square', text_scale=1.5)

        bw(parent=s.w, label='↓', size=(70, 50), position=(135, 155),
           on_activate_call=Call(s.move, 'down'),
           color=(0.3, 0.5, 0.8), textcolor=(1, 1, 1),
           button_type='square', text_scale=1.5)

        bw(parent=s.w, label='→', size=(70, 50), position=(215, 155),
           on_activate_call=Call(s.move, 'right'),
           color=(0.3, 0.5, 0.8), textcolor=(1, 1, 1),
           button_type='square', text_scale=1.5)

        tw(parent=s.w, text='Step Size:', scale=0.7,
           position=(30, 110), color=(1, 1, 1))

        s.step = 5
        s.step_text = tw(parent=s.w, text=f'{s.step} px', scale=0.7,
                        position=(150, 110), color=(1, 1, 0))

        bw(parent=s.w, label='1', size=(60, 30), position=(30, 70),
           on_activate_call=Call(s.set_step, 1),
           color=(0.5, 0.5, 0.7), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)
        bw(parent=s.w, label='5', size=(60, 30), position=(100, 70),
           on_activate_call=Call(s.set_step, 5),
           color=(0.4, 0.5, 0.7), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)
        bw(parent=s.w, label='10', size=(60, 30), position=(170, 70),
           on_activate_call=Call(s.set_step, 10),
           color=(0.4, 0.6, 0.8), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)
        bw(parent=s.w, label='20', size=(60, 30), position=(240, 70),
           on_activate_call=Call(s.set_step, 20),
           color=(0.3, 0.7, 0.8), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)

        bw(parent=s.w, label='Reset Position', size=(150, 35),
           position=(95, 25), on_activate_call=s.reset_pos,
           color=(0.8, 0.2, 0.2), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)

        gs('swish').play()

    def update_live_button(s):
        """آپدیت لحظه‌ای مکان دکمه اصلی"""
        global LIVE_BUTTONS
        try:
            if s.btn_key in LIVE_BUTTONS:
                btn = LIVE_BUTTONS[s.btn_key]
                if btn and btn.exists():
                    # ریفرش موقعیت
                    pass  # دکمه‌های اصلی رو با تابع refresh استفاده میکنیم
        except:
            pass

    def move(s, direction):
        step = s.step

        if direction == 'left':
            s.pos_x -= step
        elif direction == 'right':
            s.pos_x += step
        elif direction == 'up':
            s.pos_y += step
        elif direction == 'down':
            s.pos_y -= step

        save_pos(s.btn_key, (s.pos_x, s.pos_y))
        tw(s.pos_text, text=f'X: {s.pos_x}   Y: {s.pos_y}')

        # آپدیت لحظه‌ای دکمه‌های اصلی
        refresh_main_buttons()

        gs('click01').play()

    def set_step(s, value):
        s.step = value
        tw(s.step_text, text=f'{value} px')
        gs('dingSmall').play()

    def reset_pos(s):
        if s.btn_key == 'math':
            default = (-100, -80)
        else:
            default = (-100, -48)
        s.pos_x, s.pos_y = default
        save_pos(s.btn_key, default)
        tw(s.pos_text, text=f'X: {s.pos_x}   Y: {s.pos_y}')
        refresh_main_buttons()
        push('Position reset!', color=(0, 1, 1))
        gs('dingSmallHigh').play()


# ============================================
# 🔄 تابع ریفرش دکمه‌های اصلی
# ============================================
def refresh_main_buttons():
    """دکمه‌های اصلی رو جابجا میکنه (لحظه‌ای)"""
    global LIVE_BUTTONS
    try:
        for key, btn in LIVE_BUTTONS.items():
            if btn and btn.exists():
                pos_x, pos_y = get_pos(key, (-100, -80))
                # تلاش برای جابجایی
                try:
                    bw(btn, position=(btn.get_parent_window()._width + pos_x,
                                      btn.get_parent_window()._height + pos_y))
                except:
                    pass
    except Exception as e:
        print(f"Refresh error: {e}")


# ============================================
# 🧮 Calculator
# ============================================
class Calculator:
    def __init__(s, source):
        s.w = AR.cw(source=source, size=(340, 440), ps=AR.UIS() * 0.4)
        AR.add_close_button(s.w, position=(310, 400))

        tw(parent=s.w, text='Math Engine', scale=0.9,
           position=(170, 395), h_align='center', color=(1, 0.5, 0.9))

        tw(parent=s.w, text=SIGNATURE, scale=0.5,
           position=(170, 380), h_align='center', color=(0.6, 0.6, 0.8))

        s.display = tw(parent=s.w, text='0', scale=1.2,
                       position=(170, 348), h_align='center',
                       color=(0.3, 1, 0.7), maxwidth=310)

        s.expression = tw(parent=s.w, text='', scale=0.55,
                          position=(170, 328), h_align='center',
                          color=(0.9, 0.7, 1), maxwidth=310)

        s.current_input = '0'
        s.previous_input = ''
        s.operation = None
        s.reset_next_input = False
        s.last_expression = ''

        bw(parent=s.w, label='Copy', size=(150, 28),
           position=(15, 295), on_activate_call=Call(s.copy_result),
           color=(0.4, 0.3, 0.7), textcolor=(1, 1, 1), button_type='square')
        bw(parent=s.w, label='Send', size=(150, 28),
           position=(175, 295), on_activate_call=Call(s.send_to_chat),
           color=(0.7, 0.4, 0.2), textcolor=(1, 1, 1), button_type='square')

        bw(parent=s.w, label='Edit Position', size=(150, 28),
           position=(95, 260), on_activate_call=Call(PositionEditor, s.w, 'math', 'Math Button'),
           color=(0.5, 0.3, 0.7), textcolor=(1, 1, 1), button_type='square', text_scale=0.7)

        row_y = 220
        row_gap = 36
        btn_h = 30

        rows = [
            [('AC', s.clear_all, (15, row_y), (48, btn_h), (0.7, 0.2, 0.3)),
             ('+/-', s.toggle_sign, (70, row_y), (48, btn_h), (0.3, 0.4, 0.7)),
             ('%', s.percentage, (125, row_y), (48, btn_h), (0.3, 0.4, 0.7)),
             ('R', s.square_root, (180, row_y), (48, btn_h), (0.3, 0.4, 0.7)),
             ('x2', s.square, (235, row_y), (48, btn_h), (0.3, 0.4, 0.7)),
             ('/', lambda: s.set_operation('/'), (290, row_y), (35, btn_h), (0.8, 0.6, 0.1))],
            [('7', lambda: s.append_number('7'), (15, row_y-row_gap), (48, btn_h), (0.25, 0.3, 0.45)),
             ('8', lambda: s.append_number('8'), (70, row_y-row_gap), (48, btn_h), (0.25, 0.3, 0.45)),
             ('9', lambda: s.append_number('9'), (125, row_y-row_gap), (48, btn_h), (0.25, 0.3, 0.45)),
             ('×', lambda: s.set_operation('*'), (180, row_y-row_gap), (48, btn_h), (0.8, 0.6, 0.1)),
             ('DEL', s.backspace, (235, row_y-row_gap), (48, btn_h), (0.6, 0.15, 0.25)),
             ('1/x', s.reciprocal, (290, row_y-row_gap), (35, btn_h), (0.3, 0.4, 0.7))],
            [('4', lambda: s.append_number('4'), (15, row_y-row_gap*2), (48, btn_h), (0.25, 0.3, 0.45)),
             ('5', lambda: s.append_number('5'), (70, row_y-row_gap*2), (48, btn_h), (0.25, 0.3, 0.45)),
             ('6', lambda: s.append_number('6'), (125, row_y-row_gap*2), (48, btn_h), (0.25, 0.3, 0.45)),
             ('-', lambda: s.set_operation('-'), (180, row_y-row_gap*2), (48, btn_h), (0.8, 0.6, 0.1)),
             ('n!', s.factorial, (235, row_y-row_gap*2), (48, btn_h), (0.3, 0.4, 0.7)),
             ('log', s.logarithm, (290, row_y-row_gap*2), (35, btn_h), (0.3, 0.4, 0.7))],
            [('1', lambda: s.append_number('1'), (15, row_y-row_gap*3), (48, btn_h), (0.25, 0.3, 0.45)),
             ('2', lambda: s.append_number('2'), (70, row_y-row_gap*3), (48, btn_h), (0.25, 0.3, 0.45)),
             ('3', lambda: s.append_number('3'), (125, row_y-row_gap*3), (48, btn_h), (0.25, 0.3, 0.45)),
             ('+', lambda: s.set_operation('+'), (180, row_y-row_gap*3), (48, btn_h), (0.8, 0.6, 0.1)),
             ('^', s.power, (235, row_y-row_gap*3), (48, btn_h), (0.3, 0.4, 0.7)),
             ('pi', s.pi_value, (290, row_y-row_gap*3), (35, btn_h), (0.5, 0.3, 0.7))],
            [('0', lambda: s.append_number('0'), (15, row_y-row_gap*4), (103, btn_h), (0.25, 0.3, 0.45)),
             ('.', s.add_decimal, (125, row_y-row_gap*4), (48, btn_h), (0.25, 0.3, 0.45)),
             ('=', s.calculate, (180, row_y-row_gap*4), (48, btn_h), (0.15, 0.65, 0.35)),
             ('e', s.e_value, (235, row_y-row_gap*4), (48, btn_h), (0.5, 0.3, 0.7)),
             ('!', s.factorial, (290, row_y-row_gap*4), (35, btn_h), (0.3, 0.4, 0.7))],
        ]

        for row in rows:
            for label, callback, pos, size, color in row:
                bw(parent=s.w, label=label, size=size, position=pos,
                   on_activate_call=callback, color=color,
                   textcolor=(1, 1, 1), button_type='square', text_scale=0.75)

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
                push(f'Copied: {text}', color=(0, 1, 0))
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
            CM(message)
            push(f'Sent: {message}', color=(0, 1, 0))
            gs('dingSmall').play()
        except Exception as e:
            AR.err(f'Send error: {str(e)}')


# ============================================
# ⚙️ Edit Limits Window
# ============================================
class EditLimitsWindow:
    def __init__(s, source, item_name):
        s.item_name = item_name

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
        push(f'_{s.item_name} = {value}', color=(0, 1, 0))
        gs('dingSmallHigh').play()
        AR.swish(s.w)


# ============================================
# 🤖 Auto Buyer Window
# ============================================
class AutoBuyerWindow:
    def __init__(s, source):
        s.source = source

        s.w = AR.cw(source=source, size=(380, 520), ps=AR.UIS() * 0.4)
        AR.add_close_button(s.w, position=(350, 480))

        tw(parent=s.w, text='Auto Buyer', scale=1.1,
           position=(190, 475), h_align='center', color=(0, 1, 1))

        tw(parent=s.w, text=SIGNATURE, scale=0.5,
           position=(190, 455), h_align='center', color=(0.6, 0.6, 0.8))

        status = "ON" if auto_buyer_enabled else "OFF"
        status_color = (0, 1, 0) if auto_buyer_enabled else (1, 0, 0)

        s.status_text = tw(parent=s.w, text=f'Status: {status}',
                           position=(190, 425), h_align='center',
                           scale=0.8, color=status_color)

        s.toggle_btn = bw(parent=s.w,
                          label='Turn OFF' if auto_buyer_enabled else 'Turn ON',
                          size=(140, 30), position=(20, 385),
                          on_activate_call=Call(s.toggle),
                          color=(0.7, 0.2, 0.2) if auto_buyer_enabled else (0.2, 0.7, 0.2),
                          textcolor=(1, 1, 1), button_type='square')

        bw(parent=s.w, label='Reset All', size=(140, 30),
           position=(180, 385), on_activate_call=Call(s.reset_all),
           color=(0.7, 0.3, 0.2), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)

        bw(parent=s.w, label='Edit AutoBuy Position', size=(300, 30),
           position=(20, 345), on_activate_call=Call(s.edit_auto_pos),
           color=(0.5, 0.3, 0.7), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.7)

        tw(parent=s.w, text='─── Item Limits ───',
           position=(190, 310), h_align='center',
           scale=0.6, color=(1, 1, 0.8))

        # ✅ اسکرول‌ویجت با اندازه مناسب
        s.scroll = sw(parent=s.w, size=(340, 240), position=(20, 40))
        s.container = cw(parent=s.scroll, size=(320, 700), background=False)

        s.build_grid()

        gs('swish').play()

    def build_grid(s):
        for child in s.container.get_children():
            child.delete()

        items = list(LIMITS.items())
        col_width = 160
        row_height = 34

        num_rows = (len(items) + 1) // 2
        # ✅ ارتفاع بیشتر برای جلوگیری از قطع شدن
        total_h = num_rows * row_height + 40

        for i, (name, limit) in enumerate(items):
            col = i % 2
            row = i // 2

            x = 5 + col * col_width
            y = total_h - (row + 1) * row_height

            if limit == int(limit):
                limit_str = str(int(limit))
            else:
                limit_str = f"{limit:.2f}".rstrip('0').rstrip('.')

            bw(parent=s.container, label=f'{name}: {limit_str}',
               size=(150, 30), position=(x, y),
               on_activate_call=Call(s.edit_item, name),
               color=(0.25, 0.4, 0.6), textcolor=(1, 1, 1),
               button_type='square', text_scale=0.6)

        # ✅ تنظیم اندازه کانتینر با ارتفاع بیشتر
        cw(s.container, size=(320, total_h))

    def toggle(s):
        global auto_buyer_enabled
        auto_buyer_enabled = not auto_buyer_enabled

        if auto_buyer_enabled:
            bw(s.toggle_btn, label='Turn OFF', color=(0.7, 0.2, 0.2))
            tw(s.status_text, text='Status: ON', color=(0, 1, 0))
            push('Auto Buyer ON', color=(0, 1, 0))
        else:
            bw(s.toggle_btn, label='Turn ON', color=(0.2, 0.7, 0.2))
            tw(s.status_text, text='Status: OFF', color=(1, 0, 0))
            push('Auto Buyer OFF', color=(1, 0.5, 0))
        gs('dingSmall').play()

    def edit_item(s, name):
        EditLimitsWindow(s.w, item_name=name)
        teck(3.0, s.refresh_after_edit)

    def edit_auto_pos(s):
        PositionEditor(s.w, 'auto', 'AutoBuy Button')

    def refresh_after_edit(s):
        if s.w.exists():
            s.build_grid()

    def reset_all(s):
        global LIMITS
        LIMITS = dict(DEFAULT_LIMITS)
        save_limits(LIMITS)
        push('Reset to defaults!', color=(0, 1, 1))
        gs('dingSmallHigh').play()
        s.build_grid()


# ============================================
# 🤖 Auto Buyer Logic
# ============================================
SELL_PATTERN = re.compile(r'💰Sell ID:\s*(\w+)')
BUY_PATTERN = re.compile(
    r'(\w+):\s*💳Buy\s*<\s*([\d,]+)\s+(\w+)\s*\([^)]+\)\s*>\s*for\s*([\d,]+)\s*coins'
)


def process_sell(item_id):
    CM(f"b {item_id}")


def process_buy(item_id, count, item_name, total_price):
    bid_key = f"{item_id}_{item_name}_{count}_{total_price}"
    if bid_key in processed_buy_ids:
        return
    processed_buy_ids.add(bid_key)

    if len(processed_buy_ids) > 200:
        processed_buy_ids.clear()

    if count <= 0:
        CM("0 ")
        return

    unit_price = total_price / count
    limit = LIMITS.get(item_name, _default)

    if unit_price <= limit:
        CM("1 ")
        push(f"BUY {item_name} @ {unit_price:.2f} <= {limit}", color=(0, 1, 0))
        gs('dingSmallHigh').play()
    else:
        CM("0 ")
        push(f"SKIP {item_name} @ {unit_price:.2f} > {limit}", color=(1, 0.5, 0))


def check_chat():
    if not auto_buyer_enabled:
        teck(0.05, check_chat)
        return

    try:
        messages = GCM()
        if messages:
            for msg in messages[-3:]:
                if msg in seen_messages_set:
                    continue
                seen_messages_set.add(msg)
                seen_messages.append(msg)

                m = SELL_PATTERN.search(msg)
                if m:
                    process_sell(m.group(1))
                    continue

                m = BUY_PATTERN.search(msg)
                if m:
                    process_buy(
                        m.group(1),
                        int(m.group(2).replace(',', '')),
                        m.group(3).lower(),
                        int(m.group(4).replace(',', ''))
                    )

            if len(seen_messages) > 200:
                old = seen_messages[:-200]
                for o in old:
                    seen_messages_set.discard(o)
                seen_messages[:] = seen_messages[-200:]
    except Exception:
        pass

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
        s.seen_calc = []
        s.seen_calc_set = set()

        from bauiv1lib import party
        o = party.PartyWindow.__init__

        def e(self, *a, **k):
            r = o(self, *a, **k)

            math_x, math_y = get_pos('math', (-100, -80))
            auto_x, auto_y = get_pos('auto', (-100, -48))

            # دکمه Math
            b_calc = AR.bw(
                position=(self._width + math_x, self._height + math_y),
                parent=self._root_widget,
                size=(85, 25),
                label='Math',
                color=(0.8, 0.2, 0.7)
            )
            bw(b_calc, on_activate_call=Call(Calculator, b_calc))

            # دکمه AutoBuy
            b_auto = AR.bw(
                position=(self._width + auto_x, self._height + auto_y),
                parent=self._root_widget,
                size=(85, 25),
                label='AutoBuy',
                color=(0.2, 0.6, 0.8)
            )
            bw(b_auto, on_activate_call=Call(AutoBuyerWindow, b_auto))

            # ✅ ذخیره رفرنس‌ها برای جابجایی لحظه‌ای
            global LIVE_BUTTONS
            LIVE_BUTTONS['math'] = b_calc
            LIVE_BUTTONS['auto'] = b_auto

            return r

        party.PartyWindow.__init__ = e

        teck(3.0, lambda: push(SIGNATURE, color=(1, 0.1, 0.1)))
        teck(5.0, lambda: push("Math + AutoBuy", color=(0, 1, 1)))

        teck(0.05, check_chat)
        teck(0.1, s.check_calc)

    def check_calc(s):
        try:
            messages = GCM()
            if messages:
                for msg in messages[-3:]:
                    if msg in s.seen_calc_set:
                        continue
                    s.seen_calc_set.add(msg)
                    s.seen_calc.append(msg)

                    if ': ' in msg:
                        _, content = msg.split(': ', 1)
                        content = content.strip()

                        result = detect_calculation(content)
                        if result:
                            CM(result)

                if len(s.seen_calc) > 100:
                    old = s.seen_calc[:-100]
                    for o in old:
                        s.seen_calc_set.discard(o)
                    s.seen_calc[:] = s.seen_calc[-100:]
        except Exception:
            pass

        teck(0.1, s.check_calc)
