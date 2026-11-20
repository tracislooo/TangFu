from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess,struct,uuid,importlib.util
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';F='ui-tablefactories_assets_all.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest();OUT=R/('tactics-portraits120-condition-percent-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
before={p/n:(p/n).read_bytes() for p in [GAME,SKIN] for n in [W,F] if (p/n).exists()};missing_before=[p/n for p in [GAME,SKIN] for n in [W,F] if not (p/n).exists()]
for n in [W,F]:
 if SKIN/n in before:assert before[GAME/n]==before[SKIN/n]
for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']:before[p]=p.read_bytes()
assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']
for p,b in before.items():
 folder=OUT/('backup-skin' if p.parent==SKIN else 'backup-game');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for f in [GAME,SKIN] for p in f.glob('*.bundle') if p.name not in [W,F]}
envs={n:UnityPy.load(before[GAME/n]) for n in [W,F]};objs={n:{o.path_id:o for o in e.objects} for n,e in envs.items()};hashes={n:{i:sha(o.get_raw_data()) for i,o in os.items()} for n,os in objs.items()};changed={W:{},F:{}}
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def serial(r,i):return r.get(r[i]['data'].get('m_SerializedData',{}).get('rid'),{}) if r[i]['data'].get('m_SerializedData',{}).get('rid',-2)!=-2 else {'data':{}}
def save(n,i,d):objs[n][i].save_typetree(d);changed[n][i]=copy.deepcopy(d)
# Enlarge both portrait frames, including their fixed min/max constraints.
audit=[]
for pid,size in [(-8273082868742719783,35),(3127595210179668386,34)]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree();old=copy.deepcopy(rr)
 i=next(i for i,a in rr.items() if 'm_Parent' in a.get('data',{}) and serial(rr,i)['data'].get('name')=='TacticsPlayerPortraitFrame')
 new=struct.unpack('<f',struct.pack('<f',size*1.2))[0];top=struct.unpack('<f',struct.pack('<f',3-size*.1))[0]
 override(rr[i]['data'],[prop(k,px(new)) for k in [131105,131087,131095,131097,131094,131096]]+[prop(131104,px(top))])
 assert [x for x in old if old[x]!=rr[x]]==[i];validate_ui(doc,sheet);save(W,pid,doc);save(W,sid,sheet);audit.append({'template':doc['m_Name'],'old':size,'new':new})
# Private cell keeps the original tooltip and player mapping.
CELL=-970000000001000;STYLE=-970000000001001;GUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/TacticsConditionPercentage/v1').hex
source=objs[W][-2699943933354802414];doc=source.read_typetree();old_sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][old_sid].read_typetree();doc['m_Name']='TacticsConditionPercentageCell';doc['inlineSheet']['m_PathID']=STYLE;sheet['m_Name']='TacticsConditionPercentageCell_Style';rr=refs(doc)
page=objs[W][-930000000001001].read_typetree();pr=refs(page)
def pnode(name):return next(i for i,a in pr.items() if 'm_Parent' in a.get('data',{}) and serial(pr,i)['data'].get('name')==name)
switchid=pnode('OverviewFitness_Condition_Available');textid=pnode('OverviewFitness_Condition_Number075')
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
# Replace the icon, leaving the native tooltip above it.
image=1011;parent=rr[image]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':image});sdid=rr[image]['data']['m_SerializedData']['rid'];rr.pop(image);rr.pop(sdid);doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] in rr]
def add(proto,psd,parent,name):
 global next_rid,next_id
 a=copy.deepcopy(proto);s=copy.deepcopy(psd);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
 a['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_RuleIndex=-1,m_SerializedData={'rid':s['rid']},m_Classes=[],m_Properties=[])
 s['data'].update(uxmlAssetId=next_id,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);next_id+=1
 rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
def fill(i):override(rr[i]['data'],[prop(131105,pct(100)),prop(131087,pct(100)),prop(131097,px(0)),prop(131096,px(0)),prop(131084,num(1)),prop(131085,num(1))])
def args(raw):
 b=bytes(raw);p=1;out=[]
 for _ in range(b[0]):n=struct.unpack_from('<I',b,p)[0];p+=4;out.append(bytearray(b[p:p+n]));p+=n
 assert p==len(b);return out
def encode(a):return list(bytes([len(a)])+b''.join(struct.pack('<I',len(x))+x for x in a))
def switch(parent,limit):
 i=add(pr[switchid],serial(pr,switchid),parent,'TacticsConditionAbove'+str(limit));fill(i);s=serial(rr,i)['data'];a=args(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);struct.pack_into('<i',a[1],len(a[1])-4,limit)
 oldpath=b'person.Condition';newpath=b'player.Condition';assert a[2].endswith(bytes([len(oldpath)])+oldpath);a[2][-len(oldpath)-1:]=bytes([len(newpath)])+newpath;s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(a);return i
leafvalues={}
def leaf(parent,value):
 i=add(pr[textid],serial(pr,textid),parent,'TacticsConditionPercent'+str(value));s=serial(rr,i)['data'];s.update(text='--' if value is None else str(value)+'%',text_UxmlAttributeFlags=1,TextBinding_UxmlAttributeFlags=0,DebugDisplay='');s['TextBinding']['m_kind']=0
 rr[i]['data']['m_Classes']=['body-md','global-text-primary'];fill(i);override(rr[i]['data'],[prop(65537,px(12)),prop(65546,en('middle-center')),prop(65552,en('nowrap')),prop(262150,px(0)),prop(262151,px(0))]);leafvalues[i]=value;return i
def tree(parent,lo,hi):
 if lo==hi:return leaf(parent,(lo-50)*2)
 mid=(lo+hi)//2;i=switch(parent,mid);tree(i,lo,mid);tree(i,mid+1,hi);return i
root=switch(parent,-1);leaf(root,None);tree(root,50,100)
for i in [1001,1002,parent]:fill(i)
override(rr[1001]['data'],[prop(262151,px(0))])
def select(i,value):
 if i in leafvalues:return leafvalues[i]
 a=rr[i]['data'];s=serial(rr,i)['data'];limit=struct.unpack_from('<i',args(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])[1],34)[0]
 return select(a['m_Children'][int(value is not None and value>limit)]['rid'],value)
# Check serialized decisions against the documented UI scale.
for raw in [None,-2147483648]+list(range(-1,151)):
 expected=None if raw is None or raw<0 else max(0,min(100,(raw-50)*2));assert select(root,raw)==expected,(raw,select(root,raw),expected)
validate_ui(doc,sheet)
def clone(source,pid,d):
 assert pid not in objs[W];o=copy.copy(source);o.path_id=pid;o.data=None;o._read_until=None;o.assets_file.objects[pid]=o;objs[W][pid]=o;save(W,pid,d)
clone(source,CELL,doc);clone(objs[W][old_sid],STYLE,sheet)
metaobj=next(o for o in objs[W].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();span=[]
def pointers(v):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'}:
   if v['m_PathID'] and v not in span:span.append(copy.deepcopy(v))
  else:
   for x in v.values():pointers(x)
 elif isinstance(v,list):
  for x in v:pointers(x)
pointers(doc);pointers(sheet);span.append({'m_FileID':0,'m_PathID':CELL});meta['m_Container'].append((GUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':CELL}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda x:x[0]);save(W,metaobj.path_id,meta)
# Only the out-of-match tactical selection factory uses the private cell.
factoryid=-7014073910555419620;factory=objs[F][factoryid].read_typetree();oldfactory=copy.deepcopy(factory);col=next(c for c in factory['m_rowData'] if c['m_id']=='condition');assert col['m_uxmlRef']['m_AssetGUID']=='4873fa63429f48944abf1edead6c87a4';col['m_uxmlRef']['m_AssetGUID']=GUID;save(F,factoryid,factory)
assert sum(a!=b for a,b in zip(oldfactory['m_rowData'],factory['m_rowData']))==1
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);oldcat=cm.Catalog(before[GAME.parent/'catalog.bin']);loc=oldcat.locations('16f0f04a90621324cb8e16dcf53d5b90')[0];cat=cm.Catalog(oldcat.add_key_location(GUID,loc,loc))
idx=next(i for i,(key,_) in enumerate(cat.keys()) if key=='GameWorldVisualTreeAssetPreload');keyobj,locset=cat.key_records[idx];locs=[v[0] for v in cat.array(locset,'I')]+cat.locations(GUID);records=list(cat.key_records);records[idx]=(keyobj,cat.append(b''.join(struct.pack('<I',p) for p in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catout=bytes(cat.data)
checkcat=cm.Catalog(catout);assert set(dict(checkcat.keys()))==set(dict(oldcat.keys()))|{GUID}
newkeys=dict(checkcat.keys())
for key,locset in oldcat.keys():
 assert [v[0] for v in checkcat.array(newkeys[key],'I')]==[v[0] for v in oldcat.array(locset,'I')]+(checkcat.locations(GUID) if key=='GameWorldVisualTreeAssetPreload' else [])
outputs={n:e.file.save(packer='lz4') for n,e in envs.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,(n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,(n,i)
 (OUT/n).write_bytes(b)
hashout=hashlib.md5(catout).hexdigest().encode('ascii');(OUT/'catalog.bin').write_bytes(catout);(OUT/'catalog.hash').write_bytes(hashout)
install={p/n:b for p in [GAME,SKIN] for n,b in outputs.items()};install.update({GAME.parent/'catalog.bin':catout,GAME.parent/'catalog.hash':hashout,SKIN/'catalog.bin':catout})
restore=['$ErrorActionPreference = "Stop"']
for p in before:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-skin' if p.parent==SKIN else 'backup-game')/p.name)+"' -Destination '"+str(p)+"' -Force")
for p in missing_before:restore.append("Remove-Item -LiteralPath '"+str(p)+"' -Force -ErrorAction SilentlyContinue")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
report={'installed':False,'runtime_verified':False,'portraits':audit,'condition_formula':'clamp((raw-5000)/50,0,100)%','ui_formula':'clamp((player.Condition-50)*2,0,100)%','examples':{'5000':'0%','7500':'50%','10000':'100%'},'private_cell_guid':GUID,'factory':factory['m_Name'],'original_sort_binding_preserved':True,'original_condition_cells_preserved':True,'changed_objects':{n:list(x) for n,x in changed.items()},'percent_cases_checked':154,'after_sha256':{str(p):sha(b) for p,b in install.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in install.items():p.write_bytes(b)
 for p,b in install.items():assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 for p in missing_before:
  if p.exists():p.unlink()
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'portraits':audit,'condition_examples':report['examples']}))



