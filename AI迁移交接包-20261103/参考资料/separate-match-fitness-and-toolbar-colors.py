from pathlib import Path
import ast,json,copy,struct,importlib.util
R=Path(__file__).parent
driver_source=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
prefix=driver_source.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','separate-match-fitness-toolbar-colors-')
exec(compile(prefix,'backup-current-and-load-helpers','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];main=Doc(G,name='MatchViewer_12x4');header=Doc(M,name='OverviewHeader')
 oldenv=UnityPy.load(str(R/'live-match-fitness-tabs-20261030-092133'/('backup-'+tag)/bases[0]));oldobjs={o.path_id:o for o in oldenv.objects}
 for idx,name in enumerate(['TacticsPositionDetailed','TacticsPositionCombined']):
  live=Doc(W,name=name);private,guid=clone_doc(live,'InMatchOnly'+name,-981030000030000-idx*10);private.save()
  original=next(o for o in oldenv.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name)
  tree=copy.deepcopy(original.read_typetree());style=copy.deepcopy(oldobjs[tree['inlineSheet']['m_PathID']].read_typetree())
  pointer_remap(tree,original.assets_file,live.af);pointer_remap(style,original.assets_file,live.af)
  board=Doc(W,pid=live.obj.path_id,tree=tree,style=style)
  root=1004;children=[c['rid'] for c in board.a(root)['m_Children'] if board.r[c['rid']]['type']['class']!='UxmlObjectAsset']
  switch=board.add(header,1066,root,'InMatchOnlyFitnessSwitch');board.data(switch)['Binding']['m_kind']=1;board.data(switch)['Binding']['m_direct']['Path']['m_path']='game.IsDuringMatch'
  normal=board.add(header,1035,switch,'OutsideMatchOriginalBoard')
  for child in children:board.move(child,normal)
  alias='InMatchOnly'+name;board.d['m_Usings'].append({'alias':alias,'path':guid,'asset':{'m_FileID':0,'m_PathID':0}})
  inst=board.add(header,1096,switch,alias);board.a(inst)['m_TemplateAlias']=alias;board.data(inst)['templateId']=alias
  for key in ['m_AttributeOverrides','m_SerializedDataOverride','m_SlotUsages']:board.a(inst)[key]=[]
  for node in [switch,normal,inst]:board.st(node,[(131084,board.num(1)),(131096,board.px(0)),(131097,board.px(0))])
  board.save()
 # Retain the known working in-match dual-ring template; only the stats
 # adapter's row-to-MatchPlayer lookup and fallback bindings are changed.
 adapter=Doc(G,name='HighlightStatsLiveFitnessDualRingCell')
 rewrite_binding(adapter.d,'player.Condition','StatsLiveCondition');rewrite_binding(adapter.d,'player.Sharpness','StatsLiveSharpness')
 mapper=next(r['data'] for r in adapter.r.values() if 'Mappings' in r.get('data',{}))
 mapper['Mappings']=[{'m_serialisedType':0,'from':'person','to':{'m_path':'binding.Player'},'type':{'id':1145176065}},{'m_serialisedType':0,'from':'teamselectionindex','to':{'m_path':'tactic.TeamSelectionIndexFromPlayer'},'type':{'id':0}},{'m_serialisedType':0,'from':'selectionplayer','to':{'m_path':'tactic.ITacticsTeamSelectionReferenceFromTeamSelectionIndex.MatchPlayer'},'type':{'id':1835103332}}]
 # The original cell has an outer visibility gate on `player`. Keep that
 # reference valid independently of whether the live lookup is available.
 mapper['Mappings'].append({'m_serialisedType':0,'from':'player','to':{'m_path':'binding.Player'},'type':{'id':1145176065}})
 remapper_node=next(i for i,r in adapter.r.items() if r.get('data',{}).get('m_FullTypeName') in ['SI.Bindable.BindingRemapper','SI.Bindable.BindingRemapperComponent'])
 parent=adapter.a(remapper_node)['m_Parent']['rid'] if adapter.a(remapper_node)['m_FullTypeName'].endswith('Component') else remapper_node
 children=[c['rid'] for c in adapter.a(parent)['m_Children'] if adapter.r[c['rid']]['type']['class']!='UxmlObjectAsset']
 setter=adapter.add(header,1036,parent,'StatsLiveFitnessLookup');data=adapter.data(setter)
 data.update(ValueVariables=[{'m_name':'StatsLiveCondition','m_scopeValue':{'m_serializedData':'Int|0|'}},{'m_name':'StatsLiveSharpness','m_scopeValue':{'m_serializedData':'Int|0|'}}],ReferenceVariables=[{'m_type':{'id':1835103332},'m_initToNull':1,'m_name':'statsmatchplayer'}],ValueVariables_UxmlAttributeFlags=1,ReferenceVariables_UxmlAttributeFlags=1)
 proto=next(f for r in Doc(W,name='TacticsPositionDetailed').r.values() for f in r.get('data',{}).get('BindFunction',[]) if f.get('m_target',{}).get('m_guid')=='079b54afdf49eb242aba84c36407187b')
 data['BindFunction']=[conditional(proto,'binding.MatchPlayer','binding.MatchPlayer','selectionplayer','statsmatchplayer'),conditional(proto,'statsmatchplayer','statsmatchplayer.Condition','person.Condition','StatsLiveCondition'),conditional(proto,'statsmatchplayer','statsmatchplayer.Sharpness','person.Sharpness','StatsLiveSharpness')]
 data['BindFunction_UxmlAttributeFlags']=1
 for child in children:adapter.move(child,setter)
 adapter.save()
 toolbar=Doc(M,name='MatchUITacticalOptions');palette=[(1014,'#252F42'),(1015,'#2C374A'),(1027,'#334055'),(1048,'#2A3B4D'),(1018,'#354153')]
 for node,color in palette:
  rgb=[int(color[i:i+2],16)/255 for i in [1,3,5]]
  rgba={k:struct.unpack('<f',struct.pack('<f',v))[0] for k,v in zip(['r','g','b','a'],rgb+[1.])}
  toolbar.st(node,[(458752,toolbar.val(4,rgba))])
 toolbar.save()
 # Register only the new private in-match marker copies; shared markers
 # keep their original GUIDs and route by native game.IsDuringMatch.
 new=[a for a in asset_clones if a['bundle']==G]
 mo=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=mo.read_typetree()
 for a in new:
  span=[{'m_FileID':0,'m_PathID':a['pid']}];allptr(changes[G][a['pid']],span);allptr(changes[G][a['pid']-1],span)
  meta['m_Container'].append((a['guid'],{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':a['pid']}}));meta['m_PreloadTable']+=span
 mo.save_typetree(meta);changes[G][mo.path_id]=meta
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';raw=before[cp]
 for a in new:
  cat=cm.Catalog(raw);loc=next(p for p in cat.locations('be643be14ca6c024083f0e6b4c7dea7c') if cat.location(p)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');raw=cat.add_key_location(a['guid'],loc,loc)
 cat=cm.Catalog(raw);extra=[cat.locations(a['guid'])[0] for a in new];idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx];records=list(cat.key_records)
 records[idx]=(ko,cat.append(b''.join(struct.pack('<I',v) for v in [v[0] for v in cat.array(ls,'I')]+extra),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));cats[tag]=bytes(cat.data)
 audits.append({'variant':tag,'outside_original_board':True,'in_match_private_board_copies':True,'stats_lookup':'row.MatchPlayer or native tactics selection MatchPlayer','stats_lookup_failure_fallback':'Person values, not blank; requires in-game check','toolbar_palette':palette,'existing_working_match_list_unchanged':True})
tail=driver_source.split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'roundtrip-and-package-separation','exec'))
