from babase import Plugin
import bauiv1 as bui
import bascenev1 as bs
from bascenev1 import (
    chatmessage as CM,
    screenmessage as push,
    get_connection_to_host_info_2 as get_connection_info
)
from bauiv1 import (
    apptimer as teck,
    getsound as gs,
    containerwidget as cw,
    buttonwidget as bw,
    textwidget as tw,
    get_special_widget as gsw,
    UIScale as uis,
    app as APP,
    Call
)
from babase import app
import socket
import threading
import time
import os

server_ip = "127.0.0.1"
server_port = 43210
current_ping = 0.0
ping_thread = None

SIGNATURE = "By Mahyar"


def get_ping_btn_position(default_x=None, default_y=None):
    try:
        x = app.config.get('ping_btn_x', default_x)
        y = app.config.get('ping_btn_y', default_y)
        if x is None or y is None:
            return default_x, default_y
        return float(x), float(y)
    except:
        return default_x, default_y


def save_ping_btn_position(x, y):
    try:
        app.config['ping_btn_x'] = float(x)
        app.config['ping_btn_y'] = float(y)
        app.config.commit()
    except: pass


class RealPingThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True

    def run(self):
        global current_ping
        while self.running:
            try:
                if server_ip != "127.0.0.1" and server_port != 43210:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(1)
                    start_time = time.time()

                    try:
                        sock.sendto(b'\x0b', (server_ip, server_port))
                        data, addr = sock.recvfrom(10)
                        if data == b'\x0c':
                            ping = (time.time() - start_time) * 1000.0
                            current_ping = round(ping, 2)
                        else:
                            current_ping = 999
                    except socket.timeout:
                        current_ping = 999
                    except:
                        current_ping = 0
                    finally:
                        try: sock.close()
                        except: pass
                else:
                    current_ping = 0
            except:
                current_ping = 0

            time.sleep(1)


def get_ping_icon(ping):
    try:
        if ping == 0 or ping >= 999:
            return "❓"
        elif ping < 100:
            return "🔵"
        elif ping < 200:
            return "⚪"
        elif ping < 350:
            return "🟠"
        else:
            return "🔴"
    except:
        return "❓"


from bascenev1 import connect_to_party as _original_connect

def new_connect_to_party(address, port=43210, print_progress=False):
    global server_ip, server_port
    server_ip = address
    server_port = port
    print(f"[Ping] Server: {address}:{port}")
    return _original_connect(address, port, print_progress)


bs.connect_to_party = new_connect_to_party


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


class PingEditPlace:
    def __init__(s, source, ping_button):
        s.ping_button = ping_button
        s.step = 5

        try:
            pos = ping_button.get_position()
            s.current_x, s.current_y = float(pos[0]), float(pos[1])
        except:
            s.current_x, s.current_y = 0.0, 0.0

        s.parent_w, s.parent_h = 1920.0, 1080.0
        try:
            parent = ping_button.get_parent()
            if parent:
                psize = parent.get_size()
                s.parent_w, s.parent_h = float(psize[0]), float(psize[1])
        except: pass

        s.w = AR.cw(source=source, size=(300, 320), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(270, 285))

        tw(parent=s.w, text='Edit Ping Place', scale=0.9, position=(150, 280),
           h_align='center', color=(0, 1, 1))
        tw(parent=s.w, text=SIGNATURE, scale=0.3, position=(150, 265),
           h_align='center', color=(0.6, 0.6, 0.8))

        s.pos_text = tw(parent=s.w, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}',
                        position=(150, 242), h_align='center', scale=0.6,
                        color=(1, 1, 0))
        tw(parent=s.w, text='Each click = 5 pixels', scale=0.4,
           position=(150, 225), h_align='center', color=(0.7, 0.7, 1))

        arrow_size = (55, 42)
        arrow_color = (0.3, 0.5, 0.8)
        cx = 150

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

        bw(parent=s.w, label='Save', size=(200, 32), position=(cx - 100, 30),
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

            bw(s.ping_button, position=(s.current_x, s.current_y))
            tw(s.pos_text, text=f'X: {int(s.current_x)}   Y: {int(s.current_y)}')
            gs('click01').play()
        except Exception as e:
            print(f"[Ping] move error: {e}")

    def save(s):
        save_ping_btn_position(s.current_x, s.current_y)
        push(f'Saved: X={int(s.current_x)} Y={int(s.current_y)}', color=(0, 1, 0))
        gs('dingSmallHigh').play()


class PingWindow:
    def __init__(s, source, ping_button=None):
        s.ping_button = ping_button
        s.w = AR.cw(source=source, size=(260, 220), ps=AR.UIS() * 0.3)
        AR.add_close_button(s.w, position=(230, 185))

        tw(parent=s.w, text='Ping', scale=0.9, position=(130, 180),
           h_align='center', color=(0, 1, 1))

        s.ping_text = tw(
            parent=s.w,
            text=f'Current: {current_ping} ms',
            position=(130, 145), h_align='center',
            scale=0.7, color=(1, 1, 0)
        )

        tw(parent=s.w, text='Server:',
           position=(130, 115), h_align='center',
           scale=0.45, color=(0.8, 0.8, 1))

        s.server_text = tw(
            parent=s.w,
            text=f'{server_ip}:{server_port}',
            position=(130, 95), h_align='center',
            scale=0.45, color=(0.8, 0.8, 1)
        )

        bw(parent=s.w, label='Send Ping to Chat',
           size=(180, 32), position=(40, 50),
           on_activate_call=s.send_ping,
           color=(0.2, 0.7, 0.3), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.65)

        bw(parent=s.w, label='Edit Place',
           size=(180, 28), position=(40, 15),
           on_activate_call=s.edit_place,
           color=(0.5, 0.3, 0.7), textcolor=(1, 1, 1),
           button_type='square', text_scale=0.65)

        s.update_ping()

        gs('swish').play()

    def update_ping(s):
        try:
            if not s.w.exists():
                return
            tw(s.ping_text, text=f'Current: {current_ping} ms')
            s.ping_text_update_timer = teck(0.5, s.update_ping)
        except:
            pass

    def send_ping(s):
        try:
            icon = get_ping_icon(current_ping)
            if current_ping == 0:
                msg = f'My Ping : {icon} ?'
            else:
                msg = f'My Ping : {icon} {int(current_ping)}'
            CM(msg)
            push(f'Sent: {msg}', color=(0, 1, 0))
            gs('dingSmallHigh').play()
        except Exception as e:
            push(f'Error: {e}', color=(1, 0, 0))

    def edit_place(s):
        if s.ping_button is None:
            push('Ping button not found!', color=(1, 0, 0))
            return
        try:
            AR.swish(s.w)
            teck(0.1, lambda: PingEditPlace(s.w, s.ping_button))
        except Exception as e:
            print(f"[Ping] edit_place error: {e}")


# ba_meta require api 9
# ba_meta export babase.Plugin
class PingBot(Plugin):
    def __init__(s):
        global ping_thread

        ping_thread = RealPingThread()
        ping_thread.start()

        teck(3.0, lambda: push("Creat By Mahyar", color=(0.4, 0.8, 1.0)))

        from bauiv1lib import party
        o = party.PartyWindow.__init__

        def e(self, *a, **k):
            r = o(self, *a, **k)

            try:
                default_x = self._width - 570
                default_y = self._height - 80
                ping_x, ping_y = get_ping_btn_position(default_x, default_y)

                try:
                    ping_x = float(ping_x)
                    ping_y = float(ping_y)
                except:
                    ping_x, ping_y = float(default_x), float(default_y)

                b_ping = AR.bw(
                    position=(ping_x, ping_y),
                    parent=self._root_widget,
                    size=(80, 25),
                    label='Ping',
                    color=(0.4, 0.6, 0.8)
                )
                bw(b_ping, on_activate_call=lambda: s.open_ping(b_ping))
            except Exception as ex:
                print(f"[Ping] button error: {ex}")

            return r

        party.PartyWindow.__init__ = e

    def open_ping(s, source):
        try:
            gs('swish').play()
            teck(0.1, lambda: PingWindow(source, source))
        except Exception as e:
            print(f"[Ping] open error: {e}")
