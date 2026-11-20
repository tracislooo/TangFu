from pathlib import Path
import sys,json,hashlib,subprocess,os,uuid
out=Path(next(x for x in sys.argv[1:] if not x.startswith('--'))).resolve();restore='--restore' in sys.argv
manifest=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def closed():
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 assert not p.stdout.strip(),'Exit Football Manager normally before installing/restoring this patch.'
closed()
if not restore:
 for item in tx:
  target=Path(item['target'])
  if target.parent.name!='CustomGridCompositions':continue
  raw=target.read_bytes()
  if hashlib.sha256(raw).hexdigest()==item['before']:continue
  old=json.loads(Path(item['backup']).read_text('utf8'));new=json.loads(Path(item['source']).read_text('utf8'));mapping={}
  for a,b in zip(old['m_gridComponents'],new['m_gridComponents']):
   for c,d in zip(a['m_gridElementConfigs'],b['m_gridElementConfigs']):
    x=c['AssetRef']['m_AssetGUID'];y=d['AssetRef']['m_AssetGUID']
    if x!=y:mapping[x]=y
  current_cache=json.loads(raw.decode('utf8'))
  for block in current_cache['m_gridComponents']:
   for config in block['m_gridElementConfigs']:
    ref=config['AssetRef'];ref['m_AssetGUID']=mapping.get(ref['m_AssetGUID'],ref['m_AssetGUID'])
  encoded=json.dumps(current_cache,ensure_ascii=False,indent=2).encode('utf8')
  Path(item['backup']).write_bytes(raw);Path(item['source']).write_bytes(encoded)
  item['before']=hashlib.sha256(raw).hexdigest();item['after']=hashlib.sha256(encoded).hexdigest()
 (out/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
current={};targets={}
allowed={Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64').resolve(),Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa').resolve(),Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages').resolve()}
allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())
for row in tx:
 p=Path(row['target']);assert p.resolve().parent in allowed
 source=Path(row['backup' if restore else 'source']);data=source.read_bytes();assert sha(data)==row['before' if restore else 'after'],('Patch/backup damaged',source)
 previous=p.read_bytes();expected=row['after' if restore else 'before'];actual=sha(previous)
 assert actual==expected or (not restore and actual==row['after']),('Target changed since preparation',p)
 current[p]=previous;targets[p]=data
for path,h in manifest['protected_sha256'].items():assert sha(Path(path).read_bytes())==h,('Unrelated resource changed',path)
closed()
for p,data in current.items():assert p.read_bytes()==data
def atomic(p,data):
 temp=p.with_name(p.name+'.codex-fitness-'+uuid.uuid4().hex+'.tmp')
 try:temp.write_bytes(data);os.replace(temp,p)
 finally:
  if temp.exists():temp.unlink()
try:
 for p,data in targets.items():atomic(p,data);assert p.read_bytes()==data
 for path,h in manifest['protected_sha256'].items():assert sha(Path(path).read_bytes())==h
except BaseException:
 for p,data in current.items():atomic(p,data)
 raise
manifest.update(installed=not restore,installed_verified=not restore,restored=restore)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':not restore,'restored':restore,'verified_resource_files':len(targets),'runtime_verified':False,'output':str(out)},ensure_ascii=False))

if not restore:
 state=json.loads((out.parent/'current-highlight-layout.json').read_text('utf8'))
 state.update(status='installed',patch=str(out),source_script=str(out.parent/'fix-highlight-event-text-70.py'),restore=str(out/'restore.ps1'),verification=str(out/'manifest.json'),runtime_verified=False,event_text_scale=0.7)
 (out.parent/'current-highlight-layout.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
