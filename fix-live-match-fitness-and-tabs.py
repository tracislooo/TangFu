from pathlib import Path
import ast,json,copy,struct,importlib.util
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','live-match-fitness-tabs-').replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]','if False:assert before[SKIN/n]==before[GAME/n]').replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']",'')
exec(compile(boot,'backup-current-fitness','exec'))
bases=(W,G,M,F)
for bn in NAMES:
 alias=bn+'::skin';env[alias]=UnityPy.load(before[SKIN/bn]);objs[alias]={o.path_id:o for o in env[alias].objects};hashes[alias]={i:sha(o.get_raw_data()) for i,o in objs[alias].items()};changes[alias]={}
asset_clones=[];new_guids={}
helper=ast.parse((R/'build-highlight-five-column-native-player-lists.py').read_text('utf8'))
exec(compile(ast.Module(body=[x for x in helper.body if isinstance(x,ast.FunctionDef) and x.name in ['register_clone','clone_doc']],type_ignores=[]),'private-live-cells','exec'))
helper=ast.parse((R/'build-match-ui-avatars-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[x for x in helper.body if isinstance(x,ast.FunctionDef) and x.name in ['rewrite_arg','rewrite_binding']],type_ignores=[]),'rewrite-numeric-binding','exec'))
def unpack(raw):
 raw=bytes(raw);p=1;out=[]
 for _ in range(raw[0]):
  n=struct.unpack_from('<I',raw,p)[0];p+=4;out.append(raw[p:p+n]);p+=n
 assert p==len(raw);return out
def pack(args):return list(bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args))
def conditional(prototype,ref,a,b,dest):
 f=copy.deepcopy(prototype);args=unpack(f['m_inputs']['m_variable']['m_argumentBytes']);assert len(args)==5
 prefix=args[0][:args[0][0]+2]
 for i,value in enumerate([ref,a,b,dest]):
  raw=value.encode();assert len(raw)<128;args[i]=prefix+bytes([len(raw)])+raw
 f['m_inputs']['m_variable']['m_argumentBytes']=pack(args);return f
def allptr(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():allptr(x,out)
 elif isinstance(v,list):
  for x in v:allptr(x,out)
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'));reserved_ids={int(x['path_id']) for x in reserved['reserved_textures']}
spec=importlib.util.spec_from_file_location('fitness_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cats={};audits=[]
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];main=Doc(G,name='MatchViewer_12x4')
 header=Doc(M,name='OverviewHeader');tabs=header.named('TacticsOpened');header.st(tabs,[(131102,header.enum('relative')),(131104,header.px(48))]);header.save()
 source=Doc(W,name='TacticsConditionPercentageCell')
 direct,directguid=clone_doc(source,'MatchLiveFitnessDualRingCell',-981030000020000)
 expectation=next(r['data'] for r in direct.r.values() if 'Parameters' in r.get('data',{}))
 expectation['Parameters'][0]['type']['id']=1835103332
 mapper=next(r['data'] for r in direct.r.values() if any(m['from']=='player' for m in r.get('data',{}).get('Mappings',[])))
 mapper['Mappings']=[{'m_serialisedType':0,'from':'player','to':{'m_path':'binding'},'type':{'id':1835103332}}]
 direct.save()
 adapter,adapterguid=clone_doc(direct,'HighlightStatsLiveFitnessDualRingCell',-981030000020010)
 position=Doc(G,name='HighlightEightFieldsPositionCell')
 next(r['data'] for r in adapter.r.values() if 'Parameters' in r.get('data',{}))['Parameters']=copy.deepcopy(next(r['data']['Parameters'] for r in position.r.values() if 'Parameters' in r.get('data',{})))
 mapper=next(r['data'] for r in adapter.r.values() if 'Mappings' in r.get('data',{}))
 mapper['Mappings']=[{'m_serialisedType':0,'from':'person','to':{'m_path':'binding.Player'},'type':{'id':1145176065}},{'m_serialisedType':0,'from':'teamselectionindex','to':{'m_path':'tactic.TeamSelectionIndexFromPlayer'},'type':{'id':0}},{'m_serialisedType':0,'from':'player','to':{'m_path':'tactic.PositionFromTeamSelectionIndex.MatchPlayer'},'type':{'id':1835103332}}]
 adapter.save();factory_audit=[]
 for ob in list(objs[F].values()):
  if ob.type.name!='MonoBehaviour' or ob.peek_name() not in ['HighlightEightFieldsFactory','InMatchTacticsFitnessFactory','HalfTimeTalkFitnessFactory']:continue
  tree=ob.read_typetree();name=tree['m_Name']
  ident='halftime-condition-sharpness' if name=='HalfTimeTalkFitnessFactory' else 'condition'
  col=next(c for c in tree['m_rowData'] if c['m_id']==ident)
  if name=='HighlightEightFieldsFactory':
   col['m_uxmlRef']['m_AssetGUID']=adapterguid;col['m_valueBindings']=copy.deepcopy(next(c for c in tree['m_rowData'] if c['m_id']=='picked-position')['m_valueBindings'])
  else:
   col['m_uxmlRef']['m_AssetGUID']=directguid;col['m_valueBindings']=[{'m_serialisedType':0,'from':'binding','to':{'m_path':'binding.Player' if name=='HalfTimeTalkFitnessFactory' else 'binding'},'type':{'id':1835103332}}]
  ob.save_typetree(tree);changes[F][ob.path_id]=tree;factory_audit.append((name,ob.path_id,ident))
 # The in-match board had been reading the Person's saved condition. Use
 # native reference-aware binding to keep outside-match fallback unchanged.
 details=Doc(W,name='TacticsPositionDetailed')
 prototype=next(f for r in details.r.values() for f in r.get('data',{}).get('BindFunction',[]) if f.get('m_target',{}).get('m_guid')=='079b54afdf49eb242aba84c36407187b')
 for name in ['TacticsPositionDetailed','TacticsPositionCombined']:
  board=Doc(W,name=name);rewrite_binding(board.d,'position.Player.Condition','LiveMatchBoardCondition')
  setter=next(r['data'] for r in board.r.values() if isinstance(r.get('data',{}).get('BindFunction'),list) and 'ValueVariables' in r['data'])
  setter['ValueVariables'].append({'m_name':'LiveMatchBoardCondition','m_scopeValue':{'m_serializedData':'Int|0|'}});setter['ValueVariables_UxmlAttributeFlags']=1
  setter['BindFunction'].append(conditional(prototype,'position.MatchPlayer','position.MatchPlayer.Condition','position.Player.Condition','LiveMatchBoardCondition'));setter['BindFunction_UxmlAttributeFlags']=1
  board.save()
 mo=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=mo.read_typetree()
 for pid,guid in [(-981030000020000,directguid),(-981030000020010,adapterguid)]:
  assert pid not in reserved_ids and pid-1 not in reserved_ids
  span=[{'m_FileID':0,'m_PathID':pid},{'m_FileID':0,'m_PathID':pid-1}];allptr(changes[G][pid],span);allptr(changes[G][pid-1],span)
  meta['m_Container'].append((guid,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':pid}}));meta['m_PreloadTable']+=span
 mo.save_typetree(meta);changes[G][mo.path_id]=meta
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';raw=before[cp]
 for guid in [directguid,adapterguid]:
  cat=cm.Catalog(raw);loc=next(p for p in cat.locations('be643be14ca6c024083f0e6b4c7dea7c') if cat.location(p)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');raw=cat.add_key_location(guid,loc,loc)
 cat=cm.Catalog(raw);extra=[cat.locations(g)[0] for g in [directguid,adapterguid]]
 for loc in extra:assert bases[1] in cat.location(cat.location(loc)['dependencies'][0])['internal']
 idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx];records=list(cat.key_records)
 records[idx]=(ko,cat.append(b''.join(struct.pack('<I',v) for v in [v[0] for v in cat.array(ls,'I')]+extra),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));cats[tag]=bytes(cat.data)
 audits.append({'variant':tag,'tab_top':48,'body_padding_unchanged':True,'condition':'MatchPlayer.Condition','sharpness':'MatchPlayer.Sharpness','factories':factory_audit,'board_fallback':'Person.Condition outside matches','direct_cell':directguid,'stats_adapter':adapterguid})
W,G,M,F=bases;outputs={}
for bn in [n+s for s in ['', '::skin'] for n in NAMES]:
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
 assert reserved_ids.isdisjoint(set(saved)-set(hashes[bn]))
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
 for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t,(bn,pid)
 for doc in [d for d in documents if d.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 dest=OUT/('skin-'+bn.split('::')[0] if bn.endswith('::skin') else bn);dest.write_bytes(raw);outputs[bn]=dest
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
tx=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 for bn in NAMES:
  p=folder/bn;src=outputs[bn+('::skin' if tag=='skin' else '')];tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/bn),'before':sha(before[p]),'after':sha(src.read_bytes())})
 for name,data in [('catalog.bin',cats[tag]),('catalog.hash',hashlib.md5(cats[tag]).hexdigest().encode('ascii'))]:
  src=OUT/(tag+'-'+name);src.write_bytes(data);p=(GAME.parent if tag=='game' else SKIN)/name;tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[p]),'after':sha(data)})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'runtime_verified':False},ensure_ascii=False))
