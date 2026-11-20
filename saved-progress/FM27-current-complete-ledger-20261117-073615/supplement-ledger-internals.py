"""Add serialized type schemas and non-object resource entries to an existing immutable ledger."""
from pathlib import Path
import sys,json,gzip,hashlib,argparse,gc
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
pa=argparse.ArgumentParser();pa.add_argument('record',type=Path);a=pa.parse_args();O=a.record;m=json.loads((O/'manifest.json').read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.name.endswith('.gz'):
  with gzip.open(p,'wt',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,separators=(',',':'))
 else:p.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
def hexv(v):return v.hex() if isinstance(v,bytes) else v
def schemas(e):
 return {af.name.lower():{'header_version':af.header.version,'unity_version':af.unity_version,'types':[{'class_id':t.class_id,'script_id':hexv(t.script_id),'old_type_hash':hexv(t.old_type_hash),'node':[{**{k:v for k,v in x.to_dict().items() if k!='m_Children'},'child_count':len(x.m_Children)} for x in t.node.traverse()] if t.node else None,'dependencies':t.type_dependencies} for t in af.types],'managed_reference_types':[{'class_id':t.class_id,'class':t.m_ClassName,'namespace':t.m_NameSpace,'assembly':t.m_AssemblyName,'script_id':hexv(t.script_id),'node':[{**{k:v for k,v in x.to_dict().items() if k!='m_Children'},'child_count':len(x.m_Children)} for x in t.node.traverse()] if t.node else None} for t in (af.ref_types or [])]} for af in e.assets}
summary=[]
for row in m['bundles']:
 if not row['objects'] or row.get('shared_export_from'):continue
 n=row['bundle'];mode=row['mode'];p=O/row['snapshot'];q=O/row['original_snapshot'];ae=UnityPy.load(str(q));be=UnityPy.load(str(p));before=schemas(ae);after=schemas(be);folder=O/'bundle-internals'/mode/n;dump(folder/'original-schemas.json.gz',before);dump(folder/'modified-schemas.json.gz',after);resourcechanges=[]
 for key in sorted(set(ae.file.files)|set(be.file.files)):
  av=ae.file.files.get(key);bv=be.file.files.get(key)
  if hasattr(av,'objects') or hasattr(bv,'objects'):continue
  ab=av.bytes if av is not None else None;bb=bv.bytes if bv is not None else None
  if ab==bb:continue
  token=sha(key.encode())[:16];entry={'entry':key,'native_sha256':sha(ab) if ab is not None else None,'modified_sha256':sha(bb) if bb is not None else None,'native_bytes':len(ab) if ab is not None else None,'modified_bytes':len(bb) if bb is not None else None,'export_token':token};resourcechanges.append(entry)
  for label,data in [('original',ab),('modified',bb)]:
   if data is not None:(folder/(token+'-'+label+'.bin')).write_bytes(data)
 dump(folder/'resource-entry-changes.json',resourcechanges);row['internal_resources']={'schema_data_changed':before!=after,'resource_entry_changes':len(resourcechanges),'detail':str(folder.relative_to(O)).replace('\\','/')};summary.append({'mode':mode,'bundle':n,**row['internal_resources']});del ae,be,before,after;gc.collect()
m['bundle_internals']=summary;dump(O/'manifest.json',m);dump(O/'bundle-internals-summary.json',summary)
p=O/'README.md';p.write_text(p.read_text('utf8')+'\n补充：bundle-internals保留序列化类型/schema及managed reference类型的前后数据；对象之外的.resS等资源条目也逐项比较哈希并导出完整二进制，覆盖不限于Texture2D的数据流变化。\n','utf8')
print(json.dumps({'schema_bundle_pairs':len(summary),'changed_resource_entries':sum(x['resource_entry_changes'] for x in summary)},ensure_ascii=False))

