import datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
N='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
P=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
O=R/('迁移模板引用修正-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));O.mkdir()
before={str(p):(p/N).read_bytes() for p in [P,G]}
for tag,p in [('skin',P),('game',G)]:(O/('backup-'+tag+'.bundle')).write_bytes(before[str(p)])
assert before[str(P)]==before[str(G)]
env=UnityPy.load(before[str(P)]);obs={o.path_id:o for o in env.objects};sha=lambda b:hashlib.sha256(b).hexdigest();hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
old=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for ch in n.m_Children:
   if ch.m_Type!='ReferencedObjectData':old(v[ch.m_Name],ch,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return old(v,n,w,c)
TypeTreeHelper.write_value=write
changed={};count=0
for o in obs.values():
 if o.type.name!='MonoBehaviour' or o.peek_name() not in ['PlayerAttributesTooltipBlock','PlayerAttributesSmallBlock','PlayerAttributesStandardBlock','PlayerAttributesLargeBlock','PlayerAttributesCompactBlock']:continue
 d=o.read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};aliases={u['alias'] for u in d['m_Usings']}
 for r in rr.values():
  a=r.get('data',{});alias=a.get('m_TemplateAlias','')
  if alias.startswith(('MovedHeader_','MovedBanner_')):
   sd=rr[a['m_SerializedData']['rid']]['data'];assert alias in aliases
   if sd['templateId']!=alias:sd['templateId']=alias;count+=1
 for r in rr.values():
  a=r.get('data',{})
  if a.get('templateId_UxmlAttributeFlags')==1:assert a['templateId'] in aliases,a['templateId']
 o.save_typetree(d);changed[o.path_id]=d
assert len(changed)==5 and count>0
data=env.file.save(packer='lz4');(O/N).write_bytes(data)
saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(obs)
for i,o in saved.items():
 if i in changed:assert o.read_typetree()==changed[i]
 else:assert sha(o.get_raw_data())==hashes[i]
for p in [P,G]:assert (p/N).read_bytes()==before[str(p)]
try:
 for p in [P,G]:(p/N).write_bytes(data);assert sha((p/N).read_bytes())==sha(data)
except Exception:
 for p in [P,G]:(p/N).write_bytes(before[str(p)])
 raise
report={'template_ids_corrected':count,'changed_assets':len(changed),'unrelated_assets_verified':len(obs)-len(changed),'after_sha256':sha(data),'runtime_verified':False,'installed':True}
(O/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(str(O));print(json.dumps(report))
