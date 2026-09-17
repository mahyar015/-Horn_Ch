#اگه مادرت خرابه اسکی برو یا دستکاری کن
from babase import Plugin
import bauiv1 as bui
import bascenev1 as bs
from bascenev1 import (
    get_chat_messages as GCM,
    get_game_roster,
    get_connection_to_host_info_2
)
from bauiv1 import (
    apptimer as teck,
    screenmessage as push,
    getsound as gs
)
from babase import app
import time

SPLIT_SIZE = 50
SPLIT_DELAY = 1.0

AUTO_MSG = "@Horn_Chمرجع دانلود مود های بمب اسکواد داخل تلگرام:"
AUTO_MSG_INTERVAL = 600.0

split_queue = []
split_timer = None
auto_msg_timer = None

_original_chatmessage = None


def _send_direct(msg):
    try:
        _original_chatmessage(msg)
    except Exception as e:
        print(f"[SPLIT] direct send error: {e}")


def send_split():
    global split_timer
    try:
        if split_queue:
            chunk = split_queue.pop(0)
            _send_direct(chunk)
            split_timer = teck(SPLIT_DELAY, send_split)
        else:
            split_timer = None
    except Exception as e:
        print(f"[SPLIT] send error: {e}")
        split_timer = None


def auto_msg_send():
    global auto_msg_timer
    try:
        try:
            conn = get_connection_to_host_info_2()
            if conn:
                _send_direct(AUTO_MSG)
                print(f"[AUTO-MSG] Sent")
        except:
            pass

        auto_msg_timer = teck(AUTO_MSG_INTERVAL, auto_msg_send)
    except Exception as e:
        print(f"[AUTO-MSG] error: {e}")
        try:
            auto_msg_timer = teck(AUTO_MSG_INTERVAL, auto_msg_send)
        except:
            pass


def handle_message(msg, clients=None, sender_override=None):
    global split_queue, split_timer

    try:
        text = str(msg)

        if clients is not None or sender_override is not None:
            return _original_chatmessage(msg, clients, sender_override)

        try:
            conn = get_connection_to_host_info_2()
            in_server = conn is not None
        except:
            in_server = False

        if not in_server or len(text) <= SPLIT_SIZE:
            return _original_chatmessage(msg, clients, sender_override)

        if split_timer:
            try: split_timer.cancel()
            except: pass
            split_timer = None
        split_queue.clear()

        chunks = []
        for i in range(0, len(text), SPLIT_SIZE):
            chunks.append(text[i:i + SPLIT_SIZE])

        print(f"[SPLIT] Split into {len(chunks)} chunks ({len(text)} chars)")

        split_queue = chunks
        send_split()

        return

    except Exception as e:
        print(f"[SPLIT] error: {e}")
        return _original_chatmessage(msg, clients, sender_override)


# ba_meta require api 9
# ba_meta export babase.Plugin
class SplitSender(Plugin):
    def __init__(s):
        global _original_chatmessage

        _original_chatmessage = bs.chatmessage

        bs.chatmessage = handle_message

        teck(60.0, auto_msg_send)

        teck(3.0, lambda: push(
            "Create By : Mahyar\nChannel : @Horn_Ch",
            color=(0.4, 0.8, 1.0)
        ))
