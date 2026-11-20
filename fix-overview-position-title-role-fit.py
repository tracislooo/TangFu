from pathlib import Path
import ast,copy,json,uuid,importlib.util
boot=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8').split('ROW=-940000000006000;')[0].replace('F:/Steam/steamapps/common/Project Taco/','F:/Steam/steamapps/common/Football Manager 27/').replace('photo-up3-titled-pros-cons-tactics-thirds-','overview-position-headings-role-fit-')
boot=boot.replace('for n in [W,G]:assert before[GAME/n]==before[SKIN/n]', '# target bundles may differ; patch only the requested objects')
exec(compile(boot,'bootstrap','exec'))
newassets=[]
for bn,sourcekey,pid,label in [('ui-tableviews_assets_all.bundle','cc14c4f1722a75c4c9267bf074000f3f',-940000000019000,'OverviewCompactRoleView234'),('ui-tablefactories_assets_all.bundle','494078080b489c44fae783144f43505c',-940000000019001,'OverviewCompactRoleFactory234')]:
 for folder in [GAME,SKIN]:
  path=folder/bn;before[path]=path.read_bytes();dest=OUT/('backup-game' if folder==GAME else 'backup-skin')/bn;dest.write_bytes(before[path])
 assert before[GAME/bn]==before[SKIN/bn]
 env[bn]=UnityPy.load(before[GAME/bn]);objs[bn]={o.path_id:o for o in env[bn].objects};hashes[bn]={i:sha(o.get_raw_data()) for i,o in objs[bn].items()};changed[bn]={}
 ab=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=ab.read_typetree();entry=next(v for k,v in meta['m_Container'] if k==sourcekey);srcid=entry['asset']['m_PathID'];doc=objs[bn][srcid].read_typetree();doc['m_Name']=label
 assert pid not in objs[bn];assert str(pid) not in (R/'reserved-texture-ids.json').read_text('utf8')
 if 'm_tableView' in doc:
  for c in doc['m_tableView']['m_tableConfig']:
   m=c['m_columnMetadata'];cid=c['m_columnID']
   if cid=='star-rating':m['m_widthOverride']=75.;m['m_minWidthOverride']=75.
   else:m['m_widthOverride']=60.;m['m_minWidthOverride']=35.
 else:
  for c in doc['m_rowData']:
   if c['m_id']=='star-rating':c['m_defaultWidth']=75.;c['m_minimumWidth']=75.;c['m_allowWidthAutoResizing']=0
   elif c['m_id'] in ['role-name','role-name-short']:c['m_defaultWidth']=60.;c['m_minimumWidth']=35.
   elif c['m_id']=='selection':c['m_defaultWidth']=24.;c['m_minimumWidth']=24.
 o=copy.copy(objs[bn][srcid]);o.path_id=pid;o.assets_file.objects[pid]=o;objs[bn][pid]=o;o.save_typetree(doc);changed[bn][pid]=doc
 key=uuid.uuid5(uuid.NAMESPACE_URL,label).hex;span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
 for x in span:
  if x['m_FileID']==0 and x['m_PathID']==srcid:x['m_PathID']=pid
 meta['m_Container'].append((key,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':pid}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda x:x[0]);ab.save_typetree(meta);changed[bn][ab.path_id]=meta;newassets.append((bn,sourcekey,key,pid))
viewkey=newassets[0][2];factorykey=newassets[1][2]
for pid in [-940000000005000,-940000000008000,-940000000010020]:
 doc=objs[G][pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree()
 title=next((i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText' and rr[r['data']['m_SerializedData']['rid']]['data'].get('name')=='player-pos-title-text'),None)
 if title is not None:override(rr[title]['data'],[prop(65540,en('none'))])
 if pid!=-940000000005000:
  table=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.StreamedTable' and rr[r['data']['m_SerializedData']['rid']]['data'].get('SelectedItemsBinding',{}).get('m_path')=='rolemask');s=rr[rr[table]['data']['m_SerializedData']['rid']]['data']
  b=bytes(s['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert b.count(b'cc14c4f1722a75c4c9267bf074000f3f')==1;s['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(b.replace(b'cc14c4f1722a75c4c9267bf074000f3f',viewkey.encode()));s['FactoryAsset']['m_AssetGUID']=factorykey
  rr[table]['data'].setdefault('m_Classes',[]).append('fm27-compact-role-table234');ptr={'m_FileID':0,'m_PathID':sid}
  if ptr not in rr[table]['data']['m_Stylesheets']:rr[table]['data']['m_Stylesheets'].append(ptr)
  idx=rule([prop(65537,px(10))]);sheet['m_Rules'][idx]['m_ComplexSelectors']=[{'m_Specificity':11,'m_Selectors':[{'m_Parts':[{'m_Value':'fm27-compact-role-table234','m_Type':3}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':'SIText','m_Type':1}],'m_PreviousRelationship':2}],'ruleIndex':idx}]
 validate_ui(doc,sheet);objs[G][pid].save_typetree(doc);objs[G][sid].save_typetree(sheet);changed[G][pid]=doc;changed[G][sid]=sheet
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
outputs={}
for folder in [GAME.parent,SKIN]:
 for name in ['catalog.bin','catalog.hash']:
  path=folder/name;before[path]=path.read_bytes();(OUT/('backup-game' if folder==GAME.parent else 'backup-skin')/name).write_bytes(before[path])
 c=cm.Catalog(before[folder/'catalog.bin'])
 for bn,sourcekey,key,pid in newassets:
  loc=c.locations(sourcekey)[0];c=cm.Catalog(c.add_key_location(key,loc,loc));newloc=c.locations(key)[0];assert c.location(c.location(newloc)['dependencies'][0])['internal'].endswith(bn)
 outputs[folder/'catalog.bin']=bytes(c.data);outputs[folder/'catalog.hash']=hashlib.md5(bytes(c.data)).hexdigest().encode('ascii')
for bn in [G]+[a[0] for a in newassets]:
 b=env[bn].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects}
 for i,h in hashes[bn].items():
  if i not in changed[bn]:assert sha(check[i].get_raw_data())==h,(bn,i)
 for i,d in changed[bn].items():assert check[i].read_typetree()==d,(bn,i)
 (OUT/bn).write_bytes(b)
 outputs[GAME/bn]=b
 skinenv=UnityPy.load(before[SKIN/bn]);skinobs={o.path_id:o for o in skinenv.objects}
 for i,d in changed[bn].items():
  if i in hashes[bn]:
   assert sha(skinobs[i].get_raw_data())==hashes[bn][i],('target object differs in skin',bn,i)
   skinobs[i].save_typetree(d)
  else:
   o=copy.copy(objs[bn][i]);o.assets_file=next(iter(skinobs.values())).assets_file;o.assets_file.objects[i]=o
 outputs[SKIN/bn]=skinenv.file.save(packer='lz4')
for path,b in before.items():assert path.read_bytes()==b
report={'installed':False,'runtime_verified':False,'hide_position_heading_versions':[1,2,3,4],'compact_roles_versions':[2,3,4],'role_font_px':10,'star_column_min_px':75,'role_column_min_px':35,'private_assets':newassets,'output':str(OUT)}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for path in outputs:
 tag='backup-game' if path.parent in [GAME,GAME.parent] else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/path.name)+"' -Destination '"+str(path)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for path,b in outputs.items():
 f=OUT/('prepared-game' if path.parent in [GAME,GAME.parent] else 'prepared-skin');f.mkdir(exist_ok=True);(f/path.name).write_bytes(b)
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for path,b in outputs.items():path.write_bytes(b);assert path.read_bytes()==b
except BaseException:
 for path in outputs:path.write_bytes(before[path])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps(report))


