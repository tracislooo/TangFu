import copy, datetime, hashlib, json, sys
from pathlib import Path
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
P=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
OUT=R/('头部迁入属性区200-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
sources={n:(P/n).read_bytes() for n in [G,W]}
game_before={n:(GAME/n).read_bytes() for n in [G,W]}
for folder,data in [('backup-skin',sources),('backup-game',game_before)]:
 (OUT/folder).mkdir()
 for n,b in data.items():(OUT/folder/n).write_bytes(b)
(OUT/'modified').mkdir()
envs={n:UnityPy.load(b) for n,b in sources.items()}
obs={n:{o.path_id:o for o in e.objects} for n,e in envs.items()}
hashes={n:{i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in obs.items()}
changed={G:{},W:{}}
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
header=obs[W][5775949770471550939].read_typetree()
banner=obs[G][-4194025542157271532].read_typetree()
hs=obs[W][header['inlineSheet']['m_PathID']].read_typetree()
bs=obs[G][banner['inlineSheet']['m_PathID']].read_typetree()
vr=refs(header)[1008];vs=refs(header)[1012]
IDS=dict(height=131087,minheight=131096,maxheight=131094,grow=131084,shrink=131085,
         direction=131083,align=131073,self=131074,minwidth=131097,basis=131082,
         margin=262150,padding=262151,overflow=458768,position=131102,top=131104,left=131089)
def val(s,t,v):
 array={2:'floats',3:'dimensions',7:'strings'}[t]
 if t==3:v={'unit':1,'value':float(v)}
 s[array].append(v);return {'m_ValueType':t,'valueIndex':len(s[array])-1}
def style(s,node,props):
 prior=node.get('m_RuleIndex',-1)
 rule=copy.deepcopy(s['m_Rules'][prior]) if prior>=0 else {'m_ComplexSelectors':[],'m_Properties':[],'line':-1}
 for key,(t,v) in props.items():
  rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id']!=IDS[key]]
  rule['m_Properties'].append({'m_Id':IDS[key],'m_CustomName':'','m_Line':-1,'m_Values':[val(s,t,v)]})
 node['m_RuleIndex']=len(s['m_Rules']);s['m_Rules'].append(rule)
def fixed(s,node,h):style(s,node,{'height':(3,h),'minheight':(3,h),'maxheight':(3,h),'grow':(2,0.0),'shrink':(2,0.0)})
def import_tree(dst,s,src,ss,prefix,parent):
 rr=refs(dst);start=max(rr)+1
 records=copy.deepcopy([r for r in src['references']['RefIds'] if r['rid'] not in [-2,1000]])
 mapping={r['rid']:start+k for k,r in enumerate(records)}
 mapping[1000]=parent
 aliases={u['alias']:prefix+u['alias'] for u in src['m_Usings']}
 for u in src['m_Usings']:
  u=copy.deepcopy(u);u['alias']=aliases[u['alias']];dst['m_Usings'].append(u)
 styles={}
 def walk(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    if v['rid']!=-2:v['rid']=mapping[v['rid']]
   else:
    if set(v)=={'m_FileID','m_PathID'}:assert v['m_PathID']==0,'Unexpected cross-bundle pointer'
    for a in v.values():walk(a)
  elif isinstance(v,list):
   for a in v:walk(a)
 for r in records:
  original=r['rid'];walk(r['data']);r['rid']=mapping[original];a=r['data']
  if a.get('m_TemplateAlias') in aliases:a['m_TemplateAlias']=aliases[a['m_TemplateAlias']]
  ri=a.get('m_RuleIndex',-1)
  if ri>=0:
   if ri not in styles:
    rule=copy.deepcopy(ss['m_Rules'][ri])
    for p in rule['m_Properties']:
     for h in p['m_Values']:
      array={2:'floats',3:'dimensions',4:'colors',5:'strings',7:'strings',8:'strings'}.get(h['m_ValueType'])
      if array:
       value=copy.deepcopy(ss[array][h['valueIndex']]);h['valueIndex']=len(s[array]);s[array].append(value)
      else:assert h['m_ValueType']==1,h
    styles[ri]=len(s['m_Rules']);s['m_Rules'].append(rule)
   a['m_RuleIndex']=styles[ri]
 dst['references']['RefIds'].extend(records)
 return mapping
def element(d,parent,name):
 rr=refs(d);i=max(rr)+1;node=copy.deepcopy(vr);sd=copy.deepcopy(vs)
 node['rid']=i;sd['rid']=i+1
 node['data'].update(m_Id=2100200000+i,m_Parent={'rid':parent},m_Children=[],m_Classes=[],m_RuleIndex=-1,m_SerializedData={'rid':i+1})
 sd['data'].update(uxmlAssetId=2100200000+i,name=name,name_UxmlAttributeFlags=1)
 d['references']['RefIds'].extend([node,sd]);return node
details=[]
for name in ['PlayerAttributesTooltipBlock','PlayerAttributesSmallBlock','PlayerAttributesStandardBlock','PlayerAttributesLargeBlock','PlayerAttributesCompactBlock']:
 o=next(o for o in obs[W].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
 d=o.read_typetree();rr=refs(d);so=obs[W][d['inlineSheet']['m_PathID']];s=so.read_typetree()
 row=next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='FrameActions')
 # Existing action container becomes the complete 200px horizontal strip.
 row['data']['m_Classes']=['row-direction-normal','align-self-stretch','align-items-start','flex-no-shrink-class']
 fixed(s,row['data'],200);style(s,row['data'],{'direction':(7,'row'),'align':(7,'flex-start')})
 menu=rr[row['data']['m_Children'][0]['rid']]
 style(s,menu['data'],{'self':(7,'flex-start'),'grow':(2,0.0),'shrink':(2,0.0),'position':(7,'relative')})
 right=element(d,row['rid'],'MovedPlayerReportHeader');row['data']['m_Children'].append({'rid':right['rid']})
 right['data']['m_Classes']=['flex-grow-class','column-direction-normal']
 fixed(s,right['data'],200);style(s,right['data'],{'grow':(2,1.0),'shrink':(2,1.0),'minwidth':(3,0),'basis':(3,0),'overflow':(7,'hidden')})
 # Supply the dependencies normally inherited from the report header's outer layout.
 rem=copy.deepcopy(refs(header)[1002]);rem_sd=copy.deepcopy(refs(header)[1005]);start=max(refs(d))+1
 rem['rid']=start;rem_sd['rid']=start+1
 rem['data'].update(m_Id=2100300000+start,m_Parent={'rid':right['rid']},m_Children=[],m_Classes=['flex-grow-class'],m_SerializedData={'rid':start+1})
 rem_sd['data'].update(uxmlAssetId=2100300000+start,name='MovedHeaderContext',Mappings=[
  {'m_serialisedType':0,'from':'localteam','to':{'m_path':'person.Team'},'type':{'id':1145176088}},
  {'m_serialisedType':0,'from':'player','to':{'m_path':'person'},'type':{'id':1145176065}}])
 right['data']['m_Children']=[{'rid':start}];d['references']['RefIds'].extend([rem,rem_sd])
 hm=import_tree(d,s,header,hs,'MovedHeader_',start);rem['data']['m_Children']=[{'rid':hm[1001]}]
 rr=refs(d)
 # Replace the maximum banner TemplateAsset with an inline VisualElement container.
 old_template=rr[hm[1027]];old_sd=old_template['data']['m_SerializedData']['rid']
 newdata=copy.deepcopy(vr['data']);newdata.update(m_Id=old_template['data']['m_Id'],m_Parent=old_template['data']['m_Parent'],m_Children=[],m_Classes=['flex-grow-class'],m_RuleIndex=-1,m_SerializedData={'rid':old_sd})
 old_template['type']=copy.deepcopy(vr['type']);old_template['data']=newdata
 sd=copy.deepcopy(vs);sd['rid']=old_sd;sd['data'].update(uxmlAssetId=newdata['m_Id'],name='MovedMaximumBanner')
 d['references']['RefIds']=[sd if r['rid']==old_sd else r for r in d['references']['RefIds']]
 bm=import_tree(d,s,banner,bs,'MovedBanner_',hm[1027]);newdata['m_Children']=[{'rid':bm[1001]}]
 rr=refs(d)
 # Bound all outer header wrappers so theme classes cannot restore the old height.
 for i in [1001,1002,1004,1006,1008]:fixed(s,rr[hm[i]]['data'],200)
 style(s,rr[hm[1008]]['data'],{'direction':(7,'row'),'grow':(2,1.0),'minwidth':(3,0),'margin':(3,0),'padding':(3,0)})
 style(s,rr[hm[1010]]['data'],{'position':(7,'relative'),'height':(3,200),'minheight':(3,0),'maxheight':(3,200),'shrink':(2,0.0)})
 style(s,rr[hm[1011]]['data'],{'grow':(2,1.0),'shrink':(2,1.0),'minwidth':(3,0)})
 for i in [1001,1002,1004]:fixed(s,rr[bm[i]]['data'],200)
 changed[W][o.path_id]=d;changed[W][so.path_id]=s
 details.append({'name':name,'row':row['rid'],'header_root':hm[1001],'banner_root':bm[1001]})

# Collapse the original assets only after the independent copies have been made.
for bundle,doc,ss,pid in [(W,header,hs,5775949770471550939),(G,banner,bs,-4194025542157271532)]:
 doc=copy.deepcopy(doc);ss=copy.deepcopy(ss);rr=refs(doc)
 for r in rr.values():
  a=r.get('data',{})
  if 'm_RuleIndex' in a and a.get('m_FullTypeName')!='UnityEngine.UIElements.UXML':
   fixed(ss,a,0);style(ss,a,{'margin':(3,0),'padding':(3,0),'overflow':(7,'hidden')})
 changed[bundle][pid]=doc;changed[bundle][doc['inlineSheet']['m_PathID']]=ss

def validate(d,s):
 rr=refs(d);assert len(rr)==len(d['references']['RefIds']);seen=set();aliases={u['alias'] for u in d['m_Usings']}
 def visit(i):
  assert i not in seen;seen.add(i);a=rr[i]['data']
  if 'm_TemplateAlias' in a:assert a['m_TemplateAlias'] in aliases
  for c in a.get('m_Children',[]):assert rr[c['rid']]['data']['m_Parent']['rid']==i;visit(c['rid'])
 visit(d['m_VisualTree']['rid'])
 assert all(r['rid'] in seen for r in rr.values() if 'm_Parent' in r.get('data',{}))
 def check(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:assert v['rid'] in rr
   else:
    for a in v.values():check(a)
  elif isinstance(v,list):
   for a in v:check(a)
 check(d)
 for r in s['m_Rules']:
  for p in r['m_Properties']:
   for h in p['m_Values']:
    array={2:'floats',3:'dimensions',4:'colors',5:'strings',7:'strings',8:'strings'}.get(h['m_ValueType'])
    if array:assert 0<=h['valueIndex']<len(s[array])
manifest={'installed':False,'runtime_verified':False,'height':200,'targets':details,'files':{}}
for n in [G,W]:
 for i,d in changed[n].items():
  if 'm_VisualTree' in d:validate(d,changed[n].get(d['inlineSheet']['m_PathID'],obs[n][d['inlineSheet']['m_PathID']].read_typetree()))
  obs[n][i].save_typetree(d)
 data=envs[n].file.save(packer='lz4');(OUT/'modified'/n).write_bytes(data)
 saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(obs[n])
 for i,o in saved.items():
  if i in changed[n]:assert o.read_typetree()==changed[n][i],(n,i)
  else:assert sha(o.get_raw_data())==hashes[n][i],(n,i)
 manifest['files'][n]={'skin_before':sha(sources[n]),'game_before':sha(game_before[n]),'after':sha(data),'changed_objects':list(changed[n]),'unrelated_verified':len(obs[n])-len(changed[n])}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for n in [G,W]:assert (P/n).read_bytes()==sources[n] and (GAME/n).read_bytes()==game_before[n]
try:
 for target in [P,GAME]:
  for n in [G,W]:
   data=(OUT/'modified'/n).read_bytes();(target/n).write_bytes(data);assert sha((target/n).read_bytes())==manifest['files'][n]['after']
except Exception:
 for n in [G,W]:(P/n).write_bytes(sources[n]);(GAME/n).write_bytes(game_before[n])
 raise
manifest['installed']=True
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(str(OUT));print(json.dumps(manifest,indent=2))
