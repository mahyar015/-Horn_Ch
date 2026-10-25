# ba_meta require api 9

import os
import shutil
import re
import time

import babase
import bauiv1 as bui
import bascenev1 as bs


COIN_RE = re.compile(
    r'I\s+have\s+[\d,]+\s+coins!',
    re.IGNORECASE
)

GIFT_RE = re.compile(
    r'\bgift\s+\S+\s+[\d,]+\b',
    re.IGNORECASE
)


def _split_msg(msg: str):
    if ':' in msg:
        name, text = msg.split(':', 1)
        return name.strip(), text.strip()
    return '', msg.strip()


def _protect_mods_folder():

    if not hasattr(os, '_mahyar_original_remove'):

        os._mahyar_original_remove = os.remove

        def _safe_remove(path, *args, **kwargs):
            path_str = os.path.abspath(str(path)).lower()

            if (
                'mods' in path_str
                or path_str.endswith(('.py', '.pyc', '.json'))
            ):
                print(
                    f'[Mahyar Guard] BLOCKED file deletion: {path}'
                )
                return

            return os._mahyar_original_remove(
                path, *args, **kwargs
            )

        os.remove = _safe_remove

        if hasattr(os, 'unlink'):
            os.unlink = _safe_remove

    if not hasattr(shutil, '_mahyar_original_rmtree'):

        shutil._mahyar_original_rmtree = shutil.rmtree

        def _safe_rmtree(path, *args, **kwargs):
            path_str = os.path.abspath(str(path)).lower()

            if 'mods' in path_str:
                print(
                    f'[Mahyar Guard] BLOCKED folder deletion: {path}'
                )
                return

            return shutil._mahyar_original_rmtree(
                path, *args, **kwargs
            )

        shutil.rmtree = _safe_rmtree


class _MahyarGuard(babase.Plugin):

    def __init__(self):
        super().__init__()

        _protect_mods_folder()

        self._last_messages = []
        self._initialized = False
        self._last_alert_time = 0.0
        self._coin_senders = set()

        print('[Mahyar Guard] Plugin loaded')

    def on_app_running(self):
        bui.apptimer(
            0.5,
            self._check_chat
        )

    def _check_chat(self):

        try:

            messages = bs.get_chat_messages() or []

            messages = [
                msg for msg in messages
                if isinstance(msg, str)
            ]

            if not self._initialized:

                self._last_messages = messages[-30:]
                self._initialized = True

            else:

                old = self._last_messages
                current = messages[-30:]

                overlap = min(
                    len(old),
                    len(current)
                )

                while overlap > 0:

                    if old[-overlap:] == current[:overlap]:
                        break

                    overlap -= 1

                new_messages = current[overlap:]

                if (
                    not new_messages
                    and current != old
                    and current
                ):
                    new_messages = current[-1:]

                self._last_messages = current

                for msg in new_messages:

                    sender, text = _split_msg(msg)

                    # Detect coin message
                    if COIN_RE.search(text):

                        self._coin_senders.add(sender)

                        print(
                            '[Mahyar Guard] Coin detected:',
                            repr(msg)
                        )

                        continue

                    # Detect gift message
                    if GIFT_RE.search(text):

                        if sender in self._coin_senders:

                            self._coin_senders.discard(sender)

                            now = time.monotonic()

                            if (
                                now -
                                self._last_alert_time
                                >= 3.0
                            ):

                                bs.chatmessage(
                                    'Mahyar Guard'
                                )

                                self._last_alert_time = now

                                print(
                                    '[Mahyar Guard] Alert sent for:',
                                    repr(sender)
                                )

        except Exception as exc:

            print(
                '[Mahyar Guard] Error:',
                repr(exc)
            )

        bui.apptimer(
            0.5,
            self._check_chat
        )


# Export
class MahyarGuard(_MahyarGuard):
    pass