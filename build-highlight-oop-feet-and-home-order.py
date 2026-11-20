from pathlib import Path
import json,copy,ast,uuid,importlib.util,struct,hashlib
R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle'
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-oop-feet-and-home-order-').replace("'NAMES=[W,G]'","'NAMES=[W,G,T]'").replace('bases=(W,G)','bases=(G,T)')
exec(compile(prefix,'backup-feet-and-order','exec'))
resource_bases=(W,G,T)
for file,functions in [('build-highlight-five-column-native-player-lists.py',['register_clone','clone_doc']),('build-highlight-lower-five-by-three-with-charts.py',['copy_style','clone_native']),('build-match-ui-avatars-layout.py',['rewrite_arg','rewrite_binding'])]:
 module=ast.parse((R/file).read_text('utf8'));exec(compile(ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in functions],type_ignores=[]),'reuse-native-tools','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
asset_clones=[];new_guids={};clone_audits=[];audits=[];tx=[];cats={};defaults={};AUTO={'m_ValueType':1,'valueIndex':2}
names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
def asset_guid(bn,pid):
 meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle');return next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==pid)
def ptrs(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():ptrs(x,out)
 elif isinstance(v,list):
  for x in v:ptrs(x,out)
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 W,G,T=[n+suffix for n in resource_bases];main=Doc(G,name='HighlightFormationLiveNameAt75');oldguid=asset_guid(G,main.obj.path_id);d,guid=clone_doc(main,'HighlightPhaseSpecificFeetAndCondition',-981108000010000);donor=Doc(W,pid=-970000000009000)
 root=d.named('MatchCondition_Available');assert d.a(root)['m_FullTypeName']=='SI.Bindable.BindableSwitchElement';parent=d.a(root)['m_Parent']['rid'];index=d.a(parent)['m_Children'].index({'rid':root})
 ve=next(i for i,r in d.r.items() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement')
 def phase_gate(name):
  i=d.add(d,root,parent,name);s=d.data(i);s['Binding']['m_kind']=1;s['Binding']['m_direct']={'Path':{'m_path':'inpossession'},'Nullable':0};s['Binding_UxmlAttributeFlags']=1
  d.st(i,[(131102,d.enum('absolute')),(131089,d.px(0)),(131104,d.px(0)),(131105,d.pct(100)),(131087,d.pct(100)),(131084,d.num(0)),(131085,d.num(0))]);return i
 ringgate=phase_gate('HighlightInPossessionCondition');empty=d.add(d,ve,ringgate,'NoConditionInOutOfPossession');d.move(root,ringgate);d.move(ringgate,parent,index)
 rule=d.s['m_Rules'][d.a(root)['m_RuleIndex']];left=next(p for p in rule['m_Properties'] if p['m_Id']==131089)['m_Values'][0];beforeleft=d.s['dimensions'][left['valueIndex']]['value'];d.st(root,[(131089,d.px(beforeleft-4))])
 footgate=phase_gate('HighlightOutOfPossessionFeet');host=d.add(d,ve,footgate,'HighlightTacticsFootPair');empty=d.add(d,ve,footgate,'NoFeetInPossession')
 d.st(host,[(131102,d.enum('absolute')),(131089,AUTO),(131104,AUTO),(131103,d.px(-8)),(131080,d.px(0)),(131105,d.px(22)),(131087,d.px(10)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0))])
 for source_root,x in [(1142,0),(1362,12)]:
  newroot,mapping=clone_native(donor,source_root,host)
  for target in mapping.values():
   for oldpath in ['position.Player.Footedness.LeftFootedness','position.Player.Footedness.RightFootedness','position.Player']:
    rewrite_binding(d.r[target]['data'],oldpath,oldpath.replace('position.Player','position.MatchPlayer.Person'))
  d.st(newroot,[(131089,d.px(x)),(131104,d.px(0))])
 d.save()
 # Route only the four current Highlight formation selectors to this private row.
 counts=[]
 for name in ['HighlightFiveAnalysisHomeOriginalVertical','HighlightFiveAnalysisHomeVertical','HighlightFiveAnalysisAwayOriginalVertical','HighlightFiveAnalysisAwayVertical']:
  doc=Doc(G,name=name);count=0
  for i,r in doc.r.items():
   if r.get('data',{}).get('m_FullTypeName')=='FM.UI.FMTacticsPanel':
    s=doc.data(i)
    if s['PositionTemplateAsset']['m_AssetGUID']==oldguid:s['PositionTemplateAsset']['m_AssetGUID']=guid;s['PositionTemplateAsset_UxmlAttributeFlags']=1;count+=1
  assert count>=1,(tag,name,oldguid);doc.save();counts.append(count)
 for name in names:
  ob=find(T,name);tr=ob.read_typetree();bs=tr['m_gridComponents'];assert len(bs)==10 and bs[0]['m_elementID'].endswith('HomeOriginal')
  bs[0],bs[1]=bs[1],bs[0];bs[0]['m_location']['x']=0;bs[1]['m_location']['x']=4;tr['m_compositionVersion']+=1;tr['m_placementBindings']=[{'m_elementID':b['m_elementID'],'m_optionalConditions':[],'m_optionalConfigConditions':[]} for b in bs];ob.save_typetree(tr);changes[T][ob.path_id]=tr
  if tag=='game':defaults[name]=copy.deepcopy(tr)
 # New private row uses existing native functions, no textures or shared player cards change.
 ob=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=ob.read_typetree();meta['m_Container'].append((guid,{'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':d.obj.path_id}}))
 for key,entry in meta['m_Container']:
  pid=entry['asset']['m_PathID']
  if pid not in changes[G]:continue
  span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[G][pid],span)
  if pid==d.obj.path_id:ptrs(d.s,span)
  entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
 meta['m_Container'].sort(key=lambda x:x[0]);ob.save_typetree(meta);changes[G][ob.path_id]=meta
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';cat=cm.Catalog(before[cp]);loc=cat.locations(oldguid)[0];raw=cat.add_key_location(guid,loc,loc);cat=cm.Catalog(raw);newloc=cat.locations(guid)[0]
 idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx];records=list(cat.key_records);values=[v[0] for v in cat.array(ls,'I')]+[newloc];records[idx]=(ko,cat.append(b''.join(struct.pack('<I',v) for v in values),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));cats[tag]=bytes(cat.data)
 check=cm.Catalog(cats[tag]);record=check.location(check.locations(guid)[0]);assert G.split('::')[0] in check.location(record['dependencies'][0])['internal']
 assert check.locations(guid)[0] in [v[0] for v in check.array(check.key_records[idx][1],'I')]
 audits.append({'variant':tag,'left_top_swap':True,'in_possession_condition_left_delta':-4,'condition_left_before':beforeleft,'condition_left_after':beforeleft-4,'out_of_possession_feet_source':'TacticsDetailedCardDetailsDesktop 1142 and 1362','feet_size':[10,10],'foot_host_right':-8,'foot_host_bottom':0,'formation_row_references':counts})
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
  for pid,tr in changes[bn].items():assert saved[pid].read_typetree()==tr
  for doc in [x for x in documents if x.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
  src=OUT/(('skin-' if suffix else '')+base);src.write_bytes(raw);target=folder/base;tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
 for name,data in [('catalog.bin',cats[tag]),('catalog.hash',hashlib.md5(cats[tag]).hexdigest().encode('ascii'))]:
  target=GAME.parent/name if tag=='game' else SKIN/name;src=OUT/(tag+'-'+name);src.write_bytes(data);tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[target]),'after':sha(data)})
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');migrations=[]
for name,tr in defaults.items():
 p=cache_root/name
 if not p.exists():continue
 data=p.read_bytes();t=json.loads(data.decode('utf8'));bs=t['m_gridComponents'];assert len(bs)==10 and bs[0]['m_elementID'].endswith('HomeOriginal');bs[0],bs[1]=bs[1],bs[0];bs[0]['m_location']['x']=0;bs[1]['m_location']['x']=4;t['m_compositionVersion']=tr['m_compositionVersion'];t['m_placementBindings']=copy.deepcopy(tr['m_placementBindings']);backup=OUT/'backup-cache'/name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(data);src=OUT/('cache-'+name+'.json');raw=json.dumps(t,ensure_ascii=False,indent=2).encode('utf8');src.write_bytes(raw);tx.append({'target':str(p),'source':str(src),'backup':str(backup),'before':sha(data),'after':sha(raw)});migrations.append(name)
report={'installed':False,'runtime_verified':False,'checks':audits,'native_feet_clone_checks':clone_audits,'cache_migrations':migrations,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');installer=(R/'install-independent-resource-patch.py').read_text('utf8')
if migrations:installer=installer.replace('for row in tx:\n',"allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())\nfor row in tx:\n",1)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('上排第1、第2模块交换位置，缓存同步。仅四个当前Highlight阵型选择器改用私有球员行；根据现有inpossession参数切换：有球保留体能并相对当前left偏移向左4px，无球隐藏体能，显示战术页面现成左右脚10px彩色标识和提示。脚部标识原样复制TacticsDetailedCardDetailsDesktop的1142/1362子树，映射position.Player到position.MatchPlayer.Person，放头像右下（22×10容器，right=-8px、bottom=0，左右相距2px），不改颜色阈值/文字/提示/事件。原战术页卡面和共享Highlight行未改。注册私有行及GlobalVisualTreeAssetPreload，游戏/皮肤分别备份和增量修改。序列化和无关对象检查通过，实际显示/脚部数值/切换待游戏内验证。游戏运行时等待退出安装，restore.ps1带哈希保护。','utf8')
print(OUT)
