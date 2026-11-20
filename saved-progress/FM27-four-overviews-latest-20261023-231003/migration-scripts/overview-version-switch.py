import copy,datetime,hashlib,importlib.util,json,sys,uuid
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle'
OUT=R/('概览双版本切换-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
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
 spid=newobj(n,sheetobj,s);d['inlineSheet']={'m_FileID':0,'m_PathID':spid};d['m_Name']='OverviewToggle_'+label;s['m_Name']='OverviewToggle_'+label+'_Style'
 tpid=newobj(n,source,d);guid=uuid.uuid5(uuid.NAMESPACE_URL,'fm-overview-toggle-v1/'+label).hex
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

composition_obj=byname(L,'PlayerReportOverviewComposition-Large')
composition=copy.deepcopy(composition_obj.read_typetree())
slot=next(c for c in composition['m_gridComponents'] if c['m_elementID']=='PlayerAttributesBlock')
baseguid=slot['m_gridElementConfigs'][0]['AssetRef']['m_AssetGUID'];bn,basepid=guid_index[baseguid]
assert bn==W
original=obs[W][basepid].read_typetree()
full,fullstyle,fullpid,fullguid=clone_tree(W,basepid,'FullOverview')
simple,simplestyle,simplepid,simpleguid=clone_tree(W,basepid,'PortraitAttributes')

# Preserve an existing functioning portrait template before removing the original header.
origrefs=refs(original)
picture_node=next(r for r in origrefs.values() if r.get('data',{}).get('m_TemplateAlias')=='MovedHeader_PersonPicture')
picture_sd=origrefs[picture_node['data']['m_SerializedData']['rid']]
head=named(simple,'FrameActions');rr=refs(simple);remove=set()
def remove_references(i):
 if i==-2 or i in remove:return
 remove.add(i)
 def walk(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:remove_references(v['rid'])
   else:
    for k,a in v.items():
     if k!='m_Parent':walk(a)
  elif isinstance(v,list):
   for a in v:walk(a)
 walk(rr[i].get('data',{}))
remove_references(head['rid'])
parent=rr[head['data']['m_Parent']['rid']]
place=parent['data']['m_Children'].index({'rid':head['rid']})
parent['data']['m_Children'].remove({'rid':head['rid']})
simple['references']['RefIds']=[r for r in simple['references']['RefIds'] if r['rid'] not in remove]
assert parent['rid'] not in remove
rr=refs(simple);start=max(rr)+1
row=copy.deepcopy(head);row['rid']=start
row['data'].update(m_Id=2120000000+start,m_Parent={'rid':parent['rid']},m_Children=[{'rid':start+2}],m_Classes=['row-direction-normal','align-self-stretch','flex-no-shrink-class'],m_RuleIndex=-1,m_SerializedData={'rid':start+1})
rowsd=copy.deepcopy(origrefs[head['data']['m_SerializedData']['rid']]);rowsd['rid']=start+1
rowsd['data'].update(uxmlAssetId=2120000000+start,name='SimplePortraitHeader',name_UxmlAttributeFlags=1)
pic=copy.deepcopy(picture_node);pic['rid']=start+2
pic['data'].update(m_Id=2120000002+start,m_Parent={'rid':start},m_Classes=['flex-no-shrink-class'],m_RuleIndex=-1,m_SerializedData={'rid':start+3})
picsd=copy.deepcopy(picture_sd);picsd['rid']=start+3
picsd['data'].update(uxmlAssetId=2120000002+start,name='SimplePortrait',name_UxmlAttributeFlags=1)
parent['data']['m_Children'].insert(place,{'rid':start})
simple['references']['RefIds'].extend([row,rowsd,pic,picsd])
style(simplestyle,row['data'],{'height':(3,140),'minheight':(3,140),'maxheight':(3,140),'grow':(2,0.0),'shrink':(2,0.0),'align':(7,'center'),'padding':(3,4),'mb':(3,8)})
style(simplestyle,pic['data'],{'width':(3,120),'height':(3,120),'minheight':(3,120),'maxheight':(3,120),'shrink':(2,0.0)})

# Use the same native tile frame as the lower cards; the grid supplies its menu context.
bottom_source=byname(W,'PlayerHappinessTile_2x2').read_typetree();brr=refs(bottom_source)
frame_node=next(r for r in brr.values() if r.get('data',{}).get('m_TemplateAlias')=='tile-square-2x2')
frame_sd=brr[frame_node['data']['m_SerializedData']['rid']]
for d,s,label in [(full,fullstyle,'FullOverviewFrame'),(simple,simplestyle,'PortraitAttributesFrame')]:
 rr=refs(d);root=rr[d['m_VisualTree']['rid']];children=copy.deepcopy(root['data']['m_Children']);i=max(rr)+1
 node=copy.deepcopy(frame_node);serial=copy.deepcopy(frame_sd);node['rid']=i;serial['rid']=i+1
 node['data'].update(m_Id=2121000000+i,m_Parent={'rid':root['rid']},m_Children=children,m_Classes=['height-100-percent','flex-grow-class'],m_RuleIndex=-1,m_SerializedData={'rid':i+1},m_TemplateAlias='OverviewVersionTileFrame',m_AttributeOverrides=[],m_SerializedDataOverride=[])
 serial['data'].update(uxmlAssetId=2121000000+i,name=label,name_UxmlAttributeFlags=1,templateId='OverviewVersionTileFrame',templateId_UxmlAttributeFlags=1)
 root['data']['m_Children']=[{'rid':i}]
 for ch in children:rr[ch['rid']]['data']['m_Parent']={'rid':i}
 d['references']['RefIds'].extend([node,serial]);d['m_Usings'].append({'alias':'OverviewVersionTileFrame','path':'f677caec43d6c1342b1bba39c5ae2c5f','asset':{'m_FileID':0,'m_PathID':0}})
 style(s,node['data'],{'minheight':(3,0),'grow':(2,1.0),'padding':(3,0)})
 # Leave native frame room for its title and top-right version arrow.
 style(s,rr[1001]['data'],{'minheight':(3,674),'grow':(2,1.0)})

# Each content choice gets its own native description, using existing localized titles.
description_source=obs[L][6067656787038004271]
descriptions=[]
for ident,label,gameid,guid in [('PlayerOverviewFull','FullOverview',14593,fullguid),('PlayerOverviewSimple','PortraitAttributes',40162,simpleguid)]:
 d=copy.deepcopy(description_source.read_typetree());d['m_Name']='OverviewToggle_'+label+'Description'
 d['<Name>k__BackingField']=ident;d['<ID>k__BackingField']=ident;d['<DisplayName>k__BackingField']={'GameID':gameid}
 config=copy.deepcopy(slot['m_gridElementConfigs'][0]);config['Size']={'x':20,'y':7};config['AssetRef']['m_AssetGUID']=guid;config['Type']=0
 pid=newobj(L,description_source,d);config['Description']={'m_FileID':0,'m_PathID':pid}
 d['<Configurations>k__BackingField']=[copy.deepcopy(config)];d['<DefaultConfigIndex>k__BackingField']=0
 descriptions.append({'id':ident,'pid':pid,'config':config,'title_gameid':gameid})
slot['m_configDescriptions']=[{'m_FileID':0,'m_PathID':x['pid']} for x in descriptions]
slot['m_configDescriptionKeys']=[];slot['m_gridElementConfigs']=[x['config'] for x in descriptions]
slot['m_isLocked']=0
modified[L][composition_obj.path_id]=composition
tile_set_obj=byname(L,'PlayerReportOverviewTileSet');tile_set=copy.deepcopy(tile_set_obj.read_typetree())
tile_set['m_gridElementDescriptions'].extend([{'m_FileID':0,'m_PathID':x['pid']} for x in descriptions]);modified[L][tile_set_obj.path_id]=tile_set

# Both alternatives inherit precisely the player/team/human bindings of the original slot.
page_obj=obs[W][7857044477279960178];page=copy.deepcopy(page_obj.read_typetree())
grid=next(r['data'] for r in page['references']['RefIds'] if r.get('data',{}).get('Bindings',{}).get('m_gridCompositionSet',{}).get('m_PathID')==1615455816372668659)
bindings=grid['Bindings'];binding_copies=0
def description_refs(v):
 if isinstance(v,dict):
  return ([v] if 'DescriptionName' in v else [])+[x for a in v.values() for x in description_refs(a)]
 if isinstance(v,list):return [x for a in v for x in description_refs(a)]
 return []
for key,items in bindings.items():
 if not isinstance(items,list):continue
 originals=[x for x in items if any(z['DescriptionName']=='PlayerAttributesBlock' for z in description_refs(x))]
 for choice in descriptions:
  for item in originals:
   dup=copy.deepcopy(item)
   for z in description_refs(dup):
    if z['DescriptionName']=='PlayerAttributesBlock':z['DescriptionName']=choice['id'];binding_copies+=1
   items.append(dup)
modified[W][page_obj.path_id]=page
assert binding_copies>0

# Register only the two new UI assets; their styles remain local dependencies.
ab=next(o for o in obs[W].values() if o.type.name=='AssetBundle');meta=copy.deepcopy(ab.read_typetree())
for c in clones:
 assert c['bundle']==W
 doc=added[W][c['pid']];start=len(meta['m_PreloadTable']);meta['m_PreloadTable'].extend([copy.deepcopy(doc['m_Script']),{'m_FileID':0,'m_PathID':c['style']},{'m_FileID':0,'m_PathID':c['pid']}])
 meta['m_Container'].append((c['guid'],{'preloadIndex':start,'preloadSize':3,'asset':{'m_FileID':0,'m_PathID':c['pid']}}))
 location=next(l for l in catalog.locations(c['source_guid']) if catalog.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
 catalog=mod.Catalog(catalog.add_key_location(c['guid'],location,location))
meta['m_Container'].sort(key=lambda kv:kv[0]);modified[W][ab.path_id]=meta

def validate_ui(d):
 rr=refs(d);assert len(rr)==len(d['references']['RefIds']);aliases={u['alias'] for u in d['m_Usings']};seen=set()
 def visit(i):
  assert i not in seen;seen.add(i)
  for child in rr[i].get('data',{}).get('m_Children',[]):assert rr[child['rid']]['data']['m_Parent']['rid']==i;visit(child['rid'])
 visit(d['m_VisualTree']['rid'])
 def scan(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:assert v['rid'] in rr,v
   else:
    for a in v.values():scan(a)
  elif isinstance(v,list):
   for a in v:scan(a)
 scan(d)
 for r in rr.values():
  a=r.get('data',{})
  if 'm_Parent' in a:assert r['rid'] in seen
  if a.get('templateId_UxmlAttributeFlags')==1 and a.get('templateId'):assert a['templateId'] in aliases
validate_ui(full);validate_ui(simple)
assert any(r.get('data',{}).get('name')=='FrameActions' for r in refs(full).values())
assert not any(r.get('data',{}).get('name')=='FrameActions' for r in refs(simple).values())
report={'installed':False,'runtime_verified':False,'choices':descriptions,'binding_copies':binding_copies,'private_templates':clones,'files':{}}
for n in [W,L]:
 for i,d in {**added[n],**modified[n]}.items():
  if 'm_VisualTree' in d:validate_ui(d)
  obs[n][i].save_typetree(d)
 data=envs[n].file.save(packer='lz4');(OUT/'modified'/n).write_bytes(data)
 saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(obs[n])
 for i,obj in saved.items():
  if i in added[n]:assert obj.read_typetree()==added[n][i],(n,i)
  elif i in modified[n]:assert obj.read_typetree()==modified[n][i],(n,i)
  else:assert sha(obj.get_raw_data())==original_hashes[n][i],(n,i)
 report['files'][n]={'before':sha(before[n]),'after':sha(data),'original_changed':list(modified[n]),'added':len(added[n]),'unrelated_verified':len(original_hashes[n])-len(modified[n])}
catdata=bytes(catalog.data);(OUT/'modified/catalog.bin').write_bytes(catdata)
for n in [W,L]:assert (GAME/n).read_bytes()==before[n]
assert catpath.read_bytes()==catbefore
for n in [W,L]:assert (SKIN/n).read_bytes()==skin_before[n]
try:
 for n in [W,L]:
  data=(OUT/'modified'/n).read_bytes()
  for target in [GAME,SKIN]:(target/n).write_bytes(data);assert sha((target/n).read_bytes())==sha(data)
 catpath.write_bytes(catdata);assert catpath.read_bytes()==catdata
except Exception:
 for n in [W,L]:(GAME/n).write_bytes(before[n]);(SKIN/n).write_bytes(skin_before[n])
 catpath.write_bytes(catbefore);raise
report['installed']=True;report['catalog_before']=sha(catbefore);report['catalog_after']=sha(catdata)
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(OUT));print(json.dumps({'installed':True,'choices':[x['id'] for x in descriptions],'binding_copies':binding_copies,'files':report['files']},indent=2))

