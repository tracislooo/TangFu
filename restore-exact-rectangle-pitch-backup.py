from pathlib import Path
import sys,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
loc=json.loads((R/'current-game-location.json').read_text('utf-8-sig'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';SOURCE=R/'native-position-dots-with-values-all-20261103-032739';pids=[-940000000005000,-940000000008000,-940000000010020,-960000000003030];sha=lambda b:hashlib.sha256(b).hexdigest();OUT=R/('restore-exact-rectangle-pitch-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();outputs={};before={};audits=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 p=folder/G;before[p]=p.read_bytes();f=OUT/('backup-'+tag);f.mkdir();(f/G).write_bytes(before[p]);e=UnityPy.load(before[p]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};source={o.path_id:o for o in UnityPy.load(str(SOURCE/('backup-'+tag)/G)).objects};restored=set()
 for pid in pids:
  d=source[pid].read_typetree();sid=d['inlineSheet']['m_PathID']
  for i in [pid,sid]:obs[i].set_raw_data(source[i].get_raw_data());restored.add(i)
 out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in restored:assert sha(check[i].get_raw_data())==h
 for i in restored:assert check[i].get_raw_data()==source[i].get_raw_data()
 for pid in pids:
  rr=check[pid].read_typetree()['references']['RefIds'];assert any(r.get('data',{}).get('name')=='OverviewFourteenPositionZones' for r in rr)
 outputs[p]=out;(OUT/('prepared-'+tag+'.bundle')).write_bytes(out);audits.append({'target':str(p),'source':str(SOURCE/('backup-'+tag)/G),'restored_object_ids':[str(i) for i in sorted(restored)],'restored_objects_byte_identical_to_backup':True,'all_other_objects_unchanged':True})
report={'installed':False,'runtime_verified':False,'changes':audits,'new_style_design':False,'background_not_changed_beyond_original_backup':True};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for tag,folder in [('game',GAME),('skin',SKIN)]:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-'+tag)/G)+"' -Destination '"+str(folder/G)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
assert not subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip(),'Game running: prepared only'
for p,b in before.items():assert p.read_bytes()==b
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'restored':True,'output':str(OUT),'exact_backup_objects':8}))
