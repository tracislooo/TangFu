from pathlib import Path
R=Path(__file__).parent
prior=(R/'build-highlight-six-top-five-bottom.py').read_text('utf-8-sig')
header=prior.split("for tag,suffix,folder in [('game','',GAME)")[0].replace('highlight-six-top-five-bottom-','highlight-pitch-flanked-analysis-')
body=r'''
def erase(doc,i):
 for c in list(doc.a(i).get('m_Children',[])):erase(doc,c['rid'])
 a=doc.a(i);doc.a(a['m_Parent']['rid'])['m_Children'].remove({'rid':i});ids={i,a.get('m_SerializedData',{}).get('rid')};doc.d['references']['RefIds']=[r for r in doc.d['references']['RefIds'] if r['rid'] not in ids]
 for j in ids:doc.r.pop(j,None)

for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 G,T=[n+suffix for n in bases];d=Doc(G,name='HighlightFiveAnalysisCenterWithoutMaps');original=copy.deepcopy(d.d);root=1008;pitch=1022;cols=[c['rid'] for c in d.a(2149)['m_Children']];assert len(cols)==2
 assert all(d.a(i)['m_FullTypeName']=='UnityEngine.UIElements.VisualElement' for i in [root,2147,2149])
 for i in [cols[0],pitch,cols[1]]:d.move(i,root)
 for i in [2147,3075,2149]:erase(d,i)
 d.st(root,[(131083,d.enum('row')),(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131095,NONE),(131094,NONE),(131084,d.num(1)),(131085,d.num(1))])
 for i in [cols[0],pitch,cols[1]]:
  d.st(i,[(131102,d.enum('relative')),(131089,{'m_ValueType':1,'valueIndex':2}),(131103,{'m_ValueType':1,'valueIndex':2}),(131104,{'m_ValueType':1,'valueIndex':2}),(131080,{'m_ValueType':1,'valueIndex':2}),(131105,{'m_ValueType':1,'valueIndex':2}),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131095,NONE),(131094,NONE),(131082,d.px(0)),(131084,d.num(2 if i==pitch else 1)),(131085,d.num(1))])
 assert d.a(root)['m_Children']==[{'rid':i} for i in [cols[0],pitch,cols[1]]]
 for i,r in refs(original).items():
  if i in d.r and 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,('Chart data/event changed',i)
 d.save()
 for name in names:
  ob=find(T,name);tr=tree(T,ob.path_id);old=copy.deepcopy(tr['m_gridComponents']);assert len(old)==7
  reg=tree(T,tr['m_gridElementSet']['m_PathID']);description_refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:description_refs+=group['m_tiles']
  descs={tree(T,r['m_PathID']).get('<ID>k__BackingField'):r['m_PathID'] for r in description_refs};assert 'MatchEvents' in descs
  blocks=[copy.deepcopy(old[i]) for i in [0,1,2,3,4,6,5]]
  event=blocks[5];event.update(m_elementID='MatchEvents',m_configDescriptions=[{'m_FileID':0,'m_PathID':descs['MatchEvents']}],m_configDescriptionKeys=[],m_gridElementConfigs=[config(descs['MatchEvents'],3,3)])
  positions=[(0,0,10,5),(10,0,10,5),(0,5,3,3),(3,5,3,3),(6,5,8,3),(14,5,3,3),(17,5,3,3)]
  for b,(x,y,w,h) in zip(blocks,positions):
   b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h};b['m_gridElementConfigs']=[config(c['Description']['m_PathID'],w,h,c['AssetRef']) for c in b['m_gridElementConfigs']]
  assert blocks[:2]==old[:2],'Upper layout changed'
  for pid in set(descs.values()):
   if tree(T,pid).get(CK):config(pid,3,3)
  tr['m_gridComponents']=blocks;tr['m_optionalSlices']['m_instantiationOrder']=list(range(7));tr['m_compositionVersion']+=1;tr['m_placementBindings']=[{'m_elementID':b['m_elementID'],'m_optionalConditions':[],'m_optionalConfigConditions':[]} for b in blocks]
  cells=[(x,y) for b in blocks for x in range(b['m_location']['x'],b['m_location']['x']+b['m_location']['width']) for y in range(b['m_location']['y'],b['m_location']['y']+b['m_location']['height'])];assert len(cells)==len(set(cells))==160 and all(0<=x<20 and 0<=y<8 for x,y in cells);save(T,ob.path_id,tr)
  p=cache_root/name
  if tag=='game' and p in cache_before:
   cached=json.loads(cache_before[p].decode('utf8'));previous=cached['m_gridComponents'];assert len(previous)==7;updated=copy.deepcopy(cached);cb=[copy.deepcopy(previous[i]) for i in [0,1,2,3,4,6,5]]
   cb[5]=copy.deepcopy(event);cb[5]['m_configDescriptions']=[{'instanceID':0}];cb[5]['m_configDescriptionKeys']=['MatchEvents']
   for c in cb[5]['m_gridElementConfigs']:c['Description']={'instanceID':0};c['Asset']={'instanceID':0}
   for b,(x,y,w,h) in zip(cb,positions):
    b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h}
    key=(b.get('m_configDescriptionKeys') or [b['m_elementID']])[0];assert key in descs
    for c in b['m_gridElementConfigs']:c['Size']={'x':w,'y':h};config(descs[key],w,h,c['AssetRef'])
   assert cb[:2]==previous[:2]
   updated['m_gridComponents']=cb;updated['m_optionalSlices']=copy.deepcopy(tr['m_optionalSlices']);updated['m_placementBindings']=copy.deepcopy(tr['m_placementBindings']);updated['m_compositionVersion']=tr['m_compositionVersion'];cache_outputs[p]=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8')
  audits.append({'variant':tag,'layout':name,'grid':[20,8],'upper_lower':[5,3],'upper_objects_unchanged':True,'bottom_columns':[3,3,8,3,3],'bottom_order':['MatchMomentum','MatchStatsStandAlone','home maps / live pitch / away maps','MatchEvents','xGStory'],'center_internal_widths':[1,2,1],'chart_bindings_unchanged':True})
 # Refresh preload spans without registering new assets or rewriting catalogs.
 for bn in [G,T]:
  ob=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=ob.read_typetree()
  for key,entry in meta['m_Container']:
   pid=entry['asset']['m_PathID']
   if pid not in changes[bn]:continue
   span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[bn][pid],span)
   if bn==G and pid==d.obj.path_id:ptrs(d.s,span)
   entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
  save(bn,ob.path_id,meta)
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
  for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t
  if bn==G:validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
  src=OUT/(('skin-' if suffix else '')+base);src.write_bytes(raw);target=folder/base;tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
'''
footer=prior[prior.index('for p,raw in cache_outputs.items():'):]
footer=footer[:footer.index("(OUT/'修改说明.md')")]+"(OUT/'修改说明.md').write_text('下排3/3/8/3/3，中央8格内主队两图在左、完整实时球场居中、客队两图在右（内部1/2/1）。原6和7互换，原7改为原生赛事模块MatchEvents。上排六列、20×8及上5下3保持；全部原图绑定与点击数据不变。分别备份游戏和皮肤，restore.ps1哈希保护；游戏内显示待确认。','utf8')\nprint(OUT)\n"
(R/'build-highlight-pitch-flanked-analysis.py').write_text(header+body+footer,'utf8')

