import copy,datetime,hashlib,importlib.util,json,sys,uuid
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle'
OUT=R/('概览1080紧凑布局-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
before={n:(GAME/n).read_bytes() for n in [G,W,L]}
skin_before={n:(SKIN/n).read_bytes() if (SKIN/n).exists() else None for n in before}
for tag,data in [('backup-game',before),('backup-skin',skin_before)]:
 (OUT/tag).mkdir()
 for n,b in data.items():
  if b is not None:(OUT/tag/n).write_bytes(b)
(OUT/'modified').mkdir()
catpath=GAME.parent/'catalog.bin';catbefore=catpath.read_bytes();(OUT/'backup-game/catalog.bin').write_bytes(catbefore)
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);catalog=mod.Catalog(catbefore)
envs={n:UnityPy.load(b) for n,b in before.items()};obs={n:{o.path_id:o for o in e.objects} for n,e in envs.items()}
original_hashes={n:{i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in obs.items()}
modified={n:{} for n in before};added={n:{} for n in before};clones=[];next_id=-930000000001000
oldwrite=TypeTreeHelper.write_value
def write(v,node,writer,config):
 if node.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,config.assetsfile) is None:
  for ch in node.m_Children:
   if ch.m_Type!='ReferencedObjectData':oldwrite(v[ch.m_Name],ch,writer,config)
  if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):writer.align_stream()
  return
 return oldwrite(v,node,writer,config)
TypeTreeHelper.write_value=write
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def byname(n,name):return next(o for o in obs[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
guid_index={}
for n,e in envs.items():
 for k,v in e.container.items():
  if v.path_id in obs[n] and obs[n][v.path_id].type.name=='MonoBehaviour':
   d=obs[n][v.path_id].read_typetree()
   if 'm_VisualTree' in d:guid_index[k]=(n,v.path_id)
def newobj(n,source,doc):
 global next_id
 af=source.assets_file;pid=next_id;next_id-=1
 assert pid not in af.objects
 obj=copy.copy(source);obj.path_id=pid;obj.assets_file=af
 af.objects[pid]=obj;obs[n][pid]=obj;added[n][pid]=doc
 return pid
def clone_tree(n,pid,label):
 source=obs[n][pid];d=copy.deepcopy(source.read_typetree());sheetobj=obs[n][d['inlineSheet']['m_PathID']];s=copy.deepcopy(sheetobj.read_typetree())
 spid=newobj(n,sheetobj,s);d['inlineSheet']={'m_FileID':0,'m_PathID':spid};d['m_Name']='Overview1080_'+label;s['m_Name']='Overview1080_'+label+'_Style'
 tpid=newobj(n,source,d);guid=uuid.uuid5(uuid.NAMESPACE_URL,'fm-overview1080-v1/'+label).hex
 original_guid=next(k for k,(bn,i) in guid_index.items() if bn==n and i==pid)
 clones.append({'bundle':n,'pid':tpid,'style':spid,'guid':guid,'source_guid':original_guid,'label':label})
 return d,s,tpid,guid
IDS=dict(height=131087,minheight=131096,maxheight=131094,width=131105,minwidth=131097,
 grow=131084,shrink=131085,direction=131083,align=131073,self=131074,justify=131088,
 margin=262150,padding=262151,mt=131093,mb=131090,pt=131101,pb=131098,display=131081,overflow=458768)
def style(s,node,props):
 prior=node.get('m_RuleIndex',-1);rule=copy.deepcopy(s['m_Rules'][prior]) if prior>=0 else {'m_ComplexSelectors':[],'m_Properties':[],'line':-1}
 for key,(typ,value) in props.items():
  pid=IDS[key];rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id']!=pid]
  if typ==1:h={'m_ValueType':1,'valueIndex':value}
  else:
   array={2:'floats',3:'dimensions',7:'strings'}[typ]
   if typ==3:value={'unit':1,'value':float(value)}
   s[array].append(value);h={'m_ValueType':typ,'valueIndex':len(s[array])-1}
  rule['m_Properties'].append({'m_Id':pid,'m_CustomName':'','m_Line':-1,'m_Values':[h]})
 node['m_RuleIndex']=len(s['m_Rules']);s['m_Rules'].append(rule)
def sd(d,node):return refs(d)[node['data']['m_SerializedData']['rid']]['data']
def named(d,name):
 rr=refs(d)
 return next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name)
def using(d,alias,guid):
 entry=next(u for u in d['m_Usings'] if u['alias']==alias);entry['path']=guid;entry['asset']={'m_FileID':0,'m_PathID':0}

# Isolate the row and attribute table so other game pages keep their current styles.
rn,rpid=guid_index['6ed52c9bc6bcab046a22d7537e32f961'];row,rs,_,rowguid=clone_tree(rn,rpid,'AttributeRow24')
for r in refs(row).values():
 a=r.get('data',{})
 if 'm_RuleIndex' not in a or a.get('m_FullTypeName')=='UnityEngine.UIElements.UXML':continue
 if a.get('m_Parent',{}).get('rid')==1000 or 'attributes-row-number' in a.get('m_Classes',[]):
  a['m_Classes']=[c for c in a['m_Classes'] if c!='height-28' and not c.startswith('margin-vertical-')]
  style(rs,a,{'height':(3,24),'minheight':(3,24),'maxheight':(3,24),'mt':(3,0),'mb':(3,0),'pt':(3,0),'pb':(3,0),'shrink':(2,0.0)})
tn,tpid=guid_index['faa627c7e02762847b92be132216db17'];table,ts,_,tableguid=clone_tree(tn,tpid,'AttributesTable')
tr=refs(table);hidden=[];lists=[]
for r in tr.values():
 a=r.get('data',{});debug=a.get('DebugDisplay')
 if debug in ['Technical','Mental','Physical']:
  node=next(x for x in tr.values() if x.get('data',{}).get('m_SerializedData',{}).get('rid')==r['rid'])
  style(ts,node['data'],{'display':(7,'none'),'height':(3,0),'minheight':(3,0),'maxheight':(3,0),'margin':(3,0),'padding':(3,0)})
  hidden.append(debug)
 if r['type']['class']=='StreamedObjectList/UxmlSerializedData' and a.get('RowTemplate',{}).get('m_AssetGUID')=='6ed52c9bc6bcab046a22d7537e32f961':
  a['RowTemplate']['m_AssetGUID']=rowguid;a['FixedElementSize']=24.0;a['FixedElementSize_UxmlAttributeFlags']=1
  node=next(x for x in tr.values() if x.get('data',{}).get('m_SerializedData',{}).get('rid')==r['rid'])
  count=a['NumPreviewElements'];style(ts,node['data'],{'height':(3,count*24),'minheight':(3,count*24),'shrink':(2,0.0),'mt':(3,0),'mb':(3,0)})
  lists.append({'rows':count,'height':count*24})
assert set(hidden)=={'Technical','Mental','Physical'} and len(lists)==8

main,ms,mainpid,mainguid=clone_tree(W,7199728689344018492,'PlayerAttributesLargeBlock')
using(main,'AttributesTableTemplate',tableguid)
mr=refs(main)
style(ms,mr[1001]['data'],{'minheight':(3,700),'grow':(2,1.0),'direction':(7,'column')})
# Preserve the 250px header and allocate all remaining space to the actual attributes.
style(ms,mr[1002]['data'],{'minheight':(3,438),'grow':(2,1.0),'shrink':(2,1.0),'mt':(3,8),'pt':(3,0),'pb':(3,0)})
assert sd(main,named(main,'ReportMiddleCA000Layer'))['name']=='ReportMiddleCA000Layer'

# Obtain the game's own scroll view serialization rather than inventing a control.
scroll_sample=None;scroll_file=None
for bn in [G,W]:
 for obj in list(obs[bn].values()):
  if obj.type.name!='MonoBehaviour':continue
  doc=obj.read_typetree()
  ref=next((r for r in doc.get('references',{}).get('RefIds',[]) if r['type']['class']=='SIScrollView/UxmlSerializedData'),None)
  if ref:scroll_sample=copy.deepcopy(ref);scroll_file=obj.assets_file;break
 if scroll_sample:break
assert scroll_sample
worldaf=obs[W][7199728689344018492].assets_file
known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in worldaf.ref_types}
for t in scroll_file.ref_types:
 k=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
 if k not in known:worldaf.ref_types.append(copy.copy(t));known.add(k)
def wrap_scroll(d,s,child,parent,label):
 rr=refs(d);rid=max(rr)+1;oldnode=rr[child];oldparent=rr[parent]
 wrapper=copy.deepcopy(oldnode);wrapper['rid']=rid;wrapper['type']={'class':'VisualElementAsset','ns':'UnityEngine.UIElements','asm':'UnityEngine.UIElementsModule'}
 wrapper['data']={k:copy.deepcopy(v) for k,v in named(main,'MovedPlayerReportHeader')['data'].items()}
 wrapper['data'].update(m_FullTypeName='SI.UI.SIScrollView',m_Id=2110000000+rid,m_Parent={'rid':parent},m_Children=[{'rid':child}],m_Classes=['flex-grow-class','align-self-stretch'],m_RuleIndex=-1,m_SerializedData={'rid':rid+1})
 serial=copy.deepcopy(scroll_sample);serial['rid']=rid+1
 serial['data'].update(uxmlAssetId=2110000000+rid,name=label,name_UxmlAttributeFlags=1,mode=0,mode_UxmlAttributeFlags=1,horizontalScrollerVisibility=2,horizontalScrollerVisibility_UxmlAttributeFlags=1,verticalScrollerVisibility=0,verticalScrollerVisibility_UxmlAttributeFlags=1,showHorizontal=0,showHorizontal_UxmlAttributeFlags=1)
 index=oldparent['data']['m_Children'].index({'rid':child});oldparent['data']['m_Children'][index]={'rid':rid};oldnode['data']['m_Parent']={'rid':rid}
 d['references']['RefIds'].extend([wrapper,serial]);style(s,wrapper['data'],{'minheight':(3,0),'grow':(2,1.0),'shrink':(2,1.0)})
 return wrapper
# The right information column may contain arbitrarily many traits or bans.
info=named(main,'InfoBlockFrame');ir=info['rid'];ip=info['data']['m_Parent']['rid'];iw=wrap_scroll(main,ms,ir,ip,'OverviewInfoScroll')
iw['data']['m_Classes']=copy.deepcopy(info['data']['m_Classes']);iw['data']['m_RuleIndex']=info['data']['m_RuleIndex']
style(ms,iw['data'],{'minheight':(3,0),'grow':(2,1.0),'shrink':(2,1.0)})
style(ms,info['data'],{'width':(1,2),'minheight':(3,0),'mt':(3,0),'mb':(3,0)})

# A private tile frame removes excess title/content padding from all six lower cards.
fn,fp=guid_index['f677caec43d6c1342b1bba39c5ae2c5f'];frame,fs,_,frameguid=clone_tree(fn,fp,'CompactTileFrame')
fr=refs(frame)
for i in [1001,1002,1004,1006,1008]:style(fs,fr[i]['data'],{'minheight':(3,0),'grow':(2,1.0),'pt':(3,0),'pb':(3,0)})
fr[1006]['data']['m_Classes']=[c for c in fr[1006]['data']['m_Classes'] if c!='height-100-px']
style(fs,fr[1011]['data'],{'height':(3,26),'minheight':(3,26),'maxheight':(3,26),'pt':(3,0),'pb':(3,0),'mt':(3,0),'mb':(3,2)})
style(fs,fr[1012]['data'],{'minheight':(3,0),'grow':(2,1.0),'pt':(3,4),'pb':(3,4)})

composition_obj=byname(L,'PlayerReportOverviewComposition-Large');composition=copy.deepcopy(composition_obj.read_typetree())
bottom_details=[]
for component in composition['m_gridComponents']:
 config=component['m_gridElementConfigs'][0]
 if component['m_elementID']=='PlayerAttributesBlock':
  config['AssetRef']['m_AssetGUID']=mainguid;config['Size']['y']=7
  component['m_location']['height']=7;component['m_minSize']['y']=7;component['m_expandToContent']=0
 else:
  oldguid=config['AssetRef']['m_AssetGUID'];bn,bpid=guid_index[oldguid]
  doc,s,_,guid=clone_tree(bn,bpid,'Compact_'+component['m_elementID'])
  for u in doc['m_Usings']:
   if u['path']=='f677caec43d6c1342b1bba39c5ae2c5f':u['path']=frameguid;u['asset']={'m_FileID':0,'m_PathID':0}
  rr=refs(doc)
  for r in list(rr.values()):
   a=r.get('data',{})
   if 'm_RuleIndex' not in a or a.get('m_FullTypeName')=='UnityEngine.UIElements.UXML':continue
   if a.get('m_Parent',{}).get('rid')==1000:style(s,a,{'minheight':(3,0),'maxheight':(3,154),'pt':(3,0),'pb':(3,0)})
   a['m_Classes']=[c for c in a.get('m_Classes',[]) if c not in ['margin-bottom-global-gap-large','margin-top-global-gap-large','margin-vertical-global-gap-large']]
   if 'margin-bottom-global-gap-regular' in a.get('m_Classes',[]):style(s,a,{'mb':(3,2)})
   # Content inserted into the tile frame's content slot gets a local scroll viewport.
   par=rr.get(a.get('m_Parent',{}).get('rid'),{}).get('data',{})
   if a.get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement' and par.get('m_TemplateAlias','').startswith('tile-'):
    wrap_scroll(doc,s,r['rid'],a['m_Parent']['rid'],'OverviewCardContentScroll')
    style(s,a,{'minheight':(3,0),'pt':(3,0),'pb':(3,0),'mt':(3,0),'mb':(3,0)})
  config['AssetRef']['m_AssetGUID']=guid;config['Size']['y']=1
  component['m_location']['y']=7;component['m_location']['height']=1
  component['m_minSize']['y']=1;component['m_maxSize']['y']=1;component['m_expandToContent']=0
  bottom_details.append(component['m_elementID'])
modified[L][composition_obj.path_id]=composition
assert len(bottom_details)==6

# Register private assets without changing the public/native templates.
for n in [G,W]:
 ab=next(o for o in obs[n].values() if o.type.name=='AssetBundle');meta=copy.deepcopy(ab.read_typetree())
 for c in [c for c in clones if c['bundle']==n]:
  doc=added[n][c['pid']];start=len(meta['m_PreloadTable']);meta['m_PreloadTable'].extend([copy.deepcopy(doc['m_Script']),{'m_FileID':0,'m_PathID':c['style']},{'m_FileID':0,'m_PathID':c['pid']}])
  meta['m_Container'].append((c['guid'],{'preloadIndex':start,'preloadSize':3,'asset':{'m_FileID':0,'m_PathID':c['pid']}}))
  location=next(l for l in catalog.locations(c['source_guid']) if catalog.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
  catalog=mod.Catalog(catalog.add_key_location(c['guid'],location,location))
 meta['m_Container'].sort(key=lambda kv:kv[0]);modified[n][ab.path_id]=meta
def validate_ui(d):
 rr=refs(d);assert len(rr)==len(d['references']['RefIds']);seen=set();aliases={u['alias'] for u in d['m_Usings']}
 def visit(i):
  assert i not in seen;seen.add(i)
  for ch in rr[i].get('data',{}).get('m_Children',[]):assert rr[ch['rid']]['data']['m_Parent']['rid']==i;visit(ch['rid'])
 visit(d['m_VisualTree']['rid'])
 for r in rr.values():
  a=r.get('data',{})
  if 'm_Parent' in a:assert r['rid'] in seen
  if a.get('templateId_UxmlAttributeFlags')==1 and a.get('templateId'):assert a['templateId'] in aliases
for n in [G,W,L]:
 for i,d in {**added[n],**modified[n]}.items():
  if 'm_VisualTree' in d:validate_ui(d)
  obs[n][i].save_typetree(d)
 data=envs[n].file.save(packer='lz4');(OUT/'modified'/n).write_bytes(data)
 saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(obs[n])
 for i,o in saved.items():
  if i in added[n]:assert o.read_typetree()==added[n][i],(n,i)
  elif i in modified[n]:assert o.read_typetree()==modified[n][i],(n,i)
  else:assert sha(o.get_raw_data())==original_hashes[n][i],(n,i)
catdata=bytes(catalog.data);(OUT/'modified/catalog.bin').write_bytes(catdata)
assert all(catalog.locations(c['guid']) for c in clones)
report={'installed':False,'runtime_verified':False,'target':'1920x1080 Large breakpoint','row_height':24,'hidden_titles':hidden,'lists':lists,'lower_cards':bottom_details,'private_templates':clones,'files':{}}
for n in before:
 report['files'][n]={'before':sha(before[n]),'after':sha((OUT/'modified'/n).read_bytes()),'original_objects_changed':list(modified[n]),'private_objects_added':len(added[n]),'unrelated_original_objects_verified':len(original_hashes[n])-len(modified[n])}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for n in before:assert (GAME/n).read_bytes()==before[n]
assert catpath.read_bytes()==catbefore
for n,b in skin_before.items():assert ((SKIN/n).read_bytes() if (SKIN/n).exists() else None)==b
try:
 for n in before:
  data=(OUT/'modified'/n).read_bytes()
  for p in [GAME,SKIN]:(p/n).write_bytes(data);assert sha((p/n).read_bytes())==sha(data)
 catpath.write_bytes(catdata);assert catpath.read_bytes()==catdata
except Exception:
 for n,b in before.items():(GAME/n).write_bytes(b)
 for n,b in skin_before.items():
  if b is not None:(SKIN/n).write_bytes(b)
  elif (SKIN/n).exists():(SKIN/n).unlink()
 catpath.write_bytes(catbefore);raise
report['installed']=True;report['catalog_before']=sha(catbefore);report['catalog_after']=sha(catdata)
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(OUT));print(json.dumps({'installed':True,'row_height':24,'title_nodes_hidden':len(hidden),'private_templates':len(clones),'lower_cards':len(bottom_details),'files':report['files']},indent=2))
