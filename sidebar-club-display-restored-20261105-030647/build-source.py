"""Undo only the failed ClubScreen height compensation, preserving sidebar/header edits."""
from pathlib import Path
import datetime,hashlib,json,shutil,sys,zipfile
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
sha=lambda b:hashlib.sha256(b).hexdigest()
state=json.loads((R/'current-sidebar-version.json').read_text('utf8'));loc=json.loads((R/'current-game-location.json').read_text('utf8'));game=Path(loc['bundle_root']);skin=Path(loc['skin_packages']);previous=Path(state['sidebar_club_height_patch']);base=Path(state['installed_variant'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';target=game/W;before=target.read_bytes();env=UnityPy.load(before);a=env.assets[0];raw={i:o.get_raw_data() for i,o in a.objects.items()}
source=UnityPy.load(str(previous/'backup-game'/W)).assets[0];ob=next(o for o in source.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='ClubScreen');sid=ob.read_typetree()['inlineSheet']['m_PathID'];ids=[ob.path_id,sid]
for pid in ids:a.objects[pid].set_raw_data(source.objects[pid].get_raw_data())
data=env.file.save(packer='lz4');check=UnityPy.load(data).assets[0]
for pid,o in check.objects.items():assert o.get_raw_data()==(source.objects[pid].get_raw_data() if pid in ids else raw[pid]),pid
out=R/('sidebar-club-display-restored-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();(out/'packages').mkdir();(out/'backup-game').mkdir();p=out/'packages'/W;p.write_bytes(data);b=out/'backup-game'/W;b.write_bytes(before)
protected={str(p):sha(p.read_bytes()) for p in list(game.glob('*.bundle'))+[game.parent/'catalog.bin',game.parent/'catalog.hash']+list(skin.glob('*')) if p.is_file() and p!=target}
tx=[dict(target=str(target),source=str(p),backup=str(b),before=sha(before),after=sha(data))]
m=dict(installed=False,runtime_verified=False,restored_object_ids=ids,club_vta_and_style_equal_pre_height_change=True,all_other_objects_byte_identical=True,top_shortcuts_stay_hidden=True,sidebar_19_links_preserved=True,protected_sha256=protected)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',out/'installer.py');shutil.copy2(__file__,out/'build-source.py')
full=out/'full-sidebar';(full/'packages').mkdir(parents=True);(full/'non-sidebar-backup').mkdir();aa=out/'aa';(aa/'StandaloneWindows64').mkdir(parents=True);ftx=[]
for row in json.loads((base/'transaction.json').read_text('utf8')):
 t=Path(row['target']);current=t.read_bytes();assert sha(current)==row['after'],('Concurrent changes',t)
 payload=data if t.name==W else current;src=full/'packages'/t.name;bak=full/'non-sidebar-backup'/t.name;src.write_bytes(payload);backup=Path(row['backup']).read_bytes();assert sha(backup)==row['before'];bak.write_bytes(backup)
 ftx.append(dict(target=str(t),source=str(src),backup=str(bak),before=sha(backup),after=sha(payload)))
 (aa/('StandaloneWindows64' if t.name.endswith('.bundle') else '')/t.name).write_bytes(payload)
fm=dict(installed=False,runtime_verified=False,sidebar_only=True,fixed_navigation_count=19,club_failed_height_change_removed=True,top_custom_shortcuts_hidden=state['top_custom_shortcuts_hidden'],protected_sha256={p:h for p,h in protected.items() if p not in {x['target'] for x in ftx}})
(full/'manifest.json').write_text(json.dumps(fm,ensure_ascii=False,indent=2),'utf8');(full/'transaction.json').write_text(json.dumps(ftx,ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',full/'installer.py')
for folder,options in [(out,[('install',''),('restore-this-fix',' --restore')]),(full,[('install-sidebar',''),('restore-non-sidebar',' --restore')])]:
 for name,flag in options:(folder/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
zpath=R/'exports'/('FM27-'+out.name+'-aa.zip')
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in aa.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(out).as_posix())
with zipfile.ZipFile(zpath) as z:assert len(z.namelist())==5 and z.testzip() is None
m.update(full_sidebar=str(full),aa_export=str(zpath));(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');assert target.read_bytes()==before
print(json.dumps(dict(output=str(out),full_sidebar=str(full),zip=str(zpath),changed_objects=2),ensure_ascii=False),flush=True)
