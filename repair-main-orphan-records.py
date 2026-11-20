from pathlib import Path
import sys,json,hashlib
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
def write(v,node,writer,config):
 if node.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,config.assetsfile) is None:
  for c in node.m_Children:
   if c.m_Type!='ReferencedObjectData':oldwrite(v[c.m_Name],c,writer,config)
  if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):writer.align_stream()
  return
 return oldwrite(v,node,writer,config)
TypeTreeHelper.write_value=write
O=next(p for p in sorted(R.glob('main-1-14-rebuild-*'),reverse=True) if (p/'manifest.json').exists());m=json.loads((O/'manifest.json').read_text('utf8'));audit=[]
for bn in m['after_sha256']:
 if 'visualtree' not in bn:continue
 e=UnityPy.load(str(O/bn));changed=False
 for obj in e.objects:
  if obj.type.name!='MonoBehaviour':continue
  d=obj.read_typetree()
  if 'm_VisualTree' not in d:continue
  rr={r['rid']:r for r in d['references']['RefIds']};seen=set();todo=[d['m_VisualTree']['rid']]
  while todo:
   i=todo.pop()
   if i in seen:continue
   seen.add(i);todo.extend(x['rid'] for x in rr[i]['data'].get('m_Children',[]))
  bad={i for i,r in rr.items() if 'm_Parent' in r.get('data',{}) and i not in seen}
  if not bad:continue
  remove=set(bad)
  for i in bad:
   sd=rr[i]['data'].get('m_SerializedData',{}).get('rid',-2)
   if sd!=-2:remove.add(sd)
  d['references']['RefIds']=[r for r in d['references']['RefIds'] if r['rid'] not in remove];obj.save_typetree(d);changed=True;audit.append({'bundle':bn,'name':d['m_Name'],'path_id':obj.path_id,'removed_unattached_records':sorted(remove)})
 if changed:
  b=e.file.save(packer='lz4');(O/bn).write_bytes(b);m['after_sha256'][bn]=hashlib.sha256(b).hexdigest()
m['orphan_record_cleanup']=audit;(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');print(json.dumps(audit))
