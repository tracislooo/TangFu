from pathlib import Path
import copy,json
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','match-hotseat-stats-top-right-'),'backup-current','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases]
 d=Doc(M,name='OverviewHeader');old=copy.deepcopy(d.d);row=d.named('MatchTopRightControlsWithPendingChanges')
 # Preserve the hotseat button's complete original gate chain.
 desktop=d.add(d,1033,row,'RightHotseatDesktopOnly')
 def gate(parent,path,invert,name):
  i=d.add(d,1033,parent,name);s=d.data(i)
  s['Binding']=copy.deepcopy(d.data(1033)['Binding']);s['Binding']['m_direct']['Path']['m_path']=path
  s.update(Binding_UxmlAttributeFlags=1,InvertDirectBinding=int(invert),InvertDirectBinding_UxmlAttributeFlags=1)
  return i
 managing=gate(desktop,'match.IsManaging',False,'RightHotseatManaging')
 closed=gate(managing,'match.Tactic.NeedsConfirmation',True,'RightHotseatTacticsClosed')
 d.move(1079,closed)
 # BindingSetter and its stats-state variable move together with the button.
 d.move(1036,row)
 d.move(desktop,row,1)
 d.move(1036,row,next(i for i,c in enumerate(d.a(row)['m_Children']) if c['rid']==1037))
 for i in [desktop,managing,closed,1036]:d.st(i,[(131083,d.enum('row')),(131073,d.enum('center')),(131085,d.num(0)),(131084,d.num(0))])
 d.st(desktop,[(131092,d.px(8))]);d.st(1036,[(131091,d.px(8))])
 # The original native controls keep every serialized binding and event.
 previous=refs(old)
 for i,r in previous.items():
  if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,(tag,i)
 assert d.a(1037)['m_Parent']['rid']==row
 assert d.a(row)['m_Children'][-1]['rid']==1037
 d.save();cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'right_row_order':'tactical toolbar, hotseat toggle, pending changes, stats button, playback controls','native_events_bindings_unchanged':True,'original_visibility_gates_preserved':True})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'修改说明.md').write_text('仅调整OverviewHeader与其内联样式。右侧顺序为战术栏、热座主客队切换、待执行战术提示、查看统计、设置播放控件。统计按钮连同其stats-state变量一起移动；热座保留原桌面/执教/战术关闭及原生热座判断。未改记分牌、其他页面或公共模板。静态回读及未指定对象检查通过，游戏内位置和点击未验证。','utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
