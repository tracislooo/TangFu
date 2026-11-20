from pathlib import Path
R=Path(__file__).resolve().parent
exec(compile((R/'patch-preferences-picture-panels.py').read_text('utf8').split('before={};outputs={};changes=[];audit=[]')[0],'<setup>','exec'))
import uuid
L='ui-tileslayouts_assets_all.bundle'
out=R/('preferences-picture-grid-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir()
before={};outputs={};audits=[]
guids=['f4db6cab508a54f5923ce1285e687dd1','7f5394f1ac14510e832ba7ba73485c96']
ids=[-910700000000001,-910700000000002,-910700000000003,-910700000000004]
descids=[-910700000000005,-910700000000006]
assert reserved.isdisjoint(ids+descids)
for folder in [GAME,SKIN]:
 p=folder/W;before[p]=p.read_bytes();e=UnityPy.load(before[p]);a=e.assets[0];obs=a.objects
 # Remove only the previous failed four-object edit, preserving subsequent changes.
 old=UnityPy.load(str(R/'preferences-picture-panels-20261101-rebased'/('backup-game' if folder==GAME else 'backup-skin')/W)).assets[0]
 for name in ['OnlineGamePreferencesTile_4x2','AccessibilityPreferencesTile_4x2']:
  ob=next(o for o in obs.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name);d=ob.read_typetree();sid=d['inlineSheet']['m_PathID']
  ob.set_raw_data(old.objects[ob.path_id].get_raw_data());obs[sid].set_raw_data(old.objects[sid].get_raw_data())
 proto=next(o for o in obs.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AccessibilityPreferencesTile_4x2');pd=proto.read_typetree();pr={r['rid']:r for r in pd['references']['RefIds']};pn=pr[1004];ps=pr[pn['data']['m_SerializedData']['rid']]
 sheetproto=obs[pd['inlineSheet']['m_PathID']]
 bg=UnityPy.load(str(folder/BG)).assets[0];fid=next(i+1 for i,x in enumerate(a.externals) if x.path==f'archive:/{bg.name}/{bg.name}')
 bmobj=next(o for o in obs.values() if o.type.name=='AssetBundle');bm=bmobj.read_typetree()
 for idx,pictures in enumerate([['TFWX'],['BB','DY']]):
  pid,sid=ids[idx*2:idx*2+2];assert pid not in obs and sid not in obs
  name=['PreferenceTFWXPictureTile','PreferenceBBDYPictureTile'][idx]
  d=copy.deepcopy(pd);d.update(m_Name=name,m_Usings=[],inlineSheet={'m_FileID':0,'m_PathID':sid},m_ContentContainerId=0,m_Slots=[],m_AssetEntries=[])
  root=copy.deepcopy(pr[1000]);root['data']['m_Children']=[{'rid':1001}];d['references']['RefIds']=[root]
  s=sheetproto.read_typetree();s['m_Name']=name+'_Style';st=Styles(s)
  rr={1000:root}
  def node(rid,parent,label):
   n=copy.deepcopy(pn);sd=copy.deepcopy(ps);uid=1988100000+rid
   n['rid']=rid;sd['rid']=rid+1;n['data'].update(m_Id=uid,m_Parent={'rid':parent},m_Children=[],m_Classes=[],m_Properties=[],m_RuleIndex=-1,m_SerializedData={'rid':rid+1})
   sd['data'].update(uxmlAssetId=uid,name=label,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
   d['references']['RefIds'] += [n,sd];rr[rid]=n
   if parent!=1000:rr[parent]['data']['m_Children'].append({'rid':rid})
   return n
  stage=node(1001,1000,name)
  st.edit(stage,[st.p(131102,st.en('relative')),st.p(131105,st.pct(100)),st.p(131087,st.pct(100)),st.p(131096,st.px(140)),st.p(131084,st.num(1))],reset=True)
  for i,picture in enumerate(pictures):
   n=node(1003+i*2,1001,picture);ptr={'m_FileID':fid,'m_PathID':int(records[picture]['path_id'])}
   assert bg.objects[ptr['m_PathID']].peek_name()==picture
   st.edit(n,[st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131104,st.pct(i*52)),st.p(131105,st.pct(100)),st.p(131087,st.pct(100 if len(pictures)==1 else 48)),st.p(458753,st.h(6,ptr)),st.p(262153,st.en('scale-to-fit'))],reset=True)
  for source,tree,newid in [(proto,d,pid),(sheetproto,s,sid)]:
   ob=copy.copy(source);ob.path_id=newid;ob.assets_file=a;ob.data=None;ob._read_until=None;ob.set_raw_data(source.get_raw_data());obs[newid]=ob;ob.save_typetree(tree)
  start=len(bm['m_PreloadTable']);bm['m_PreloadTable'] += [{'m_FileID':0,'m_PathID':pid},{'m_FileID':0,'m_PathID':sid}]
  bm['m_Container'].append((guids[idx],{'preloadIndex':start,'preloadSize':2,'asset':{'m_FileID':0,'m_PathID':pid}}))
 bm['m_Container'].sort(key=lambda x:x[0]);bmobj.save_typetree(bm);outputs[p]=e.file.save(packer='lz4')
 lp=folder/L;before[lp]=lp.read_bytes();le=UnityPy.load(before[lp]);la=le.assets[0];lo=la.objects
 desc=next(o for o in lo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='OnlineGamePreferencesTileDescription')
 for idx,pid in enumerate(descids):
  assert pid not in lo;d=desc.read_typetree();name=['PreferenceTFWXPictures','PreferenceBBDYPictures'][idx];d['m_Name']=name+'Description';d['<Name>k__BackingField']=name;d['<ID>k__BackingField']=name;d['m_availabilityPath']={'m_path':''}
  for config in d['<Configurations>k__BackingField']:
   config['Description']={'m_FileID':0,'m_PathID':pid};config['AssetRef']['m_AssetGUID']=guids[idx]
  ob=copy.copy(desc);ob.path_id=pid;ob.assets_file=la;ob.data=None;ob._read_until=None;ob.set_raw_data(desc.get_raw_data());lo[pid]=ob;ob.save_typetree(d)
 for ob in list(lo.values()):
  if ob.type.name!='MonoBehaviour':continue
  name=ob.peek_name() or ''
  if name=='OverviewPreferencesFMMenuCardGridElementSet':
   d=ob.read_typetree();d['m_gridElementDescriptions'] += [{'m_FileID':0,'m_PathID':x} for x in descids];ob.save_typetree(d)
  if name in ['OverviewPreferencesFMMenuCardGridComposition','OverviewPreferencesFMMenuCardGridComposition-FMC']:
   d=ob.read_typetree();targets=[x for x in d['m_gridComponents'] if x['m_elementID'] in ['OnlineGamePreferences','AccessibilityPreferencesTile']]
   assert len(targets)==2
   for idx,element in enumerate(targets):
    image=copy.deepcopy(element);element['m_location']['height']=1
    image['m_elementID']=['PreferenceTFWXPictures','PreferenceBBDYPictures'][idx];image['m_location']['y']=5;image['m_location']['height']=2
    image['m_configDescriptions']=[{'m_FileID':0,'m_PathID':descids[idx]}]
    for config in image['m_gridElementConfigs']:
     config['Description']={'m_FileID':0,'m_PathID':descids[idx]};config['AssetRef']['m_AssetGUID']=guids[idx]
    d['m_gridComponents'].append(image);d['m_placementBindings'].append({'m_elementID':image['m_elementID'],'m_optionalConditions':[],'m_optionalConfigConditions':[]})
   ob.save_typetree(d)
 outputs[lp]=le.file.save(packer='lz4')
 sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
 cp=(GAME.parent if folder==GAME else folder)/'catalog.bin';before[cp]=cp.read_bytes();cb=before[cp]
 for guid in guids:
  c=cm.Catalog(cb);loc=next(x for x in c.locations('ae9bdc5188c75f04d8e6e2df495fa461') if c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');cb=c.add_key_location(guid,loc,loc)
 c=cm.Catalog(cb)
 for guid in guids:
  locs=c.locations(guid);assert len(locs)==1;v=c.location(locs[0]);assert v['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'
  assert any(c.location(x)['internal'].endswith('\\'+BG) for x in v['dependencies'])
 outputs[cp]=cb;hp=cp.with_name('catalog.hash');before[hp]=hp.read_bytes();outputs[hp]=hashlib.md5(cb).hexdigest().encode('ascii')
 audits.append({'folder':str(folder),'new_picture_template_guids':guids,'catalog_background_dependencies_verified':True})
 # Assert unrelated existing objects are byte-identical after serialization.
 for path in [p,lp]:
  olda=UnityPy.load(before[path]).assets[0];newa=UnityPy.load(outputs[path]).assets[0]
  changed=[i for i in olda.objects if olda.objects[i].get_raw_data()!=newa.objects[i].get_raw_data()]
  if path==p:assert len(changed)==5
  else:assert len(changed)==3
items=[]
for p,b in outputs.items():
 tag='game' if p.parent in [GAME,GAME.parent] else 'skin';source=Path(tag)/p.name;backup=Path('backup-'+tag)/p.name
 for rel,content in [(source,b),(backup,before[p])]:
  (out/rel).parent.mkdir(exist_ok=True);(out/rel).write_bytes(content)
 items.append({'target':str(p),'source':source.as_posix(),'backup':backup.as_posix(),'before_sha256':sha(before[p]),'after_sha256':sha(b)})
protected={str(p):sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p not in outputs}
m={'installed':False,'runtime_verified':False,'install_files':items,'protected_sha256':protected,'catalog_audits':audits,'layout':'Native settings row y4 height1, image row y5 height2; left TFWX, right BB above DY'}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
source=ast.parse((R/'add-start-screen-kunshan-overlay.py').read_text('utf8'))
for n in source.body:
 if isinstance(n,ast.FunctionDef) and n.name=='install':n.body=n.body[:-1]
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['running','install']],type_ignores=[]),'<installer>','exec'))
for action,flag in [('install',''),('restore',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'fix-preferences-picture-grid-install.py')+"' '"+str(out)+"'"+flag+'\n','utf8')
assert all(p.read_bytes()==before[p] for p in outputs)
print(out,flush=True);install(out)
