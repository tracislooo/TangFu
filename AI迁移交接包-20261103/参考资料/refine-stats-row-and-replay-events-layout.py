from pathlib import Path
import json,copy,struct,ast
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
prefix=driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','stats-row22-replay-events-')
prefix=prefix.replace(".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F]')", ".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F,\"ui-tileslayouts_assets_all.bundle\"]')")
exec(compile(prefix,'backup-current','exec'))
BaseDoc=Doc
class Doc(BaseDoc):
 def __init__(self,n,name=None,pid=None,tree=None,style=None):
  ob=objs[n][pid] if pid is not None else find(n,name)
  if tree is None:tree=copy.deepcopy(changes[n].get(ob.path_id,ob.read_typetree()))
  if style is None:
   sid=tree['inlineSheet']['m_PathID'];style=copy.deepcopy(changes[n].get(sid,objs[n][sid].read_typetree()))
  super().__init__(n,pid=ob.path_id,tree=tree,style=style)
AUTO={'m_ValueType':1,'valueIndex':2};cache_targets={}
def resolve(bns,guid):
 for bn in bns:
  ab=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle')
  for k,v in ab['m_Container']:
   if k==guid:
    ob=objs[bn].get(v['asset']['m_PathID'])
    if ob and ob.type.name=='MonoBehaviour' and 'inlineSheet' in ob.read_typetree():return Doc(bn,pid=ob.path_id)
 raise ValueError(guid)
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];T='ui-tileslayouts_assets_all.bundle'+suffix;main=Doc(G,name='MatchViewer_12x4');header=Doc(M,name='OverviewHeader')
 # 1. Increase rows and their private cell fonts together.
 d=Doc(G,name='HighlightRestoredNativeEightStats')
 for r in d.r.values():
  v=r.get('data',{})
  if 'FactoryAsset' in v and 'FixedElementSize' in v:v.update(FixedElementSize=22.,FixedElementSizeControllerOrTouch=22.)
 d.save();factory=find(F,'HighlightEightFieldsFactory').read_typetree();mapped={}
 for c in factory['m_rowData']:
  guid=c['m_uxmlRef']['m_AssetGUID']
  if guid in mapped:continue
  source=resolve([G,W],guid);cell,newguid=clone_doc(source,'HighlightStatsRow22Cell'+str(len(mapped)),-981101000020000-len(mapped)*10)
  for i,r in cell.r.items():
   x=r.get('data',{})
   if x.get('m_FullTypeName')=='SI.Bindable.SIText':cell.st(i,[(65537,cell.px(10)),(131096,cell.px(0))])
  if c['m_id']=='picked-position':
   cell.st(1001,[(131087,cell.px(22)),(131096,cell.px(22)),(131073,cell.enum('center'))])
   for i in [1005,1007,1008,1014,1017]:cell.st(i,[(131087,cell.px(18)),(131096,cell.px(0)),(131094,cell.px(18)),(131073,cell.enum('center'))])
   cell.st(1008,[(131093,cell.px(2)),(131099,cell.px(0)),(131100,cell.px(0))])
  cell.save();mapped[guid]=newguid
 for ob in objs[F].values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name()!='HighlightEightFieldsFactory':continue
  t=ob.read_typetree()
  for c in t['m_rowData']:c['m_uxmlRef']['m_AssetGUID']=mapped[c['m_uxmlRef']['m_AssetGUID']]
  ob.save_typetree(t);changes[F][ob.path_id]=t
 # 2. Round the actual color-bearing holder, not only its transparent children.
 for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']:
  d=Doc(W,name=name)
  for label in ['MatchCardNumberKitColourBinding','MatchCardNumberNativeKitFill','MatchCardShirtNumber']:d.st(d.named(label),[(262147,d.px(3))])
  d.save()
 # 3. Create a replay-only copy; the live Highlight keeps its existing charts.
 replay,rguid=clone_doc(main,'ReplayHighlightEventsCentre',-981101000020300)
 replay.st(1022,[(131081,replay.enum('none'))])
 remapper=next(i for i,r in replay.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingRemapper')
 context=replay.add(replay,remapper,2147,'ReplayCentreMatchEventsContext');replay.move(context,2147,1)
 replay.data(context).update(Mappings=[{'m_serialisedType':0,'from':'fixture','to':{'m_path':'fixturetouse'},'type':{'id':1718188148}},{'m_serialisedType':0,'from':'isonmainscreen','to':{'m_path':'const.False'},'type':{'id':0}}],Mappings_UxmlAttributeFlags=1)
 alias='ReplayNativeMatchEvents';replay.d['m_Usings'].append({'alias':alias,'path':'dbda07217faf707419c93266465db7b8','asset':{'m_FileID':0,'m_PathID':0}})
 event=replay.add(header,1096,context,'ReplayCentreMatchEvents');replay.a(event)['m_TemplateAlias']=alias;replay.data(event)['templateId']=alias
 for k in ['m_AttributeOverrides','m_SerializedDataOverride','m_SlotUsages']:replay.a(event)[k]=[]
 replay.st(context,[(131105,replay.pct(50)),(131087,replay.pct(100)),(131084,replay.num(0)),(131085,replay.num(0)),(131096,replay.px(0))]);replay.fill(event)
 replay.st(3169,[(131081,replay.enum('none'))])
 for i in [3123,3261]:replay.st(i,[(131105,replay.pct(50)),(131082,replay.px(0)),(131084,replay.num(1)),(131085,replay.num(1)),(131097,replay.px(0))])
 replay.save()
 # Give only the historical report its own descriptor.
 CK='<Configurations>k__BackingField';src=objs[T][2268119280419395392];dt=src.read_typetree();dpid=-981101000020500;ident='ReplayHighlightViewer'
 cfg=copy.deepcopy(next(c for c in dt[CK] if c['Size']=={'x':10,'y':8}));cfg['AssetRef']['m_AssetGUID']=rguid;cfg['Description']={'m_FileID':0,'m_PathID':dpid}
 dt.update({'<Name>k__BackingField':ident,'<ID>k__BackingField':ident,CK:[cfg],'<DefaultConfigIndex>k__BackingField':0})
 register_clone(T,src,ident+'Description',dpid,dt)
 for name in ['PastMatchTeamReportGridComposition-Large','PastMatchTeamReportGridComposition-Large-FMC']:
  ob=find(T,name);t=ob.read_typetree()
  for b in t['m_gridComponents']:
   if b['m_elementID']=='MatchViewer':b.update(m_elementID=ident,m_configDescriptions=[{'m_FileID':0,'m_PathID':dpid}],m_configDescriptionKeys=[],m_gridElementConfigs=[copy.deepcopy(cfg)])
   if b['m_location']['y']==6 and b['m_location']['x'] in [0,15]:
    label='HomeTeamShotMapTileDescription' if b['m_location']['x']==0 else 'AwayTeamShotMapTileDescription';desc=find(T,label);dd=copy.deepcopy(changes[T].get(desc.path_id,desc.read_typetree()));q=next((c for c in dd[CK] if c['Size']=={'x':5,'y':4}),None)
    if q is None:q=copy.deepcopy(dd[CK][0]);q['Size']={'x':5,'y':4};dd[CK].append(q);desc.save_typetree(dd);changes[T][desc.path_id]=dd
    b.update(m_elementID=label,m_configDescriptions=[{'m_FileID':0,'m_PathID':desc.path_id}],m_configDescriptionKeys=[],m_gridElementConfigs=[copy.deepcopy(q)])
  t['m_compositionVersion']+=1;ob.save_typetree(t);changes[T][ob.path_id]=t
  if tag=='game':cache_targets[name]=copy.deepcopy(t)
 ob=find(T,'PastMatchTeamReportGridElementSet');t=ob.read_typetree();t['m_gridElementDescriptions'].append({'m_FileID':0,'m_PathID':dpid});ob.save_typetree(t);changes[T][ob.path_id]=t
 d=Doc(G,name='PastMatchTeamReport')
 for r in d.r.values():
  bindings=r.get('data',{}).get('Bindings')
  if not bindings:continue
  for b in list(bindings['m_gridElementBindingData']):
   if b['DescriptionAndMapping']['DescriptionName']=='MatchViewer':b=copy.deepcopy(b);b['DescriptionAndMapping']['DescriptionName']=ident;bindings['m_gridElementBindingData'].append(b)
 d.save()
 # The post-replay full-time screen selects the same PastMatch composition set.
 # Supply the replay descriptor bindings at that entry as well.
 d=Doc(M,name='FullTimeTeamReport');pastset=find(T,'PastMatchTeamReportGridCompositionSet').path_id;covered=0
 for r in d.r.values():
  for group in r.get('data',{}).get('GridCompositionSets',[]):
   bset=group['m_gridCompositionSetBindings']
   if bset['m_gridCompositionSet']['m_PathID']!=pastset:continue
   covered+=1
   for b in list(bset['m_gridElementBindingData']):
    if b['DescriptionAndMapping']['DescriptionName']=='MatchViewer':b=copy.deepcopy(b);b['DescriptionAndMapping']['DescriptionName']=ident;bset['m_gridElementBindingData'].append(b)
 assert covered==1
 d.save()
 # Addressables, owner-first dependencies and preload entries.
 register=(R/'separate-match-fitness-and-toolbar-colors.py').read_text('utf8').split(' new=[a for a in asset_clones')[1].split(' audits.append')[0]
 exec(__import__('textwrap').dedent(' new=[a for a in asset_clones'+register))
 mo=next(o for o in objs[T].values() if o.type.name=='AssetBundle');meta=mo.read_typetree()
 for a in [a for a in asset_clones if a['bundle']==T]:
  span=[{'m_FileID':0,'m_PathID':a['pid']}];allptr(changes[T][a['pid']],span);meta['m_Container'].append((a['guid'],{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':span[0]}));meta['m_PreloadTable']+=span
  cat=cm.Catalog(cats[tag]);loc=cat.locations(a['source_guid'])[0];cats[tag]=cat.add_key_location(a['guid'],loc,loc)
 mo.save_typetree(meta);changes[T][mo.path_id]=meta
 audits.append({'variant':tag,'row_height':22,'cell_font':10,'position_badge_height':18,'position_badge_offset_down':2,'number_corner_radius':3,'replay_events_centre':True,'replay_native_shot_maps':True,'replay_lower_charts':'momentum/xG 50/50','live_highlight_unchanged':True})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
cache=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');tx=json.loads((OUT/'transaction.json').read_text('utf8'))
for name,target in cache_targets.items():
 p=cache/name
 if not p.exists():continue
 old=p.read_bytes();t=json.loads(old);t['m_gridComponents']=copy.deepcopy(target['m_gridComponents']);t['m_compositionVersion']=target['m_compositionVersion']
 for b in t['m_gridComponents']:b.update(m_configDescriptions=[],m_configDescriptionKeys=[b['m_elementID']],m_gridElementConfigs=[])
 new=json.dumps(t,ensure_ascii=False,indent=2).encode('utf8');bp=OUT/('cache-backup-'+name+'.json');sp=OUT/('cache-'+name+'.json');bp.write_bytes(old);sp.write_bytes(new);tx.append({'target':str(p),'source':str(sp),'backup':str(bp),'before':sha(old),'after':sha(new)})
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');installer=(OUT/'installer.py').read_text('utf8').replace('for row in tx:',"allowed.add(Path("+repr(str(cache))+").resolve())\nfor row in tx:");(OUT/'installer.py').write_text(installer,'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())

