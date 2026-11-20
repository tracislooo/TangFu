"""Read installed resources and historical evidence; write only into a new audit folder."""
from pathlib import Path
import sys,json,hashlib,datetime,collections,re,gc,shutil,importlib.util
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
O=R/'saved-progress'/('FM27-current-state-audit-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
O.mkdir(parents=True)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,default=str),'utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
loc=read(R/'current-game-location.json')
roots={'game':Path(loc['bundle_root']),'skin':Path(loc['skin_packages'])}
errors=[];indexes={};patches=collections.defaultdict(set);broken=[]
def scan(v,index,key=''):
 if isinstance(v,dict):
  for k,x in v.items():scan(x,index,k)
 elif isinstance(v,list):
  for x in v:scan(x,index,key)
 elif isinstance(v,str) and re.match(r'^[A-Za-z]:[/\\]',v):
  p=Path(v)
  if not p.is_relative_to(R):return
  if p.exists():
   q=p if p.is_dir() else p.parent
   if (q/'manifest.json').exists() or (q/'transaction.json').exists():patches[q].add(index)
  elif key not in {'obsolete_game_root'}:broken.append({'index':index,'key':key,'path':v})
for p in sorted(R.glob('current-*.json')):
 try:
  v=read(p);indexes[p.name]=v;scan(v,p.name);shutil.copy2(p,O/'indexes'/p.name) if (O/'indexes').exists() else ((O/'indexes').mkdir(),shutil.copy2(p,O/'indexes'/p.name))
 except Exception as e:errors.append({'stage':'index','path':str(p),'error':str(e)})
# Recent unindexed transactions may supersede an old current-* pointer.
for p in R.iterdir():
 if p.is_dir() and re.search(r'202611(17|18|19)',p.name) and (p/'transaction.json').exists():patches[p].add('(recent transaction; may be uninstalled)')
dump(O/'indexes-and-records.json',{'indexes':list(indexes),'patches':{str(k):sorted(v) for k,v in patches.items()},'broken_paths':broken})
inventory=[];hashes={};stats={}
for mode,root in roots.items():
 files=list(root.glob('*.bundle'))+[p for p in (root.parent if mode=='game' else root).iterdir() if p.is_file() and (p.name.startswith('catalog.') or p.name=='settings.json')]
 print('Inventory',mode,len(files),flush=True)
 for p in sorted(set(files)):
  s=p.stat();h=sha(p);hashes[str(p)]=h;stats[str(p)]=(s.st_size,s.st_mtime_ns)
  inventory.append({'mode':mode,'path':str(p),'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':h})
dump(O/'installed-inventory.json',inventory)
print('Inventory complete',len(inventory),flush=True)
cache={}
def summary(p,known=None):
 p=Path(p);h=known or hashes.get(str(p)) or sha(p)
 if h in cache:return cache[h]
 cp=O/'object-cache'/(h+'.json')
 if cp.exists():v=read(cp);cache[h]=v;return v
 env=UnityPy.load(str(p));objects={};containers=[];preloads=[]
 for o in env.objects:
  pid=str(o.path_id)
  if pid in objects:raise ValueError('ambiguous multi-CAB path ID '+str(p)+' '+pid)
  try:n=o.peek_name() or ''
  except Exception:n=''
  row={'name':n,'type':o.type.name,'sha256':hashlib.sha256(o.get_raw_data()).hexdigest(),'cab':o.assets_file.name.lower()}
  objects[pid]=row
  if o.type.name=='AssetBundle':
   t=o.read_typetree()
   containers.extend({'key':k,'pid':str(v['asset']['m_PathID']),'fid':v['asset']['m_FileID']} for k,v in t['m_Container'])
   preloads.extend({'pid':str(v['m_PathID']),'fid':v['m_FileID']} for v in t['m_PreloadTable'])
 v={'sha256':h,'objects':objects,'containers':containers,'preloads':preloads};dump(cp,v);cache[h]=v
 del env;gc.collect();return v
current={}
ledger=Path(indexes['current-complete-bundle-ledger.json']['archive']);lm=read(ledger/'manifest.json');ledger_results=[]
for b in lm['bundles']:
 if not b['objects']:continue
 mode='game' if b['mode']=='current-game' else 'skin';p=roots[mode]/b['bundle']
 print('Ledger',mode,b['bundle'],flush=True)
 if not p.exists():errors.append({'stage':'ledger','path':str(p),'error':'bundle missing'});continue
 try:v=summary(p);current[(mode,p.name)]=v
 except Exception as e:errors.append({'stage':'ledger','path':str(p),'error':str(e)});continue
 for x in b['objects']:
  ob=v['objects'].get(x['path_id']);expected=x.get('after_raw_sha256')
  status='historical_deletion_still_absent' if x['status']=='deleted' and ob is None else 'historical_deletion_now_present' if x['status']=='deleted' else 'historical_object_absent' if ob is None else 'same_object_bytes' if ob['sha256']==expected else 'same_as_old_native' if ob['sha256']==x.get('before_raw_sha256') else 'object_changed_requires_review'
  ledger_results.append({'mode':mode,'bundle':p.name,'pid':x['path_id'],'name':x['name'],'type':x['type'],'historical_change':x['status'],'status':status,'current':ob,'record':x['detail']})
dump(O/'ledger-object-comparison.json',ledger_results)
print('Ledger comparison complete',dict(collections.Counter(x['status'] for x in ledger_results)),flush=True)
transactions=[]
for patch,refs in sorted(patches.items()):
 tp=patch/'transaction.json';manifest={}
 try:
  if (patch/'manifest.json').exists():manifest=read(patch/'manifest.json')
  if not tp.exists():continue
  t=read(tp);rows=[]
  if isinstance(t,list):rows=t
  elif isinstance(t,dict) and isinstance(t.get('sources'),dict):
   rows=[{'target':k,'source':v,'backup':t.get('before',{}).get(k)} for k,v in t['sources'].items()]
  elif isinstance(t,dict) and isinstance(t.get('files'),list):rows=t['files']
  for row in rows:
   if not isinstance(row,dict) or not row.get('target') or not row.get('source'):continue
   target=Path(row['target']);mode=next((k for k,r in roots.items() if target.parent==r),None)
   if mode is None or target.suffix!='.bundle':continue
   transactions.append({'patch':str(patch),'indexes':sorted(refs),'mode':mode,'target':str(target),'source':row['source'],'backup':row.get('backup'),'expected_hash':row.get('after'),'installed_claim':manifest.get('installed'),'restored_claim':manifest.get('restored')})
 except Exception as e:errors.append({'stage':'transaction','path':str(tp),'error':str(e)})
dump(O/'transaction-inputs.json',transactions)
results=[]
for i,t in enumerate(transactions):
 print('Transaction',i+1,'/',len(transactions),Path(t['patch']).name,t['mode'],Path(t['target']).name,flush=True)
 r={**t};results.append(r);source=Path(t['source']);backup=Path(t['backup']) if t['backup'] else None
 try:
  if not source.exists():r['status']='evidence_source_missing';continue
  sh=sha(source);r['source_sha256']=sh
  if t['expected_hash'] and sh!=t['expected_hash']:r['status']='evidence_hash_mismatch';continue
  if hashes.get(t['target'])==sh:r['status']='whole_bundle_matches';continue
  if backup is None or not backup.exists():r['status']='no_before_bundle_for_object_diff';continue
  a=summary(backup);b=summary(source,sh);c=current.get((t['mode'],Path(t['target']).name))
  if c is None:c=summary(t['target']);current[(t['mode'],Path(t['target']).name)]=c
  changed=[]
  for pid in a['objects'].keys()|b['objects'].keys():
   before=a['objects'].get(pid);after=b['objects'].get(pid)
   if (before or {}).get('sha256')==(after or {}).get('sha256'):continue
   if (after or before)['type']=='AssetBundle':continue
   now=c['objects'].get(pid)
   status='retained' if (now or {}).get('sha256')==(after or {}).get('sha256') else 'back_to_before' if (now or {}).get('sha256')==(before or {}).get('sha256') else 'absent' if now is None else 'changed_since_patch'
   changed.append({'pid':pid,'name':(after or before)['name'],'type':(after or before)['type'],'change':'added' if before is None else 'deleted' if after is None else 'modified','status':status,'before':before,'after':after,'current':now})
  r['objects']=changed;r['counts']=dict(collections.Counter(x['status'] for x in changed));r['status']='all_changed_objects_retained' if all(x['status']=='retained' for x in changed) else 'object_review_required'
 except Exception as e:r['status']='error';r['error']=str(e);errors.append({'stage':'transaction-compare','path':str(source),'error':str(e)})
 dump(O/'transaction-object-comparison.json',results)
# Actual texture identities and permanently retired IDs, including container/preload occupancy.
reg=read(R/'current-custom-textures.json');ret=read(R/'reserved-texture-ids.json')['reserved_textures']+reg.get('removed_textures',[])
forbidden={str(x['path_id']) for x in ret}|{'-910000000000146','-910000000000001','-910000000000002'}
textures=[];retired=[];state=[]
for mode,root in roots.items():
 bg=root/'ui-backgrounds_assets_common.bundle';v=summary(bg)
 for x in reg['textures']:
  ob=v['objects'].get(str(x['path_id']));textures.append({'mode':mode,'name':x['name'],'pid':str(x['path_id']),'status':'identity_present' if ob and ob['type']=='Texture2D' and ob['name']==x['name'] else 'missing_or_wrong_identity','actual':ob})
 for name in ['ui-backgrounds_assets_common.bundle','ui-backgrounds_assets_.bundle']:
  s=summary(root/name)
  for pid in forbidden:
   if pid in s['objects']:retired.append({'mode':mode,'bundle':name,'pid':pid,'where':'object'})
   for c in s['containers']+s['preloads']:
    if c['fid']==0 and c['pid']==pid:retired.append({'mode':mode,'bundle':name,'pid':pid,'where':'container/preload'})
 w=summary(root/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')
 state.append({'mode':mode,'sidebar_named_objects':[{'pid':pid,**ob} for pid,ob in w['objects'].items() if 'tfreferencebookmark' in ob['name'].lower()], 'background_picker_named_objects':[{'pid':pid,**ob} for pid,ob in w['objects'].items() if any(z in ob['name'].lower() for z in ['backgroundthumbnail','backgroundpicker'])]})
dump(O/'texture-identity-check.json',{'active_registry_count':len(reg['textures']),'textures':textures,'forbidden_occupancy':retired,'ui_named_objects':state})
# Check all GUID registrations whose actual objects are present in the inspected bundles.
spec=importlib.util.spec_from_file_location('catalog_audit',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog_results=[]
for mode,root in roots.items():
 cp=(root.parent if mode=='game' else root)/'catalog.bin';cat=cm.Catalog(cp.read_bytes());keys=dict(cat.keys());checks=[]
 for (m,name),v in current.items():
  if m!=mode:continue
  label=next((b for a,b in [('gameworldvisualtree','GameWorld'),('globalvisualtree','Global'),('matchvisualtree','Match'),('introvisualtree','Intro'),('fantasydraftvisualtree','FantasyDraft')] if a in name),None)
  for entry in v['containers']:
   key=entry['key'];ob=v['objects'].get(entry['pid'])
   if not ob or entry['fid'] or not re.fullmatch(r'[a-f0-9]{32}',key):continue
   if key not in keys:
    checks.append({'key':key,'bundle':name,'pid':entry['pid'],'name':ob['name'],'status':'container_guid_missing_catalog'});continue
   for (lid,) in cat.array(keys[key],'I'):
    l=cat.location(lid)
    if not (l['type'][1].endswith('VisualTreeAsset') or l['type'][1].endswith('VisualFunction')):continue
    owner=cat.location(l['dependencies'][0])['internal'].replace('\\','/').split('/')[-1] if l['dependencies'] else None
    status='registered_owner_matches' if owner==name else 'catalog_owner_mismatch'
    if label and l['type'][1].endswith('VisualTreeAsset') and status=='registered_owner_matches':
     k=label+'VisualTreeAssetPreload'
     if k not in keys or (lid,) not in cat.array(keys[k],'I'):status='not_in_owner_preload_label'
    checks.append({'key':key,'bundle':name,'pid':entry['pid'],'name':ob['name'],'type':l['type'][1],'owner':owner,'status':status})
 catalog_results.append({'mode':mode,'counts':dict(collections.Counter(x['status'] for x in checks)),'checks':checks})
dump(O/'catalog-registration-check.json',catalog_results)
changed=[]
for p,(size,mtime) in stats.items():
 s=Path(p).stat()
 if (s.st_size,s.st_mtime_ns)!=(size,mtime) and sha(p)!=hashes[p]:changed.append(p)
dump(O/'audit-summary.json',{'output':str(O),'installed_files':len(inventory),'indexes':len(indexes),'patch_dirs':len(patches),'transaction_bundle_checks':len(results),'transaction_counts':dict(collections.Counter(x['status'] for x in results)),'ledger_counts':dict(collections.Counter(x['status'] for x in ledger_results)),'texture_counts':dict(collections.Counter(x['status'] for x in textures)),'forbidden_occupancy':len(retired),'catalog_counts':[{k:v for k,v in x.items() if k!='checks'} for x in catalog_results],'source_files_changed_during_audit':changed,'errors':errors,'broken_index_paths':len(broken),'writes_to_installations':False,'runtime_verified':False})
print('DONE',O,flush=True)
