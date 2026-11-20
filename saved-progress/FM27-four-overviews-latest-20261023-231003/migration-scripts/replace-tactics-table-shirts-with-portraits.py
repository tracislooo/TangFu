from pathlib import Path
source=Path('combine-tactics-condition-sharpness.py').read_text('utf-8-sig');exec(compile(source.split('bge = UnityPy.load')[0].replace('tactics-combined-condition-sharpness-','tactics-table-shirts-to-portraits-').replace('[W, F, V]', '[W, F]'),'boot','exec'))
PID,SID=-970000000008000,-970000000008001;GUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/TacticsPlayerPortraitNameCell/v1').hex;SOURCE=2337472693558817972;FACTORY=-7014073910555419620
for f in [GAME,SKIN]:protected[f/V]=sha((f/V).read_bytes())
doc=obs[W][SOURCE].read_typetree();r=refs(doc);old=copy.deepcopy(r);old_sid=doc['inlineSheet']['m_PathID'];sheet=obs[W][old_sid].read_typetree();st=Styles(sheet);P=st.p;doc['m_Name']='TacticsPlayerPortraitNameCell';doc['inlineSheet']['m_PathID']=SID;sheet['m_Name']='TacticsPlayerPortraitNameCell_Style'
donor=obs[W][-4028782843705546248].read_typetree();dr=refs(donor)
# Replace only the existing shirt renderer; all name/selection widgets are unchanged.
oldshirt=copy.deepcopy(r[1008]);sdrid=oldshirt['data']['m_SerializedData']['rid'];picture=copy.deepcopy(dr[1007]);picture_sd=copy.deepcopy(serial(dr,1007));picture['rid']=1008;picture_sd['rid']=sdrid;picture['data'].update(m_Id=oldshirt['data']['m_Id'],m_Parent=oldshirt['data']['m_Parent'],m_Children=[],m_RuleIndex=-1,m_SerializedData={'rid':sdrid});picture_sd['data'].update(uxmlAssetId=oldshirt['data']['m_Id'],name='TacticsTablePlayerPortrait',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);r[1008].clear();r[1008].update(picture);r[sdrid].clear();r[sdrid].update(picture_sd)
# Native PersonPicture expects 'person'; this cell already maps player from binding.Player.
mapper=copy.deepcopy(r[1038]);mapper_sd=copy.deepcopy(serial(r,1038));next_rid=max(r)+1;newid=max(a.get('data',{}).get('m_Id',0) for a in r.values())+1;mapper['rid']=next_rid;mapper_sd['rid']=next_rid+1;mapper['data'].update(m_Id=newid,m_Parent={'rid':1002},m_Children=[{'rid':1008}],m_RuleIndex=-1,m_SerializedData={'rid':next_rid+1},m_Classes=[],m_Properties=[]);mapper_sd['data'].update(uxmlAssetId=newid,name='TacticsTablePortraitPersonContext',name_UxmlAttributeFlags=1,Mappings=[{'m_serialisedType':0,'from':'person','to':{'m_path':'player'},'type':{'id':1145176065}}],Mappings_UxmlAttributeFlags=1);doc['references']['RefIds'] += [mapper,mapper_sd];r[next_rid]=mapper;r[next_rid+1]=mapper_sd;r[1002]['data']['m_Children']=[{'rid':next_rid}];r[1008]['data']['m_Parent']={'rid':next_rid}
for i in [1002,next_rid,1008]:st.edit(r[i],[P(131105,st.px(28)),P(131087,st.px(28)),P(131097,st.px(28)),P(131095,st.px(28)),P(131096,st.px(28)),P(131094,st.px(28)),P(131084,st.num(0)),P(131085,st.num(0))])
doc['m_Usings'].append(copy.deepcopy(next(u for u in donor['m_Usings'] if u['alias']=='PersonPicture')))
for i,a in old.items():
 if i not in [1002,1008,sdrid]:assert r[i]==a,('existing name/selection event changed',i)
assert not any(a.get('data',{}).get('m_FullTypeName')=='FM.UI.FMTacticsShirt' for a in r.values())
validate_ui(doc,sheet);clone(obs[W][SOURCE],PID,doc);clone(obs[W][old_sid],SID,sheet)
fdoc=obs[F][FACTORY].read_typetree();oldf=copy.deepcopy(fdoc);col=next(c for c in fdoc['m_rowData'] if c['m_id']=='name');assert col['m_uxmlRef']['m_AssetGUID']=='8dc914c8439e7c54b8a97c3b866e2ebe';col['m_uxmlRef']['m_AssetGUID']=GUID;assert sum(a!=b for a,b in zip(fdoc['m_rowData'],oldf['m_rowData']))==1;save(F,FACTORY,fdoc)
metaobj=next(o for o in obs[W].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();entry=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==SOURCE);portrait=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==-4028782843705546248);span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]);span=[p for p in span if not(p['m_FileID']==0 and p['m_PathID'] in [SOURCE,old_sid])];span += [{'m_FileID':0,'m_PathID':PID},{'m_FileID':0,'m_PathID':SID}]
for ptr in meta['m_PreloadTable'][portrait['preloadIndex']:portrait['preloadIndex']+portrait['preloadSize']]+[portrait['asset']]:
 if ptr not in span:span.append(copy.deepcopy(ptr))
meta['m_Container'].append((GUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':PID}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda a:a[0]);save(W,metaobj.path_id,meta)
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);oldcat=cm.Catalog(before[GAME.parent/'catalog.bin']);loc=oldcat.locations('8dc914c8439e7c54b8a97c3b866e2ebe')[0];cat=cm.Catalog(oldcat.add_key_location(GUID,loc,loc));idx=next(i for i,(key,_) in enumerate(cat.keys()) if key=='GameWorldVisualTreeAssetPreload');keyobj,locset=cat.key_records[idx];locs=[a[0] for a in cat.array(locset,'I')]+cat.locations(GUID);records=list(cat.key_records);records[idx]=(keyobj,cat.append(b''.join(struct.pack('<I',i) for i in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*a) for a in records),True));catout=bytes(cat.data);newcat=cm.Catalog(catout);newkeys=dict(newcat.keys());assert set(newkeys)==set(dict(oldcat.keys()))|{GUID}
for key,locset in oldcat.keys():assert [a[0] for a in newcat.array(newkeys[key],'I')]==[a[0] for a in oldcat.array(locset,'I')]+(newcat.locations(GUID) if key=='GameWorldVisualTreeAssetPreload' else [])
outputs={n:env[n].file.save(packer='lz4') for n in [W,F]}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert check.keys()==obs[n].keys()
 for i,h in hashes[n].items():
  if i not in expected[n]:assert sha(check[i].get_raw_data())==h,(n,i)
 for i,data in expected[n].items():assert check[i].read_typetree()==data,(n,i)
 (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catout);hashout=hashlib.md5(catout).hexdigest().encode('ascii');(OUT/'catalog.hash').write_bytes(hashout)
install={f/n:b for f in [GAME,SKIN] for n,b in outputs.items()};install.update({GAME.parent/'catalog.bin':catout,GAME.parent/'catalog.hash':hashout,SKIN/'catalog.bin':catout})
report={'installed':False,'runtime_verified':False,'portrait_size':28,'portrait_source':'native PersonPicture','binding':'binding.Player => player => person','existing_name_and_selection_events_preserved':True,'original_shared_PlayerCell_unchanged':True,'new_cell_guid':GUID,'changed_objects':{n:list(a) for n,a in expected.items()},'after_sha256':{str(p):sha(b) for p,b in install.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"];installer=list(restore)
for p,b in before.items():
 if p.name==V:continue
 tag='backup-skin' if p.parent==SKIN else 'backup-game';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force");installer.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(b)+"') { throw 'Package changed since preparation.' }")
for p in install:installer.append("Copy-Item -LiteralPath '"+str(OUT/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');(OUT/'install.ps1').write_text('\n'.join(installer),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in install.items():p.write_bytes(b)
 for p,b in install.items():assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'portrait_size':28}))


