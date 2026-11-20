from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent
boot=(R/'repair-background-switch-local-assignment.py').read_text('utf8').split('for folder,tag in [(GAME,')[0].replace('background-switch-local-assignment-','background-picker-removed-')
exec(compile(boot,'setup','exec'))
src=ast.parse((R/'hover-fc-portrait-selector-20261112-211124/add-hover-fc-portrait-selector.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='owned'],type_ignores=[]),'ownership','exec'))
oldtx=json.loads((R/'background-thumbnail-picker-20261113-015608/transaction.json').read_text('utf8'))
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 before=(folder/W).read_bytes();env={W:UnityPy.load(before)};objs={W:{o.path_id:o for o in env[W].objects}};hashes={i:sha(o.get_raw_data()) for i,o in objs[W].items()};changes={W:{}}
 nav=Doc(W,name='PrimaryNavigationBar');start=nav.named('TFBackgroundButtonSharedSelection');parent=nav.a(start)['m_Parent']['rid'];original=copy.deepcopy(nav.d);removed=owned(nav.r,start);nav.a(parent)['m_Children'].remove({'rid':start});nav.d['references']['RefIds']=[r for r in nav.d['references']['RefIds'] if r['rid'] not in removed];nav.r=refs(nav.d);nav.save()
 old=UnityPy.load(str(R/'background-switch-button-20261113-012354'/('backup-'+tag)/W));oldobjs={o.path_id:o for o in old.objects}
 for pid in [-716828569427839901,-967645546861759389]:
  d=oldobjs[pid].read_typetree();objs[W][pid].save_typetree(d);changes[W][pid]=d
 delete={-941300000001000,-941300000001001}
 metaob=next(o for o in objs[W].values() if o.type.name=='AssetBundle');meta=metaob.read_typetree();oldpre=meta['m_PreloadTable'];newpre=[];entries=[]
 for key,entry in meta['m_Container']:
  if entry['asset']['m_FileID']==0 and entry['asset']['m_PathID'] in delete:continue
  span=[x for x in oldpre[entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']] if not(x['m_FileID']==0 and x['m_PathID'] in delete)]
  entry['preloadIndex']=len(newpre);entry['preloadSize']=len(span);newpre+=span;entries.append((key,entry))
 meta['m_Container']=entries;meta['m_PreloadTable']=newpre;metaob.save_typetree(meta);changes[W][metaob.path_id]=meta
 for pid in delete:
  ob=objs[W].pop(pid);del ob.assets_file.objects[pid]
 payload=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(payload).objects};assert set(saved)==set(hashes)-delete
 for pid,h in hashes.items():
  if pid not in changes[W] and pid not in delete:assert sha(saved[pid].get_raw_data())==h,(tag,pid)
 for pid,d in changes[W].items():assert saved[pid].read_typetree()==d
 for r in saved[8206725239586998471].read_typetree()['references']['RefIds']:assert not r.get('data',{}).get('name','').startswith('TFBackground')
 for target,data in [(folder/W,payload)]+[(Path(x['target']),Path(x['backup']).read_bytes()) for x in oldtx if Path(x['target']).parent==(GAME.parent if tag=='game' else SKIN) and Path(x['target']).name in ['catalog.bin','catalog.hash']]:
  previous=target.read_bytes()
  if target.name in ['catalog.bin','catalog.hash']:
   oldrow=next(x for x in oldtx if x['target']==str(target));assert sha(previous)==oldrow['after']
  backup=OUT/('backup-'+tag)/target.name;source=OUT/tag/target.name;backup.parent.mkdir(exist_ok=True);source.parent.mkdir(exist_ok=True);backup.write_bytes(previous);source.write_bytes(data);protected.pop(str(target),None);transactions.append({'target':str(target),'backup':str(backup),'source':str(source),'before':sha(previous),'after':sha(data)})
 reports.append({'target':tag,'removed_selector':True,'original_background_restored':True,'unrelated_objects_verified':len(hashes)-len(changes[W])-len(delete),'changed_objects':list(changes[W]),'deleted_private_objects':list(delete),'existing_navigation_other_records_preserved':all(nav.r[i]==r for i,r in refs(original).items() if i not in removed and i!=parent)})
 assert reports[-1]['existing_navigation_other_records_preserved']
for x in transactions:assert sha(Path(x['target']).read_bytes())==x['before']
for path,h in protected.items():assert sha(Path(path).read_bytes())==h
(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'reports':reports,'protected_sha256':protected},ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(transactions,ensure_ascii=False,indent=2),'utf8');print(str(OUT))
