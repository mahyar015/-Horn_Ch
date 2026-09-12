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
    clipboard_is_supported as CIS
)
from bascenev1 import (
    chatmessage as CM,
    screenmessage as push,
)
import math

class AR:
    @classmethod
    def UIS(c=0):
        i = APP.ui_v1.uiscale
        return [1.5,1.1,0.8][0 if i == uis.SMALL else 1 if i == uis.MEDIUM else 2]

    @classmethod
    def add_close_button(c, window, position=(10, 10)):
        return bw(
            parent=window,
            size=(30, 30),
            position=position,
            label='X',
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=Call(c.swish, t=window)
        )

    @classmethod
    def bw(c,**k):
        return bw(**k, textcolor=(1,1,1), enable_sound=False, button_type='square')

    @classmethod
    def cw(c,source,ps=0,**k):
        o = source.get_screen_space_center() if source else None
        r = cw(
            **k,
            scale=c.UIS()+ps,
            transition='in_scale',
            color=(0.18,0.18,0.18),
            parent=gsw('overlay_stack'),
            scale_origin_stack_offset=o
        )
        cw(r,on_outside_click_call=Call(c.swish,t=r))
        return r

    swish = lambda c=0,t=0: (gs('swish').play(),cw(t,transition='out_scale') if t else t)
    err = lambda t: (gs('block').play(),push(t,color=(1,1,0)))


class Calculator:
    def __init__(s, source):
        s.w = AR.cw(source=source, size=(420, 400), ps=AR.UIS()*0.7)
        AR.add_close_button(s.w, position=(390, 360))

        # Title
        tw(
            parent=s.w, text='🧮 Calculator', scale=1.2,
            position=(210, 355), h_align='center', color=(0, 1, 1)
        )

        # Display
        s.display = tw(
            parent=s.w, text='0', scale=1.4,
            position=(210, 310), h_align='center',
            color=(1, 1, 1), maxwidth=380
        )

        # Variables
        s.current_input = '0'
        s.previous_input = ''
        s.operation = None
        s.reset_next_input = False

        # Action buttons
        bw(
            parent=s.w, label='Copy', size=(180, 35),
            position=(20, 260), on_activate_call=Call(s.copy_result),
            color=(0.3, 0.6, 0.8), textcolor=(1, 1, 1), button_type='square'
        )
        bw(
            parent=s.w, label='Send to Chat', size=(180, 35),
            position=(220, 260), on_activate_call=Call(s.send_to_chat),
            color=(0.2, 0.7, 0.4), textcolor=(1, 1, 1), button_type='square'
        )

        # Row 1
        buttons_row1 = [
            ('C', s.clear_all, (20, 210), (60, 35), (1, 0.4, 0.4)),
            ('±', s.toggle_sign, (90, 210), (60, 35), (0.5, 0.7, 1)),
            ('%', s.percentage, (160, 210), (60, 35), (0.5, 0.7, 1)),
            ('√', s.square_root, (230, 210), (60, 35), (0.5, 0.7, 1)),
            ('x²', s.square, (300, 210), (60, 35), (0.5, 0.7, 1)),
            ('÷', lambda: s.set_operation('/'), (370, 210), (30, 35), (1, 0.8, 0.3)),
        ]
        for label, callback, pos, size, color in buttons_row1:
            bw(parent=s.w, label=label, size=size, position=pos,
               on_activate_call=callback, color=color,
               textcolor=(1, 1, 1), button_type='square', text_scale=0.9)

        # Row 2
        buttons_row2 = [
            ('7', lambda: s.append_number('7'), (20, 165), (60, 35), (0.4, 0.4, 0.6)),
            ('8', lambda: s.append_number('8'), (90, 165), (60, 35), (0.4, 0.4, 0.6)),
            ('9', lambda: s.append_number('9'), (160, 165), (60, 35), (0.4, 0.4, 0.6)),
            ('×', lambda: s.set_operation('*'), (230, 165), (60, 35), (1, 0.8, 0.3)),
            ('⌫', s.backspace, (300, 165), (60, 35), (0.8, 0.3, 0.3)),
            ('1/x', s.reciprocal, (370, 165), (30, 35), (0.5, 0.7, 1)),
        ]
        for label, callback, pos, size, color in buttons_row2:
            bw(parent=s.w, label=label, size=size, position=pos,
               on_activate_call=callback, color=color,
               textcolor=(1, 1, 1), button_type='square', text_scale=0.9)

        # Row 3
        buttons_row3 = [
            ('4', lambda: s.append_number('4'), (20, 120), (60, 35), (0.4, 0.4, 0.6)),
            ('5', lambda: s.append_number('5'), (90, 120), (60, 35), (0.4, 0.4, 0.6)),
            ('6', lambda: s.append_number('6'), (160, 120), (60, 35), (0.4, 0.4, 0.6)),
            ('-', lambda: s.set_operation('-'), (230, 120), (60, 35), (1, 0.8, 0.3)),
            ('n!', s.factorial, (300, 120), (60, 35), (0.5, 0.7, 1)),
            ('log', s.logarithm, (370, 120), (30, 35), (0.5, 0.7, 1)),
        ]
        for label, callback, pos, size, color in buttons_row3:
            bw(parent=s.w, label=label, size=size, position=pos,
               on_activate_call=callback, color=color,
               textcolor=(1, 1, 1), button_type='square', text_scale=0.9)

        # Row 4
        buttons_row4 = [
            ('1', lambda: s.append_number('1'), (20, 75), (60, 35), (0.4, 0.4, 0.6)),
            ('2', lambda: s.append_number('2'), (90, 75), (60, 35), (0.4, 0.4, 0.6)),
            ('3', lambda: s.append_number('3'), (160, 75), (60, 35), (0.4, 0.4, 0.6)),
            ('+', lambda: s.set_operation('+'), (230, 75), (60, 35), (1, 0.8, 0.3)),
            ('x^y', s.power, (300, 75), (60, 35), (0.5, 0.7, 1)),
            ('π', s.pi_value, (370, 75), (30, 35), (0.7, 0.5, 0.8)),
        ]
        for label, callback, pos, size, color in buttons_row4:
            bw(parent=s.w, label=label, size=size, position=pos,
               on_activate_call=callback, color=color,
               textcolor=(1, 1, 1), button_type='square', text_scale=0.9)

        # Row 5
        buttons_row5 = [
            ('0', lambda: s.append_number('0'), (20, 30), (130, 35), (0.4, 0.4, 0.6)),
            ('.', s.add_decimal, (160, 30), (60, 35), (0.4, 0.4, 0.6)),
            ('=', s.calculate, (230, 30), (60, 35), (0.2, 0.8, 0.2)),
            ('e', s.e_value, (300, 30), (60, 35), (0.7, 0.5, 0.8)),
            ('x!', s.factorial, (370, 30), (30, 35), (0.5, 0.7, 1)),
        ]
        for label, callback, pos, size, color in buttons_row5:
            bw(parent=s.w, label=label, size=size, position=pos,
               on_activate_call=callback, color=color,
               textcolor=(1, 1, 1), button_type='square', text_scale=0.9)

        AR.swish()

    # ============ Input Methods ============
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

    # ============ Operations ============
    def set_operation(s, op):
        if s.operation and not s.reset_next_input:
            s.calculate()
        s.previous_input = s.current_input
        s.operation = op
        s.reset_next_input = True
        gs('click01').play()

    def calculate(s):
        try:
            if not s.operation or s.reset_next_input:
                return
            num1 = float(s.previous_input)
            num2 = float(s.current_input)

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

            s.current_input = str(int(result)) if result.is_integer() else str(result)
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
        s.update_display()
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
            s.current_input = str(int(result)) if result.is_integer() else str(result)
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
            s.current_input = str(int(result)) if result.is_integer() else str(result)
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
            s.current_input = str(int(result)) if result.is_integer() else str(result)
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

    # ============ Copy / Send ============
    def copy_result(s):
        try:
            if CIS():
                from babase import clipboard_set_text
                clipboard_set_text(s.current_input)
                push(f'Copied: {s.current_input}', color=(0, 1, 0))
                gs('dingSmall').play()
            else:
                AR.err('Clipboard not supported!')
        except Exception as e:
            AR.err(f'Copy error: {str(e)}')

    def send_to_chat(s):
        try:
            CM(s.current_input)
            push(f'Sent: {s.current_input}', color=(0, 1, 0))
            gs('dingSmall').play()
        except Exception as e:
            AR.err(f'Send error: {str(e)}')


# ba_meta require api 9
# ba_meta export babase.Plugin
class byTaha(Plugin):
    def __init__(s):
        from bauiv1lib import party
        o = party.PartyWindow.__init__

        def e(self, *a, **k):
            r = o(self, *a, **k)

            b_calc = AR.bw(
                position=(self._width - 95, self._height - 80),
                parent=self._root_widget,
                size=(85, 25),
                label='Calc'
            )
            bw(b_calc, on_activate_call=Call(Calculator, b_calc))

            return r

        party.PartyWindow.__init__ = e