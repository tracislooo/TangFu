from pathlib import Path
import json,copy,ast
R=Path(__file__).parent
source=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8')
prefix=source.split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-in-possession-native-vertical-').replace("'NAMES=[W,G]'","'NAMES=[G]'").replace('bases=(W,G)','bases=(G,)')
exec(compile(prefix,'backup-current-formation-only','exec'))
helper=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'copy-pitch-with-original-bindings','exec'))
clone_audits=[];audits=[];tx=[]
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 bn=bases[0]+suffix;native=Doc(bn,name='TeamFormationAdaptiveBlock')
 for name in ['HighlightHomeHorizontalFormation','HighlightAwayHorizontalFormation']:
  d=Doc(bn,name=name);old=copy.deepcopy(d.d);panel_checks=[]
  for i in [1064,1065]:
   parent=d.a(i)['m_Parent']['rid'];idx=next(j for j,c in enumerate(d.a(parent)['m_Children']) if c['rid']==i)
   switch=d.add(d,1045,parent,'InPossessionVerticalPitch_'+str(i));s=d.data(switch);s['Binding']['m_kind']=1;s['Binding']['m_direct']['Path']['m_path']='inpossession';s['Binding_UxmlAttributeFlags']=1
   d.move(i,switch);vertical,mapping=clone_native(d,i,switch)
   d.data(vertical).update(Orientation=0,Orientation_UxmlAttributeFlags=1,FlipPositions=0,FlipPositions_UxmlAttributeFlags=1)
   for key in ['FillAllAvailableSpace','UseParentRectForOutline']:
    if key in native.data(i):d.data(vertical)[key]=native.data(i)[key];d.data(vertical)[key+'_UxmlAttributeFlags']=1
   d.move(switch,parent,idx);d.fill(switch)
   assert [c['rid'] for c in d.a(switch)['m_Children']]==[i,vertical]
   assert d.data(i)==sd(refs(old),i)
   assert d.data(vertical)['Orientation']==0 and d.data(vertical)['FlipPositions']==0
   panel_checks.append({'original_horizontal_node_for_oop':i,'vertical_node_for_ip':vertical,'orientation':0,'flip':0})
  for i,r in refs(old).items():
   if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,('Existing bindings/events changed',i)
  d.save();audits.append({'variant':tag,'template':name,'panels':panel_checks,'in_possession':'native vertical: forwards top, goalkeeper bottom','out_of_possession':'existing horizontal unchanged','lower_oop_templates_unchanged':True})
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,(bn,pid)
  for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t,(bn,pid)
  for ob in saved.values():
   if ob.path_id in changes[bn] and ob.type.name=='MonoBehaviour':
    t=ob.read_typetree()
    if 'inlineSheet' in t:validate_ui(t,saved[t['inlineSheet']['m_PathID']].read_typetree())
  src=OUT/('skin-'+base if suffix else base);src.write_bytes(raw);target=folder/base;assert target.read_bytes()==before[target]
  tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'no_new_assets_or_catalog_changes':True,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('仅修改Highlight左右顶部两个私有阵型模板，在两个直播/历史FMTacticsPanel分支外各加入原生inpossession布尔开关。有球true分支复制现有球场，恢复原生Orientation=0/FlipPositions=0及原生填充控制，前锋在上、门将在下；无球false分支保留原有水平球场与完整绑定不变。头像、姓名、评分、选择器、下方无球模板和其他模块保持原样。不新增资源GUID或公共API；仅当前游戏与皮肤的global包增量修改。静态回读及无关对象一致性通过，实际显示待确认。','utf8')
print(str(OUT))
