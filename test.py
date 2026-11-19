# ba_meta require api 9
# ba_meta export babase.Plugin

from babase import Plugin, apptimer
import bauiv1 as bui
from bauiv1 import (
    containerwidget,
    buttonwidget,
    textwidget,
    get_special_widget,
    UIScale,
)
import threading
import urllib.request
import re
import html
import time
from datetime import datetime, timedelta

PAGE_URL = "https://bslife.ir/post.php?post=RankingReset"
REQUEST_TIMEOUT = 12


def _clean_page(raw):
    """Convert page HTML to readable lines."""
    raw = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</li>", "\n", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    lines = []
    for line in raw.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if line and line not in lines:
            lines.append(line)
    return lines


def _extract_reset_lines(lines):
    keys = ("reset", "restart", "ranking", "ریست", "ریستارت", "رنک")
    found = []
    for line in lines:
        low = line.lower()
        if any(key in low for key in keys):
            found.append(line[:180])
    return found[:18]


def _find_next_datetime(lines):
    """Find an explicit date+time if the page publishes one."""
    text = "\n".join(lines)
    patterns = [
        r"(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})[ T،-]+(\d{1,2}):(\d{2})",
        r"(\d{1,2})[-/.](\d{1,2})[-/.](20\d{2})[ T،-]+(\d{1,2}):(\d{2})",
    ]
    for index, pattern in enumerate(patterns):
        match = re.search(pattern, text)
        if not match:
            continue
        try:
            if index == 0:
                year, month, day, hour, minute = map(int, match.groups())
            else:
                day, month, year, hour, minute = map(int, match.groups())
            return datetime(year, month, day, hour, minute)
        except ValueError:
            pass
    return None


class RankingWindow:
    def __init__(self, source=None):
        self._alive = True
        self._last_lines = []
        self._next_reset = None
        self._status = "در حال دریافت اطلاعات..."
        scale = 1.0
        try:
            ui_scale = bui.app.ui_v1.uiscale
            scale = 1.25 if ui_scale == UIScale.SMALL else 1.0 if ui_scale == UIScale.MEDIUM else 0.85
        except Exception:
            pass

        self._w = containerwidget(
            parent=get_special_widget("overlay_stack"),
            size=(390, 390),
            scale=scale,
            color=(0.10, 0.12, 0.19),
            transition="in_scale",
        )
        containerwidget(
            self._w,
            on_outside_click_call=self.close,
            on_cancel_call=self.close,
        )
        textwidget(
            parent=self._w, text="BSLIFE RANKING",
            position=(195, 350), size=(330, 30),
            scale=0.95, color=(0.3, 0.9, 1.0),
            h_align="center",
        )
        buttonwidget(
            parent=self._w, label="X", size=(30, 30),
            position=(345, 345), color=(0.65, 0.16, 0.22),
            on_activate_call=self.close,
        )
        self._status_text = textwidget(
            parent=self._w, text=self._status,
            position=(20, 305), size=(350, 28),
            scale=0.65, color=(1, 0.85, 0.3),
            h_align="center",
        )
        self._countdown_text = textwidget(
            parent=self._w, text="زمان ریست بعدی: نامشخص",
            position=(20, 265), size=(350, 30),
            scale=0.72, color=(0.35, 1.0, 0.65),
            h_align="center",
        )
        self._content = textwidget(
            parent=self._w,
            text="برای دریافت زمان‌بندی، دکمه بروزرسانی را بزنید.",
            position=(22, 75), size=(346, 175),
            scale=0.58, color=(0.92, 0.94, 1.0),
            h_align="center", v_align="top",
            maxwidth=340,
        )
        buttonwidget(
            parent=self._w, label="بروزرسانی اطلاعات",
            size=(220, 38), position=(85, 22),
            color=(0.12, 0.48, 0.72),
            on_activate_call=self.refresh,
        )
        self.refresh()
        self._tick()

    def close(self):
        self._alive = False
        try:
            bui.getsound("swish").play()
            containerwidget(self._w, transition="out_scale")
        except Exception:
            pass

    def refresh(self):
        if not self._alive:
            return
        textwidget(self._status_text, text="در حال اتصال به BSLIFE...",
                   color=(1, 0.85, 0.3))
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        try:
            request = urllib.request.Request(
                PAGE_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml",
                },
            )
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                raw = response.read().decode("utf-8", "replace")
            lines = _clean_page(raw)
            reset_lines = _extract_reset_lines(lines)
            next_reset = _find_next_datetime(lines)
            if not reset_lines:
                reset_lines = ["صفحه دریافت شد، اما زمان‌بندی قابل تشخیص نبود."]
            apptimer(0.0, lambda: self._show_result(
                "اطلاعات دریافت شد", reset_lines, next_reset, None
            ))
        except Exception as exc:
            message = str(exc)
            apptimer(0.0, lambda: self._show_result(
                "دریافت اطلاعات ناموفق بود", [],
                None, message
            ))

    def _show_result(self, status, lines, next_reset, error):
        if not self._alive:
            return
        self._status = status
        self._last_lines = lines
        self._next_reset = next_reset
        color = (0.3, 1.0, 0.55) if error is None else (1.0, 0.35, 0.3)
        textwidget(self._status_text, text=status, color=color)
        if error:
            body = (
                "اتصال به سایت انجام نشد.\n"
                "ممکن است سایت دسترسی ربات را محدود کرده باشد.\n\n"
                + error[:120]
            )
        else:
            body = "\n".join(lines) if lines else "اطلاعاتی پیدا نشد."
        textwidget(self._content, text=body)
        self._update_countdown()

    def _update_countdown(self):
        if not self._alive:
            return
        if self._next_reset is None:
            value = "زمان ریست بعدی: در اطلاعات سایت پیدا نشد"
        else:
            remaining = self._next_reset - datetime.now()
            if remaining.total_seconds() <= 0:
                value = "زمان اعلام‌شده گذشته است؛ بروزرسانی کنید."
            else:
                seconds = int(remaining.total_seconds())
                days, seconds = divmod(seconds, 86400)
                hours, seconds = divmod(seconds, 3600)
                minutes, seconds = divmod(seconds, 60)
                value = "تا ریست: {} روز، {:02d}:{:02d}:{:02d}".format(
                    days, hours, minutes, seconds
                )
        try:
            textwidget(self._countdown_text, text=value)
        except Exception:
            pass

    def _tick(self):
        if not self._alive:
            return
        self._update_countdown()
        apptimer(1.0, self._tick)


# ba_meta require api 9
# ba_meta export babase.Plugin
class BSLifeRankingPlugin(Plugin):
    def __init__(self):
        from bauiv1lib import party
        self._old_party_init = party.PartyWindow.__init__
        plugin = self

        def party_init(window, *args, **kwargs):
            result = plugin._old_party_init(window, *args, **kwargs)
            try:
                buttonwidget(
                    parent=window._root_widget,
                    label="Ranking",
                    size=(92, 30),
                    position=(window._width - 105, 15),
                    color=(0.12, 0.48, 0.72),
                    textcolor=(1, 1, 1),
                    button_type="square",
                    on_activate_call=plugin.open_ranking,
                )
            except Exception as exc:
                print("BSLife Ranking button error:", exc)
            return result

        party.PartyWindow.__init__ = party_init

    def open_ranking(self):
        try:
            RankingWindow()
            bui.getsound("swish").play()
        except Exception as exc:
            bui.screenmessage("Ranking error: " + str(exc), color=(1, 0, 0))
            print("BSLife Ranking error:", exc)

    def on_app_shutdown(self):
        try:
            from bauiv1lib import party
            party.PartyWindow.__init__ = self._old_party_init
        except Exception:
            pass
