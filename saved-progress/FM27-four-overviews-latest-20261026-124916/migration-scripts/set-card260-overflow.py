import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
P=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
N='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT=R/('卡面260-允许溢出-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
before={str(p):(p/N).read_bytes() for p in [P,GAME]}
for tag,p in [('skin',P),('game',GAME)]:(OUT/('backup-'+tag+'.bundle')).write_bytes(before[str(p)])
assert before[str(P)]==before[str(GAME)]
env=UnityPy.load(before[str(GAME)]);obs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
old=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for ch in n.m_Children:
   if ch.m_Type!='ReferencedObjectData':old(v[ch.m_Name],ch,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return old(v,n,w,c)
TypeTreeHelper.write_value=write
def override(s,a,props):
 ri=a.get('m_RuleIndex',-1)
 rule=copy.deepcopy(s['m_Rules'][ri]) if ri>=0 else {'m_ComplexSelectors':[],'m_Properties':[],'line':-1}
 for pid,(t,value) in props.items():
  array={2:'floats',3:'dimensions',7:'strings'}[t]
  if t==3:value={'unit':1,'value':float(value)}
  s[array].append(value)
  rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id']!=pid]
  rule['m_Properties'].append({'m_Id':pid,'m_CustomName':'','m_Line':-1,'m_Values':[{'m_ValueType':t,'valueIndex':len(s[array])-1}]})
 a['m_RuleIndex']=len(s['m_Rules']);s['m_Rules'].append(rule)
changed={};details=[]
for o in obs.values():
 if o.type.name!='MonoBehaviour' or o.peek_name() not in ['PlayerAttributesTooltipBlock','PlayerAttributesSmallBlock','PlayerAttributesStandardBlock','PlayerAttributesLargeBlock','PlayerAttributesCompactBlock']:continue
 d=o.read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};so=obs[d['inlineSheet']['m_PathID']];s=so.read_typetree()
 def name(r):return rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')
 card=next(r for r in rr.values() if name(r)=='ReportMiddleCA000Layer')
 def property_value(node,pid):
  ri=node.get('m_RuleIndex',-1)
  if ri<0:return None
  prop=next((p for p in s['m_Rules'][ri]['m_Properties'] if p['m_Id']==pid),None)
  if not prop:return None
  return [s[{2:'floats',3:'dimensions',7:'strings'}[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in [2,3,7] else h for h in prop['m_Values']]
 ca=card['data'];old_width=property_value(ca,131105)[0];old_left=property_value(ca,131089)[0];old_top=copy.deepcopy(property_value(ca,131104))
 assert old_width['unit']==old_left['unit']==1
 new_left=old_left['value']+(old_width['value']-260)/2
 override(s,ca,{131105:(3,260),131087:(3,260),131089:(3,new_left),458768:(7,'visible')})
 # Explicit unit scale cancels the previous 0.98 transform.
 rule=s['m_Rules'][ca['m_RuleIndex']]
 rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id']!=327681]
 s['floats'].append(1.0);one=len(s['floats'])-1
 rule['m_Properties'].append({'m_Id':327681,'m_CustomName':'','m_Line':-1,'m_Values':[{'m_ValueType':2,'valueIndex':one},{'m_ValueType':2,'valueIndex':one}]})
 assert property_value(ca,131104)==old_top
 assert new_left+130==old_left['value']+old_width['value']/2
 ancestors=[];i=ca['m_Parent']['rid']
 while i!=-2 and rr[i]['data'].get('m_FullTypeName')!='UnityEngine.UIElements.UXML':
  node=rr[i]['data'];override(s,node,{458768:(7,'visible')});ancestors.append(i);i=node['m_Parent']['rid']
 for r in rr.values():
  if name(r)=='FrameActions':
   assert property_value(r['data'],131087)==[{'unit':1,'value':250.0}]
 images=[r for r in rr.values() if (name(r) or '').startswith('ReportCACardImage')]
 assert len(images)==5
 for image in images:
  assert property_value(image['data'],131105)==[{'unit':2,'value':100.0}]
  assert property_value(image['data'],131087)==[{'unit':2,'value':100.0}]
 assert property_value(ca,131105)==property_value(ca,131087)==[{'unit':1,'value':260.0}]
 assert all(property_value(rr[i]['data'],458768)==['visible'] for i in ancestors)
 # Validate the actual action parent and complete hierarchy after reparenting.
 seen=set()
 def visit(i):
  assert i not in seen;seen.add(i)
  for c in rr[i].get('data',{}).get('m_Children',[]):
   assert rr[c['rid']]['data']['m_Parent']['rid']==i;visit(c['rid'])
 visit(d['m_VisualTree']['rid'])
 assert all(r['rid'] in seen for r in rr.values() if 'm_Parent' in r.get('data',{}))
 changed[o.path_id]=d;changed[so.path_id]=s
 details.append({'asset':d['m_Name'],'card_size':[260,260],'card_left':new_left,'top_preserved':old_top,'unclipped_ancestors':len(ancestors),'ability_variants_verified':5})
assert len(details)==5
for i,d in changed.items():obs[i].save_typetree(d)
data=env.file.save(packer='lz4');(OUT/N).write_bytes(data)
saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(obs)
for i,o in saved.items():
 if i in changed:assert o.read_typetree()==changed[i]
 else:assert sha(o.get_raw_data())==hashes[i]
for p in [P,GAME]:assert (p/N).read_bytes()==before[str(p)]
try:
 for p in [P,GAME]:(p/N).write_bytes(data);assert sha((p/N).read_bytes())==sha(data)
except Exception:
 for p in [P,GAME]:(p/N).write_bytes(before[str(p)])
 raise
report={'installed':True,'runtime_verified':False,'bar_height':250,'card_size':[260,260],'changes':details,'after_sha256':sha(data),'unrelated_objects_verified':len(obs)-len(changed)}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(str(OUT));print(json.dumps(report,indent=2))
