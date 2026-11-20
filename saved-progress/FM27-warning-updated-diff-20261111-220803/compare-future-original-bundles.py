"""Read-only three-way update report. Never writes game resources."""
from pathlib import Path
import sys,json,hashlib,argparse
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
p=argparse.ArgumentParser();p.add_argument('--record',type=Path,required=True);p.add_argument('--updated-aa',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.resolve().is_relative_to(a.updated_aa.resolve()):raise ValueError('Output must be outside game aa')
m=json.loads((a.record/'manifest.json').read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest();out=[]
def get(t,path):
 for k in path.split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');t=t[int(k)] if isinstance(t,list) else t[k]
 return t
for r in m['bundles']:
 if not r['objects']:continue
 path=a.updated_aa/'StandaloneWindows64'/r['bundle'];entry={'mode':r['mode'],'bundle':r['bundle'],'objects':[]};out.append(entry)
 if not path.exists():entry['status']='bundle_missing';continue
 entry['updated_sha256']=sha(path.read_bytes())
 if entry['updated_sha256']==r['original_sha256']:entry['status']='original_unchanged';continue
 entry['status']='review_object_changes';e=UnityPy.load(str(path));obs={(o.assets_file.name.lower(),str(o.path_id)):o for o in e.objects}
 for rec in r['objects']:
  o=obs.get((rec['cab'],rec['path_id']));d={'path_id':rec['path_id'],'name':rec['name'],'kind':rec['status']};entry['objects'].append(d)
  if rec['status']=='added':d['status']='new_id_available_review_dependencies' if o is None else 'id_collision_or_already_present';continue
  if o is None:d['status']='identity_missing_rematch_by_guid_or_name';continue
  h=sha(o.get_raw_data())
  if h==rec['before_raw_sha256']:d['status']='original_object_unchanged';continue
  if h==rec['after_raw_sha256']:d['status']='modified_object_already_present';continue
  if rec['status']=='deleted':d['status']='deletion_conflict_native_object_changed';continue
  try:
   t=o.read_typetree();changes=json.loads((a.record/rec['detail']/'changes.json').read_text('utf8'));checks=[]
   for c in changes:
    state='review_structure_or_binary'
    if c['op']=='replace':
     try:
      v=get(t,c['path']);state='safe_field_candidate' if v==c['before'] else 'already_applied' if v==c['after'] else 'conflict'
     except (KeyError,IndexError,TypeError,ValueError):state='path_missing'
    checks.append({'path':c['path'],'status':state})
   d['status']='field_review_required';d['fields']=checks
  except Exception as ex:d['status']='decode_error';d['error']=str(ex)
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'record':str(a.record),'updated_aa':str(a.updated_aa),'read_only':True,'warning':'Array indices, reference IDs, external CAB mappings, GUID/catalog entries, streamed binary payloads and preload dependencies require semantic verification before applying. Safe field candidates are not installation approval.','bundles':out},ensure_ascii=False,indent=2),'utf8');print(str(a.output))
