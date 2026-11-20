from pathlib import Path
R=Path(__file__).parent
old=(R/'build-highlight-integrated-team-stats.py').read_text('utf8')
header=old.split("for tag,suffix,folder in [('game','',GAME)")[0].replace('highlight-integrated-team-stats-','highlight-six-top-five-bottom-')
body=r'''
def config(pid,w,h,asset=None):
 desc=tree(T,pid);found=next((c for c in desc[CK] if c['Size']=={'x':w,'y':h} and (asset is None or c['AssetRef']==asset)),None)
 if found:return copy.deepcopy(found)
 candidates=[c for c in desc[CK] if asset is None or c['AssetRef']==asset];assert candidates,(pid,w,h,asset)
 c=copy.deepcopy(min(candidates,key=lambda c:abs(c['Size']['x']-w)+abs(c['Size']['y']-h)));c['Size']={'x':w,'y':h};c['Description']={'m_FileID':0,'m_PathID':pid};desc[CK].append(copy.deepcopy(c));save(T,pid,desc);return c

for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 G,T=[n+suffix for n in bases];main=Doc(G,name='MatchViewer_12x4');source_guids={};dependency_sources={}
 for index,side in enumerate(['Home','Away']):
  source=Doc(G,name='HighlightFiveAnalysis'+side+'Vertical');oop,guid=clone_doc(source,'HighlightSixColumns'+side+'OutOfPossession',-981111000010000-index*10);source_guids[guid]=asset_guid(G,source.obj.path_id)
  selected=[]
  for r in oop.r.values():
   s=r.get('data',{})
   for v in s.get('ValueVariables',[]):
    if v['m_name'].startswith('SelectedFormation'):
     val=v['m_scopeValue']['m_serializedData'];val=val.replace('Int|0|','Int|1|')
     if v['m_name']!='SelectedFormation':
      import re
      val=re.sub(r'\{[^{}]*SelectedFormation(?:Human|AI|Default)\}', '{HighlightSixColumns'+side+v['m_name']+'}',val)
     v['m_scopeValue']['m_serializedData']=val;selected.append(v['m_name']);assert val.startswith('Int|1|')
   for p in s.get('m_Properties',[]):
    if p.get('name')=='value-vars':
     import re
     p['value']=re.sub(r'(\{SelectedFormation(?:Human|AI|Default)?\}\{)Int\|0\|',r'\1Int|1|',p['value'])
     p['value']=p['value'].replace('Highlight18x10'+side,'HighlightSixColumns'+side)
  assert len(selected)==4
  panels=[oop.data(i) for i,r in oop.r.items() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.FMTacticsPanel']
  assert panels and all(s['Orientation']==0 and s['FlipPositions']==0 for s in panels)
  assert all(s['PositionTemplateAsset']['m_AssetGUID']==asset_guid(G,find(G,'HighlightPhaseSpecificFeetAndCondition').path_id) for s in panels if 'PositionTemplateAsset' in s and s['PositionTemplateAsset']['m_AssetGUID'])
  oop.save()
  d=Doc(G,name='HighlightIntegrated'+side+'StatsAndFormation');original=copy.deepcopy(d.d);row=d.named('IntegratedTeamStatsAndFormationRow');stats=d.named('Fixed'+side+'FirstStatsPageContext');carousel=Doc(G,name='HighlightLower'+side+'SixPageCarousel')
  instance=d.add(carousel,1013,row,side+'OutOfPossessionSelector');alias='HighlightSixColumns'+side+'OOP';d.a(instance)['m_TemplateAlias']=alias;d.data(instance)['templateId']=alias
  d.d['m_Usings'].append({'alias':alias,'path':guid,'asset':{'m_FileID':0,'m_PathID':0}})
  order=[stats,instance,1002] if side=='Home' else [1002,instance,stats]
  for i in order:d.move(i,row)
  for i in order:
   weight=3 if i==stats else 3.5
   d.st(i,[(131105,{'m_ValueType':1,'valueIndex':2}),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131095,NONE),(131094,NONE),(131082,d.px(0)),(131084,d.num(weight)),(131085,d.num(1))])
  assert d.a(row)['m_Children']==[{'rid':i} for i in order]
  # Every old binding/event remains identical; only new sibling and flex sizing added.
  for i,r in refs(original).items():
   if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,(side,i,'Existing binding changed')
  d.save();dependency_sources[asset_guid(G,d.obj.path_id)]=[guid]
 for name in names:
  ob=find(T,name);tr=tree(T,ob.path_id);old=copy.deepcopy(tr['m_gridComponents']);assert len(old)==8
  regpid=tr['m_gridElementSet']['m_PathID'];reg=tree(T,regpid);description_refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:description_refs+=group['m_tiles']
  descs={tree(T,r['m_PathID']).get('<ID>k__BackingField'):r['m_PathID'] for r in description_refs}
  assert 'LiveTable' in descs
  # Full native grid menu, exactly like the existing xG slot, not the custom six-page carousel.
  native=copy.deepcopy(old[6]);native['m_elementID']='LiveTable';native['m_configDescriptions']=[{'m_FileID':0,'m_PathID':descs['LiveTable']}];native['m_configDescriptionKeys']=[];native['m_gridElementConfigs']=[config(descs['LiveTable'],4,3)]
  blocks=[copy.deepcopy(old[i]) for i in [0,2,4,5,1,6]]+[native]
  positions=[(0,0,10,5),(10,0,10,5),(0,5,4,3),(4,5,4,3),(8,5,4,3),(12,5,4,3),(16,5,4,3)]
  for b,(x,y,w,h) in zip(blocks,positions):
   b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h};b['m_gridElementConfigs']=[config(c['Description']['m_PathID'],w,h,c['AssetRef']) for c in b['m_gridElementConfigs']]
  # All native menu choices need the new bottom 4x3 dimensions.
  for pid in set(descs.values()):
   if tree(T,pid).get(CK):config(pid,4,3)
  tr['m_gridComponents']=blocks;tr['m_layoutPreset']={'Name':'','Size':{'x':20,'y':8}};tr['m_optionalSlices']['m_instantiationOrder']=list(range(7));tr['m_compositionVersion']+=1;tr['m_placementBindings']=[{'m_elementID':b['m_elementID'],'m_optionalConditions':[],'m_optionalConfigConditions':[]} for b in blocks]
  cells=[(x,y) for b in blocks for x in range(b['m_location']['x'],b['m_location']['x']+b['m_location']['width']) for y in range(b['m_location']['y'],b['m_location']['y']+b['m_location']['height'])];assert len(cells)==len(set(cells))==160 and all(0<=x<20 and 0<=y<8 for x,y in cells);save(T,ob.path_id,tr)
  p=cache_root/name
  if tag=='game' and p in cache_before:
   cached=json.loads(cache_before[p].decode('utf8'));previous=cached['m_gridComponents'];assert len(previous)==8;updated=copy.deepcopy(cached);cb=[copy.deepcopy(previous[i]) for i in [0,2,4,5,1,6]]+[copy.deepcopy(native)]
   # Replace instance IDs only on the new native slot; retain all other selections.
   cb[-1]['m_configDescriptions']=[{'instanceID':0}];cb[-1]['m_configDescriptionKeys']=['LiveTable']
   for c in cb[-1]['m_gridElementConfigs']:c['Description']={'instanceID':0};c['Asset']={'instanceID':0}
   for b,(x,y,w,h) in zip(cb,positions):
    b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h}
    for c in b['m_gridElementConfigs']:c['Size']={'x':w,'y':h}
    key=(b.get('m_configDescriptionKeys') or [b['m_elementID']])[0];assert key in descs
    for c in b['m_gridElementConfigs']:config(descs[key],w,h,c['AssetRef'])
   updated['m_gridComponents']=cb;updated['m_layoutPreset']=copy.deepcopy(tr['m_layoutPreset']);updated['m_optionalSlices']=copy.deepcopy(tr['m_optionalSlices']);updated['m_placementBindings']=copy.deepcopy(tr['m_placementBindings']);updated['m_compositionVersion']=tr['m_compositionVersion'];cache_outputs[p]=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8')
  audits.append({'variant':tag,'layout':name,'grid':[20,8],'upper_lower':[5,3],'upper_columns':[3,3.5,3.5,3.5,3.5,3],'logical_top_slots':[10,10],'bottom_columns':[4]*5,'bottom_order':['MatchMomentum','MatchStatsStandAlone','live pitch and four maps','xGStory','LiveTable native picker'],'native_menu_choices_sized':True,'existing_formation_bindings_preserved':True,'out_of_possession_default':1})
'''
footer=' # Register new private assets'+old.split(' # Register new private assets',1)[1]
# New clones are only G assets; keep existing descriptor registration paths unaltered.
footer=footer[:footer.index("(OUT/'install-after-game-exits.ps1')")]+r'''
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('20×8网格、上5下3。上方两个10格原生容器，内部各按3/3.5/3.5和3.5/3.5/3布局，总六列为主队统计/无球/有球/客队有球/无球/统计；无球副本默认第二页，保留原生左右脚及选择器、竖向阵型。下方五等宽依次比赛势头/比赛统计/原球场与四图/xG/原生可选区默认实时积分榜。复用当前样式和数据绑定，保留其他原生选择，缓存同步。分别备份游戏与皮肤，restore.ps1哈希保护。文件检查通过，实际游戏内显示尚未验证。','utf8')
print(OUT)
'''
(R/'build-highlight-six-top-five-bottom.py').write_text(header+body+footer,'utf8')
