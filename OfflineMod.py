from babase import Plugin
import bascenev1 as bs
from bauiv1 import apptimer as teck, screenmessage as push, getsound as gs
import re

_p_activity = None
_p_session = None

def _get_players():
    global _p_activity
    try:
        _p_activity = bs.get_foreground_host_activity()
        if _p_activity and _p_activity.players:
            return list(_p_activity.players)
    except: pass
    return []

def _get_session_players():
    global _p_session
    try:
        _p_session = bs.get_foreground_host_session()
        if _p_session and _p_session.sessionplayers:
            return list(_p_session.sessionplayers)
    except: pass
    return []

def _send(msg):
    try: bs.chatmessage(msg)
    except: pass

def _find_player(arg):
    players = _get_players()
    if not players: return None
    if not arg:
        return players[0] if players else None
    if arg.lower() == 'a':
        return 'ALL'
    try:
        idx = int(arg)
        if 0 <= idx < len(players):
            return players[idx]
    except: pass
    return None

def _apply_to_targets(target, callback):
    if target == 'ALL':
        for p in _get_players():
            try: callback(p)
            except: pass
    elif target:
        try: callback(target)
        except: pass

# ============================================
# 🎯 HANDLERS
# ============================================

def cmd_h(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def heal(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                node = pl.actor.node
                if hasattr(node, 'heal'):
                    node.heal()
                elif hasattr(pl.actor, 'hitpoints'):
                    pl.actor.hitpoints = 1000
        except: pass
    _apply_to_targets(target, heal)
    _send("Healed!")

def cmd_d(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def kill(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.handle_message({'type': 'die'})
        except: pass
    _apply_to_targets(target, kill)
    _send("Killed!")

def cmd_g(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def god(pl):
        try:
            if pl.actor:
                if hasattr(pl.actor, 'hitpoints'):
                    pl.actor.hitpoints = 999999
                if hasattr(pl.actor, 'punch_power'):
                    pl.actor.punch_power = 10.0
        except: pass
    _apply_to_targets(target, god)
    _send("God mode ON!")

def cmd_z(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def shield(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'equip_shields'):
                pl.actor.equip_shields()
        except: pass
    _apply_to_targets(target, shield)
    _send("Shield ON!")

def cmd_sp(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def speed(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.speed_scale = 2.0
        except: pass
    _apply_to_targets(target, speed)
    _send("Speed up!")

def cmd_sm(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def slow(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.speed_scale = 0.4
        except: pass
    _apply_to_targets(target, slow)
    _send("Slow motion!")

def cmd_cu(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def curse(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'curse'):
                pl.actor.curse()
        except: pass
    _apply_to_targets(target, curse)
    _send("Cursed!")

def cmd_sl(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def sleep(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.handle_message({'type': 'knockout'})
        except: pass
    _apply_to_targets(target, sleep)
    _send("Sleeping!")

def cmd_hed(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def headless(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.head_scale = 0.01
        except: pass
    _apply_to_targets(target, headless)
    _send("Headless!")

def cmd_v(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def invis(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.color = (1, 1, 1, 0.05)
        except: pass
    _apply_to_targets(target, invis)
    _send("Invisible!")

def cmd_r(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def remove(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.delete()
        except: pass
    _apply_to_targets(target, remove)
    _send("Removed!")

def cmd_fr(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def freeze(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.frozen = True
        except: pass
    _apply_to_targets(target, freeze)
    _send("Frozen!")

def cmd_u(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def thaw(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.frozen = False
        except: pass
    _apply_to_targets(target, thaw)
    _send("Thawed!")

def cmd_cel(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    _send(":)")

def cmd_fl(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def fly(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.fly = True
        except: pass
    _apply_to_targets(target, fly)
    _send("Flying!")

def cmd_fall(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def fall(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'node'):
                pl.actor.node.position = (0, 0, 0)
        except: pass
    _apply_to_targets(target, fall)
    _send("Teleported to 0,0,0!")

def cmd_pun(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def punch(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'punch_power'):
                pl.actor.punch_power = 1.0
        except: pass
    _apply_to_targets(target, punch)
    _send("Punch normal!")

def cmd_sh(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def shield(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'equip_shields'):
                pl.actor.equip_shields()
        except: pass
    _apply_to_targets(target, shield)
    _send("Shield!")

def cmd_superpunch(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def sp(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'punch_power'):
                pl.actor.punch_power = 10.0
        except: pass
    _apply_to_targets(target, sp)
    _send("Super punch!")

def cmd_spun(p, arg=None):
    _send("spun: use 'spun <power>' (not fully supported)")

# Bombs
def cmd_bm(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def bm(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'default_bomb_type'):
                pl.actor.default_bomb_type = 'normal'
        except: pass
    _apply_to_targets(target, bm)
    _send("Bomb: Normal")

def cmd_bs(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def bs(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'default_bomb_type'):
                pl.actor.default_bomb_type = 'sticky'
        except: pass
    _apply_to_targets(target, bs)
    _send("Bomb: Sticky")

def cmd_bi(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def bi(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'default_bomb_type'):
                pl.actor.default_bomb_type = 'ice'
        except: pass
    _apply_to_targets(target, bi)
    _send("Bomb: Ice")

def cmd_bt(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def bt(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'default_bomb_type'):
                pl.actor.default_bomb_type = 'impact'
        except: pass
    _apply_to_targets(target, bt)
    _send("Bomb: Impact")

def cmd_tn(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def tn(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'default_bomb_type'):
                pl.actor.default_bomb_type = 'tnt'
        except: pass
    _apply_to_targets(target, tn)
    _send("Bomb: TNT")

def cmd_bomb(p, arg=None):
    _send("bomb: set default bomb type")

def cmd_tb(p, arg=None):
    target = _find_player(arg)
    if not target: _send("Player not found!"); return
    def tb(pl):
        try:
            if pl.actor and hasattr(pl.actor, 'max_bombs'):
                pl.actor.max_bombs = 3
        except: pass
    _apply_to_targets(target, tb)
    _send("Max bombs: 3")

# Environment
def cmd_day(p, arg=None):
    try:
        act = bs.get_foreground_host_activity()
        if act and hasattr(act, 'globalsnode'):
            act.globalsnode.tint = (1, 1, 1)
    except: pass
    _send("Day!")

def cmd_n(p, arg=None):
    try:
        act = bs.get_foreground_host_activity()
        if act and hasattr(act, 'globalsnode'):
            act.globalsnode.tint = (0.3, 0.3, 0.5)
    except: pass
    _send("Night!")

def cmd_red(p, arg=None):
    try:
        act = bs.get_foreground_host_activity()
        if act and hasattr(act, 'globalsnode'):
            act.globalsnode.tint = (1, 0.2, 0.2)
    except: pass
    _send("Red!")

def cmd_dark(p, arg=None):
    try:
        act = bs.get_foreground_host_activity()
        if act and hasattr(act, 'globalsnode'):
            act.globalsnode.tint = (0.1, 0.1, 0.1)
    except: pass
    _send("Dark!")

def cmd_t(p, arg=None):
    _send("t: set sky color")

def cmd_pas(p, arg=None):
    try:
        act = bs.get_foreground_host_activity()
        if act:
            act.paused = not act.paused
    except: pass
    _send("Pause toggled!")

def cmd_camera(p, arg=None):
    try:
        act = bs.get_foreground_host_activity()
        if act and hasattr(act, 'globalsnode'):
            act.globalsnode.camera_mode = 'rotate'
    except: pass
    _send("Camera rotate!")

def cmd_e(p, arg=None):
    try:
        act = bs.get_foreground_host_activity()
        if act and hasattr(act, 'end'):
            act.end()
    except: pass
    _send("Game ended!")

# Info
def cmd_help(p, arg=None):
    _send("Commands: h d g z sp sm cu sl hed v r fr u cel fl fall pun sh superpunch bm bs bi bt tn tb day n red dark pas camera e id")

def cmd_id(p, arg=None):
    try:
        sp = _get_session_players()
        ap = _get_players()
        if sp and ap:
            for i, s in enumerate(sp):
                name = s.get_name() if hasattr(s, 'get_name') else '?'
                _send(f"[{i}] {name}")
    except: pass

# ============================================
# 🎯 COMMAND MAP
# ============================================
COMMANDS = {
    'h': cmd_h, 'd': cmd_d, 'g': cmd_g, 'z': cmd_z,
    'sp': cmd_sp, 'sm': cmd_sm, 'cu': cmd_cu, 'sl': cmd_sl,
    'hed': cmd_hed, 'v': cmd_v, 'r': cmd_r, 'fr': cmd_fr,
    'u': cmd_u, 'cel': cmd_cel, 'fl': cmd_fl, 'fall': cmd_fall,
    'pun': cmd_pun, 'sh': cmd_sh, 'superpunch': cmd_superpunch,
    'spun': cmd_spun, 'bm': cmd_bm, 'bs': cmd_bs, 'bi': cmd_bi,
    'bt': cmd_bt, 'tn': cmd_tn, 'bomb': cmd_bomb, 'tb': cmd_tb,
    'day': cmd_day, 'n': cmd_n, 'red': cmd_red, 'dark': cmd_dark,
    't': cmd_t, 'pas': cmd_pas, 'camera': cmd_camera, 'e': cmd_e,
    'help': cmd_help, 'id': cmd_id,
}

# ============================================
# 🎯 CHAT LISTENER
# ============================================
_last_msg = ""

def chat_ear():
    global _last_msg
    try:
        teck(0.2, chat_ear)
        msgs = bs.get_chat_messages()
        if not msgs: return
        last = msgs[-1]
        if last == _last_msg: return
        _last_msg = last

        # جدا کردن متن
        content = last
        if ': ' in last:
            _, content = last.split(': ', 1)
        content = content.strip()

        parts = content.split()
        if not parts: return

        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None

        if cmd in COMMANDS:
            COMMANDS[cmd](None, arg)
    except: 
        try: teck(0.2, chat_ear)
        except: pass

# ============================================
# 🎯 PLUGIN
# ============================================
# ba_meta require api 9
# ba_meta export babase.Plugin
class AdminPanel(Plugin):
    def __init__(s):
        teck(1, chat_ear)
        teck(2.0, lambda: push("Admin Panel Loaded - By Mahyar", color=(0.4, 0.8, 1.0)))
