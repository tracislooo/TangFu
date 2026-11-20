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
bn='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';e=UnityPy.load(str(O/bn));obs={o.path_id:o for o in e.objects};removed=set()
for o in list(obs.values()):
 if o.type.name=='MonoBehaviour' and o.peek_name().startswith('TFReferenceBookmark'):
  removed.add(o.path_id);d=o.read_typetree()
  if d.get('inlineSheet',{}).get('m_PathID'):removed.add(d['inlineSheet']['m_PathID'])
for pid in removed:e.assets[0].objects.pop(pid,None)
ab=next(o for o in obs.values() if o.type.name=='AssetBundle');d=ab.read_typetree();d['m_Container']=[(k,v) for k,v in d['m_Container'] if not(v['asset']['m_FileID']==0 and v['asset']['m_PathID'] in removed)]
for ptr in d['m_PreloadTable']:
 if ptr['m_FileID']==0 and ptr['m_PathID'] in removed:ptr['m_PathID']=0
ab.save_typetree(d);b=e.file.save(packer='lz4');(O/bn).write_bytes(b);m['after_sha256'][bn]=hashlib.sha256(b).hexdigest();m['removed_sidebar_object_ids']=sorted(removed);(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');print(sorted(removed))
