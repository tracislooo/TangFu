from pathlib import Path
import json,re,types
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle';V='ui-tableviews_assets_all.bundle';VS=V+'::skin'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-lower-oop-eightstats-footer-').replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F,T,V]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]','if SKIN/n in before and n!=V:assert before[SKIN/n]==before[GAME/n]')
exec(compile(boot,'backup-current-resources','exec'))
env[VS]=UnityPy.load(before[SKIN/V]);objs[VS]={o.path_id:o for o in env[VS].objects};hashes[VS]={i:sha(o.get_raw_data()) for i,o in objs[VS].items()};changes[VS]={}
registry=json.loads((R/'reserved-texture-ids.json').read_text('utf8'));reserved_ids={int(x['path_id']) for x in registry['reserved_textures']};reserved_names={x['name'].lower() for x in registry['reserved_textures']}
main=Doc(G,name='MatchViewer_12x4');asset_clones=[];new_guids={}
source=(R/'build-highlight-five-column-native-player-lists.py').read_text('utf8');helpers=ast.parse(source)
exec(compile(ast.Module(body=[x for x in helpers.body if isinstance(x,ast.FunctionDef) and x.name in ['register_clone','clone_doc','allptr']],type_ignores=[]),'private-asset-helpers','exec'))
helper=ast.parse((R/'build-match-ui-avatars-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[x for x in helper.body if isinstance(x,ast.FunctionDef) and x.name in ['rewrite_arg','rewrite_binding']],type_ignores=[]),'binding-path-helper','exec'))
def unpack(raw):
 raw=bytes(raw);p=1;out=[]
 for _ in range(raw[0]):
  n=struct.unpack_from('<I',raw,p)[0];p+=4;out.append(bytearray(raw[p:p+n]));p+=n
 assert p==len(raw);return out
def pack(args):return list(bytes([len(args)])+b''.join(struct.pack('<I',len(x))+x for x in args))
lookup={};pidguid={}
for bn in env:
 meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle')
 lookup[bn]={}
 for key,entry in meta['m_Container']:
  pid=entry['asset']['m_PathID'];pidguid.setdefault((bn,pid),key)
  ob=objs[bn].get(pid)
  if not ob or ob.type.name!='MonoBehaviour':continue
  tree=ob.read_typetree()
  if 'm_Rules' not in tree:lookup[bn].setdefault(key,pid)
def resolve(guid):
 hits=[(bn,pid) for bn,m in lookup.items() if bn!=VS for k,pid in m.items() if k==guid]
 assert len(hits)==1,(guid,hits)
 return hits[0]
def simple_clone(bn,pid,newpid,name,tree=None,register=True):
 assert newpid not in objs[bn] and newpid not in reserved_ids and name.lower() not in reserved_names
 src=objs[bn][pid];tree=copy.deepcopy(tree if tree is not None else src.read_typetree());tree['m_Name']=name
 ob=copy.copy(src);ob.path_id=newpid;ob.data=None;ob._read_until=None;ob.assets_file.objects[newpid]=ob;objs[bn][newpid]=ob;ob.save_typetree(tree);changes[bn][newpid]=copy.deepcopy(tree)
 guid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/highlight-oop-eight-stats/'+name).hex
 if register:asset_clones.append({'bundle':bn,'pid':newpid,'guid':guid,'name':name,'source_guid':pidguid[(bn,pid)]})
 return tree,guid
AUTO={'m_ValueType':1,'valueIndex':2}

# Native eight-field data, retaining PlayerMatchStats rows and localized metrics.
factory_source=objs[F][lookup[F]['87bd2578ac5057a0a370123b4c1e836d']]
old_factory=factory_source.read_typetree();old_cols={c['m_id']:c for c in old_factory['m_rowData']}
extended=find(F,'PlayerStatsExtendedFactory').read_typetree();ext={c['m_id']:c for c in extended['m_rowData']}
fitness=find(F,'TacticTeamSelectionTableFactory').read_typetree();fit={c['m_id']:c for c in fitness['m_rowData']}
factory,factory_guid=simple_clone(F,factory_source.path_id,-981028000001000,'HighlightEightFieldsFactory')
pos_bn,pos_pid=resolve(ext['picked-position']['m_uxmlRef']['m_AssetGUID'])
posdoc,pos_guid=clone_doc(Doc(pos_bn,pid=pos_pid),'HighlightEightFieldsPositionCell',-981028000001100)
for i,a in posdoc.r.items():
 if a.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText':posdoc.st(i,[(65537,posdoc.px(struct.unpack('<f',struct.pack('<f',9.8))[0]))])
posdoc.save()
rows=[]
for ident,width in [('picked-position',36),('player',88),('rating',30),('condition',90),('tactics-fatigue-value',40),('clearCutChances',36),('keyPasses',36),('keyTackles',36)]:
 if ident in old_cols:c=copy.deepcopy(old_cols[ident])
 elif ident in fit:c=copy.deepcopy(fit[ident])
 else:c=copy.deepcopy(ext[ident])
 c.update(m_defaultWidth=float(width),m_minimumWidth=float(width),m_allowWidthAutoResizing=0)
 if ident=='picked-position':c['m_uxmlRef']['m_AssetGUID']=pos_guid
 if ident in ['clearCutChances','keyPasses','keyTackles']:c['m_uxmlRef']=copy.deepcopy(old_cols['goals']['m_uxmlRef'])
 if ident=='player':c['m_minimumWidth']=64.;c['m_allowWidthAutoResizing']=1
 rows.append(c)
factory['m_rowData']=rows;objs[F][-981028000001000].save_typetree(factory);changes[F][-981028000001000]=copy.deepcopy(factory)
column_ids=[c['m_id'] for c in rows];assert len(column_ids)==8

view_guid=None
for bn in [V,VS]:
 source_pid=lookup[bn]['c08126334cf0c614a85c220cf1a73090'];tree=objs[bn][source_pid].read_typetree()
 nativecfg=tree['m_tableView']['m_tableConfig'];proto=copy.deepcopy(nativecfg[0]);newcfg=[]
 for ident,row in zip(column_ids,rows):
  c=copy.deepcopy(next((x for x in nativecfg if x['m_columnID']==ident),proto));c['m_columnID']=ident
  c['m_columnMetadata'].update(m_widthOverride=row['m_defaultWidth'],m_minWidthOverride=row['m_minimumWidth'],m_applicableBreakpoints=-1,m_required=1)
  c['m_columnMetadata']['m_titleTranslationIdOverride']['GameID']=0;newcfg.append(c)
 tree['m_tableView']['m_tableConfig']=newcfg
 tree,vg=simple_clone(bn,source_pid,-981028000001200,'HighlightEightFieldsView',tree)
 if view_guid is None:view_guid=vg
 else:assert vg==view_guid

# The lower copy retains the upper native OOP machinery and direction, but has its own state.
wrapper_guids={};wrapper_audits=[]
for side,pid,flip in [('Home',-981025000002000,1),('Away',-981025000002100,0)]:
 donor=Doc(G,pid=pid);doc,guid=clone_doc(donor,'HighlightLower'+side+'StatsAndOOP',-981028000002000-(0 if side=='Home' else 10))
 for var in ['SelectedFormationHuman','SelectedFormationAI','SelectedFormationDefault']:
  rewrite_binding(doc.d,var,'HighlightLower'+side+var)
 doc.r=refs(doc.d)
 for v in doc.r[1011]['data']['ValueVariables']:
  if v['m_name']=='SelectedFormation' or v['m_name'].startswith('HighlightLower'+side+'SelectedFormation'):
   v['m_scopeValue']['m_serializedData']=v['m_scopeValue']['m_serializedData'].replace('Int|0|','Int|2|',1)
 for p in doc.a(1005)['m_Properties']:
  if p['name']=='value-vars':p['value']=re.sub(r'(\{(?:SelectedFormation|HighlightLower'+side+r'SelectedFormation(?:Human|AI|Default))\}\{Int\|)0\|',r'\g<1>2|',p['value'])
 for node in [1036,1037,1039,1040]:
  dropdown_data=doc.data(node);args=unpack(dropdown_data['BindChoicesFunction']['m_inputs']['m_variable']['m_argumentBytes'])
  a=args[0]
  # StructList<BindingPath>: string descriptor, count, then kind/length/name per item.
  marker=b'\x01\x07option';start=bytes(a).find(marker);assert start>0
  args[0]=a[:start-1]+bytearray([2])+bytearray(b'\x01\x07option3\x01\x07option2')
  dropdown_data['BindChoicesFunction']['m_inputs']['m_variable']['m_argumentBytes']=pack(args)
  dropdown_data.update(AlwaysUpdateInternalSelection=1,AlwaysUpdateInternalSelection_UxmlAttributeFlags=1)
 doc.st(1042,[(131081,doc.enum('none'))])
 table=doc.data(1043);table['FactoryAsset']['m_AssetGUID']=factory_guid
 stats_source=Doc(G,pid=-981025000003600);table['InitFunction']=copy.deepcopy(stats_source.data(1028)['InitFunction'])
 raw=bytes(table['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert b'c08126334cf0c614a85c220cf1a73090' in raw
 table['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(raw.replace(b'c08126334cf0c614a85c220cf1a73090',view_guid.encode()))
 table.update(FixedElementSize=24.,FixedElementSize_UxmlAttributeFlags=1,FixedElementSizeControllerOrTouch=24.,FixedElementSizeControllerOrTouch_UxmlAttributeFlags=1,ScrollViewMode=2,ScrollViewMode_UxmlAttributeFlags=1)
 table['HeaderCellAsset']=copy.deepcopy(stats_source.data(1028)['HeaderCellAsset'])
 for panel in [1064,1065]:assert doc.data(panel)['Orientation']==1 and doc.data(panel)['FlipPositions']==flip
 doc.st(1028,[(131084,doc.num(1)),(131096,doc.px(0)),(131105,doc.pct(100))])
 doc.save();wrapper_guids[side]=guid
 wrapper_audits.append({'side':side,'guid':guid,'default_stats_value':2,'dropdown_values':[2,1],'direction_flip':flip,'row_height_px':24,'upper_template_unchanged':True})

# Private descriptors and bindings affect Highlight; halftime and fulltime grid choices stay intact.
CK='<Configurations>k__BackingField';private_desc={};old_stats_pids={'Home':1730867061287688386,'Away':-2842495133054264931}
for side in ['Home','Away']:
 source_pid=old_stats_pids[side];tree=objs[T][source_pid].read_typetree();name='Highlight'+side+'EightStatsAndOOP';tree['<Name>k__BackingField']=name;tree['<ID>k__BackingField']=name
 cfg=copy.deepcopy(next(c for c in tree[CK] if c['Size']=={'x':5,'y':4}));newpid=-981028000003000-(0 if side=='Home' else 10)
 cfg['Description']['m_PathID']=newpid;cfg['AssetRef']['m_AssetGUID']=wrapper_guids[side];cfg['Type']=1;tree[CK]=[cfg]
 tree,_=simple_clone(T,source_pid,newpid,name,tree);private_desc[side]=(newpid,name,cfg)
for name in ['MatchExperienceHumanGridElementSet','MatchExperienceGridElementSet']:
 ob=find(T,name);tree=ob.read_typetree()
 def retarget(v):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_FileID']==0:
    for side,pid in old_stats_pids.items():
     if v['m_PathID']==pid:v['m_PathID']=private_desc[side][0];break
   else:
    for x in v.values():retarget(x)
  elif isinstance(v,list):
   for x in v:retarget(x)
 retarget(tree);ob.save_typetree(tree);changes[T][ob.path_id]=tree
layout_names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague'];versions={}
for name in layout_names:
 ob=find(T,name);tree=ob.read_typetree();old=copy.deepcopy(tree)
 for side in ['Home','Away']:
  oldid='PlayerStats'+side+'Team';newpid,newid,cfg=private_desc[side]
  for a in tree['m_gridComponents']:
   if a['m_elementID']==oldid:
    a['m_elementID']=newid;a['m_configDescriptions']=[{'m_FileID':0,'m_PathID':newpid}];a['m_configDescriptionKeys']=[];a['m_gridElementConfigs']=[copy.deepcopy(cfg)]
  for a in tree['m_placementBindings']:
   if a['m_elementID']==oldid:a['m_elementID']=newid
 tree['m_compositionVersion']+=1;versions[name]={'before':old['m_compositionVersion'],'after':tree['m_compositionVersion']}
 assert [a['m_location'] for a in tree['m_gridComponents']]==[a['m_location'] for a in old['m_gridComponents']]
 ob.save_typetree(tree);changes[T][ob.path_id]=tree
overview=Doc(M,name='OverviewPrototype');overview_before=copy.deepcopy(overview.d)
for record in overview.r.values():
 for group in record.get('data',{}).get('GridCompositionSets',[]):
  bindings=group['m_gridCompositionSetBindings']['m_gridElementBindingData']
  for side in ['Home','Away']:
   originals=[copy.deepcopy(x) for x in bindings if x['DescriptionAndMapping']['DescriptionName']=='PlayerStats'+side+'Team']
   assert originals
   for x in originals:x['DescriptionAndMapping']['DescriptionName']=private_desc[side][1]
   bindings.extend(originals)
overview.save()

# Referee: use the same selected fixture that supplies the working central statistics.
ref=main.named('HighlightRefereeText');assert main.data(ref)['TextBinding']['m_direct']['Path']['m_path']=='match.MatchReferee.Name'
main.data(ref)['TextBinding']['m_direct']['Path']['m_path']='fixturetouse.MatchReferee.Name'
main.save()

# Footer: equal flexible halves around a fixed centered hyphen.
footer_audits=[]
for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']:
 doc=Doc(W,name=name);original=copy.deepcopy(doc.d);pos=doc.named('PosTitleSwitch');roletext=doc.named('MatchCardRoleAndDutyText');rolebox=doc.a(doc.a(roletext)['m_Parent']['rid'])['m_Parent']['rid'];header=doc.a(pos)['m_Parent']['rid']
 assert doc.a(rolebox)['m_FullTypeName']=='SI.Bindable.BindingRemapper'
 row=doc.add(doc,1019,header,'MatchPositionDutyHeader');doc.move(row,header,0)
 doc.st(header,[(131102,doc.enum('relative'))])
 doc.st(row,[(131102,doc.enum('absolute')),(131089,doc.px(0)),(131103,doc.px(0)),(131104,doc.px(0)),(131080,doc.px(0)),(131083,doc.enum('row')),(131073,doc.enum('center'))])
 doc.move(pos,row);dash=doc.add(doc,1036,row,'MatchPositionDutyDash');doc.move(rolebox,row)
 for node in [pos,rolebox]:
  doc.st(node,[(131105,doc.px(0)),(131082,doc.px(0)),(131097,doc.px(0)),(131084,doc.num(1)),(131085,doc.num(1)),(131087,doc.pct(100))]+[(p,doc.px(0)) for p in [131090,131091,131092,131093,131098,131099,131100,131101]])
 for child in doc.a(pos)['m_Children']:
  i=child['rid'];doc.st(i,[(131105,doc.pct(100)),(65546,doc.enum('middle-right')),(65552,doc.enum('nowrap')),(131097,doc.px(0))])
 ds=doc.data(dash);ds.update(text='-',text_UxmlAttributeFlags=1,TextBinding_UxmlAttributeFlags=0,DebugDisplay='');ds['TextBinding']['m_kind']=0
 doc.a(dash)['m_Classes']=['content-no-wrap'];doc.size(dash,8,16);doc.st(dash,[(65537,doc.px(10)),(65546,doc.enum('middle-center'))])
 doc.st(roletext,[(131105,doc.pct(100)),(131097,doc.px(0)),(65546,doc.enum('middle-left')),(65552,doc.enum('nowrap'))])
 assert doc.data(roletext)['TextBinding']==sd(refs(original),roletext)['TextBinding']
 doc.save();footer_audits.append({'name':name,'position_node':pos,'role_context':rolebox,'dash_node':dash,'equal_width_halves':True,'role_binding_preserved':True})

# Update preload spans including dependencies of new private objects.
for bn in env:
 mo=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=mo.read_typetree();old_meta=copy.deepcopy(meta)
 for c in [x for x in asset_clones if x['bundle']==bn]:meta['m_Container'].append((c['guid'],{'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':c['pid']}}))
 for key,entry in meta['m_Container']:
  pid=entry['asset']['m_PathID']
  if pid not in changes[bn]:continue
  span=[] if pid not in hashes[bn] else copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]);allptr(changes[bn][pid],span)
  if pid in objs[bn] and 'inlineSheet' in changes[bn][pid]:allptr(changes[bn].get(changes[bn][pid]['inlineSheet']['m_PathID'],{}),span)
  ptr={'m_FileID':0,'m_PathID':pid}
  if ptr not in span:span.append(ptr)
  entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
 if meta!=old_meta:mo.save_typetree(meta);changes[bn][mo.path_id]=meta
spec=importlib.util.spec_from_file_location('eightstats_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog=before[GAME.parent/'catalog.bin'];unique={c['guid']:c for c in asset_clones if c['bundle']!=VS}
for c in unique.values():
 cat=cm.Catalog(catalog);locs=cat.locations(c['source_guid']);wanted='UnityEngine.UIElements.VisualTreeAsset' if c['bundle']==G else None
 loc=next((x for x in locs if not wanted or cat.location(x)['type'][1]==wanted));catalog=cat.add_key_location(c['guid'],loc,loc)
cat=cm.Catalog(catalog);preload_key='GlobalVisualTreeAssetPreload';extra=[cat.locations(c['guid'])[0] for c in asset_clones if c['bundle']==G]
idx=next(i for i,(k,_) in enumerate(cat.keys()) if k==preload_key);ko,ls=cat.key_records[idx];locs=[v[0] for v in cat.array(ls,'I')]+extra
records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',p) for p in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catalog=bytes(cat.data)
oldcat=cm.Catalog(before[GAME.parent/'catalog.bin']);cc=cm.Catalog(catalog);keys=dict(cc.keys());assert set(keys)==set(dict(oldcat.keys()))|set(unique)
for k,l in oldcat.keys():assert [x[0] for x in cc.array(keys[k],'I')]==[x[0] for x in oldcat.array(l,'I')]+(extra if k==preload_key else [])

# Save independent packages, verify every untouched original object, and preserve all image bundles.
outputs={};checks=[]
for bn in env:
 data=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated original asset changed',bn,pid)
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree,('Roundtrip mismatch',bn,pid)
 for doc in [d for d in documents if d.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 assert reserved_ids.isdisjoint(set(saved)-set(hashes[bn]))
 dest=OUT/('output-skin' if bn==VS else 'output-game')/(V if bn==VS else bn);dest.parent.mkdir(exist_ok=True);dest.write_bytes(data);outputs[bn]=dest
 checks.append({'bundle':bn,'changed_objects':len(changes[bn]),'all_original_unrelated_objects_unchanged':True})
for side,basepid in [('Home',-981025000002000),('Away',-981025000002100)]:
 assert basepid not in changes[G] and objs[G][basepid].read_typetree()['m_Name']=='Highlight'+side+'HorizontalFormation'
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h

migration_code='import copy\nVERSIONS='+repr(versions)+'\nIDS='+repr({('PlayerStats'+side+'Team'):private_desc[side][1] for side in ['Home','Away']})+'''
def migrate_layout(document,forward=True,version=None,limits_from=None):
 if not forward:
  assert limits_from is not None
  return copy.deepcopy(limits_from)
 result=copy.deepcopy(document)
 for a in result['m_gridComponents']:
  if a['m_elementID'] in IDS:
   a['m_elementID']=IDS[a['m_elementID']];a['m_configDescriptionKeys']=[a['m_elementID']];a['m_configDescriptions']=[];a['m_gridElementConfigs']=[]
 for a in result.get('m_placementBindings',[]):
  if a['m_elementID'] in IDS:a['m_elementID']=IDS[a['m_elementID']]
 result['m_compositionVersion']=version
 return result
'''
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions')
tx=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for n in NAMES:
  src=outputs[VS if n==V and tag=='skin' else n];p=folder/n;tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/n),'before':sha(before[p]),'after':sha(src.read_bytes())})
 for n,data in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode('ascii'))]:
  src=OUT/n;src.write_bytes(data);p=(folder.parent if tag=='game' else folder)/n;tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/n),'before':sha(before[p]),'after':sha(data)})
migration=types.ModuleType('lower_migration');exec(migration_code,migration.__dict__);cache_audits=[]
for name,ver in versions.items():
 p=cache_root/name
 if not p.exists():continue
 original=p.read_bytes();old=json.loads(original);new=migration.migrate_layout(old,version=ver['after']);assert migration.migrate_layout(new,False,limits_from=old)==old
 assert [c['m_location'] for c in new['m_gridComponents']]==[c['m_location'] for c in old['m_gridComponents']]
 dest=OUT/'cache-output'/name;dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(new,ensure_ascii=False,indent=2),'utf8');backup=OUT/'backup-custom'/name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(original)
 tx.append({'target':str(p),'source':str(dest),'backup':str(backup),'before':sha(original),'after':sha(dest.read_bytes())});cache_audits.append(name)
other_caches={p:sha(p.read_bytes()) for p in cache_root.iterdir() if p.is_file() and p.name not in cache_audits} if cache_root.exists() else {}
for p,h in other_caches.items():protected[p]=h
report={'installed':False,'runtime_verified':False,'output':str(OUT),'columns':column_ids,'column_widths':[r['m_defaultWidth'] for r in rows],'wrappers':wrapper_audits,'upper_choices_preserved':True,'footer':footer_audits,'referee_name_binding':'fixturetouse.MatchReferee.Name','referee_native_fixture_path_verified_in_preview_templates':True,'row_height_24_to_fit_22_ring':True,'checks':checks,'cache_migration':cache_audits,'new_assets':asset_clones,'protected_sha256':{str(p):h for p,h in protected.items()},'no_texture_bundle_or_reserved_id_changes':True,'catalog_old_locations_preserved':True,'serialization_roundtrip':True}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'grid_migration.py').write_text(migration_code,'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8').replace("Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages').resolve()}","Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages').resolve(),Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve()}")
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('Highlight下方主客队统计使用各自私有横向阵型副本，内建选择器第一项统计、第二项无球阵型；上方所有选项不改，两个下方选择状态独立。统计八列：位置、姓名、评分、体能/比赛状态、原始疲劳、绝佳机会、关键传球、关键断球（原生KeyTackles）。复用原生PlayerMatchStats字段和90px同心百分比组件，24px行高容纳22px圆环，姓名与数值沿用70%字体，窄窗允许横向滚动。仅Highlight四套Large网格及对应缓存改为私有描述，报告网格默认项不改。裁判改用当前MatchViewer统一选定的fixturetouse.MatchReferee.Name，保留此前可见性和宽度保护。底部首发/替补卡片两个展开模板把原职责绑定移到顶部，位置在左、职责在右，中间固定8px“-”，两边等宽紧靠，原职责数据和其他内容不改。不改背景纹理、永久禁用ID或卡面函数。静态/序列化通过，游戏内未验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'columns':column_ids,'private_lower_wrappers':2,'upper_templates_unchanged':True,'cache_migrations':cache_audits,'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
