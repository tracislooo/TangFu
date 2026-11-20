from pathlib import Path
import sys,copy,json,hashlib,datetime,ast,uuid,importlib.util,struct,zlib,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';B='ui-backgrounds_assets_common.bundle'
CACHE=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large');PREV=R/'right-status-bans-hidden-tactics-20261020-135932';sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=R/('swap-radar-status-transparent-tactics-restore-bottom-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
paths=[GAME/W,SKIN/W,GAME/L,SKIN/L,GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin',CACHE];before={p:p.read_bytes() for p in paths}
for p,b in before.items():
 tag='backup-cache' if p==CACHE else ('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin');folder=OUT/tag;folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/B,SKIN/B,GAME/G,SKIN/G]};assert before[GAME/W]==before[SKIN/W];assert before[GAME/L]==before[SKIN/L]
e=UnityPy.load(before[GAME/W]);o={x.path_id:x for x in e.objects};af=e.assets[0];hashes={i:sha(x.get_raw_data()) for i,x in o.items()};oldwrite=TypeTreeHelper.write_value
source=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'style helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};source=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
nativepid=4958372856258444847;native=o[nativepid].read_typetree();newpid=-940000000003000;key=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-right-middle-tactical-effectiveness-content-only').hex;assert newpid not in o
private=copy.deepcopy(native);private['m_Name']='RightMiddleTacticalEffectivenessContentOnly';private['m_ContentHash']=struct.unpack('<i',struct.pack('<I',zlib.crc32(key.encode())))[0];rs={r['rid']:r for r in private['references']['RefIds']}
assert rs[1004]['data']['m_TemplateAlias']=='tile-figma-base-template';assert rs[1004]['data']['m_Children']==[{'rid':1006}]
children=rs[1001]['data']['m_Children'];index=children.index({'rid':1004});children[index]={'rid':1006};rs[1006]['data']['m_Parent']={'rid':1001}
private['references']['RefIds']=[r for r in private['references']['RefIds'] if r['rid'] not in [1004,1007,1008,1009]];private['m_Usings']=[u for u in private['m_Usings'] if u['alias']!='tile-figma-base-template']
assert all(r.get('data',{}).get('m_TemplateAlias')!='tile-figma-base-template' for r in private['references']['RefIds']);validate_ui(private,o[private['inlineSheet']['m_PathID']].read_typetree())
obj=copy.copy(o[nativepid]);obj.path_id=newpid;af.objects[newpid]=obj;obj.save_typetree(private);changed={newpid:private};audit=[]
for pid in [-930000000001001,-930000000001003]:
 doc=o[pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};sid=doc['inlineSheet']['m_PathID'];sheet=o[sid].read_typetree();original=copy.deepcopy(rr)
 def name(r):return rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name','')
 def find(n):
  hits=[r['rid'] for r in rr.values() if name(r)==n];assert len(hits)==1,(n,hits);return hits[0]
 def st(i,props):override(rr[i]['data'],props)
 if pid==-930000000001001:
  radar=find('AttributeSpiderChart');status=find('OverviewTopRightStatusPanel');parent=rr[radar]['data']['m_Parent']['rid'];management=rr[status]['data']['m_Parent']['rid'];assert parent==1173 and management==1349
  # Exchange the slots, retaining the original chart content and the status/bans data.
  ix=rr[parent]['data']['m_Children'].index({'rid':radar});rr[parent]['data']['m_Children'][ix]={'rid':status};rr[status]['data']['m_Parent']={'rid':parent}
  ix=rr[management]['data']['m_Children'].index({'rid':status});rr[management]['data']['m_Children'][ix]={'rid':radar};rr[radar]['data']['m_Parent']={'rid':management}
  auto={'m_ValueType':1,'valueIndex':2}
  st(status,[prop(131102,en('relative')),prop(131089,auto),prop(131104,auto),prop(131103,auto),prop(131074,en('auto')),prop(131105,px(240)),prop(131097,px(240)),prop(131095,px(240)),prop(131087,px(176)),prop(131096,px(176)),prop(131094,px(176)),prop(131084,num(0)),prop(131085,num(0))])
  bs=find('OverviewTopRightBansScroll');st(bs,[prop(131105,px(240)),prop(131087,px(128))])
  st(radar,[prop(131102,en('absolute')),prop(131089,px(252)),prop(131104,px(0)),prop(131105,px(240)),prop(131097,px(240)),prop(131095,px(240)),prop(131087,px(220)),prop(131096,px(220)),prop(131094,px(220)),prop(131085,num(0)),prop(131073,en('center')),prop(131088,en('center'))])
  # The chart itself retains its original 220 x 176 drawing size and bindings.
  assert rr[1043]==original[1043]
 for u in doc['m_Usings']:
  if u['alias']=='RightMiddleTacticalEffectiveness':u['path']=key;u['asset']={'m_FileID':0,'m_PathID':0}
 t=find('RightMiddleTacticalEffectiveness');st(t,[prop(131087,px(140)),prop(131096,px(140))]);validate_ui(doc,sheet)
 for i,r in original.items():
  n=r.get('data',{}).get('name','')
  if n.startswith(('OverviewFitness_','RightHidden')):assert rr[i]==r,('data binding changed',pid,i)
 o[pid].save_typetree(doc);o[sid].save_typetree(sheet);changed[pid]=doc;changed[sid]=sheet;audit.append({'page':pid,'private_tactical_guid':key,'native_bottom_tactical_unchanged':True,'radar_swapped':pid==-930000000001001})
# Register only the isolated content component; the original native tile remains untouched.
metaobj=next(x for x in o.values() if x.type.name=='AssetBundle');meta=metaobj.read_typetree();preload=len(meta['m_PreloadTable']);meta['m_PreloadTable'] += [copy.deepcopy(private['m_Script']),copy.deepcopy(private['inlineSheet']),{'m_FileID':0,'m_PathID':newpid}];meta['m_Container'].append((key,{'preloadIndex':preload,'preloadSize':3,'asset':{'m_FileID':0,'m_PathID':newpid}}));meta['m_Container'].sort(key=lambda p:p[0]);metaobj.save_typetree(meta);changed[metaobj.path_id]=meta
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin']);nativekey='414d4dc7ae21fca47a2684eb783dd244';loc=next(x for x in cat.locations(nativekey) if cat.location(x)['type'][1].endswith('VisualTreeAsset'));cat=cm.Catalog(cat.add_key_location(key,loc,loc));newloc=cat.locations(key)[0];assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(W)
idx=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)=='GameWorldVisualTreeAssetPreload');ko,ls=cat.key_records[idx];locs=[x[0] for x in cat.array(ls,'I')]+[newloc];newset=cat.append(b''.join(struct.pack('<I',x) for x in locs),True);records=list(cat.key_records);records[idx]=(ko,newset);table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table);catout=bytes(cat.data)
# Restore the original lower strip, selecting the native tactical tile for its previous slot.
le=UnityPy.load(before[GAME/L]);lo={x.path_id:x for x in le.objects};lh={i:sha(x.get_raw_data()) for i,x in lo.items()};layoutpid=3901662990989568885;layout=lo[layoutpid].read_typetree();oldle={x.path_id:x for x in UnityPy.load(str(PREV/'backup-game'/L)).objects};oldlayout=oldle[layoutpid].read_typetree();slot=copy.deepcopy(oldlayout['m_gridComponents'][-1]);assert slot['m_elementID']=='CareerStats'
slot['m_elementID']='TacticalEffectiveness';slot['m_configDescriptions']=[{'m_FileID':3,'m_PathID':-7013958222950011377}];slot['m_configDescriptionKeys']=[];cfg=slot['m_gridElementConfigs'][0];cfg['Description']={'m_FileID':3,'m_PathID':-7013958222950011377};cfg['AssetRef']['m_AssetGUID']=nativekey;layout['m_gridComponents'].append(slot);layout['m_optionalSlices']['m_instantiationOrder'].append(len(layout['m_gridComponents'])-1)
placement=copy.deepcopy(oldlayout['m_placementBindings'][-1]);placement['m_elementID']='TacticalEffectiveness';layout['m_placementBindings'].append(placement);lo[layoutpid].save_typetree(layout)
cache=json.loads(before[CACHE]);oldcache=json.loads((PREV/'backup-cache'/CACHE.name).read_bytes());slot=copy.deepcopy(next(c for c in oldcache['m_gridComponents'] if c['m_elementID']=='TacticalEffectiveness'));slot['m_configDescriptions']=[{'instanceID':0}]
for cfg in slot['m_gridElementConfigs']:cfg['Description']={'instanceID':0};cfg['AssetRef']['m_AssetGUID']=nativekey
assert all(c['m_elementID']!='TacticalEffectiveness' for c in cache['m_gridComponents']);cache['m_gridComponents'].append(slot);cache['m_optionalSlices']['m_instantiationOrder'].append(len(cache['m_gridComponents'])-1)
if not any(x['m_elementID']=='TacticalEffectiveness' for x in cache['m_placementBindings']):cache['m_placementBindings'].append({'m_elementID':'TacticalEffectiveness','m_optionalConditions':[],'m_optionalConfigConditions':[]})
assert cache['m_gridComponents'][:-1]==json.loads(before[CACHE])['m_gridComponents']
outputs={W:e.file.save(packer='lz4'),L:le.file.save(packer='lz4')}
for n,b in outputs.items():
 check={x.path_id:x for x in UnityPy.load(b).objects};hs=hashes if n==W else lh;expected=changed if n==W else {layoutpid:layout};assert set(check)==set(hs)|set(expected)
 for i,h in hs.items():
  if i not in expected:assert sha(check[i].get_raw_data())==h,('native asset altered',n,i)
 for i,d in expected.items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 if n==W:
  for i in [-930000000001001,-930000000001003,newpid]:
   d=check[i].read_typetree();validate_ui(d,check[d['inlineSheet']['m_PathID']].read_typetree())
 (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catout);(OUT/'catalog.hash').write_bytes(hashlib.md5(catout).hexdigest().encode());(OUT/'saved-layout.json').write_text(json.dumps(cache,ensure_ascii=False,separators=(',',':')),'utf8')
for p,b in before.items():assert p.read_bytes()==b,('file changed during build',str(p))
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'pages':audit,'native_tactical_asset_unchanged':True,'private_tactical_frame_and_title_removed':True,'lower_strip_restored':True,'other_current_lower_cards_preserved':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}};(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared successfully; game must exit before install'
try:
 for n,b in outputs.items():
  for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
 for p,b in [(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',(OUT/'catalog.hash').read_bytes()),(CACHE,(OUT/'saved-layout.json').read_bytes())]:p.write_bytes(b);assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-cache' if p==CACHE else ('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin');restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'private_tactical_guid':key,'bottom_cards':len(cache['m_gridComponents']),'background_unchanged':True},ensure_ascii=True))

