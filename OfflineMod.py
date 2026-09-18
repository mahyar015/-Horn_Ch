# ba_meta require api 9
# ba_meta export babase.Plugin

from babase import Plugin
from bauiv1 import (
    apptimer as teck,
    screenmessage as smsg,
    getsound as gs
)
from bascenev1 import (
    chatmessage as cmsg,
    get_foreground_host_activity,
    get_foreground_host_session,
    get_game_roster,
    get_chat_messages,
    set_party_icon_always_visible,
    DieMessage,
    FreezeMessage,
    ThawMessage,
    StandMessage,
    CelebrateMessage,
    PowerupMessage
)

px = ''
ok = 'Syydooh'
a = ''

_last_msg = ""


class _cmds:

    @staticmethod
    def _get_players():
        try:
            activity = get_foreground_host_activity()
            if activity and activity.players:
                return list(activity.players)
        except:
            pass
        return []

    @staticmethod
    def _get_session_players():
        try:
            session = get_foreground_host_session()
            if session and session.sessionplayers:
                return list(session.sessionplayers)
        except:
            pass
        return []

    @staticmethod
    def _parse_chat():
        try:
            msgs = get_chat_messages()
            if not msgs:
                return None, None, []
            last = msgs[-1]
            if ': ' in last:
                _, content = last.split(': ', 1)
            else:
                content = last
            content = content.strip()
            parts = content.split()
            if not parts:
                return None, None, []
            cmd = parts[0]
            args = parts[1:]
            return content, cmd, args
        except:
            return None, None, []

    @staticmethod
    def _process_cmd():
        try:
            msgs = get_chat_messages()
            if not msgs:
                return
            last = msgs[-1]
            if last == getattr(_cmds, '_last', None):
                return
            _cmds._last = last

            content, cmd, args = _cmds._parse_chat()
            if not cmd:
                return
            if cmd.startswith(px):
                _cmds._handle(cmd, args)
        except:
            pass

    @staticmethod
    def _handle(m, n):
        try:
            set_party_icon_always_visible(True)
        except:
            pass

        roster = get_game_roster()
        session_players = _cmds._get_session_players()
        activity_players = _cmds._get_players()

        n1 = n[1:] if len(n) > 1 else []
        n2 = n[2:] if len(n) > 2 else []

        if m == px + ok:
            cmsg('help for help')

        elif m == px + 'help':
            if n == []:
                cmsg('===========================================')
                cmsg('id = مشخص کننده ایدی های پلیر ها')
                cmsg('h = پر کردن جون به صد در صد')
                cmsg('d = کشتن')
                cmsg('g = GOD MODE')
                cmsg('sp = سرعت راه رفتن')
                cmsg('cu = سمی کردن')
                cmsg('sl = خوابیدن یا بیهوش کردن')
                cmsg('hed = محو شدن سر بازیکن')
                cmsg('v = نامرعی شدن')
                cmsg('r = حذف کردن پلیر')
                cmsg('sm = حرکت اهسته')
                cmsg('n = شب کردن مپ')
                cmsg('e = پایان دادن به بازی')
                cmsg('pun = مشت یا کمکی بکس')
                cmsg('sh = شیلد یا محافظ')
                cmsg('fr = یخ زدن')
                cmsg('u = آب شدن یا همون آن فریز')
                cmsg('cel = خوشحالی')
                cmsg('fl = پرواز دو بعدی')
                cmsg('bm = انداختن مین به جای بمب')
                cmsg('bs = انداختن بمب چسبناک به جای بمب')
                cmsg('bi = اندتختن بمب یخی به جای بمب')
                cmsg('bt = انداختن بمب کرونایی به جای بمب')
                cmsg('t = تنظیم رنگ هوا')
                cmsg('======= New command =======')
                cmsg('day = روز')
                cmsg('red = هوای قرمز یا خونی')
                cmsg('dark = هوای سیاه و تاریک')
                cmsg('pas = متوقف کردن بازی')
                cmsg('superpunch = مشت گودرت مند')
                cmsg('fall = تلپورت به ادرس ۰,۰,۰')
                cmsg('camera = چرخیدن دوربین')
                cmsg('tb = ثبت تعداد حداکثر انداختن بمب')
                cmsg('bomb = ثبت نوع بمب')
                cmsg('tn = انداختن تی ان تی به جای بمب')
                cmsg('spun = تنظیم قدرت مشت')
                cmsg('Q = خروج از بازی (حرف بزرگ نوشته شود!)')
                cmsg('===========================================')

        elif m == px + 'id':
            cmsg('======= id ======')
            for i in session_players:
                try:
                    cmsg(i.getname() + ' -->  ' + str(session_players.index(i)) + '\n')
                except:
                    pass
            if roster:
                for i in roster:
                    cmsg(f'======For {px}kick only======')
                    try:
                        cmsg(str(i['players'][0]['name_full']) + '   -   ' + str(i['client_id']))
                    except:
                        pass

        elif m == px + 'Q':
            cmsg("پیدرت")

        elif m == px + 'day':
            try:
                activity = get_foreground_host_activity()
                activity.globalsnode.tint = (1.1, 1.2, 1.1)
            except:
                pass

        elif m in [px + 'n', px + 'night']:
            try:
                activity = get_foreground_host_activity()
                activity.globalsnode.tint = (0.5, 0.7, 1.0)
            except:
                pass

        elif m == px + 'red':
            try:
                activity = get_foreground_host_activity()
                activity.globalsnode.tint = (0.8, 0.0, 0.0)
            except:
                pass

        elif m == px + 'dark':
            try:
                activity = get_foreground_host_activity()
                activity.globalsnode.tint = (0.3, 0.3, 0.3)
            except:
                pass

        elif m in [px + 'end', px + 'e']:
            if n == []:
                try:
                    activity = get_foreground_host_activity()
                    for i in activity.players:
                        try:
                            i.actor.node.handlemessage(DieMessage())
                        except:
                            pass
                    activity.end_game()
                except:
                    pass

        elif m in [px + 'sm', px + 'slow']:
            if n == []:
                try:
                    activity = get_foreground_host_activity()
                    if not activity.globalsnode.slow_motion:
                        activity.globalsnode.slow_motion = True
                        cmsg('Slow mode = on')
                    else:
                        activity.globalsnode.slow_motion = False
                        cmsg('Slow mode = off')
                except:
                    pass

        elif m == px + 'z':
            if n == []:
                try:
                    activity_players[0].actor.node.invincible = True
                    cmsg('Anti-punch ON')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.invincible = True
                    cmsg('Anti-punch ON (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.invincible = True
                    cmsg('Anti-punch ON')
                except:
                    pass

        elif m in [px + 't', px + 'T']:
            if n == []:
                try:
                    for i in activity_players:
                        i.actor.bomb_scale = 6
                except:
                    pass
            else:
                try:
                    e1 = float(n[0])
                    e2 = float(n1[0])
                    e3 = float(n2[0])
                    activity = get_foreground_host_activity()
                    activity.globalsnode.tint = (e1, e2, e3)
                    cmsg('Tint set')
                except:
                    pass

        elif m in [px + 'spun', px + 'Spun', px + 'Gpun', px + 'gpun']:
            if n == []:
                cmsg('Mesal: spun 10')
            else:
                try:
                    for i in activity_players:
                        i.actor._punch_power_scale = int(n[0])
                    cmsg('Punch power = ' + str(n[0]))
                except:
                    pass

        elif m == px + 'pas':
            if n == []:
                try:
                    activity = get_foreground_host_activity()
                    if not activity.globalsnode.paused:
                        activity.globalsnode.paused = True
                        cmsg('Game Paused')
                    else:
                        activity.globalsnode.paused = False
                        cmsg('Game un-paused')
                except:
                    pass

        elif m == px + 'camera':
            if n == []:
                try:
                    activity = get_foreground_host_activity()
                    if activity.globalsnode.camera_mode != 'rotate':
                        activity.globalsnode.camera_mode = 'rotate'
                        cmsg('Camera rotate')
                    else:
                        activity.globalsnode.camera_mode = 'follow'
                        cmsg('Camera follow')
                except:
                    pass

        elif m in [px + 'r', px + 'remove']:
            if n == []:
                try:
                    session_players[0].remove_from_game()
                    cmsg('Player removed')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in session_players:
                        i.remove_from_game()
                    cmsg('All removed')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    session_players[idx].remove_from_game()
                    cmsg('Player removed')
                except:
                    pass

        elif m == px + 'v':
            if n == []:
                try:
                    body = activity_players[0].actor.node
                    body.head_model = None
                    body.torso_model = None
                    body.upper_arm_model = None
                    body.forearm_model = None
                    body.pelvis_model = None
                    body.hand_model = None
                    body.toes_model = None
                    body.upper_leg_model = None
                    body.lower_leg_model = None
                    body.style = 'cyborg'
                    cmsg('Invisible ON')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        body = i.actor.node
                        body.head_model = None
                        body.torso_model = None
                        body.upper_arm_model = None
                        body.forearm_model = None
                        body.pelvis_model = None
                        body.hand_model = None
                        body.toes_model = None
                        body.upper_leg_model = None
                        body.lower_leg_model = None
                        body.style = 'cyborg'
                    cmsg('Invisible ON (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    body = activity_players[idx].actor.node
                    body.head_model = None
                    body.torso_model = None
                    body.upper_arm_model = None
                    body.forearm_model = None
                    body.pelvis_model = None
                    body.hand_model = None
                    body.toes_model = None
                    body.upper_leg_model = None
                    body.lower_leg_model = None
                    body.style = 'cyborg'
                    cmsg('Invisible ON')
                except:
                    pass

        elif m == px + 'sp':
            if n == []:
                try:
                    activity_players[0].actor.node.hockey = True
                    cmsg('Speed ON')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.hockey = True
                    cmsg('Speed ON (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.hockey = True
                    cmsg('Speed ON')
                except:
                    pass

        elif m == px + 'hed':
            if n == []:
                try:
                    activity_players[0].actor.node.head_model = None
                    cmsg('Headless ON')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.head_model = None
                    cmsg('Headless ON (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.head_model = None
                    cmsg('Headless ON')
                except:
                    pass

        elif m in [px + 'd', px + 'D']:
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage(DieMessage())
                    cmsg('Killed')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage(DieMessage())
                    cmsg('All killed')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.handlemessage(DieMessage())
                    cmsg('Killed')
                except:
                    pass

        elif m in [px + 'h', px + 'H']:
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage(
                        PowerupMessage(poweruptype='health'))
                    cmsg('Healed')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage(
                            PowerupMessage(poweruptype='health'))
                    cmsg('Healed (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.handlemessage(
                        PowerupMessage(poweruptype='health'))
                    cmsg('Healed')
                except:
                    pass

        elif m in [px + 'cu', px + 'Cu']:
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage(
                        PowerupMessage(poweruptype='curse'))
                    cmsg('Cursed')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage(
                            PowerupMessage(poweruptype='curse'))
                    cmsg('Cursed (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.handlemessage(
                        PowerupMessage(poweruptype='curse'))
                    cmsg('Cursed')
                except:
                    pass

        elif m == px + 'sl':
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage('knockout', 8000)
                    cmsg('Sleeping')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage('knockout', 8000)
                    cmsg('Sleeping (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.handlemessage('knockout', 8000)
                    cmsg('Sleeping')
                except:
                    pass

        elif m == px + 'superpunch':
            if n == []:
                try:
                    activity_players[0].actor._punch_power_scale = 15
                    activity_players[0].actor._punch_cooldown = 0
                    cmsg('Super punch ON')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor._punch_power_scale = 15
                        i.actor._punch_cooldown = 0
                    cmsg('Super punch ON (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor._punch_power_scale = 15
                    activity_players[idx].actor._punch_cooldown = 0
                    cmsg('Super punch ON')
                except:
                    pass

        elif m in [px + 'tn', px + 'tnt']:
            if n == []:
                try:
                    activity_players[0].actor.bomb_type = 'tnt'
                    cmsg('TNT given')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.bomb_type = 'tnt'
                    cmsg('TNT given (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.bomb_type = 'tnt'
                    cmsg('TNT given')
                except:
                    pass

        elif m == px + 'bt':
            if n == []:
                try:
                    activity_players[0].actor.bomb_type = 'impact'
                    cmsg('Impact bomb given')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.bomb_type = 'impact'
                    cmsg('Impact bomb given (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.bomb_type = 'impact'
                    cmsg('Impact bomb given')
                except:
                    pass

        elif m == px + 'bs':
            if n == []:
                try:
                    activity_players[0].actor.bomb_type = 'sticky'
                    cmsg('Sticky bomb given')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.bomb_type = 'sticky'
                    cmsg('Sticky bomb given (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.bomb_type = 'sticky'
                    cmsg('Sticky bomb given')
                except:
                    pass

        elif m == px + 'bi':
            if n == []:
                try:
                    activity_players[0].actor.bomb_type = 'ice'
                    cmsg('Ice bomb given')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.bomb_type = 'ice'
                    cmsg('Ice bomb given (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.bomb_type = 'ice'
                    cmsg('Ice bomb given')
                except:
                    pass

        elif m == px + 'bm':
            if n == []:
                try:
                    activity_players[0].actor.bomb_type = 'land_mine'
                    cmsg('Mine given')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.bomb_type = 'land_mine'
                    cmsg('Mine given (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.bomb_type = 'land_mine'
                    cmsg('Mine given')
                except:
                    pass

        elif m == px + 'pun':
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage(
                        PowerupMessage(poweruptype='punch'))
                    cmsg('Punch given')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage(
                            PowerupMessage(poweruptype='punch'))
                    cmsg('Punch given (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.handlemessage(
                        PowerupMessage(poweruptype='punch'))
                    cmsg('Punch given')
                except:
                    pass

        elif m == px + 'sh':
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage(
                        PowerupMessage(poweruptype='shield'))
                    cmsg('Shield given')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage(
                            PowerupMessage(poweruptype='shield'))
                    cmsg('Shield given (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.handlemessage(
                        PowerupMessage(poweruptype='shield'))
                    cmsg('Shield given')
                except:
                    pass

        elif m == px + 'fr':
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage(FreezeMessage())
                    cmsg('Frozen')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage(FreezeMessage())
                    cmsg('Frozen (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.handlemessage(FreezeMessage())
                    cmsg('Frozen')
                except:
                    pass

        elif m == px + 'u':
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage(ThawMessage())
                    cmsg('Thawed')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage(ThawMessage())
                    cmsg('Thawed (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.handlemessage(ThawMessage())
                    cmsg('Thawed')
                except:
                    pass

        elif m == px + 'fall':
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage(StandMessage())
                    cmsg('Teleported')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage(StandMessage())
                    cmsg('Teleported (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.handlemessage(StandMessage())
                    cmsg('Teleported')
                except:
                    pass

        elif m == px + 'cel':
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage(CelebrateMessage())
                    cmsg('Celebrated')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage(CelebrateMessage())
                    cmsg('Celebrated (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.handlemessage(CelebrateMessage())
                    cmsg('Celebrated')
                except:
                    pass

        elif m == px + 'fl':
            if n == []:
                try:
                    activity_players[0].actor.node.fly = True
                    cmsg('Fly ON')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.fly = True
                    cmsg('Fly ON (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.fly = True
                    cmsg('Fly ON')
                except:
                    pass

        elif m == px + 'g':
            if n == []:
                try:
                    activity_players[0].actor.node.invincible = True
                    activity_players[0].actor._punch_power_scale = 7
                    cmsg('God mod on')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.invincible = True
                        i.actor._punch_power_scale = 7
                    cmsg('God mod on (all)')
                except:
                    pass
            else:
                try:
                    idx = int(n[0])
                    activity_players[idx].actor.node.invincible = True
                    activity_players[idx].actor._punch_power_scale = 7
                    cmsg('God mod on')
                except:
                    pass

        elif m in [px + 'bomb', px + 'default_bomb']:
            if n == []:
                cmsg('bomb: ice / impact / land_mine / normal / sticky / tnt')
            elif n[0] == 'help':
                cmsg("bombtypes: ice / impact / land_mine / normal / sticky / tnt")
            elif n[0] in ['ice', 'impact', 'land_mine', 'normal', 'sticky', 'tnt']:
                try:
                    for i in activity_players:
                        i.actor.bomb_type = n[0]
                    cmsg('Bomb type = ' + n[0])
                except:
                    pass
            else:
                cmsg('Bomb: ice / impact / land_mine / normal / sticky / tnt')

        elif m == px + 'tb':
            if n == []:
                cmsg('Mesal: tb 3')
            else:
                try:
                    for i in activity_players:
                        i.actor.set_bomb_count(int(n[0]))
                    cmsg('Bomb count = ' + str(n[0]))
                except:
                    pass


# ba_meta require api 9
# ba_meta export babase.Plugin
class CMD(Plugin):
    def __init__(s):
        cmsg("CMD Mod - By @bombsquad_mod1")
        teck(0, _cmds._process_cmd)
