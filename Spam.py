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
    scrollwidget as sw
)
from bascenev1 import (
    chatmessage as CM,
    screenmessage as push,
    get_chat_messages as GCM,
    get_connection_to_host_info_2 as get_connection_info
)
from babase import app
import time
import re
import os

SIGNATURE = "By Mahyar"

DEFAULT_DELAY = 2.0
INVISIBLE_CHARS = ['', '\u200b', '\u200c', '\u200d', '\u2060', '\u180e', '\ufeff', '\u200e', '\u200f', '\u2061']


def get_spam_btn_position(default_x=None, default_y=None):
    try:
        x = app.config.get('spam_btn_x', default_x)
        y = app.config.get('spam_btn_y', default_y)
        if x is None or y is None:
            return default_x, default_y
        return float(x), float(y)
    except:
        return default_x, default_y


def save_spam_btn_position(x, y):
    try:
        app.config['spam_btn_x'] = float(x)
        app.config['spam_btn_y'] = float(y)
        app.config.commit()
    except: pass


def get_spam_messages():
    try:
        saved = app.config.get('spam_msg_list', [])
        if isinstance(saved, list):
            return [dict(m) for m in saved if isinstance(m, dict)]
    except: pass
    return []


def save_spam_messages(msgs):
    try:
        app.config['spam_msg_list'] = [dict(m) for m in msgs]
        app.config.commit()
    except: pass


def get_loop_state():
    try:
        return app.config.get('spam_loop', True)
    except:
        return True


def save_loop_state(v):
    try:
        app.config['spam_loop'] = bool(v)
        app.config.commit()
    except: pass


spam_active = False
spam_timer = None
spam_counter = 0

spam_single_msg = ""
spam_single_delay = DEFAULT_DELAY

spam_list = []
spam_list_index = 0
spam_loop = True

spam_mode = 'single'


def safe_chat_send(msg):
    try:
        CM(msg)
    except Exception as e:
        print(f"[Spam] send error: {e}")


def spam_tick():
    global spam_active, spam_timer, spam_counter, spam_list_index

    if not spam_active:
        return

    try:
        try:
            conn = get_connection_info()
            in_server = conn is not None
        except:
            in_server = False

        if not in_server:
            spam_active = False
            push("Spam Stopped (left server)", color=(1, 0.5, 0))
            return

        suffix = INVISIBLE_CHARS[spam_counter % len(INVISIBLE_CHARS)]
        spam_counter += 1
        if spam_counter >= 100:
            spam_counter = 0

        if spam_mode == 'single':
            if spam_single_msg:
                safe_chat_send(spam_single_msg + suffix)
            spam_timer = teck(spam_single_delay, spam_tick)

        elif spam_mode == 'list':
            if not spam_list:
                spam_active = False
                return

            current = spam_list[spam_list_index]
            msg = current.get('text', '')
            delay = float(current.get('delay', DEFAULT_DELAY))

            if msg:
                safe_chat_send(msg + suffix)

            spam_list_index += 1

            if spam_list_index >= len(spam_list):
                if spam_loop:
                    spam_list_index = 0
                else:
                    spam_active = False
                    push("Spam finished!", color=(0, 1, 0))
                    return

            spam_timer = teck(delay, spam_tick)

    except Exception as e:
        print(f"[Spam] tick error: {e}")
        spam_active = False


def start_spam_single(msg, delay):
    global spam_active, spam_timer, spam_single_msg, spam_single_delay, spam_counter, spam_mode
    stop_spam()
    spam_active = True
    spam_mode = 'single'
    spam_single_msg = msg
    spam_single_delay = float(delay)
    spam_counter = 0
    spam_tick()


def start_spam_list():
    global spam_active, spam_timer, spam_list_index, spam_counter, spam_mode
    stop_spam()
    if not spam_list:
        push("List is empty!", color=(1, 0.5, 0))
        return
    spam_active = True
    spam_mode = 'list'
    spam_list_index = 0
    spam_counter = 0
    spam_tick()


def stop_spam():
    global spam_active, spam_timer
    if spam_timer:
        try:
            spam_timer.cancel()
        except: pass
        spam_timer = None
    spam_active = False


def check_spam_command(msg):
    global spam_single_msg, spam_single_delay

    try:
        content = msg
        if ': ' in msg:
            parts = msg.split(': ', 1)
            sender = parts[0].strip()
            content = parts[1].strip()
        else:
            sender = None
            content = msg.strip()

        content_lower = content.lower()

        if content_lower in ('spam off', 'اسپم خاموش', 'توقف اسپم', 'stop spam'):
            stop_spam()
            push("Spam Stopped", color=(1, 0.5, 0))
            return True

        if content_lower in ('spam on', 'اسپم روشن'):
            if spam_single_msg:
                start_spam_single(spam_single_msg, spam_single_delay)
                push("Spam Started", color=(0, 1, 0))
            else:
                push("No message set!", color=(1, 0.5, 0))
            return True

        match = re.match(r'^spam\s+(.+?)\s+([\d.]+)\s*$', content_lower)
        if match:
            message = match.group(1).strip()
            try:
                delay = float(match.group(2))
            except:
                return False
            if delay <= 0:
                delay = DEFAULT_DELAY
            spam_single_msg = message
            spam_single_delay = delay
            start_spam_single(message, delay)
            push(f"Spam: {message} ({delay}s)", color=(0, 1, 0))
            return True

    except Exception as e:
        print(f"[Spam] cmd error: {e}")
    return False


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


class SpamEditPlace:
    def __init__(s, source, spam_button):
        s.spam_button = spam_button
        s.step = 5

        try:
            pos = spam_button.get_position()
            s.current_x, s.current_y = float(pos[0]), float(pos[1])
        except:
            s.current_x, s.current_y = 0.0, 0.0

        s.parent_w, s.parent_h = 1920.0, 1080.0
        try:
            parent = spam_button.get_parent()
            if parent:
                psize = parent.get_size()
                s.parent_w, s.parent_h = float(psize[0]), float(psize[1])
        except: pass

        s.w = AR.cw(source=source, size=(280, 320), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(250, 285))

        tw(parent=s.w, text='Edit Spam Place', scale=0.85, position=(140, 280),
           h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.3, position=(140, 265),
           h_align='center', color=(0.6, 0.6, 0.8))

        s.pos_text = tw(parent=s.w, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}',
                        position=(140, 242), h_align='center', scale=0.55,
                        color=(1, 1, 0))

        arrow_size = (55, 42)
        arrow_color = (0.3, 0.5, 0.8)
        cx = 140

        bw(parent=s.w, label='^', size=arrow_size,
           position=(cx - 27, 175),
           on_activate_call=lambda: s.move(0, s.step),
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.1)

        bw(parent=s.w, label='<', size=arrow_size,
           position=(cx - 90, 128),
           on_activate_call=lambda: s.move(-s.step, 0),
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.1)

        bw(parent=s.w, label='>', size=arrow_size,
           position=(cx + 35, 128),
           on_activate_call=lambda: s.move(s.step, 0),
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.1)

        bw(parent=s.w, label='v', size=arrow_size,
           position=(cx - 27, 81),
           on_activate_call=lambda: s.move(0, -s.step),
           color=arrow_color, textcolor=(1, 1, 1),
           button_type='square', text_scale=1.1)

        bw(parent=s.w, label='Save', size=(180, 32), position=(cx - 90, 30),
           on_activate_call=s.save, color=(0.2, 0.7, 0.3),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.75)

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

            bw(s.spam_button, position=(s.current_x, s.current_y))
            tw(s.pos_text, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}')
            gs('click01').play()
        except Exception as e:
            print(f"[Spam] move error: {e}")

    def save(s):
        save_spam_btn_position(s.current_x, s.current_y)
        push(f'Spam Saved: X={int(s.current_x)} Y={int(s.current_y)}', color=(0, 1, 0))
        gs('dingSmallHigh').play()


class AddMsgWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(240, 160), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(210, 125))

        tw(parent=s.w, text='Add to List', scale=0.75, position=(120, 120),
           h_align='center', color=(1, 1, 0))

        tw(parent=s.w, text='Text:', scale=0.5, position=(60, 95),
           h_align='center', color=(1, 1, 1))
        s.text_input = tw(parent=s.w, text='', editable=True, scale=0.7,
                          position=(25, 65), size=(190, 24),
                          h_align='center', color=(0.9, 0.9, 0.9))

        tw(parent=s.w, text='Delay:', scale=0.5, position=(60, 45),
           h_align='center', color=(1, 1, 1))
        s.delay_input = tw(parent=s.w, text=str(DEFAULT_DELAY), editable=True, scale=0.7,
                           position=(25, 18), size=(190, 24),
                           h_align='center', color=(0.9, 0.9, 0.9))

        bw(parent=s.w, label='Add', size=(80, 26), position=(150, 18),
           on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.6)

        gs('swish').play()

    def save(s):
        global spam_list
        text = tw(query=s.text_input).strip()
        if not text:
            AR.err('Text required!')
            return
        try:
            delay = float(tw(query=s.delay_input).strip())
            if delay <= 0: delay = DEFAULT_DELAY
        except:
            delay = DEFAULT_DELAY

        spam_list.append({'text': text, 'delay': delay})
        save_spam_messages(spam_list)
        push(f'Added: {text}', color=(0, 1, 0))
        gs('dingSmallHigh').play()

        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class SpamWindow:
    def __init__(s, source, spam_button=None):
        s.spam_button = spam_button
        s.w = AR.cw(source=source, size=(320, 480), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(290, 445))

        tw(parent=s.w, text='Spam', scale=0.9, position=(160, 440),
           h_align='center', color=(1, 0.5, 0.5))

        s.status = tw(parent=s.w, text='Not Spamming',
                      position=(160, 420), h_align='center',
                      scale=0.5, color=(1, 1, 0))

        tw(parent=s.w, text='Quick Spam', scale=0.55,
           position=(160, 395), h_align='center', color=(0.8, 0.8, 1))

        s.text_input = tw(parent=s.w, text=spam_single_msg, editable=True, scale=0.75,
                          position=(20, 365), size=(280, 26),
                          h_align='center', color=(0.9, 0.9, 0.9))

        s.delay_input = tw(parent=s.w, text=str(spam_single_delay), editable=True, scale=0.75,
                           position=(20, 335), size=(130, 26),
                           h_align='center', color=(0.9, 0.9, 0.9))

        tw(parent=s.w, text='sec', scale=0.5, position=(155, 348),
           h_align='center', color=(1, 1, 1))

        bw(parent=s.w, label='▶ START', size=(135, 30), position=(20, 298),
           on_activate_call=Call(s.start_current), color=(0.2, 0.7, 0.3),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.7)

        bw(parent=s.w, label='■ STOP', size=(135, 30), position=(165, 298),
           on_activate_call=Call(s.stop), color=(0.7, 0.2, 0.2),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.7)

        tw(parent=s.w, text='Message List', scale=0.55,
           position=(160, 275), h_align='center', color=(0.8, 0.8, 1))

        s.scroll = sw(parent=s.w, size=(280, 130), position=(20, 140))
        s.container = cw(parent=s.scroll, size=(260, 300), background=False)
        s.item_buttons = {}
        s.build_grid()

        bw(parent=s.w, label='+ Add', size=(130, 28), position=(20, 108),
           on_activate_call=Call(s.add_new), color=(0.2, 0.7, 0.3),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.65)

        s.loop_btn = bw(parent=s.w, label='🔄 Loop: ' + ('ON' if spam_loop else 'OFF'),
                        size=(140, 28), position=(160, 108),
                        on_activate_call=Call(s.toggle_loop),
                        color=(0.2, 0.7, 0.2) if spam_loop else (0.7, 0.2, 0.2),
                        textcolor=(1, 1, 1), button_type='square', text_scale=0.6)

        bw(parent=s.w, label='▶ Start List', size=(130, 30), position=(20, 72),
           on_activate_call=Call(s.start_list), color=(0.3, 0.6, 0.4),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.65)

        bw(parent=s.w, label='Clear All', size=(140, 30), position=(160, 72),
           on_activate_call=Call(s.clear_all), color=(0.7, 0.3, 0.2),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.6)

        bw(parent=s.w, label='Edit Place', size=(280, 28), position=(20, 34),
           on_activate_call=Call(s.edit_place), color=(0.5, 0.3, 0.7),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.6)

        gs('swish').play()

    def build_grid(s):
        for child in s.container.get_children(): child.delete()
        s.item_buttons.clear()

        items = list(spam_list)
        row_height = 28
        total_h = max(len(items) * row_height + 20, 100)

        for i, item in enumerate(items):
            y = total_h - (i + 1) * row_height
            text = item.get('text', '')
            delay = item.get('delay', 2)
            label = f'{text[:20]} ({delay}s)'

            btn = bw(parent=s.container, label=label,
                     size=(210, 24), position=(5, y),
                     on_activate_call=lambda idx=i: s.edit_item(idx),
                     color=(0.25, 0.4, 0.6),
                     textcolor=(1, 1, 1), button_type='square', text_scale=0.45)
            s.item_buttons[i] = btn

            bw(parent=s.container, label='X', size=(25, 24),
               position=(220, y),
               on_activate_call=lambda idx=i: s.delete_item(idx),
               color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1),
               button_type='square', text_scale=0.6)

        cw(s.container, size=(260, total_h))

    def start_current(s):
        global spam_single_msg, spam_single_delay
        text = tw(query=s.text_input).strip()
        if not text:
            AR.err('Text required!')
            return
        try:
            delay = float(tw(query=s.delay_input).strip())
            if delay <= 0: delay = DEFAULT_DELAY
        except:
            delay = DEFAULT_DELAY

        spam_single_msg = text
        spam_single_delay = delay
        start_spam_single(text, delay)
        tw(s.status, text=f'Spamming: {text}', color=(0, 1, 0))
        gs('dingSmallHigh').play()

    def start_list(s):
        if not spam_list:
            AR.err('List is empty!')
            return
        start_spam_list()
        tw(s.status, text='Spamming List...', color=(0, 1, 0))
        gs('dingSmallHigh').play()

    def stop(s):
        stop_spam()
        tw(s.status, text='Stopped', color=(1, 1, 0))
        gs('dingSmallLow').play()

    def add_new(s):
        AddMsgWindow(s.w, parent_window=s)

    def edit_item(s, idx):
        if idx >= len(spam_list): return
        item = spam_list[idx]
        s.edit_window = AR.cw(source=s.w, size=(240, 160), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.edit_window, position=(210, 125))

        tw(parent=s.edit_window, text='Edit Message', scale=0.75, position=(120, 120),
           h_align='center', color=(1, 1, 0))

        tw(parent=s.edit_window, text='Text:', scale=0.5, position=(60, 95),
           h_align='center', color=(1, 1, 1))
        text_in = tw(parent=s.edit_window, text=item.get('text', ''), editable=True, scale=0.7,
                     position=(25, 65), size=(190, 24),
                     h_align='center', color=(0.9, 0.9, 0.9))

        tw(parent=s.edit_window, text='Delay:', scale=0.5, position=(60, 45),
           h_align='center', color=(1, 1, 1))
        delay_in = tw(parent=s.edit_window, text=str(item.get('delay', 2)), editable=True, scale=0.7,
                      position=(25, 18), size=(190, 24),
                      h_align='center', color=(0.9, 0.9, 0.9))

        def do_save():
            new_text = tw(query=text_in).strip()
            if not new_text:
                AR.err('Text required!')
                return
            try:
                new_delay = float(tw(query=delay_in).strip())
                if new_delay <= 0: new_delay = DEFAULT_DELAY
            except:
                new_delay = DEFAULT_DELAY

            if idx < len(spam_list):
                spam_list[idx]['text'] = new_text
                spam_list[idx]['delay'] = new_delay
                save_spam_messages(spam_list)
                push('Saved!', color=(0, 1, 0))
                gs('dingSmallHigh').play()
                AR.swish(s.edit_window)
                s.build_grid()

        bw(parent=s.edit_window, label='Save', size=(80, 26), position=(150, 18),
           on_activate_call=do_save, color=(0.2, 0.7, 0.3),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.6)

    def delete_item(s, idx):
        if idx < len(spam_list):
            spam_list.pop(idx)
            save_spam_messages(spam_list)
            push('Deleted!', color=(1, 0.5, 0))
            gs('dingSmallLow').play()
            s.build_grid()

    def clear_all(s):
        global spam_list
        spam_list = []
        save_spam_messages(spam_list)
        push('List cleared!', color=(1, 0.5, 0))
        gs('dingSmallLow').play()
        s.build_grid()

    def toggle_loop(s):
        global spam_loop
        spam_loop = not spam_loop
        save_loop_state(spam_loop)
        if spam_loop:
            bw(s.loop_btn, label='🔄 Loop: ON', color=(0.2, 0.7, 0.2))
            push('Loop ON', color=(0, 1, 0))
        else:
            bw(s.loop_btn, label='🔄 Loop: OFF', color=(0.7, 0.2, 0.2))
            push('Loop OFF', color=(1, 0.5, 0))
        gs('dingSmall').play()

    def edit_place(s):
        if s.spam_button is None:
            AR.err('Spam button not found!')
            return
        try:
            AR.swish(s.w)
            teck(0.1, lambda: SpamEditPlace(s.w, s.spam_button))
        except Exception as e:
            print(f"[Spam] edit_place error: {e}")


# ba_meta require api 9
# ba_meta export babase.Plugin
class SpamBot(Plugin):
    def __init__(s):
        global spam_list, spam_loop, spam_single_msg, spam_single_delay

        spam_list = get_spam_messages()
        spam_loop = get_loop_state()

        s.last_msg_hash = ""

        teck(1, s.ear)

        teck(3.0, lambda: push("Creat By Mahyar", color=(1, 0.5, 0.5)))

        from bauiv1lib import party
        o = party.PartyWindow.__init__

        def e(self, *a, **k):
            r = o(self, *a, **k)

            try:
                default_x = self._width - 145
                default_y = self._height - 155
                spam_x, spam_y = get_spam_btn_position(default_x, default_y)

                try:
                    spam_x = float(spam_x)
                    spam_y = float(spam_y)
                except:
                    spam_x, spam_y = float(default_x), float(default_y)

                b_spam = AR.bw(
                    position=(spam_x, spam_y),
                    parent=self._root_widget,
                    size=(85, 25),
                    label='Spam',
                    color=(0.8, 0.4, 0.2)
                )
                bw(b_spam, on_activate_call=lambda: s.open_spam(b_spam))
            except Exception as ex:
                print(f"[Spam] button error: {ex}")

            return r

        party.PartyWindow.__init__ = e

    def open_spam(s, source):
        try:
            gs('swish').play()
            teck(0.1, lambda: SpamWindow(source, source))
        except Exception as e:
            print(f"[Spam] open error: {e}")

    def ear(s):
        try:
            z = GCM()
            teck(0.005, s.ear)

            if not z:
                s.last_msg_hash = ""
                return

            try:
                last_msg = z[-1]
            except (IndexError, TypeError):
                s.last_msg_hash = ""
                return

            current_hash = f"{len(last_msg)}_{last_msg}"
            if current_hash == s.last_msg_hash:
                return
            s.last_msg_hash = current_hash

            try:
                check_spam_command(last_msg)
            except Exception as e:
                print(f"[Spam] cmd error: {e}")

        except Exception as e:
            try:
                teck(0.005, s.ear)
            except: pass
            print(f"[Spam] ear error: {e}")
