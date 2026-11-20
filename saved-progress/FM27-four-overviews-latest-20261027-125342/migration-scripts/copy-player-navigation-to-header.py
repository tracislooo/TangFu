import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
N='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT=R/('头部复制上下球员按钮-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
before=(GAME/N).read_bytes();assert before==(SKIN/N).read_bytes();(OUT/'backup.bundle').write_bytes(before)
sha=lambda b:hashlib.sha256(b).hexdigest();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
old=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for ch in n.m_Children:
   if ch.m_Type!='ReferencedObjectData':old(v[ch.m_Name],ch,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return old(v,n,w,c)
TypeTreeHelper.write_value=write
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def named(d,name):
 rr=refs(d);return next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name)
nav=obs[4643068090026484269].read_typetree();nr=refs(nav);navigation=obs[1190799287003167625].read_typetree();qr=refs(navigation)
remapper=nr[1094];remapper_sd=nr[remapper['data']['m_SerializedData']['rid']]
assert remapper_sd['data']['Mappings'][0]['to']['m_path']=='person.NextSibling'
propids={'width':131105,'height':131087,'minheight':131096,'maxheight':131094,'grow':131084,'shrink':131085,'left':131089,'top':131104,'position':131102,'direction':131083,'margin':262150,'padding':262151,'pl':131099}
def style(s,node,props):
 i=node.get('m_RuleIndex',-1);rule=copy.deepcopy(s['m_Rules'][i]) if i>=0 else {'m_ComplexSelectors':[],'m_Properties':[],'line':-1}
 for key,(t,v) in props.items():
  array={2:'floats',3:'dimensions',7:'strings'}[t]
  if t==3:v={'unit':1,'value':float(v)}
  s[array].append(v);pid=propids[key];rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id']!=pid]
  rule['m_Properties'].append({'m_Id':pid,'m_CustomName':'','m_Line':-1,'m_Values':[{'m_ValueType':t,'valueIndex':len(s[array])-1}]})
 node['m_RuleIndex']=len(s['m_Rules']);s['m_Rules'].append(rule)
source_records=[r for r in navigation['references']['RefIds'] if r['rid'] not in [-2,1000]]
assert all(r.get('data',{}).get('m_RuleIndex',-1)==-1 for r in source_records)
changed={};details=[]
for obj in obs.values():
 if obj.type.name!='MonoBehaviour' or obj.peek_name() not in ['OverviewToggle_FullOverview','OverviewToggle_PortraitAttributes']:continue
 d=obj.read_typetree();rr=refs(d);sheetobj=obs[d['inlineSheet']['m_PathID']];s=sheetobj.read_typetree()
 simple=d['m_Name']=='OverviewToggle_PortraitAttributes'
 parent=named(d,'SimplePortraitHeader' if simple else 'MovedPlayerReportHeader')
 start=max(rr)+1;wrap=copy.deepcopy(remapper);wrapsd=copy.deepcopy(remapper_sd);wrap['rid']=start;wrapsd['rid']=start+1
 mapping={r['rid']:start+2+k for k,r in enumerate(source_records)};mapping[1000]=start
 wrap['data'].update(m_Id=2130000000+start,m_Parent={'rid':parent['rid']},m_Children=[{'rid':mapping[1001]}],m_Classes=[],m_RuleIndex=-1,m_SerializedData={'rid':start+1})
 wrapsd['data'].update(uxmlAssetId=2130000000+start,name='HeaderPlayerQuickFlickContext',name_UxmlAttributeFlags=1)
 parent['data']['m_Children'].append({'rid':start})
 records=copy.deepcopy(source_records)
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    if v['rid']!=-2:v['rid']=mapping[v['rid']]
   else:
    for a in v.values():remap(a)
  elif isinstance(v,list):
   for a in v:remap(a)
 for r in records:
  oldid=r['rid'];remap(r.get('data',{}));r['rid']=mapping[oldid]
  if r['type']['class']=='ContextShortcutsElement/UxmlSerializedData':
   a=r['data'];a['ShortcutEvent']={'m_bytes':[]};a['ShortcutEvent_UxmlAttributeFlags']=1
   a['InputActionRef']={'m_inputActionAsset':{'m_AssetGUID':'','m_SubObjectName':'','m_SubObjectType':''},'m_actionID':''};a['InputActionRef_UxmlAttributeFlags']=1
 d['references']['RefIds'].extend([wrap,wrapsd]+records);rr=refs(d)
 style(s,wrap['data'],{'position':(7,'absolute'),'left':(3,4 if simple else 44),'top':(3,42 if simple else 90),'width':(3,28),'height':(3,54),'minheight':(3,54),'maxheight':(3,54),'grow':(2,0.0),'shrink':(2,0.0),'margin':(3,0),'padding':(3,0)})
 for i in [1001,1002,1004,1006]:style(s,rr[mapping[i]]['data'],{'width':(3,28),'direction':(7,'column'),'margin':(3,0),'padding':(3,0)})
 for i in [1011,1013]:
  a=rr[mapping[i]]['data'];a['m_Classes']=[c for c in a['m_Classes'] if 'margin' not in c]
  style(s,a,{'width':(3,28),'height':(3,26),'minheight':(3,26),'maxheight':(3,26),'margin':(3,0),'padding':(3,0),'shrink':(2,0.0)})
 for i in [1015,1017]:
  a=rr[mapping[i]]['data'];serial=rr[a['m_SerializedData']['rid']]['data'];serial['pickingMode']=1;serial['pickingMode_UxmlAttributeFlags']=1
 if simple:style(s,parent['data'],{'pl':(3,44)})
 # Native click payloads remain byte-for-byte identical; only shortcut registration is omitted.
 for i in [1016,1018]:assert rr[mapping[i]]['data']['Events']==qr[i]['data']['Events']
 seen=set()
 def visit(i):
  assert i not in seen;seen.add(i)
  for ch in rr[i].get('data',{}).get('m_Children',[]):assert rr[ch['rid']]['data']['m_Parent']['rid']==i;visit(ch['rid'])
 visit(d['m_VisualTree']['rid']);assert all(r['rid'] in seen for r in rr.values() if 'm_Parent' in r.get('data',{}))
 changed[obj.path_id]=d;changed[sheetobj.path_id]=s;details.append({'asset':d['m_Name'],'left':4 if simple else 44,'top':42 if simple else 90,'button_size':[28,26]})
assert len(details)==2
for i,d in changed.items():obs[i].save_typetree(d)
data=env.file.save(packer='lz4');(OUT/N).write_bytes(data)
for o in UnityPy.load(data).objects:
 if o.path_id in changed:assert o.read_typetree()==changed[o.path_id]
 else:assert sha(o.get_raw_data())==hashes[o.path_id]
assert 4643068090026484269 not in changed and 1190799287003167625 not in changed
assert (GAME/N).read_bytes()==(SKIN/N).read_bytes()==before
try:
 for p in [GAME,SKIN]:(p/N).write_bytes(data);assert (p/N).read_bytes()==data
except Exception:
 for p in [GAME,SKIN]:(p/N).write_bytes(before)
 raise
report={'installed':True,'runtime_verified':False,'original_nav_preserved':True,'keyboard_shortcuts_not_duplicated':True,'copies':details,'before_sha256':sha(before),'after_sha256':sha(data),'unrelated_objects_verified':len(obs)-len(changed)}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(str(OUT));print(json.dumps(report,indent=2))
