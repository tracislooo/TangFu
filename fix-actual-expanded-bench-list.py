from pathlib import Path
import json,copy,ast
R=Path(__file__).parent
source=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8')
prefix=source.split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','actual-expanded-bench-list-fix-').replace("'NAMES=[W,G]'","'NAMES=[M,G]'").replace('bases=(W,G)','bases=(M,G)')
exec(compile(prefix,'backup-actual-player-list','exec'))
helper=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'native-clone','exec'))
clone_audits=[];audits=[];tx=[]
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 M,G=[x+suffix for x in bases]
 # The native showminres variable is already computed from the displayed list's count > 11.
 d=Doc(M,name='SquadOverview');old=copy.deepcopy(d.d)
 assert d.data(1070)['Binding']['m_direct']['Path']['m_path']=='showminres'
 assert [c['rid'] for c in d.a(1070)['m_Children']]==[1087,1088]
 compactguid='d8b28e612b34531ba0f09ff5a425e022'
 assert d.data(1088)['Binding']['m_direct']['Path']['m_path']=='match.Tactic.SquadOverviewPlayerInformation'
 d.data(1088)['RowTemplate']['m_AssetGUID']=compactguid
 d.data(1088).update(FixedElementSize=60.,FixedElementSizeControllerOrTouch=60.)
 parent=d.a(1073)['m_Parent']['rid'];index=next(i for i,c in enumerate(d.a(parent)['m_Children']) if c['rid']==1073)
 switch,mapping=clone_native(d,1070,parent)
 # clone only the native switch shell; discard copied lists to avoid unrelated duplicates.
 def erase(i):
  for c in list(d.a(i).get('m_Children',[])):erase(c['rid'])
  a=d.a(i);p=a['m_Parent']['rid'];sr=a.get('m_SerializedData',{}).get('rid');d.a(p)['m_Children'].remove({'rid':i});ids={i,sr};d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in ids]
  for j in ids:d.r.pop(j,None)
 for c in list(d.a(switch)['m_Children']):erase(c['rid'])
 d.data(switch)['name']='NativeManyPlayersSmallBreakpointSwitch'
 d.move(1073,switch);compact,mapping=clone_native(d,1073,switch);d.data(compact)['RowTemplate']['m_AssetGUID']=compactguid;d.data(compact).update(FixedElementSize=60.,FixedElementSizeControllerOrTouch=60.)
 d.move(switch,parent,index);d.st(switch,[(131084,d.num(1)),(131097,d.px(0)),(131087,d.pct(100))])
 assert d.data(1087)==sd(refs(old),1087)
 assert d.data(1073)==sd(refs(old),1073)
 d.save()
 donor=Doc(G,name='MatchManySubstitutesRegularCard')
 for name in ['MatchManySubstitutesSmallCard','MatchManySubstitutesRegularCard']:
  d=Doc(G,name=name);beforetree=copy.deepcopy(d.d);d.st(1050,[(131081,d.enum('none'))])
  if name.endswith('SmallCard'):icon,mapping=clone_native(donor,donor.named('BodyLanguageMorphIcon'),1032)
  else:icon=d.named('BodyLanguageMorphIcon')
  d.move(icon,1032,2);d.st(icon,[(131091,d.px(8)),(131105,d.px(18)),(131087,d.px(18)),(131097,d.px(18)),(131096,d.px(18)),(131084,d.num(0)),(131085,d.num(0)),(131074,d.enum('center'))]);d.st(1032,[(131088,d.enum('flex-start'))])
  d.st(1006,[(131102,d.enum('relative')),(131104,d.px(40))])
  for i,r in refs(beforetree).items():
   if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,('Existing card binding/event changed',i)
  d.save()
 audits.append({'variant':tag,'actual_list':'match.Tactic.SquadOverviewPlayerInformation','native_threshold':'showminres: displayed list > 11','normal_list_1087_unchanged':True,'small_normal_list_1073_unchanged':True,'many_list_1088_compact_guid':compactguid,'small_breakpoint_uses_same_native_count_switch':True,'only_compact_cards_rating_removed':True,'native_state_icon_reused':True,'content_offset_40':True})
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
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'normal_card_templates_unchanged':True,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('修正实际入口：截图为原生showingsubs开关打开后，底部主列表match.Tactic.SquadOverviewPlayerInformation显示替补。旧修改只接独立sublist，未覆盖该入口。现在用原生showminres（原生BindingSetterComponent中已将该显示列表人数与11比较）在大屏1088和小屏新增同原生开关的true分支引用已登记的紧凑小卡片，60px步长；<=11原始1087/1073列表及gameworld卡片不变。紧凑卡片实际内容下移40界面单位、隐藏评分、原生状态图标放到原评分位置；小卡片直接复用常规紧凑卡片原生状态及提示子树。未改公共API、纹理、侧栏、其他包内对象。备份和哈希保护restore.ps1在本目录。实际显示待用户验证。','utf8')
print(str(OUT))
