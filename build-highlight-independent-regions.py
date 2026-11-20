from pathlib import Path
import ast,copy,json,uuid,hashlib,importlib.util
R=Path(__file__).parent
source=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8')
prefix=source.split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-independent-regions-').replace("'NAMES=[W,G]'","'NAMES=[M,T]'").replace('bases=(W,G)','bases=(M,T)')
T='ui-tileslayouts_assets_all.bundle'
exec(compile(prefix,'backup-independent-regions','exec'))
helper=ast.parse((R/'build-highlight-five-column-native-player-lists.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='register_clone'],type_ignores=[]),'clone-grid','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
asset_clones=[];new_guids={};tx=[];audits=[];CK='<Configurations>k__BackingField';AUTO={'m_ValueType':1,'valueIndex':2}
def ptrs(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():ptrs(x,out)
 elif isinstance(v,list):
  for x in v:ptrs(x,out)
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 M,T=[n+suffix for n in bases];d=Doc(M,name='OverviewPrototype');donor=Doc(M,name='TeamNewsPanel');ve=next(i for i,r in d.r.items() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement');scale=next(i for i,r in donor.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.ScalableBindableGridLayoutElement')
 grids=[i for i,r in list(d.r.items()) if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.ScalableBindableGridLayoutElement' and d.data(i).get('name','').startswith('ResponsiveNativeGrid_')];assert len(grids)==4
 def fit(i):
  d.st(i,[(131097,d.px(0)),(131096,d.px(0)),(131095,d.pct(100)),(131094,d.pct(100)),(131084,d.num(1)),(131085,d.num(1)),(131082,d.px(0)),(131074,d.enum('stretch'))])
 def box(parent,name):
  i=d.add(d,ve,parent,name);fit(i);return i
 for gi,old in enumerate(grids):
  binding=copy.deepcopy(d.data(old)['Bindings']);setpid=binding['m_gridCompositionSet']['m_PathID'];oldset=objs[T][setpid].read_typetree();layoutptr=next(e['m_value'][0] for e in oldset['m_gridBreakpointCompositionData']['m_values'] if e['m_key']==3);layoutob=objs[T][layoutptr['m_PathID']];layout=layoutob.read_typetree();assert len(layout['m_gridComponents'])==9
  registry=objs[T][layout['m_gridElementSet']['m_PathID']].read_typetree()
  for ref in registry['m_gridElementDescriptions']:
   dp=ref['m_PathID'];desc=copy.deepcopy(changes[T].get(dp,objs[T][dp].read_typetree()))
   if not any(c['Size']=={'x':1,'y':1} for c in desc.get(CK,[])):
    sourceconfigs=[c for c in desc.get(CK,[]) if c['Size']=={'x':6,'y':4}] or desc.get(CK,[])[:1]
    for c in sourceconfigs:
     cfg=copy.deepcopy(c);cfg['Size']={'x':1,'y':1};desc[CK].append(cfg)
    objs[T][dp].save_typetree(desc);changes[T][dp]=desc
  # Preserve the bool-switch position. Its replacement has two independent rows.
  parent=d.a(old)['m_Parent']['rid'];idx=d.a(parent)['m_Children'].index({'rid':old});root=box(parent,'BoundedRegions_'+str(gi));d.move(root,parent,idx);d.move(old,root);d.st(old,[(131081,d.enum('none'))]);d.st(root,[(131083,d.enum('column')),(131087,d.pct(100)),(131105,d.pct(100))])
  upper=box(root,'Upper60Percent');lower=box(root,'Lower40Percent');d.st(upper,[(131084,d.num(3)),(131083,d.enum('row'))]);d.st(lower,[(131084,d.num(2)),(131083,d.enum('row'))])
  for si,block in enumerate(layout['m_gridComponents']):
   host=box(upper if si<5 else lower,'Region_'+str(si));weight=[3,3,5,3,3][si] if si<5 else 1;d.st(host,[(131084,d.num(weight)),(131102,d.enum('relative'))])
   # Each native selector owns one logical cell. No cross-row pixel grid remains.
   tr=copy.deepcopy(layout);b=copy.deepcopy(block);b['m_location']={'x':0,'y':0,'width':1,'height':1};b['m_minSize']={'x':1,'y':1};b['m_maxSize']={'x':1,'y':1}
   for c in b['m_gridElementConfigs']:c['Size']={'x':1,'y':1}
   tr['m_gridComponents']=[b];tr['m_layoutPreset']={'Name':'','Size':{'x':1,'y':1}};tr['m_optionalSlices']['m_instantiationOrder']=[0];tr['m_placementBindings']=[v for v in tr['m_placementBindings'] if v['m_elementID']==b['m_elementID']];tr['m_compositionVersion']+=1
   pid=-981104500000000-gi*100-si*2;name='HighlightRegionComposition_'+str(gi)+'_'+str(si);ob,tr,guid=register_clone(T,layoutob,name,pid,tr)
   st=copy.deepcopy(oldset)
   for entry in st['m_gridBreakpointCompositionData']['m_values']:
    if entry['m_key'] in [0,1,2,3]:entry['m_value']=[{'m_FileID':0,'m_PathID':pid}]
   sob,st,sguid=register_clone(T,objs[T][setpid],name+'Set',pid-1,st)
   node=d.add(donor,scale,host,'NativeRegion_'+str(gi)+'_'+str(si));s=d.data(node);s['Bindings']=copy.deepcopy(binding);s['Bindings']['m_gridCompositionSet']={'m_FileID':binding['m_gridCompositionSet']['m_FileID'],'m_PathID':pid-1};s.update(Bindings_UxmlAttributeFlags=1,IsCustomisable=1,IsCustomisable_UxmlAttributeFlags=1,IgnoreOuterPadding=1,IgnoreOuterPadding_UxmlAttributeFlags=1,CentreContent=0,CentreContent_UxmlAttributeFlags=1,pickingMode=0,pickingMode_UxmlAttributeFlags=1)
   fit(node);d.st(node,[(131102,d.enum('absolute')),(131089,d.px(0)),(131103,d.px(0)),(131104,d.px(0)),(131080,d.px(0))])
 d.save()
 metaob=next(o for o in objs[T].values() if o.type.name=='AssetBundle');meta=metaob.read_typetree();new=[a for a in asset_clones if a['bundle']==T]
 for a in new:
  span=[{'m_FileID':0,'m_PathID':a['pid']}];ptrs(changes[T][a['pid']],span);meta['m_Container'].append((a['guid'],{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':a['pid']}}));meta['m_PreloadTable']+=span
 meta['m_Container'].sort(key=lambda x:x[0]);metaob.save_typetree(meta);changes[T][metaob.path_id]=meta
 for bn in [M,T]:
  bundleob=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');bundlemeta=bundleob.read_typetree()
  for key,entry in bundlemeta['m_Container']:
   pid=entry['asset']['m_PathID']
   if pid not in changes[bn]:continue
   span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[bn][pid],span)
   entry.update(preloadIndex=len(bundlemeta['m_PreloadTable']),preloadSize=len(span));bundlemeta['m_PreloadTable']+=span
  bundleob.save_typetree(bundlemeta);changes[bn][bundleob.path_id]=bundlemeta
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';raw=before[cp]
 for a in new:
  cat=cm.Catalog(raw);loc=cat.locations(a['source_guid'])[0];raw=cat.add_key_location(a['guid'],loc,loc)
 check=cm.Catalog(raw)
 for a in new:assert T.split('::')[0] in check.location(check.location(check.locations(a['guid'])[0])['dependencies'][0])['internal']
 for base in bases:
  bn=base+suffix;data=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
  for pid,tr in changes[bn].items():assert saved[pid].read_typetree()==tr
  dest=folder/base;src=OUT/(('skin-' if suffix else '')+base);src.write_bytes(data);tx.append({'target':str(dest),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[dest]),'after':sha(data)})
 for name,data in [('catalog.bin',raw),('catalog.hash',hashlib.md5(raw).hexdigest().encode())]:
  dest=GAME.parent/name if tag=='game' else SKIN/name;src=OUT/((tag+'-')+name);src.write_bytes(data);tx.append({'target':str(dest),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[dest]),'after':sha(data)})
 audits.append({'variant':tag,'independent_native_regions':36,'ratios':[[3,2],[3,3,5,3,3],[1,1,1,1]],'unrelated_objects_identical':True})
(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'checks':audits,'protected_sha256':{}},indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
print(OUT)
