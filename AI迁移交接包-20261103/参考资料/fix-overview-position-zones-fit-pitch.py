from pathlib import Path
import ast,copy,json
boot=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8').split('ROW=-940000000006000;')[0].replace('photo-up3-titled-pros-cons-tactics-thirds-','fix-overview-position-zones-fit-pitch-')
exec(compile(boot,'backups-and-helpers','exec'))
audits=[]
for pid in [-940000000008000,-940000000010020]:
 doc=objs[G][pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree()
 overlay=named('OverviewFourteenPositionZones');source=rr[overlay]['data']['m_Parent']['rid'];target=rr[1022]['data']['m_Parent']['rid']
 assert source!=target
 assert rr[target]['data']['m_FullTypeName']=='SI.Bindable.SIAspectRatioFitter'
 assert rr[1023]['data']['m_Parent']['rid']==target
 rr[source]['data']['m_Children'].remove({'rid':overlay});rr[target]['data']['m_Children'].append({'rid':overlay});rr[overlay]['data']['m_Parent']={'rid':target}
 for i,r in old.items():
  if i not in [source,target,overlay]:assert rr[i]==r,('unrelated selector record changed',pid,i)
 assert all(rr[i]['data']['m_Parent']['rid']==target for i in [overlay,1022,1023])
 assert sheet==objs[G][sid].read_typetree()
 validate_ui(doc,sheet);objs[G][pid].save_typetree(doc);changed[G][pid]=doc
 audits.append({'selector':str(pid),'old_parent':source,'new_parent':target,'parent_type':rr[target]['data']['m_FullTypeName'],'pitch_and_grid_use_same_bounds':True})
output=env[G].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[G])
for i,h in hashes[G].items():
 if i not in changed[G]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',i)
for i,d in changed[G].items():assert check[i].read_typetree()==d
for pid in [-940000000005000,-940000000005001,-940000000018000,-940000000018001]:assert sha(check[pid].get_raw_data())==hashes[G][pid]
(OUT/G).write_bytes(output)
report={'installed':False,'runtime_verified':False,'fixed_versions':[2,3,4],'first_version_unchanged':True,'fix':'move position grid inside the exact native aspect-ratio fitter that contains the pitch image','selectors':audits,'bindings_numbers_colours_geometry_and_clicks_unchanged':True,'only_modified_objects':[str(i) for i in changed[G]],'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first.' }"]
install=list(restore)
for p,b in before.items():
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
 if p.name==G:install.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(b)+"') { throw 'Installed bundle changed since preparation.' }")
for p in [GAME/G,SKIN/G]:install.append("Copy-Item -LiteralPath '"+str(OUT/G)+"' -Destination '"+str(p)+"' -Force")
install.append("$manifestFile = '"+str(OUT/'manifest.json')+"'")
install.append("$record = Get-Content -LiteralPath $manifestFile -Raw | ConvertFrom-Json; $record.installed = $true; $record | Add-Member -NotePropertyName installed_verified -NotePropertyValue $true -Force; $record | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $manifestFile -Encoding utf8")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');(OUT/'install.ps1').write_text('\n'.join(install),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p in [GAME/G,SKIN/G]:p.write_bytes(output);assert p.read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'fixed_versions':[2,3,4]}))
