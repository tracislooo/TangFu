import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
P=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
N='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT=R/('操作按钮右移-高度350-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
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
 row=next(r for r in rr.values() if name(r)=='FrameActions')
 menu=next(r for r in rr.values() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.PluginContextMenuBindings' and r['data']['m_Parent']['rid']==row['rid'])
 scout=next(r for r in rr.values() if r.get('data',{}).get('m_TemplateAlias')=='MovedBanner_PlayerReportHeaderScoutSection')
 parent=rr[scout['data']['m_Parent']['rid']]
 row['data']['m_Children'].remove({'rid':menu['rid']})
 insertion=parent['data']['m_Children'].index({'rid':scout['rid']})
 parent['data']['m_Children'].insert(insertion,{'rid':menu['rid']});menu['data']['m_Parent']={'rid':parent['rid']}
 override(s,parent['data'],{131083:(7,'column'),131073:(7,'stretch')})
 override(s,menu['data'],{131074:(7,'flex-end'),131084:(2,0.0),131085:(2,0.0),131102:(7,'relative'),131090:(3,8)})
 resized=0
 for r in rr.values():
  a=r.get('data',{});ri=a.get('m_RuleIndex',-1)
  if ri<0:continue
  props={}
  for p in s['m_Rules'][ri]['m_Properties']:
   if p['m_Id'] in [131087,131094,131096] and len(p['m_Values'])==1:
    h=p['m_Values'][0]
    if h['m_ValueType']==3 and s['dimensions'][h['valueIndex']]=={'unit':1,'value':185.0}:props[p['m_Id']]=(3,350)
  if props:override(s,a,props);resized+=1
 assert resized>=8
 # Validate the actual action parent and complete hierarchy after reparenting.
 seen=set()
 def visit(i):
  assert i not in seen;seen.add(i)
  for c in rr[i].get('data',{}).get('m_Children',[]):
   assert rr[c['rid']]['data']['m_Parent']['rid']==i;visit(c['rid'])
 visit(d['m_VisualTree']['rid'])
 assert all(r['rid'] in seen for r in rr.values() if 'm_Parent' in r.get('data',{}))
 changed[o.path_id]=d;changed[so.path_id]=s
 details.append({'asset':d['m_Name'],'menu_above_scout':True,'height_nodes_updated':resized})
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
report={'installed':True,'runtime_verified':False,'height':350,'changes':details,'after_sha256':sha(data),'unrelated_objects_verified':len(obs)-len(changed)}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(str(OUT));print(json.dumps(report,indent=2))
