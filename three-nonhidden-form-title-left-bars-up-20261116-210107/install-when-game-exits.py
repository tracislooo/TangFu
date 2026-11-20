from pathlib import Path
import hashlib,json,subprocess,sys,time,traceback
out=Path(__file__).resolve().parent
r=out.parent
status=out/'automatic-install-status.txt'
def running():
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 return bool(p.stdout.strip())
status.write_text('Waiting for Football Manager to exit normally.','utf8')
try:
 while True:
  while running():time.sleep(5)
  result=subprocess.run([sys.executable,str(out/'installer.py'),str(out)],capture_output=True,text=True)
  (out/'automatic-install.log').write_text(result.stdout+result.stderr,'utf8')
  if result.returncode==0:break
  if running():continue
  raise RuntimeError('Installation stopped: target hashes or another precondition changed; see automatic-install.log.')
 m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
 for row in tx:assert hashlib.sha256(Path(row['target']).read_bytes()).hexdigest()==row['after']
 v=dict(passed=True,installed_files=len(tx),checks=m['checks'],runtime_verified=False)
 (out/'verification-installed.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
 for name in ['current-approved-left-portrait-nonhidden-overview.json','current-middle-portrait-nonhidden-layout.json','current-old-left-portrait-nonhidden-overview.json']:
  p=r/name;idx=json.loads(p.read_text('utf8'));idx.update(previous_manifest=idx['manifest'],manifest=str(out/'manifest.json'),verification=str(out/'verification-installed.json'),script=str(r/'adjust-three-nonhidden-title-left-bars-up.py'),installed=True,installed_verified=True,runtime_verified=False)
  layout=idx.get('recent_form_layout',{});layout.update(title_visible=False,form_left_padding_px=0,content_left_px=0,chart_top_px=-40);idx['recent_form_layout']=layout
  p.write_text(json.dumps(idx,ensure_ascii=False,indent=2),'utf8')
 status.write_text('Installed and hash-verified; runtime display unverified.','utf8')
except BaseException:
 (out/'automatic-install-error.txt').write_text(traceback.format_exc(),'utf8')
 status.write_text('Installation stopped; see automatic-install-error.txt.','utf8')
 raise
