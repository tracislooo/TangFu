from pathlib import Path
import json,copy,ast
R=Path(__file__).parent
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','small-substitutes-state-and-last-five-')
exec(compile(prefix,'backup-small-sub-form','exec'))
helper=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'clone-native-state-form','exec'))
clone_audits=[];audits=[];tx=[];AUTO={'m_ValueType':1,'valueIndex':2};NONE={'m_ValueType':1,'valueIndex':3}
def ptrs(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():ptrs(x,out)
 elif isinstance(v,list):
  for x in v:ptrs(x,out)
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 W,G=[n+suffix for n in bases];d=Doc(G,name='SmallSubstituteCardLowerNoRating');regular=Doc(W,name='SquadOverviewPlayerBlock');chart=Doc(G,name='PlayerLastFiveMatchesChartFormSmallBarsCell');original=copy.deepcopy(d.d)
 gate=d.named('OnlySmallSubstitutePresentation');body=d.a(gate)['m_Children'][1]['rid']
 def walk(i):
  yield i
  for c in d.a(i).get('m_Children',[]):yield from walk(c['rid'])
 descendants=list(walk(body))
 def local(name):return next(i for i in descendants if 'm_SerializedData' in d.a(i) and d.data(i).get('name')==name)
 title=local('title area frame');d.st(title,[(131081,d.enum('none'))])
 rating=next(i for i in descendants if d.a(i).get('m_FullTypeName')=='SI.Bindable.SIStyleSetter' and d.data(i).get('name')=='Background');status=d.a(rating)['m_Parent']['rid'];footer=d.a(status)['m_Parent']['rid']
 mood,mapping=clone_native(regular,regular.named('BodyLanguageMorphIcon'),status);d.move(mood,status,1)
 d.st(status,[(131083,d.enum('row')),(131088,d.enum('flex-start')),(131073,d.enum('center')),(131105,d.pct(100)),(131087,d.px(32)),(131096,d.px(32)),(131084,d.num(0)),(131085,d.num(0))])
 d.st(mood,[(131102,d.enum('relative')),(131089,AUTO),(131104,AUTO),(131105,d.px(16)),(131087,d.px(16)),(131097,d.px(16)),(131096,d.px(16)),(131084,d.num(0)),(131085,d.num(0)),(131091,d.px(6))])
 d.st(footer,[(131083,d.enum('column')),(131087,AUTO),(131096,d.px(0)),(131094,NONE),(131084,d.num(0)),(131085,d.num(0))])
 remap_source=next(i for i,a in d.r.items() if a.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingRemapper')
 remap=d.add(d,remap_source,footer,'SmallSubstituteLastFiveMatchesContext');d.data(remap).update(Mappings=[{'m_serialisedType':0,'from':'matchratinglist','to':{'m_path':'playerinfo.Person.LastFiveMatchesForm.LastFiveMatchesList'},'type':{'id':0}},{'m_serialisedType':0,'from':'player','to':{'m_path':'playerinfo.Person'},'type':{'id':1145176065}}],Mappings_UxmlAttributeFlags=1)
 d.st(remap,[(131105,d.pct(100)),(131087,d.px(22)),(131096,d.px(22)),(131097,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131093,d.px(3)),(131073,d.enum('center')),(131088,d.enum('center'))])
 graph,mapping=clone_native(chart,1002,remap)
 d.st(graph,[(131105,d.pct(100)),(131087,d.px(22)),(131096,d.px(0)),(131097,d.px(0)),(131094,NONE),(131095,NONE),(131084,d.num(0)),(131085,d.num(0))])
 # Only the substitute branch gained content; the original small starting-player subtree is intact.
 original_refs=refs(original)
 def oldwalk(i):
  yield i
  for c in original_refs[i]['data'].get('m_Children',[]):yield from oldwalk(c['rid'])
 for i in oldwalk(1006):
  assert d.r[i]==original_refs[i]
  sid=original_refs[i]['data'].get('m_SerializedData',{}).get('rid')
  if sid is not None:assert d.r[sid]==original_refs[sid]
 d.save()
 ob=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=ob.read_typetree();entry=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==d.obj.path_id);span=[{'m_FileID':0,'m_PathID':d.obj.path_id}];ptrs(d.d,span);ptrs(d.s,span);entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span;ob.save_typetree(meta);changes[G][ob.path_id]=meta
 raw=env[G].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[G])
 for pid,h in hashes[G].items():
  if pid not in changes[G]:assert sha(saved[pid].get_raw_data())==h
 for pid,t in changes[G].items():assert saved[pid].read_typetree()==t
 validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
 src=OUT/(('skin-' if suffix else '')+bases[1]);src.write_bytes(raw);target=folder/bases[1];tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/bases[1]),'before':sha(before[target]),'after':sha(raw)})
 audits.append({'variant':tag,'small_sub_title_hidden':True,'native_state_icon_next_to_condition':True,'state_source':'SquadOverviewPlayerBlock.BodyLanguageMorphIcon','last_five_chart_source':'PlayerLastFiveMatchesChartFormSmallBarsCell','matchratinglist':'playerinfo.Person.LastFiveMatchesForm.LastFiveMatchesList','chart_height':22,'starting_small_card_branch_identical':True})
report={'installed':False,'runtime_verified':False,'checks':audits,'native_clone_checks':clone_audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('仅修改SmallSubstituteCardLowerNoRating私有模板的替补分支。移除顶部替补序号标题及占位，原生BodyLanguageMorphIcon放到体能百分比右侧（16px图标、6px间距），保留原生可见性/颜色/提示和伤病图标。下方复用原生PlayerLastFiveMatchesChartFormSmallBarsCell完整22px条形图，映射player=playerinfo.Person、matchratinglist=playerinfo.Person.LastFiveMatchesForm.LastFiveMatchesList（与球队训话原生form列相同来源），保留原生条目顺序、颜色、提示、点击和无数据状态。原卡片下移16px、评分隐藏、旧号码隐藏、右侧号码保留设置沿用。首发小卡片分支逐节点相同，大卡片及其他模块不改。仅游戏/皮肤各自Global包，备份和restore.ps1带哈希保护。序列化/克隆/无关对象检查通过，实际显示及近五场数据待游戏验证。','utf8')
print(OUT)
