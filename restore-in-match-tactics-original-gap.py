from pathlib import Path
import json,copy
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','in-match-tactics-original-gap-').replace('NAMES=[W,G,M,F]','NAMES=[M]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]','if False:assert before[SKIN/n]==before[GAME/n]').replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']",'')
exec(compile(boot,'backup-current-gap-adjustment','exec'))
MS=M+'::skin';env[MS]=UnityPy.load(before[SKIN/M]);objs[MS]={o.path_id:o for o in env[MS].objects};hashes[MS]={i:sha(o.get_raw_data()) for i,o in objs[MS].items()};changes[MS]={};audits=[]
for tag,bn in [('game',M),('skin',MS)]:
 path=R/'in-match-tactics-top-clearance-20261030-064259'/('backup-'+tag)/M
 src=UnityPy.load(str(path));os={o.path_id:o for o in src.objects}
 for name,nodes in [('MatchTacticsRoot',[1001,1002]),('OverviewHeader',[1073])]:
  source=next(o.read_typetree() for o in src.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name);sr=refs(source);ss=os[source['inlineSheet']['m_PathID']].read_typetree()
  doc=Doc(bn,name=name);original=copy.deepcopy(doc.d)
  for node in nodes:
   idx=sr[node]['data']['m_RuleIndex'];doc.a(node)['m_RuleIndex']=-1
   if idx>=0:
    rule=copy.deepcopy(ss['m_Rules'][idx]);rule['m_ComplexSelectors']=[]
    for prop in rule['m_Properties']:
     for handle in prop['m_Values']:
      typ=handle['m_ValueType']
      if typ in poolmap:handle.update(doc.val(typ,copy.deepcopy(ss[poolmap[typ]][handle['valueIndex']])))
    doc.s['m_Rules'].append(rule);doc.a(node)['m_RuleIndex']=len(doc.s['m_Rules'])-1
  for i,r in refs(original).items():
   expected=copy.deepcopy(r)
   if i in nodes:expected['data']['m_RuleIndex']=doc.a(i)['m_RuleIndex']
   assert doc.r[i]==expected,('Unexpected change',name,i)
  doc.save();audits.append({'variant':tag,'template':name,'restored_style_nodes':nodes,'all_other_nodes_and_bindings_unchanged':True})
tail=(R/'repair-highlight-six-page-buttons.py').read_text('utf8').split('outputs={}')[1]
tail=tail.replace('for bn in NAMES:', 'for bn in list(env):',1).replace('dest=OUT/bn;',"dest=OUT/('output-skin.bundle' if bn==MS else bn);")
tail=tail.replace('str(outputs[bn])',"str(outputs[MS if tag=='skin' else bn])").replace('sha(outputs[bn].read_bytes())',"sha(outputs[MS if tag=='skin' else bn].read_bytes())")
tail=tail.replace("'root_cause_found':'All 12 SIButton controls were created with pickingMode Ignore (1).'","'requested_change':'Restore original tactics-page spacing by undoing only the previous 48-unit page and tab offsets.'").replace("'clickable_buttons':12","'original_tactics_spacing_restored':True")
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('仅按同一实际安装目录48单位调整前的备份，恢复MatchTacticsRoot节点1001/1002及OverviewHeader节点1073的原始样式。逐项核对其他节点、绑定及事件未变；保留最新右上战术按钮栏、待更改提示和其他所有修改，不覆盖旧整包。游戏与皮肤分别处理。文件回读通过，实际间距待游戏内验收。','utf8')"+tail[end:]
exec(compile('outputs={}'+tail,'check-and-package-gap-only','exec'))
