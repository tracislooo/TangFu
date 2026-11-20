from pathlib import Path
import json,copy,struct
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','advice-label-card-flag-offset-'),'backup-current','exec'))
def color(r,g,b):return {k:struct.unpack('<f',struct.pack('<f',v))[0] for k,v in zip(['r','g','b','a'],[r/255,g/255,b/255,1.])}
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases]
 d=Doc(W,name='OppositionInstructionsBlock');button=d.named('ApplyAdviceButton');overlay=d.named('LakeBlueActionGradient')
 d.st(overlay,[(131081,d.enum('none'))])
 d.st(button,[(458752,d.val(4,color(12,167,211))),(65536,d.val(4,color(255,255,255)))])
 d.save()
 for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']:
  d=Doc(W,name=name);flag=d.named('MatchCardNationalityFlag');number=d.named('MatchCardShirtNumber')
  # Native visual-function arguments contain full length-prefixed binding paths.
  fn=d.data(flag)['Binding']['m_visualFunction'];args=unpack(fn['m_inputs']['m_variable']['m_argumentBytes'])
  count=0
  for idx,arg in enumerate(args):
   if b'Nation.' not in arg:continue
   offset=arg.index(b'Nation.');size=arg[offset-1];old=arg[offset:offset+size].decode('utf8')
   assert old.startswith('Nation.')
   new='person.'+old;args[idx]=arg[:offset-1]+bytes([len(new)])+new.encode()+arg[offset+size:];count+=1
  assert count==4,count
  fn['m_inputs']['m_variable']['m_argumentBytes']=pack(args)
  d.st(flag,[(131104,d.px(34))])
  d.st(number,[(131104,d.px(34)),(262147,[d.px(3),d.px(0),d.px(0),d.px(3)])])
  d.save()
 cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'advice_gradient_overlay_hidden':True,'button_text_color':'white','flag_full_paths_corrected':True,'flag_and_number_down_px':6,'number_left_corner_radius':3,'right_corner_radius':0})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
