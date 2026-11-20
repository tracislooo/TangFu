from pathlib import Path
import json
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','match-card-goal-assist-spacing-'),'backup-current','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases]
 for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']:
  d=Doc(W,name=name)
  for root,top,textname in [(1042,0,'GoalsText'),(1044,18,'AssistText')]:
   text=d.named(textname);row=d.a(text)['m_Parent']['rid'];icon=next(c['rid'] for c in d.a(row)['m_Children'] if c['rid']!=text)
   d.st(root,[(131105,d.px(32)),(131087,d.px(14)),(131104,d.px(top))])
   d.st(row,[(131083,d.enum('row')),(131073,d.enum('center')),(131088,d.enum('flex-end')),(131105,d.px(32)),(131087,d.px(14))])
   d.st(icon,[(131105,d.px(12)),(131087,d.px(12)),(131085,d.num(0))])
   d.st(text,[(131091,d.px(4)),(131105,d.px(16)),(131087,d.px(14)),(65537,d.px(9)),(65546,d.enum('middle-left')),(131085,d.num(0))])
  d.save()
 cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'icon_number_gap':4,'goal_row_top':0,'assist_row_top':18,'row_height':14,'shirt_number_top_unchanged':34,'native_bindings_unchanged':True})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
