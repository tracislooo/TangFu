from pathlib import Path
import json,copy,ast
R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle'
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-maps-under-live-pitch-').replace("'NAMES=[W,G]'","'NAMES=[G,T]'").replace('bases=(W,G)','bases=(G,T)')
exec(compile(prefix,'backup-maps-under-pitch','exec'))
helper=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'clone-current-chart-bindings','exec'))
clone_audits=[];audits=[];tx=[];defaults={};CK='<Configurations>k__BackingField';AUTO={'m_ValueType':1,'valueIndex':2}
names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
def erase(doc,i):
 for c in list(doc.a(i).get('m_Children',[])):erase(doc,c['rid'])
 a=doc.a(i);p=a['m_Parent']['rid'];sr=a.get('m_SerializedData',{}).get('rid');doc.a(p)['m_Children'].remove({'rid':i});ids={i,sr};doc.d['references']['RefIds']=[r for r in doc.d['references']['RefIds'] if r['rid'] not in ids]
 for j in ids:doc.r.pop(j,None)
def tree(bn,pid):return copy.deepcopy(changes[bn].get(pid,objs[bn][pid].read_typetree()))
def save(bn,pid,tr):objs[bn][pid].save_typetree(tr);changes[bn][pid]=tr
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 G,T=[n+suffix for n in bases];source=Doc(G,name='HighlightFiveAnalysisFourMaps');d=Doc(G,name='HighlightFiveAnalysisCenterWithoutMaps');old=copy.deepcopy(d.d)
 for c in list(d.a(2149)['m_Children']):erase(d,c['rid'])
 d.st(2149,[(131083,d.enum('row')),(131097,d.px(0)),(131096,d.px(0))])
 roots=[]
 for root in [2151,2153]:
  newroot,mapping=clone_native(source,root,2149);roots.append(newroot)
 d.save();assert d.a(2149)['m_Children']==[{'rid':i} for i in roots]
 def config(pid,w,h):
  desc=tree(T,pid);found=next((c for c in desc[CK] if c['Size']=={'x':w,'y':h}),None)
  if found:return copy.deepcopy(found)
  c=copy.deepcopy(min(desc[CK],key=lambda c:abs(c['Size']['x']-w)+abs(c['Size']['y']-h)));c['Size']={'x':w,'y':h};c['Description']={'m_FileID':0,'m_PathID':pid};desc[CK].append(copy.deepcopy(c));save(T,pid,desc);return c
 for name in names:
  ob=find(T,name);tr=tree(T,ob.path_id);assert len(tr['m_gridComponents'])==10
  reg=tree(T,tr['m_gridElementSet']['m_PathID']);description_refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:description_refs+=group['m_tiles']
  descs={tree(T,r['m_PathID']).get('<ID>k__BackingField'):r['m_PathID'] for r in description_refs}
  for index,ident in [(6,'MatchMomentum'),(7,'MatchStatsStandAlone'),(8,'xGStory')]:
   block=tr['m_gridComponents'][index];pid=descs[ident];loc=block['m_location'];block.update(m_elementID=ident,m_configDescriptions=[{'m_FileID':0,'m_PathID':pid}],m_configDescriptionKeys=[],m_gridElementConfigs=[config(pid,loc['width'],loc['height'])])
  tr['m_placementBindings']=[{'m_elementID':b['m_elementID'],'m_optionalConditions':[],'m_optionalConfigConditions':[]} for b in tr['m_gridComponents']];tr['m_compositionVersion']+=1;save(T,ob.path_id,tr)
  if tag=='game':defaults[name]=(copy.deepcopy(tr),{k:tree(T,v)['<ID>k__BackingField'] for k,v in descs.items()})
  audits.append({'variant':tag,'layout':name,'lower_middle_defaults':['MatchMomentum','MatchStatsStandAlone','xGStory'],'grid':[20,8],'pitch_and_maps_same_upper_lower_dimensions':True})
 # Update preload spans of changed templates, styles, descriptions and compositions.
 def ptrs(v,out):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
   else:
    for x in v.values():ptrs(x,out)
  elif isinstance(v,list):
   for x in v:ptrs(x,out)
 for bn in [G,T]:
  ob=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=ob.read_typetree()
  for key,entry in meta['m_Container']:
   pid=entry['asset']['m_PathID']
   if pid not in changes[bn]:continue
   span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[bn][pid],span)
   if bn==G and pid==d.obj.path_id:ptrs(d.s,span)
   entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
  ob.save_typetree(meta);changes[bn][ob.path_id]=meta
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
  for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t
  if bn==G:validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
  src=OUT/(('skin-' if suffix else '')+base);src.write_bytes(raw);target=folder/base;tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');migrations=[]
for name,(template,descs) in defaults.items():
 p=cache_root/name
 if not p.exists():continue
 data=p.read_bytes();updated=json.loads(data.decode('utf8'));assert len(updated['m_gridComponents'])==10
 for i,ident in [(6,'MatchMomentum'),(7,'MatchStatsStandAlone'),(8,'xGStory')]:
  b=copy.deepcopy(template['m_gridComponents'][i]);b['m_configDescriptions']=[{'instanceID':0}];b['m_configDescriptionKeys']=[ident]
  for c in b['m_gridElementConfigs']:c['Description']={'instanceID':0};c['Asset']={'instanceID':0}
  updated['m_gridComponents'][i]=b
 updated['m_compositionVersion']=template['m_compositionVersion'];updated['m_placementBindings']=copy.deepcopy(template['m_placementBindings']);backup=OUT/'backup-cache'/name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(data);src=OUT/('cache-'+name+'.json');raw=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8');src.write_bytes(raw);tx.append({'target':str(p),'source':str(src),'backup':str(backup),'before':sha(data),'after':sha(raw)});migrations.append(name)
report={'installed':False,'runtime_verified':False,'checks':audits,'chart_binding_clone_checks':clone_audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'cache_migrations':migrations,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8')
if migrations:installer=installer.replace('for row in tx:\n',"allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())\nfor row in tx:\n",1)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('四张分析图移入上排中间实时球场下方的整个红框区域，替换该区域原比赛信息、数据对比和三个小图表。保持现有球场上下分区尺寸和四图两列两行，主队左客队右、热点上传球下，完整复制原生绑定、方向与点击事件。下排中间三格均为原生可选模块区，默认比赛势头/比赛统计/预期进球视图；完整菜单沿用当前私有原生注册表。布局20×8、上排4/4/4/4/4、下排5/3/4/3/5保持。分别备份并修改游戏与皮肤；迁移当前自定义布局中间三槽，其余选择保留。序列化、克隆绑定和无关对象一致性检查通过；实际显示/刷新/点击待游戏验证。restore.ps1带哈希保护。','utf8')
print(OUT)
