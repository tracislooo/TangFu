from pathlib import Path
import json,copy,ast,struct,uuid,hashlib,importlib.util
R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle'
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-pitch-flanked-analysis-').replace("'NAMES=[W,G]'","'NAMES=[G,T]'").replace('bases=(W,G)','bases=(G,T)')
exec(compile(prefix,'backup-integrated-highlight','exec'))
helper=ast.parse((R/'build-highlight-five-column-native-player-lists.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['register_clone','clone_doc']],type_ignores=[]),'clone-private-assets','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
CK='<Configurations>k__BackingField';NONE={'m_ValueType':1,'valueIndex':3};asset_clones=[];new_guids={};audits=[];tx=[];cache_outputs={}
names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');cache_before={p:p.read_bytes() for name in names for p in [cache_root/name] if p.exists()}
for p,data in cache_before.items():q=OUT/'backup-cache'/p.name;q.parent.mkdir(exist_ok=True);q.write_bytes(data)
def tree(bn,pid):return copy.deepcopy(changes[bn].get(pid,objs[bn][pid].read_typetree()))
def save(bn,pid,tr):objs[bn][pid].save_typetree(tr);changes[bn][pid]=tr
def asset_guid(bn,pid):
 meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle');return next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==pid)
def ptrs(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():ptrs(x,out)
 elif isinstance(v,list):
  for x in v:ptrs(x,out)

def config(pid,w,h,asset=None):
 desc=tree(T,pid);found=next((c for c in desc[CK] if c['Size']=={'x':w,'y':h} and (asset is None or c['AssetRef']==asset)),None)
 if found:return copy.deepcopy(found)
 candidates=[c for c in desc[CK] if asset is None or c['AssetRef']==asset];assert candidates,(pid,w,h,asset)
 c=copy.deepcopy(min(candidates,key=lambda c:abs(c['Size']['x']-w)+abs(c['Size']['y']-h)));c['Size']={'x':w,'y':h};c['Description']={'m_FileID':0,'m_PathID':pid};desc[CK].append(copy.deepcopy(c));save(T,pid,desc);return c


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
   cb[5]=copy.deepcopy(event);cb[5]['m_configDescriptions']=[{'instanceID':0}];cb[5]['m_configDescriptionKeys']=['MatchEvents'];cb[6]=copy.deepcopy(blocks[6]);cb[6]['m_configDescriptions']=[{'instanceID':0}];cb[6]['m_configDescriptionKeys']=['xGStory']
   for b in [cb[5],cb[6]]:
    for c in b['m_gridElementConfigs']:c['Description']={'instanceID':0};c['Asset']={'instanceID':0}
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
for p,raw in cache_outputs.items():
 src=OUT/('cache-'+p.name+'.json');src.write_bytes(raw);tx.append({'target':str(p),'source':str(src),'backup':str(OUT/'backup-cache'/p.name),'before':sha(cache_before[p]),'after':sha(raw)})
(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'cache_migrations':[str(p) for p in cache_outputs],'protected_sha256':{}},ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');installer=(R/'install-independent-resource-patch.py').read_text('utf8')
if cache_outputs:installer=installer.replace('for row in tx:\n',"allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())\nfor row in tx:\n",1)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')

(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('下排3/3/8/3/3，中央8格内主队两图在左、完整实时球场居中、客队两图在右（内部1/2/1）。原6和7互换，原7改为原生赛事模块MatchEvents。上排六列、20×8及上5下3保持；全部原图绑定与点击数据不变。分别备份游戏和皮肤，restore.ps1哈希保护；游戏内显示待确认。','utf8')
print(OUT)

