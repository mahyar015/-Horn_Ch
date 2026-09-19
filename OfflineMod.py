# ba_meta require api 9
# ba_meta export babase.Plugin

from babase import Plugin
from bauiv1 import apptimer as teck
from bascenev1 import (
    chatmessage as cmsg,
    get_foreground_host_activity,
    get_foreground_host_session,
    get_game_roster,
    get_chat_messages,
    DieMessage,
    FreezeMessage,
    ThawMessage,
    StandMessage,
    CelebrateMessage,
    PowerupMessage
)

px = ''
ok = 'Syydooh'


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
                return None, []
            last = msgs[-1]
            if ': ' in last:
                _, content = last.split(': ', 1)
            else:
                content = last
            content = content.strip()
            parts = content.split()
            if not parts:
                return None, []
            return parts[0], parts[1:]
        except:
            return None, []

    @staticmethod
    def _process_cmd():
        try:
            msgs = get_chat_messages()
            if msgs:
                last = msgs[-1]
                if last != getattr(_cmds, '_last', None):
                    _cmds._last = last
                    cmd, args = _cmds._parse_chat()
                    if cmd and cmd.startswith(px):
                        _cmds._handle(cmd, args)
        except:
            pass
        teck(0.2, _cmds._process_cmd)

    @staticmethod
    def _handle(m, n):
        roster = get_game_roster()
        session_players = _cmds._get_session_players()
        activity_players = _cmds._get_players()

        n1 = n[1:] if len(n) > 1 else []
        n2 = n[2:] if len(n) > 2 else []

        if m == px + ok:
            cmsg('help for help')

        elif m == px + 'help':
            if n == []:
                cmsg('===== HELP =====')
                cmsg('h d g sp cu sl hed v r sm')
                cmsg('n e pun sh fr u cel fl')
                cmsg('bm bs bi bt tn')
                cmsg('day red dark pas camera')
                cmsg('superpunch fall tb bomb')
                cmsg('spun id Q')
                cmsg('===== HELP =====')

        elif m == px + 'id':
            cmsg('======= id ======')
            for i in session_players:
                try:
                    cmsg(i.getname() + ' -->  ' + str(session_players.index(i)))
                except:
                    pass

        elif m == px + 'Q':
            cmsg("bye")

        elif m == px + 'day':
            try:
                activity = get_foreground_host_activity()
                activity.globalsnode.tint = (1.1, 1.2, 1.1)
                cmsg('day')
            except:
                pass

        elif m in [px + 'n', px + 'night']:
            try:
                activity = get_foreground_host_activity()
                activity.globalsnode.tint = (0.5, 0.7, 1.0)
                cmsg('night')
            except:
                pass

        elif m == px + 'red':
            try:
                activity = get_foreground_host_activity()
                activity.globalsnode.tint = (0.8, 0.0, 0.0)
                cmsg('red')
            except:
                pass

        elif m == px + 'dark':
            try:
                activity = get_foreground_host_activity()
                activity.globalsnode.tint = (0.3, 0.3, 0.3)
                cmsg('dark')
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
                        cmsg('Slow on')
                    else:
                        activity.globalsnode.slow_motion = False
                        cmsg('Slow off')
                except:
                    pass

        elif m == px + 'z':
            if n == []:
                try:
                    activity_players[0].actor.node.invincible = True
                    cmsg('Anti-punch on')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.invincible = True
                    cmsg('Anti-punch on all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.invincible = True
                    cmsg('Anti-punch on')
                except:
                    pass

        elif m in [px + 't', px + 'T']:
            if n == []:
                try:
                    for i in activity_players:
                        i.actor.bomb_scale = 6
                    cmsg('Bomb scale set')
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

        elif m in [px + 'spun', px + 'Spun']:
            if n == []:
                cmsg('spun 10')
            else:
                try:
                    for i in activity_players:
                        i.actor._punch_power_scale = int(n[0])
                    cmsg('Punch power ' + str(n[0]))
                except:
                    pass

        elif m == px + 'pas':
            if n == []:
                try:
                    activity = get_foreground_host_activity()
                    if not activity.globalsnode.paused:
                        activity.globalsnode.paused = True
                        cmsg('Paused')
                    else:
                        activity.globalsnode.paused = False
                        cmsg('Unpaused')
                except:
                    pass

        elif m == px + 'camera':
            if n == []:
                try:
                    activity = get_foreground_host_activity()
                    if activity.globalsnode.camera_mode != 'rotate':
                        activity.globalsnode.camera_mode = 'rotate'
                        cmsg('Rotate')
                    else:
                        activity.globalsnode.camera_mode = 'follow'
                        cmsg('Follow')
                except:
                    pass

        elif m in [px + 'r', px + 'remove']:
            if n == []:
                try:
                    session_players[0].remove_from_game()
                    cmsg('Removed')
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
                    session_players[int(n[0])].remove_from_game()
                    cmsg('Removed')
                except:
                    pass

        elif m == px + 'v':
            def make_inv(player):
                body = player.actor.node
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
            if n == []:
                try:
                    make_inv(activity_players[0])
                    cmsg('Invisible on')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        make_inv(i)
                    cmsg('Invisible on all')
                except:
                    pass
            else:
                try:
                    make_inv(activity_players[int(n[0])])
                    cmsg('Invisible on')
                except:
                    pass

        elif m == px + 'sp':
            if n == []:
                try:
                    activity_players[0].actor.node.hockey = True
                    cmsg('Speed on')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.hockey = True
                    cmsg('Speed on all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.hockey = True
                    cmsg('Speed on')
                except:
                    pass

        elif m == px + 'hed':
            if n == []:
                try:
                    activity_players[0].actor.node.head_model = None
                    cmsg('Headless on')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.head_model = None
                    cmsg('Headless on all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.head_model = None
                    cmsg('Headless on')
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
                    activity_players[int(n[0])].actor.node.handlemessage(DieMessage())
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
                    cmsg('Healed all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.handlemessage(
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
                    cmsg('Cursed all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.handlemessage(
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
                    cmsg('Sleeping all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.handlemessage('knockout', 8000)
                    cmsg('Sleeping')
                except:
                    pass

        elif m == px + 'superpunch':
            if n == []:
                try:
                    activity_players[0].actor._punch_power_scale = 15
                    activity_players[0].actor._punch_cooldown = 0
                    cmsg('Super punch on')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor._punch_power_scale = 15
                        i.actor._punch_cooldown = 0
                    cmsg('Super punch all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor._punch_power_scale = 15
                    activity_players[int(n[0])].actor._punch_cooldown = 0
                    cmsg('Super punch on')
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
                    cmsg('TNT all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.bomb_type = 'tnt'
                    cmsg('TNT given')
                except:
                    pass

        elif m == px + 'bt':
            if n == []:
                try:
                    activity_players[0].actor.bomb_type = 'impact'
                    cmsg('Impact given')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.bomb_type = 'impact'
                    cmsg('Impact all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.bomb_type = 'impact'
                    cmsg('Impact given')
                except:
                    pass

        elif m == px + 'bs':
            if n == []:
                try:
                    activity_players[0].actor.bomb_type = 'sticky'
                    cmsg('Sticky given')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.bomb_type = 'sticky'
                    cmsg('Sticky all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.bomb_type = 'sticky'
                    cmsg('Sticky given')
                except:
                    pass

        elif m == px + 'bi':
            if n == []:
                try:
                    activity_players[0].actor.bomb_type = 'ice'
                    cmsg('Ice given')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.bomb_type = 'ice'
                    cmsg('Ice all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.bomb_type = 'ice'
                    cmsg('Ice given')
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
                    cmsg('Mine all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.bomb_type = 'land_mine'
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
                    cmsg('Punch all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.handlemessage(
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
                    cmsg('Shield all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.handlemessage(
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
                    cmsg('Frozen all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.handlemessage(FreezeMessage())
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
                    cmsg('Thawed all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.handlemessage(ThawMessage())
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
                    cmsg('Teleport all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.handlemessage(StandMessage())
                    cmsg('Teleported')
                except:
                    pass

        elif m == px + 'cel':
            if n == []:
                try:
                    activity_players[0].actor.node.handlemessage(CelebrateMessage())
                    cmsg('Celebrate')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.handlemessage(CelebrateMessage())
                    cmsg('Celebrate all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.handlemessage(CelebrateMessage())
                    cmsg('Celebrate')
                except:
                    pass

        elif m == px + 'fl':
            if n == []:
                try:
                    activity_players[0].actor.node.fly = True
                    cmsg('Fly on')
                except:
                    pass
            elif n[0] == 'a':
                try:
                    for i in activity_players:
                        i.actor.node.fly = True
                    cmsg('Fly on all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.fly = True
                    cmsg('Fly on')
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
                    cmsg('God mod on all')
                except:
                    pass
            else:
                try:
                    activity_players[int(n[0])].actor.node.invincible = True
                    activity_players[int(n[0])].actor._punch_power_scale = 7
                    cmsg('God mod on')
                except:
                    pass

        elif m in [px + 'bomb', px + 'default_bomb']:
            if n == []:
                cmsg('bomb: ice impact land_mine normal sticky tnt')
            elif n[0] in ['ice', 'impact', 'land_mine', 'normal', 'sticky', 'tnt']:
                try:
                    for i in activity_players:
                        i.actor.bomb_type = n[0]
                    cmsg('Bomb ' + n[0])
                except:
                    pass

        elif m == px + 'tb':
            if n == []:
                cmsg('tb 3')
            else:
                try:
                    for i in activity_players:
                        i.actor.set_bomb_count(int(n[0]))
                    cmsg('Bomb count ' + str(n[0]))
                except:
                    pass


# ba_meta require api 9
# ba_meta export babase.Plugin
class CMD(Plugin):
    def __init__(s):
        teck(1, _cmds._process_cmd)
