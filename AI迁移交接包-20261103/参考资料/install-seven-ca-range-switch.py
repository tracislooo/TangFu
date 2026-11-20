from pathlib import Path
import ast,copy,json,struct,hashlib,importlib.util,zlib
boot=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8').split('ROW=-940000000006000;')[0].replace('photo-up3-titled-pros-cons-tactics-thirds-','seven-ca-range-switch-')
exec(compile(boot,'backup-and-ui-helpers','exec'))
B='ui-backgrounds_assets_common.bundle';V59=R/'七张CA更新及新增150和170-V59-20261027';vm_path=V59/'图片及引用校验记录.json';vm=json.loads(vm_path.read_text('utf8'))
registry_path=R/'current-custom-textures.json';registry_before=registry_path.read_bytes();current=json.loads(registry_before);latest=json.loads((V59/'当前175张有效图片恢复来源.json').read_text('utf8'))
banned=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];bannedids={int(x['path_id']) for x in banned};bannednames={x['name'].lower() for x in banned}
bg_bytes=(V59/B).read_bytes();assert all(sha(bg_bytes)==x['after_sha256'] for x in vm['install_files'])
for folder in [GAME,SKIN]:
 p=folder/B;data=p.read_bytes();allowed={x['before_sha256'] for x in vm['install_files']}|{sha(bg_bytes)};assert sha(data) in allowed,('unexpected installed backgrounds version',str(p));before[p]=data;protected.pop(p,None);(OUT/('backup-game' if folder==GAME else 'backup-skin')/B).write_bytes(data)
be=UnityPy.load(bg_bytes);ba=be.assets[0];bo={o.path_id:o for o in be.objects};bm=next(o.read_typetree() for o in be.objects if o.type.name=='AssetBundle')
assert len(latest['textures'])==latest['active_custom_texture_count']==175 and bannedids.isdisjoint(bo)
assert not any(o.type.name=='Texture2D' and o.peek_name().lower() in bannednames for o in bo.values())
assert all(p['m_PathID'] not in bannedids for p in bm['m_PreloadTable'])
assert all(k.lower() not in bannednames and v['asset']['m_PathID'] not in bannedids for k,v in bm['m_Container'])
for t in latest['textures']:assert bo[int(t['path_id'])].peek_name()==t['name']
cards={o.peek_name():o.path_id for o in bo.values() if o.type.name=='Texture2D' and o.peek_name() in ['CA000','CA120','CA140','CA150','CA160','CA170','CA180']}
assert cards=={'CA000':-910000000000003,'CA120':-910000000000004,'CA140':-910000000000005,'CA160':-910000000000006,'CA180':-910000000000007,'CA150':-910000000000143,'CA170':-910000000000144}
limits=[109,129,139,149,159,169];order=['CA120','CA000','CA160','CA140','CA150','CA170','CA180']
serial=lambda r,i:r[r[i]['data']['m_SerializedData']['rid']]
def decode(raw):
 b=bytes(raw);p=1;out=[]
 for _ in range(b[0]):
  size=struct.unpack_from('<I',b,p)[0];p+=4;out.append(b[p:p+size]);p+=size
 assert p==len(b);return out
def encode(a):return list(bytes([len(a)])+b''.join(struct.pack('<I',len(v))+v for v in a))
def f32all(v):
 if isinstance(v,float):return struct.unpack('<f',struct.pack('<f',v))[0]
 if isinstance(v,list):return [f32all(x) for x in v]
 if isinstance(v,dict):return {k:f32all(x) for k,x in v.items()}
 return v
audits=[]
for bn in [W,G]:
 for pid,obj in list(objs[bn].items()):
  if obj.type.name!='MonoBehaviour':continue
  doc=obj.read_typetree()
  if 'inlineSheet' not in doc:continue
  rr=refs(doc)
  roots=[i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement' and serial(rr,i)['data'].get('name')=='ReportCAAbove119Switch']
  if not roots:continue
  assert len(roots)==1;root=roots[0];old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];assert doc['inlineSheet']['m_FileID']==0;sheet=objs[bn][sid].read_typetree()
  switches=[];images={};oldtree=set()
  def walk(i):
   oldtree.add(i);oldtree.add(rr[i]['data']['m_SerializedData']['rid']);a=rr[i]['data'];s=sd(i)
   if a['m_FullTypeName']=='SI.Bindable.BindableSwitchElement':
    switches.append(i)
    for c in a['m_Children']:walk(c['rid'])
   else:
    assert not a['m_Children'];key=s['name'].removeprefix('ReportCACardImage');assert key in cards;images[key]=i
  walk(root);assert len(switches)==4 and set(images)==set(['CA000','CA120','CA140','CA160','CA180'])
  fid=next(i+1 for i,x in enumerate(obj.assets_file.externals) if x.name.lower()==ba.name.lower())
  next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;assert next_id+8<2147483647
  new=[]
  def clone(i):
   global next_rid,next_id
   a=copy.deepcopy(old[i]);s=copy.deepcopy(serial(old,i));a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2;a['data'].update(m_Id=next_id,m_Children=[],m_SerializedData={'rid':s['rid']});s['data']['uxmlAssetId']=next_id;next_id+=1
   rr[a['rid']]=a;rr[s['rid']]=s;new.extend([a,s]);return a['rid']
  switches += [clone(root),clone(root)]
  for name in ['CA150','CA170']:
   i=clone(images['CA140']);images[name]=i;sd(i).update(name='ReportCACardImage'+name,name_UxmlAttributeFlags=1)
   ptr={'m_FileID':fid,'m_PathID':cards[name]}
   if ptr not in sheet['assets']:sheet['assets'].append(ptr)
   override(rr[i]['data'],[prop(458753,{'m_ValueType':6,'valueIndex':sheet['assets'].index(ptr)})])
  for j,(i,limit) in enumerate(zip(switches,limits)):
   s=sd(i);a=decode(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert struct.unpack_from('<i',a[0],len(a[0])-4)[0]==4;assert a[2].endswith(b'person.PlayerCurrentAbility');a[1]=a[1][:-4]+struct.pack('<i',limit);s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(a);s.update(name=f'ReportCAAbove{limit}Switch',name_UxmlAttributeFlags=1)
   low=images[order[j]];high=switches[j+1] if j<5 else images['CA180'];rr[i]['data']['m_Children']=[{'rid':low},{'rid':high}];rr[low]['data']['m_Parent']={'rid':i};rr[high]['data']['m_Parent']={'rid':i}
  doc['references']['RefIds'].extend(new);doc['m_ContentHash']=struct.unpack('<i',struct.pack('<I',zlib.crc32((doc['m_Name']+'-seven-ca-custom-ranges-v1').encode())))[0]
  for i,r in old.items():
   if i not in oldtree:assert rr[i]==r,('unrelated UI record changed',bn,pid,i)
  assert root==switches[0] and rr[root]['data']['m_Parent']==old[root]['data']['m_Parent']
  def selected(raw):
   i=root
   while rr[i]['data']['m_FullTypeName']=='SI.Bindable.BindableSwitchElement':
    args=decode(sd(i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack_from('<i',args[1],len(args[1])-4)[0];i=rr[i]['data']['m_Children'][int(raw is not None and raw>limit)]['rid']
   p=next(p for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==458753);ptr=sheet['assets'][p['m_Values'][0]['valueIndex']];assert ptr['m_FileID']==fid
   return bo[ptr['m_PathID']].peek_name()
  cases=[None,-2147483648]+list(range(-1,202))
  for ca in cases:
   expected=order[sum(ca is not None and ca>n for n in limits)];assert selected(ca)==expected,(doc['m_Name'],ca,selected(ca),expected)
  sheet=f32all(sheet);validate_ui(doc,sheet);obj.save_typetree(doc);objs[bn][sid].save_typetree(sheet);changed[bn][pid]=doc;changed[bn][sid]=sheet
  audits.append({'bundle':bn,'name':doc['m_Name'],'path_id':str(pid),'inlineStyle':str(sid),'verified_CA_cases':len(cases),'background_file_id':fid})
assert len(audits)>=9 and any(x['name']=='TooltipFCPlayerCard' for x in audits)
# Append the two already-existing background texture pointers to each changed page's preload span.
for bn in [W,G]:
 if not changed[bn]:continue
 metaobj=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree()
 for row in [a for a in audits if a['bundle']==bn]:
  entry=next(v for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':int(row['path_id'])});span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
  for name in ['CA150','CA170']:
   p={'m_FileID':row['background_file_id'],'m_PathID':cards[name]}
   if p not in span:span.append(p)
  entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
 metaobj.save_typetree(meta);changed[bn][metaobj.path_id]=meta
outputs={B:bg_bytes}
for bn in [W,G]:
 if not changed[bn]:continue
 data=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[bn].keys()
 for i,h in hashes[bn].items():
  if i not in changed[bn]:assert sha(saved[i].get_raw_data())==h,('unrelated object changed',bn,i)
 for i,d in changed[bn].items():assert saved[i].read_typetree()==d,('roundtrip failed',bn,i)
 outputs[bn]=data
# Addressables validation covers all current UI templates and custom functions in the affected bundles.
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);catalog_audits=[]
for catpath in [GAME.parent/'catalog.bin',SKIN/'catalog.bin']:
 c=cm.Catalog(catpath.read_bytes());key_locations={k:[x for x, in c.array(p,'I')] for k,p in c.keys() if isinstance(k,str)};keys=set(key_locations);locations={x for locs in key_locations.values() for x in locs}
 def bundleloc(n):return next(l for l in locations if c.location(l)['provider'].endswith('.AssetBundleProvider') and c.location(l)['internal'].endswith('\\'+n))
 bloc=bundleloc(B);count=0
 for bn in [W,G]:
  own=bundleloc(bn);meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle')
  for key,entry in meta['m_Container']:
   if len(key)!=32 or entry['asset']['m_FileID']!=0:continue
   ob=objs[bn].get(entry['asset']['m_PathID'])
   if ob is None or ob.type.name!='MonoBehaviour':continue
   d=ob.read_typetree();kind='SI.VisualScripting.VisualFunction' if 'm_nodes' in d else ('UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in d else None)
   if not kind:continue
   assert key in keys,('missing catalog registration',key,d.get('m_Name'))
   matching=[c.location(loc) for loc in key_locations[key] if c.location(loc)['type'][1]==kind];assert matching,('missing matching catalog type',key,kind)
   for v in matching:
    assert v['dependencies'][0]==own,(key,kind,v)
    if kind.endswith('VisualTreeAsset'):assert bloc in v['dependencies'],('missing background dependency',key)
   count+=1
 catalog_audits.append({'catalog':str(catpath),'registered_assets_checked':count,'unchanged_sha256':sha(catpath.read_bytes())})
for name,data in outputs.items():(OUT/name).write_bytes(data)
report={'installed':False,'runtime_verified':False,'mapping':[{'card':n,'min':lo,'max':hi} for n,lo,hi in [('CA120',1,109),('CA000',110,129),('CA160',130,139),('CA140',140,149),('CA150',150,159),('CA170',160,169),('CA180',170,200)]],'zero_or_missing':'CA120','used_prebuilt_V59_backgrounds':True,'new_textures_created':0,'existing_ids_preserved':True,'retired70_absent':True,'active_textures':175,'components':audits,'catalog_audits':catalog_audits,'rating_functions_and_non_card_UI_unchanged':True,'after_sha256':{n:sha(d) for n,d in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
pending={folder/name:data for name,data in outputs.items() for folder in [GAME,SKIN]}
registry_out=json.dumps(latest,ensure_ascii=False,indent=2).encode('utf8');vm_out=copy.deepcopy(vm);vm_out.update(installed=True,installed_hash_verified=True,installed_by_seven_ca_switch=str(OUT/'manifest.json'))
pending[registry_path]=registry_out;pending[vm_path]=json.dumps(vm_out,ensure_ascii=False,indent=2).encode('utf8')
for p in [registry_path,vm_path]:before[p]=p.read_bytes();(OUT/('backup-registry' if p==registry_path else 'backup-V59-record')).mkdir(exist_ok=True);(OUT/('backup-registry' if p==registry_path else 'backup-V59-record')/p.name).write_bytes(before[p])
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first.' }"]
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin' if p.parent==SKIN else 'backup-registry' if p==registry_path else 'backup-V59-record'
 restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,data in pending.items():p.write_bytes(data);assert p.read_bytes()==data
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,data in before.items():p.write_bytes(data)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'components':len(audits),'CA_checks':sum(x['verified_CA_cases'] for x in audits),'background_reused_V59':True,'new_images_created':0,'active_textures':175}))
