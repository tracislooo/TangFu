import copy, datetime, hashlib, json, sys
from pathlib import Path
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
P=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
OUT=R/('旧版头部迁入185-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
sources={n:(P/n).read_bytes() for n in [G,W]}
game_before={n:(GAME/n).read_bytes() for n in [G,W]}
for folder,data in [('backup-skin',sources),('backup-game',game_before)]:
 (OUT/folder).mkdir()
 for n,b in data.items():(OUT/folder/n).write_bytes(b)
(OUT/'modified').mkdir()
envs={n:UnityPy.load(str(R/'头部迁入属性区200-20261016-004829/backup-skin'/n)) for n in [G,W]}
obs={n:{o.path_id:o for o in e.objects} for n,e in envs.items()}
hashes={n:{o.path_id:sha(o.get_raw_data()) for o in UnityPy.load(sources[n]).objects} for n in [G,W]}
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
OLD=Path('K:/桌面/27skin/package')
oldenv={n:UnityPy.load(str(OLD/n)) for n in [G,W,'ui-visualfunctions_assets_all.bundle','ui-backgrounds_assets_common.bundle']}
oldobs={n:{o.path_id:o for o in e.objects} for n,e in oldenv.items()}
header=oldobs[W][5775949770471550939].read_typetree()
banner=oldobs[G][-4194025542157271532].read_typetree()
hs=oldobs[W][header['inlineSheet']['m_PathID']].read_typetree()
bs=oldobs[G][banner['inlineSheet']['m_PathID']].read_typetree()

vr=refs(header)[1008];vs=refs(header)[1012]
import importlib.util, struct
spec=importlib.util.spec_from_file_location('catalog_migration',R/'catalog-binary-v35.py')
catmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(catmod)
catalog_path=GAME.parent/'catalog.bin';catalog_before=catalog_path.read_bytes()
(OUT/'backup-game/catalog.bin').write_bytes(catalog_before)
catalog=catmod.Catalog(catalog_before)
catalog_keys={k for k,l in catalog.keys() if isinstance(k,str)}
old_file_names={next(iter(oo.values())).assets_file.name:n for n,oo in oldobs.items()}
dst_files={n:next(iter(oo.values())).assets_file for n,oo in obs.items()}
old_guid={}
for n,e in oldenv.items():
 for k,ptr in e.container.items():
  obj=oldobs[n].get(ptr.path_id)
  if obj is not None:
   old_guid.setdefault(k,[]).append((n,obj))
current_guid={}
for n,e in envs.items():
 for k,ptr in e.container.items():
  if ptr.path_id in obs[n]:current_guid.setdefault(k,[]).append(obs[n][ptr.path_id])
examples={G:{},W:{}}
for dn in [G,W]:
 for obj in obs[dn].values():
  if obj.type.name!='MonoBehaviour':continue
  for ref in obj.read_typetree().get('references',{}).get('RefIds',[]):
   if 'data' in ref:examples[dn].setdefault(tuple(ref['type'].values()),ref['data'])
def neutral(v):
 if isinstance(v,dict):return {k:neutral(a) for k,a in v.items()}
 if isinstance(v,list):return []
 if isinstance(v,str):return ''
 if isinstance(v,float):return 0.0
 if isinstance(v,int):return 0
 return v
def upgrade_refs(d,dn):
 for ref in d.get('references',{}).get('RefIds',[]):
  if 'data' not in ref:continue
  sample=examples[dn].get(tuple(ref['type'].values()),{})
  for k,v in sample.items():
   if k not in ref['data']:ref['data'][k]=neutral(v)
  if sample:
   for k in list(ref['data']):
    if k not in sample:
     flag=k if k.endswith('_UxmlAttributeFlags') else k+'_UxmlAttributeFlags'
     assert ref['data'].get(flag,0)==0,('Unsupported active legacy field',k)
     del ref['data'][k]
imported_ids={G:set(),W:set()};imported_docs={G:{},W:{}};clone_map={};next_pid=-920000000001000
functions_to_register={}

def external_id(srcaf,index,dstaf):
 ext=srcaf.externals[index-1]
 for j,target in enumerate(dstaf.externals):
  if target.path==ext.path:return j+1
 dstaf.externals.append(copy.copy(ext));return len(dstaf.externals)

def import_type(src,dstaf):
 st=src.serialized_type
 for j,t in enumerate(dstaf.types):
  if t.class_id==st.class_id and t.script_id==st.script_id and t.old_type_hash==st.old_type_hash:return j,t
 st=copy.copy(st)
 if st.script_type_index>=0:
  script=copy.copy(src.assets_file.script_types[st.script_type_index])
  if script.local_serialized_file_index:
   script.local_serialized_file_index=external_id(src.assets_file,script.local_serialized_file_index,dstaf)
  st.script_type_index=len(dstaf.script_types);dstaf.script_types.append(script)
 dstaf.types.append(st);return len(dstaf.types)-1,st

def merge_ref_types(srcaf,dstaf):
 known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in dstaf.ref_types}
 for t in srcaf.ref_types:
  k=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
  if k not in known:dstaf.ref_types.append(copy.copy(t));known.add(k)

def clone_object(srcn,pid,dstn):
 global next_pid
 key=(srcn,pid,dstn)
 if key in clone_map:return clone_map[key]
 src=oldobs[srcn][pid];dstaf=dst_files[dstn]
 use=pid
 if use in dstaf.objects:
  if dstaf.objects[use].get_raw_data()==src.get_raw_data():clone_map[key]=use;return use
  use=next_pid;next_pid-=1
 clone_map[key]=use
 d=copy.deepcopy(src.read_typetree())
 prepare(d,srcn,dstn)
 merge_ref_types(src.assets_file,dstaf)
 upgrade_refs(d,dstn)
 obj=copy.copy(src);obj.assets_file=dstaf;obj.path_id=use;obj.type_id,obj.serialized_type=import_type(src,dstaf)
 dstaf.objects[use]=obj;obs[dstn][use]=obj
 if src.type.name=='Texture2D':assert d['m_StreamData']['size']==0,'Unexpected streamed texture'
 obj.save_typetree(d);imported_ids[dstn].add(use);imported_docs[dstn][use]=d
 return use

def prepare(v,srcn,dstn):
 srcaf=next(iter(oldobs[srcn].values())).assets_file;dstaf=dst_files[dstn]
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_PathID']:
   pid=v['m_PathID'];index=v['m_FileID'];sn=srcn
   if index:
    ext=srcaf.externals[index-1].path
    sn=next((n for file,n in old_file_names.items() if file in ext),None)
   if sn is not None and pid in oldobs[sn]:
    v['m_PathID']=clone_object(sn,pid,dstn);v['m_FileID']=0
   elif index:v['m_FileID']=external_id(srcaf,index,dstaf)
   else:raise ValueError(('Unresolved source pointer',srcn,pid))
   return
  # Use a private direct template reference when the supplied template differs.
  if 'alias' in v and 'path' in v and 'asset' in v and not v['asset']['m_PathID']:
   key=v['path']
   if v['alias']!='report-player-banner-max':
    candidates=[(n,o) for n,o in old_guid.get(key,[]) if o.type.name=='MonoBehaviour' and 'm_VisualTree' in o.read_typetree()]
    if candidates:
     n,src=candidates[0]
     stock=next((o for o in current_guid.get(key,[]) if o.type.name=='MonoBehaviour' and o.peek_name()==src.peek_name()),None)
     if stock is None or stock.get_raw_data()!=src.get_raw_data():
      v['asset']={'m_FileID':0,'m_PathID':clone_object(n,src.path_id,dstn)}
   return
  guid=v.get('m_guid')
  if guid and guid not in catalog_keys:
   candidates=[(n,o) for n,o in old_guid.get(guid,[]) if o.type.name=='MonoBehaviour']
   if candidates:
    n,src=candidates[0]
    if src.peek_name() in ['ReportFiveAttributeSum','ReportMovementSumAsText']:
     functions_to_register[guid]=clone_object(n,src.path_id,G)
    else:raise ValueError(('Missing GUID dependency',guid,src.peek_name()))
  for a in v.values():prepare(a,srcn,dstn)
 elif isinstance(v,list):
  for a in v:prepare(a,srcn,dstn)

# Remove only the old duplicate action subtree, retaining all other legacy content.
br=refs(banner)
action=next(r for r in br.values() if br.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='FrameActions')
remove=set()
def remove_branch(i):
 remove.add(i);a=br[i]['data']
 if a.get('m_SerializedData',{}).get('rid',-2)!=-2:remove.add(a['m_SerializedData']['rid'])
 for c in a.get('m_Children',[]):remove_branch(c['rid'])
remove_branch(action['rid'])
br[action['data']['m_Parent']['rid']]['data']['m_Children'].remove({'rid':action['rid']})
banner['references']['RefIds']=[r for r in banner['references']['RefIds'] if r['rid'] not in remove]
old_max_rid=next(r['rid'] for r in refs(header).values() if r.get('data',{}).get('m_TemplateAlias')=='report-player-banner-max')
for d,ss,n in [(header,hs,W),(banner,bs,G)]:
 # The root script and inlineSheet are not imported; only clone content dependencies.
 prepare(d['references'],n,W);prepare(d['m_Usings'],n,W);prepare(ss['assets'],n,W);upgrade_refs(d,W)
 merge_ref_types(oldobs[n][5775949770471550939 if n==W else -4194025542157271532].assets_file,dst_files[W])

def register_functions():
 if not functions_to_register:return catalog_before
 bundle=next(o for o in obs[G].values() if o.type.name=='AssetBundle');meta=bundle.read_typetree()
 for guid,pid in functions_to_register.items():
  start=len(meta['m_PreloadTable']);tree=obs[G][pid].read_typetree()
  meta['m_PreloadTable'].extend([copy.deepcopy(tree['m_Script']),{'m_FileID':0,'m_PathID':pid}])
  meta['m_Container'].append((guid,{'preloadIndex':start,'preloadSize':2,'asset':{'m_FileID':0,'m_PathID':pid}}))
  native=next(loc for loc in catalog.locations('f6f314e9db56227459137669d87c44e9'))
  dep=catalog.locations('528775c3a6df3ee44a81b3d826326f09')[0]
  catalog.add_key_location(guid,native,dep)
 meta['m_Container'].sort(key=lambda kv:kv[0]);changed[G][bundle.path_id]=meta
 return bytes(catalog.data)

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
    if set(v)=={'m_FileID','m_PathID'}:pass  # Pointers were remapped by dependency preparation.
    for a in v.values():walk(a)
  elif isinstance(v,list):
   for a in v:walk(a)
 for r in records:
  original=r['rid'];walk(r['data']);r['rid']=mapping[original];a=r['data']
  if a.get('m_TemplateAlias') in aliases:a['m_TemplateAlias']=aliases[a['m_TemplateAlias']]
  if a.get('templateId') in aliases:a['templateId']=aliases[a['templateId']]
  ri=a.get('m_RuleIndex',-1)
  if ri>=0:
   if ri not in styles:
    rule=copy.deepcopy(ss['m_Rules'][ri])
    for p in rule['m_Properties']:
     for h in p['m_Values']:
      array={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}.get(h['m_ValueType'])
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
 node['data'].update(m_Id=2100185000+i,m_Parent={'rid':parent},m_Children=[],m_Classes=[],m_RuleIndex=-1,m_SerializedData={'rid':i+1})
 sd['data'].update(uxmlAssetId=2100185000+i,name=name,name_UxmlAttributeFlags=1)
 d['references']['RefIds'].extend([node,sd]);return node
details=[]
for name in ['PlayerAttributesTooltipBlock','PlayerAttributesSmallBlock','PlayerAttributesStandardBlock','PlayerAttributesLargeBlock','PlayerAttributesCompactBlock']:
 o=next(o for o in obs[W].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
 d=o.read_typetree();rr=refs(d);so=obs[W][d['inlineSheet']['m_PathID']];s=so.read_typetree()
 row=next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='FrameActions')
 # Existing action container becomes the complete 185px horizontal strip.
 row['data']['m_Classes']=['row-direction-normal','align-self-stretch','align-items-start','flex-no-shrink-class']
 fixed(s,row['data'],185);style(s,row['data'],{'direction':(7,'row'),'align':(7,'flex-start')})
 menu=rr[row['data']['m_Children'][0]['rid']]
 style(s,menu['data'],{'self':(7,'flex-start'),'grow':(2,0.0),'shrink':(2,0.0),'position':(7,'relative')})
 right=element(d,row['rid'],'MovedPlayerReportHeader');row['data']['m_Children'].append({'rid':right['rid']})
 right['data']['m_Classes']=['flex-grow-class','column-direction-normal']
 fixed(s,right['data'],185);style(s,right['data'],{'grow':(2,1.0),'shrink':(2,1.0),'minwidth':(3,0),'basis':(3,0),'overflow':(7,'hidden')})
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
 old_template=rr[hm[old_max_rid]];old_sd=old_template['data']['m_SerializedData']['rid']
 newdata=copy.deepcopy(vr['data']);newdata.update(m_Id=old_template['data']['m_Id'],m_Parent=old_template['data']['m_Parent'],m_Children=[],m_Classes=['flex-grow-class'],m_RuleIndex=-1,m_SerializedData={'rid':old_sd})
 old_template['type']=copy.deepcopy(vr['type']);old_template['data']=newdata
 sd=copy.deepcopy(vs);sd['rid']=old_sd;sd['data'].update(uxmlAssetId=newdata['m_Id'],name='MovedMaximumBanner')
 d['references']['RefIds']=[sd if r['rid']==old_sd else r for r in d['references']['RefIds']]
 bm=import_tree(d,s,banner,bs,'MovedBanner_',hm[old_max_rid]);newdata['m_Children']=[{'rid':bm[1001]}]
 rr=refs(d)
 # Bound all outer header wrappers so theme classes cannot restore the old height.
 for i in [1001,1002,1004,1006,1008]:fixed(s,rr[hm[i]]['data'],185)
 style(s,rr[hm[1008]]['data'],{'direction':(7,'row'),'grow':(2,1.0),'minwidth':(3,0),'margin':(3,0),'padding':(3,0)})
 style(s,rr[hm[1010]]['data'],{'position':(7,'relative'),'height':(3,185),'minheight':(3,0),'maxheight':(3,185),'shrink':(2,0.0)})
 style(s,rr[hm[1011]]['data'],{'grow':(2,1.0),'shrink':(2,1.0),'minwidth':(3,0)})
 for i in [1001,1002,1004]:fixed(s,rr[bm[i]]['data'],185)
 changed[W][o.path_id]=d;changed[W][so.path_id]=s
 details.append({'name':name,'row':row['rid'],'header_root':hm[1001],'banner_root':bm[1001]})

# Collapse the original assets only after the independent copies have been made.
for bundle,pid in [(W,5775949770471550939),(G,-4194025542157271532)]:
 doc=obs[bundle][pid].read_typetree();ss=obs[bundle][doc['inlineSheet']['m_PathID']].read_typetree()
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
    array={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}.get(h['m_ValueType'])
    if array:assert 0<=h['valueIndex']<len(s[array])
catalog_data=register_functions()
(OUT/'modified/catalog.bin').write_bytes(catalog_data)
manifest={'installed':False,'runtime_verified':False,'height':185,'targets':details,'files':{}}
for n in [G,W]:
 for i,d in changed[n].items():
  if 'm_VisualTree' in d:validate(d,changed[n].get(d['inlineSheet']['m_PathID'],obs[n][d['inlineSheet']['m_PathID']].read_typetree()))
  obs[n][i].save_typetree(d)
 data=envs[n].file.save(packer='lz4');(OUT/'modified'/n).write_bytes(data)
 saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(obs[n])
 for i,o in saved.items():
  if i in changed[n]:assert o.read_typetree()==changed[n][i],(n,i)
  elif i in imported_ids[n]:
   actual=o.read_typetree();expected=imported_docs[n][i]
   if actual!=expected:
    (OUT/'expected.json').write_text(json.dumps(expected,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'actual.json').write_text(json.dumps(actual,ensure_ascii=False,indent=2),encoding='utf-8')
    print('DIFF',i,expected.get('m_Name'),str(OUT));raise AssertionError((n,i))
  else:assert sha(o.get_raw_data())==hashes[n][i],(n,i)
 manifest['files'][n]={'skin_before':sha(sources[n]),'game_before':sha(game_before[n]),'after':sha(data),'changed_objects':list(changed[n]),'unrelated_verified':len(obs[n])-len(changed[n])-len(imported_ids[n]),'imported_objects':len(imported_ids[n])}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
assert catalog_path.read_bytes()==catalog_before
for n in [G,W]:assert (P/n).read_bytes()==sources[n] and (GAME/n).read_bytes()==game_before[n]
try:
 for target in [P,GAME]:
  for n in [G,W]:
   data=(OUT/'modified'/n).read_bytes();(target/n).write_bytes(data);assert sha((target/n).read_bytes())==manifest['files'][n]['after']
 catalog_path.write_bytes(catalog_data)
 assert catalog_path.read_bytes()==catalog_data
except Exception:
 catalog_path.write_bytes(catalog_before)
 for n in [G,W]:(P/n).write_bytes(sources[n]);(GAME/n).write_bytes(game_before[n])
 raise
manifest['catalog_before']=sha(catalog_before);manifest['catalog_after']=sha(catalog_data);manifest['functions_registered']=functions_to_register
manifest['installed']=True
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(str(OUT));print(json.dumps(manifest,indent=2))
