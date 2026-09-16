# اگه مادرت خرابه اسکی برو یا تغییرش بده
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
    get_game_roster as get_roster,
    get_connection_to_host_info_2 as get_connection_info
)
import time
import re
from babase import app

AUTO_MSG = "@Horn_Chمرجع دانلود مود های بمب اسکواد داخل تلگرام:"
AUTO_MSG_INTERVAL = 600.0
auto_msg_timer = None

filter_enabled = True
filter_words = []
filter_cooldown = {}

SIGNATURE = "By Mahyar"


def get_flw_position(default_x=None, default_y=None):
    try:
        x = app.config.get('flw_btn_x', default_x)
        y = app.config.get('flw_btn_y', default_y)
        if x is None or y is None:
            return default_x, default_y
        return float(x), float(y)
    except:
        return default_x, default_y


def save_flw_position(x, y):
    try:
        app.config['flw_btn_x'] = float(x)
        app.config['flw_btn_y'] = float(y)
        app.config.commit()
    except:
        pass


def load_filter_words():
    global filter_words, filter_enabled
    try:
        saved = app.config.get('flw_filter_words', [])
        if isinstance(saved, list):
            filter_words = [str(w).strip().lower() for w in saved if str(w).strip()]
        filter_enabled = app.config.get('flw_enabled', True)
    except Exception as e:
        print(f"[FLW] load error: {e}")


def save_filter_words():
    try:
        app.config['flw_filter_words'] = list(filter_words)
        app.config['flw_enabled'] = filter_enabled
        app.config.commit()
    except Exception as e:
        print(f"[FLW] save error: {e}")


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


def safe_chat_send(message):
    try:
        CM(message)
    except Exception as e:
        print(f"[FLW] Chat send error: {e}")


def get_client_id_of_sender(sender):
    if not sender:
        return None

    sender_clean = ''.join(c for c in str(sender) if not (0xE000 <= ord(c) <= 0xF8FF)).strip()
    if not sender_clean:
        return None

    sender_lower = sender_clean.lower()

    try:
        roster = get_roster()
        for entry in roster:
            display = str(entry.get('display_string', '')).strip()
            display_clean = ''.join(c for c in display if not (0xE000 <= ord(c) <= 0xF8FF)).strip()
            players = entry.get('players', [])

            if display_clean.lower() == sender_lower:
                return entry.get('client_id')

            for p in players:
                pname = str(p.get('name_full', '')).strip()
                if pname.lower() == sender_lower:
                    return entry.get('client_id')

                parts = pname.split(' ', 1)
                if len(parts) > 1 and parts[1].strip().lower() == sender_lower:
                    return entry.get('client_id')

                if pname and (sender_lower in pname.lower() or pname.lower() in sender_lower):
                    return entry.get('client_id')
    except Exception as e:
        print(f"[FLW] get_client_id error: {e}")

    return None


def check_filter(msg):
    global filter_enabled, filter_words

    if not filter_enabled:
        return False

    if not filter_words:
        return False

    try:
        sender = None
        content = msg
        if ': ' in msg:
            parts = msg.split(': ', 1)
            sender = parts[0].strip()
            content = parts[1].strip()
        else:
            content = msg.strip()

        if not sender:
            return False

        content_lower = content.lower()

        for word in filter_words:
            if word in content_lower:
                cid = get_client_id_of_sender(sender)
                if cid is not None:
                    safe_chat_send(f"%rep {cid}")
                    try: gs('dingSmallHigh').play()
                    except: pass
                    print(f"[FLW] Filter triggered: '{word}' by {sender} (cid={cid})")
                    return True
                else:
                    print(f"[FLW] Filter hit but cid not found for {sender}")
                    return False
    except Exception as e:
        print(f"[FLW] check_filter error: {e}")

    return False


def auto_msg_send():
    global auto_msg_timer
    try:
        try:
            conn = get_connection_info()
            if conn:
                safe_chat_send(AUTO_MSG)
                print(f"[FLW] Auto msg sent")
        except:
            pass

        auto_msg_timer = teck(AUTO_MSG_INTERVAL, auto_msg_send)
    except Exception as e:
        print(f"[FLW] auto_msg error: {e}")
        try:
            auto_msg_timer = teck(AUTO_MSG_INTERVAL, auto_msg_send)
        except: pass


class AddWordWindow:
    def __init__(s, source, parent_window=None):
        s.parent_window = parent_window
        s.w = AR.cw(source=source, size=(220, 140), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(190, 105))

        tw(parent=s.w, text='Add Word', scale=0.75, position=(110, 100),
           h_align='center', color=(1, 1, 0))

        s.input = tw(parent=s.w, text='', editable=True, scale=0.75,
                     position=(20, 55), size=(180, 26),
                     h_align='center', color=(0.9, 0.9, 0.9))

        bw(parent=s.w, label='Add', size=(100, 28), position=(60, 10),
           on_activate_call=Call(s.save), color=(0.2, 0.7, 0.3),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.65)

        gs('swish').play()

    def save(s):
        global filter_words
        value = tw(query=s.input).strip().lower()
        if not value:
            AR.err('Word required!')
            return
        if value in filter_words:
            AR.err('Already exists!')
            return

        filter_words.append(value)
        save_filter_words()
        push(f'Added: {value}', color=(0, 1, 0))
        gs('dingSmallHigh').play()

        if s.parent_window:
            try: s.parent_window.build_grid()
            except: pass
        AR.swish(s.w)


class FLWEditPlace:
    def __init__(s, source, flw_button):
        s.flw_button = flw_button
        s.step = 5

        try:
            pos = flw_button.get_position()
            s.current_x, s.current_y = float(pos[0]), float(pos[1])
        except:
            s.current_x, s.current_y = 0.0, 0.0

        s.parent_w, s.parent_h = 1920.0, 1080.0
        try:
            parent = flw_button.get_parent()
            if parent:
                psize = parent.get_size()
                s.parent_w, s.parent_h = float(psize[0]), float(psize[1])
        except:
            pass

        s.w = AR.cw(source=source, size=(280, 320), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(250, 285))

        tw(parent=s.w, text='Edit FLW Place', scale=0.85, position=(140, 280),
           h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.3, position=(140, 265),
           h_align='center', color=(0.6, 0.6, 0.8))

        s.pos_text = tw(parent=s.w, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}',
                        position=(140, 242), h_align='center', scale=0.55,
                        color=(1, 1, 0))
        tw(parent=s.w, text='Each click = 5 pixels',
           position=(140, 225), h_align='center', scale=0.4,
           color=(0.7, 0.7, 1))

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

            bw(s.flw_button, position=(s.current_x, s.current_y))
            tw(s.pos_text, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}')
            gs('click01').play()
        except Exception as e:
            print(f"[FLW] Move error: {e}")

    def save(s):
        save_flw_position(s.current_x, s.current_y)
        push(f'FLW Saved: X={int(s.current_x)} Y={int(s.current_y)}', color=(0, 1, 0))
        gs('dingSmallHigh').play()


class FilterWindow:
    def __init__(s, source, flw_button=None):
        s.flw_button = flw_button
        s.w = AR.cw(source=source, size=(240, 360), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(210, 325))

        tw(parent=s.w, text='FLW', scale=0.85, position=(120, 320),
           h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.3, position=(120, 305),
           h_align='center', color=(0.6, 0.6, 0.8))

        s.count_text = tw(parent=s.w, text=f'Words: {len(filter_words)}',
                          position=(120, 285), h_align='center',
                          scale=0.45, color=(1, 1, 0))

        s.scroll = sw(parent=s.w, size=(210, 140), position=(15, 135))
        s.container = cw(parent=s.scroll, size=(190, 300), background=False)
        s.item_buttons = {}
        s.build_grid()

        s.toggle_btn = bw(
            parent=s.w,
            label='ON' if filter_enabled else 'OFF',
            size=(210, 26),
            position=(15, 102),
            on_activate_call=Call(s.toggle),
            color=(0.2, 0.7, 0.2) if filter_enabled else (0.7, 0.2, 0.2),
            textcolor=(1, 1, 1), button_type='square', text_scale=0.65
        )

        bw(parent=s.w, label='+ Add', size=(100, 26), position=(15, 68),
           on_activate_call=Call(s.add_new), color=(0.2, 0.7, 0.3),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.6)

        bw(parent=s.w, label='Clear', size=(100, 26), position=(125, 68),
           on_activate_call=Call(s.clear_all), color=(0.7, 0.3, 0.2),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.6)

        bw(parent=s.w, label='Edit Place', size=(210, 26), position=(15, 34),
           on_activate_call=Call(s.edit_place), color=(0.5, 0.3, 0.7),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.6)

        gs('swish').play()

    def build_grid(s):
        for child in s.container.get_children(): child.delete()
        s.item_buttons.clear()
        items = list(filter_words)
        row_height = 26
        total_h = max(len(items) * row_height + 20, 100)

        for i, word in enumerate(items):
            y = total_h - (i + 1) * row_height
            btn = bw(parent=s.container, label=word,
                     size=(140, 22), position=(5, y),
                     on_activate_call=Call(s.edit_word, word),
                     color=(0.25, 0.4, 0.6),
                     textcolor=(1, 1, 1), button_type='square',
                     text_scale=0.45)
            s.item_buttons[word] = btn
            bw(parent=s.container, label='X', size=(22, 22),
               position=(150, y),
               on_activate_call=Call(s.delete_word, word),
               color=(0.7, 0.2, 0.2), textcolor=(1, 1, 1),
               button_type='square', text_scale=0.55)

        cw(s.container, size=(190, total_h))
        try:
            tw(s.count_text, text=f'Words: {len(filter_words)}')
        except: pass

    def add_new(s):
        AddWordWindow(s.w, parent_window=s)

    def edit_place(s):
        if s.flw_button is None:
            AR.err('FLW button not found!')
            return
        try:
            AR.swish(s.w)
            teck(0.1, lambda: FLWEditPlace(s.w, s.flw_button))
        except Exception as e:
            print(f"[FLW] edit_place error: {e}")

    def edit_word(s, word):
        s.edit_window = AR.cw(source=s.w, size=(220, 140), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.edit_window, position=(190, 105))
        tw(parent=s.edit_window, text=f'Edit Word', scale=0.75, position=(110, 100),
           h_align='center', color=(1, 1, 0))

        input_w = tw(parent=s.edit_window, text=word, editable=True, scale=0.75,
                     position=(20, 55), size=(180, 26),
                     h_align='center', color=(0.9, 0.9, 0.9))

        def do_save():
            global filter_words
            new_value = tw(query=input_w).strip().lower()
            if not new_value:
                AR.err('Word required!')
                return
            if new_value != word and new_value in filter_words:
                AR.err('Already exists!')
                return
            if word in filter_words:
                idx = filter_words.index(word)
                filter_words[idx] = new_value
            save_filter_words()
            push(f'Saved: {new_value}', color=(0, 1, 0))
            gs('dingSmallHigh').play()
            try: AR.swish(s.edit_window)
            except: pass
            s.build_grid()

        bw(parent=s.edit_window, label='Save', size=(100, 28), position=(60, 10),
           on_activate_call=do_save, color=(0.2, 0.7, 0.3),
           textcolor=(1, 1, 1), button_type='square', text_scale=0.65)

    def delete_word(s, word):
        global filter_words
        if word in filter_words:
            filter_words.remove(word)
            save_filter_words()
            push(f'Removed: {word}', color=(1, 0.5, 0))
            gs('dingSmallLow').play()
            s.build_grid()

    def clear_all(s):
        global filter_words
        filter_words = []
        save_filter_words()
        push('All words cleared!', color=(1, 0.5, 0))
        gs('dingSmallLow').play()
        s.build_grid()

    def toggle(s):
        global filter_enabled
        filter_enabled = not filter_enabled
        save_filter_words()
        if filter_enabled:
            bw(s.toggle_btn, label='ON', color=(0.2, 0.7, 0.2))
            push('Filter ON', color=(0, 1, 0))
        else:
            bw(s.toggle_btn, label='OFF', color=(0.7, 0.2, 0.2))
            push('Filter OFF', color=(1, 0.5, 0))
        gs('dingSmall').play()


# ba_meta require api 9
# ba_meta export babase.Plugin
class FLW(Plugin):
    def __init__(s):
        s.last_msg_hash = ""

        load_filter_words()

        teck(1, s.ear)
        teck(60.0, auto_msg_send)

        from bauiv1lib import party
        o = party.PartyWindow.__init__

        def e(self, *a, **k):
            r = o(self, *a, **k)

            try:
                default_x = self._width - 50
                default_y = self._height - 155
                flw_x, flw_y = get_flw_position(default_x, default_y)

                try:
                    flw_x = float(flw_x)
                    flw_y = float(flw_y)
                except:
                    flw_x, flw_y = float(default_x), float(default_y)

                b_flw = AR.bw(
                    position=(flw_x, flw_y),
                    parent=self._root_widget,
                    size=(85, 25),
                    label='FLW',
                    color=(0.6, 0.25, 0.4)
                )
                bw(b_flw, on_activate_call=lambda: s.open_filter(b_flw))
            except Exception as ex:
                print(f"[FLW] button error: {ex}")

            return r

        party.PartyWindow.__init__ = e

        teck(3.0, lambda: push("Tel : @Mahyar015\nChannel : @Horn_Ch", color=(0.6, 0.25, 0.4)))

    def open_filter(s, source):
        try:
            gs('swish').play()
            teck(0.1, lambda: FilterWindow(source, source))
        except Exception as e:
            print(f"[FLW] open error: {e}")

    def ear(s):
        try:
            z = GCM()
            teck(0.003, s.ear)

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
                check_filter(last_msg)
            except Exception as e:
                print(f"[FLW] filter error: {e}")

        except Exception as e:
            try:
                teck(0.003, s.ear)
            except: pass
            print(f"[FLW] ear error: {e}")
