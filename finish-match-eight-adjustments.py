from pathlib import Path
import json,copy,ast,struct
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
prefix=driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','match-eight-adjustments-')
prefix=prefix.replace(".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F]')", ".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F,\"ui-tileslayouts_assets_all.bundle\",\"ui-tableviews_assets_all.bundle\"]')")
exec(compile(prefix,'backup-current','exec'))
# Reopening a template must use pending edits, not UnityPy's cached original tree.
BaseDoc=Doc
class Doc(BaseDoc):
 def __init__(self,n,name=None,pid=None,tree=None,style=None):
  ob=objs[n][pid] if pid is not None else find(n,name)
  if tree is None:tree=copy.deepcopy(changes[n].get(ob.path_id,ob.read_typetree()))
  if style is None:
   sid=tree['inlineSheet']['m_PathID'];style=copy.deepcopy(changes[n].get(sid,objs[n][sid].read_typetree()))
  super().__init__(n,pid=ob.path_id,tree=tree,style=style)
helper=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'clone-native-subtrees','exec'))
clone_audits=[];cache_targets={};clone_origins={};AUTO={'m_ValueType':1,'valueIndex':2};NONE={'m_ValueType':1,'valueIndex':3}
def resolve(bns,guid):
 for bn in bns:
  ab=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle')
  for k,v in ab['m_Container']:
   if k==guid:
    ob=objs[bn].get(v['asset']['m_PathID'])
    if ob and ob.type.name=='MonoBehaviour' and 'inlineSheet' in ob.read_typetree():return Doc(bn,pid=ob.path_id)
 raise ValueError(guid)
def fn(guid,args):return {'m_target':{'m_guid':guid},'m_inputs':{'m_variable':{'m_argumentBytes':pack(args)}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];T='ui-tileslayouts_assets_all.bundle'+suffix;V='ui-tableviews_assets_all.bundle'+suffix
 main=Doc(G,name='MatchViewer_12x4');header=Doc(M,name='OverviewHeader')
 # 1. Use the same match-human-team kit path as the native card number colors.
 for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']:
  d=Doc(W,name=name);holder=d.named('MatchCardNumberKitColourBinding');fill=d.named('MatchCardNumberNativeKitFill');number=d.named('MatchCardShirtNumber');s=d.data(holder)
  for k,path in [('PrimaryColorDataLink','kit.BackgroundColour'),('SecondaryColorDataLink','kit.NumberColour')]:s[k]['m_path']=path
  args=unpack(s['BindFunction']['m_inputs']['m_variable']['m_argumentBytes']);path=b'kit.BackgroundColour';args[0]=args[0][:args[0][0]+2]+bytes([len(path)])+path;args[1]=args[1][:-1]+bytes([0]);s['BindFunction']['m_inputs']['m_variable']['m_argumentBytes']=pack(args)
  # The native function writes the holder/children; do not cover it with a theme fill.
  d.a(fill)['m_Classes']=[];d.st(fill,[(458752,d.val(4,{'r':0.,'g':0.,'b':0.,'a':0.}))]);d.st(number,[(458752,d.val(4,{'r':0.,'g':0.,'b':0.,'a':0.}))]);d.save()
 # 2. Both live and past-fixture rows use the same compact height.
 d=Doc(G,name='HighlightRestoredNativeEightStats')
 for i,r in d.r.items():
  s=r.get('data',{})
  if 'FactoryAsset' in s and 'FixedElementSize' in s:s.update(FixedElementSize=20.,FixedElementSizeControllerOrTouch=20.)
 d.save()
 row=Doc(G,name='HighlightHomeAwayStatsRow21Font70')
 for i,r in row.r.items():
  if 'm_Parent' in r.get('data',{}) and r['data']['m_Parent']['rid']!=-2:row.st(i,[(131096,row.px(0))])
 row.save()
 # 3/4. Force the OOP page's own scope, preserve independent carousel state.
 tiny,guid=clone_doc(resolve([G,W],'f677caec43d6c1342b1bba39c5ae2c5f'),'HighlightFormationCompactTitleTile',-981101000010100)
 for i,r in tiny.r.items():
  x=r.get('data',{});s=tiny.data(i) if 'm_Parent' in x and 'm_SerializedData' in x else {};n=s.get('name','')
  if n=='title area frame':tiny.st(i,[(131087,tiny.px(20)),(131096,tiny.px(20)),(131094,tiny.px(20)),(131082,tiny.px(20)),(131093,tiny.px(0)),(131090,tiny.px(0))])
  if x.get('m_FullTypeName')=='SI.Bindable.SIText' and ('title' in n):tiny.st(i,[(65537,tiny.px(11))])
 tiny.save()
 for side in ['Home','Away']:
  d=Doc(G,name='HighlightNative'+side+'OOPHorizontal');expect=next(i for i,r in d.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingExpect')
  children=[c['rid'] for c in d.a(expect)['m_Children']];source=next(i for i,r in d.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingRemapper')
  mapper=d.add(d,source,expect,'FixedOutOfPossessionContext');d.data(mapper).update(Mappings=[{'m_serialisedType':0,'from':'inpossession','to':{'m_path':'const.False'},'type':{'id':0}}],Mappings_UxmlAttributeFlags=1)
  for c in children:d.move(c,mapper)
  for u in d.d['m_Usings']:
   if u['alias']=='tile-tall-4x6':u['path']=guid;u['asset']={'m_FileID':0,'m_PathID':0}
  d.st(mapper,[(131084,d.num(1)),(131096,d.px(0)),(131105,d.pct(100))]);d.save()
 for name in ['HighlightHomeHorizontalFormation','HighlightAwayHorizontalFormation','HighlightNativeHomeOOPHorizontal','HighlightNativeAwayOOPHorizontal']:
  d=Doc(G,name=name)
  panels=[i for i,r in d.r.items() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.FMTacticsPanel']
  for i in panels:
   s=d.data(i);s.update(FillAllAvailableSpace=1,FillAllAvailableSpace_UxmlAttributeFlags=1,UseParentRectForOutline=1,UseParentRectForOutline_UxmlAttributeFlags=1)
   d.st(i,[(131105,d.pct(100)),(131087,d.pct(100)),(131096,d.px(0)),(131094,NONE),(131084,d.num(1))])
   parent=d.a(i)['m_Parent']['rid'];d.st(parent,[(131084,d.num(1)),(131096,d.px(0)),(131094,NONE),(131074,d.enum('stretch'))])
  for i,r in d.r.items():
   x=r.get('data',{})
   if x.get('m_FullTypeName')=='SI.Bindable.SIText' and d.data(i).get('name') in ['FormationView','FormationViewPastMatch','statsView']:d.st(i,[(65537,d.px(11))])
  d.save()
 # 5. Shrink the whole substitute card only above 11 substitutes.
 d=Doc(M,name='SquadOverview');lists=[i for i,r in d.r.items() if 'm_Parent' in r.get('data',{}) and d.data(i).get('RowTemplate') and d.data(i).get('Binding',{}).get('m_direct',{}).get('Path',{}).get('m_path')=='sublist' and d.data(i).get('FixedElementSize') in [80.,110.]]
 # Native comparison argument prefixes come from a working condition tree.
 cdoc=Doc(G,name='TacticsMatchPositionFilled');comp=next(s['data']['Binding']['m_visualFunction'] for s in cdoc.r.values() if s.get('data',{}).get('name')=='MatchCondition_Above50');ca=unpack(comp['m_inputs']['m_variable']['m_argumentBytes']);bp=ca[2][:ca[2][0]+2];boolarg=bytes([35])+b'SI.VisualScripting.BooleanVisualArg'+bytes([0])
 def patharg(p):return bp+bytes([len(p)])+p.encode()
 for index,i in enumerate(lists):
  s=d.data(i);basewidth=s['FixedElementSize'];source=resolve([W,G],s['RowTemplate']['m_AssetGUID']);compact,cguid=clone_doc(source,'MatchManySubstitutes'+('Small' if basewidth==80 else 'Regular')+'Card',-981101000010200-index*10)
  clone_origins[cguid]=(W,source.obj.path_id)
  root=next(j for j,r in compact.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingRoot')
  compact.st(root,[(131105,compact.px(basewidth)),(131097,compact.px(basewidth)),(327681,[compact.num(.75),compact.num(.75)]),(327682,[compact.px(0),compact.px(0)])]);compact.save()
  parent=d.a(i)['m_Parent']['rid'];place=next(j for j,c in enumerate(d.a(parent)['m_Children']) if c['rid']==i)
  setter=d.add(header,1036,parent,'SubstituteCountForCompactCards');ss=d.data(setter);ss.update(ValueVariables=[{'m_name':'SubstituteCount','m_scopeValue':{'m_serializedData':'Int|0|'}}],ReferenceVariables=[],ValueVariables_UxmlAttributeFlags=1,ReferenceVariables_UxmlAttributeFlags=1,BindFunction=[fn('96d2a04b75016c74980995c0eee24c2e',[patharg('sublist'),patharg('SubstituteCount'),boolarg])],BindFunction_UxmlAttributeFlags=1)
  switch=d.add(header,1066,setter,'ManySubstitutesCompactSwitch');switchdata=d.data(switch);a=copy.deepcopy(ca);a[1]=a[1][:-4]+struct.pack('<i',11);a[2]=patharg('SubstituteCount');switchdata['Binding']=copy.deepcopy(cdoc.data(cdoc.named('MatchCondition_Above50'))['Binding']);switchdata['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=pack(a)
  d.move(i,switch);copied,mapping=clone_native(d,i,switch);v=d.data(copied);v['RowTemplate']['m_AssetGUID']=cguid;v['FixedElementSize']=basewidth*.75;v['FixedElementSizeControllerOrTouch']=basewidth*.75;d.move(setter,parent,place)
  for j in [setter,switch]:d.st(j,[(131084,d.num(1)),(131097,d.px(0))])
 d.save()
 # 6. Move only the existing condition ring to the portrait's bottom-right.
 d=Doc(G,name='TacticsMatchPositionFilled');ring=d.named('MatchCondition_Available');d.st(ring,[(131089,AUTO),(131104,AUTO),(131103,d.px(-4)),(131080,d.px(-4))]);d.save()
 # Historical formation rows also use the same existing portrait source.
 live=Doc(G,name='TacticsMatchPositionFilled');d=Doc(G,name='TacticsPastMatchPositionFilled')
 portrait,mapping=clone_native(live,live.named('MatchPlayerPortraitBinding'),1026)
 for i in mapping.values():rewrite_binding(d.r[i],'position.MatchPlayer.Person','position.Player')
 d.st(1036,[(131081,d.enum('none'))]);d.st(1017,[(131105,d.px(36)),(131087,d.px(36))]);d.st(1022,[(65537,d.px(9))]);d.save()
 # 7. Reuse the current full-time grid in the historical/replay report.
 donor=find(T,'FullTimeTeamReportGridComposition-Large').read_typetree()
 for name in ['PastMatchTeamReportGridComposition-Large','PastMatchTeamReportGridComposition-Large-FMC']:
  ob=find(T,name);t=ob.read_typetree();old=copy.deepcopy(t);score=next(b for b in old['m_gridComponents'] if b['m_elementID']=='MatchResult')
  for key in ['m_gridComponents','m_optionalSlices','m_layoutMode']:t[key]=copy.deepcopy(donor[key])
  t['m_gridComponents'][0]=score;t['m_compositionVersion']+=1;ob.save_typetree(t);changes[T][ob.path_id]=t
  if tag=='game':cache_targets[name]=copy.deepcopy(t)
 ab=find(T,'PastMatchTeamReportGridElementSet');t=ab.read_typetree();existing={r['m_PathID'] for r in t['m_gridElementDescriptions']}
 for b in donor['m_gridComponents']:
  for ref in b['m_configDescriptions']:
   if ref['m_PathID'] not in existing:t['m_gridElementDescriptions'].append(copy.deepcopy(ref));existing.add(ref['m_PathID'])
 ab.save_typetree(t);changes[T][ab.path_id]=t
 past=Doc(G,name='PastMatchTeamReport');full=Doc(M,name='FullTimeTeamReport')
 fullbindings=[]
 for r in full.r.values():
  s=r.get('data',{});groups=[g['m_gridCompositionSetBindings'] for g in s.get('GridCompositionSets',[])];groups+=([s['Bindings']] if 'Bindings' in s else [])
  for group in groups:fullbindings.extend(copy.deepcopy(b) for b in group['m_gridElementBindingData'] if b['DescriptionAndMapping']['DescriptionName'] in ['LiveTable','LatestScores'])
 for r in past.r.values():
  group=r.get('data',{}).get('Bindings')
  if not group:continue
  for b in fullbindings:
   if b not in group['m_gridElementBindingData']:group['m_gridElementBindingData'].append(copy.deepcopy(b))
 past.save()
 # 8. The replay-only controls retain their own gate and move to the right.
 d=Doc(M,name='OverviewHeader');d.st(1012,[(131102,d.enum('absolute')),(131103,d.px(0)),(131104,d.px(0)),(131089,AUTO),(131085,d.num(0))]);d.save()
 # Register the new private templates with the same owner bundle and preload.
 register=(R/'separate-match-fitness-and-toolbar-colors.py').read_text('utf8').split(' new=[a for a in asset_clones')[1].split(' audits.append')[0]
 exec(__import__('textwrap').dedent(' new=[a for a in asset_clones'+register))
 cat=cm.Catalog(cats[tag])
 for asset in [a for a in asset_clones if a['bundle']==G and a['guid'] in clone_origins]:
  origin_bn,origin_pid=clone_origins[asset['guid']];ab=next(o.read_typetree() for o in objs[origin_bn].values() if o.type.name=='AssetBundle');origin_guid=next(k for k,v in ab['m_Container'] if v['asset']['m_PathID']==origin_pid)
  source_loc=next(p for p in cat.locations(origin_guid) if cat.location(p)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');new_loc=cat.locations(asset['guid'])[0];deps=cat.location(new_loc)['dependencies'];deps=deps+[p for p in cat.location(source_loc)['dependencies'] if p not in deps]
  struct.pack_into('<I',cat.data,new_loc+12,cat.append(b''.join(struct.pack('<I',p) for p in deps),True))
  assert bases[1] in cat.location(deps[0])['internal']
 cats[tag]=bytes(cat.data)
 audits.append({'variant':tag,'items':[1,2,3,4,5,6,7,8],'stats_row_height':20,'formation_title_font':11,'compact_substitutes_above':11,'compact_scale':.75,'runtime_verified':False})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
tail=tail.replace("for p,h in protected.items():assert sha(p.read_bytes())==h", "for p,h in protected.items():assert sha(p.read_bytes())==h,('Concurrent resource change',str(p))")
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
cache=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');tx=json.loads((OUT/'transaction.json').read_text('utf8'))
for name,target in cache_targets.items():
 p=cache/name
 if not p.exists():continue
 old=p.read_bytes();t=json.loads(old);t['m_gridComponents']=copy.deepcopy(target['m_gridComponents']);t['m_optionalSlices']=copy.deepcopy(target['m_optionalSlices']);t['m_compositionVersion']=target['m_compositionVersion'];t['m_layoutMode']=target['m_layoutMode']
 for b in t['m_gridComponents']:b.update(m_configDescriptions=[],m_configDescriptionKeys=[b['m_elementID']],m_gridElementConfigs=[])
 new=json.dumps(t,ensure_ascii=False,indent=2).encode('utf8');bp=OUT/('cache-backup-'+name+'.json');sp=OUT/('cache-'+name+'.json');bp.write_bytes(old);sp.write_bytes(new);tx.append({'target':str(p),'source':str(sp),'backup':str(bp),'before':sha(old),'after':sha(new)})
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');installer=(OUT/'installer.py').read_text('utf8').replace('for row in tx:',"allowed.add(Path("+repr(str(cache))+").resolve())\nfor row in tx:");(OUT/'installer.py').write_text(installer,'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
