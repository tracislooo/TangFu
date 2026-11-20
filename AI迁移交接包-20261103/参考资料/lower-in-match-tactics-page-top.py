from pathlib import Path
import json,copy
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','in-match-tactics-top-clearance-').replace('NAMES=[W,G,M,F]','NAMES=[M]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]','if False:assert before[SKIN/n]==before[GAME/n]').replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']",'')
exec(compile(boot,'backup-current-tactics-entry','exec'))
MS=M+'::skin';env[MS]=UnityPy.load(before[SKIN/M]);objs[MS]={o.path_id:o for o in env[MS].objects};hashes[MS]={i:sha(o.get_raw_data()) for i,o in objs[MS].items()};changes[MS]={};audits=[]
for bn in [M,MS]:
 page=Doc(bn,name='MatchTacticsRoot');old=copy.deepcopy(page.d)
 assert page.a(1002)['m_TemplateAlias']=='RevampTacticalPlanner'
 # Padding reduces the content box inside the existing allocated height.
 page.st(1001,[(131101,page.px(48)),(131096,page.px(0))])
 page.st(1002,[(131096,page.px(0)),(131084,page.num(1)),(131085,page.num(1))])
 assert page.data(1001)==sd(refs(old),1001) and page.data(1002)==sd(refs(old),1002)
 page.save()
 header=Doc(bn,name='OverviewHeader');old=copy.deepcopy(header.d)
 tabs=header.named('TacticsOpened')
 assert header.a(1081)['m_Parent']['rid']==tabs
 header.st(tabs,[(131102,header.enum('relative')),(131104,header.px(48))])
 assert header.data(1081)==sd(refs(old),1081)
 for i,r in refs(old).items():
  if 'm_Parent' not in r.get('data',{}):assert header.r[i]==r
 header.save();audits.append({'bundle':bn,'tactics_page_top_padding':48,'tabs_relative_top':48,'bottom_and_outer_page_allocation_unchanged':True,'original_bindings_and_events_unchanged':True})
tail=(R/'repair-highlight-six-page-buttons.py').read_text('utf8').split('outputs={}')[1]
tail=tail.replace('for bn in NAMES:', 'for bn in list(env):',1).replace('dest=OUT/bn;',"dest=OUT/('output-skin.bundle' if bn==MS else bn);")
tail=tail.replace('str(outputs[bn])',"str(outputs[MS if tag=='skin' else bn])").replace('sha(outputs[bn].read_bytes())',"sha(outputs[MS if tag=='skin' else bn].read_bytes())")
tail=tail.replace("'root_cause_found':'All 12 SIButton controls were created with pickingMode Ignore (1).'","'requested_change':'Lower only in-match tactics page and its open-state header tabs by 48 UI units, keeping the bottom fixed.'").replace("'clickable_buttons':12","'top_clearance_ui_units':48")
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('仅比赛内战术页：MatchTacticsRoot内容区顶部预留48界面单位，外层分配高度和底边不变；OverviewHeader中TacticsOpened标签行相对下移48，保留战术/定位球/点球/针对性指令的绑定和事件。不更改赛前战术、正常比赛画面、记分牌和底部战术按钮。游戏与皮肤按各自当前包独立修改；回读和未改对象字节检查通过。实际页面位置和底边、滚动需游戏内核对。','utf8')"+tail[end:]
exec(compile('outputs={}'+tail,'check-package-independent-files','exec'))
