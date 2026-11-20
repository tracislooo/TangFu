import sys, json, hashlib, datetime, copy
from pathlib import Path
root=Path(__file__).parent
sys.path.insert(0,str(root/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
base=root/'Action移入属性区-20261016-002020/backup'
packages=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
name='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
src=UnityPy.load(str(base/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'))
srcobs={o.path_id:o for o in src.objects}
sheet=srcobs[8045407476604796436].read_typetree()
out=root/('Action点击区域修正-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir()
before=(packages/name).read_bytes();(out/('backup-'+name)).write_bytes(before)
env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};hashes={i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in obs.items()}
old=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for ch in n.m_Children:
   if ch.m_Type!='ReferencedObjectData':old(v[ch.m_Name],ch,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return old(v,n,w,c)
TypeTreeHelper.write_value=write
changes={};details=[]
for o in obs.values():
 if o.type.name!='MonoBehaviour' or o.peek_name() not in ['PlayerAttributesTooltipBlock','PlayerAttributesSmallBlock','PlayerAttributesStandardBlock','PlayerAttributesLargeBlock','PlayerAttributesCompactBlock']:continue
 d=o.read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};so=obs[d['inlineSheet']['m_PathID']];s=so.read_typetree()
 menu=next(r for r in rr.values() if r['type']['class']=='PluginContextMenuBindings/UxmlSerializedData')
 node=next(r for r in rr.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==menu['rid'])
 text=next(r for r in rr.values() if r.get('data',{}).get('DebugDisplay')=='Actions')
 textnode=next(r for r in rr.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==text['rid'])
 for target,source in [(node,5),(textnode,6)]:
  rule=copy.deepcopy(sheet['m_Rules'][source])
  for p in rule['m_Properties']:
   for h in p['m_Values']:
    # Keyword indices are enum values, not indices into the dimensions array.
    array={2:'floats',3:'dimensions',4:'colors',5:'strings',7:'strings',8:'strings'}.get(h['m_ValueType'])
    if array:
     value=copy.deepcopy(sheet[array][h['valueIndex']]);h['valueIndex']=len(s[array]);s[array].append(value)
    else:assert h['m_ValueType']==1
  s['m_Rules'][target['data']['m_RuleIndex']]=rule
 # Let the menu element receive the click, including clicks on its label/icons.
 for ch in node['data']['m_Children']:
  child=rr[ch['rid']]['data'];sd=rr[child['m_SerializedData']['rid']]['data']
  sd['pickingMode']=1;sd['pickingMode_UxmlAttributeFlags']=1
 changes[o.path_id]=d;changes[so.path_id]=s
 details.append({'name':d['m_Name'],'width_keyword_restored':2,'decorative_children_ignore_picking':True})
for i,d in changes.items():obs[i].save_typetree(d)
data=env.file.save(packer='lz4');(out/name).write_bytes(data)
saved={o.path_id:o for o in UnityPy.load(data).objects}
assert set(saved)==set(obs)
for i,o in saved.items():
 if i in changes:assert o.read_typetree()==changes[i]
 else:assert hashlib.sha256(o.get_raw_data()).hexdigest()==hashes[i]
assert (packages/name).read_bytes()==before
(packages/name).write_bytes(data)
manifest={'installed':True,'runtime_verified':False,'changes':details,'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(data).hexdigest(),'unrelated_objects_verified':len(obs)-len(changes)}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(str(out));print(json.dumps(manifest,indent=2))
