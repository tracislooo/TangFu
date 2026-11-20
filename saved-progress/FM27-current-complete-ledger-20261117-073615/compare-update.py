"""Compare a future native update with a complete ledger; read-only, never installs."""
from pathlib import Path
import sys,json,gzip,hashlib,argparse,collections
R=Path(__file__).resolve().parent
for q in [R/'.codex-deps',Path('G:/Doc/ChatGPT/New project/.codex-deps')]:
 if q.exists():sys.path.insert(0,str(q));break
import UnityPy
pa=argparse.ArgumentParser();pa.add_argument('--record',type=Path,required=True);pa.add_argument('--updated-aa',type=Path,required=True);pa.add_argument('--output',type=Path,required=True);pa.add_argument('--mode',choices=['current-game','independent-main'],default='current-game');a=pa.parse_args()
if a.output.resolve().is_relative_to(a.updated_aa.resolve()):raise ValueError('Write reports outside the game aa directory')
def read(p):
 if p.name.endswith('.gz'):
  with gzip.open(p,'rt',encoding='utf8') as f:return json.load(f)
 return json.loads(p.read_text('utf8'))
def ph(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def payload(o):
 t=o.read()
 if not t.image_data and (t.m_StreamData is None or t.m_StreamData.size==0):return b''
 return t.get_image_data()
m=read(a.record/'manifest.json');base=read(a.record/'baseline-index.json');bi={r['bundle']:r for r in base['bundles']};folder=a.updated_aa/'StandaloneWindows64';current={p.name:p for p in folder.glob('*.bundle')};hashes={n:ph(p) for n,p in current.items()};allfiles=[{'bundle':n,'status':'added_native_bundle' if n not in bi else 'native_unchanged' if h==bi[n]['sha256'] else 'native_changed','sha256':h} for n,h in hashes.items()];results=[]
for row in m['bundles']:
 if row['mode']!=a.mode or not row['objects']:continue
 n=row['bundle'];out={'bundle':n,'objects':[]};results.append(out)
 if n not in current:out['status']='bundle_missing';continue
 if hashes[n]==row['original_sha256']:out['status']='native_bundle_unchanged_reuse_candidate';continue
 if hashes[n]==row['modified_sha256']:out['status']='matches_archived_modified_bundle_check_native_assumption';continue
 out['status']='native_bundle_changed_review_required';e=UnityPy.load(str(current[n]));obs={(o.assets_file.name.lower(),str(o.path_id)):o for o in e.objects};byid=collections.defaultdict(list);bykey=collections.defaultdict(list)
 for o in e.objects:
  byid[str(o.path_id)].append(o)
  if o.type.name=='AssetBundle':
   for k,v in o.read_typetree()['m_Container']:
    ptr=v['asset']
    if ptr['m_FileID']==0:
     match=obs.get((o.assets_file.name.lower(),str(ptr['m_PathID'])))
     if match:bykey[k].append(match)
 for rec in row['objects']:
  r={'path_id':rec['path_id'],'name':rec['name'],'type':rec['type'],'original_change':rec['status'],'record':rec['detail']};out['objects'].append(r);o=obs.get((rec['cab'],rec['path_id']));identity='cab_and_path_id'
  if o is None:
   candidates={}
   for k in rec.get('native_keys',[])+rec.get('modified_keys',[]):
    for t in bykey.get(k,[]):
     if t.type.name==rec['type']:candidates[(t.assets_file.name,str(t.path_id))]=t
   if len(candidates)==1:o=next(iter(candidates.values()));identity='container_key_rematched_requires_reference_rewrite'
   elif len(byid.get(rec['path_id'],[]))==1:
    t=byid[rec['path_id']][0]
    if t.type.name==rec['type']:o=t;identity='path_id_only_cab_changed_requires_review'
  r['identity_match']=identity
  if o is None:r['status']='custom_addition_available_check_dependencies' if rec['status']=='added' else 'native_identity_missing_or_ambiguous';continue
  if o.type.name!=rec['type']:r['status']='object_type_conflict';continue
  h=hashlib.sha256(o.get_raw_data()).hexdigest();r['updated_path_id']=str(o.path_id);r['updated_cab']=o.assets_file.name.lower();r['updated_raw_sha256']=h
  if 'texture_payload' in rec:
   try:r['updated_texture_payload_sha256']=hashlib.sha256(payload(o)).hexdigest()
   except Exception as ex:r['status']='stream_payload_read_error';r['error']=str(ex);continue
  before_ok=h==rec['before_raw_sha256'];after_ok=h==rec['after_raw_sha256']
  if 'texture_payload' in rec:
   before_ok=before_ok and r['updated_texture_payload_sha256']==rec['texture_payload']['native_sha256'];after_ok=after_ok and r['updated_texture_payload_sha256']==rec['texture_payload']['modified_sha256']
  if after_ok:r['status']='object_already_matches_modified';continue
  if rec['status']=='added':r['status']='custom_id_or_key_collision';continue
  if before_ok:r['status']='native_object_unchanged_migration_candidate' if identity=='cab_and_path_id' else 'native_bytes_unchanged_but_identity_remap_required';continue
  if rec['status']=='deleted':r['status']='deletion_conflict_native_object_changed';continue
  r['status']='native_object_changed_three_way_review';p=a.record/rec['detail']/'changes.json.gz'
  if p.exists():r['recorded_field_operations']=len(read(p))
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'mode':a.mode,'record':str(a.record),'updated_aa':str(a.updated_aa),'read_only':True,'all_native_files':allfiles,'removed_native_bundles':sorted(set(bi)-set(current)),'modified_bundle_reviews':results,'limits':'Candidates are not a verified build. Matching GUIDs/keys or raw object bytes does not validate schemas, all reference rewrites, array identity, catalog extraData, preload closures, streamed payloads of non-Texture2D resources, or runtime behavior. Preserve new official changes; merge conflicting fields manually; rebase sidebar only after the new main skin.'},ensure_ascii=False,indent=2),'utf8');print(str(a.output))
