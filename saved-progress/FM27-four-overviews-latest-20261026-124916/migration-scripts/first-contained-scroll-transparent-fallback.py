from pathlib import Path
import ast,copy,json,struct,uuid,zlib,importlib.util
boot=Path('second-overview-stats-bans-stacked-pitch.py').read_text('utf8').split('SELECTOR_SOURCE =')[0].replace('second-overview-stats-bans-stacked-pitch-','first-contained-scroll-transparent-fallback-')
exec(compile(boot,'backup-and-helpers','exec'))
clones=[]
helpers=ast.parse(Path('third-left-fc-hidden-overview.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['serial','add_object','save','clone','commit_clone']],type_ignores=[]),'cloning-helpers','exec'))
BASE,BS=-940000000016000,-940000000016001;TRANSFER,TS=-940000000016010,-940000000016011;FAV,FS=-940000000016020,-940000000016021
BASEKEY=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-first-fallback-transparent-native-tile-frame-v1').hex;TRANSFERKEY=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-first-transfer2x1-transparent-contained-v1').hex;FAVKEY=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-first-favoured-personnel-transparent-contained-v1').hex
# Private native frame: keep title/interaction slots and remove only painted card surfaces.
doc,sheet,oldstyle=clone(G,4266724946999838712,BASE,BS,BASEKEY,'FirstOverviewTransparentNativeTileFrame');rr=refs(doc);old=copy.deepcopy(rr)
slot=rr[1006]['data']['m_SerializedData']['rid'];replacement=copy.deepcopy(serial(old,1002));replacement['rid']=slot;replacement['data'].update(uxmlAssetId=rr[1006]['data']['m_Id'],name='FirstOverviewTransparentTileBody',name_UxmlAttributeFlags=1);rr[slot].clear();rr[slot].update(replacement);rr[1006]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
for i in [1002,1004,1006,1008,1010]:
 rr[i]['data']['m_Classes']=[x for x in rr[i]['data'].get('m_Classes',[]) if x not in ['layout-tile-interaction-button-background','surfaces-card-tile-border','height-100-px']]
 override(rr[i]['data'],[prop(458752,val(4,{'r':0.0,'g':0.0,'b':0.0,'a':0.0})),prop(458753,none),prop(131096,px(0)),prop(131094,pct(100))])
for i in [1001,1002,1004,1006,1008]:override(rr[i]['data'],[prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131084,num(1)),prop(131085,num(1))])
override(rr[1010]['data'],[prop(131081,en('none'))])
commit_clone(G,4266724946999838712,BASE,BS,oldstyle,doc,sheet)
for source,pid,sid,key,label in [(-6532285783748324082,TRANSFER,TS,TRANSFERKEY,'FirstOverviewTransparentTransferStatus2x1'),(-6585881198965646880,FAV,FS,FAVKEY,'FirstOverviewTransparentFavouredPersonnel')]:
 doc,sheet,oldstyle=clone(W,source,pid,sid,key,label);rr=refs(doc)
 for u in doc['m_Usings']:
  if u['path']=='f677caec43d6c1342b1bba39c5ae2c5f':u.update(path=BASEKEY,asset={'m_FileID':0,'m_PathID':0})
 for i in [1001,1002]:override(rr[i]['data'],[prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131084,num(1)),prop(131085,num(1)),prop(458768,en('hidden'))])
 if pid==FAV:
  for r in list(rr.values()):
   if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.StreamedObjectList':
    i=r['rid']
    for k,v in {'ClampSizeToPage':1,'HorizontalScrollerVisibility':2,'VerticalScrollerVisibility':0}.items():sd(i)[k]=v;sd(i)[k+'_UxmlAttributeFlags']=1
    override(rr[i]['data'],[prop(131087,px(0)),prop(131096,px(0)),prop(131094,pct(100)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1))])
 commit_clone(W,source,pid,sid,oldstyle,doc,sheet)
# The first version's own pros/cons module gets two independent, bounded vertical lists.
MODULE=-940000000015000;doc=objs[G][MODULE].read_typetree();SID=doc['inlineSheet']['m_PathID'];sheet=objs[G][SID].read_typetree();rr=refs(doc);old=copy.deepcopy(rr)
for i in [1001,1002,1004,1005]:override(rr[i]['data'],[prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131085,num(1)),prop(458768,en('hidden'))])
for i in [1001,1002]:override(rr[i]['data'],[prop(131082,px(0)),prop(131084,num(1))])
for i in [1008,1011]:
 override(rr[i]['data'],[prop(131087,px(0)),prop(131096,px(0)),prop(131094,pct(100)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1))])
 for k,v in {'ClampSizeToPage':1,'HorizontalScrollerVisibility':2,'VerticalScrollerVisibility':0}.items():sd(i)[k]=v;sd(i)[k+'_UxmlAttributeFlags']=1
 for k in ['Binding','RowTemplate','RowParamName']:assert sd(i)[k]==serial(old,i)['data'][k]
save(G,MODULE,doc,SID,sheet)
# Remove the right-wide scroll view; flex the lower region into space left below hidden attributes.
PAGE,STYLE=-930000000001001,-930000000001000;doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree()
scrollsd=rr[1703]['data']['m_SerializedData']['rid'];replacement=copy.deepcopy(serial(old,1011));replacement['rid']=scrollsd;replacement['data'].update(uxmlAssetId=rr[1703]['data']['m_Id'],name='FirstOverviewRightAreaWithoutOuterScroll',name_UxmlAttributeFlags=1);rr[scrollsd].clear();rr[scrollsd].update(replacement);rr[1703]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
for i in [1703,1011]:override(rr[i]['data'],[prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131085,num(1)),prop(131084,num(1)),prop(458768,en('hidden')),prop(131083,en('column'))])
override(rr[1011]['data'],[prop(131082,px(0))])
row=named('FirstOverviewTransferPlayerMapping');left=named('FirstOverviewNativeTransferStatusFallback');right=named('FirstOverviewFavouredPersonnelFallback');switch=named('FirstOverviewProsConsOrTransferSwitch')
for i in [6298,switch,6306,6308]:override(rr[i]['data'],[prop(131087,px(0)),prop(131096,px(0)),prop(131094,pct(100)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(458768,en('hidden'))])
# Both alternative branches use the same available height, never the old unbounded 260px.
override(rr[row]['data'],[prop(131087,px(0)),prop(131096,px(0)),prop(131094,pct(100)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(458768,en('hidden'))])
for i in [left,right]:override(rr[i]['data'],[prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131085,num(1)),prop(458768,en('hidden'))])
for u in doc['m_Usings']:
 if u['alias']=='FirstOverviewNativeTransferStatus':u.update(path=TRANSFERKEY,asset={'m_FileID':0,'m_PathID':0})
 elif u['alias']=='FirstOverviewNativeFavouredPersonnel':u.update(path=FAVKEY,asset={'m_FileID':0,'m_PathID':0})
assert serial(rr,switch)==serial(old,switch)
assert rr[row]['data']['m_Children']==old[row]['data']['m_Children']
save(W,PAGE,doc,STYLE,sheet)
# Register the private transparent components using native providers and own-bundle-first dependencies.
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin'])
for n in [W,G]:
 ab=next(o for o in objs[n].values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
 for c in [c for c in clones if c['bundle']==n]:
  entry=next(v for k,v in meta['m_Container'] if k==c['source_key'] and v['asset']['m_PathID']==c['source']);span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
  for ptr in span:
   if ptr['m_FileID']==0:
    if ptr['m_PathID']==c['source']:ptr['m_PathID']=c['pid']
    elif ptr['m_PathID']==c['source_style']:ptr['m_PathID']=c['style']
  meta['m_Container'].append((c['key'],{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':c['pid']}}));meta['m_PreloadTable'].extend(span)
  loc=next(x for x in cat.locations(c['source_key']) if cat.location(x)['type'][1].endswith('VisualTreeAsset'));cat=cm.Catalog(cat.add_key_location(c['key'],loc,loc));label='GameWorldVisualTreeAssetPreload' if n==W else 'GlobalVisualTreeAssetPreload';idx=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)==label);ko,ls=cat.key_records[idx];locs=[x[0] for x in cat.array(ls,'I')]+cat.locations(c['key']);newset=cat.append(b''.join(struct.pack('<I',x) for x in locs),True);records=list(cat.key_records);records[idx]=(ko,newset);table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table);cat=cm.Catalog(bytes(cat.data))
 meta['m_Container'].sort(key=lambda x:x[0]);save(n,ab.path_id,meta)
catout=bytes(cat.data)

outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catout);hashout=__import__('hashlib').md5(catout).hexdigest().encode('ascii');(OUT/'catalog.hash').write_bytes(hashout)
report={'installed':False,'runtime_verified':False,'first_only':True,
    'outer_right_scroll_removed':True,'lower_region_height':'remaining space below hidden attributes',
    'pros_cons_scroll':'separate internal vertical lists only','fallback_columns':[50,50],
    'transfer_and_favoured_backgrounds_removed':True,'fallback_condition_unchanged':True,
    'private_components':{'frame':BASEKEY,'transfer':TRANSFERKEY,'favoured':FAVKEY},
    'other_versions_unchanged':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
pending=[(folder/n,b) for n,b in outputs.items() for folder in [GAME,SKIN]]+[(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',hashout),(SKIN/'catalog.hash',hashout)]
for p,b in pending:
 if p not in before:
  before[p]=p.read_bytes() if p.exists() else None
  if before[p] is not None:(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name).write_bytes(before[p])
restore=['$ErrorActionPreference = "Stop"']
for p,b in before.items():
 if b is not None:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in pending:p.write_bytes(b);assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():
  if b is not None:p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'outer_scroll_removed':True,'transparent_fallback':True}))
