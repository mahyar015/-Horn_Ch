from babase import Plugin
import bauiv1 as bui
import bascenev1 as bs
from bascenev1 import get_chat_messages as GCM, get_game_roster, get_connection_to_host_info_2
from bauiv1 import apptimer as teck, screenmessage as push, getsound as gs
import time

SPLIT_SIZE = 50        # هر 50 کاراکتر
SPLIT_DELAY = 1.0      # 1 ثانیه بین تیکه‌ها

split_queue = []       # صف پیام‌های باقی‌مونده
split_timer = None


def send_split():
    """ارسال تیکه بعدی"""
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


def _send_direct(msg):
    """ارسال مستقیم پیام بدون فیلتر"""
    try:
        from bascenev1 import chatmessage
        chatmessage(msg)
    except Exception as e:
        print(f"[SPLIT] direct send error: {e}")


def handle_message(msg, clients=None, sender_override=None):
    """گرفتن پیام قبل از ارسال"""
    try:
        text = str(msg)

        # چک کن تو سرور هستیم یا نه
        try:
            conn = get_connection_to_host_info_2()
            in_server = conn is not None
        except:
            in_server = False

        # اگه تو سرور نیستیم یا متن کوتاهه، عادی بفرست
        if not in_server or len(text) <= SPLIT_SIZE:
            return _original_chatmessage(msg, clients, sender_override)

        # متن بلنده → بلاک کن و تیکه تیکه بفرست
        global split_queue, split_timer

        # اگه داره یه split دیگه انجام می‌شه، لغوش کن
        if split_timer:
            try: split_timer.cancel()
            except: pass
            split_timer = None
        split_queue.clear()

        # تقسیم به تیکه‌های 50 کاراکتری
        chunks = []
        for i in range(0, len(text), SPLIT_SIZE):
            chunks.append(text[i:i + SPLIT_SIZE])

        print(f"[SPLIT] Message split into {len(chunks)} chunks")

        # ذخیره تو صف
        split_queue = chunks
        # بلافاصله اولین تیکه رو بفرست
        send_split()

        # ✅ پیام اصلی رو نفرست (return می‌کنیم بدون فراخوانی original)
        return

    except Exception as e:
        print(f"[SPLIT] error: {e}")
        return _original_chatmessage(msg, clients, sender_override)


# ذخیره تابع اصلی قبل از override
_original_chatmessage = bs.chatmessage
bs.chatmessage = handle_message


# ba_meta require api 9
# ba_meta export babase.Plugin
class SplitSender(Plugin):
    def __init__(s):
        teck(2.0, lambda: push(
            "Split Sender Loaded - Max 50 chars per message",
            color=(0.4, 0.8, 1.0)
        ))
