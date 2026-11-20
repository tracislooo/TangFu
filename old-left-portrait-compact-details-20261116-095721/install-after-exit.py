from pathlib import Path
import json,hashlib,subprocess,sys,time,traceback
out=Path(__file__).resolve().parent;r=Path("G:/Doc/ChatGPT/New project");status=out/'automatic-install-status.txt';sha=lambda b:hashlib.sha256(b).hexdigest()
try:
 status.write_text('Waiting for Football Manager to exit normally','utf8')
 while subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():time.sleep(5)
 status.write_text('Installing','utf8')
 result=subprocess.run([sys.executable,str(out/'installer.py'),str(out)],capture_output=True,text=True)
 (out/'automatic-install-log.txt').write_text(result.stdout+'\n'+result.stderr,'utf8')
 if result.returncode:raise RuntimeError(result.stderr)
 m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
 for row in tx:assert sha(Path(row['target']).read_bytes())==row['after']
 report=dict(passed=True,installed=True,files=[dict(target=row['target'],sha256=row['after'])for row in tx],checks=m['checks'],runtime_verified=False)
 (out/'verification-installed.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
 p=r/'current-old-left-portrait-hidden-overview.json';state=json.loads(p.read_text('utf8'));previous=state['manifest'];state.update(previous_manifest=previous,manifest=str(out/'manifest.json'),verification=str(out/'verification-installed.json'),script=str(r/'compact-old-left-portrait-details.py'),installed=True,installed_verified=True,runtime_verified=False,personal_details_height_px=108,nation_club_font_reduced_px=3,layout_outside_portrait_matches_current_old_left_fc=False)
 state['compact_details_update']=dict(manifest=str(out/'manifest.json'),installed=True,installed_verified=True,runtime_verified=False)
 p.write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
 p=r/'current-player-overview-six-variants.json';idx=json.loads(p.read_text('utf8'));idx['old_left_portrait_hidden_layout_update']=state;p.write_text(json.dumps(idx,ensure_ascii=False,indent=2),'utf8')
 status.write_text('Installed and verified: game and independent skin, 2 files; runtime unverified','utf8')
except BaseException:
 status.write_text('Installation stopped: '+traceback.format_exc(),'utf8');raise
