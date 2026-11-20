"""Install the prepared career scroller after a normal game exit."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,time
R=Path(__file__).resolve().parent
out=Path(json.loads((R/'middle-fc-career-scroll-inset-prepared.json').read_text('utf8'))['output'])
flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
def status(value,**extra):
    (out/'automatic-install-status.json').write_text(json.dumps(dict(status=value,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**extra),ensure_ascii=False,indent=2),'utf8')
def running():
    p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True,creationflags=flags)
    assert p.returncode in[0,1]
    return bool(p.stdout.strip())
try:
    assert json.loads((out/'verification-prepared.json').read_text('utf8'))['passed']
    status('waiting_for_game_exit')
    while running():time.sleep(5)
    status('installing')
    with (out/'automatic-install.log').open('w',encoding='utf8')as log:
        subprocess.run([sys.executable,str(out/'installer.py'),str(out)],check=True,stdout=log,stderr=subprocess.STDOUT,creationflags=flags)
    rows=json.loads((out/'transaction.json').read_text('utf8'));m=json.loads((out/'manifest.json').read_text('utf8'))
    for row in rows:assert hashlib.sha256(Path(row['target']).read_bytes()).hexdigest()==row['after']
    (out/'verification-installed.json').write_text(json.dumps(dict(passed=True,installed_files=len(rows),checks=m['checks'],runtime_verified=False),ensure_ascii=False,indent=2),'utf8')
    p=R/'current-middle-player-overview-layout.json';idx=json.loads(p.read_text('utf8'));(out/'previous-index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2),'utf8')
    idx.update(previous_manifest=idx['manifest'],manifest=str(out/'manifest.json'),career_scroller_script=str(R/'add-middle-fc-career-scroller.py'),verification=str(out/'verification-installed.json'),career_vertical_scroller=True,career_left_inset_px=10,club_crest_right_shift_px=6,installed=True,installed_verified=True,runtime_verified=False)
    p.write_text(json.dumps(idx,ensure_ascii=False,indent=2),'utf8')
    p=R/'current-player-overview-six-variants.json';a=json.loads(p.read_text('utf8'));a['middle_fc_layout_update']=idx;p.write_text(json.dumps(a,ensure_ascii=False,indent=2),'utf8')
    status('installed_and_hash_verified',runtime_verified=False)
except BaseException as exc:
    status('failed',error=str(exc));raise
