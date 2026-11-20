"""Apply the requested Club overview layout to the current installed resources."""
from pathlib import Path
R=Path(__file__).resolve().parent
L='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','club-overview-native-site-').replace('NAMES=[W,G,M,F]','NAMES=[W,L]').replace('hours=-4','hours=-6')
exec(compile(boot,'current-club-bundles-and-codecs','exec'))
import re,subprocess,os
CK='<Configurations>k__BackingField'
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
banned={int(t['path_id']) for t in reserved}|{-910000000000146}
banned_names={t['name'].lower() for t in reserved}|{'tf patch'}
protected.update({p:sha(p.read_bytes()) for p in [R/'reserved-texture-ids.json',R/'current-custom-textures.json']})
new_objects=[]

def clone_object(n,source,pid,tree):
 assert pid not in objs[n] and pid not in banned
 ob=copy.copy(source);ob.path_id=pid;ob.data=None;ob._read_until=None
 ob.assets_file.objects[pid]=ob;objs[n][pid]=ob;ob.save_typetree(tree);changes[n][pid]=copy.deepcopy(tree)
 new_objects.append({'bundle':n,'path_id':str(pid),'name':tree.get('m_Name','')})
 return ob

def clone_doc(name,newname,pid,sid):
 source=Doc(W,name=name);d=copy.deepcopy(source.d);s=copy.deepcopy(source.s)
 d['m_Name']=newname;d['inlineSheet']['m_PathID']=sid;s['m_Name']=newname+'Style'
 clone_object(W,source.obj,pid,d);clone_object(W,objs[W][source.sid],sid,s)
 guid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/club-overview/'+newname).hex
 clones.append({'bundle':W,'guid':guid,'source_pid':source.obj.path_id,'pid':pid,'style':sid})
 return Doc(W,pid=pid,tree=d,style=s),guid

# The whole native row is drawn at half scale, including runtime-created action
# buttons. Twice the layout width compensates for the scale so the row stays full width.
compact,cguid=clone_doc('HumanActionsControlPanelBlock','ClubOverviewCompactActions',-990000000050000,-990000000050001)
for rid in [1001,1002]:compact.fill(rid)
compact.st(1002,[(131102,compact.enum('relative')),(458768,compact.enum('hidden'))])
compact.st(1004,[(131102,compact.enum('absolute')),(131105,compact.pct(200)),(131087,compact.pct(200)),(131089,compact.pct(-50)),(131104,compact.pct(-50)),(327681,[compact.num(.5),compact.num(.5)]),(131084,compact.num(0)),(131085,compact.num(0))])
compact.save()
original_actions=Doc(W,name='HumanActionsControlPanelBlock')
for i,x in original_actions.r.items():
 actual=copy.deepcopy(compact.r[i])
 if 'm_RuleIndex' in x.get('data',{}):actual['data']['m_RuleIndex']=x['data']['m_RuleIndex']
 assert actual==x,('Action binding or structure changed',i)

# Retain the existing grid entry/GUID and its expected club/team parameters.
# It now hosts the exact native other-club header and body templates.
host=Doc(W,name='ClubScreenOverviewBlock');donor=Doc(W,name='ClubSiteHeader')
keep={1000,1001,host.a(1001)['m_SerializedData']['rid'],-2}
host.d['references']['RefIds']=[x for x in host.d['references']['RefIds'] if x['rid'] in keep]
host.r=refs(host.d);host.a(1001)['m_Children']=[];host.d['m_Usings']=[]
host.st(1001,[(131084,host.num(1)),(131085,host.num(1)),(131096,host.px(0)),(131105,host.pct(100)),(131087,host.pct(100)),(131083,host.enum('column')),(458768,host.enum('hidden'))])
native_guids={}
meta=next(o.read_typetree() for o in objs[W].values() if o.type.name=='AssetBundle')
for name in ['ClubSiteHeader','ClubSiteBlock']:
 ob=find(W,name);guid=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':ob.path_id});native_guids[name]=guid
 rid=host.add(donor,1012,1001,'ClubOverview'+name)
 host.a(rid)['m_TemplateAlias']=name;host.data(rid)['templateId']=name
 host.d['m_Usings'].append({'alias':name,'path':guid,'asset':{'m_FileID':0,'m_PathID':0}})
 host.st(rid,[(131105,host.pct(100)),(131097,host.px(0)),(131096,host.px(0)),(131085,host.num(1 if name=='ClubSiteBlock' else 0)),(131084,host.num(1 if name=='ClubSiteBlock' else 0))])
 if name=='ClubSiteHeader':host.st(rid,[(131087,host.px(180)),(131096,host.px(180)),(131094,host.px(180))])
 else:host.st(rid,[(131087,{'m_ValueType':1,'valueIndex':2})])
host.save()

# Refine only Club's logical grid: double its vertical precision. The action row
# takes one new row (half the previous height), and its released space goes to
# the overview. The bottom tiles retain their original screen proportions.
description_map={};nextpid=-990000000050100;layout_audits=[]
def private_description(sourcepid):
 global nextpid
 if sourcepid in description_map:return description_map[sourcepid]
 src=objs[L][sourcepid];d=src.read_typetree();pid=nextpid;nextpid-=1
 d['m_Name']='ClubOverviewPrivate_'+d['m_Name']
 for cfg in d[CK]:
  cfg['Description']['m_PathID']=pid
  cfg['Size']['y']*=2
  if d['<ID>k__BackingField']=='HumanActionsControlPanelBlock':
   cfg['Size']['y']=1;cfg['AssetRef']['m_AssetGUID']=cguid
  elif d['<ID>k__BackingField']=='ClubScreenOverviewBlock':cfg['Size']['y']+=1
 clone_object(L,src,pid,d);description_map[sourcepid]=pid
 return pid

def remap_descs(v):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_FileID']==0 and v['m_PathID'] in description_map:v['m_PathID']=description_map[v['m_PathID']]
  else:
   for x in v.values():remap_descs(x)
 elif isinstance(v,(list,tuple)):
  for x in v:remap_descs(x)

for size in ['Large','Standard','Small']:
 ob=find(L,'ClubComposition-'+size);old=ob.read_typetree();tree=copy.deepcopy(old)
 for slot in tree['m_gridComponents']:
  ident=slot['m_elementID'];q=slot['m_location'];q['y']*=2;q['height']*=2
  for key in ['m_minSize','m_maxSize']:slot[key]['y']*=2
  if ident=='HumanActionsControlPanelBlock':q['height']=1;slot['m_minSize']['y']=slot['m_maxSize']['y']=1
  elif ident=='ClubScreenOverviewBlock':q['y']-=1;q['height']+=1;slot['m_minSize']['y']+=1
  for ptr in slot['m_configDescriptions']:ptr['m_PathID']=private_description(ptr['m_PathID'])
  slot['m_gridElementConfigs']=[]
  for ptr in slot['m_configDescriptions']:
   dt=changes[L][ptr['m_PathID']]
   slot['m_gridElementConfigs'].extend(copy.deepcopy(c) for c in dt[CK] if c['Size']=={'x':q['width'],'y':q['height']})
  assert slot['m_gridElementConfigs'],(size,ident,q)
 # Optional slices also use the new vertical unit while keeping their assets.
 for value in tree['m_optionalSlices'].values():
  if isinstance(value,list):
   for slot in value:
    if isinstance(slot,dict) and 'm_location' in slot:
     slot['m_location']['y']*=2;slot['m_location']['height']*=2
     for key in ['m_minSize','m_maxSize']:slot[key]['y']*=2
     for cfg in slot['m_gridElementConfigs']:cfg['Size']['y']*=2
 # The private grid element set isolates description additions from other pages.
 src=objs[L][tree['m_gridElementSet']['m_PathID']];gt=src.read_typetree();remap_descs(gt)
 gt['m_Name']='ClubOverviewPrivateSet_'+size;pid=nextpid;nextpid-=1
 clone_object(L,src,pid,gt);tree['m_gridElementSet']['m_PathID']=pid
 tree['m_compositionVersion']+=1
 cells=set()
 for slot in tree['m_gridComponents']:
  q=slot['m_location']
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):assert (x,y) not in cells;cells.add((x,y))
 original_bottom=min(x['m_location']['y'] for x in old['m_gridComponents'] if x['m_elementID'] not in ['ClubScreenOverviewBlock','HumanActionsControlPanelBlock'])
 for a,b in zip(old['m_gridComponents'],tree['m_gridComponents']):
  if a['m_location']['y']==original_bottom:
   assert b['m_location']['y']==a['m_location']['y']*2 and b['m_location']['height']==a['m_location']['height']*2
 ob.save_typetree(tree);changes[L][ob.path_id]=tree
 layout_audits.append({'name':tree['m_Name'],'before':{s['m_elementID']:s['m_location'] for s in old['m_gridComponents']},'after':{s['m_elementID']:s['m_location'] for s in tree['m_gridComponents']},'bottom_proportions_preserved':True})

def allptr(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'}:
   if v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():allptr(x,out)
 elif isinstance(v,(list,tuple)):
  for x in v:allptr(x,out)

# Register the new template and include direct/transitive references in preload.
for n in [W,L]:
 mo=next(o for o in objs[n].values() if o.type.name=='AssetBundle');mt=mo.read_typetree()
 for c in [c for c in clones if c['bundle']==n]:
  mt['m_Container'].append((c['guid'],{'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':c['pid']}}))
 for key,entry in mt['m_Container']:
  pid=entry['asset']['m_PathID']
  if pid not in changes[n] or entry['asset']['m_FileID']!=0:continue
  span=copy.deepcopy(mt['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
  allptr(changes[n][pid],span)
  if pid==host.obj.path_id:
   for name in native_guids:
    ent=next(v for k,v in mt['m_Container'] if k==native_guids[name])
    for ptr in mt['m_PreloadTable'][ent['preloadIndex']:ent['preloadIndex']+ent['preloadSize']]:
     if ptr not in span:span.append(copy.deepcopy(ptr))
  done=set();j=0
  while j<len(span):
   ptr=span[j];j+=1
   if ptr['m_FileID'] or ptr['m_PathID'] in done:continue
   done.add(ptr['m_PathID'])
   if ptr['m_PathID'] in changes[n]:allptr(changes[n][ptr['m_PathID']],span)
  if {'m_FileID':0,'m_PathID':pid} not in span:span.append({'m_FileID':0,'m_PathID':pid})
  entry.update(preloadIndex=len(mt['m_PreloadTable']),preloadSize=len(span));mt['m_PreloadTable'].extend(span)
 mt['m_Container'].sort(key=lambda kv:kv[0]);mo.save_typetree(mt);changes[n][mo.path_id]=mt

spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog=before[GAME.parent/'catalog.bin'];cat=cm.Catalog(catalog)
origguid=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':original_actions.obj.path_id})
loc=cat.locations(origguid)[0];catalog=cat.add_key_location(cguid,loc,loc);cat=cm.Catalog(catalog)
idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GameWorldVisualTreeAssetPreload')
ko,ls=cat.key_records[idx];locs=[v[0] for v in cat.array(ls,'I')]+cat.locations(cguid)
records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',p) for p in locs),True))
struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catalog=bytes(cat.data)

# Validate all native templates/functions referenced transitively by the newly
# hosted site against catalog type, actual object, and owning bundle dependency.
cat=cm.Catalog(catalog);catkeys=dict(cat.keys());asset_index={};loaded={}
for n in [W,G,L]:
 af=(env[n].assets[0] if n in env else UnityPy.load(str(GAME/n)).assets[0]);loaded[n]=af
 mo=next(o for o in af.objects.values() if o.type.name=='AssetBundle')
 mt=changes.get(n,{}).get(mo.path_id) or mo.read_typetree()
 for k,v in mt['m_Container']:
  if v['asset']['m_FileID']==0:
   pid=v['asset']['m_PathID'];ob=af.objects.get(pid)
   if ob is not None and ob.type.name=='MonoBehaviour' and 'm_Rules' in (changes.get(n,{}).get(pid) or ob.read_typetree()):continue
   asset_index[k]=(n,af,pid)
allloc={l for _,p in cat.keys() for (l,) in cat.array(p,'I')}
bundlelocs={}
for l in allloc:
 q=cat.location(l)
 if q['provider'].endswith('.AssetBundleProvider'):bundlelocs[q['internal'].replace('\\','/').split('/')[-1]]=l
audit=[];seen=set()
def guids(v):
 found=set()
 if isinstance(v,dict):
  for k,x in v.items():
   if k in ['m_guid','m_AssetGUID','path'] and isinstance(x,str) and re.fullmatch('[0-9a-f]{32}',x):found.add(x)
   else:found.update(guids(x))
 elif isinstance(v,(list,tuple)):
  for x in v:found.update(guids(x))
 return found
def audit_guid(guid):
 if guid in seen:return
 seen.add(guid)
 assert guid in catkeys,('GUID missing from catalog',guid)
 locations=[cat.location(x) for x in cat.locations(guid)]
 for q in locations:
  assert q['dependencies'],('No bundle dependency',guid)
 if guid not in asset_index:
  # Load the owning bundle lazily for factories, functions and helper templates.
  q=locations[0];name=next((n for n,l in bundlelocs.items() if l==q['dependencies'][0]),None)
  assert name and (GAME/name).exists(),('Owning bundle absent',guid,name)
  if name not in loaded:loaded[name]=UnityPy.load(str(GAME/name)).assets[0]
  af=loaded[name];mt=next(o.read_typetree() for o in af.objects.values() if o.type.name=='AssetBundle')
  for k,v in mt['m_Container']:
   if v['asset']['m_FileID']==0:
    pid=v['asset']['m_PathID'];ob=af.objects.get(pid)
    if ob is not None and ob.type.name=='MonoBehaviour' and 'm_Rules' in ob.read_typetree():continue
    asset_index[k]=(name,af,pid)
 assert guid in asset_index,('Bundle has no GUID object',guid)
 name,af,pid=asset_index[guid];assert pid in af.objects
 ob=af.objects[pid]
 if ob.type.name!='MonoBehaviour':return
 d=changes.get(name,{}).get(pid) or ob.read_typetree();typ='UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in d else ('SI.VisualScripting.VisualFunction' if 'm_nodes' in d else None)
 if not typ:return
 typed=[q for q in locations if q['type'][1]==typ]
 assert typed,('GUID registered with wrong resource type',guid,typ)
 for q in typed:assert q['dependencies'][0]==bundlelocs[name],(guid,name,q)
 audit.append({'guid':guid,'name':d['m_Name'],'type':typ,'bundle':name,'path_id':str(pid)})
 for child in guids(d):audit_guid(child)
for guid in [cguid,*native_guids.values()]:audit_guid(guid)

# Protect texture inventory and the retired IDs without editing either background bundle.
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'))
ba=UnityPy.load(str(GAME/'ui-backgrounds_assets_common.bundle')).assets[0]
assert banned.isdisjoint(ba.objects)
bm=next(o.read_typetree() for o in ba.objects.values() if o.type.name=='AssetBundle')
assert all(v['asset']['m_PathID'] not in banned and k.lower() not in banned_names for k,v in bm['m_Container'])
assert all(p['m_PathID'] not in banned for p in bm['m_PreloadTable'])
assert all(o.peek_name().lower() not in banned_names for o in ba.objects.values() if o.type.name=='Texture2D')
for t in registry['textures']:
 ob=ba.objects[int(t['path_id'])];assert ob.peek_name()==t['name'] and sha(ob.get_raw_data())==t['texture_sha256']

outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n]);assert banned.isdisjoint(check)
 for i,h in hashes[n].items():
  if i not in changes[n]:assert sha(check[i].get_raw_data())==h,('Unrelated object changed',n,i)
 for i,d in changes[n].items():assert check[i].read_typetree()==d,('Roundtrip failed',n,i)
 for doc in [x for x in documents if x.n==n]:validate_ui(check[doc.obj.path_id].read_typetree(),check[doc.sid].read_typetree())
 (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catalog);(OUT/'catalog.hash').write_bytes(hashlib.md5(catalog).hexdigest().encode('ascii'))
tx=[]
for folder in [GAME,SKIN]:
 for name in [W,L,'catalog.bin','catalog.hash']:
  p=(GAME.parent/name if folder==GAME and name.startswith('catalog.') else folder/name)
  b=(OUT/name).read_bytes();tx.append({'target':str(p),'source':str(OUT/name),'backup':str(OUT/('backup-game' if folder==GAME else 'backup-skin')/name),'before':sha(before[p]),'after':sha(b)})
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'request':'Club overview: actions 50% height and content scale; native other-club header and four-column overview in main area','changes':{n:{str(i):d.get('m_Name','AssetBundle') for i,d in ds.items()} for n,ds in changes.items()},'clones':clones,'new_objects':new_objects,'layouts':layout_audits,'catalog_audits':audit,'reserved_and_deleted_texture_ids_absent':True,'current_textures_verified':len(registry['textures']),'unrelated_objects_byte_identical':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
print(json.dumps({'prepared':True,'output':str(OUT),'changed_objects':{n:len(v) for n,v in changes.items()},'catalog_templates_and_functions_checked':len(audit)},ensure_ascii=False),flush=True)
