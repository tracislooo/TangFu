from pathlib import Path
import json,copy,ast,struct,uuid,importlib.util
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','pending-anchor-stats-live-condition-').replace('NAMES=[W,G,M,F]','NAMES=[G,M,F]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]','if False:assert before[SKIN/n]==before[GAME/n]').replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']",'')
exec(compile(boot,'backup-independent-current-packages','exec'))
baseG,baseM,baseF=G,M,F
for bn in NAMES:
 alias=bn+'::skin';env[alias]=UnityPy.load(before[SKIN/bn]);objs[alias]={o.path_id:o for o in env[alias].objects};hashes[alias]={i:sha(o.get_raw_data()) for i,o in objs[alias].items()};changes[alias]={}
env[W]=UnityPy.load(str(GAME/W));objs[W]={o.path_id:o for o in env[W].objects}
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'));reserved_ids={int(x['path_id']) for x in reserved['reserved_textures']}
asset_clones=[];new_guids={};audits=[];catalog_outputs={}
helpers=ast.parse((R/'build-highlight-five-column-native-player-lists.py').read_text('utf8'))
exec(compile(ast.Module(body=[x for x in helpers.body if isinstance(x,ast.FunctionDef) and x.name in ['register_clone','clone_doc']],type_ignores=[]),'private-live-cell','exec'))
helpers=ast.parse((R/'build-match-ui-avatars-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[x for x in helpers.body if isinstance(x,ast.FunctionDef) and x.name in ['rewrite_arg','rewrite_binding']],type_ignores=[]),'binding-rewrite','exec'))
spec=importlib.util.spec_from_file_location('live_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for tag,suffix in [('game',''),('skin','::skin')]:
 G,M,F=baseG+suffix,baseM+suffix,baseF+suffix
 main=Doc(G,name='MatchViewer_12x4')
 header=Doc(M,name='OverviewHeader');row=header.named('MatchTopRightControlsWithPendingChanges')
 header.st(row,[(131102,header.enum('absolute')),(131103,header.px(0)),(131104,header.px(0)),(131089,{'m_ValueType':1,'valueIndex':2}),(131091,header.px(0)),(131093,header.px(0)),(131083,header.enum('row')),(131073,header.enum('center')),(131085,header.num(0)),(131084,header.num(0))])
 assert header.a(1037)['m_Parent']['rid']==row
 header.save()
 # Stop the toast's theme classes from taking it out of the native row.
 popup=Doc(G,name='MatchTacticPendingChanges')
 for node in [1004,1006]:popup.st(node,[(131102,popup.enum('relative'))]+[(p,{'m_ValueType':1,'valueIndex':2}) for p in [131089,131103,131104,131080]])
 popup.save()
 donor=Doc(W,name='TacticsConditionPercentageCell')
 pid=-981030000001000
 assert pid not in reserved_ids and pid-1 not in reserved_ids
 cell,guid=clone_doc(donor,'HighlightLiveMatchConditionPercentageCell',pid)
 position=Doc(G,name='HighlightEightFieldsPositionCell')
 expectation=next(r['data'] for r in cell.r.values() if 'Parameters' in r.get('data',{}))
 position_expect=next(r['data'] for r in position.r.values() if 'Parameters' in r.get('data',{}))
 expectation['Parameters']=copy.deepcopy(position_expect['Parameters'])
 remap=next(r['data'] for r in cell.r.values() if any(m['from']=='player' for m in r.get('data',{}).get('Mappings',[])))
 remap['Mappings']=[{'m_serialisedType':0,'from':'person','to':{'m_path':'binding.Player'},'type':{'id':1145176065}}, {'m_serialisedType':0,'from':'teamselectionindex','to':{'m_path':'tactic.TeamSelectionIndexFromPlayer'},'type':{'id':0}}, {'m_serialisedType':0,'from':'player','to':{'m_path':'tactic.PositionFromTeamSelectionIndex.MatchPlayer'},'type':{'id':1835103332}}]
 rewrite_binding(cell.d,'player.Sharpness','player.Person.Sharpness')
 cell.save()
 factory=find(F,'HighlightEightFieldsFactory');tree=factory.read_typetree();column=next(c for c in tree['m_rowData'] if c['m_id']=='condition');pos=next(c for c in tree['m_rowData'] if c['m_id']=='picked-position')
 column['m_uxmlRef']['m_AssetGUID']=guid;column['m_valueBindings']=copy.deepcopy(pos['m_valueBindings'])
 factory.save_typetree(tree);changes[F][factory.path_id]=tree
 metaobj=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree()
 ptr={'m_FileID':0,'m_PathID':pid};span=[ptr,{'m_FileID':0,'m_PathID':pid-1}]
 def collect_ptrs(v):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in span:span.append(copy.deepcopy(v))
   else:
    for x in v.values():collect_ptrs(x)
  elif isinstance(v,list):
   for x in v:collect_ptrs(x)
 collect_ptrs(cell.d);collect_ptrs(cell.s)
 meta['m_Container'].append((guid,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':ptr}));meta['m_PreloadTable']+=span
 metaobj.save_typetree(meta);changes[G][metaobj.path_id]=meta
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';cat=cm.Catalog(before[cp]);source=next(x for x in cat.locations('be643be14ca6c024083f0e6b4c7dea7c') if cat.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
 raw=cat.add_key_location(guid,source,source);cat=cm.Catalog(raw);loc=next(x for x in cat.locations(guid) if cat.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
 assert baseG in cat.location(cat.location(loc)['dependencies'][0])['internal']
 idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx];records=list(cat.key_records)
 records[idx]=(ko,cat.append(b''.join(struct.pack('<I',x) for x in [v[0] for v in cat.array(ls,'I')]+[loc]),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catalog_outputs[tag]=bytes(cat.data)
 audits.append({'variant':tag,'live_cell_guid':guid,'cell_live_player_path':'tactic.PositionFromTeamSelectionIndex.MatchPlayer','factory_context_from_existing_position_column':True,'popup_right_anchor_px':0,'native_controls_retain_position_in_row':True})
G,M,F=baseG,baseM,baseF
outputs={}
for bn in [n+s for s in ['', '::skin'] for n in NAMES]:
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
 assert set(saved)==set(objs[bn]);assert reserved_ids.isdisjoint(set(saved)-set(hashes[bn]))
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree,(bn,pid)
 for doc in [d for d in documents if d.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 dest=OUT/('skin-'+bn.split('::')[0] if bn.endswith('::skin') else bn);dest.write_bytes(raw);outputs[bn]=dest
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
tx=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 for bn in NAMES:
  p=folder/bn;src=outputs[bn+('::skin' if tag=='skin' else '')];tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/bn),'before':sha(before[p]),'after':sha(src.read_bytes())})
 for name,data in [('catalog.bin',catalog_outputs[tag]),('catalog.hash',hashlib.md5(catalog_outputs[tag]).hexdigest().encode('ascii'))]:
  src=OUT/(tag+'-'+name);src.write_bytes(data);p=(GAME.parent if tag=='game' else SKIN)/name
  tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[p]),'after':sha(data)})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'runtime_verified':False},ensure_ascii=False))
