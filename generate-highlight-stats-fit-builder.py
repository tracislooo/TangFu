from pathlib import Path
R=Path(__file__).parent
prior=(R/'build-highlight-integrated-team-stats.py').read_text('utf8')
head=prior.split("for tag,suffix,folder in [('game','',GAME)")[0].replace("R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle'", "R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle';V='ui-tableviews_assets_all.bundle'")
head=head.replace('highlight-integrated-team-stats-','highlight-stats-order-fit-').replace("'NAMES=[G,T]'","'NAMES=[G,T,V]'").replace("'bases=(G,T)'","'bases=(G,T,V)'")
body=r'''
def resolve_guid(bn,guid):
 meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle');return objs[bn][next(v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==guid)]

for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 G,T,V=[n+suffix for n in bases];main=Doc(G,name='MatchViewer_12x4');source_guids={};dependency_sources={}
 source=Doc(G,name='HighlightRestoredNativeEightStats');stats,statsguid=clone_doc(source,'HighlightUpperGoalsAssistsTallerRows',-981112000010000);source_guids[statsguid]=asset_guid(G,source.obj.path_id)
 raw=bytes(stats.data(1028)['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']);import re
 oldviewguid=re.findall(rb'[0-9a-f]{32}',raw)[0].decode();sourceview=resolve_guid(V,oldviewguid);oldview=sourceview.read_typetree();pid=-981112000020000;ob,tr,viewguid=register_clone(V,sourceview,'HighlightUpperGoalsAssistsView',pid,oldview,source_guid=oldviewguid)
 order=['picked-position','player','rating','goals','assists','run','pass%','keyPasses','keyTackles'];cols={c['m_columnID']:c for c in tr['m_tableView']['m_tableConfig']};assert set(cols)==set(order);tr['m_tableView']['m_tableConfig']=[cols[k] for k in order];save(V,pid,tr)
 for node in [1028,1032]:
  s=stats.data(node);assert s['FixedElementSize']==22
  s.update(FixedElementSize=28.,FixedElementSizeControllerOrTouch=28.,FixedElementSize_UxmlAttributeFlags=1,FixedElementSizeControllerOrTouch_UxmlAttributeFlags=1)
  data=bytes(s['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert oldviewguid.encode() in data;s['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(data.replace(oldviewguid.encode(),viewguid.encode()))
 for r in stats.r.values():
  for prop in r.get('data',{}).get('m_Properties',[]):
   if isinstance(prop.get('value'),str):prop['value']=prop['value'].replace(oldviewguid,viewguid)
 stats.save()
 for side in ['Home','Away']:
  d=Doc(G,name='HighlightIntegrated'+side+'StatsAndFormation');alias='Highlight'+side+'Stats';u=next(u for u in d.d['m_Usings'] if u['alias']==alias);assert u['path']==source_guids[statsguid];u['path']=statsguid;d.save()
 source=Doc(G,name='MatchStats_4x4');d,compactguid=clone_doc(source,'HighlightCompactMatchStatsThreeByThree',-981112000010010);source_guids[compactguid]=asset_guid(G,source.obj.path_id);unchanged=copy.deepcopy(d.d)
 NONE={'m_ValueType':1,'valueIndex':3};AUTO={'m_ValueType':1,'valueIndex':2}
 # Let the five native comparison rows share the available height; override old minimums.
 for i in [1001,1002,1004,1006,1008,1010]:d.st(i,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131095,NONE),(131094,NONE),(131084,d.num(1)),(131085,d.num(1))])
 d.st(1015,[(131096,d.px(0)),(131087,d.px(20)),(131084,d.num(0)),(131085,d.num(0)),(131090,d.px(2)),(131093,d.px(0))])
 d.st(1016,[(131096,d.px(0)),(131087,AUTO),(131082,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131093,d.px(0)),(131090,d.px(0))])
 for i in [1021,1022,1023,1024,1025]:
  d.st(i,[(131096,d.px(0)),(131094,NONE),(131087,AUTO),(131082,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131093,d.px(0)),(131090,d.px(0)),(131101,d.px(0)),(131098,d.px(0))])
 for i,r in list(d.r.items()):
  if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText':d.st(i,[(65537,d.px(10)),(131096,d.px(0))])
 for i in [1031,1034,1037,1040,1043]:d.st(i,[(65537,d.px(9)),(131087,d.px(12)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131093,d.px(0)),(131090,d.px(0))])
 for i in [1032,1035,1038,1041,1044]:d.st(i,[(131087,d.px(12)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131093,d.px(0)),(131090,d.px(0))])
 for i,r in refs(unchanged).items():
  if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,('Comparison binding changed',i)
 d.save()
 changed_descriptions=0
 for name in names:
  ob=find(T,name);layout=tree(T,ob.path_id);reg=tree(T,layout['m_gridElementSet']['m_PathID']);description_refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:description_refs+=group['m_tiles']
  descpid=next(r['m_PathID'] for r in description_refs if tree(T,r['m_PathID']).get('<ID>k__BackingField')=='MatchStatsStandAlone');desc=tree(T,descpid)
  for c in desc[CK]:
   if c['AssetRef']['m_AssetGUID']==source_guids[compactguid]:c['AssetRef']['m_AssetGUID']=compactguid
  save(T,descpid,desc);changed_descriptions+=1
  for b in layout['m_gridComponents']:
   for c in b['m_gridElementConfigs']:
    if c['AssetRef']['m_AssetGUID']==source_guids[compactguid]:c['AssetRef']['m_AssetGUID']=compactguid
  save(T,ob.path_id,layout)
  p=cache_root/name
  if tag=='game' and p in cache_before:
   cached=json.loads(cache_before[p].decode('utf8'));updated=copy.deepcopy(cached)
   for b in updated['m_gridComponents']:
    for c in b['m_gridElementConfigs']:
     if c['AssetRef']['m_AssetGUID']==source_guids[compactguid]:c['AssetRef']['m_AssetGUID']=compactguid
   cache_outputs[p]=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8')
 audits.append({'variant':tag,'column_order':order,'upper_row_height_before':22,'upper_row_height_after':28,'upper_stats_private_template':statsguid,'private_table_view':viewguid,'compact_comparisons_private_template':compactguid,'all_comparison_bindings_preserved':True,'grid_locations_unchanged':True,'shared_stats_and_original_view_unchanged':True})
'''
footer=' # Register new private assets'+prior.split(' # Register new private assets',1)[1]
footer=footer.replace('for bn in [G,T]:','for bn in [G,T,V]:').replace("a['bundle'] in [G,T]","a['bundle'] in [G,T,V]")
# Clone metadata source GUID for views comes from the original, only VTA needs separate source map.
footer=footer[:footer.index("(OUT/'修改说明.md')")]+"(OUT/'修改说明.md').write_text('仅上方两端统计使用专用模板和专用表格视图，列序位置/姓名/评分/进球/助攻/跑动/传球成功率/关键传球/关键抢断；行高22→28。原共用统计、轮播与其他视图不变。下方比赛数据使用私有紧凑模板，字体9/10px，五行均分可用高度并取消旧最小高度和垂直空隙。保持20×8及所有位置比例和原绑定，备份/哈希回退齐全。文件检查通过，实际行高与显示待游戏确认。','utf8')\nprint(OUT)\n"
(R/'build-highlight-stats-order-fit.py').write_text(head+body+footer,'utf8')
