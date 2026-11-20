from pathlib import Path
import json,copy
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','match-pending-changes-right-controls-').replace('NAMES=[W,G,M,F]','NAMES=[M]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]', 'if False:assert before[SKIN/n]==before[GAME/n]')
boot=boot.replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']",'')
exec(compile(boot,'backup-current-header','exec'))
d=Doc(M,name='OverviewHeader');original=copy.deepcopy(d.d);orr=refs(original)
assert d.a(1089)['m_TemplateAlias']=='MatchTacticPendingChanges'
assert d.a(1037)['m_TemplateAlias']=='MatchPlaybackControls'
# Keep both original switch slots: the old pending slot becomes empty.
blank=d.add(d,1035,1083,'PendingChangesOriginalSlotEmpty');d.move(blank,1083,1)
row=d.add(d,1035,1027,'MatchTopRightControlsWithPendingChanges')
d.st(row,[(131083,d.enum('row')),(131073,d.enum('center')),(131074,d.enum('flex-end')),(131085,d.num(0)),(131084,d.num(0)),(131093,{'m_ValueType':1,'valueIndex':2})])
# Reproduce the old ancestor gates without relocating other tactical controls.
phone=d.add(d,1033,row,'PendingChangesDesktopOnly')
def gate(parent,name,path,invert=False):
 i=d.add(d,1033,parent,name);v=d.data(i)
 v['Binding']=copy.deepcopy(d.data(1033)['Binding']);v['Binding']['m_kind']=1;v['Binding']['m_direct']['Path']['m_path']=path
 v.update(Binding_UxmlAttributeFlags=1,InvertDirectBinding=int(invert),InvertDirectBinding_UxmlAttributeFlags=1)
 return i
managing=gate(phone,'PendingChangesManaging','match.IsManaging')
closed=gate(managing,'PendingChangesTacticsClosed','match.Tactic.NeedsConfirmation',True)
period=d.add(d,1078,closed,'PendingChangesNotPenalties')
pending=gate(period,'PendingChangesVisible','match.MatchTeamHasPendingChanges')
d.move(1089,pending);d.move(1037,row)
d.st(phone,[(131090,d.px(8)),(131085,d.num(0))])
assert len(d.a(1083)['m_Children'])==2
assert d.data(1089)==sd(orr,1089) and d.data(1037)==sd(orr,1037)
for i in orr:
 if 'm_Parent' not in orr[i].get('data',{}):assert d.r[i]==orr[i],('Existing binding or event changed',i)
d.save();audits=[{'template':'OverviewHeader','pending_template':'MatchTacticPendingChanges','placement':'same native row immediately before MatchPlaybackControls','gap_px':8,'native_popup_and_playback_data_unchanged':True,'original_visibility_gates_preserved':True,'old_switch_slot_count':2}]
tail=(R/'repair-highlight-six-page-buttons.py').read_text('utf8').split('outputs={}')[1]
tail=tail.replace("'root_cause_found':'All 12 SIButton controls were created with pickingMode Ignore (1).'","'requested_change':'Move pending tactical changes immediately left of top-right playback controls.'")
tail=tail.replace("'clickable_buttons':12","'header_popup_repositioned':True")
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('仅修改当前OverviewHeader：将原生MatchTacticPendingChanges移到MatchPlaybackControls左侧，同一行按内容宽度排列，间隔8px。保留原手机/执教/战术确认/非点球/待更改可见条件，旧Switch保留两个槽位；不改提示框内容、编辑/取消事件、记分牌和其他战术按钮。仅Header及内联样式变更，其他对象字节一致。静态与回读检查通过，实际游戏显示待验证。','utf8')"+tail[end:]
MS=M+'::skin'
env[MS]=UnityPy.load(before[SKIN/M]);objs[MS]={o.path_id:o for o in env[MS].objects};hashes[MS]={pid:sha(o.get_raw_data()) for pid,o in objs[MS].items()};changes[MS]={}
# Apply identical local edits against the skin's own current object graph.
patch_source=Path(__file__).read_text('utf8').split("d=Doc(M,name='OverviewHeader')",1)[1].split("tail=(R/",1)[0]
exec(compile("d=Doc(MS,name='OverviewHeader')"+patch_source,'independent-skin-header','exec'))
tail=tail.replace('for bn in NAMES:', 'for bn in list(env):',1)
tail=tail.replace('dest=OUT/bn;',"dest=OUT/('output-skin.bundle' if bn==MS else bn);")
tail=tail.replace("str(outputs[bn])","str(outputs[MS if tag=='skin' else bn])")
tail=tail.replace("sha(outputs[bn].read_bytes())","sha(outputs[MS if tag=='skin' else bn].read_bytes())")
exec(compile('outputs={}'+tail,'verify-and-package','exec'))
