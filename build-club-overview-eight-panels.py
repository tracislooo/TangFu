"""Club-specific eight-panel dashboard, migrated separately onto current game/skin."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,os,re,struct,subprocess,sys,uuid
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
source=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'codec','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
source=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
source=ast.parse((R/'build-match-ui-avatars-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['refs','sd','find','pointer_remap','import_types'] or isinstance(n,ast.ClassDef) and n.name=='Doc'],type_ignores=[]),'doc-helpers','exec'))
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(cfg['bundle_root']);SKIN=Path(cfg['skin_packages'])
assert 'Football Manager 27' in str(GAME) and 'Project Taco' not in str(GAME)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle';NAMES=[W,G,L]
sha=lambda b:hashlib.sha256(b).hexdigest()
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
ROOTOUT=R/('club-overview-eight-panels-'+stamp);ROOTOUT.mkdir()
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];banned={int(x['path_id']) for x in reserved}|{-910000000000001,-910000000000002,-910000000000146}
protected={};tx=[];audits=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 OUT=ROOTOUT/tag;OUT.mkdir();(OUT/'templates').mkdir();backup=ROOTOUT/('backup-'+tag);backup.mkdir()
 before={n:(folder/n).read_bytes() for n in NAMES}
 env={n:UnityPy.load(b) for n,b in before.items()};objs={n:{o.path_id:o for o in e.objects} for n,e in env.items()}
 hashes={n:{i:sha(o.get_raw_data()) for i,o in obs.items()} for n,obs in objs.items()};changes={n:{} for n in NAMES};documents=[];clones=[]
 catpath=(folder.parent if tag=='game' else folder)/'catalog.bin';hashpath=catpath.with_suffix('.hash');catbefore=catpath.read_bytes();cathashbefore=hashpath.read_bytes()
 metas={n:next(o.read_typetree() for o in objs[n].values() if o.type.name=='AssetBundle') for n in NAMES}
 def guidof(n,pid):return next(k for k,v in metas[n]['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':pid})
 def clone(n,name,newname,pid):
  src=Doc(n,name=name);d=copy.deepcopy(src.d);s=copy.deepcopy(src.s);d['m_Name']=newname;s['m_Name']=newname+'Style';d['inlineSheet']['m_PathID']=pid-1
  for so,j,tr in [(src.obj,pid,d),(objs[n][src.sid],pid-1,s)]:
   assert j not in objs[n] and j not in banned
   o=copy.copy(so);o.path_id=j;o.data=None;o._read_until=None;o.assets_file.objects[j]=o;objs[n][j]=o;o.save_typetree(tr);changes[n][j]=copy.deepcopy(tr)
  guid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/club-eight-panels/'+newname).hex
  clones.append({'bundle':n,'pid':pid,'style':pid-1,'guid':guid,'source_guid':guidof(n,src.obj.path_id)})
  return Doc(n,pid=pid,tree=d,style=s),guid
 def flex(d,i,grow=1):
  d.st(i,[(131105,d.pct(100)),(131097,d.px(0)),(131087,d.px(0)),(131096,d.px(0)),(131084,d.num(grow)),(131085,d.num(1)),(458768,d.enum('hidden'))])
 def ve(d,parent,name,row=False):
  donor=Doc(W,name='ClubSiteBlock');i=d.add(donor,1014,parent,name)
  d.st(i,[(131083,d.enum('row' if row else 'column')),(131097,d.px(0)),(131096,d.px(0)),(131085,d.num(1))]);return i
 templdonor=Doc(W,name='ClubSiteHeader')
 def template(d,parent,name,guid,alias=None):
  alias=alias or name;i=d.add(templdonor,1012,parent,name)
  d.a(i).update(m_TemplateAlias=alias,m_AttributeOverrides=[],m_SerializedDataOverride=[],m_SlotUsages=[]);d.data(i)['templateId']=alias
  d.d['m_Usings'].append({'alias':alias,'path':guid,'asset':{'m_FileID':0,'m_PathID':0}});flex(d,i);return i
 def title(d,parent,label,translation=None,source=None,rid=None):
  donor=source or Doc(W,name='ClubSiteBlock');i=d.add(donor,rid or 1118,parent,label+'Heading');sd=d.data(i)
  if translation is not None:
   raw=bytearray(sd['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);raw[-5:-1]=struct.pack('<I',translation);sd['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(raw)
  elif source is None:
   sd.update(text=label,text_UxmlAttributeFlags=1,TextBinding_UxmlAttributeFlags=0);sd['TextBinding']['m_kind']=0
  d.a(i)['m_Classes']=['thematic-md','global-text-link','margin-bottom-8','flex-no-shrink-class']
  d.st(i,[(131087,d.px(22)),(131085,d.num(0)),(65537,d.px(14))]);return i
 # Private header children retain every original control ID and override path.
 top,tg=clone(G,'ClubSiteHeaderTemplate','ClubOverviewWideHeaderDetails',-991100000000000)
 top.st(1009,[(131081,top.enum('none'))]);top.st(1006,[(131097,top.px(0)),(131085,top.num(1))])
 top.st(1010,[(131093,top.px(0)),(131090,top.px(12))]);top.save()
 season,sg=clone(G,'ClubSiteHeaderSeasonInformationTemplate','ClubOverviewInsetSeasonCards',-991100000000010)
 flex(season,1001);season.st(1001,[(131087,season.pct(100))]);flex(season,1004);season.st(1004,[(131087,season.pct(100))]);season.st(1006,[(131105,season.pct(100)),(131087,season.pct(100)),(131096,season.px(0))])
 for ch in season.a(1006)['m_Children']:
  i=ch['rid'];season.st(i,[(131105,season.px(0)),(131097,season.px(0)),(131084,season.num(1)),(131085,season.num(1)),(131087,season.pct(100))])
 season.save()
 header,hg=clone(W,'ClubSiteHeader','ClubOverviewLargeCrestHeader',-991100000000020)
 for alias,guid in [('ClubSiteHeaderTemplate',tg),('ClubSiteHeaderSeasonInformationTemplate',sg)]:next(u for u in header.d['m_Usings'] if u['alias']==alias)['path']=guid
 for i in [1001,1004,1006,1010]:
  header.st(i,[(131105,header.pct(100)),(131087,header.pct(100)),(131096,header.px(0)),(131094,header.pct(100)),(131084,header.num(1)),(131085,header.num(1)),(131102,header.enum('relative'))])
 header.st(1006,[(262151,header.px(4))])
 for i,h,y in [(1012,66,0),(1013,100,70)]:
  header.st(i,[(131102,header.enum('absolute')),(131089,header.px(176)),(131103,header.px(0)),(131104,header.px(y)),(131105,{'m_ValueType':1,'valueIndex':2}),(131087,header.px(h)),(131096,header.px(0)),(131084,header.num(0)),(131085,header.num(1))])
 originaltop=Doc(G,name='ClubSiteHeaderTemplate');crest=header.add(originaltop,1009,1010,'ClubOverviewTwoRowCrest');header.using(originaltop,'ClubIcon')
 header.size(crest,160,166);header.st(crest,[(131102,header.enum('absolute')),(131089,header.px(4)),(131104,header.px(0)),(262153,header.enum('scale-to-fit'))]);header.save()
 # Left-bottom stadium: original field bindings in a compact vertical stack.
 stadium,stadg=clone(W,'ClubFacilitiesStadiumBlock','ClubOverviewStadiumStack',-991100000000030)
 for i in [1001,1004,1006,1010]:flex(stadium,i);stadium.st(i,[(131087,stadium.pct(100)),(131083,stadium.enum('column')),(262151,stadium.px(0)),(262148,stadium.px(0))])
 keep_rows={1023,1025,1027,1028,1033,1034}
 for ch in stadium.a(1016)['m_Children']:
  i=ch['rid']
  if i not in keep_rows:stadium.st(i,[(131081,stadium.enum('none'))])
  else:stadium.st(i,[(131087,stadium.px(21)),(131096,stadium.px(21)),(131085,stadium.num(0)),(131105,stadium.pct(100))])
 for i in [1014,1015]:stadium.st(i,[(131081,stadium.enum('none'))])
 stadium.st(1012,[(131087,stadium.px(126)),(131096,stadium.px(126)),(131084,stadium.num(0)),(131085,stadium.num(0))])
 # Native DatabaseTableType.Stadium=21; BindToDatabaseObjectImage handles player packs.
 icon=Doc(W,name='ClubIcon');imgdonor=next(i for i,x in icon.r.items() if x.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIImage')
 photo=stadium.add(icon,imgdonor,1010,'ClubOverviewStadiumPackPhoto');ps=stadium.data(photo)
 functionpath=folder/'ui-visualfunctions_assets_all.bundle'
 if not functionpath.exists():functionpath=GAME/'ui-visualfunctions_assets_all.bundle'
 fa=UnityPy.load(functionpath.read_bytes()).assets[0]
 fm=next(o.read_typetree() for o in fa.objects.values() if o.type.name=='AssetBundle');fguid=next(k for k,v in fm['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':639978368030298025})
 def argblob(args):return list(bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args))
 path=b'club.MainTeam.Stadium.UniqueId'
 argpath=bytes([62])+b'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'+bytes([1,len(path)])+path
 assert len(b'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]')==62
 enumtype=b'SI.VisualScripting.EnumVisualArg`1[FM.UI.DatabaseTableType]'
 enumarg=bytes([len(enumtype)])+enumtype+struct.pack('<i',21)
 args=[bytes([31])+b'SI.Bindable.BindingKeyVisualArg'+bytes([0]),enumarg,argpath]
 ps['Binding']={'m_kind':2,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':fguid},'m_inputs':{'m_variable':{'m_argumentBytes':argblob(args)}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}}
 ps.update(Binding_UxmlAttributeFlags=1,PlaceholderImagePath='',PlaceholderImagePath_UxmlAttributeFlags=1,ScaleMode=2,ScaleMode_UxmlAttributeFlags=1)
 flex(stadium,photo);stadium.st(photo,[(262153,stadium.enum('scale-to-fit')),(131098,stadium.px(4))]);stadium.save()
 finance,fg=clone(W,'ClubFinancesSummaryBlock','ClubOverviewFinancesPanel',-991100000000040)
 for i in [1001,1002,1004,1006,1009]:flex(finance,i);finance.st(i,[(131087,finance.pct(100)),(262151,finance.px(0))])
 finance.st(1008,[(131085,finance.num(0)),(131087,{'m_ValueType':1,'valueIndex':2}),(131090,finance.px(4))]);finance.st(1021,[(65537,finance.px(19))])
 finance.st(1009,[(131087,finance.px(0)),(131084,finance.num(1)),(131096,finance.px(0))]);flex(finance,1013);finance.st(1013,[(131087,finance.pct(100)),(262151,finance.px(8))]);finance.save()
 stats,stg=clone(W,'ClubStatsBlock','ClubOverviewTeamStatsPanel',-991100000000050)
 for i in [1001,1004]:flex(stats,i);stats.st(i,[(131087,stats.pct(100)),(262151,stats.px(0))])
 flex(stats,1007);stats.save()
 body,bg=clone(W,'ClubSiteBlock','ClubOverviewEightPanelBody',-991100000000060)
 flex(body,1001);body.st(1001,[(131087,body.pct(100))]);flex(body,1004);body.st(1004,[(131087,body.pct(100))]);flex(body,1007);body.st(1007,[(131087,body.pct(100)),(131083,body.enum('column')),(262151,body.px(8))])
 # Remove the old shortcut branches, so a saved visibility binding cannot reopen them.
 def remove_branch(d,i):
  parent=d.a(i)['m_Parent']['rid'];d.a(parent)['m_Children'].remove({'rid':i});todo=[i];drop=set()
  def managed(v):
   if isinstance(v,dict):
    if set(v)=={'rid'}:
     if v['rid']!=-2:yield v['rid']
    else:
     for k,x in v.items():
      if k!='m_Parent':yield from managed(x)
   elif isinstance(v,list):
    for x in v:yield from managed(x)
  while todo:
   j=todo.pop()
   if j in drop:continue
   drop.add(j);todo.extend(managed(d.r[j].get('data',{})))
  d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in drop]
  for j in drop:d.r.pop(j)
 for i in [1008,1005]:remove_branch(body,i)
 upper=ve(body,1007,'ClubOverviewUpperRow',True);lower=ve(body,1007,'ClubOverviewLowerRow',True)
 for row in [upper,lower]:flex(body,row);body.st(row,[(131083,body.enum('row')),(131087,body.px(0)),(131084,body.num(1)),(131082,body.px(0))])
 body.st(upper,[(131090,body.px(6))]);body.st(lower,[(131098,body.px(6))])
 for i in [1014,1015,1016,1017,1018,1019,1020]:body.move(i,upper)
 for i in [1014,1016,1018,1020]:
  body.st(i,[(131105,body.px(0)),(131097,body.px(0)),(131084,body.num(1)),(131085,body.num(1)),(131087,body.pct(100)),(131096,body.px(0)),(458768,body.enum('hidden'))])
 for i in [1015,1017,1019]:body.st(i,[(131093,body.px(8)),(131090,body.px(8)),(131105,body.px(1)),(131085,body.num(0))])
 for i in [1026,1030,1034,1038,1066,1089,1116,1145]:
  body.st(i,[(131096,body.px(0)),(131087,body.px(0)),(131084,body.num(1)),(131085,body.num(1)),(458768,body.enum('hidden'))])
 body.st(1073,[(131087,body.px(145)),(131085,body.num(0))])
 # Let the whole news article scroll within its half-height panel.
 newsdonor=Doc(W,name='ClubSiteBlock');newsscroll=body.add(newsdonor,1030,1020,'ClubOverviewNewsScroll');flex(body,newsscroll);body.move(1038,newsscroll)
 for i in [1038,1066,1089,1116]:body.st(i,[(131087,{'m_ValueType':1,'valueIndex':2}),(131084,body.num(0)),(131085,body.num(0))])
 body.st(1145,[(131087,body.px(160)),(131096,body.px(160)),(131084,body.num(0)),(131085,body.num(0))])
 split=body.add(newsdonor,1081,1007,'ClubOverviewRowDivider');body.using(newsdonor,'layout-divider-solid-horizontal');body.move(split,1007,1)
 body.st(split,[(131087,body.px(1)),(131096,body.px(1)),(131084,body.num(0)),(131085,body.num(0)),(131098,body.px(0)),(131090,body.px(0))])
 for titleid in [1025,1029,1033,1037]:body.a(titleid)['m_Classes']=[x for x in body.a(titleid)['m_Classes'] if not x.startswith('margin-bottom')];body.st(titleid,[(131090,body.px(6)),(131085,body.num(0))])
 columns=[]
 for j in range(4):
  if j:
   div=body.add(Doc(W,name='ClubSiteBlock'),1015,lower,'ClubOverviewLowerDivider'+str(j));body.using(Doc(W,name='ClubSiteBlock'),'layout-divider-solid-vertical');body.st(div,[(131105,body.px(1)),(131093,body.px(8)),(131090,body.px(8)),(131085,body.num(0))])
  col=ve(body,lower,'ClubOverviewLowerColumn'+str(j+1));body.st(col,[(131105,body.px(0)),(131097,body.px(0)),(131087,body.pct(100)),(131084,body.num(1)),(131085,body.num(1)),(458768,body.enum('hidden'))]);columns.append(col)
 title(body,columns[0],'球场信息',source=Doc(W,name='ClubFacilitiesStadiumBlock'),rid=1147);template(body,columns[0],'ClubOverviewStadiumStack',stadg)
 title(body,columns[1],'财政',translation=28061);template(body,columns[1],'ClubOverviewFinancesPanel',fg)
 title(body,columns[2],'俱乐部荣誉',translation=28083);body.move(1052,columns[2]);body.st(1075,[(131081,body.enum('none'))]);flex(body,1052);body.st(1052,[(262151,body.px(0))]);flex(body,1076);flex(body,1099)
 title(body,columns[3],'球队数据统计',translation=15274);template(body,columns[3],'ClubOverviewTeamStatsPanel',stg)
 body.save()
 # Existing club-only host keeps its original GUID and inherited club/team scope.
 host=Doc(W,name='ClubScreenOverviewBlock')
 for alias,guid in [('ClubSiteHeader',hg),('ClubSiteBlock',bg)]:next(u for u in host.d['m_Usings'] if u['alias']==alias)['path']=guid
 host.save()
 # Remove bottom shortcuts, and extend the existing overview to the original bottom edge.
 CK='<Configurations>k__BackingField';layouts=[]
 for size in ['Large','Standard','Small']:
  ob=find(L,'ClubComposition-'+size);tr=ob.read_typetree();old=copy.deepcopy(tr)
  overview=next(x for x in tr['m_gridComponents'] if x['m_elementID']=='ClubScreenOverviewBlock');actions=next(x for x in tr['m_gridComponents'] if x['m_elementID']=='HumanActionsControlPanelBlock')
  bottom=max(x['m_location']['y']+x['m_location']['height'] for x in tr['m_gridComponents']);h=bottom-overview['m_location']['y'];w=overview['m_location']['width']
  overview['m_location']['height']=h;overview['m_minSize']['y']=h;overview['m_maxSize']={'x':100,'y':h};overview['m_expandToContent']=0
  configs=[]
  for ptr in overview['m_configDescriptions']:
   pid=ptr['m_PathID'];dt=copy.deepcopy(changes[L].get(pid) or objs[L][pid].read_typetree());cs=dt[CK]
   c=next((x for x in cs if x['Size']=={'x':w,'y':h}),None)
   if c is None:
    c=copy.deepcopy(min(cs,key=lambda x:abs(x['Size']['x']-w)+abs(x['Size']['y']-h)));c['Size']={'x':w,'y':h};cs.append(c);objs[L][pid].save_typetree(dt);changes[L][pid]=dt
   configs.append(copy.deepcopy(c))
  overview['m_gridElementConfigs']=configs;tr['m_gridComponents']=[overview,actions];tr['m_compositionVersion']+=1
  tr['m_placementBindings']=[x for x in tr['m_placementBindings'] if x['m_elementID'] in ['ClubScreenOverviewBlock','HumanActionsControlPanelBlock']]
  assert actions==next(x for x in old['m_gridComponents'] if x['m_elementID']=='HumanActionsControlPanelBlock')
  objs[L][ob.path_id].save_typetree(tr);changes[L][ob.path_id]=tr;layouts.append({'name':tr['m_Name'],'overview':overview['m_location'],'bottom_shortcuts_removed':True})
 # Preload registration for private templates, their styles and nested sources.
 def ptrs(v,result):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'}:
    if v['m_PathID'] and v not in result:result.append(copy.deepcopy(v))
   else:
    for x in v.values():ptrs(x,result)
  elif isinstance(v,(list,tuple)):
   for x in v:ptrs(x,result)
 for n in NAMES:
  mo=next(o for o in objs[n].values() if o.type.name=='AssetBundle');mt=copy.deepcopy(metas[n])
  for c in [c for c in clones if c['bundle']==n]:mt['m_Container'].append((c['guid'],{'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':c['pid']}}))
  for key,entry in mt['m_Container']:
   pid=entry['asset']['m_PathID']
   if entry['asset']['m_FileID'] or pid not in changes[n]:continue
   span=copy.deepcopy(mt['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]);ptrs(changes[n][pid],span)
   dc=next((d for d in documents if d.n==n and d.obj.path_id==pid),None)
   if dc:
    ptrs(dc.s,span)
    for u in dc.d['m_Usings']:
     c=next((c for c in clones if c['guid']==u['path']),None)
     if c and c['bundle']==n:
      for q in [c['pid'],c['style']]:
       p={'m_FileID':0,'m_PathID':q}
       if p not in span:span.append(p)
   if {'m_FileID':0,'m_PathID':pid} not in span:span.append({'m_FileID':0,'m_PathID':pid})
   entry.update(preloadIndex=len(mt['m_PreloadTable']),preloadSize=len(span));mt['m_PreloadTable'].extend(span)
  mt['m_Container'].sort(key=lambda kv:kv[0]);mo.save_typetree(mt);changes[n][mo.path_id]=mt
 cat=cm.Catalog(catbefore)
 for c in clones:
  source=next(l for l in cat.locations(c['source_guid']) if cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
  cat=cm.Catalog(cat.add_key_location(c['guid'],source,source))
 for key,n in [('GameWorldVisualTreeAssetPreload',W),('GlobalVisualTreeAssetPreload',G)]:
  idx=next(i for i,(k,_) in enumerate(cat.keys()) if k==key);ko,ls=cat.key_records[idx];locs=[v[0] for v in cat.array(ls,'I')]
  locs += [cat.locations(c['guid'])[0] for c in clones if c['bundle']==n]
  records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',x) for x in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));cat=cm.Catalog(bytes(cat.data))
 catalog=bytes(cat.data)
 # Existing keys/locations remain registered; all new templates have exact types and own-bundle-first dependencies.
 oldcat=cm.Catalog(catbefore);oldkeys=dict(oldcat.keys());newkeys=dict(cat.keys())
 assert set(newkeys)==set(oldkeys)|{c['guid'] for c in clones}
 for key,loc in oldkeys.items():
  if key not in ['GameWorldVisualTreeAssetPreload','GlobalVisualTreeAssetPreload']:assert cat.array(newkeys[key],'I')==oldcat.array(loc,'I')
 for c in clones:
  v=cat.location(cat.locations(c['guid'])[0]);src=next(oldcat.location(l) for l in oldcat.locations(c['source_guid']) if oldcat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
  assert v['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' and v['dependencies']==src['dependencies']
 for d in documents:
  validate_ui(d.d,d.s)
  for u in d.d['m_Usings']:assert any(cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' for l in cat.locations(u['path']))
 assert any(cat.location(l)['type'][1]=='SI.VisualScripting.VisualFunction' for l in cat.locations(fguid))
 outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
 for n,b in outputs.items():
  check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n]);assert banned.isdisjoint(set(check)-set(hashes[n]))
  for i,h in hashes[n].items():
   if i not in changes[n]:assert sha(check[i].get_raw_data())==h,(tag,n,i)
  for i,tr in changes[n].items():assert check[i].read_typetree()==tr,(tag,n,i)
  for d in [x for x in documents if x.n==n]:validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
  source=OUT/n;source.write_bytes(b);bp=backup/n;bp.write_bytes(before[n]);tx.append({'target':str(folder/n),'source':str(source),'backup':str(bp),'before':sha(before[n]),'after':sha(b)})
 for p,b,original in [(catpath,catalog,catbefore),(hashpath,hashlib.md5(catalog).hexdigest().encode('ascii'),cathashbefore)]:
  sp=OUT/p.name;bp=backup/p.name;sp.write_bytes(b);bp.write_bytes(original);tx.append({'target':str(p),'source':str(sp),'backup':str(bp),'before':sha(original),'after':sha(b)})
 for n,b in before.items():assert (folder/n).read_bytes()==b
 assert catpath.read_bytes()==catbefore and hashpath.read_bytes()==cathashbefore
 for p in folder.glob('*.bundle'):
  if p.name not in NAMES:protected[str(p)]=sha(p.read_bytes())
 audits.append({'target':tag,'layouts':layouts,'private_templates':clones,'original_shared_templates_unchanged':True,'unrelated_objects_byte_identical':True,'stadium_photo_native_function':fguid,'stadium_database_type':21,'stadium_photo_binding':'club.MainTeam.Stadium.UniqueId','runtime_verified':False})
 print(json.dumps({'prepared_target':tag,'output':str(OUT),'private_templates':len(clones)},ensure_ascii=False),flush=True)
for p in [R/'reserved-texture-ids.json',R/'current-custom-textures.json',R/'current-game-location.json']:protected[str(p)]=sha(p.read_bytes())
manifest={'installed':False,'runtime_verified':False,'request':'Eight-panel Club Overview with two-row crest and native stadium-pack photo, preserving independent current game and skin baselines.','audits':audits,'protected_sha256':protected}
(ROOTOUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(ROOTOUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 text="$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n";(ROOTOUT/(action+'.ps1')).write_text(text,'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(ROOTOUT),'install_files':len(tx)},ensure_ascii=False),flush=True)
