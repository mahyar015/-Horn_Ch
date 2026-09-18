"""This Mod By @Horn_Ch"""

# ba_meta require api 9
from babase import (
    get_foreground_host_activity,
    get_foreground_host_session,
    get_game_roster,
    get_chat_messages,
    set_party_icon_always_visible,
    chatmessage as cmsg,
    screenmessage as smsg
)
import bascenev1 as ba

px=''
a=''
ok='Syydooh'
ab = 'lotfa id on Player ra moshakhas Konid'

class _cmds:
	
	def _process_cmd():
		set_party_icon_always_visible(True)
		messages=get_chat_messages()
		if len(messages)>1:
			lastmsg = messages[len(messages)-1]
			
			m=lastmsg.split(' ')[1]
			if m.startswith(px):
				return _cmds._handle()
			else:
				pass
				
	def _handle():
		messages=get_chat_messages()
		if len(messages)>1:
			lastmsg = messages[len(messages)-1]
			
			m=lastmsg.split(' ')[1]
			n=lastmsg.split(' ')[2:] 
			n1=lastmsg.split(' ')[3:] 
			n2=lastmsg.split(' ')[4:] 
			
			roster=get_game_roster()
			session=get_foreground_host_session()
			session_players=session.sessionplayers
			
			activity=get_foreground_host_activity()
			activity_players=activity.players
			
			if m == px+ok:
				cmsg(px+'help for help')
				
			elif m == px+'help' :
				if n==[]:
					cmsg('===========================================')
					cmsg(f'id = نمایش شناسه بازیکنان')
					cmsg(f'h = بازیابی سلامت کامل')
					cmsg(f'd = نابود کردن')
					cmsg(f'g = حالت جاودانگی')
					cmsg(f'sp = تندتر کردن حرکت')
					cmsg(f'cu = نفرین کردن')
					cmsg(f'sl = بی هوش کردن')
					cmsg(f'hed = ناپدید کردن سر')
					cmsg(f'v = پنهان کردن کامل بدن')
					cmsg(f'r = اخراج بازیکن')
					cmsg(f'sm = حرکت آرام')
					cmsg(f'n = تاریک کردن محیط')
					cmsg(f'e = خاتمه دادن به مسابقه')
					cmsg(f'pun = نیروی مشت اضافه')
					cmsg(f'sh = سپر محافظ')
					cmsg(f'fr = منجمد کردن')
					cmsg(f'u = باز کردن یخ')
					cmsg(f'cel = جشن گرفتن')
					cmsg(f'fl = پرواز آزاد')
					cmsg(f'bm = جایگزینی بمب با مین')
					cmsg(f'bs = جایگزینی بمب با چسبونکی')
					cmsg(f'bi = جایگزینی بمب با یخی')
					cmsg(f'bt = جایگزینی بمب با ضربه‌ای')
					cmsg(f't = تنظیم رنگ فضا')
					cmsg(f'======= New command =======')
					cmsg(f'day = روشنایی روز')
					cmsg(f'red = فضای سرخ')
					cmsg(f'dark = فضای تیره')
					cmsg(f'pas = توقف بازی')
					cmsg(f'superpunch = قدرت عظیم مشت🦦')
					cmsg(f'fall = انتقال به مرکز')
					cmsg(f'camera = چرخش دید')
					cmsg(f'tb = تنظیم ظرفیت بمب')
					cmsg(f'bomb = تعیین نوع بمب')
					cmsg(f'tn = جایگزینی بمب با ناری')
					cmsg(f'spun = تنظیم قدرت ضربه')
					cmsg(f'Q = خروج از مسابقه (بزرگ بنویسید)')
					cmsg(f'===========================================')
			elif m in [ px+'id' ]:
				cmsg('======= id ======')
				for i in session_players:
					cmsg(i.getname()+' -->  '+str(session_players.index(i))+'\n')
				if not roster ==[]:
					for i in roster:
						cmsg(f'======For {px}kick only======')
					cmsg(str(i['players'][0]['nam_full'])+'   -   '+str(i['client_id']))
	
			elif m in [ px+'Q' ]:
				cmsg("خداحافظ")
	
			elif m in [ px+'day' ]:
				if activity.globalsnode.tint==(1.1,1.2,1.1):
					activity.globalsnode.tint=(1.1,1.2,1.1)
				else:
					activity.globalsnode.tint=(1.1,1.2,1.1)

			elif m in [ px+'n' , px+'night' ]:
				if activity.globalsnode.tint==(0.5, 0.7, 1.0):
					cmsg(f'')
				else:
					activity.globalsnode.tint=(0.5, 0.7, 1.0)
	
			elif m in [ px+'red' ]:
				if activity.globalsnode.tint==(0.8, 0.0, 0.0):
					cmsg(f'')
				else:
					activity.globalsnode.tint=(0.8, 0.0, 0.0)
	
			elif m in [ px+'dark' ]:
				if activity.globalsnode.tint==(0.3, 0.3, 0.3):
					cmsg(f'')
				else:
					activity.globalsnode.tint=(0.3, 0.3, 0.3)
			elif m in [ px+'end' , px+'e' ]:
				if n==[]:
					for i in activity_players:
						cmsg(a)
						i.actor.node.handlemessage(ba.DieMessage())
						activity.end_game()
					else:
						cmsg(a)
			elif m in [ px+'sm' , px+'slow' ]:
				if n==[]:
					if not activity.globalsnode.slow_motion:
						activity.globalsnode.slow_motion=True
						cmsg('حالت آرام = فعال')
					else:
						activity.globalsnode.slow_motion=False
						cmsg('حالت آرام = غیرفعال')
	
			elif m in [ px+'z' ]:
				if n==[]:
					try:
						is_name=session_players[int(0)].getname()
						if not activity_players[int(0)].actor.node.invincible==True:
							activity_players[int(0)].actor.node.invincible=True
							cmsg('مقاومت فعال شد برای '+is_name)
						else:
							activity_players[int(0)].actor.node.invincible=False
							cmsg('مقاومت غیرفعال شد برای '+is_name)
					except:
						cmsg('بازیکن یافت نشد')
				elif n[0]=='a':
					for i in activity_players:
						if not i.actor.node.invincible==True:
							i.actor.node.invincible=True
							cmsg('مقاومت برای همه فعال شد')
						else:
							i.actor.node.invincible=False
							cmsg('مقاومت برای همه غیرفعال شد')
				else:
					try:
						is_name=session_players[int(n[0])].getname()
						if not activity_players[int(n[0])].actor.node.invincible==True:
							activity_players[int(n[0])].actor.node.invincible=True
							cmsg('مقاومت فعال شد برای '+is_name)
						else:
							activity_players[int(n[0])].actor.node.invincible=False
							cmsg('مقاومت غیرفعال شد برای '+is_name)
					except:
						cmsg('بازیکن یافت نشد')
	
			elif m in [ px+'t' , px+'T' ]:
				if n == []:
					i.actor.bomb_scale: float = 6
				else:
					e1= float(n[0])
					e2= float(n1[0])
					e3= float(n2[0])
					activity.globalsnode.tint=(e1,e2,e3)
	
			elif m in [ px+'spun', px+'Spun', px+'Gpun', px+'gpun' ]:
				if n == []:
					cmsg('لطفاً مقدار قدرت ضربه را وارد کنید مثل: spun 10')
				else:
					try:
						for i in activity_players:
							i.actor._punch_power_scale=(int(n[0]))
							cmsg('قدرت ضربه روی '+str(n[0])+' تنظیم شد')
					except:
						cmsg('')
	
			elif m in [ px+'pas' ]:
				if n == []:
					if not activity.globalsnode.paused:
						activity.globalsnode.paused=True
						cmsg('بازی متوقف شد')
					else:
						activity.globalsnode.paused=False
						cmsg('بازی ادامه یافت')
	
			elif m in [ px+'camera' ]:
				if n == []:
					if not activity.globalsnode.camera_mode == 'rotate':
							activity.globalsnode.camera_mode = 'rotate'
							cmsg('')
					else:
						activity.globalsnode.camera_mode = 'follow'
						cmsg('')

			elif m in [ px+'r' , px+'remove' ]:
				if n == []:
					try:
						r=session_players[int(0)]
						r.remove_from_game()
						cmsg('بازیکن اخراج شد')
					except:
						cmsg('بازیکن اخراج شد')
				elif n[0] == 'a':
					for i in session_players:
						i.remove_from_game()
						cmsg('همه بازیکنان اخراج شدند')
				else:
					try:
						r=session_players[int(n[0])]
						r.remove_from_game()
						cmsg('بازیکن اخراج شد')
					except:
						cmsg('شناسه اشتباه است')
			elif m in  [ px+'v' ]:
				if n==[]:
					body=activity_players[int(0)].actor.node
					is_name=session_players[int(0)].getname()
					if not body.torso_model==None:
						body.head_model=None
						body.torso_model=None
						body.upper_arm_model=None
						body.forearm_model=None
						body.pelvis_model=None
						body.hand_model=None
						body.toes_model=None
						body.upper_leg_model=None
						body.lower_leg_model=None
						body.style='cyborg'
						cmsg(is_name+' نامرئی شد')
					else:
						cmsg('')
				elif n[0]=='a':
					for i in activity_players:
						body=i.actor.node
						if not body.torso_model==None:
							body.head_model=None
							body.torso_model=None
							body.upper_arm_model=None
							body.forearm_model=None
							body.pelvis_model=None
							body.hand_model=None
							body.toes_model=None
							body.upper_leg_model=None
							body.lower_leg_model=None
							body.style='cyborg'
						else:
							cmsg('')
				else:
					body=activity_players[int(n[0])].actor.node
					is_name=session_players[int(n[0])].getname()
					if not body.torso_model==None:
						body.head_model=None
						body.torso_model=None
						body.upper_arm_model=None
						body.forearm_model=None
						body.pelvis_model=None
						body.hand_model=None
						body.toes_model=None
						body.upper_leg_model=None
						body.lower_leg_model=None
						body.style='cyborg'
						cmsg(is_name+' نامرئی شد')
					else:
						cmsg('')
	
			elif m in [ px+'sp' ]:
				if n==[]:
					try:
						is_name=session_players[int(0)].getname()
						if not activity_players[int(0)].actor.node.hockey==True:
							activity_players[int(0)].actor.node.hockey=True
							cmsg('سرعت برای '+is_name+' فعال شد')
						else:
							activity_players[int(0)].actor.node.hockey=False
							cmsg('سرعت '+is_name+' غیرفعال شد')
					except:
						cmsg('بازیکن یافت نشد')
				elif n[0]=='a':
					for i in activity_players:
						if not i.actor.node.hockey==True:
							i.actor.node.hockey=True
							cmsg('سرعت برای همه فعال شد')
						else:
							i.actor.node.hockey=False
							cmsg('سرعت برای همه غیرفعال شد')
				else:
					try:
						is_name=session_players[int(n[0])].getname()
						if not activity_players[int(n[0])].actor.node.hockey==True:
							activity_players[int(n[0])].actor.node.hockey=True
							cmsg('سرعت برای '+is_name+' فعال شد')
						else:
							activity_players[int(n[0])].actor.node.hockey=False
							cmsg('')
					except:
						cmsg('بازیکن یافت نشد')
	
			elif m in [ px+'hed' ]:
				if n==[]:
					try:
						body=activity_players[int(0)].actor.node
						body.head_model=None
						cmsg('سر بازیکن ناپدید شد')
					except:
						cmsg('بازیکن یافت نشد')
				elif n[0]=='a':
					for i in activity_players:
						body=i.actor.node
						body.head_model=None
				else:
					try:
						body=activity_players[int(n[0])].actor.node
						body.head_model=None
						cmsg('سر بازیکن ناپدید شد')
					except:
						cmsg('بازیکن یافت نشد')
	
			elif m in [ px+'d' , px+'D' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.node.handlemessage(ba.DieMessage())
					cmsg(is_name+' نابود شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.node.handlemessage(ba.DieMessage())
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.node.handlemessage(ba.DieMessage())
					cmsg(is_name+' نابود شد')

			elif m in [ px+'h' , px+'H' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.node.handlemessage(ba.PowerupMessage(poweruptype='health'))
					cmsg('سلامت '+is_name+' بازیابی شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.node.handlemessage(ba.PowerupMessage(poweruptype='health'))
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.node.handlemessage(ba.PowerupMessage(poweruptype='health'))
					cmsg('سلامت '+is_name+' بازیابی شد')
	
			elif m in [ px+'cu' , px+'Cu' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.node.handlemessage(ba.PowerupMessage(poweruptype='curse'))
					cmsg(is_name+' نفرین شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.node.handlemessage(ba.PowerupMessage(poweruptype='curse'))
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.node.handlemessage(ba.PowerupMessage(poweruptype='curse'))
					cmsg(is_name+' نفرین شد')
	
			elif m in [ px+'sl' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.node.handlemessage('knockout', 8000)
					cmsg(is_name+' بی هوش شد :)')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.node.handlemessage('knockout', 8000)
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.node.handlemessage('knockout', 8000)
					cmsg(is_name+' بی هوش شد :)')
	
			elif m in [ px+'superpunch' ]:
				if n == []:
					try:
						if not activity_players[int(0)].actor._punch_power_scale==15:
							is_name=session_players[int(0)].getname()
							activity_players[int(0)].actor._punch_power_scale=15
							activity_players[int(0)].actor._punch_cooldown=0
							cmsg('قدرت ضربه '+is_name+' افزایش یافت')
						else:
							activity_players[int(0)].actor._punch_power_scale=1.2
							activity_players[int(0)].actor._punch_cooldown=400
							cmsg('قدرت ضربه '+is_name+' کاهش یافت')
					except:
						pass
				elif n[0]=='a':
					for i in activity_players:
						if not i.actor._punch_power_scale==15:
							i.actor._punch_power_scale=15
							i.actor._punch_cooldown=0
							cmsg('قدرت ضربه همه افزایش یافت')
						else:
							i.actor._punch_power_scale=1.2
							i.actor._punch_cooldown=400
							cmsg('قدرت ضربه همه کاهش یافت')
				else:
					try:
						if not activity_players[int(n[0])].actor._punch_power_scale==15:
							is_name=session_players[int(n[0])].getname()
							activity_players[int(n[0])].actor._punch_power_scale=15
							activity_players[int(n[0])].actor._punch_cooldown=0
							cmsg('قدرت ضربه '+is_name+' افزایش یافت')
						else:
							activity_players[int(n[0])].actor._punch_power_scale=1.2
							activity_players[int(n[0])].actor._punch_cooldown=400
							cmsg('قدرت ضربه '+is_name+' کاهش یافت')
					except:
						pass

			elif m in [ px+'tn', px+'tnt' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.bomb_type='tnt'
					cmsg('ناری برای '+is_name+' فعال شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.bomb_type='tnt'
						cmsg('ناری برای همه فعال شد')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.bomb_type='tnt'
					cmsg('ناری برای '+is_name+' فعال شد')
	
			elif m in [ px+'bt' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.bomb_type='impact'
					cmsg('بمب ضربه‌ای برای '+is_name+' فعال شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.bomb_type='impact'
						cmsg('بمب ضربه‌ای برای همه فعال شد')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.bomb_type='impact'
					cmsg('بمب ضربه‌ای برای '+is_name+' فعال شد')
	
			elif m in [ px+'bs' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.bomb_type='sticky'
					cmsg('چسبونکی برای '+is_name+' فعال شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.bomb_type='sticky'
						cmsg('چسبونکی برای همه فعال شد')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.bomb_type='sticky'
					cmsg('چسبونکی برای '+is_name+' فعال شد')
	
			elif m in [ px+'bi' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.bomb_type='ice'
					cmsg('یخی برای '+is_name+' فعال شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.bomb_type='ice'
						cmsg('یخی برای همه فعال شد')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.bomb_type='ice'
					cmsg('یخی برای '+is_name+' فعال شد')
	
			elif m in [ px+'bm' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.bomb_type='land_mine'
					cmsg('مین برای '+is_name+' فعال شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.bomb_type='land_mine'
						cmsg('مین برای همه فعال شد')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.bomb_type='land_mine'
					cmsg('مین برای '+is_name+' فعال شد')
	
			elif m in [ px+'pun' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.node.handlemessage(ba.PowerupMessage(poweruptype='punch'))
					cmsg('مشت برای '+is_name+' فعال شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.node.handlemessage(ba.PowerupMessage(poweruptype='punch'))
						cmsg('مشت برای همه فعال شد')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.node.handlemessage(ba.PowerupMessage(poweruptype='punch'))
					cmsg('مشت برای '+is_name+' فعال شد')
	
	
			elif m in [ px+'sh' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.node.handlemessage(ba.PowerupMessage(poweruptype='shield'))
					cmsg('سپر برای '+is_name+' فعال شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.node.handlemessage(ba.PowerupMessage(poweruptype='shield'))
						cmsg('سپر برای همه فعال شد :)')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.node.handlemessage(ba.PowerupMessage(poweruptype='shield'))
					cmsg('سپر برای '+is_name+' فعال شد')
	
			elif m in [ px+'fr' ]:
				if n == []:
					is_name=session_players[int()].getname()
					activity_players[int(0)].actor.node.handlemessage(ba.FreezeMessage())
					cmsg(is_name+' منجمد شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.node.handlemessage(ba.FreezeMessage())
						cmsg('همه منجمد شدند')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.node.handlemessage(ba.FreezeMessage())
					cmsg(is_name+' منجمد شد')
	
			elif m in [ px+'u' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.node.handlemessage(ba.ThawMessage())
					cmsg('یخ '+is_name+' باز شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.node.handlemessage(ba.ThawMessage())
						cmsg('یخ همه باز شد')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.node.handlemessage(ba.ThawMessage())
					cmsg('یخ '+is_name+' باز شد')
	
			elif m in [ px+'fall' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.node.handlemessage(ba.StandMessage())
					cmsg(is_name+' به مرکز منتقل شد')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.node.handlemessage(ba.StandMessage())
						cmsg('همه به مرکز منتقل شدند')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.node.handlemessage(ba.StandMessage())
					cmsg(is_name+' به مرکز منتقل شد')
	
			elif m in [ px+'cel' ]:
				if n == []:
					is_name=session_players[int(0)].getname()
					activity_players[int(0)].actor.node.handlemessage(ba.CelebrateMessage())
					cmsg(is_name+' جشن گرفت')
				elif n[0]=='a':
					for i in activity_players:
						i.actor.node.handlemessage(ba.CelebrateMessage())
						cmsg('همه جشن گرفتند')
				else:
					is_name=session_players[int(n[0])].getname()
					activity_players[int(n[0])].actor.node.handlemessage(ba.CelebrateMessage())
					cmsg(is_name+' جشن گرفت')
	
			elif m in [ px+'fl' ]:
				if n==[]:
					try:
						is_name=session_players[int(0)].getname()
						if not activity_players[int(0)].actor.node.fly==True:
							activity_players[int(0)].actor.node.fly=True
							cmsg(is_name+' به حالت پرواز درآمد')
						else:
							activity_players[int(0)].actor.node.fly=False
							cmsg(is_name+' از حالت پرواز خارج شد')
					except:
						cmsg('بازیکن یافت نشد')
						pass
				elif n[0]=='a':
					for i in activity_players:
						if not i.actor.node.fly==True:
							i.actor.node.fly=True
							cmsg('پرواز همه = فعال')
						else:
							i.actor.node.fly=False
							cmsg('پرواز همه = غیرفعال')
				else:
					try:
						is_name=session_players[int(n[0])].getname()
						if not activity_players[int(n[0])].actor.node.fly==True:
							activity_players[int(n[0])].actor.node.fly=True
							cmsg(is_name+' به حالت پرواز درآمد')
						else:
							activity_players[int(n[0])].actor.node.fly=False
							cmsg(is_name+' از حالت پرواز خارج شد')
					except:
						cmsg('بازیکن یافت نشد')
						pass
	
			elif m in [ px+'g' ]:
				if n==[]:
					try:
						is_name=session_players[int(0)].getname()
						if not activity_players[int(0)].actor.node.invincible==True:
							activity_players[int(0)].actor.node.invincible=True
							activity_players[int(0)].actor._punch_power_scale=7
							cmsg('جاودانگی برای '+is_name+' فعال شد')
						else:
							activity_players[int(0)].actor.node.invincible=False
							activity_players[int(0)].actor._punch_power_scale=1.2
							cmsg('جاودانگی '+is_name+' غیرفعال شد')
					except:
						cmsg('بازیکن یافت نشد')
				elif n[0]=='a':
					for i in activity_players:
						if not i.actor.node.invincible==True:
							i.actor.node.invincible=True
							i.actor._punch_power_scale=7
							cmsg('جاودانگی برای همه فعال شد')
						else:
							i.actor.node.invincible=False
							i.actor._punch_power_scale=1.2
							cmsg('جاودانگی همه غیرفعال شد')
				else:
					try:
						is_name=session_players[int(n[0])].getname()
						if not activity_players[int(n[0])].actor.node.invincible==True:
							activity_players[int(n[0])].actor.node.invincible=True
							activity_players[int(n[0])].actor._punch_power_scale=7
							cmsg('جاودانگی برای '+is_name+' فعال شد')
						else:
							activity_players[int(n[0])].actor.node.invincible=False
							activity_players[int(n[0])].actor._punch_power_scale=1.2
							cmsg('جاودانگی '+is_name+' غیرفعال شد')
					except:
						cmsg('بازیکن یافت نشد')
			elif m in [ px+'bomb', px+'default_bomb' ]:
				if n == []:
					cmsg('نوع بمب اشتباه است')
					cmsg("ice / impact / land_mine / normal / sticky / tnt")
				elif n[0]=='help':
					cmsg("bombtypes - ['ice', 'impact', 'land_mine', 'normal', 'sticky','tnt']")
				elif n[0] in [ 'ice' , 'impact',  'land_mine' , 'normal' , 'sticky' , 'tnt']:
					for i in activity_players:
						i.actor.bomb_type=n[0]
						cmsg(str(n[0]))
				else:
					cmsg('نوع بمب اشتباه است')
					cmsg('ice / impact / land_mine / normal / sticky / tnt')
	
			elif m in [ px+'tb' ]:
				if n == []:
					cmsg('لطفاً ظرفیت بمب را وارد کنید')
				else:
					try:
						for i in activity_players:
							i.actor.set_bomb_count(int(n[0]))
							cmsg('ظرفیت بمب روی '+str(n[0])+' تنظیم شد')
					except:
						cmsg('لطفاً از عدد استفاده کنید')



def bomb():
	cmsg("This Mod By @Horn_Ch")
	ba.timer(0, _cmds._process_cmd, True)

# ba_meta export babase.Plugin
class Horn_Ch(Plugin):
	bomb()
