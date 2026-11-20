from pathlib import Path
import json,copy
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','replay-leave-button-before-tactics-'),'backup-current','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];d=Doc(M,name='OverviewHeader');old=copy.deepcopy(d.d);oldr=refs(old)
 button=1054;oldparent=d.a(button)['m_Parent']['rid'];assert oldparent==1042 and d.a(button)['m_TemplateAlias']=='button-primary-label'
 row=d.named('MatchTopRightControlsWithPendingChanges');desktop=d.add(d,1033,row,'ReplayLeaveDesktopOnly')
 visible=d.add(d,1033,desktop,'ReplayLeaveNotManaging');s=d.data(visible);s['Binding']=copy.deepcopy(d.data(1033)['Binding']);s['Binding']['m_direct']['Path']['m_path']='match.IsManaging';s.update(Binding_UxmlAttributeFlags=1,InvertDirectBinding=1,InvertDirectBinding_UxmlAttributeFlags=1)
 d.move(button,visible);blank=d.add(d,1035,oldparent,'OriginalLeaveButtonSlotEmpty');d.move(blank,oldparent,0)
 d.move(desktop,row,0)
 for i in [desktop,visible]:d.st(i,[(131083,d.enum('row')),(131073,d.enum('center')),(131084,d.num(0)),(131085,d.num(0))])
 d.st(desktop,[(131092,d.px(8))])
 assert len(d.a(oldparent)['m_Children'])==2
 assert d.a(row)['m_Children'][0]['rid']==desktop
 for i,r in oldr.items():
  if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,('Original binding/event changed',i)
 d.save();cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'actual_control':'Leave Match / replay exit (OverviewHeader 1054)','right_row_order':'leave replay, tactics toolbar, other existing controls','desktop_and_not_managing_gates_preserved':True,'native_click_event_unchanged':True,'scoreboard_unchanged':True})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
tail=tail.replace('for p,b in before.items():assert p.read_bytes()==b',"for p,b in before.items():assert p.read_bytes()==b,('Concurrent target change',str(p))")
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
